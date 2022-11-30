"""Wallet urls file."""

from rest_framework import routers
from elites_retail_portal.wallet import views

router = routers.DefaultRouter()
router.register(r'wallets', views.WalletViewSet)
router.register(r'wallet_records', views.WalletRecordViewSet)
router.register(r'anonymous_wallets', views.AnonymousWalletViewSet)

urlpatterns = router.urls
