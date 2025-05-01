from django.db.models import Q
from rest_framework import viewsets, status, generics, permissions
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Recipe, Comment, SearchHistory, Favorite, RecentlyViewed, RecipeAttribute, RecipeStepImage
from .serializers import (
    RecipeSerializer, UserSerializer, CommentSerializer,
    SearchHistorySerializer, FavoriteSerializer, RecentlyViewedSerializer
)
import json

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_queryset(self):
        queryset = Recipe.objects.all()
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(ingredients_list__icontains=search_query)
            )
        return queryset

    def list(self, request, *args, **kwargs):
        print("Запрос к /api/recipes/")
        print("Параметры запроса:", request.query_params)
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.serializer_class(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = self.serializer_class(recipe, context={'request': request})
        if request.user.is_authenticated:
            RecentlyViewed.objects.create(user=request.user, recipe=recipe)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        step_images = []
        step_instructions = []

        # Собираем пошаговые изображения
        for i in range(10):
            step_image_key = f'step_image_{i}'
            if step_image_key in request.FILES:
                step_images.append(request.FILES[step_image_key])

        # Собираем пошаговые инструкции
        for i in range(10):
            step_instruction_key = f'step_instruction_{i}'
            if step_instruction_key in request.POST:
                step_instructions.append(request.POST[step_instruction_key])

        # Добавляем step_instructions в data
        data['step_instructions'] = json.dumps(step_instructions, ensure_ascii=False)

        # Удаляем step_images из data, так как они обрабатываются отдельно
        if 'step_images' in data:
            data.pop('step_images')

        serializer = self.serializer_class(data=data, context={'request': request})
        if serializer.is_valid():
            recipe = serializer.save(user=request.user)
            if 'image' in request.FILES:
                recipe.image = request.FILES['image']
                recipe.save()

            # Сохраняем пошаговые изображения
            for img in step_images:
                RecipeStepImage.objects.create(recipe=recipe, image=img)

            # Обрабатываем атрибуты
            for key, value in data.items():
                if key.startswith('attribute_name_'):
                    idx = key.replace('attribute_name_', '')
                    attr_name = value
                    attr_value = data.get(f'attribute_value_{idx}', '')
                    if attr_name and attr_value:
                        RecipeAttribute.objects.create(recipe=recipe, name=attr_name, value=attr_value)

            response_serializer = self.serializer_class(recipe, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        print("Ошибки сериализатора:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=pk)
        if recipe.user != request.user:
            return Response({"detail": "У вас нет прав для редактирования этого рецепта."},
                            status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        step_images = []
        step_instructions = []

        # Собираем пошаговые изображения
        for i in range(10):
            step_image_key = f'step_image_{i}'
            if step_image_key in request.FILES:
                step_images.append(request.FILES[step_image_key])

        # Собираем пошаговые инструкции
        for i in range(10):
            step_instruction_key = f'step_instruction_{i}'
            if step_instruction_key in request.POST:
                step_instructions.append(request.POST[step_instruction_key])

        # Добавляем step_instructions в data
        data['step_instructions'] = step_instructions

        # Удаляем step_images из data
        if 'step_images' in data:
            data.pop('step_images')

        serializer = self.serializer_class(recipe, data=data, partial=True, context={'request': request})
        if serializer.is_valid():
            recipe = serializer.save()
            if 'image' in request.FILES:
                recipe.image = request.FILES['image']
                recipe.save()

            # Удаляем старые пошаговые изображения и добавляем новые
            if step_images:
                recipe.step_images.all().delete()
                for img in step_images:
                    RecipeStepImage.objects.create(recipe=recipe, image=img)

            # Обновляем атрибуты
            recipe.attributes.all().delete()
            for key, value in data.items():
                if key.startswith('attribute_name_'):
                    idx = key.replace('attribute_name_', '')
                    attr_name = value
                    attr_value = data.get(f'attribute_value_{idx}', '')
                    if attr_name and attr_value:
                        RecipeAttribute.objects.create(recipe=recipe, name=attr_name, value=attr_value)

            response_serializer = self.serializer_class(recipe, context={'request': request})
            return Response(response_serializer.data)
        print("Ошибки сериализатора:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=pk)
        if recipe.user != request.user:
            return Response(
                {"detail": "У вас нет прав для удаления этого рецепта."},
                status=status.HTTP_403_FORBIDDEN
            )
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        recipe_id = self.request.query_params.get('recipe', None)
        if recipe_id is not None:
            return Comment.objects.filter(recipe_id=recipe_id)
        return Comment.objects.all()

class SearchHistoryViewSet(viewsets.ModelViewSet):
    queryset = SearchHistory.objects.all()
    serializer_class = SearchHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SearchHistory.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class FavoriteListCreateView(generics.ListCreateAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        recipe_id = self.request.data.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        serializer.save(user=self.request.user, recipe=recipe)

class FavoriteDeleteView(generics.DestroyAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

class RecentlyViewedViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RecentlyViewed.objects.all()
    serializer_class = RecentlyViewedSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RecentlyViewed.objects.filter(user=self.request.user)

class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]