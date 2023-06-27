"""Catalog filters file."""

from django.db.models import Q
from rest_framework import filters

from elites_retail_portal.common.filters import SearchComboboxBaseFilter
from elites_retail_portal.catalog import models
from elites_retail_portal.items.models import Product


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


class CatalogItemAuditLogFilter(SearchComboboxBaseFilter):
    """Filter individual catalog audit logs."""

    class Meta:
        """Restrict filter fields."""

        model = models.CatalogItemAuditLog
        fields = '__all__'


class ProductSearchFilter(filters.SearchFilter):
    """Search Catalog item by Product."""

    def filter_queryset(self, request, queryset, view):
        """Filter the queryset."""
        search_fields = getattr(view, 'search_fields', None)
        if not search_fields:
            return queryset

        search_terms = self.get_search_terms(request)
        if not search_terms:
            return queryset

        search_queries = Q()
        for term in search_terms:
            for field in search_fields:
                search_queries |= Q(**{f"{field}__icontains": term})
                item_ids = list(map(str, Product.objects.filter(
                    serial_number__icontains=term).values_list('item__id', flat=True)))
                if len(item_ids) >= 1:
                    search_queries |= Q(**{"inventory_item__item__id__in": item_ids})

        queryset = queryset.filter(search_queries).distinct()
        return queryset
