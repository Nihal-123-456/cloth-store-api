from django.shortcuts import render,redirect
from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from sslcommerz_lib import SSLCOMMERZ 
from django.contrib.auth.models import User
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

        color_param = self.request.query_params.get('color')
        color = color_param.split(',')if color_param else []
        size_param = self.request.query_params.get('size')
        size = size_param.split(',')if size_param else []

        average_rating = self.request.query_params.get('average_rating')
        sort = self.request.query_params.get('sort')
        if category:
            queryset = queryset.filter(category__title=category)

        if color:
            queryset = queryset.filter(color__title__in=color).distinct()
        if size:
            queryset = queryset.filter(size__title__in=size).distinct()

        if average_rating:
            queryset = queryset.annotate(avg_rating=Avg('reviews__rating'))
            queryset = queryset.filter(avg_rating__gte=average_rating)

        if sort:
            if sort == 'price_low_to_high':
                queryset = queryset.order_by('price')
            elif sort == 'price_high_to_low':
                queryset = queryset.order_by('-price')
            elif sort == 'popularity':
                queryset = queryset.order_by('-sales_number')
            elif sort == 'latest':
                queryset = queryset.order_by('-entry_date')
            elif sort == 'discount':
                queryset = queryset.filter(discount=True)
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
            queryset = queryset.filter(user = user)
        elif item:
            queryset = queryset.filter(item = item)
        elif rating:
            queryset = queryset.filter(rating=rating)
        return queryset

def paymentgateway_view(request, uid):
    user = User.objects.get(id=uid)
    settings = { 'store_id': 'nihal66962fa452342', 'store_pass': 'nihal66962fa452342@ssl', 'issandbox': True }
    sslcz = SSLCOMMERZ(settings)
    post_body = {}
    post_body['total_amount'] = 100.26
    post_body['currency'] = "BDT"
    post_body['tran_id'] = "12345"
    post_body['success_url'] = "your success url"
    post_body['fail_url'] = "your fail url"
    post_body['cancel_url'] = "your cancel url"
    post_body['emi_option'] = 0
    post_body['cus_name'] = "test"
    post_body['cus_email'] = "test@test.com"
    post_body['cus_phone'] = "01700000000"
    post_body['cus_add1'] = "customer address"
    post_body['cus_city'] = "Dhaka"
    post_body['cus_country'] = "Bangladesh"
    post_body['shipping_method'] = "NO"
    post_body['multi_card_name'] = ""
    post_body['num_of_item'] = 1
    post_body['product_name'] = "Test"
    post_body['product_category'] = "Test Category"
    post_body['product_profile'] = "general"


    response = sslcz.createSession(post_body)
    return redirect(response['GatewayPageURL'])
