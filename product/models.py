from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg

# Create your models here.
class Category(models.Model):
    title = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to='product/media/images/')
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title

class Color(models.Model):
    title = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.title

class Size(models.Model):
    title = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.title

class Item(models.Model):
    title = models.CharField(max_length=255, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.IntegerField()
    description = models.TextField()
    discount = models.BooleanField(default=False)
    discount_percentage = models.PositiveIntegerField(null=True, blank=True)
    color = models.ManyToManyField(Color)
    size = models.ManyToManyField(Size)
    sales_number = models.PositiveIntegerField(default=0)
    entry_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    quantity_available = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.title
    
    def discount_price(self):
        if self.discount is True:
            return  ((self.price) - (self.price)*(self.discount_percentage/100))

    def average_rating(self):
        return self.reviews.aggregate(Avg('rating'))['rating__avg']

class ItemImage(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product/media/images/')

    def __str__(self):
        return self.item.title
    
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField()
    review = models.TextField()
    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s review on {self.item.title}"


