from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EquipmentDatasetViewSet, EquipmentItemViewSet

router = DefaultRouter()
router.register(r'datasets', EquipmentDatasetViewSet, basename='dataset')
router.register(r'items', EquipmentItemViewSet, basename='item')

urlpatterns = [
    path('', include(router.urls)),
]
