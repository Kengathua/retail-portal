"""Credit side views init file."""
from elites_retail_portal.credit.views.purchases import (
    PurchaseViewSet, PurchaseItemViewSet)
from elites_retail_portal.credit.views.sales_returns import SalesReturnViewSet

__all__ = ('PurchaseViewSet', 'PurchaseItemViewSet', 'SalesReturnViewSet')
