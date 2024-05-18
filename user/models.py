from django.db import models
from django.contrib.auth.models import User
from product.models import Item
from django.core.validators import MinValueValidator
# Create your models here.

class Userinfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contact_number = models.IntegerField()
    street_address = models.TextField()

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} wishlisted {self.item.title}'

ORDER_STATUS = {('Pending', 'Pending'),
    ('Confirmed', 'Confirmed'),
    ('Delivered', 'Delivered')}

class OrderHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
    color = models.CharField(max_length=255, null=True, blank=True)
    size = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(choices=ORDER_STATUS,max_length=255, null=True, blank=True)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} ordered {self.item.title}'
    def total_item_price(self):
        total_price = 0
        if self.item.discount==True:
            total_price += ((self.item.price) - (self.item.price)*(self.item.discount_percentage/100)) * self.quantity
        else:
            total_price += self.item.price * self.quantity
        return total_price

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} cart'
    
    def total_payment(self):
        total_price = 0
        cart_items = self.cart_items.all()
        for cart_item in cart_items:
            if cart_item.item.discount==True:
                total_price += ((cart_item.item.price) - (cart_item.item.price)*(cart_item.item.discount_percentage/100)) * cart_item.quantity
            else:
                total_price += cart_item.item.price * cart_item.quantity
        return total_price

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f'{self.cart.user.first_name} {self.cart.user.last_name} has added {self.item.title} to their cart'

    