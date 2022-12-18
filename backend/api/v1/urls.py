from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, TagViewSet, UserViewSet

v1_router = DefaultRouter()
v1_router.register('tags', TagViewSet, basename='tags')
v1_router.register('users', UserViewSet, basename='users')
v1_router.register('ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    path('', include(v1_router.urls)),
]
