"""Transaction urls file."""

from rest_framework import routers
from elites_retail_portal.transactions import views

router = routers.DefaultRouter()
router.register(r'transactions', views.TransactionViewSet)
router.register(r'payments', views.PaymentViewSet)
router.register(r'payment_requests', views.PaymentRequestViewSet, 'paymentrequest')

urlpatterns = router.urls
