from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag
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
    '''Сериализатор игридиентов в рецепте'''
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()

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

    def get_ingredients(self, obj):
        ingredients = IngredientRecipe.objects.filter(recipe=obj)
        return IngredientInRecipeSerializer(ingredients, many=True).data
