from recipes.models import (Ingredient, IngredientRecipe, Recipe, Tag,
                            Favorite, ShoppingCart)
from drf_extra_fields.fields import Base64ImageField
from users.models import User
from rest_framework import serializers
from users.serializers import CustomUserSerializer


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
    is_favorite = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorite',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    @staticmethod
    def get_ingredients(obj):
        """Метод получения ингредиентов для рецепта из связанной таблицы.
        Т.к. self не используется, ставится декоратор @staticmethod"""
        ingredients = IngredientRecipe.objects.filter(recipe=obj)
        return IngredientInRecipeSerializer(ingredients, many=True).data

    def get_is_favorite(self, obj):
        """Метод получения статуса избранного у пользователя.
        Если пользователь не авторизован, то отдается False
        Для авторизованного пользователя рецепт в избранном True, нет False."""
        request = self.context['request']
        if not request.user.is_authenticated:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Метод получения статуса нахождения в корзине у пользователя
        Если пользователь не авторизован, то отдается False
        Для авторизованного пользователя рецепт в корзине True, нет False."""

        request = self.context['request']
        if not request.user.is_authenticated:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj).exists()


class PostRecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(many=True)
    image = Base64ImageField()

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

    def to_representation(self, instance):
        """Метод переопределяет сериализер для отображения в соответствии с
        документацией после успешного POST запроса по коду 201"""
        return GetRecipeSerializer(
            instance=instance, context=self.context).data

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

        for ingredient_dict in ingredients:

            IngredientRecipe.objects.create(
                ingredient=ingredient_dict['ingredient'],
                amount=ingredient_dict['amount'],
                recipe=recipe,
            )

        return recipe

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

        for ingredient_dict in ingredients:

            IngredientRecipe.objects.create(
                ingredient=ingredient_dict['ingredient'],
                amount=ingredient_dict['amount'],
                recipe=instance,
            )

        return instance


# TODO Унаследоваться от него в рецепты
class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class SubscribeSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    @staticmethod
    def get_recipes(obj):
        recipes = Recipe.objects.filter(author=obj)
        serializer = ShortRecipeSerializer(recipes, many=True)
        return serializer.data

    @staticmethod
    def get_recipes_count(obj):
        recipes = Recipe.objects.filter(author=obj)
        return recipes.count()
