"""Модуль с представлениями API."""

from io import StringIO

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from django.db.models import Sum
from django.http import HttpResponse

from recipes.models import (
    FavoriteRecipe, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag,
)
from users.models import Subscription, User

from .filters import FavoriteAndShoppingCartFilter
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (
    ChangePasswordSerializer, IngredientSerializer, RecipeCreateSerializer,
    RecipeFullSerializer, RecipeSerializer, SubscriptionSerializer,
    TagSerializer, UserSerializer,
)


class UserView(viewsets.ModelViewSet):
    """Представление для пользователей."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    pagination_class = PageNumberPagination

    @action(
        detail=False, methods=["get"], permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        """Метод для информации о текущем пользователе."""
        return Response(UserSerializer(request.user).data)

    @action(
        detail=False, methods=["post"], permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        """Метод для изменения пароля пользователя."""
        serializer = ChangePasswordSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        if request.user.check_password(
            serializer.validated_data["current_password"]
        ):
            request.user.set_password(
                serializer.validated_data["new_password"]
            )
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise ValidationError("Текущий пароль неверный.")

    @action(
        detail=False, methods=["get"], permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """Метод для получения списка подписок пользователя."""
        self.queryset = Subscription.objects.filter(follower=request.user)
        self.serializer_class = SubscriptionSerializer
        return super().list(request)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, pk=None):
        """Метод для подписки и отписки пользователей."""
        if self.get_object() == request.user:
            return Response(
                {"error": "Вы не можете взаимодействовать с собой."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.method == "POST":
            if Subscription.objects.filter(
                follower=request.user, author=self.get_object()
            ).exists():
                return Response(
                    {"error": "Вы уже подписаны на этого пользователя."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            Subscription.objects.create(
                follower=request.user, author=self.get_object()
            )
            return Response(
                {"success": "Вы успешно подписались на пользователя."},
                status=status.HTTP_201_CREATED,
            )

        elif request.method == "DELETE":
            try:
                subscription = Subscription.objects.get(
                    follower=request.user, author=self.get_object()
                )
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Subscription.DoesNotExist:
                return Response(
                    {"error": "Вы не были подписаны на этого пользователя."},
                    status=status.HTTP_400_BAD_REQUEST,
                )


class TagView(viewsets.ModelViewSet):
    """Представление для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]


class IngredientView(viewsets.ModelViewSet):
    """Представление для ингредиентов."""

    permission_classes = [AllowAny]
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [SearchFilter]
    search_fields = ["name"]


class RecipeView(viewsets.ModelViewSet):
    """Представление для рецептов."""

    pagination_class = PageNumberPagination
    queryset = Recipe.objects.all()
    serializer_class = RecipeFullSerializer
    permission_classes = [IsAuthorOrAdminOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FavoriteAndShoppingCartFilter

    def get_serializer(self, *args, **kwargs):
        """Получение сериализатора с контекстом запроса."""
        return super().get_serializer(
            *args, **kwargs, context={"request": self.request}
        )

    def get_permissions(self):
        """Проверка аутентификации пользователя."""
        if self.action == "create":
            return [IsAuthenticated()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        """Метод создания рецепта."""
        serializer = RecipeCreateSerializer(
            data=request.data, context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        recipe = serializer.save(author=request.user)
        response_serializer = RecipeFullSerializer(recipe)
        return Response(
            response_serializer.data, status=status.HTTP_201_CREATED
        )

    @action(
        detail=True, methods=["post"], permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        """Метод для добавления рецепта в избранное."""
        recipe = self.get_object()
        user = request.user

        if FavoriteRecipe.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {"errors": "Рецепт уже добавлен в избранное."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        FavoriteRecipe.objects.create(user=user, recipe=recipe)
        serializer = RecipeSerializer(recipe)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def favorite_delete(self, request, pk):
        """Метод для удаления рецепта в избранное."""
        recipe = self.get_object()
        user = request.user

        try:
            favorite_recipe = FavoriteRecipe.objects.get(
                user=user, recipe=recipe
            )
            favorite_recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except FavoriteRecipe.DoesNotExist:
            return Response(
                {"errors": "Рецепт не найден в избранном."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def partial_update(self, request, *args, **kwargs):
        """Метод для изменения рецепта."""
        instance = self.get_object()
        user = request.user

        if instance.author != user and not user.is_staff:
            return Response(
                {"detail": "У вас недостаточно прав для данного действия."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = RecipeCreateSerializer(
            instance,
            data=request.data,
            context={"request": request},
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()
            response_serializer = RecipeFullSerializer(instance)
            return Response(
                response_serializer.data, status=status.HTTP_200_OK
            )
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        """Метод для удаления рецепта."""
        instance = self.get_object()
        user = request.user

        if instance.author != user and not user.is_staff:
            return Response(
                {"detail": "У вас недостаточно прав для удаления."},
                status=status.HTTP_403_FORBIDDEN,
            )

        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        """Метод для добавления рецепта в список покупок."""
        recipe = self.get_object()
        user = request.user

        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {"errors": "Рецепт уже добавлен в список покупок."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ShoppingCart.objects.create(user=user, recipe=recipe)
        serializer = RecipeSerializer(recipe)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @shopping_cart.mapping.delete
    def shopping_cart_delete(self, request, pk):
        """Метод для удаления рецепта из списка покупок."""
        recipe = self.get_object()
        user = request.user
        try:
            shopping_cart = ShoppingCart.objects.get(user=user, recipe=recipe)

            shopping_cart.delete()
            return Response(
                {"message": "Рецепт успешно удален из списка покупок."},
                status=status.HTTP_204_NO_CONTENT,
            )

        except ShoppingCart.DoesNotExist:
            return Response(
                {"errors": "Рецепт не найден в списке покупок."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["get"])
    def download_shopping_cart(self, request, *args, **kwargs):
        """Метод для скачивания списка покупок."""
        user = request.user

        if not user.is_authenticated:
            return Response(
                {"detail": "Пользователь не авторизован."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        ingredients = (
            RecipeIngredient.objects.filter(recipe__in_carts__user=user)
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(total_quantity=Sum("amount"))
        )

        txt_buffer = StringIO()
        txt_buffer.write("Список покупок:\n\n")

        for ingredient in ingredients:
            txt_buffer.write(
                f"- {ingredient['ingredient__name']}: "
                f"{ingredient['total_quantity']} "
                f"{ingredient['ingredient__measurement_unit']}\n"
            )

        txt_buffer.seek(0)
        response = HttpResponse(txt_buffer, content_type="text/plain")
        response[
            "Content-Disposition"
        ] = 'attachment; filename="shopping_list.txt"'
        return response
