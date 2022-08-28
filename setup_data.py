import uuid
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from elites_franchise_portal.customers.models import Customer
from elites_franchise_portal.debit.models.inventory import InventoryInventoryItem
from elites_franchise_portal.franchises.models import Franchise
from elites_franchise_portal.items.models import (
    Category, ItemType, Brand, BrandItemType, ItemModel,
    Item, Units, UnitsItemType, ItemUnits)
from elites_franchise_portal.debit.models import (
    Inventory, InventoryItem, InventoryRecord)
from elites_franchise_portal.debit.models import (
    Warehouse, WarehouseItem, WarehouseRecord, WarehouseWarehouseItem)
from elites_franchise_portal.catalog.models import (
    Section, Catalog, CatalogItem, CatalogCatalogItem)
from elites_franchise_portal.debit.models import Sale
from elites_franchise_portal.config import settings

if settings.DEBUG:
    franchise = Franchise.objects.create(
        name='Elites Supermarket', updated_by=uuid.uuid4(), created_by=uuid.uuid4())
    user = get_user_model().objects.filter(email='adminuser@email.com')
    if user.exists():
        user = user.first()
    else:
        user = get_user_model().objects.create_superuser(
                email='adminuser@email.com', first_name='Admin', last_name='User',
                guid=uuid.uuid4(), password='Hu46!YftP6^l$', franchise=franchise.elites_code)

    audit_fields = {
        'created_by': user.id,
        'updated_by': user.id,
        'franchise': user.franchise
    }
