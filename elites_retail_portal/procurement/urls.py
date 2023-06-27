"""Item registry urls file."""

from rest_framework import routers
from elites_retail_portal.procurement import views

router = routers.DefaultRouter()
router.register(r'purchase_orders', views.PurchaseOrderViewSet)
router.register(r'purchase_order_items', views.PurchaseOrderItemViewSet)
router.register(r'purchase_order_scans', views.PurchaseOrderScanViewSet)

urlpatterns = router.urls
