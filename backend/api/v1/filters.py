from django_filters.rest_framework import FilterSet, filters
from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    def filter_is_favorited(self, queryset, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(favorite__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(shoppingcart__user=user)
        return

    class Meta:
        model = Recipe
        fields = ('tags', 'author',)
