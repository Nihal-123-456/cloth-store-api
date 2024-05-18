from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

class UserData(serializers.Serializer):
    username = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)

class UserinfoSerializer(serializers.ModelSerializer):
    user_data = UserData(source = 'user', read_only = True) 
    class Meta:
        model = Userinfo
        fields = '__all__'

class WishlistItemSerializer(serializers.ModelSerializer):
    buyer_name = serializers.CharField(source='user', read_only = True)
    item_name = serializers.CharField(source='item', read_only = True)
    item_image = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = WishlistItem
        fields = '__all__'
    
    def get_item_image(self, instance):
        request = self.context.get('request')
        if instance.item.images.exists():
            first_image = instance.item.images.first()
            return request.build_absolute_uri(first_image.image.url)
        return None
    
    def validate_item(self, value):
        qs = WishlistItem.objects.filter(item=value)
        if qs.exists():
            raise serializers.ValidationError(f"{value} already exists in your wishlist")
        return value

class OrderHistorySerializer(serializers.ModelSerializer):
    buyer_name = serializers.CharField(source='user', read_only = True)
    item_name = serializers.CharField(source='item', read_only = True)
    item_image = serializers.SerializerMethodField(read_only=True)
    total_item_price = serializers.IntegerField(read_only=True)
    class Meta:
        model = OrderHistory
        fields = '__all__'
    
    def get_item_image(self, instance):
        request = self.context.get('request')
        if instance.item.images.exists():
            first_image = instance.item.images.first()
            return request.build_absolute_uri(first_image.image.url)
        return None
    def validate(self, data):
        item = data.get('item')
        color = data.get('color')
        size = data.get('size')

        if color and not item.color.filter(title=color).exists():
            raise serializers.ValidationError(f'{color} color not available for this product.')
        if size and not item.size.filter(title=size).exists():
            raise serializers.ValidationError(f'{size} size not available for this product')
        return data   

class CartItemReadSerializer(serializers.ModelSerializer):
    item_image = serializers.SerializerMethodField(read_only=True)
    item_name = serializers.CharField(source='item', read_only=True)
    item_price = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = CartItem
        fields = ['item_name', 'item_image', 'quantity', 'item_price']
    
    def get_item_image(self, instance):
        request = self.context.get('request')
        if instance.item.images.exists():
            first_image = instance.item.images.first()
            return request.build_absolute_uri(first_image.image.url)
        return None
    
    def get_item_price(self, instance):
        if instance.item.discount == True:
            return ((instance.item.price) - (instance.item.price)*(instance.item.discount_percentage/100))
        return instance.item.price

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = '__all__'
    
    def create(self, validated_data):
        cart = validated_data['cart']
        item = validated_data['item']
        quantity = validated_data['quantity']

        existing_item = CartItem.objects.filter(cart=cart, item=item).first()
        if existing_item:
            existing_item.quantity += quantity
            existing_item.save()
            return existing_item
            
        new_item = CartItem.objects.create(cart=cart, item=item, quantity=quantity)
        return new_item

class CartSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user', read_only=True)
    cart_items = CartItemReadSerializer(many=True, read_only=True)
    total_payment = serializers.IntegerField(read_only=True)
    class Meta:
        model = Cart
        fields = '__all__'

class RegistrationSerializer(serializers.ModelSerializer):
    contact_number = serializers.IntegerField(required=True)
    street_address = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'confirm_password','contact_number', 'street_address']
    
    def save(self):
        first_name = self.validated_data['first_name']
        last_name = self.validated_data['last_name']
        email = self.validated_data['email']
        username = self.validated_data['username']
        password = self.validated_data['password']
        confirm_password = self.validated_data['confirm_password']
        contact_number = self.validated_data['contact_number']
        street_address = self.validated_data['street_address']

        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match")
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("An account with this username already exists")
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("An account with this email already exists")
        
        account = User(username=username, email=email, first_name=first_name, last_name=last_name)
        account.set_password(password)
        account.is_active = False
        account.save()
        userinfo = Userinfo(user = account, contact_number = contact_number, street_address = street_address)
        userinfo.save()
        cart = Cart(user = account)
        cart.save()

        return account

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

