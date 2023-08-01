# Generated by Django 3.2.16 on 2023-07-31 14:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeingredient',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ingredient_recipe', to='recipes.ingredient', verbose_name='Ингредиент'),
        ),
    ]
