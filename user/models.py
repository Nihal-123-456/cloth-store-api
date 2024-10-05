from django.db import models
from django.contrib.auth.models import User
from product.models import Item
from django.core.validators import MinValueValidator
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver
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
    order_date = models.DateField(null=True, blank=True, auto_now_add=True)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} ordered {self.item.title}'
    def total_item_price(self):
        total_price = 0
        if self.item.discount==True:
            total_price += ((self.item.price) - (self.item.price)*(self.item.discount_percentage/100)) * self.quantity
        else:
            total_price += self.item.price * self.quantity
        return total_price
    def save(self, *args, **kwargs):
        if self.pk:
            old_status = OrderHistory.objects.get(pk=self.pk).status
            if old_status != self.status:
                if self.status == "Delivered":
                    item = self.item
                    item.sales_number += self.quantity
                    item.quantity_available -= self.quantity
                    item.save()
                self.send_status_change_email()
        super(OrderHistory, self).save(*args, **kwargs)
    def send_status_change_email(self):
        email_subject = f'Order status updated - Order #{self.id}'
        email_body = render_to_string('status_change_email.html', {'order': self})
        email = EmailMultiAlternatives(email_subject, '', to=[self.user.email])
        email.attach_alternative(email_body, 'text/html')
        email.send()

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
    def total_quantity(self):
        total_quantity = 0
        cart_items = self.cart_items.all()
        for item in cart_items:
            total_quantity += item.quantity
        return total_quantity

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    color = models.CharField(max_length=255, null=True, blank=True)
    size = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'{self.cart.user.first_name} {self.cart.user.last_name} has added {self.item.title} to their cart'

@receiver(post_save, sender=OrderHistory)
def send_order_confirmation_email(sender, instance, created, **kwargs):
    if created:
        email_subject = f'Order Confirmation - Order #{instance.id}'
        email_body = render_to_string('order_email.html', {'order': instance})
        email = EmailMultiAlternatives(email_subject, '', to=[instance.user.email])
        email.attach_alternative(email_body, 'text/html')
        email.send()
