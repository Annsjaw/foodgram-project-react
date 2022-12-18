from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TagViewSet, UserViewSet

v1_router = DefaultRouter()
v1_router.register('tags', TagViewSet, basename='tags')
v1_router.register('users', UserViewSet, basename='userss')

urlpatterns = [
    path('', include(v1_router.urls)),
]
