"""Debit side urls file."""

from rest_framework import routers
from elites_retail_portal.debit import views

router = routers.DefaultRouter()
router.register(r'inventories', views.InventoryViewSet)
router.register(r'inventory_items', views.InventoryItemViewSet)
router.register(r'inventory_inventory_items', views.InventoryInventoryItemViewSet)
router.register(r'inventory_records', views.InventoryRecordViewSet)
router.register(r'sales', views.SaleViewSet)
router.register(r'sale_items', views.SaleItemViewSet)
router.register(r'purchases_returns', views.PurchasesReturnViewSet)

urlpatterns = router.urls
