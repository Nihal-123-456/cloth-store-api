from rest_framework.routers import DefaultRouter
from .views import *
from django.urls import path, include

router = DefaultRouter()
router.register('userinfo', UserinfoView)
router.register('wishlist', WishlistItemView)
router.register('order_history', OrderHistoryView)
router.register('cart', CartView)
router.register('cart_items', CartItemView)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('active/<uid64>/<token>',activate, name='activate' ),
    path('change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('forget_password/', ForgetPasswordView.as_view(), name='forget_password'),
    path('password_reset/<uid>/<token>', PasswordResetView.as_view(), name='password_reset'),
]