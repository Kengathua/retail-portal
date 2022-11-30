"""Inventory model helpers."""

from elites_retail_portal.enterprise_mgt.helpers import get_valid_enterprise_setup_rules
from elites_retail_portal.debit.models import InventoryRecord
from elites_retail_portal.catalog.models import CatalogItem

def get_available_quantity_of_inventory_item_in_inventory(inventory_item, inventory=None):
    """."""
    quantity = 0
    if not inventory:
        enterprise = inventory_item.enterprise
        enterprise_setup_rules = get_valid_enterprise_setup_rules(enterprise)
        inventory = enterprise_setup_rules.default_inventory

    import pdb
    pdb.set_trace()

    inventory_records = InventoryRecord.objects.filter(inventory=inventory, inventory_item=inventory_item)
    if inventory_records.exists():
        inventory_record = inventory_records.latest('updated_on')
        quantity = inventory_record.closing_stock_quantity

    return quantity
