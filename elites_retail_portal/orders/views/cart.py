"""Cart views file."""

from elites_retail_portal.common.views import BaseViewMixin
from elites_retail_portal.orders.models import (
    Cart, CartItem)
from elites_retail_portal.orders import serializers, filters


class CartViewSet(BaseViewMixin):
    """Cart Viewset class."""

    queryset = Cart.objects.all().order_by('customer__first_name')
    serializer_class = serializers.CartSerializer
    filterset_class = filters.CartFilter
    search_fields = (
        'encounter__encounter_number', 'encounter__receipt_number', 'cart_code',
        'customer__first_name', 'customer__last_name', 'customer__other_names')


class CartItemViewSet(BaseViewMixin):
    """Cart Item Viewset class."""

    queryset = CartItem.objects.all().order_by('catalog_item__inventory_item__item__name')
    serializer_class = serializers.CartItemSerializer
    filterset_class = filters.CartItemFilter
