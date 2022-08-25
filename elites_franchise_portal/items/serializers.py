"""Item serializers file."""

from rest_framework.fields import SerializerMethodField

from elites_franchise_portal.common.serializers import BaseSerializerMixin
from elites_franchise_portal.items import models


class CategorySerializer(BaseSerializerMixin):
    """Category Serializer class."""

    class Meta:
        """Categories serializer Meta class."""

        model = models.Category
        fields = '__all__'

    def create(self, validated_data):
        """Create function for Category serializer."""
        sections = validated_data.pop('sections', None)
        self._populate_audit_fields(validated_data, True)
        category = models.Category.objects.create(**validated_data)
        if sections:
            for section in sections:
                data = {
                    'category': category,
                    'section': section,
                }
                self._populate_audit_fields(data, True)
                models.CategorySection.objects.create(**data)

        return category


class ItemTypeSerializer(BaseSerializerMixin):
    """Item type serializer class."""

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
        request = self.context['request']
        user = request.user
        audit_fields = {
            'created_by':user.id,
            'updated_by':user.id,
            'franchise':user.franchise,
            }

        item_types_ids = request.data['item_types'] if 'item_types' in request.data.keys() else []
        brand = models.Brand.objects.create(**validated_data, **audit_fields)
        for item_type_id in item_types_ids:
            item_type = models.ItemType.objects.get(id=item_type_id)
            models.BrandItemType.objects.create(
                brand=brand, item_type=item_type, **audit_fields)
        return brand

    def update(self, instance, validated_data):
        request = self.context['request']
        user = request.user
        audit_fields = {
            'created_by':user.id,
            'updated_by':user.id,
            'franchise':user.franchise,
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

    heading = SerializerMethodField()

    def get_heading(self, instance):
        model_name = instance.model_name
        brand_name = instance.brand.brand_name
        type_name = instance.item_type.type_name
        return f'{model_name} {brand_name} {type_name}'

    class Meta:
        """Item models Meta class."""

        model = models.ItemModel
        fields = '__all__'


class ItemSerializer(BaseSerializerMixin):
    """Item serializer class."""

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

    class Meta:
        """Units Meta class."""

        model = models.Units
        fields = '__all__'


class ItemUnitsSerializer(BaseSerializerMixin):
    """Item units serializer class."""

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


