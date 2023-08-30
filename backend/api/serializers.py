"""Модуль с сериализаторами для API."""
import base64

from djoser.serializers import UserSerializer
from rest_framework import serializers

from django.core.files.base import ContentFile

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
        fields = ("id", "name", "measurement_unit")


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов в рецепте."""

    quantity = serializers.IntegerField()
    name = serializers.ReadOnlyField(
        source="ingredient.name",
    )
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit",
    )

    class Meta:
        """Метакласс ингредиентов в рецепте."""

        model = RecipeIngredient
        fields = ["id", "quantity", "name", "measurement_unit"]


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
        """Метакласс создания рецепта."""

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

    tags = TagSerializer(
        many=True,
    )
    ingredients = RecipeIngredientSerializer(
        many=True,
        source="amount",
    )
    author = UserSerializer(
        read_only=True,
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        """Метакласс информации о рецепте."""

        model = Recipe
        fields = [
            "id",
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
            "is_favorited",
            "is_in_shopping_cart",
        ]

    def validate_cooking_time(self, value):
        """Время приготовления больше ли 0."""
        if value < 1:
            raise serializers.ValidationError(
                {"errors": "Время приготовления должно быть больше 0.."}
            )

    def get_is_favorited(self, obj):
        """Добавлен ли рецепт в избранное для текущего пользователя."""
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return obj.in_favorites.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        """Добавлен ли рецепт в корзину для текущего пользователя."""
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return obj.in_carts.filter(user=request.user).exists()
