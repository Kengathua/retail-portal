"""Credit side serializers file."""

from elites_franchise_portal.common.serializers import BaseSerializerMixin
from elites_franchise_portal.credit import models


class PurchaseSerializer(BaseSerializerMixin):
    """Purchases serializer class."""

    class Meta:
        """Serializer Meta class."""

        model = models.Purchase
        fields = '__all__'
