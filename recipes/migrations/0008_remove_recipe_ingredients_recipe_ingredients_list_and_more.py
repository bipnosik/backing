import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_recipe_instructions'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='ingredients',
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients_list',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='recipe',
            name='step_images',
            field=models.JSONField(default=list),
        ),
        migrations.CreateModel(
            name='RecipeAttribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('value', models.CharField(max_length=50)),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attributes', to='recipes.recipe')),
            ],
        ),
    ]