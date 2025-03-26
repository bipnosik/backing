from rest_framework import serializers
from .models import Recipe, Comment, SearchHistory, Favorite, RecentlyViewed
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

class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'user', 'description', 'ingredients', 'instructions','image', 'cooking_time', 'calories', 'created_at']
        extra_kwargs = {'user': {'read_only': True}}

    def get_userCreated(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.user == request.user
        return False

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