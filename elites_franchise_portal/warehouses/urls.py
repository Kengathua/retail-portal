"""Warehouse urls file."""

from rest_framework import routers
from elites_franchise_portal.warehouses import views

router = routers.DefaultRouter()
router.register(r'warehouses', views.WarehouseViewSet)
router.register(r'warehouse_items', views.WarehouseItemViewSet)
router.register(r'warehouse_records', views.WarehouseRecordViewSet)
router.register(r'warehouse_warehouse_items', views.WarehouseWarehouseItemViewSet)

urlpatterns = router.urls
