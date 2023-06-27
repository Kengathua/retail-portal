"""."""

import pytest
from decimal import Decimal
from django.utils import timezone

from elites_retail_portal.enterprises.models import Enterprise
from elites_retail_portal.warehouses.models import (
    Warehouse, WarehouseItem, WarehouseWarehouseItem, WarehouseRecord)
from elites_retail_portal.debit.models import Inventory
from elites_retail_portal.catalog.models import Catalog
from elites_retail_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemModel, ItemType,
    ItemUnits, UnitsItemType, Units)
from elites_retail_portal.debit.models import (
    InventoryItem, InventoryRecord, InventoryInventoryItem)
from elites_retail_portal.debit.stock.reports import (
    generate_stock_report, generate_items_history)
from elites_retail_portal.enterprise_mgt.models import (
    EnterpriseSetupRule, EnterpriseSetupRuleCatalog,
    EnterpriseSetupRuleInventory, EnterpriseSetupRuleWarehouse)
from elites_retail_portal.catalog.models import CatalogItem
from model_bakery import baker

pytestmark = pytest.mark.django_db


def test_create_stock_report():
    """."""
    franchise = baker.make(Enterprise, name='Elites Age Supermarket')
    enterprise_code = franchise.enterprise_code
    cat = baker.make(
        Category, category_name='Cat One',
        enterprise=enterprise_code)
    item_type = baker.make(
        ItemType, category=cat, type_name='Cooker',
        enterprise=enterprise_code)
    brand = baker.make(
        Brand, brand_name='Samsung', enterprise=enterprise_code)
    baker.make(
        BrandItemType, brand=brand, item_type=item_type,
        enterprise=enterprise_code)
    item_model = baker.make(
        ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
        enterprise=enterprise_code)
    item = baker.make(
        Item, item_model=item_model, barcode='83838388383', make_year=2020,
        enterprise=enterprise_code)
    s_units = baker.make(Units, units_name='packet', enterprise=enterprise_code)
    baker.make(UnitsItemType, item_type=item_type, units=s_units, enterprise=enterprise_code)
    s_units.item_types.set([item_type])
    s_units.save()
    p_units = baker.make(Units, units_name='Dozen', enterprise=enterprise_code)
    baker.make(UnitsItemType, item_type=item_type, units=p_units, enterprise=enterprise_code)
    p_units.item_types.set([item_type])
    p_units.save()
    baker.make(
        ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
        quantity_of_sale_units_per_purchase_unit=12, enterprise=enterprise_code)
    inventory_item = baker.make(InventoryItem, item=item, enterprise=enterprise_code)
    warehouse_item = baker.make(WarehouseItem, item=item, enterprise=enterprise_code)
    inventory = baker.make(
        Inventory, inventory_name='Elites Age Supermarket Available Inventory',
        is_default=True, is_master=True,
        is_active=True, inventory_type='AVAILABLE', enterprise=enterprise_code)
    catalog = baker.make(
        Catalog, catalog_name='Elites Age Supermarket Standard Catalog',
        is_default=True,
        description='Standard Catalog', is_standard=True, enterprise=enterprise_code)
    warehouse = baker.make(
        Warehouse, warehouse_name='Elites Private Warehouse', is_default=True,
        is_receiving=True, enterprise=enterprise_code)
    rule = baker.make(
        EnterpriseSetupRule, name='Elites Age', is_active=True, enterprise=enterprise_code)
    baker.make(
        EnterpriseSetupRuleInventory, rule=rule, inventory=inventory,
        enterprise=enterprise_code)
    baker.make(
        EnterpriseSetupRuleWarehouse, rule=rule, warehouse=warehouse,
        enterprise=enterprise_code)
    baker.make(
        EnterpriseSetupRuleCatalog, rule=rule, catalog=catalog,
        enterprise=enterprise_code)
    report = generate_stock_report(enterprise_code)
    assert len(report['stock_data']) == 1
    assert report == {
        'stock_data': [
            {
                'item': 'SAMSUNG GE731K-B SUT COOKER',
                'marked_price': 0,
                'quantity_in_catalog': 0,
                'quantity_in_inventory': 0,
                'quantity_in_warehouse': 0,
                'selling_price': 0,
                'status': 'INACTIVE',
                'threshold_price': 0
            }
        ],
        'totals_data': {
            'quantity_in_catalog': 0,
            'quantity_in_inventory': 0,
            'quantity_in_warehouse': 0
        }
    }

    catalog_item = baker.make(
        CatalogItem, inventory_item=inventory_item, enterprise=enterprise_code,
        marked_price=60000)
    assert catalog_item
    report = generate_stock_report(enterprise_code)
    assert report == {
        'stock_data': [
            {
                'item': 'SAMSUNG GE731K-B SUT COOKER',
                'marked_price': Decimal('60000.00'),
                'quantity_in_catalog': 0.0,
                'quantity_in_inventory': 0,
                'quantity_in_warehouse': 0,
                'selling_price': Decimal('60000.00'),
                'status': 'INACTIVE',
                'threshold_price': Decimal('60000.00')
            }
        ],
        'totals_data': {
            'quantity_in_catalog': 0.0,
            'quantity_in_inventory': 0,
            'quantity_in_warehouse': 0
        }
    }

    baker.make(
        InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item,
        enterprise=enterprise_code)
    record_date = timezone.now()
    inventory_record = baker.make(
        InventoryRecord, inventory=inventory, inventory_item=inventory_item,
        record_date=record_date, record_type='ADD', quantity_recorded=5,
        unit_price=60000, enterprise=enterprise_code)
    assert inventory_record
    report = generate_stock_report(enterprise_code)
    assert report == {
        'stock_data': [
            {
                'item': 'SAMSUNG GE731K-B SUT COOKER',
                'marked_price': Decimal('60000.00'),
                'quantity_in_catalog': 5.0,
                'quantity_in_inventory': 5.0,
                'quantity_in_warehouse': 0,
                'selling_price': Decimal('60000.00'),
                'status': 'INACTIVE',
                'threshold_price': Decimal('60000.00')
            }
        ],
        'totals_data': {
            'quantity_in_catalog': 5.0,
            'quantity_in_inventory': 5.0,
            'quantity_in_warehouse': 0
        }
    }

    baker.make(
        WarehouseWarehouseItem, warehouse=warehouse, warehouse_item=warehouse_item,
        enterprise=enterprise_code)
    record_date = timezone.now()
    warehouse_record1 = baker.make(
        WarehouseRecord, warehouse=warehouse, warehouse_item=warehouse_item,
        record_date=record_date, record_type='ADD', quantity_recorded=3,
        unit_price=60000, enterprise=enterprise_code)
    assert warehouse_record1
    report = generate_stock_report(enterprise_code)

    assert report == {
        'stock_data': [
            {
                'item': 'SAMSUNG GE731K-B SUT COOKER',
                'marked_price': Decimal('60000.00'),
                'quantity_in_catalog': 5.0,
                'quantity_in_inventory': 5.0,
                'quantity_in_warehouse': 3.0,
                'selling_price': Decimal('60000.00'),
                'status': 'INACTIVE',
                'threshold_price': Decimal('60000.00')
            }
        ],
        'totals_data': {
            'quantity_in_catalog': 5.0,
            'quantity_in_inventory': 5.0,
            'quantity_in_warehouse': 3.0
        }
    }

    item.activate()
    report = generate_stock_report(enterprise_code)

    assert report == {
        'stock_data': [
            {
                'item': 'SAMSUNG GE731K-B SUT COOKER',
                'marked_price': Decimal('60000.00'),
                'quantity_in_catalog': 5.0,
                'quantity_in_inventory': 5.0,
                'quantity_in_warehouse': 3.0,
                'selling_price': Decimal('60000.00'),
                'status': 'ACTIVE',
                'threshold_price': Decimal('60000.00')
            }
        ],
        'totals_data': {
            'quantity_in_catalog': 5.0,
            'quantity_in_inventory': 5.0,
            'quantity_in_warehouse': 3.0
        }
    }

    warehouse_record2 = baker.make(
        WarehouseRecord, warehouse=warehouse, warehouse_item=warehouse_item,
        record_type='REMOVE', removal_type='INVENTORY', quantity_recorded=2,
        unit_price=60000, enterprise=enterprise_code)
    assert warehouse_record2
    report = generate_stock_report(enterprise_code)
    assert report == {
        'stock_data': [
            {
                'item': 'SAMSUNG GE731K-B SUT COOKER',
                'marked_price': Decimal('60000.00'),
                'quantity_in_catalog': 7.0,
                'quantity_in_inventory': 7.0,
                'quantity_in_warehouse': 1.0,
                'selling_price': Decimal('60000.00'),
                'status': 'ACTIVE',
                'threshold_price': Decimal('60000.00')
            }
        ],
        'totals_data': {
            'quantity_in_catalog': 7.0,
            'quantity_in_inventory': 7.0,
            'quantity_in_warehouse': 1.0
        }
    }


def test_generate_items_history():
    """."""
    franchise = baker.make(Enterprise, name='Elites Age Supermarket')
    enterprise_code = franchise.enterprise_code
    cat = baker.make(
        Category, category_name='Cat One',
        enterprise=enterprise_code)
    item_type = baker.make(
        ItemType, category=cat, type_name='Cooker',
        enterprise=enterprise_code)
    brand = baker.make(
        Brand, brand_name='Samsung', enterprise=enterprise_code)
    baker.make(
        BrandItemType, brand=brand, item_type=item_type,
        enterprise=enterprise_code)
    item_model = baker.make(
        ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
        enterprise=enterprise_code)
    item = baker.make(
        Item, item_model=item_model, barcode='83838388383', make_year=2020,
        enterprise=enterprise_code)
    s_units = baker.make(Units, units_name='packet', enterprise=enterprise_code)
    baker.make(UnitsItemType, item_type=item_type, units=s_units, enterprise=enterprise_code)
    s_units.item_types.set([item_type])
    s_units.save()
    p_units = baker.make(Units, units_name='Dozen', enterprise=enterprise_code)
    baker.make(UnitsItemType, item_type=item_type, units=p_units, enterprise=enterprise_code)
    p_units.item_types.set([item_type])
    p_units.save()
    baker.make(
        ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
        quantity_of_sale_units_per_purchase_unit=12, enterprise=enterprise_code)
    inventory_item = baker.make(InventoryItem, item=item, enterprise=enterprise_code)
    warehouse_item = baker.make(WarehouseItem, item=item, enterprise=enterprise_code)
    inventory = baker.make(
        Inventory, inventory_name='Elites Age Supermarket Available Inventory',
        is_default=True, is_master=True,
        is_active=True, inventory_type='AVAILABLE', enterprise=enterprise_code)
    catalog = baker.make(
        Catalog, catalog_name='Elites Age Supermarket Standard Catalog',
        is_default=True,
        description='Standard Catalog', is_standard=True, enterprise=enterprise_code)
    warehouse = baker.make(
        Warehouse, warehouse_name='Elites Private Warehouse', is_default=True,
        is_receiving=True, enterprise=enterprise_code)
    rule = baker.make(
        EnterpriseSetupRule, name='Elites Age', is_active=True, enterprise=enterprise_code)
    baker.make(
        EnterpriseSetupRuleInventory, rule=rule, inventory=inventory,
        enterprise=enterprise_code)
    baker.make(
        EnterpriseSetupRuleWarehouse, rule=rule, warehouse=warehouse,
        enterprise=enterprise_code)
    baker.make(
        EnterpriseSetupRuleCatalog, rule=rule, catalog=catalog,
        enterprise=enterprise_code)
    history = generate_items_history(enterprise_code)
    assert history == {}
    item.activate()
    items_history1 = generate_items_history(enterprise_code)
    history_keys = list(items_history1.keys())
    assert str(item.id) in history_keys
    assert items_history1[str(item.id)]['history'] == []

    catalog_item = baker.make(
        CatalogItem, inventory_item=inventory_item, enterprise=enterprise_code,
        marked_price=60000)
    assert catalog_item
    items_history2 = generate_items_history(enterprise_code)
    history_keys = list(items_history2.keys())
    assert str(item.id) in history_keys
    assert items_history2[str(item.id)]['history'] == []

    baker.make(
        InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item,
        enterprise=enterprise_code)
    record_date1 = timezone.now()
    onboarding_inventory_record = baker.make(
        InventoryRecord, inventory=inventory, inventory_item=inventory_item,
        record_date=record_date1, record_type='ADD', quantity_recorded=5,
        unit_price=60000, enterprise=enterprise_code)
    assert onboarding_inventory_record
    items_history3 = generate_items_history(enterprise_code)
    history_keys = list(items_history3.keys())
    assert str(item.id) in history_keys
    assert items_history3[str(item.id)]['history'] == [
        {
            'closing_quantity': 5.0,
            'date': record_date1,
            'item': 'SAMSUNG GE731K-B SUT COOKER',
            'opening_quantity': 0,
            'quantity': 5.0,
            'source': 'INVENTORY',
            'total': 300000.0,
            'type': 'ONBOARDING',
            'unit_price': 60000.0
        }
    ]

    baker.make(
        WarehouseWarehouseItem, warehouse=warehouse, warehouse_item=warehouse_item,
        enterprise=enterprise_code)
    record_date2 = timezone.now()
    onboarding_warehouse_record1 = baker.make(
        WarehouseRecord, warehouse=warehouse, warehouse_item=warehouse_item,
        record_date=record_date2, record_type='ADD', quantity_recorded=3,
        unit_price=60000, enterprise=enterprise_code)
    assert onboarding_warehouse_record1
    items_history4 = generate_items_history(enterprise_code)
    history_keys = list(items_history4.keys())
    assert str(item.id) in history_keys
    assert items_history4[str(item.id)]['history'] == [
        {
            'closing_quantity': 5.0,
            'date': record_date1,
            'item': 'SAMSUNG GE731K-B SUT COOKER',
            'opening_quantity': 0.0,
            'quantity': 5.0,
            'source': 'INVENTORY',
            'total': 300000.0,
            'type': 'ONBOARDING',
            'unit_price': 60000.0
        },
        {
            'closing_quantity': 8.0,
            'date': record_date2,
            'item': 'SAMSUNG GE731K-B SUT COOKER',
            'opening_quantity': 5.0,
            'quantity': 3.0,
            'source': 'WAREHOUSE',
            'total': 180000.0,
            'type': 'ONBOARDING',
            'unit_price': 60000.0
        }
    ]

    record_date3 = timezone.now()
    warehouse_record2 = baker.make(
        WarehouseRecord, record_date=record_date3, warehouse=warehouse,
        warehouse_item=warehouse_item, record_type='REMOVE', removal_type='INVENTORY',
        quantity_recorded=2, unit_price=60000, enterprise=enterprise_code)
    assert warehouse_record2
    inventory_record1 = InventoryRecord.objects.get(addition_guid=warehouse_record2.id)
    items_history5 = generate_items_history(enterprise_code)
    history_keys = list(items_history5.keys())
    assert str(item.id) in history_keys
    assert items_history5[str(item.id)]['history'] == [
        {
            'closing_quantity': 5.0,
            'date': record_date1,
            'item': 'SAMSUNG GE731K-B SUT COOKER',
            'opening_quantity': 0.0,
            'quantity': 5.0,
            'source': 'INVENTORY',
            'total': 300000.0,
            'type': 'ONBOARDING',
            'unit_price': 60000.0
        },
        {
            'closing_quantity': 8.0,
            'date': record_date2,
            'item': 'SAMSUNG GE731K-B SUT COOKER',
            'opening_quantity': 5.0,
            'quantity': 3.0,
            'source': 'WAREHOUSE',
            'total': 180000.0,
            'type': 'ONBOARDING',
            'unit_price': 60000.0
        },
        {
            'closing_quantity': 6.0,
            'date': record_date3,
            'item': 'SAMSUNG GE731K-B SUT COOKER',
            'opening_quantity': 8.0,
            'quantity': -2.0,
            'source': 'WAREHOUSE',
            'total': -120000.0,
            'type': 'REMOVAL',
            'unit_price': 60000.0
        },
        {
            'closing_quantity': 8.0,
            'date': inventory_record1.record_date,
            'item': 'SAMSUNG GE731K-B SUT COOKER',
            'opening_quantity': 6.0,
            'quantity': 2.0,
            'source': 'INVENTORY',
            'total': 120000.0,
            'type': 'ADDITION',
            'unit_price': 60000.0
        }
    ]

    record_date4 = timezone.now()
    inventory_record2 = baker.make(
        InventoryRecord, record_date=record_date4, inventory=inventory,
        inventory_item=inventory_item, record_type='ADD', quantity_recorded=2,
        unit_price=60000, enterprise=enterprise_code)
    assert inventory_record2
    items_history6 = generate_items_history(enterprise_code)
    history_keys = list(items_history6.keys())
    assert str(item.id) in history_keys
    assert items_history6[str(item.id)]['history'] == [
        {
            'closing_quantity': 5.0,
            'date': record_date1,
            'item': 'SAMSUNG GE731K-B SUT COOKER',
            'opening_quantity': 0.0,
            'quantity': 5.0,
            'source': 'INVENTORY',
            'total': 300000.0,
            'type': 'ONBOARDING',
            'unit_price': 60000.0
        },
        {
            'closing_quantity': 8.0,
            'date': record_date2,
            'item': 'SAMSUNG GE731K-B SUT COOKER',
            'opening_quantity': 5.0,
            'quantity': 3.0,
            'source': 'WAREHOUSE',
            'total': 180000.0,
            'type': 'ONBOARDING',
            'unit_price': 60000.0
        },
        {
            'closing_quantity': 6.0,
            'date': record_date3,
            'item': 'SAMSUNG GE731K-B SUT COOKER',
            'opening_quantity': 8.0,
            'quantity': -2.0,
            'source': 'WAREHOUSE',
            'total': -120000.0,
            'type': 'REMOVAL',
            'unit_price': 60000.0
        },
        {
            'closing_quantity': 8.0,
            'date': inventory_record1.record_date,
            'item': 'SAMSUNG GE731K-B SUT COOKER',
            'opening_quantity': 6.0,
            'quantity': 2.0,
            'source': 'INVENTORY',
            'total': 120000.0,
            'type': 'ADDITION',
            'unit_price': 60000.0
        },
        {
            'closing_quantity': 10.0,
            'date': record_date4,
            'item': 'SAMSUNG GE731K-B SUT COOKER',
            'opening_quantity': 8.0,
            'quantity': 2.0,
            'source': 'INVENTORY',
            'total': 120000.0,
            'type': 'ADDITION',
            'unit_price': 60000.0
        }
    ]
