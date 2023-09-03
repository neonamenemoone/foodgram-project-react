"""Модуль с сериализаторами для API."""
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from django.contrib.auth.password_validation import validate_password
from django.db.models import Count

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import Subscription, User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователей."""

    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    class Meta:
        """Метакласс регистрации пользователя."""

        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password']

    def validate_password(self, password):
        """Проверяет валидность пароля."""
        validate_password(password)
        return password

    def create(self, validated_data):
        """Создает нового пользователя."""
        password = validated_data.pop('password')
        user: User = super().create(validated_data)
        try:
            user.set_password(password)
            user.save()
            return user
        except serializers.ValidationError as exc:
            user.delete()
            raise exc


class ChangePasswordSerializer(serializers.Serializer):
    """Сериализатор для изменения пароля пользователя."""

    current_password = serializers.CharField(
        required=True,
    )
    new_password = serializers.CharField(
        required=True,
    )

    def validate_new_password(self, value):
        """Проверяет новый пароль."""
        validate_password(value)
        return value


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        """Метакласс тегов."""

        model = Tag
        fields = [
            'id',
            'name',
            'color',
            'slug'
        ]


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        """Метакласс ингредиентов."""

        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов в рецепте."""

    amount = serializers.IntegerField()
    name = serializers.ReadOnlyField(
        source='ingredient.name',
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        """Метакласс ингредиентов в рецепте."""

        model = RecipeIngredient
        fields = [
            'id',
            'amount',
            'name',
            'measurement_unit'
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""

    email = serializers.EmailField(source='author.email')
    id = serializers.IntegerField(source='author.id')
    username = serializers.CharField(source='author.username')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    is_subscribed = serializers.BooleanField(default=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        """Метакласс подписок."""

        model = Subscription
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        ]

    def get_recipes(self, obj):
        """Метод для получения списка рецептов пользователя."""
        recipes = Recipe.objects.filter(author=obj.author)
        serializers = RecipeSerializer(recipes, many=True)
        return serializers.data

    def get_queryset(self, queryset, name, value):
        """Метод для получения queryset с аннотацией количества рецептов."""
        return queryset.annotate(recipes_count=Count('author__recipe'))


class UserWithSubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя с подписками."""

    subscriptions = UserSerializer(many=True)

    class Meta:
        """Метакласс пользователя с подписками."""

        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'subscriptions',
        ]


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецепта."""

    class Meta:
        """Метакласс рецепта."""

        model = Recipe
        fields = [
            'id',
            'name',
            'image',
            'cooking_time'
        ]


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )

    class Meta:
        """Метакласс создания рецепта."""

        model = Recipe
        fields = [
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        ]

    def recipe_ingredients_set(self, recipe, ingredients):
        """Добавляет ингредиенты к рецепту."""
        recipe_ingredients = []

        for ingredient, amount in ingredients.values():
            recipe_ingredients.append(
                RecipeIngredient(
                    recipe=recipe, ingredient=ingredient, amount=amount
                )
            )

        RecipeIngredient.objects.bulk_create(recipe_ingredients)


class RecipeFullSerializer(serializers.ModelSerializer):
    """Сериализатор для полной информации о рецепте."""

    tags = TagSerializer(
        many=True,
    )
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='amount',
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
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
        ]

    def validate_cooking_time(self, value):
        """Время приготовления больше ли 0."""
        if value < 1:
            raise serializers.ValidationError(
                {'errors': 'Время приготовления должно быть больше 0..'}
            )

    def get_is_favorited(self, obj):
        """Добавлен ли рецепт в избранное для текущего пользователя."""
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.in_favorites.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        """Добавлен ли рецепт в корзину для текущего пользователя."""
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.in_carts.filter(user=request.user).exists()
