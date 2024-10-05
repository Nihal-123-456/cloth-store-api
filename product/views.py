from django.shortcuts import render,redirect
from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from sslcommerz_lib import SSLCOMMERZ 
from django.contrib.auth.models import User
from user.models import Cart,Userinfo,OrderHistory,CartItem
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, authenticate
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_backends
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

def generate_transaction_id():
    return str(uuid.uuid4())

def get_cart_products(uid):
    cart = Cart.objects.get(user=uid)
    cart_products = cart.cart_items.all()
    products = ''
    for p in cart_products:
        products += f'{p.item.title},'
    return products  

def paymentgateway_view(request, uid):
    user = User.objects.get(id=uid)
    user_info = Userinfo.objects.get(user=uid)
    cart = Cart.objects.get(user=uid)
    settings = { 'store_id': 'nihal66962fa452342', 'store_pass': 'nihal66962fa452342@ssl', 'issandbox': True }
    sslcz = SSLCOMMERZ(settings)
    post_body = {}
    post_body['total_amount'] = cart.total_payment()
    post_body['currency'] = "BDT"
    post_body['tran_id'] = generate_transaction_id()
    post_body['success_url'] = request.build_absolute_uri(f'/product/paymentsuccess/{uid}')
    post_body['fail_url'] = "http://127.0.0.1:8000/product/"
    post_body['cancel_url'] = "http://127.0.0.1:8000/product/"
    post_body['emi_option'] = 0
    post_body['cus_name'] = f"{user.first_name} {user.last_name}"
    post_body['cus_email'] = user.email
    post_body['cus_phone'] = user_info.contact_number
    post_body['cus_add1'] = user_info.street_address
    post_body['cus_city'] = ""
    post_body['cus_country'] = ""
    post_body['shipping_method'] = "NO"
    post_body['multi_card_name'] = ""
    post_body['num_of_item'] = cart.cart_items.count()
    post_body['product_name'] = get_cart_products(uid)
    post_body['product_category'] = "general"
    post_body['product_profile'] = "general"


    response = sslcz.createSession(post_body)
    return redirect(response['GatewayPageURL'])
    # return JsonResponse({'payment_url': response['GatewayPageURL']})

@csrf_exempt
def paymentsuccess_view(request, uid):
    user = User.objects.get(id=uid)
    cart = Cart.objects.get(user=uid)
    cart_items = CartItem.objects.filter(cart=cart)

    for cart_item in cart_items:
        order = OrderHistory.objects.create(user=user, item=cart_item.item, quantity=cart_item.quantity,color=cart_item.color, size=cart_item.size, status = 'Pending')
        order.save()
    cart_items.delete()
    return redirect('http://127.0.0.1:5500/profile.html#orders')
    

    

    

