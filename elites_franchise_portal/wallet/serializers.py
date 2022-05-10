"""Wallet serializers file."""

from elites_franchise_portal.wallet import models
from elites_franchise_portal.common.serializers import BaseSerializerMixin


class WalletSerializer(BaseSerializerMixin):
    """Wallet serializer class."""

    class Meta:
        """Serializer Meta class."""

        model = models.Wallet
        fields = '__all__'


class WalletRecordSerializer(BaseSerializerMixin):
    """Wallet record Serializer class."""

    class Meta:
        """Serializer Meta class."""

        model = models.WalletRecord
        fields = '__all__'


class AnonymousWalletSerializer(BaseSerializerMixin):
    """Anonymous wallet serializer class."""

    class Meta:
        """Serializer Meta class."""

        model = models.AnonymousWallet
        fields = '__all__'
