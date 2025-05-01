from django.db import models
from django.contrib.auth.models import User

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username}: {self.query}"

class Recipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(default='No description provided')
    ingredients_list = models.JSONField(default=list)
    instructions = models.TextField(default='No instructions provided')
    step_instructions = models.JSONField(default=list)
    image = models.ImageField(upload_to='recipes/', null=True, blank=True)
    cooking_time = models.IntegerField(null=True, blank=True)
    calories = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class RecipeStepImage(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='step_images')
    image = models.ImageField(upload_to='recipes/steps/')


    def __str__(self):
        return f"Step image for {self.recipe.name}"

    class Meta:
        ordering = ['id']  # Изменил с '-created_at' на 'id', так как поле created_at отсутствует

class RecipeAttribute(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='attributes')
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name}: {self.value} for {self.recipe.name}"

class Comment(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author} on {self.recipe}'

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.username} - {self.recipe.name}"

class RecentlyViewed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recently_viewed')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-viewed_at']
        unique_together = ['user', 'recipe']

    def __str__(self):
        return f"{self.user.username} viewed {self.recipe.name}"