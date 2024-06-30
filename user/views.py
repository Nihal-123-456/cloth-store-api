from django.shortcuts import render, redirect
from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.views import APIView, View
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import status
# Create your views here.

class UserinfoView(viewsets.ModelViewSet):
    queryset = Userinfo.objects.all()
    serializer_class = UserinfoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.query_params.get('user')
        if user:
            queryset = queryset.filter(user = user)
        return queryset

class WishlistItemView(viewsets.ModelViewSet):
    queryset = WishlistItem.objects.all()
    serializer_class = WishlistItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.query_params.get('user')
        if user:
            queryset = queryset.filter(user = user)
        return queryset

class OrderHistoryView(viewsets.ModelViewSet):
    queryset = OrderHistory.objects.all()
    serializer_class = OrderHistorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.query_params.get('user')
        if user:
            queryset = queryset.filter(user = user)
        return queryset
    
    def perform_create(self, serializer):
        instance = serializer.save()
        self.send_order_confirmation_email(instance)
        self.update_sales_number(instance)
    
    def perform_update(self, serializer):
        instance = serializer.save()
        self.send_order_status_change_email(instance)

    def send_order_confirmation_email(self, instance):
        email_subject = f'Order Confirmation - Order #{instance.id}'
        email_body = render_to_string('order_email.html', {'order': instance})
        email = EmailMultiAlternatives(email_subject, '', to=[instance.user.email])
        email.attach_alternative(email_body, 'text/html')
        email.send()
    
    def send_order_status_change_email(self, instance):
        if instance.status == "Confirmed" or instance.status == "Delivered":
            email_subject = f'Order status updated - Order #{instance.id}'
            email_body = render_to_string('status_change_email.html', {'order': instance})
            email = EmailMultiAlternatives(email_subject, '', to=[instance.user.email])
            email.attach_alternative(email_body, 'text/html')
            email.send()

    def update_sales_number(self, instance):
        item = instance.item
        item.sales_number += instance.quantity
        item.save()   

class CartView(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.query_params.get('user')
        if user:
            queryset = queryset.filter(user=user)
        return queryset

class CartItemView(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        cart = self.request.query_params.get('cart')
        if cart:
            queryset = queryset.filter(cart__user=cart)
        return queryset

class RegistrationView(APIView):
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            confirm_link = request.build_absolute_uri(f'/user/active/{uid}/{token}') 
            email_subject = 'Confirmation Email'
            email_body = render_to_string('confirm_email.html', {'confirm_link':confirm_link} )
            email = EmailMultiAlternatives(email_subject, '', to=[user.email])
            email.attach_alternative(email_body, 'text/html')
            email.send()
            return Response('Check your email for confirmation link')
        return Response(serializer.errors)

def activate(self, uid64, token):
    try:
        uid = urlsafe_base64_decode(uid64).decode()
        user = User._default_manager.get(pk=uid)
    except(User.DoesNotExist):
        user=None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('https://cloth-store-api.onrender.com/user/')
    else:
        return redirect('https://cloth-store-api.onrender.com/user/')

class LoginView(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer =  self.serializer_class(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                login(request, user)
                return Response({'token':token.key, 'uid':user.id})
            else:
                return Response('Invalid username or password')
        return Response(serializer.errors)

class LogoutView(APIView):
    def get(self, request):
        request.user.auth_token.delete()
        logout(request)
        return redirect(request.build_absolute_uri('/user'))

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            new_password = serializer.validated_data['new_password']
            user.set_password(new_password)
            user.save()

            email_subject = f'Password changed successfully'
            email_body = render_to_string('password_change.html', {'user': user})
            email = EmailMultiAlternatives(email_subject, '', to=[user.email])
            email.attach_alternative(email_body, 'text/html')
            email.send()
            
            user = authenticate(username=user.username, password=new_password)
            if user is not None:
                login(request, user)
                return Response({'detail': 'Password changed successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Re-authentication failed'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ForgetPasswordView(APIView):
    serializer_class = ForgetPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            password_reset_link = request.build_absolute_uri(f'/user/password_reset/{uid}/{token}')
            email_subject = 'Password Reset Email'
            email_body = render_to_string('password_reset.html', {'password_reset_link':password_reset_link})
            email = EmailMultiAlternatives(email_subject, '', to=[email])
            email.attach_alternative(email_body, 'text/html')
            email.send()
            return Response("A link has been sent your email for changing password")
        return Response(serializer.errors)

class PasswordResetView(APIView):
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            uid = kwargs.get('uid')
            token = kwargs.get('token')

            try:
                user_id = urlsafe_base64_decode(uid).decode()
                user = User.objects.get(pk=user_id)
            except (User.DoesNotExist, ValueError, TypeError, OverflowError):
                user = None
            
            if user is not None and default_token_generator.check_token(user, token):
                new_password = serializer.validated_data['new_password']
                user.set_password(new_password)
                user.save()

                email_subject = f'Password changed successfully'
                email_body = render_to_string('password_change.html', {'user': user})
                email = EmailMultiAlternatives(email_subject, '', to=[user.email])
                email.attach_alternative(email_body, 'text/html')
                email.send()
                
                return Response("password successfully changed. please log in.")

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




