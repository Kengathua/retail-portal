"""."""

import uuid
import pytest
from unittest import mock

from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from elites_retail_portal.catalog.models import (
    Section, Catalog, CatalogItem, CatalogCatalogItem, CatalogItemAuditLog)
from elites_retail_portal.customers.models import Customer
from elites_retail_portal.debit.models import (
    InventoryItem, Inventory, InventoryRecord, InventoryInventoryItem)
from elites_retail_portal.encounters.models import Encounter
from elites_retail_portal.enterprises.models import Enterprise
from elites_retail_portal.enterprise_mgt.models import (
    EnterpriseSetupRule, EnterpriseSetupRuleCatalog,
    EnterpriseSetupRuleInventory, EnterpriseSetupRuleWarehouse)
from elites_retail_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemAttribute, ItemModel, ItemType,
    ItemUnits, UnitsItemType, Units)
from elites_retail_portal.orders.models import (
    Cart, CartItem)
from elites_retail_portal.warehouses.models import Warehouse
from elites_retail_portal.catalog.helpers import get_catalog_item_available_quantity

from model_bakery import baker
from model_bakery.recipe import Recipe

pytestmark = pytest.mark.django_db
MK_ROOT = 'elites_retail_portal.encounters'


@mock.patch(MK_ROOT + '.tasks.process_customer_encounter')
def test_get_catalog_item_available_quantity(mock_process_customer_encounter):
    """."""

    franchise = baker.make(Enterprise, name='Elites Age Supermarket')
    enterprise_code = franchise.enterprise_code
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
        is_receiving=True,
        enterprise=enterprise_code)
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
    baker.make(
        InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item)
    catalog_item = baker.make(
        CatalogItem, inventory_item=inventory_item, enterprise=enterprise_code)

    with pytest.raises(ValidationError) as ve:
        get_catalog_item_available_quantity(catalog_item, True)
    msg = 'The item does not exist in the default catalog'
    assert msg in ve.value.messages

    user = get_user_model().objects.create_superuser(
            email='user@email.com', first_name='Test', last_name='User',
            guid=uuid.uuid4(),
            password='Testpass254$', enterprise=enterprise_code)
    catalog_item.add_to_catalogs(user, [catalog])
    quantity = get_catalog_item_available_quantity(catalog_item, True)
    assert quantity == 0.0

    baker.make(
        InventoryInventoryItem, inventory=inventory, inventory_item=inventory_item)
    baker.make(
        InventoryRecord, inventory=inventory, inventory_item=inventory_item,
        record_type='ADD', quantity_recorded=15, unit_price=300, enterprise=enterprise_code)

    quantity = get_catalog_item_available_quantity(catalog_item, True)
    assert quantity == 15

    billing = [
        {
            'catalog_item': str(catalog_item.id),
            'item_name': catalog_item.inventory_item.item.item_name,
            'quantity': 4,
            'unit_price': 1600,
            'total': 3200,
            'deposit': None,
            'sale_type': 'INSTANT'
        }
    ]
    payments = [
        {
            'means': 'CASH',
            'amount': 5000
        },
        {
            'means': 'MPESA TILL',
            'amount': 2000
        }
    ]

    encounter = baker.make(
        Encounter, billing=billing, processing_status='PENDING',
        payments=payments, submitted_amount=7000, enterprise=enterprise_code)

    quantity = get_catalog_item_available_quantity(catalog_item, True)
    assert quantity == 15 - 4 == 11
