from django.shortcuts import render
from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticatedOrReadOnly
# Create your views here.

class CategoryView(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ColorView(viewsets.ModelViewSet):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class SizeView(viewsets.ModelViewSet):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ItemView(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        discount = self.request.query_params.get('discount')

        color_param = self.request.query_params.get('color')
        color = color_param.split(',')if color_param else []
        size_param = self.request.query_params.get('size')
        size = size_param.split(',')if size_param else []

        average_rating = self.request.query_params.get('average_rating')
        filter = self.request.query_params.get('filter')
        sort = self.request.query_params.get('sort')
        if category:
            queryset = queryset.filter(category__title=category)
        if discount:
            queryset = queryset.filter(discount=discount)

        if color:
            queryset = queryset.filter(color__title__in=color).distinct()
        if size:
            queryset = queryset.filter(size__title__in=size).distinct()

        if average_rating:
            queryset = queryset.annotate(avg_rating=Avg('reviews__rating'))
            queryset = queryset.filter(avg_rating__gte=average_rating)
        if filter:
            if filter == 'popularity':
                queryset = queryset.order_by('-sales_number')
            elif filter == 'latest':
                queryset = queryset.order_by('-entry_date')
        if sort:
            if sort == 'price_low_to_high':
                queryset = queryset.order_by('price')
            elif sort == 'price_high_to_low':
                queryset = queryset.order_by('-price')
        return queryset

class ReviewView(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.query_params.get('user')
        item = self.request.query_params.get('item')
        rating = self.request.query_params.get('rating')
        if user:
            queryset = queryset.filter(user__username = user)
        elif item:
            queryset = queryset.filter(item__title=item)
        elif rating:
            queryset = queryset.filter(rating=rating)
        return queryset

