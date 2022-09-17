"""Credit side serializers file."""

from rest_framework.fields import CharField

from elites_franchise_portal.common.serializers import BaseSerializerMixin
from elites_franchise_portal.credit import models


class PurchaseSerializer(BaseSerializerMixin):
    """Purchases serializer class."""

    supplier_name = CharField(source='supplier.name', read_only=True)
    barcode = CharField(source='item.barcode', read_only=True)
    item_name = CharField(source='item.item_name', read_only=True)

    class Meta:
        """Serializer Meta class."""

        model = models.Purchase
        fields = '__all__'
