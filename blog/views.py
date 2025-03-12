from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, filters, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import F, Q
from django.utils import timezone
from django.conf import settings
from .models import BlogCategory, Tag, BlogPost, Comment
from .serializers import (
    BlogCategorySerializer,
    TagSerializer,
    BlogPostListSerializer,
    BlogPostDetailSerializer,
    CommentSerializer
)

# Create your views here.

class BlogCategoryViewSet(viewsets.ModelViewSet):
    queryset = BlogCategory.objects.all()
    serializer_class = BlogCategorySerializer
    lookup_field = 'slug'
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['get'])
    def posts(self, request, slug=None):
        """Get all posts for a specific category"""
        category = self.get_object()
        posts = BlogPost.objects.filter(
            category=category,
            status='published'
        ).order_by('-created_at')
        serializer = BlogPostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['get'])
    def posts(self, request, slug=None):
        tag = self.get_object()
        posts = BlogPost.objects.filter(tags=tag, status='published')
        serializer = BlogPostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.filter(status='published')
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return BlogPostListSerializer
        return BlogPostDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by category if provided
        category_slug = self.request.query_params.get('category', None)
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        return queryset.order_by('-created_at')

    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular posts (currently returns most recent)"""
        posts = self.get_queryset().order_by('-created_at')[:5]
        serializer = BlogPostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def related(self, request, slug=None):
        """Get related posts based on category and tags"""
        post = self.get_object()
        related_posts = BlogPost.objects.filter(
            Q(category=post.category) | Q(tags__in=post.tags.all())
        ).exclude(
            id=post.id
        ).distinct()[:4]
        serializer = BlogPostListSerializer(related_posts, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def comments(self, request, slug=None):
        post = self.get_object()
        comments = post.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['get', 'post', 'delete']

    def perform_create(self, serializer):
        serializer.save()
