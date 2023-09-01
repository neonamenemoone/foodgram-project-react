"""Модуль фильтрации API."""
from django_filters import rest_framework as django_filters

from django.contrib.auth import get_user_model

from recipes.models import Recipe, Tag


User = get_user_model()


class FavoriteAndShoppingCartFilter(django_filters.FilterSet):
    """Фильтрация избранного и списка покупок."""

    tags = django_filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all(),
    )
    author = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    is_in_shopping_cart = django_filters.NumberFilter(method="get_queryset")
    is_favorited = django_filters.NumberFilter(method="get_queryset")

    def get_queryset(self, queryset, name, value):
        """Определяет, какие объекты следует фильтровать."""
        if name == "is_in_shopping_cart":
            return queryset.filter(in_carts__user=self.request.user)
        if name == "is_favorited":
            return queryset.filter(in_favorites__user=self.request.user)
        return queryset

    class Meta:
        """Метакласс фильтра."""

        model = Recipe
        fields = ("tags", "author", "is_favorited", "is_in_shopping_cart")
