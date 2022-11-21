import uuid
import django

django.setup()

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
from django.conf import settings
from elites_franchise_portal.enterprise_mgt.models import (
    EnterpriseSetupRule, EnterpriseSetupRuleCatalog, EnterpriseSetupRuleInventory, EnterpriseSetupRuleWarehouse)

# settings.configure()

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

rule,_ = EnterpriseSetupRule.objects.update_or_create(
    name='Elites Age Supermarket', is_default=True, supports_installment_sales=True,
    is_active=True, **audit_fields)
