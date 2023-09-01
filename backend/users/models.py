"""Модуль, содержащий модели Django-приложения users."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя."""


class Subscription(models.Model):
    """Модель подписки."""

    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followers"
    )
