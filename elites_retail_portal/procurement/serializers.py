"""Procurement serializers file."""
from rest_framework.fields import CharField, ReadOnlyField
from rest_framework import serializers

from elites_retail_portal.common.serializers import BaseSerializerMixin
from elites_retail_portal.procurement import models


class MultipleFileSerializer(serializers.Serializer):
    """Serialize multiple files."""

    files = serializers.ListField(
        child=serializers.FileField(
            max_length=100000, allow_empty_file=False,
            use_url=False)
        )


class PurchaseOrderSerializer(BaseSerializerMixin):
    """PurchaseOrder Serializer class."""

    supplier_name = CharField(source='supplier.name', read_only=True)
    total_price = ReadOnlyField()

    class Meta:
        """Purchase Order serializer Meta class."""

        model = models.PurchaseOrder
        fields = '__all__'


class PurchaseOrderScanSerializer(BaseSerializerMixin):
    """PurchaseOrder Scan Serializer class."""

    class Meta:
        """Purchase Order serializer Meta class."""

        model = models.PurchaseOrderScan
        fields = '__all__'


class PurchaseOrderItemSerializer(BaseSerializerMixin):
    """Purchase Order Item Serializer class."""

    item_name = ReadOnlyField(source="item.item_name")

    class Meta:
        """Purchase Order Item serializer Meta class."""

        model = models.PurchaseOrderItem
        fields = '__all__'
