"""Модуль, содержащий модели Django-приложения users."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField('Email', unique=True)
    username = models.CharField('Username', max_length=150, unique=True)
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    is_subscribed = models.BooleanField('Подписан', default=False)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель подписки."""

    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followers'
    )

    def __str__(self):
        return f'{self.follower.username} follows {self.author.username}'
