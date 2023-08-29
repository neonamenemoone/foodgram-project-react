from io import StringIO

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
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import Subscription, User

from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeFullSerializer,
    RecipeSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
    UserSetPasswordSerializer,
)


class UserView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [AllowAny]
    pagination_class = PageNumberPagination

    def create(self, request):
        serializer = UserRegistrationSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        return super().create(request)

    def perform_update(self, serializer):
        serializer.save()

    def retrieve(self, request, *args, **kwargs):
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)
        return super().retrieve(request)

    @action(
        detail=False, methods=["get"], permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        return Response(UserProfileSerializer(request.user).data)

    @action(
        detail=False, methods=["post"], permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        serializer = UserSetPasswordSerializer(data=self.request.data)
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
        self.queryset = Subscription.objects.filter(follower=request.user)
        self.serializer_class = SubscriptionSerializer
        return super().list(request)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, pk=None):
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
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]


class IngredientView(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [SearchFilter]
    search_fields = ["name"]


class RecipeView(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    queryset = Recipe.objects.all()
    serializer_class = RecipeFullSerializer
    permission_classes = [IsAuthorOrAdminOrReadOnly]
    filter_backends = [SearchFilter]
    search_fields = ["name", "author__username"]

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = RecipeCreateSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            recipe = serializer.save(author=request.user)
            response_serializer = RecipeFullSerializer(recipe)
            return Response(
                response_serializer.data, status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=["post", "delete"])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        user = request.user

        if user.is_authenticated:
            if request.method == "POST":
                if FavoriteRecipe.objects.filter(
                    user=user, recipe=recipe
                ).exists():
                    return Response(
                        {"errors": "Рецепт уже добавлен в избранное."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                FavoriteRecipe.objects.create(user=user, recipe=recipe)
                serializer = RecipeSerializer(recipe)
            elif request.method == "DELETE":
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

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"detail": "Пользователь не авторизован."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user

        if instance.author != user and not user.is_staff:
            return Response(
                {
                    "detail": "У вас недостаточно прав для выполнения данного действия."
                },
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
        instance = self.get_object()
        user = request.user

        if instance.author != user and not user.is_staff:
            return Response(
                {
                    "detail": "У вас недостаточно прав для удаления данного рецепта."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        user = request.user

        if not user.is_authenticated:
            return Response(
                {"detail": "Пользователь не авторизован."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        shopping_cart, created = ShoppingCart.objects.get_or_create(
            user=user, recipe=recipe, quantity=1
        )

        if request.method == "POST":
            if not created:
                return Response(
                    {"error": "Рецепт уже есть в вашем списке покупок."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"message": "Рецепт успешно добавлен в список покупок."},
                status=status.HTTP_201_CREATED,
            )

        if request.method == "DELETE":
            if not created:
                shopping_cart.delete()
                return Response(
                    {"message": "Рецепт успешно удален из списка покупок."},
                    status=status.HTTP_204_NO_CONTENT,
                )
            else:
                return Response(
                    {"error": "Рецепт не найден в вашем списке покупок."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

    @action(detail=False, methods=["get"])
    def download_shopping_cart(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return Response(
                {"detail": "Пользователь не авторизован."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        ingredients = (
            RecipeIngredient.objects.filter(recipe__shoppingcart__user=user)
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(total_quantity=Sum("quantity"))
        )

        txt_buffer = StringIO()
        txt_buffer.write("Список покупок:\n\n")

        for ingredient in ingredients:
            txt_buffer.write(
                f"- {ingredient['ingredient__name']}: {ingredient['total_quantity']} {ingredient['ingredient__measurement_unit']}\n"
            )

        txt_buffer.seek(0)
        response = HttpResponse(txt_buffer, content_type="text/plain")
        response[
            "Content-Disposition"
        ] = 'attachment; filename="shopping_list.txt"'
        return response
