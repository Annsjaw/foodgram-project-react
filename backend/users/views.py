from djoser.views import UserViewSet
from users.models import User, Subscribe
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from users.serializers import CustomUserSerializer
from api.v1.serializers import SubscribeSerializer
from django.shortcuts import get_object_or_404


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(methods=['post', 'delete'], detail=True)
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        is_subscribed = Subscribe.objects.filter(
            user=request.user, author=author)

        if request.method == 'POST':
            if is_subscribed.exists():
                return Response("Вы уже подписаны на этого автора",
                                status=status.HTTP_400_BAD_REQUEST)
            elif author == request.user:
                return Response("Нельзя подписаться на самого себя",
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                Subscribe.objects.create(user=request.user, author=author)
                serializer = SubscribeSerializer(author, context={'request': request})
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            subscribe_user = Subscribe.objects.filter(
                user=request.user, author=author)
            subscribe_user.delete()
            return Response(f'Подписка на пользователя удалена',
                            status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False)
    def subscriptions(self, request):
        user = self.request.user
        if user.is_anonymous:
            return Response(status=HTTP_401_UNAUTHORIZED)
        subscription_list = User.objects.filter(following__user=request.user)
        pages = self.paginate_queryset(subscription_list)
        serializer = SubscribeSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
