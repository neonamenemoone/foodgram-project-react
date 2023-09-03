"""Модуль, содержащий модели Django-приложения users."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField(
        "Email",
        blank=False,
        null=False,
        unique=True,
    )
    username = models.CharField("Username", max_length=150, unique=True)
    first_name = models.CharField("Имя", max_length=150)
    last_name = models.CharField("Фамилия", max_length=150)
    is_subscribed = models.BooleanField("Подписан", default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        """Метакласс модели пользователя."""

        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        """Возвращает строковое представление объекта."""
        return self.username


class Subscription(models.Model):
    """Модель подписки."""

    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followers"
    )

    class Meta:
        """Метакласс модели подписки."""

        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        """Возвращает строковое представление объекта."""
        return f"{self.follower.username} follows {self.author.username}"
