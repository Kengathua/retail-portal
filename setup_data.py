import uuid
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from elites_franchise_portal.customers.models import Customer
from elites_franchise_portal.debit.models.inventory import InventoryInventoryItem
from elites_franchise_portal.enterprises.models import Enterprise
from elites_franchise_portal.items.models import (
    Category, ItemType, Brand, BrandItemType, ItemModel,
    Item, Units, UnitsItemType, ItemUnits)
from elites_franchise_portal.debit.models import (
    Inventory, InventoryItem, InventoryRecord)
from elites_franchise_portal.warehouses.models import (
    Warehouse, WarehouseItem, WarehouseRecord, WarehouseWarehouseItem)
from elites_franchise_portal.catalog.models import (
    Section, Catalog, CatalogItem, CatalogCatalogItem)
from elites_franchise_portal.debit.models import Sale
from elites_franchise_portal.config import settings
from elites_franchise_portal.restrictions_mgt.models import EnterpriseSetupRules

if settings.DEBUG:
    enterprise = Enterprise.objects.create(
        name='Elites Supermarket', updated_by=uuid.uuid4(), created_by=uuid.uuid4())
    user = get_user_model().objects.filter(email='adminuser@email.com')
    if user.exists():
        user = user.first()
    else:
        user = get_user_model().objects.create_superuser(
                email='adminuser@email.com', first_name='Admin', last_name='User',
                guid=uuid.uuid4(), password='Hu46!YftP6^l$', enterprise=enterprise.enterprise_code)

    audit_fields = {
        'created_by': user.id,
        'updated_by': user.id,
        'enterprise': user.enterprise
    }

    receiving_warehouse, _ = Warehouse.objects.update_or_create(
        warehouse_name='Elites Private Warehouse', warehouse_type='PRIVATE',
        description='Will be receiving goods for the supermarket eg Purchases',
        is_default=True, is_active=True, **audit_fields)
    master_inventory, _ = Inventory.objects.update_or_create(
        inventory_name='Elites Age Supermarket Working Stock Inventory',
        is_master=True, is_active=True, inventory_type='WORKING STOCK',
        description='The Reference or Master inventory',
        **audit_fields)
    default_inventory, _ = Inventory.objects.update_or_create(
        inventory_name='Elites Age Supermarket Available Inventory',
        description='Day to day sales will be made frim here inventory',
        is_active=True, inventory_type='AVAILABLE', **audit_fields)
    standard_catalog, _ = Catalog.objects.update_or_create(
        catalog_name='Elites Age Standard Catalog', catalog_code='C-0001',
        description='Will have all items being sold at the shop',
        is_standard=True, **audit_fields)

    EnterpriseSetupRules.objects.update_or_create(
        master_inventory=master_inventory, default_inventory=default_inventory,
        receiving_warehouse=receiving_warehouse, default_warehouse=receiving_warehouse,
        standard_catalog=standard_catalog, default_catalog=standard_catalog,
        is_active=True, **audit_fields)