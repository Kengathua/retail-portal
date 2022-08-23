"""Debit side urls file."""

from rest_framework import routers
from elites_franchise_portal.debit import views

router = routers.DefaultRouter()
router.register(r'warehouses', views.WarehouseViewSet)
router.register(r'warehouse_items', views.WarehouseItemViewSet)
router.register(r'warehouse_warehouse_items', views.WarehouseWarehouseItemViewSet)
router.register(r'warehouse_records', views.WarehouseRecordViewSet)
router.register(r'inventories', views.InventoryViewSet)
router.register(r'inventory_items', views.InventoryItemViewSet)
router.register(r'inventory_inventory_items', views.InventoryInventoryItemViewSet)
router.register(r'inventory_records', views.InventoryRecordViewSet)
router.register(r'sales', views.SaleViewSet)
router.register(r'sale_records', views.SaleRecordViewSet)

urlpatterns = router.urls
