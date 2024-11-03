from django.core.validators import MinLengthValidator
from rest_framework import serializers

from .models import User, Address, Book


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "complete_name",
            "email",
            "password",
            "account_type",
            "phone",
            "created_at",
            "updated_at",
            "is_superuser",
            "is_staff",
            "is_active",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "id": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
            "is_superuser": {"read_only": True},
            "is_staff": {"read_only": True},
            "is_active": {"read_only": True},
            "account_type": {"default": "leitor"},
        }

    def create(self, validated_data):
        print(validated_data)
        if validated_data["account_type"] and validated_data["account_type"] == "admin":
            return User.objects.create_superuser(
                **validated_data, username=validated_data["email"]
            )
        else:
            return User.objects.create_user(
                **validated_data, username=validated_data["email"]
            )


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "cep",
            "state",
            "city",
            "district",
            "street",
            "number",
            "complement",
            "created_at",
            "updated_at",
            "owner",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "isbn",
            "editor",
            "year_publication",
            "gender",
            "total_quantity",
            "available_quantity",
            "description",
            "created_at",
            "updated_at",
        ]

        extra_kwargs = {
            "id": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }