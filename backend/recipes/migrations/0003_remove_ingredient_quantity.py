# Generated by Django 3.2.3 on 2023-08-27 06:43

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0002_ingredient_quantity"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="ingredient",
            name="quantity",
        ),
    ]
