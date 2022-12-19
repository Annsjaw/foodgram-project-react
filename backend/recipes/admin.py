from django.contrib import admin
from recipes.models import Ingredient, IngredientExtended, Recipe, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug', )
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngridientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit', )
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'author',
                    'name',
                    'image',
                    'text',
                    'cooking_time',
                    )
    empty_value_display = '-пусто-'


@admin.register(IngredientExtended)
class IngredientExtendedAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount', )
    empty_value_display = '-пусто-'
