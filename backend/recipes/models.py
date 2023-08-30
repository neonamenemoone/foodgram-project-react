"""Модуль, содержащий модели Django-приложения recipes."""
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import models


User = get_user_model()


class Tag(models.Model):
    """Модель для хранения информации о тегах."""

    name = models.CharField(max_length=200, unique=True)
    color = models.CharField(max_length=7)
    slug = models.SlugField(
        max_length=200,
        unique=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r"^[-a-zA-Z0-9_]+$",
                message="Slug не может содержать такие символы.",
                code="invalid_slug",
            )
        ],
    )

    def __str__(self):
        """Возвращает строковое представление объекта тега."""
        return self.name


class Ingredient(models.Model):
    """Модель для хранения информации об ингредиентах рецептов."""

    name = models.CharField(max_length=255)
    measurement_unit = models.CharField(max_length=50)
    amount = models.PositiveSmallIntegerField(
        null=False, blank=False, default=1
    )

    def __str__(self):
        """Возвращает строковое представление объекта ингредиента."""
        return self.name


class Recipe(models.Model):
    """Модель для хранения информации о рецептах."""

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="recipes/")
    description = models.TextField()
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient, through="RecipeIngredient"
    )
    tags = models.ManyToManyField(Tag)
    cooking_time = models.PositiveIntegerField()
    is_favorited = models.BooleanField(default=False)
    is_in_shopping_cart = models.BooleanField(default=False)

    def __str__(self):
        """Возвращает строковое представление объекта."""
        return self.name


class RecipeIngredient(models.Model):
    """Модель для хранения информации о ингредиентах в рецептах."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        """Возвращает строковое представление объекта."""
        return f"{self.recipe} - {self.ingredient}"


class FavoriteRecipe(models.Model):
    """Модель для хранения информации о рецептах, добавленных в избранное."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)


class ShoppingCart(models.Model):
    """Модель для рецептов, добавленных в список покупок."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    quantity = models.DecimalField(
        "Количество", max_digits=10, decimal_places=2
    )

    class Meta:
        """Метакласс модели списка покупок."""

        unique_together = ["user", "recipe"]
