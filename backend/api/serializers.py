from djoser.serializers import UserSerializer
from rest_framework import serializers
from users.models import User
from recipes.models import Tag


class UserSerializer(UserSerializer):

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
        ]


class UserRegistrationSerializer(UserSerializer):

    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password']


class UserProfileSerializer(UserSerializer):

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name']


class UserSetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")
