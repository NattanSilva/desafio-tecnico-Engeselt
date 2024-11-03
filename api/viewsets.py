from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Address, User, Book
from .permissions import IsAdminOrReadOnly, IsAdminToCreateABook
from .serializers import AddressSerializer, UserSerializer, BookSerializer


# Create your views here.
class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrReadOnly]


class LoginViewset(ViewSet):
    serializer_class = TokenObtainPairSerializer

    def create(self, request, *args, **kwargs):
        view = TokenObtainPairView.as_view()

        return view(request._request, *args, **kwargs)


class AddressViewSet(ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrReadOnly]


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminToCreateABook]
