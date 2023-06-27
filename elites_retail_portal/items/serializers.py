"""Item serializers file."""

from django.core.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField, CharField, ReadOnlyField

from elites_retail_portal.common.serializers import BaseSerializerMixin
from elites_retail_portal.items import models


class CategorySerializer(BaseSerializerMixin):
    """Category Serializer class."""

    class Meta:
        """Categories serializer Meta class."""

        model = models.Category
        fields = '__all__'


class ItemTypeSerializer(BaseSerializerMixin):
    """Item type serializer class."""

    category_name = ReadOnlyField(source='category.category_name')

    class Meta:
        """Item type serializer Meta class."""

        model = models.ItemType
        fields = '__all__'

        extra_kwargs = {
            'category_section': {'write_only': True},
        }


class BrandSerializer(BaseSerializerMixin):
    """Brand serializer class."""

    item_types = ItemTypeSerializer(many=True, required=False, read_only=True)

    def create(self, validated_data):
        """Create brand serializer."""
        request = self.context['request']
        user = request.user
        audit_fields = {
            'created_by': user.id,
            'updated_by': user.id,
            'enterprise': user.enterprise,
            }

        item_types_ids = request.data['item_types'] if 'item_types' in request.data.keys() else []
        brand = models.Brand.objects.create(**validated_data, **audit_fields)
        for item_type_id in item_types_ids:
            item_type = models.ItemType.objects.get(id=item_type_id)
            models.BrandItemType.objects.create(
                brand=brand, item_type=item_type, **audit_fields)
        return brand

    def update(self, instance, validated_data):
        """Update brands serializer."""
        request = self.context['request']
        user = request.user
        audit_fields = {
            'created_by': user.id,
            'updated_by': user.id,
            'enterprise': user.enterprise,
            }

        item_types_ids = request.data['item_types'] if 'item_types' in request.data.keys() else []

        for item in validated_data:
            if models.Brand._meta.get_field(item):
                setattr(instance, item, validated_data[item])
        models.BrandItemType.objects.filter(brand=instance).delete()
        for item_type_id in item_types_ids:
            item_type = models.ItemType.objects.get(id=item_type_id)
            models.BrandItemType.objects.create(
                brand=instance, item_type=item_type, **audit_fields)
        instance.save()
        return instance

    class Meta:
        """Category serializer Meta class."""

        model = models.Brand
        fields = '__all__'


class BrandItemTypeSerializer(BaseSerializerMixin):
    """Brand Item Type serializer class."""

    class Meta:
        """Category serializer Meta class."""

        model = models.BrandItemType
        fields = '__all__'


class ItemModelSerializer(BaseSerializerMixin):
    """Item model serializer class."""

    heading = ReadOnlyField()
    brand_name = SerializerMethodField()
    type_name = SerializerMethodField()

    def get_brand_name(self, item_model):
        """Get brand name."""
        return item_model.brand.brand_name

    def get_type_name(self, item_model):
        """Get type name."""
        return item_model.item_type.type_name

    class Meta:
        """Item models Meta class."""

        model = models.ItemModel
        fields = '__all__'


class ItemSerializer(BaseSerializerMixin):
    """Item serializer class."""

    quantity_of_sale_units_per_purchase_unit = SerializerMethodField()
    purchase_units_name = SerializerMethodField()
    sale_units_name = SerializerMethodField()
    model_name = ReadOnlyField(source='item_model.heading')

    def get_quantity_of_sale_units_per_purchase_unit(self, item):
        """Get the number of sale units per purchase unit."""
        item_units = models.ItemUnits.objects.filter(item=item).first()
        if item_units:
            return item_units.quantity_of_sale_units_per_purchase_unit

        return 1

    def get_purchase_units_name(self, item):
        """Get the purchase units name."""
        item_units = models.ItemUnits.objects.filter(item=item).first()
        if item_units:
            return item_units.purchases_units.units_name

        return None

    def get_sale_units_name(self, item):
        """Get the sale units name."""
        item_units = models.ItemUnits.objects.filter(item=item).first()
        if item_units:
            return item_units.sales_units.units_name

        return None

    class Meta:
        """Item Meta class."""

        model = models.Item
        fields = '__all__'


class UnitsItemTypeSerializer(BaseSerializerMixin):
    """Units Item Type Serializer."""

    class Meta:
        """Item Type Units through M2M model serializer."""

        model = models.UnitsItemType
        fields = '__all__'

        extra_kwargs = {
            'units': {'write_only': True},
            'item_type': {'write_only': True},
        }


class UnitsSerializer(BaseSerializerMixin):
    """Units serializer class."""

    item_types = ItemTypeSerializer(many=True, required=False, read_only=True)

    def create(self, validated_data):
        """Create brand serializer."""
        request = self.context['request']
        audit_fields = {
            'created_by': request.user.id,
            'updated_by': request.user.id,
            'enterprise': request.user.enterprise,
            }

        item_types_ids = request.data['item_types'] if 'item_types' in request.data.keys() else []
        units = models.Units.objects.create(**validated_data, **audit_fields)
        for item_type_id in item_types_ids:
            item_type = models.ItemType.objects.get(id=item_type_id)
            models.UnitsItemType.objects.create(
                units=units, item_type=item_type, **audit_fields)
        return units

    def update(self, instance, validated_data):
        """Update brands serializer."""
        request = self.context['request']
        audit_fields = {
            'created_by': request.user.id,
            'updated_by': request.user.id,
            'enterprise': request.user.enterprise,
            }

        item_types_ids = request.data['item_types'] if 'item_types' in request.data.keys() else []

        for item in validated_data:
            if models.Units._meta.get_field(item):
                setattr(instance, item, validated_data[item])
        models.UnitsItemType.objects.filter(units=instance).delete()
        for item_type_id in item_types_ids:
            item_type = models.ItemType.objects.get(id=item_type_id)
            models.UnitsItemType.objects.create(
                units=instance, item_type=item_type, **audit_fields)
        instance.save()
        return instance

    class Meta:
        """Units Meta class."""

        model = models.Units
        fields = '__all__'


class ItemUnitsSerializer(BaseSerializerMixin):
    """Item units serializer class."""

    item_name = CharField(source='item.item_name', read_only=True)
    sales_units_name = CharField(source='sales_units.units_name', read_only=True)
    purchases_units_name = CharField(source='purchases_units.units_name', read_only=True)

    class Meta:
        """Item Units Meta class."""

        model = models.ItemUnits
        fields = '__all__'


class ItemAttributeSerializer(BaseSerializerMixin):
    """Item Attributes Serializer."""

    class Meta:
        """Item attributes Meta class."""

        model = models.ItemAttribute
        fields = '__all__'


class ItemImageSerializer(BaseSerializerMixin):
    """Item image serializer class."""

    class Meta:
        """Item images Meta class."""

        model = models.ItemImage
        fields = '__all__'


class ProductSerializer(BaseSerializerMixin):
    """Product Serializer class."""

    item_name = ReadOnlyField(source='item.item_name')
    barcode = ReadOnlyField(source='item.barcode')
    selling_price = SerializerMethodField()
    quantity = SerializerMethodField()
    catalog_item_id = SerializerMethodField()

    def get_selling_price(self, instance):
        """Get selling price."""
        if instance.catalog_item:
            return instance.catalog_item.selling_price
        return 0

    def get_quantity(self, instance):
        """Get quantity."""
        if instance.catalog_item:
            return instance.catalog_item.get_quantity()
        return 0

    def get_catalog_item_id(self, instance):
        """Get catalog item id."""
        if instance.catalog_item:
            return instance.catalog_item.id
        return None

    def create(self, cleaned_data):
        """Create action."""
        serial_numbers = dict(self.request.data).get('serial_numbers', None)
        item_id = self.request.data.get('item', None)
        item = models.Item.objects.filter(id=item_id).first()
        if not item:
            msg = "Please select an item"
            raise ValidationError({'serial_number': msg})

        if not serial_numbers:
            return super().create(cleaned_data)

        if len(serial_numbers) < 1:
            return super().create(cleaned_data)

        audit_fields = {
            'created_by': self.request.user.id,
            'updated_by': self.request.user.id,
            'enterprise': self.request.user.enterprise,
        }
        products = []
        for serial_number in serial_numbers:
            payload = {
                'serial_number': serial_number,
                'item': item
            }
            products.append(models.Product.objects.create(**payload, **audit_fields))
        return products[0]

    class Meta:
        """Categories serializer Meta class."""

        model = models.Product
        fields = '__all__'
