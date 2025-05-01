from rest_framework import serializers
from .models import Recipe, Comment, SearchHistory, Favorite, RecentlyViewed, RecipeAttribute, RecipeStepImage
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

class RecipeStepImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeStepImage
        fields = ['image']

    def to_representation(self, instance):
        request = self.context.get('request')
        if instance.image and request:
            return request.build_absolute_uri(instance.image.url).replace('http://', 'https://')
        return instance.image.url if instance.image else None

class RecipeSerializer(serializers.ModelSerializer):
    attributes = RecipeAttributeSerializer(many=True, read_only=True)
    step_images = RecipeStepImageSerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'user', 'description', 'ingredients_list', 'instructions', 'image', 'step_images', 'step_instructions', 'cooking_time', 'calories', 'created_at', 'attributes']
        extra_kwargs = {'user': {'read_only': True}}

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url).replace('http://', 'https://')
        return obj.image.url if obj.image else None

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