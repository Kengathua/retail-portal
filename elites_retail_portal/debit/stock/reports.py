"""Stock report workflow."""

from operator import itemgetter

from elites_retail_portal.catalog.models import CatalogItem
from elites_retail_portal.debit.models import (
    InventoryItem, InventoryRecord, PurchasesReturn, SaleItem)
from elites_retail_portal.items.models import Item
from elites_retail_portal.items.serializers import ItemSerializer
from elites_retail_portal.enterprise_mgt.helpers import (
    get_valid_enterprise_setup_rules)
from elites_retail_portal.warehouses.models import WarehouseItem, WarehouseRecord
from elites_retail_portal.credit.models import PurchaseItem, SalesReturn


def create_report_data(inventory_items, all=True):
    """Create report data."""
    stock_data = []
    totals_data = {}
    total_quantity_in_catalog = 0
    total_quantity_in_warehouse = 0
    total_quantity_in_inventory = 0
    available_inventory = get_valid_enterprise_setup_rules(
        inventory_items[0].enterprise).available_inventory
    default_warehouse = get_valid_enterprise_setup_rules(
        inventory_items[0].enterprise).default_warehouse

    if all:
        inventory_items_ids = list(map(str, inventory_items.values_list('id', flat=True)))
        included_items_ids = list(map(str, inventory_items.values_list('item__id', flat=True)))
        catalog_items = CatalogItem.objects.filter(inventory_item__id__in=inventory_items_ids)
        cataloged_inventory_items_ids = list(
            map(str, catalog_items.values_list('inventory_item__id', flat=True)))
        uncataloged_inventory_items = InventoryItem.objects.exclude(
            id__in=cataloged_inventory_items_ids)
        excluded_items = Item.objects.exclude(id__in=included_items_ids)

        if catalog_items:
            for catalog_item in catalog_items:
                warehouse_item = WarehouseItem.objects.get(
                    item=catalog_item.inventory_item.item)
                inventory_summary = available_inventory.get_inventory_item_summary(
                    catalog_item.inventory_item)
                warehouse_summary = default_warehouse.get_warehouse_item_summary(warehouse_item)
                data = {
                    'item': catalog_item.inventory_item.item.item_name,
                    'quantity_in_catalog': catalog_item.quantity,
                    'quantity_in_warehouse': warehouse_summary['closing_quantity'],
                    'quantity_in_inventory': inventory_summary['closing_stock_quantity'],
                    'status': 'ACTIVE' if catalog_item.inventory_item.item.is_active else "INACTIVE",   # noqa
                    'marked_price': catalog_item.marked_price,
                    'selling_price': catalog_item.selling_price,
                    'threshold_price': catalog_item.threshold_price,
                }
                stock_data.append(data)
                total_quantity_in_catalog += data['quantity_in_catalog']
                total_quantity_in_warehouse += data['quantity_in_warehouse']
                total_quantity_in_inventory += data['quantity_in_inventory']

        if uncataloged_inventory_items:
            for inventory_item in uncataloged_inventory_items:
                data = {
                    'item': inventory_item.item.item_name,
                    'quantity_in_catalog': 0,
                    'quantity_in_warehouse': 0,
                    'quantity_in_inventory': 0,
                    'status': 'ACTIVE' if inventory_item.item.is_active else "INACTIVE",
                    'marked_price': 0,
                    'selling_price': 0,
                    'threshold_price': 0,
                }
                stock_data.append(data)
                total_quantity_in_catalog += data['quantity_in_catalog']
                total_quantity_in_warehouse += data['quantity_in_warehouse']
                total_quantity_in_inventory += data['quantity_in_inventory']

        if excluded_items:
            for item in excluded_items:
                data = {
                    'item': item.item_name,
                    'quantity_in_catalog': 0,
                    'quantity_in_warehouse': 0,
                    'quantity_in_inventory': 0,
                    'status': 'ACTIVE' if item.is_active else "INACTIVE",
                    'marked_price': 0,
                    'selling_price': 0,
                    'threshold_price': 0,
                }
                stock_data.append(data)
                total_quantity_in_catalog += data['quantity_in_catalog']
                total_quantity_in_warehouse += data['quantity_in_warehouse']
                total_quantity_in_inventory += data['quantity_in_inventory']

        totals_data['quantity_in_catalog'] = total_quantity_in_catalog
        totals_data['quantity_in_warehouse'] = total_quantity_in_warehouse
        totals_data['quantity_in_inventory'] = total_quantity_in_inventory

        return {
            "stock_data": stock_data,
            "totals_data": totals_data,
        }


def generate_stock_report(enterprise_code, inventory_items=[]):
    """Generate stock report."""
    if inventory_items:
        return create_report_data(inventory_items, all=False)

    inventory_items = InventoryItem.objects.filter(
        enterprise=enterprise_code).order_by('-created_on')
    if inventory_items:
        return create_report_data(inventory_items, all=True)


def get_item_history(enterprise_code, item):    # noqa
    """Generate item history."""
    item_history = []
    warehouse_item_onboarding_record = None
    inventory_item_onboarding_record = None
    warehouse_item_onboarding_records = WarehouseRecord.objects.filter(
        warehouse_item__item=item, opening_quantity=0,
        opening_total_amount=0,  record_type="ADD",
        enterprise=enterprise_code, addition_guid__isnull=True)
    if warehouse_item_onboarding_records.exists():
        warehouse_item_onboarding_record = warehouse_item_onboarding_records.earliest(
            'record_date')

    if warehouse_item_onboarding_record:
        data = {
            "date": warehouse_item_onboarding_record.record_date,
            "item": warehouse_item_onboarding_record.warehouse_item.item.item_name,
            "quantity": warehouse_item_onboarding_record.quantity_recorded,
            "unit_price": warehouse_item_onboarding_record.unit_price,
            "total": float(
                warehouse_item_onboarding_record.unit_price) * float(
                    warehouse_item_onboarding_record.quantity_recorded),
            "source": "WAREHOUSE",
            "type": "ONBOARDING",
        }

        item_history.append(data)

    inventory_item_onboarding_records = InventoryRecord.objects.filter(
        inventory_item__item=item, opening_stock_quantity=0,
        opening_stock_total_amount=0,  record_type="ADD",
        enterprise=enterprise_code, addition_guid__isnull=True)

    if inventory_item_onboarding_records.exists():
        inventory_item_onboarding_record = inventory_item_onboarding_records.earliest(
            'record_date')

    if inventory_item_onboarding_record:
        data = {
            "date": inventory_item_onboarding_record.record_date,
            "item": inventory_item_onboarding_record.inventory_item.item.item_name,
            "quantity": inventory_item_onboarding_record.quantity_recorded,
            "unit_price": inventory_item_onboarding_record.unit_price,
            "total": float(
                inventory_item_onboarding_record.unit_price) * float(
                    inventory_item_onboarding_record.quantity_recorded),
            "source": "INVENTORY",
            "type": "ONBOARDING",
        }
        item_history.append(data)

    warehouse_records = WarehouseRecord.objects.filter(
        warehouse_item__item=item, enterprise=enterprise_code, addition_guid__isnull=True,
        removal_guid__isnull=True)
    if warehouse_records.exists() and warehouse_item_onboarding_record:
        warehouse_records = warehouse_records.exclude(id=warehouse_item_onboarding_record.id)
        if warehouse_records:
            for warehouse_record in warehouse_records:
                data = {
                    "date": warehouse_record.record_date,
                    "item": warehouse_record.warehouse_item.item.item_name,
                    "quantity": warehouse_record.quantity_recorded,
                    "unit_price": warehouse_record.unit_price,
                    "total": float(
                        warehouse_record.unit_price) * float(
                            warehouse_record.quantity_recorded),
                    "source": "WAREHOUSE",
                    "type": "ADDITION",
                }
                item_history.append(data)

    warehouse_records = WarehouseRecord.objects.filter(
        warehouse_item__item=item, enterprise=enterprise_code, addition_guid__isnull=True,
        removal_guid__isnull=False)
    if warehouse_records.exists():
        for warehouse_record in warehouse_records:
            data = {
                "date": warehouse_record.record_date,
                "item": warehouse_record.warehouse_item.item.item_name,
                "quantity": warehouse_record.quantity_recorded,
                "unit_price": warehouse_record.unit_price,
                "total": float(
                    warehouse_record.unit_price) * float(
                        warehouse_record.quantity_recorded),
                "source": "WAREHOUSE",
                "type": "REMOVAL",
            }
            item_history.append(data)

            inventory_records = InventoryRecord.objects.filter(addition_guid=warehouse_record.id)
            if inventory_records.exists():
                for inventory_record in inventory_records:
                    data = {
                        "date": inventory_record.record_date,
                        "item": inventory_record.inventory_item.item.item_name,
                        "quantity": inventory_record.quantity_recorded,
                        "unit_price": inventory_record.unit_price,
                        "total": float(
                            inventory_record.unit_price) * float(
                                inventory_record.quantity_recorded),
                        "source": "INVENTORY",
                        "type": "ADDITION",
                    }
                    item_history.append(data)

    inventory_records = InventoryRecord.objects.filter(
        inventory_item__item=item, enterprise=enterprise_code, addition_guid__isnull=True,
        removal_guid__isnull=True)
    if inventory_records.exists() and inventory_item_onboarding_record:
        inventory_records = inventory_records.exclude(id=inventory_item_onboarding_record.id)
        if inventory_records:
            for inventory_record in inventory_records:
                data = {
                    "date": inventory_record.record_date,
                    "item": inventory_record.inventory_item.item.item_name,
                    "quantity": inventory_record.quantity_recorded,
                    "unit_price": inventory_record.unit_price,
                    "total": float(
                        inventory_record.unit_price) * float(
                            inventory_record.quantity_recorded),
                    "source": "INVENTORY",
                    "type": "ADDITION",
                }
                item_history.append(data)

    purchase_items = PurchaseItem.objects.filter(item=item)
    if purchase_items:
        for purchase_item in purchase_items:
            data = {
                "date": purchase_item.purchase.purchase_date,
                "item": purchase_item.item.item_name,
                "opening_quantity": 0,
                "quantity": purchase_item.quantity_purchased,
                "closing_quantity": purchase_item.quantity_purchased,
                "unit_price": purchase_item.unit_cost,
                "total": float(
                    purchase_item.unit_cost) * float(purchase_item.quantity_purchased),
                "source": "PURCHASES",
                "type": "ADDITION",
            }

            item_history.append(data)

            purchase_return = PurchasesReturn.objects.filter(purchase_item=purchase_item).first()
            if purchase_return:
                data = {
                    "date": purchase_return.return_date,
                    "item": purchase_return.purchase_item.item.item_name,
                    "opening_quantity": 0,
                    "quantity": purchase_return.quantity_returned,
                    "closing_quantity": purchase_return.quantity_returned,
                    "unit_price": purchase_return.unit_cost,
                    "total": float(
                        purchase_return.unit_cost) * float(purchase_return.quantity_returned),
                    "source": "PURCHASES",
                    "type": "REMOVAL",
                }
                item_history.append(data)

    sale_items = SaleItem.objects.filter(catalog_item__inventory_item__item=item)
    for sale_item in sale_items:
        data = {
            "date": sale_item.sale.sale_date,
            "item": sale_item.catalog_item.inventory_item.item.item_name,
            "quantity": sale_item.quantity_sold,
            "unit_price": sale_item.selling_price,
            "total": float(sale_item.selling_price) * float(sale_item.quantity_sold),
            "source": "SALES",
            "type": "REMOVAL",
        }
        item_history.append(data)
        sales_returns = SalesReturn.objects.filter(sale_item=sale_item)
        for sale_return in sales_returns:
            data = {
                "date": sale_return.return_date,
                "item": sale_return.sale_item.catalog_item.inventory_item.item.item_name,
                "quantity": sale_return.quantity_returned,
                "unit_price": sale_return.unit_price,
                "total": float(
                    sale_return.unit_price) * float(sale_return.quantity_returned),
                "source": "SALES",
                "type": "ADDITION",
            }
            item_history.append(data)

    item_history.sort(key=itemgetter('date'))
    if len(item_history) >= 1:
        for count, history in enumerate(item_history):
            if count == 0:
                history['opening_quantity'] = 0
                history['closing_quantity'] = history['quantity']

                item_history[count] = history

            else:
                history['opening_quantity'] = item_history[count-1]['closing_quantity']
                history['closing_quantity'] = (
                    item_history[count-1]['closing_quantity'] + history['quantity'])
                if history['type'] == "REMOVAL":
                    history['closing_quantity'] = (
                        item_history[count-1]['closing_quantity'] - history['quantity'])
                    history['quantity'] = -history['quantity']
                    history['total'] = -history['total']

                item_history[count] = history

    return item_history


def generate_items_history(enterprise_code, item=None):
    """Generate item history."""
    history = {}
    if item:
        history[str(item.id)] = {
            "item": ItemSerializer(item).data,
            "history": get_item_history(enterprise_code, item),
        }
        return history

    items = Item.objects.filter(enterprise=enterprise_code, is_active=True)
    for item in items:
        history[str(item.id)] = {
            "item": ItemSerializer(item).data,
            "history": get_item_history(enterprise_code, item),
        }
    return history
