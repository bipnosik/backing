# SiteC/MeowSite/SiteC/recipes/serializers.py
from rest_framework import serializers
from .models import Recipe, Comment, SearchHistory, Favorite, RecentlyViewed, RecipeAttribute
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user

class RecipeAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeAttribute
        fields = ['id', 'name', 'value']

class RecipeSerializer(serializers.ModelSerializer):
  attributes = RecipeAttributeSerializer(many=True, read_only=True)
  image = serializers.SerializerMethodField()
  step_images = serializers.SerializerMethodField()
  user = serializers.CharField(source='user.username', read_only=True)

  class Meta:
    model = Recipe
    fields = ['id', 'name', 'user', 'description', 'ingredients_list', 'instructions', 'image', 'step_images', 'cooking_time', 'calories', 'created_at', 'attributes']
    extra_kwargs = {'user': {'read_only': True}}

  def get_image(self, obj):
    if obj.image:
      request = self.context.get('request')
      # Принудительно используем HTTPS
      return request.build_absolute_uri(obj.image.url).replace('http://', 'https://') if request else obj.image.url
    return None

  def get_step_images(self, obj):
    if obj.step_images:
      request = self.context.get('request')
      # Принудительно используем HTTPS для всех пошаговых изображений
      return [request.build_absolute_uri(img).replace('http://', 'https://') if request else img for img in obj.step_images]
    return []

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Comment
        fields = ['id', 'recipe', 'author', 'text', 'created_at']
        read_only_fields = ['author', 'created_at']

class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = ['query']

class FavoriteSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'recipe', 'added_at']

class RecentlyViewedSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializer(read_only=True)

    class Meta:
        model = RecentlyViewed
        fields = ['id', 'recipe', 'viewed_at']