from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register('color', ColorView)
router.register('size', SizeView)
router.register('category', CategoryView)
router.register('item', ItemView)
router.register('review', ReviewView)

urlpatterns = router.urls

