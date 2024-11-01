from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    gerency_loans,
    home,
    inactive_book,
    login,
    logout,
    regist_book,
    regist_user,
    regist_devolution, loans_relatory
)
from .viewsets import LoginViewset, UserViewSet

router = DefaultRouter()

# Registrando rotas
router.register("users", UserViewSet)
router.register("login", LoginViewset, basename="login")

urlpatterns = [
    path("api/", include(router.urls)),
    path("", login, name="login"),
    path("home/", home, name="home"),
    path("logout", logout, name="logout"),
    path("regist_user/", regist_user, name="regist_user"),
    path("regist_book/", regist_book, name="regist_book"),
    path("inactive_book/", inactive_book, name="inactive_book"),
    path("gerency_loans/", gerency_loans, name="gerency_loans"),
    path("regist_devolution/", regist_devolution, name="regist_devolution"),
    path("loans_relatory/", loans_relatory, name="loans_relatory"),
]
