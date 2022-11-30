"""."""

from elites_retail_portal.debit.views.inventory import (
    InventoryViewSet, InventoryItemViewSet, InventoryInventoryItemViewSet,
    InventoryRecordViewSet)
from elites_retail_portal.debit.views.sales import (
    SaleItemViewSet, SaleViewSet)
from elites_retail_portal.debit.views.purchases_returns import PurchasesReturnViewSet

__all__ = (
    'InventoryViewSet', 'InventoryRecordViewSet', 'InventoryItemViewSet',
    'InventoryInventoryItemViewSet', 'SaleItemViewSet', 'SaleViewSet',
    'PurchasesReturnViewSet'
    )
