from django.db.models import Model
from rest_framework import viewsets, status, generics, permissions, filters
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.filters import SearchFilter
from django.db.models import Q
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Recipe, Comment, SearchHistory, Favorite
from .serializers import RecipeSerializer, UserSerializer, CommentSerializer, SearchHistorySerializer, FavoriteSerializer


class FavoriteListCreateView(generics.ListCreateAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        recipe_id = request.data.get('recipe_id')
        if not recipe_id:
            return Response({"error": "Recipe ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            recipe = Recipe.objects.get(id=recipe_id)
            favorite, created = Favorite.objects.get_or_create(user=request.user, recipe=recipe)
            if created:
                return Response(FavoriteSerializer(favorite).data, status=status.HTTP_201_CREATED)
            return Response({"message": "Recipe already in favorites"}, status=status.HTTP_200_OK)
        except Recipe.DoesNotExist:
            return Response({"error": "Recipe not found"}, status=status.HTTP_404_NOT_FOUND)


class FavoriteDeleteView(generics.DestroyAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def get_object(self):
        recipe_id = self.kwargs.get('recipe_id')
        return get_object_or_404(Favorite, user=self.request.user, recipe__id=recipe_id)

class SearchHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = SearchHistorySerializer
    permission_classes = [IsAuthenticated]  # Только авторизованные пользователи

    def get_queryset(self):
        # Возвращаем последние 20 запросов текущего пользователя
        return SearchHistory.objects.filter(user=self.request.user)[:20]

    def perform_create(self, serializer):
        # При создании записи автоматически привязываем текущего пользователя
        serializer.save(user=self.request.user)

class RecipeViewSet(viewsets.ModelViewSet):

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


    def get_queryset(self):
        queryset = Recipe.objects.all()
        search_query = self.request.query_params.get('search', None)
        if search_query:
            # Поиск без учета регистра по всем указанным полям
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(ingredients__icontains=search_query)
            )
        return queryset

    def list(self, request, *args, **kwargs):
        print("Запрос к /api/recipes/")
        print("Параметры запроса:", request.query_params)
        queryset = self.filter_queryset(self.get_queryset())
        print("Отфильтрованный queryset:", queryset)

    queryset = Recipe.objects.all()  # Все рецепты по умолчанию
    serializer_class = RecipeSerializer  # Сериализатор для рецептов
    parser_classes = (MultiPartParser, FormParser)  # Поддержка multipart/form-data для загрузки изображений
    permission_classes = [IsAuthenticatedOrReadOnly]  # Чтение — всем, запись — авторизованным

    def get_queryset(self):
        # Возвращаем все рецепты для списка
        return Recipe.objects.all()

    def list(self, request, *args, **kwargs):
        # Вывод списка всех рецептов
        print("Запрос к /api/recipes/")  # Лог для отладки
        queryset = self.get_queryset()

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)  # Возвращаем сериализованные данные

    def retrieve(self, request, pk=None, *args, **kwargs):
        # Получение конкретного рецепта по ID
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = self.serializer_class(recipe)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # Создание нового рецепта
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Автоматически привязываем текущего пользователя
            return Response(serializer.data, status=status.HTTP_201_CREATED)  # Успешное создание
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Ошибка валидации

    def update(self, request, pk=None, *args, **kwargs):
        # Обновление рецепта
        recipe = get_object_or_404(Recipe, pk=pk)
        # Проверяем, что пользователь — владелец рецепта
        if recipe.user != request.user:
            return Response({"detail": "You do not have permission to edit this recipe."}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.serializer_class(recipe, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # Сохраняем изменения
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None, *args, **kwargs):
        # Удаление рецепта
        recipe = get_object_or_404(Recipe, pk=pk)
        # Проверяем, что пользователь — владелец рецепта
        if recipe.user != request.user:
            return Response({"detail": "You do not have permission to delete this recipe."}, status=status.HTTP_403_FORBIDDEN)
        recipe.delete()  # Удаляем рецепт
        return Response(status=status.HTTP_204_NO_CONTENT)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()  # Все пользователи
    permission_classes = (permissions.AllowAny,)  # Доступ всем (регистрация)
    serializer_class = UserSerializer  # Сериализатор для пользователей

    def create(self, request, *args, **kwargs):
        # Создание нового пользователя
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()  # Сохраняем пользователя
        refresh = RefreshToken.for_user(user)  # Генерируем токены
        return Response({
            'refresh': str(refresh),
            "access": str(refresh.access_token),
        })  # Возвращаем токены

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()  # Все комментарии
    serializer_class = CommentSerializer  # Сериализатор для комментариев
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Чтение — всем, запись — авторизованным

    def perform_create(self, serializer):
        # Привязываем текущего пользователя как автора комментария
        serializer.save(author=self.request.user)

    def get_queryset(self):
        # Фильтрация комментариев по ID рецепта из параметров запроса
        recipe_id = self.request.query_params.get('recipe', None)
        if recipe_id is not None:
            return Comment.objects.filter(recipe_id=recipe_id)
        return Comment.objects.all()