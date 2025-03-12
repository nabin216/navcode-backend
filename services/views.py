from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import ServiceCategory, Service
from .serializers import ServiceCategoryListSerializer, ServiceCategoryDetailSerializer, ServiceSerializer

# Create your views here.

class ServiceCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ServiceCategory.objects.filter(is_active=True)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ServiceCategoryListSerializer
        return ServiceCategoryDetailSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().prefetch_related('services')
        serializer = ServiceCategoryDetailSerializer(queryset, many=True)
        return Response(serializer.data)

class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.request.query_params.get('category', None)
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset
