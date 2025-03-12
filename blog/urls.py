from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BlogPostViewSet, BlogCategoryViewSet, TagViewSet, CommentViewSet

router = DefaultRouter()
router.register(r'categories', BlogCategoryViewSet, basename='category')
router.register(r'posts', BlogPostViewSet, basename='post')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
] 