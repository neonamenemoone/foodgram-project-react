# Generated by Django 3.2.3 on 2023-08-29 18:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0014_shoppingcart"),
    ]

    operations = [
        migrations.AddField(
            model_name="shoppingcart",
            name="quantity",
            field=models.DecimalField(
                decimal_places=2, default=1, max_digits=10, verbose_name="Количество"
            ),
            preserve_default=False,
        ),
    ]