from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    error,
    regist_loans,
    home,
    inactive_book,
    loans_relatory,
    login,
    logout,
    regist_book,
    regist_devolution,
    regist_user,
    success,
)
from .viewsets import AddressViewSet, LoginViewset, UserViewSet, BookViewSet, LoanViewSet

router = DefaultRouter()

# Registrando rotas
router.register("users", UserViewSet)
router.register("login", LoginViewset, basename="login")
router.register("address", AddressViewSet, basename="address")
router.register("books", BookViewSet, basename="book")
router.register("loans", LoanViewSet, basename="loan")

urlpatterns = [
    path("api/", include(router.urls)),
    path("", login, name="login"),
    path("home/", home, name="home"),
    path("logout", logout, name="logout"),
    path("regist_user/", regist_user, name="regist_user"),
    path("regist_book/", regist_book, name="regist_book"),
    path("inactive_book/", inactive_book, name="inactive_book"),
    path("regist_loans/", regist_loans, name="regist_loans"),
    path("regist_devolution/", regist_devolution, name="regist_devolution"),
    path("loans_relatory/", loans_relatory, name="loans_relatory"),
    path("success/", success, name="success"),
    path("error/", error, name="error"),
]
