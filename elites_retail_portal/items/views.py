"""Items views file."""

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser, MultiPartParser

from django.shortcuts import get_object_or_404
from elites_retail_portal.common.views import BaseViewMixin
from elites_retail_portal.items.models import (
    Brand, BrandItemType, Category, ItemType,
    ItemModel, Item, ItemAttribute, ItemUnits, Units,
    ItemImage, UnitsItemType)
from elites_retail_portal.items import serializers
from elites_retail_portal.items import filters


class CategoryViewSet(BaseViewMixin):
    """Category ViewSet class."""

    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer
    filterset_class = filters.CategoryFilter
    search_fields = (
        'category_name', 'category_code')


class ItemTypeViewSet(BaseViewMixin):
    """Item Type Viewset class."""

    queryset = ItemType.objects.all()
    serializer_class = serializers.ItemTypeSerializer
    filterset_class = filters.ItemTypeFilter
    search_fields = (
        'category__category_name', 'category__category_code',
        'type_name', 'type_code',
    )


class BrandViewSet(BaseViewMixin):
    """Brand Viewset class."""

    queryset = Brand.objects.all()
    serializer_class = serializers.BrandSerializer
    filterset_class = filters.BrandFilter
    search_fields = (
        'item_types__type_name', 'item_types__type_code',
        'brand_name', 'brand_code',
    )


class BrandItemTypeViewSet(BaseViewMixin):
    """Brand Item Type Viewset class."""

    queryset = BrandItemType.objects.all()
    serializer_class = serializers.BrandItemTypeSerializer
    filterset_class = filters.BrandItemTypeFilter
    search_fields = (
        'brand__brand_name', 'brand__brand_code',
        'item_type__type_name', 'item_type__item_code',)


class ItemModelViewSet(BaseViewMixin):
    """Item Model Viewset class."""

    queryset = ItemModel.objects.all()
    serializer_class = serializers.ItemModelSerializer
    filterset_class = filters.ItemModelTypeFilter
    search_fields = (
        'brand__brand_name', 'brand__brand_code', 'item_type__type_name',
        'item_type__type_code', 'item_type__category__category_name',
        'item_type__category__category_code', 'model_name', 'model_code',
    )


class ItemViewSet(BaseViewMixin):
    """Item Viewset class."""

    queryset = Item.objects.all()
    serializer_class = serializers.ItemSerializer
    filterset_class = filters.ItemFilter
    search_fields = (
        'item_model__model_name', 'item_model__model_code', 'barcode',
        'item_name', 'item_code', 'make_year',
    )

    @action(methods=['post'], detail=True)
    def activate(self, request, *args, **kwargs):
        """Activate item end point."""
        user = request.user
        item = self.get_object()
        item.activate(user)

        return Response(data={"status": "OK"}, status=status.HTTP_200_OK)


class ItemAttributeViewSet(BaseViewMixin):
    """Item Attributes Viewset."""

    queryset = ItemAttribute.objects.all()
    serializer_class = serializers.ItemAttributeSerializer
    filterset_class = filters.ItemAttributeFilter
    search_fields = ('')


class UnitsViewSet(BaseViewMixin):
    """Units Viewset class."""

    queryset = Units.objects.all()
    serializer_class = serializers.UnitsSerializer
    filterset_class = filters.UnitsFilter
    search_fields = ('units_name', 'units_code',)


class ItemUnitsViewSet(BaseViewMixin):
    """Item Units Viewset class."""

    queryset = ItemUnits.objects.all()
    serializer_class = serializers.ItemUnitsSerializer
    filterset_class = filters.ItemUnitsFilter
    search_fields = ('')


class ItemImageViewSet(BaseViewMixin):
    """Item Images Viewset class."""

    queryset = ItemImage.objects.all()
    serializer_class = serializers.ItemImageSerializer
    parser_classes = (MultiPartParser, JSONParser)

    def perform_update(self, serializer):
        """Perform an update."""
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        """Perform  partial updates on images."""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @action(methods=['post'], detail=False)
    def upload_image(self, request,  format='multipart', *args, **kwargs):
        """Upload an image."""
        if request.method == 'POST':
            file = request.FILES['image']
            # an error might be raised here not yet tested
            item = Item.objects.get(id=request.data['item'])
            data = {
                'created_by': item.created_by,
                'updated_by': item.created_by,
                'enterprise': item.enterprise,
                'item': item,
                'image': file,
                'is_hero_image': request.data['is_hero_image']
            }
            item_image = ItemImage.objects.create(**data)

            data = self.get_serializer(item_image).data

            return Response(data=data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=False)
    def bulk_upload_images(self, request, *args, **kwargs):
        """Perform bulk images upload."""
        pass

    @action(methods=['patch'], detail=True)
    def patch_uploaded_image(self, request, *args, **kwargs):
        """Patch uploaded images."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if serializer.is_valid():
            pass
        # item_image = ItemImage.objects.all()

    @action(methods=['delete'], detail=False)
    def multiple_delete(self, request, *args, **kwargs):
        """Get the primary key value of the objects you want to delete."""
        pks = request.query_params.get('pks', None)
        if not pks:
            return Response(status=status.HTTP_404_NOT_FOUND)
        for pk in pks.split(','):
            get_object_or_404(self.model, id=int(pk)).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UnitsItemTypeViewSet(BaseViewMixin):
    """Units Item Type Viewset class."""

    queryset = UnitsItemType.objects.all()
    serializer_class = serializers.UnitsItemTypeSerializer
    filterset_class = filters.UnitsItemTypeFilter
    search_fields = ('units__units_name', 'item_type__type_name')
