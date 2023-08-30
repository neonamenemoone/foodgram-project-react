"""Модуль admin определяет настройки для административной части."""

from django.contrib import admin

from .models import Ingredient, Recipe, RecipeIngredient, Tag


class RecipeIngredientInline(admin.TabularInline):
    """Кастомный админский класс для модели Рецепт-ингридиент."""

    model = RecipeIngredient
    extra = 1
    fields = ["ingredient", "quantity"]


class RecipeAdmin(admin.ModelAdmin):
    """Кастомный админский класс для модели Рецепт."""

    list_display = ("name", "author")
    list_filter = ("author", "name", "tags")
    search_fields = ("name", "author__email", "author__username")
    inlines = [RecipeIngredientInline]

    def get_favorite_count(self, obj):
        return obj.favorite_set.count()

    get_favorite_count.short_description = "Добавления в избранное"


class TagAdmin(admin.ModelAdmin):
    """Кастомный админский класс для модели Тег."""

    list_display = ("name", "color", "slug")
    list_filter = ("name",)


class IngredientAdmin(admin.ModelAdmin):
    """Кастомный админский класс для модели Ингредиент."""

    list_display = ("name", "measurement_unit")
    list_filter = ("name",)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
