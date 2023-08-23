from djoser.serializers import UserSerializer
from rest_framework import serializers
from users.models import User


class UserSerializer(UserSerializer):

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
        ]


class UserRegistrationSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password']


class UserProfileSerializer(UserSerializer):

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name']
