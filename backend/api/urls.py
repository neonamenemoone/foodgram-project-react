"""Модуль urls определяет маршруты для страниц API."""

from rest_framework.routers import DefaultRouter

from django.urls import include, path, re_path

from .views import IngredientView, RecipeView, TagView, UserView


router = DefaultRouter()
router.register(r"users", UserView)
router.register(r"tags", TagView)
router.register(r"ingredients", IngredientView, basename="ingredient")
router.register(r"recipes", RecipeView)

app_name = "api"

urlpatterns = [
    path("", include(router.urls)),
    re_path("^auth/", include("djoser.urls.authtoken")),
    path("", UserView.as_view({"get": "me"})),
    path("", UserView.as_view({"post": "set_password"})),
    path("", UserView.as_view({"get": "subscriptions"})),
    path(
        "<int:pk>/subscribe/",
        UserView.as_view({"post": "subscribe", "delete": "subscribe"}),
        name="subscribe",
    ),
    path(
        "<int:pk>/favorite/",
        RecipeView.as_view({"post": "favorite"}),
        name="favorite",
    ),
    path(
        "<int:pk>/recipes/",
        RecipeView.as_view({"post": "create"}),
        name="create_recipe",
    ),
    path(
        "<int:pk>/shopping_cart/",
        RecipeView.as_view(
            {"post": "shopping_cart", "delete": "shopping_cart"},
            name="shopping_cart",
        ),
    ),
    path(
        "download_shopping_cart/",
        RecipeView.as_view({"get": "download_shopping_cart"}),
        name="download_shopping_cart",
    ),
]
