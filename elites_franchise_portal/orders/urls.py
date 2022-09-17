"""Orders urls file."""

from rest_framework import routers
from elites_franchise_portal.orders import views

router = routers.DefaultRouter()
router.register(r'carts', views.CartViewSet)
router.register(r'cart_items', views.CartItemViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'instant_order_items', views.InstantOrderItemViewSet)
router.register(
    r'installment_order_items', views.InstallmentsOrderItemViewSet,
    'installmentorderitem')
router.register(r'installments', views.InstallmentViewSet)
router.register(r'order_transactions', views.OrderTransactionViewSet)

urlpatterns = router.urls
