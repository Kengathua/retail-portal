"""."""

def activate_warehouse_item(warehouse, item, audit_fields):
    """Activate Warehouse item."""
    from elites_franchise_portal.warehouses.models import (
        WarehouseItem, WarehouseWarehouseItem)

    warehouse_item = WarehouseItem.objects.filter(item=item, is_active=True).first()
    if not warehouse_item:
        payload = {
            "item": item,
            "description": item.item_name,
            "is_active": True,
        }
        warehouse_item = WarehouseItem.objects.create(**payload, **audit_fields)

    warehouse_warehouse_item = WarehouseWarehouseItem.objects.filter(
        warehouse=warehouse, warehouse_item=warehouse_item, is_active=True).first()
    if not warehouse_warehouse_item:
        payload = {
            'warehouse': warehouse,
            'warehouse_item': warehouse_item,
            'is_active': True,
        }
        WarehouseWarehouseItem.objects.create(**payload, **audit_fields)


def activate_inventory_item(inventory, item, audit_fields):
    """Activate Inventory item."""
    from elites_franchise_portal.debit.models import (
        InventoryItem, InventoryInventoryItem)

    inventory_item = InventoryItem.objects.filter(
        item=item, is_active=True).first()
    if not inventory_item:
        payload = {
            "item": item,
            "description": item.item_name,
            "is_active": True,
        }
        inventory_item = InventoryItem.objects.create(
            **payload, **audit_fields)

    inventory_inventory_item = InventoryInventoryItem.objects.filter(
        inventory=inventory, inventory_item=inventory_item,
        is_active=True).first()
    if not inventory_inventory_item:
        payload = {
            'inventory': inventory,
            'inventory_item': inventory_item,
            'is_active': True,
        }
        InventoryInventoryItem.objects.create(**payload, **audit_fields)
