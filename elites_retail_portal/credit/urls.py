"""Credit side urls file."""

from rest_framework import routers
from elites_retail_portal.credit import views

router = routers.DefaultRouter()
router.register(r'purchases', views.PurchaseViewSet)
router.register(r'purchase_items', views.PurchaseItemViewSet)
router.register(r'purchase_payments', views.PurchasePaymentViewSet)
router.register(r'sales_returns', views.SalesReturnViewSet)

urlpatterns = router.urls
