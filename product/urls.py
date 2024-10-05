from rest_framework.routers import DefaultRouter
from .views import *
from django.urls import path, include

router = DefaultRouter()
router.register('color', ColorView)
router.register('size', SizeView)
router.register('category', CategoryView)
router.register('item', ItemView)
router.register('review', ReviewView)

urlpatterns = [
    path('', include(router.urls)),
    path('paymentgateway/<int:uid>', paymentgateway_view, name='paymentgateway'),
    path('paymentsuccess/<int:uid>', paymentsuccess_view, name='paymentsuccess'),
    path('paymentfailure/', paymentfailure_view, name='paymentfailure'),
]

