from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    email = models.EmailField('Email', unique=True)
    username = models.CharField('Username', max_length=150, unique=True)
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    is_subscribed = models.BooleanField('Подписан', default=False)


class Subscription(models.Model):

    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
