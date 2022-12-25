from djoser.views import UserViewSet
from users.models import User
from users.serializers import CustomUserSerializer


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
