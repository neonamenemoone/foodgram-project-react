from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True)
    color = models.CharField(max_length=7)
    slug = models.SlugField(max_length=200, unique=True, null=True, validators=[RegexValidator(
        regex=r'^[-a-zA-Z0-9_]+$',
        message='Slug может содержать только буквы, цифры, дефисы и символ подчеркивания.',
        code='invalid_slug'
    )])

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=255, unique=True)
    measurement_unit = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='recipes/')
    description = models.TextField()
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredient')
    tags = models.ManyToManyField(Tag)
    cooking_time = models.PositiveIntegerField()

    def __str__(self):
        return self.title


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.recipe} - {self.ingredient}'
