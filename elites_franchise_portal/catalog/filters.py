"""Catalog filters file."""

from elites_franchise_portal.common.filters import SearchComboboxBaseFilter
from elites_franchise_portal.catalog import models


class SectionFilter(SearchComboboxBaseFilter):
    """Filter individual sections."""

    class Meta:
        """Restrict filter fields."""

        model = models.Section
        fields = '__all__'


class CatalogFilter(SearchComboboxBaseFilter):
    """Filter individual catalogs."""

    class Meta:
        """Restrict filter fields."""

        model = models.Catalog
        fields = '__all__'


class CatalogItemFilter(SearchComboboxBaseFilter):
    """Filter individual catalog items."""

    class Meta:
        """Restrict filter fields."""

        model = models.CatalogItem
        fields = '__all__'


class CatalogCatalogItemFilter(SearchComboboxBaseFilter):
    """Filter individual catalog catalog items."""

    class Meta:
        """Restrict filter fields."""

        model = models.CatalogCatalogItem
        fields = '__all__'
