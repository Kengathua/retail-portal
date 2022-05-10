"""Debit side urls file."""

from rest_framework import routers
from elites_franchise_portal.debit import views

router = routers.DefaultRouter()
router.register(r'store_items', views.StoreViewSet)
router.register(r'store_records', views.StoreRecordViewSet)
router.register(r'inventory_items', views.InventoryItemViewSet)
router.register(r'inventory_records', views.InventoryRecordViewSet)
router.register(r'sales', views.SaleViewSet)
router.register(r'sale_records', views.SaleRecordViewSet)

urlpatterns = router.urls

# urlpatterns = [
#     path('debit/', include((debit_patterns, 'debit'), namespace='debit')),
# ]
