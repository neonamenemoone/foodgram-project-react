"""Модуль с сериализаторами для API."""
import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import Subscription, User


class Base64ImageField(serializers.ImageField):
    """Сериализатор для изображений в формате Base64."""

    def to_internal_value(self, data):
        """Метод для преобразования данных изображения в формате Base64."""
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            return ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


class UserSerializer(UserSerializer):
    """Сериализатор пользователей."""

    class Meta:
        """Метакласс пользователя."""

        model = User
        fields = [
            "first_name",
            "last_name",
        ]


class UserRegistrationSerializer(UserSerializer):
    """Сериализатор регистрации пользователя."""

    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        """Метакласс регистрации пользователя."""

        model = User
        fields = ["email", "username", "first_name", "last_name", "password"]


class UserProfileSerializer(UserSerializer):
    """Сериализатор профиля пользователя."""

    class Meta:
        """Метакласс профиля пользователя."""

        model = User
        fields = [
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        ]


class UserSetPasswordSerializer(serializers.Serializer):
    """Сериализатор для изменения пароля пользователя."""

    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        """Метакласс тегов."""

        model = Tag
        fields = ("id", "name", "color", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        """Метакласс ингредиентов."""

        model = Ingredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов в рецепте."""

    id = IngredientSerializer()
    amount = serializers.IntegerField()

    class Meta:
        """Метакласс ингредиентов в рецепте."""

        model = RecipeIngredient
        fields = ["id", "amount"]


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""

    email = serializers.EmailField(source="author.email")
    id = serializers.IntegerField(source="author.id")
    username = serializers.CharField(source="author.username")
    first_name = serializers.CharField(source="author.first_name")
    last_name = serializers.CharField(source="author.last_name")
    is_subscribed = serializers.BooleanField(default=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_recipes(self, obj):
        """Метод для получения списка рецептов пользователя."""
        recipes = Recipe.objects.filter(author=obj.author)
        serializers = RecipeSerializer(recipes, many=True)
        return serializers.data

    def get_recipes_count(self, obj):
        """Метод для получения количества рецептов пользователя."""
        recipes = Recipe.objects.filter(author=obj.author)
        return recipes.count()

    class Meta:
        """Метакласс подписок."""

        model = Subscription
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )


class UserWithSubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя с подписками."""

    subscriptions = UserSerializer(many=True)

    class Meta:
        """Метакласс пользователя с подписками."""

        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "subscriptions",
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецепта."""

    class Meta:
        """Метакласс рецепта."""

        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    image = Base64ImageField()

    class Meta:
        """Метакласс создания."""

        model = Recipe
        fields = [
            "id",
            "tags",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        ]


class RecipeFullSerializer(serializers.ModelSerializer):
    """Сериализатор для полной информации о рецепте."""

    author = UserProfileSerializer()
    tags = TagSerializer(many=True)
    ingredients = IngredientSerializer(many=True)

    class Meta:
        """Метакласс информации о рецепте."""

        model = Recipe
        fields = [
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        ]
