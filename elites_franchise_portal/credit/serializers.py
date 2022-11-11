"""Credit side serializers file."""

from rest_framework.fields import CharField, ReadOnlyField

from elites_franchise_portal.common.serializers import BaseSerializerMixin
from elites_franchise_portal.credit import models


class PurchaseSerializer(BaseSerializerMixin):
    """Purchases serializer class."""

    supplier_name = CharField(source='supplier.name', read_only=True)
    barcode = CharField(source='item.barcode', read_only=True)
    total_cost = ReadOnlyField()

    class Meta:
        """Serializer Meta class."""

        model = models.Purchase
        fields = '__all__'


class PurchaseItemSerializer(BaseSerializerMixin):
    """Purchases Items serializer class."""

    item_name = CharField(source='item.item_name', read_only=True)

    class Meta:
        """Serializer Meta class."""

        model = models.PurchaseItem
        fields = '__all__'


class SalesReturnSerializer(BaseSerializerMixin):
    """Sales Return serializer class."""

    item_name = CharField(source='sale_item.catalog_item.inventory_item.item.item_name', read_only=True)

    class Meta:
        """Serializer Meta class."""

        model = models.SalesReturn
        fields = '__all__'
