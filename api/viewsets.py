from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .permissions import IsAdminOrReadOnly
from .serializers import UserSerializer


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
