# Generated by Django 5.1.6 on 2025-05-01 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0009_alter_recipe_options_remove_recipe_step_images_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='step_instructions',
            field=models.JSONField(default=list),
        ),
    ]
