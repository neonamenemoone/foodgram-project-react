# Generated by Django 3.2.3 on 2023-08-29 18:16

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0004_user_shopping_cart"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="favorite_recipes",
        ),
        migrations.RemoveField(
            model_name="user",
            name="shopping_cart",
        ),
    ]