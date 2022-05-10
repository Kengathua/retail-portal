"""Catalog views file."""

from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

from elites_franchise_portal.catalog import serializers
from elites_franchise_portal.catalog.models import (
    Catalog, CatalogItem, CatalogCatalogItem, Section)
from elites_franchise_portal.common.views import BaseViewMixin
from elites_franchise_portal.catalog import filters


class SectionViewSet(BaseViewMixin):
    """Section Viewset class."""

    queryset = Section.objects.all()
    serializer_class = serializers.SectionSerializer
    filterset_class = filters.SectionFilter
    search_fields = ('section_name', 'section_code')

    partition_spec = {
        'SHOP': 'franchise'
    }


class CatalogViewSet(BaseViewMixin):
    """Catalog Viewset class."""

    queryset = Catalog.objects.all().order_by('name')
    serializer_class = serializers.CatalogSerializer
    filterset_class = filters.CatalogFilter
    search_fields = ('catalog_name')


class CatalogItemViewSet(BaseViewMixin):
    """Catalog Item Viewset class."""

    queryset = CatalogItem.objects.all().order_by('inventory_item__item__item_name')
    serializer_class = serializers.CatalogItemSerializer
    filterset_class = filters.CatalogItemFilter
    search_fields = (
        'section__section_name', 'inventory_item__item__item_name',
        'inventory_item__item__item_model__model_name',
        'inventory_item__item__item_model__brand_item_type__brand__brand_name',
        'inventory_item__item__item_model__brand_item_type__item_type__type_name',
        'inventory_item__item__item_code', 'inventory_item__item__barcode')

    @method_decorator(vary_on_cookie)
    @method_decorator(cache_page(60*60*14))
    def dispatch(self, *args, **kwargs):
        """."""
        catalog_items_objects = cache.get('catalog_items_objects')
        if catalog_items_objects is None:
            cache.set('catalog_items_objects', self.queryset)
        return super(CatalogItemViewSet, self).dispatch(*args, **kwargs)


class CatalogCatalogItemViewSet(BaseViewMixin):
    """CatalogCatalogItem Viewset class."""

    queryset = CatalogCatalogItem.objects.all().order_by('catalog__name')
    serializer_class = serializers.CatalogCatalogItemSerializer
    filterset_class = filters.CatalogCatalogItemFilter
    search_fields = (
        'catalog__catalog_name', 'catalog_item__section__section_name',
        'catalog_item__inventory_item__item__item_name',
        'catalog_item__inventory_item__item__item_code',
        'catalog_item__inventory_item__item__barcode')
