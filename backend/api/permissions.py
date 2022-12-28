from rest_framework import permissions


class IsAuthorOrAdminPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.author == request.user


class AuthorOrReadOnly(permissions.BasePermission):
    """Доступ по GET всем, создание рецепта только авторизованному юзеру,
    редактирование только автору."""

    message = 'Изменение чужого контента запрещено!'

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
