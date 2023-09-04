"""Модуль admin определяет настройки для административной части."""

from typing import Any

from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest

from .models import (
    FavoriteRecipe, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag,
)


class RecipeIngredientInline(admin.TabularInline):
    """Первый кастомный админский класс для модели Рецепт-ингридиент."""

    model = RecipeIngredient
    extra = 1


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Второй кастомный админский класс для модели Рецепт-ингридиент."""


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Кастомный админский класс для модели Рецепт."""

    list_display = ("name", "author")
    list_filter = ("author", "name", "tags")
    search_fields = ("name", "author__email", "author__username")

    inlines = [RecipeIngredientInline]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        """Получает кастомный QuerySet для списка рецептов в админке."""
        return (
            Recipe.objects.prefetch_related("tags")
            .prefetch_related("ingredients")
            .select_related("author")
            .all()
        )

    def get_favorite_count(self, obj):
        """Количество добавлений в избранное для данного рецепта."""
        return obj.favorite_set.count()

    get_favorite_count.short_description = "Добавления в избранное"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Кастомный админский класс для модели Тег."""

    list_display = ("name", "color", "slug")
    list_filter = ("name",)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Кастомный админский класс для модели Ингредиент."""

    list_display = ("name", "measurement_unit")
    list_filter = ("name",)


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    """Кастомный админский класс для модели Избранных рецептов."""

    list_display = ("user", "recipe")
    list_filter = ("user", "recipe")
    search_fields = ("user__username", "recipe__name")

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        """Получает кастомный QuerySet для списка избранных рецептов."""
        return FavoriteRecipe.objects.select_related("user", "recipe").all()


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Кастомный админский класс для модели Списка покупок."""

    list_display = ("user", "recipe")
    list_filter = ("user", "recipe")
    search_fields = ("user__username", "recipe__name")

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        """Получает кастомный QuerySet для списка покупок."""
        return ShoppingCart.objects.select_related("user", "recipe").all()
