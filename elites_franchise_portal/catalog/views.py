"""Catalog views file."""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from elites_franchise_portal.catalog import serializers
from elites_franchise_portal.catalog.models import (
    Catalog, CatalogItem, CatalogCatalogItem, CatalogItemAuditLog, Section)
from elites_franchise_portal.common.views import BaseViewMixin
from elites_franchise_portal.catalog import filters


class SectionViewSet(BaseViewMixin):
    """Section Viewset class."""

    queryset = Section.objects.all()
    serializer_class = serializers.SectionSerializer
    filterset_class = filters.SectionFilter
    search_fields = ('section_name', 'section_code')

    partition_spec = {
        'FRANCHISE': 'enterprise'
    }


class CatalogViewSet(BaseViewMixin):
    """Catalog Viewset class."""

    queryset = Catalog.objects.all().order_by('catalog_name')
    serializer_class = serializers.CatalogSerializer
    filterset_class = filters.CatalogFilter
    search_fields = ('catalog_name', 'catalog_code')


class CatalogItemViewSet(BaseViewMixin):
    """Catalog Item Viewset class."""

    queryset = CatalogItem.objects.all().order_by('inventory_item__item__item_name')
    serializer_class = serializers.CatalogItemSerializer
    filterset_class = filters.CatalogItemFilter
    search_fields = (
        'section__section_name', 'inventory_item__item__item_name',
        'inventory_item__item__item_model__model_name',
        'inventory_item__item__item_model__brand__brand_name',
        'inventory_item__item__item_model__item_type__type_name',
        'inventory_item__item__item_code', 'inventory_item__item__barcode')

    # @method_decorator(vary_on_cookie)
    # @method_decorator(cache_page(60*60*14))
    # def dispatch(self, *args, **kwargs):
    #     """."""
    #     if self.request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
    #         cache.delete('catalog_items_objects')
    #     catalog_items_objects = cache.get('catalog_items_objects')
    #     if catalog_items_objects is None:
    #         cache.set('catalog_items_objects', self.queryset)
    #     return super(CatalogItemViewSet, self).dispatch(*args, **kwargs)


    @action(methods=['post'], detail=True)
    def add_to_catalogs(self, request, *args, **kwargs):
        user = request.user
        catalog_item = self.get_object()
        catalogs = Catalog.objects.filter(id__in=request.data['catalogs'])
        catalog_item.add_to_catalogs(user, catalogs)

        return Response(data={"status": "OK"}, status=status.HTTP_200_OK)

class CatalogCatalogItemViewSet(BaseViewMixin):
    """CatalogCatalogItem Viewset class."""

    queryset = CatalogCatalogItem.objects.all().order_by('catalog__catalog_name')
    serializer_class = serializers.CatalogCatalogItemSerializer
    filterset_class = filters.CatalogCatalogItemFilter
    search_fields = (
        'catalog__catalog_name', 'catalog_item__section__section_name',
        'catalog_item__inventory_item__item__item_name',
        'catalog_item__inventory_item__item__item_code',
        'catalog_item__inventory_item__item__barcode')


class CatalogItemAuditLogViewSet(BaseViewMixin):
    """Viewset for CatalogItemAuditLog model."""

    queryset = CatalogItemAuditLog.objects.all().order_by('created_on')
    serializer_class = serializers.CatalogItemAuditLogSerializer
    filterset_class = filters.CatalogItemAuditLogFilter
    search_fields = (
        'catalog_item__inventory_item__item__item_name',
        'catalog_item__inventory_item__item__item_code',
        'catalog_item__inventory_item__item__barcode',
        'record_type', 'operation_type',
    )
