from os.path import basename

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, RegisterView, CommentViewSet, SearchHistoryViewSet, FavoriteListCreateView, FavoriteDeleteView

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'search-history', SearchHistoryViewSet, basename='search-history')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('favorites/', FavoriteListCreateView.as_view(), name='favorite-list-create'),
    path('favorites/<int:recipe_id>/', FavoriteDeleteView.as_view(), name='favorite-delete'),
]