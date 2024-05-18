from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Userinfo)
admin.site.register(WishlistItem)
admin.site.register(OrderHistory)
admin.site.register(Cart)
admin.site.register(CartItem)
