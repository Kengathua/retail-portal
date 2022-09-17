"""Orders filters file."""
from elites_franchise_portal.common.filters import SearchComboboxBaseFilter
from elites_franchise_portal.orders import models


class CartFilter(SearchComboboxBaseFilter):
    """Filter carts."""

    class Meta:
        """Restrict filter fields."""

        model = models.Cart
        fields = '__all__'


class CartItemFilter(SearchComboboxBaseFilter):
    """Filter cart items."""

    class Meta:
        """Restrict filter fields."""

        model = models.CartItem
        fields = '__all__'


class OrderFilter(SearchComboboxBaseFilter):
    """Filter Orders."""

    class Meta:
        """Restrict filter fields."""

        model = models.Order
        fields = '__all__'


class InstantOrderItemFilter(SearchComboboxBaseFilter):
    """Filter InstantOrder items."""

    class Meta:
        """Restrict filter fields."""

        model = models.InstantOrderItem
        fields = '__all__'


class InstallmentsOrderItemFilter(SearchComboboxBaseFilter):
    """Filter InstallmentsOrder items."""

    class Meta:
        """Restrict filter fields."""

        model = models.InstallmentsOrderItem
        fields = '__all__'


class OrderTransactionFilter(SearchComboboxBaseFilter):
    """Filter Order Transactions."""

    class Meta:
        """Restrict filter fields."""

        model = models.OrderTransaction
        fields = '__all__'
