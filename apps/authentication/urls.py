from django.urls import path
from rest_framework_simplejwt.views import TokenBlacklistView
from .views import *

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", TokenBlacklistView.as_view(), name="logout"),
]
