"""Credit side serializers file."""

from rest_framework.fields import CharField, ReadOnlyField, SerializerMethodField
from django.core.exceptions import ValidationError

from elites_retail_portal.common.serializers import BaseSerializerMixin
from elites_retail_portal.credit import models
from elites_retail_portal.items.models import ItemUnits
from elites_retail_portal.items.models import Product


class PurchaseSerializer(BaseSerializerMixin):
    """Purchases serializer class."""

    supplier_name = CharField(source='supplier.name', read_only=True)
    barcode = CharField(source='item.barcode', read_only=True)
    total_cost = ReadOnlyField()
    total_payments_amount = ReadOnlyField()
    balance_amount = ReadOnlyField()

    class Meta:
        """Serializer Meta class."""

        model = models.Purchase
        fields = '__all__'


class PurchaseItemSerializer(BaseSerializerMixin):
    """Purchases Items serializer class."""

    item_name = CharField(source='item.item_name', read_only=True)
    unit_quantity = SerializerMethodField()
    purchase_units_name = SerializerMethodField()
    sale_units_name = SerializerMethodField()

    def get_unit_quantity(self, purchase_item):
        """Get the number of sale units per purchase unit."""
        item_units = ItemUnits.objects.filter(item=purchase_item.item).first()
        if item_units:
            return item_units.quantity_of_sale_units_per_purchase_unit

        return 1

    def get_purchase_units_name(self, purchase_item):
        """Get the purchase units name."""
        item_units = ItemUnits.objects.filter(item=purchase_item.item).first()
        if item_units:
            return item_units.purchases_units.units_name

        return None

    def get_sale_units_name(self, purchase_item):
        """Get the sale units name."""
        item_units = ItemUnits.objects.filter(item=purchase_item.item).first()
        if item_units:
            return item_units.sales_units.units_name

        return None

    def create(self, cleaned_data):
        """Create purchase item."""
        serial_numbers = dict(self.request.data).get('serial_numbers', [])
        audit_fields = {
            'created_by': self.request.user.id,
            'updated_by': self.request.user.id,
            'enterprise': self.request.user.enterprise,
        }

        if len(serial_numbers) < 1:
            purchase_item = models.PurchaseItem.objects.create(**audit_fields, **cleaned_data)
            return purchase_item

        products = Product.objects.filter(
            serial_number__in=serial_numbers, enterprise=self.request.user.enterprise)
        if products.exists():
            msg = "A product with the serial number {} already exists".format(
                products.first().serial_number)
            raise ValidationError({'serial_number': msg})

        purchase_item = models.PurchaseItem.objects.create(**audit_fields, **cleaned_data)
        for serial_number in serial_numbers:
            payload = {
                'item': purchase_item.item,
                'serial_number': serial_number,
                'product_name': purchase_item.item.item_name,
            }
            Product.objects.create(**audit_fields, **payload)

        return purchase_item

    def update(self, instance, cleaned_data):
        """Update purchase item."""
        serial_numbers = dict(self.request.data).get('serial_numbers', [])
        for field in instance._meta.fields:
            cleaned_value = cleaned_data.get(field.name, None)
            if cleaned_value:
                setattr(instance, field.name, cleaned_value)

        instance.save()

        if len(serial_numbers) < 1:
            return instance

        audit_fields = {
            'created_by': self.request.user.id,
            'updated_by': self.request.user.id,
            'enterprise': self.request.user.enterprise,
        }
        for serial_number in serial_numbers:
            payload = {
                'item': instance.item,
                'serial_number': serial_number,
                'product_name': instance.item.item_name,
            }
            if not Product.objects.filter(
                    serial_number=serial_number,
                    enterprise=self.request.user.enterprise).exists():
                Product.objects.create(**audit_fields, **payload)

        return instance

    class Meta:
        """Serializer Meta class."""

        model = models.PurchaseItem
        fields = '__all__'


class PurchasePaymentSerializer(BaseSerializerMixin):
    """Purchase Payment serializer class."""

    class Meta:
        """Serializer Meta class."""

        model = models.PurchasePayment
        fields = '__all__'


class SalesReturnSerializer(BaseSerializerMixin):
    """Sales Return serializer class."""

    item_name = CharField(
        source='sale_item.catalog_item.inventory_item.item.item_name', read_only=True)

    class Meta:
        """Serializer Meta class."""

        model = models.SalesReturn
        fields = '__all__'
