"""Debit side filters file."""
from elites_retail_portal.common.filters import SearchComboboxBaseFilter
from elites_retail_portal.items import models


class CategoryFilter(SearchComboboxBaseFilter):
    """Filter individual categories."""

    class Meta:
        """Restrict filter fields."""

        model = models.Category
        fields = '__all__'


class ItemTypeFilter(SearchComboboxBaseFilter):
    """Filter individual item type."""

    class Meta:
        """Restrict filter fields."""

        model = models.ItemType
        fields = '__all__'


class BrandFilter(SearchComboboxBaseFilter):
    """Filter individual brand."""

    class Meta:
        """Restrict filter fields."""

        model = models.Brand
        fields = '__all__'


class BrandItemTypeFilter(SearchComboboxBaseFilter):
    """Filter individual brand item_type."""

    class Meta:
        """Restrict filter fields."""

        model = models.BrandItemType
        fields = '__all__'


class ItemModelTypeFilter(SearchComboboxBaseFilter):
    """Filter individual brand item_type."""

    class Meta:
        """Restrict filter fields."""

        model = models.ItemModel
        fields = '__all__'


class ItemFilter(SearchComboboxBaseFilter):
    """Filter individual item."""

    class Meta:
        """Restrict filter fields."""

        model = models.Item
        fields = '__all__'


class UnitsFilter(SearchComboboxBaseFilter):
    """Filter individual units."""

    class Meta:
        """Restrict filter fields."""

        model = models.Units
        fields = '__all__'


class UnitsItemTypeFilter(SearchComboboxBaseFilter):
    """Filter individual units item_type."""

    class Meta:
        """Restrict filter fields."""

        model = models.UnitsItemType
        fields = '__all__'


class ItemUnitsFilter(SearchComboboxBaseFilter):
    """Filter individual item units."""

    class Meta:
        """Restrict filter fields."""

        model = models.ItemUnits
        fields = '__all__'


class ItemAttributeFilter(SearchComboboxBaseFilter):
    """Filter individual item attributes."""

    class Meta:
        """Restrict filter fields."""

        model = models.ItemAttribute
        fields = '__all__'


# class ItemImageFilter(SearchComboboxBaseFilter):
#     """Filter individual item attributes."""

#     class Meta:
#         """Restrict filter fields."""

#         model = models.ItemImage
#         fields = '__all__'
#         filter_overrides = {
#              models.ImageField: {
#                  'filter_class': django_filters.CharFilter,
#                  'extra': lambda f: {
#                      'lookup_expr': 'icontains',
#                  },
#              },
#         }
