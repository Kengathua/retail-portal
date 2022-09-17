"""Cart views file."""

from elites_franchise_portal.common.views import BaseViewMixin
from elites_franchise_portal.orders.models import (
    Cart, CartItem)
from elites_franchise_portal.orders import serializers, filters


class CartViewSet(BaseViewMixin):
    """Cart Viewset class."""

    queryset = Cart.objects.all().order_by('customer__first_name')
    serializer_class = serializers.CartSerializer
    filterset_class = filters.CartFilter


class CartItemViewSet(BaseViewMixin):
    """Cart Item Viewset class."""

    queryset = CartItem.objects.all().order_by('catalog_item__inventory_item__item__name')
    serializer_class = serializers.CartItemSerializer
    filterset_class = filters.CartItemFilter
