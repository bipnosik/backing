# SiteC/MeowSite/SiteC/recipes/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RecipeViewSet, CommentViewSet, SearchHistoryViewSet,
    FavoriteListCreateView, FavoriteDeleteView, RecentlyViewedViewSet, UserCreateView
)

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'search-history', SearchHistoryViewSet)
router.register(r'recently-viewed', RecentlyViewedViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('favorites/', FavoriteListCreateView.as_view(), name='favorite-list-create'),
    path('favorites/<int:pk>/', FavoriteDeleteView.as_view(), name='favorite-delete'),
    path('register/', UserCreateView.as_view(), name='user-register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]