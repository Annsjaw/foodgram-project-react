from recipes.models import (Ingredient, Recipe, Tag, Favorite, ShoppingCart,
                            IngredientRecipe)
from django.db.models import Sum
from rest_framework.response import Response
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from api.permissions import AuthorOrReadOnly
from rest_framework.decorators import action

from .serializers import (IngredientSerializer, TagSerializer,
                          GetRecipeSerializer, PostRecipeSerializer,
                          ShortRecipeSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', )
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = GetRecipeSerializer
    permission_classes = AuthorOrReadOnly,
    filter_backends = (filters.SearchFilter, )
    search_fields = ('author', 'tars', 'is_favorite', 'is_in_shopping_cart', )

    def perform_create(self, serializer):
        """Метод автоматически добавляет текущего пользователя в поле автора
        при создании рецепта"""
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        """Метод определяет какой сериализатор использовать.
        При GET запросе данные отдаются в расширенном формате, а POST запрос
        принимает не все поля в ingredients"""
        if self.request.method == 'GET':
            return GetRecipeSerializer
        return PostRecipeSerializer

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, pk):
        """Метод создает новый эндпоинт в семействе рецептов:
        recipes/{id}/favorite/ и в зависимости от типа запроса POST или DELETE
        добавляет, или удаляет запись об авторе и рецепте в таблице
        избранного"""
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            Favorite.objects.create(recipe=recipe, user=request.user)
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            favorite_recipe = Favorite.objects.filter(
                 user=request.user, recipe=recipe)
            favorite_recipe.delete()
            return Response(f'Рецепт ({recipe.name}) удален из избранного '
                            f'пользователя ({request.user.username})',
                            status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, pk):
        """Метод создает новый эндпоинт в семействе рецептов:
        recipes/{id}/shopping_cart/ и в зависимости от типа запроса
        POST или DELETE добавляет, или удаляет запись об авторе и рецепте в
        таблице корзины"""
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            ShoppingCart.objects.create(recipe=recipe, user=request.user)
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            shoppingcart_recipe = ShoppingCart.objects.filter(
                 user=request.user, recipe=recipe)
            shoppingcart_recipe.delete()
            return Response(f'Рецепт ({recipe.name}) удален из корзины '
                            f'пользователя ({request.user.username})',
                            status=status.HTTP_204_NO_CONTENT)

        @action(methods=['get'], detail=False,
                permission_classes=(IsAuthenticated,))
        def download_shopping_cart(self, request):
            ingredient_list = IngredientRecipe.objects.filter(
                recipe__recipe_cart__user=request.user).values(
                'ingredient__name', 'ingredient__measurement_unit'
            ).annotate(sum_amount=Sum('amount'))
            shopping_list = ['Список покупок:\n']
            shopping_list += '\n'.join([
                f'{ingredient["ingredient__name"]}'
                f'({ingredient["ingredient__measurement_unit"]}) - '
                f'{ingredient["sum_amount"]}'
                for ingredient in ingredient_list
            ])
            filename = 'shopping_cart.txt'
            response = HttpResponse(shopping_list, content_type='text/plain')
            response[
                'Content-Disposition'] = f'attachment; filename={filename}'
            return response
