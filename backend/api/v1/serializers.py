import logging

from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag
from rest_framework import serializers, status
from users.models import User
from users.serializers import CustomUserSerializer

logger = logging.getLogger(__name__)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug', )


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов в рецепте"""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    name = serializers.SlugRelatedField(
        source='ingredient',
        read_only=True,
        slug_field='name'
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class GetRecipeSerializer(serializers.ModelSerializer):
    """Сериализер для представления json в формате отвечающем документации"""
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField()

    @staticmethod
    def get_ingredients(obj):
        """Метод получения ингредиентов для рецепта из связанной таблицы.
        Т.к. self не используется, ставится декоратор @staticmethod"""
        ingredients = IngredientRecipe.objects.filter(recipe=obj)
        return IngredientInRecipeSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        """Метод получения статуса избранного у пользователя.
        Если пользователь не авторизован, то отдается False
        Для авторизованного пользователя рецепт в избранном True, нет False."""
        request = self.context['request']
        return (request.user.is_authenticated
                and obj.favorite.filter(user=request.user).exists())

    def get_is_in_shopping_cart(self, obj):
        """Метод получения статуса нахождения в корзине у пользователя
        Если пользователь не авторизован, то отдается False
        Для авторизованного пользователя рецепт в корзине True, нет False."""
        request = self.context['request']
        return (request.user.is_authenticated
                and obj.shoppingcart.filter(user=request.user).exists())

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )


class WriteRecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(many=True)
    image = Base64ImageField()

    def validate(self, data):
        """Валидация данных от клиента"""
        if not data.get('tags'):
            raise serializers.ValidationError('Поле tags отсутствует')
        tag_list = []
        for tag in data.get('tags'):
            if not Tag.objects.filter(name=tag).exists():
                raise serializers.ValidationError(
                    f'Тега с названием {tag} не существует в базе данных'
                )
            if tag in tag_list:
                raise serializers.ValidationError(
                    'Вы не можете указывать два и более одинаковых тега'
                )
            tag_list.append(tag)
        return data

    @staticmethod
    def validate_ingredients(ingredients):
        """Валидация поля Ingredients"""
        if not ingredients:
            raise serializers.ValidationError('Поле ingredients отсутствует')

        ingredient_list = []
        for ingredient_dict in ingredients:
            ingredient_id = ingredient_dict.get('ingredient').id
            ingredient_amount = ingredient_dict.get('amount')

            if not ingredient_id:
                raise serializers.ValidationError(
                    'id ингредиент не указан')
            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise serializers.ValidationError(
                    f'Ингредиента с id={ingredient_id} нет в базе данных')
            if ingredient_id in ingredient_list:
                raise serializers.ValidationError(
                    'Ингредиенты в одном рецепте не могут повторяться')

            if not ingredient_amount:
                raise serializers.ValidationError(
                    'Поле amount ингредиента отсутствует')
            if int(ingredient_amount) <= 0:
                raise serializers.ValidationError(
                    'Количество ингредиентов должно быть больше 0')
            ingredient_list.append(ingredient_id)

        return ingredients

    def to_representation(self, instance):
        """Метод переопределяет сериализер для отображения в соответствии с
        документацией после успешного POST запроса по коду 201"""
        return GetRecipeSerializer(
            instance=instance, context=self.context).data

    @staticmethod
    def add_ingredients(recipe, ingredients):
        ingredients_recipe = list()
        for ingredient_dict in ingredients:
            ingredients_recipe.append(
                IngredientRecipe(
                    ingredient=ingredient_dict['ingredient'],
                    amount=ingredient_dict['amount'],
                    recipe=recipe,
                )
            )
        IngredientRecipe.objects.bulk_create(ingredients_recipe)

    @transaction.atomic
    def create(self, validated_data):
        """В validate_data находятся данные которые я передаю методом post
        1. Извлекаю данные в переменные ingredients и tags.
        2. Создаю новый рецепт с пустыми полями ingredients и tags.
        3. Вставляю список тегов в объект recipe.
        4. Прохожусь по списку ингредиентов в цикле и вставляю данные в
        связанную таблицу
        """

        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.add_ingredients(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """В instance находится экземпляр класса Recipe из базы данных.
        В validated_data данные на которые нужно заменить.
        1. Вытаскиваю ingredients и tags из validated_data.
        2. Обновляю данные instance на validate_data
        3. Очищаю поле ingredients и tags в instance
        4. Сохраняю рецепт
        5. Вставляю tags
        6. Вставляю ингредиенты"""

        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = super().update(instance, validated_data)
        instance.ingredients.clear()
        instance.tags.clear()
        instance.save()
        instance.tags.set(tags)
        self.add_ingredients(instance, ingredients)
        return instance

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class SubscribeSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if author.following.filter(user=user).exists():
            raise serializers.ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise serializers.ValidationError(
                detail='Вы не можете подписаться на самого себя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    @staticmethod
    def get_recipes(obj):
        recipes = Recipe.objects.filter(author=obj)
        serializer = ShortRecipeSerializer(recipes, many=True)
        return serializer.data

    @staticmethod
    def get_recipes_count(obj):
        recipes = Recipe.objects.filter(author=obj)
        return recipes.count()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
        read_only_fields = ('email', 'username',)
