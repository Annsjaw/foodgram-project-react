from django.urls import include, path
from users import urls as user_urls

from .v1 import urls as v1_urls

urlpatterns = [
    path('', include(v1_urls)),
    path('', include(user_urls)),
]
