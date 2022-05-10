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

    class Meta:
        """Category serializer Meta class."""

        model = models.Brand
        fields = '__all__'


class BrandItemTypeSerializer(BaseSerializerMixin):
    """Brand Item Type serializer class."""

    brand_details = SerializerMethodField()

    def get_brand_details(self, brand_item_type):
        """Get brand details function."""
        brand_details = {
            'id': brand_item_type.brand.id,
            'brand_name': brand_item_type.brand.brand_name,
            'brand_code': brand_item_type.brand.brand_code
        }

        return brand_details

    item_type_details = SerializerMethodField()

    def get_item_type_details(self, brand_item_type):
        """Get item type details function."""
        type_details = {
            'id': brand_item_type.item_type.id,
            'type_name': brand_item_type.item_type.type_name,
            'type_code': brand_item_type.item_type.type_code,
        }

        return type_details

    class Meta:
        """Category serializer Meta class."""

        model = models.BrandItemType
        fields = '__all__'

        extra_kwargs = {
            'brand': {'write_only': True},
            'item_type': {'write_only': True},
        }


class ItemModelSerializer(BaseSerializerMixin):
    """Item model serializer class."""

    class Meta:
        """Item models Meta class."""

        model = models.ItemModel
        fields = '__all__'

        extra_kwargs = {
            'brand_item': {'write_only': True},
        }


class ItemSerializer(BaseSerializerMixin):
    """Item serializer class."""

    class Meta:
        """Item Meta class."""

        model = models.Item
        fields = '__all__'

        extra_kwargs = {
            'item_model': {'write_only': True},
        }


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


