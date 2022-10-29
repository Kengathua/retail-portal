"""Catalog serializers file."""

from elites_franchise_portal.catalog import models
from elites_franchise_portal.common.serializers import BaseSerializerMixin

from rest_framework.fields import CharField


class SectionSerializer(BaseSerializerMixin):
    """Section serializer class."""

    class Meta:
        """Serializer Meta class."""

        model = models.Section
        fields = '__all__'


class CatalogSerializer(BaseSerializerMixin):
    """Catalog serializer class."""

    class Meta:
        """Serializer Meta class."""

        model = models.Catalog
        fields = '__all__'


class CatalogItemSerializer(BaseSerializerMixin):
    """Catalog Item Serializer class."""

    section_name = CharField(source='section.section_name', read_only=True)
    barcode = CharField(source='inventory_item.item.barcode', read_only=True)
    item_name = CharField(source='inventory_item.item.item_name', read_only=True)
    unit_price = CharField(source='inventory_item.unit_price', read_only=True)

    class Meta:
        """Serializer Meta class."""

        model = models.CatalogItem
        fields = '__all__'


class CatalogCatalogItemSerializer(BaseSerializerMixin):
    """CatalogCatalogItem Serializer class."""

    class Meta:
        """Serializer Meta class."""

        model = models.CatalogCatalogItem
        fields = '__all__'
