"""Wallet views file."""

from elites_retail_portal.common.views import BaseViewMixin
from elites_retail_portal.wallet.models import Wallet, WalletRecord, AnonymousWallet
from elites_retail_portal.wallet import serializers


class WalletViewSet(BaseViewMixin):
    """Wallet ViewSet."""

    queryset = Wallet.objects.all()
    serializer_class = serializers.WalletSerializer


class WalletRecordViewSet(BaseViewMixin):
    """Wallet record Viewset."""

    queryset = WalletRecord.objects.all()
    serializer_class = serializers.WalletRecordSerializer


class AnonymousWalletViewSet(BaseViewMixin):
    """Anonymous wallet Viewset."""

    queryset = AnonymousWallet.objects.all()
    serializer_class = serializers.AnonymousWalletSerializer
