from rest_framework import serializers
from .models import *

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
    
    def validate_title(self, value):
        qs = Category.objects.filter(title__iexact=value)
        if qs.exists():
            raise serializers.ValidationError(f"{value} already exists")
        return value

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = '__all__'
    
    def validate_title(self, value):
        qs = Color.objects.filter(title__iexact=value)
        if qs.exists():
            raise serializers.ValidationError(f"{value} already exists")
        return value

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = '__all__'
    
    def validate_title(self, value):
        qs = Size.objects.filter(title__iexact=value)
        if qs.exists():
            raise serializers.ValidationError(f"{value} already exists")
        return value

class ItemImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemImage
        fields = ['image',]

class ItemSerializer(serializers.ModelSerializer):
    average_rating = serializers.FloatField(read_only=True)
    discount_price = serializers.IntegerField(read_only=True)
    category_name = serializers.CharField(source='category', read_only=True)
    color_list = serializers.SerializerMethodField()
    size_list = serializers.SerializerMethodField()
    images = ItemImageSerializer(many=True, read_only=True)
    class Meta:
        model = Item
        fields = '__all__'
    
    def get_color_list(self, obj):
        return [color.title for color in obj.color.all()]
    
    def get_size_list(self, obj):
        return [size.title for size in obj.size.all()]
    
    def validate(self, attrs):
        discount = attrs.get('discount')
        discount_percentage = attrs.get('discount_percentage')
        title = attrs.get('title')

        if not discount and discount_percentage is not None:
            raise serializers.ValidationError("Discount percentage cannot be entered when discount is False.")
        elif Item.objects.filter(title__iexact=title).exists():
            raise serializers.ValidationError(f"{title} already exists")
        
        return attrs
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not data.get('discount'):
            data.pop('discount_percentage', None)
            data.pop('discount_price', None)
        return data

class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user', read_only=True)
    class Meta:
        model = Review
        fields = '__all__'