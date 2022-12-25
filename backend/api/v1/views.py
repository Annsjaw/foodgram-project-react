from recipes.models import Ingredient, Recipe, Tag
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from api.permissions import IsAuthorOrAdminPermission

from .serializers import IngredientSerializer, TagSerializer, RecipeSerializer


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
    serializer_class = RecipeSerializer

    def get_permissions(self):
        if self.action in ('update', 'destroy'):
            permission_classes = [IsAuthorOrAdminPermission]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]
