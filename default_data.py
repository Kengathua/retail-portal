import uuid
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from elites_retail_portal.customers.models import Customer
from elites_retail_portal.debit.models.inventory import InventoryInventoryItem
from elites_retail_portal.enterprises.models import Enterprise
from elites_retail_portal.items.models import (
    Category, ItemType, Brand, BrandItemType, ItemModel,
    Item, Units, UnitsItemType, ItemUnits)
from elites_retail_portal.debit.models import (
    Inventory, InventoryItem, InventoryRecord, Sale, SaleItem)
from elites_retail_portal.warehouses.models import (
    Warehouse, WarehouseItem, WarehouseRecord, WarehouseWarehouseItem)
from elites_retail_portal.catalog.models import (
    Section, Catalog, CatalogItem, CatalogCatalogItem)
from elites_retail_portal.debit.models import Sale
from elites_retail_portal.config import settings
from elites_retail_portal.enterprise_mgt.models import EnterpriseSetupRule
from elites_retail_portal.encounters.models import Encounter
from elites_retail_portal.encounters.tasks import process_customer_encounter
from elites_retail_portal.orders.models import Order

from unittest import mock

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

    category1, _ = Category.objects.update_or_create(
        category_name='ELECTRONICS', **audit_fields)
    category2, _ = Category.objects.update_or_create(
        category_name='UTENSILS', **audit_fields)
    category3, _ = Category.objects.update_or_create(
        category_name='FURNITURE', **audit_fields)
    item_type1, _ = ItemType.objects.update_or_create(
        category=category1, type_name='TV', **audit_fields)
    item_type2, _ = ItemType.objects.update_or_create(
        category=category1, type_name='FRIDGE', **audit_fields)
    item_type3, _ = ItemType.objects.update_or_create(
        category=category1, type_name='Microwave', **audit_fields)
    item_type4, _ = ItemType.objects.update_or_create(
        category=category2, type_name='SUFURIA', **audit_fields)
    item_type5, _ = ItemType.objects.update_or_create(
        category=category2, type_name='PAN', **audit_fields)
    item_type6, _ = ItemType.objects.update_or_create(
        category=category2, type_name='PLATES', **audit_fields)
    item_type7, _ = ItemType.objects.update_or_create(
        category=category3, type_name='BED', **audit_fields)
    item_type8, _ = ItemType.objects.update_or_create(
        category=category3, type_name='COUCH', **audit_fields)
    item_type9, _ = ItemType.objects.update_or_create(
        category=category3, type_name='TABLE', **audit_fields)

    brand1, _ = Brand.objects.update_or_create(
        brand_name='SAMSUNG', **audit_fields)
    brand_item_type1, _ = BrandItemType.objects.update_or_create(
        brand=brand1, item_type=item_type1, **audit_fields)
    brand2, _ = Brand.objects.update_or_create(
        brand_name='LG', **audit_fields)
    brand_item_type2, _ = BrandItemType.objects.update_or_create(
        brand=brand2, item_type=item_type2, **audit_fields)
    brand3, _ = Brand.objects.update_or_create(
        brand_name='SONY', **audit_fields)
    brand_item_type3, _ = BrandItemType.objects.update_or_create(
        brand=brand3, item_type=item_type1, **audit_fields)
    brand4, _ = Brand.objects.update_or_create(
        brand_name='MAMBA', **audit_fields)
    brand_item_type4, _ = BrandItemType.objects.update_or_create(
        brand=brand4, item_type=item_type2, **audit_fields)
    brand5, _ = Brand.objects.update_or_create(
        brand_name='SUNDABESTS', **audit_fields)
    brand_item_type5, _ = BrandItemType.objects.update_or_create(
        brand=brand5, item_type=item_type1, **audit_fields)
    brand6, _ = Brand.objects.update_or_create(
        brand_name='THERMO', **audit_fields)
    brand_item_type6, _ = BrandItemType.objects.update_or_create(
        brand=brand6, item_type=item_type2, **audit_fields)
    brand7, _ = Brand.objects.update_or_create(
        brand_name='MILAN', **audit_fields)
    brand_item_type7, _ = BrandItemType.objects.update_or_create(
        brand=brand7, item_type=item_type1, **audit_fields)
    brand8, _ = Brand.objects.update_or_create(
        brand_name='OLYMPIA', **audit_fields)
    brand_item_type8, _ = BrandItemType.objects.update_or_create(
        brand=brand8, item_type=item_type2, **audit_fields)
    brand9, _ = Brand.objects.update_or_create(
        brand_name='MONACO', **audit_fields)
    brand_item_type9, _ = BrandItemType.objects.update_or_create(
        brand=brand9, item_type=item_type1, **audit_fields)



    item_model1, _ = ItemModel.objects.update_or_create(
        brand=brand1, item_type=item_type1, model_name='BGDTDDR677', **audit_fields)
    item_model2, _ = ItemModel.objects.update_or_create(
        brand=brand2, item_type=item_type2, model_name='I5UYTFGD678', **audit_fields)
    item_model3, _ = ItemModel.objects.update_or_create(
        brand=brand3, item_type=item_type3, model_name='HG7FDTYU679', **audit_fields)
    item_model4, _ = ItemModel.objects.update_or_create(
        brand=brand1, item_type=item_type4, model_name='U8YTRFGH680', **audit_fields)
    item_model5, _ = ItemModel.objects.update_or_create(
        brand=brand2, item_type=item_type5, model_name='NB9VCVBN681', **audit_fields)
    item_model6, _ = ItemModel.objects.update_or_create(
        brand=brand3, item_type=item_type6, model_name='GG5RFGBNM674', **audit_fields)
    item_model7, _ = ItemModel.objects.update_or_create(
        brand=brand1, item_type=item_type7, model_name='F9TFGHNJM676', **audit_fields)
    item_model8, _ = ItemModel.objects.update_or_create(
        brand=brand2, item_type=item_type8, model_name='N3BVCDFGH675', **audit_fields)
    item_model9, _ = ItemModel.objects.update_or_create(
        brand=brand3, item_type=item_type9, model_name='E0TRHMNVE673', **audit_fields)
    item_model10, _ = ItemModel.objects.update_or_create(
        brand=brand1, item_type=item_type1, model_name='N3FVDFGHJ672', **audit_fields)

    item_model11, _ = ItemModel.objects.update_or_create(
        brand=brand2, item_type=item_type2, model_name='H8MMDNHE677', **audit_fields)
    item_model12, _ = ItemModel.objects.update_or_create(
        brand=brand3, item_type=item_type3, model_name='KJ14DJDYE678', **audit_fields)
    item_model13, _ = ItemModel.objects.update_or_create(
        brand=brand1, item_type=item_type4, model_name='M6NBFGHJK679', **audit_fields)
    item_model14, _ = ItemModel.objects.update_or_create(
        brand=brand2, item_type=item_type5, model_name='V8BGFYNBB680', **audit_fields)
    item_model15, _ = ItemModel.objects.update_or_create(
        brand=brand3, item_type=item_type6, model_name='J1HGFRTYU681', **audit_fields)
    item_model16, _ = ItemModel.objects.update_or_create(
        brand=brand1, item_type=item_type7, model_name='K6JHRTYUB674', **audit_fields)
    item_model17, _ = ItemModel.objects.update_or_create(
        brand=brand2, item_type=item_type8, model_name='M8NBVDFGE676', **audit_fields)
    item_model18, _ = ItemModel.objects.update_or_create(
        brand=brand3, item_type=item_type9, model_name='R6FGNMNBV675', **audit_fields)
    item_model19, _ = ItemModel.objects.update_or_create(
        brand=brand1, item_type=item_type1, model_name='I4UYGTFGH673', **audit_fields)
    item_model20, _ = ItemModel.objects.update_or_create(
        brand=brand2, item_type=item_type2, model_name='E8FHYEHEG672', **audit_fields)

    item1, _ = Item.objects.update_or_create(
        item_model=item_model1, barcode=12345678,
        make_year=2021, **audit_fields)
    item2, _ = Item.objects.update_or_create(
        item_model=item_model2, barcode=765433346,
        make_year=2021, **audit_fields)
    item3, _ = Item.objects.update_or_create(
        item_model=item_model3, barcode=6655443456,
        make_year=2021, **audit_fields)
    item4, _ = Item.objects.update_or_create(
        item_model=item_model4, barcode=9988776546,
        make_year=2021, **audit_fields)
    item5, _ = Item.objects.update_or_create(
        item_model=item_model5, barcode=4556483833,
        make_year=2021, **audit_fields)
    item6, _ = Item.objects.update_or_create(
        item_model=item_model6, barcode=88363636373,
        make_year=2021, **audit_fields)
    item7, _ = Item.objects.update_or_create(
        item_model=item_model7, barcode=83764545622,
        make_year=2021, **audit_fields)
    item8, _ = Item.objects.update_or_create(
        item_model=item_model8, barcode=988474747646,
        make_year=2021, **audit_fields)
    item9, _ = Item.objects.update_or_create(
        item_model=item_model9, barcode=77376353533,
        make_year=2021, **audit_fields)
    item10, _ = Item.objects.update_or_create(
        item_model=item_model10, barcode=9837365534,
        make_year=2021, **audit_fields)

    item11, _ = Item.objects.update_or_create(
        item_model=item_model11, barcode=92828373664,
        make_year=2021, **audit_fields)
    item12, _ = Item.objects.update_or_create(
        item_model=item_model12, barcode=948474645333,
        make_year=2021, **audit_fields)
    item13, _ = Item.objects.update_or_create(
        item_model=item_model13, barcode=938736363533,
        make_year=2021, **audit_fields)
    item14, _ = Item.objects.update_or_create(
        item_model=item_model14, barcode=847474646444,
        make_year=2021, **audit_fields)
    item15, _ = Item.objects.update_or_create(
        item_model=item_model15, barcode=948474746464,
        make_year=2021, **audit_fields)
    item16, _ = Item.objects.update_or_create(
        item_model=item_model16, barcode=4747464646484,
        make_year=2021, **audit_fields)
    item17, _ = Item.objects.update_or_create(
        item_model=item_model17, barcode=84847494039373,
        make_year=2021, **audit_fields)
    item18, _ = Item.objects.update_or_create(
        item_model=item_model18, barcode=8746453537494,
        make_year=2021, **audit_fields)
    item19, _ = Item.objects.update_or_create(
        item_model=item_model19, barcode=8373635484998,
        make_year=2021, **audit_fields)
    item20, _ = Item.objects.update_or_create(
        item_model=item_model20, barcode=73736363636353,
        make_year=2021, **audit_fields)

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

    EnterpriseSetupRule.objects.update_or_create(
        master_inventory=master_inventory, default_inventory=default_inventory,
        receiving_warehouse=receiving_warehouse, default_warehouse=receiving_warehouse,
        standard_catalog=standard_catalog, default_catalog=standard_catalog,
        is_active=True, **audit_fields)

    s_units, _ = Units.objects.update_or_create(units_name='32 Inch', **audit_fields)
    p_units, _ = Units.objects.update_or_create(units_name='32 Inch', **audit_fields)

    UnitsItemType.objects.update_or_create(item_type=item_type1, units=s_units, **audit_fields)
    UnitsItemType.objects.update_or_create(item_type=item_type2, units=s_units, **audit_fields)
    UnitsItemType.objects.update_or_create(item_type=item_type1, units=p_units, **audit_fields)
    UnitsItemType.objects.update_or_create(item_type=item_type2, units=p_units, **audit_fields)

    ItemUnits.objects.update_or_create(
        item=item1, sales_units=s_units, purchases_units=p_units,
        quantity_of_sale_units_per_purchase_unit=1, **audit_fields)
    ItemUnits.objects.update_or_create(
        item=item2, sales_units=s_units, purchases_units=p_units,
        quantity_of_sale_units_per_purchase_unit=1, **audit_fields)
    ItemUnits.objects.update_or_create(
        item=item3, sales_units=s_units, purchases_units=p_units,
        quantity_of_sale_units_per_purchase_unit=1, **audit_fields)
    ItemUnits.objects.update_or_create(
        item=item4, sales_units=s_units, purchases_units=p_units,
        quantity_of_sale_units_per_purchase_unit=1, **audit_fields)
    ItemUnits.objects.update_or_create(
        item=item5, sales_units=s_units, purchases_units=p_units,
        quantity_of_sale_units_per_purchase_unit=1, **audit_fields)
    ItemUnits.objects.update_or_create(
        item=item6, sales_units=s_units, purchases_units=p_units,
        quantity_of_sale_units_per_purchase_unit=1, **audit_fields)
    ItemUnits.objects.update_or_create(
        item=item7, sales_units=s_units, purchases_units=p_units,
        quantity_of_sale_units_per_purchase_unit=1, **audit_fields)
    ItemUnits.objects.update_or_create(
        item=item8, sales_units=s_units, purchases_units=p_units,
        quantity_of_sale_units_per_purchase_unit=1, **audit_fields)
    ItemUnits.objects.update_or_create(
        item=item9, sales_units=s_units, purchases_units=p_units,
        quantity_of_sale_units_per_purchase_unit=1, **audit_fields)
    ItemUnits.objects.update_or_create(
        item=item10, sales_units=s_units, purchases_units=p_units,
        quantity_of_sale_units_per_purchase_unit=1, **audit_fields)
    ItemUnits.objects.update_or_create(
        item=item11, sales_units=s_units, purchases_units=p_units,
        quantity_of_sale_units_per_purchase_unit=1, **audit_fields)
    ItemUnits.objects.update_or_create(
        item=item12, sales_units=s_units, purchases_units=p_units,
        quantity_of_sale_units_per_purchase_unit=1, **audit_fields)
    ItemUnits.objects.update_or_create(
        item=item13, sales_units=s_units, purchases_units=p_units,
        quantity_of_sale_units_per_purchase_unit=1, **audit_fields)
    ItemUnits.objects.update_or_create(
        item=item14, sales_units=s_units, purchases_units=p_units,
        quantity_of_sale_units_per_purchase_unit=1, **audit_fields)
    ItemUnits.objects.update_or_create(
        item=item15, sales_units=s_units, purchases_units=p_units,
        quantity_of_sale_units_per_purchase_unit=1, **audit_fields)
    ItemUnits.objects.update_or_create(
        item=item16, sales_units=s_units, purchases_units=p_units,
        quantity_of_sale_units_per_purchase_unit=1, **audit_fields)
    ItemUnits.objects.update_or_create(
        item=item17, sales_units=s_units, purchases_units=p_units,
        quantity_of_sale_units_per_purchase_unit=1, **audit_fields)
    ItemUnits.objects.update_or_create(
        item=item18, sales_units=s_units, purchases_units=p_units,
        quantity_of_sale_units_per_purchase_unit=1, **audit_fields)
    ItemUnits.objects.update_or_create(
        item=item19, sales_units=s_units, purchases_units=p_units,
        quantity_of_sale_units_per_purchase_unit=1, **audit_fields)
    ItemUnits.objects.update_or_create(
        item=item20, sales_units=s_units, purchases_units=p_units,
        quantity_of_sale_units_per_purchase_unit=1, **audit_fields)

    item1.activate(user)
    item2.activate(user)
    item3.activate(user)
    item4.activate(user)
    item5.activate(user)
    item6.activate(user)
    item7.activate(user)
    item8.activate(user)
    item9.activate(user)
    item10.activate(user)
    item11.activate(user)
    item12.activate(user)
    item13.activate(user)
    item14.activate(user)
    item15.activate(user)
    item16.activate(user)
    item17.activate(user)
    item18.activate(user)
    item19.activate(user)
    item20.activate(user)

    inventory_item1, _ = InventoryItem.objects.update_or_create(item=item1, **audit_fields)
    inventory_item2, _ = InventoryItem.objects.update_or_create(item=item2, **audit_fields)
    inventory_item3, _ = InventoryItem.objects.update_or_create(item=item3, **audit_fields)
    inventory_item4, _ = InventoryItem.objects.update_or_create(item=item4, **audit_fields)
    inventory_item5, _ = InventoryItem.objects.update_or_create(item=item5, **audit_fields)
    inventory_item6, _ = InventoryItem.objects.update_or_create(item=item6, **audit_fields)
    inventory_item7, _ = InventoryItem.objects.update_or_create(item=item7, **audit_fields)
    inventory_item8, _ = InventoryItem.objects.update_or_create(item=item8, **audit_fields)
    inventory_item9, _ = InventoryItem.objects.update_or_create(item=item9, **audit_fields)
    inventory_item10, _ = InventoryItem.objects.update_or_create(item=item10, **audit_fields)

    inventory_item11, _ = InventoryItem.objects.update_or_create(item=item11, **audit_fields)
    inventory_item12, _ = InventoryItem.objects.update_or_create(item=item12, **audit_fields)
    inventory_item13, _ = InventoryItem.objects.update_or_create(item=item13, **audit_fields)
    inventory_item14, _ = InventoryItem.objects.update_or_create(item=item14, **audit_fields)
    inventory_item15, _ = InventoryItem.objects.update_or_create(item=item15, **audit_fields)
    inventory_item16, _ = InventoryItem.objects.update_or_create(item=item16, **audit_fields)
    inventory_item17, _ = InventoryItem.objects.update_or_create(item=item17, **audit_fields)
    inventory_item18, _ = InventoryItem.objects.update_or_create(item=item18, **audit_fields)
    inventory_item19, _ = InventoryItem.objects.update_or_create(item=item19, **audit_fields)
    inventory_item20, _ = InventoryItem.objects.update_or_create(item=item20, **audit_fields)

    # for inventory_item in InventoryItem.objects.all():
    #     InventoryInventoryItem.objects.update_or_create(
    #         inventory=master_inventory, inventory_item=inventory_item, **audit_fields)
    #     InventoryInventoryItem.objects.update_or_create(
    #         inventory=default_inventory, inventory_item=inventory_item, **audit_fields)

    InventoryRecord.objects.update_or_create(
        inventory=default_inventory,
        inventory_item=inventory_item1, record_type='ADD', quantity_of_stock_on_display=7,
        quantity_recorded=15, unit_price=3000, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory=default_inventory,
        inventory_item=inventory_item2, record_type='ADD', quantity_of_stock_on_display=4,
        quantity_recorded=14, unit_price=2300, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory=default_inventory,
        inventory_item=inventory_item3, record_type='ADD', quantity_of_stock_on_display=3,
        quantity_recorded=10, unit_price=3500, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory=default_inventory,
        inventory_item=inventory_item4, record_type='ADD', quantity_of_stock_on_display=14,
        quantity_recorded=25, unit_price=4100, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory=default_inventory,
        inventory_item=inventory_item5, record_type='ADD', quantity_of_stock_on_display=26,
        quantity_recorded=45, unit_price=500, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory=default_inventory,
        inventory_item=inventory_item6, record_type='ADD', quantity_of_stock_on_display=17,
        quantity_recorded=35, unit_price=300, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory=default_inventory,
        inventory_item=inventory_item7, record_type='ADD', quantity_of_stock_on_display=7,
        quantity_recorded=17, unit_price=3700, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory=default_inventory,
        inventory_item=inventory_item8, record_type='ADD', quantity_of_stock_on_display=5,
        quantity_recorded=13, unit_price=5200, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory=default_inventory,
        inventory_item=inventory_item9, record_type='ADD', quantity_of_stock_on_display=3,
        quantity_recorded=9, unit_price=5600, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory=default_inventory,
        inventory_item=inventory_item10, record_type='ADD', quantity_of_stock_on_display=6,
        quantity_recorded=8, unit_price=700, **audit_fields)

    InventoryRecord.objects.update_or_create(
        inventory=default_inventory,
        inventory_item=inventory_item11, record_type='ADD', quantity_of_stock_on_display=3,
        quantity_recorded=6, unit_price=20000, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory=default_inventory,
        inventory_item=inventory_item12, record_type='ADD', quantity_of_stock_on_display=4,
        quantity_recorded=12, unit_price=30500, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory=default_inventory,
        inventory_item=inventory_item13, record_type='ADD', quantity_of_stock_on_display=7,
        quantity_recorded=16, unit_price=42000, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory=default_inventory,
        inventory_item=inventory_item14, record_type='ADD', quantity_of_stock_on_display=6,
        quantity_recorded=11, unit_price=66000, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory=default_inventory,
        inventory_item=inventory_item15, record_type='ADD', quantity_of_stock_on_display=13,
        quantity_recorded=18, unit_price=38000, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory=default_inventory,
        inventory_item=inventory_item16, record_type='ADD', quantity_of_stock_on_display=4,
        quantity_recorded=13, unit_price=24000, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory=default_inventory,
        inventory_item=inventory_item17, record_type='ADD', quantity_of_stock_on_display=7,
        quantity_recorded=15, unit_price=56000, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory=default_inventory,
        inventory_item=inventory_item18, record_type='ADD', quantity_of_stock_on_display=5,
        quantity_recorded=17, unit_price=29000, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory=default_inventory,
        inventory_item=inventory_item19, record_type='ADD', quantity_of_stock_on_display=3,
        quantity_recorded=5, unit_price=43500, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory=default_inventory,
        inventory_item=inventory_item20, record_type='ADD', quantity_of_stock_on_display=4,
        quantity_recorded=9, unit_price=25000, **audit_fields)

    section, _ = Section.objects.update_or_create(
        section_name='Section A', **audit_fields)

    catalog_item1, _ = CatalogItem.objects.update_or_create(
        section=section, inventory_item=inventory_item1, **audit_fields)
    catalog_item2, _ = CatalogItem.objects.update_or_create(
        section=section, inventory_item=inventory_item2, **audit_fields)
    catalog_item3, _ = CatalogItem.objects.update_or_create(
        section=section, inventory_item=inventory_item3, **audit_fields)
    catalog_item4, _ = CatalogItem.objects.update_or_create(
        section=section, inventory_item=inventory_item4, **audit_fields)
    catalog_item5, _ = CatalogItem.objects.update_or_create(
        section=section, inventory_item=inventory_item5, **audit_fields)
    catalog_item6, _ = CatalogItem.objects.update_or_create(
        section=section, inventory_item=inventory_item6, **audit_fields)
    catalog_item7, _ = CatalogItem.objects.update_or_create(
        section=section, inventory_item=inventory_item7, **audit_fields)
    catalog_item8, _ = CatalogItem.objects.update_or_create(
        section=section, inventory_item=inventory_item8, **audit_fields)
    catalog_item9, _ = CatalogItem.objects.update_or_create(
        section=section, inventory_item=inventory_item9, **audit_fields)
    catalog_item10, _ = CatalogItem.objects.update_or_create(
        section=section, inventory_item=inventory_item10, **audit_fields)

    catalog_item11, _ = CatalogItem.objects.update_or_create(
        section=section, inventory_item=inventory_item11, **audit_fields)
    catalog_item12, _ = CatalogItem.objects.update_or_create(
        section=section, inventory_item=inventory_item12, **audit_fields)
    catalog_item13, _ = CatalogItem.objects.update_or_create(
        section=section, inventory_item=inventory_item13, **audit_fields)
    catalog_item14, _ = CatalogItem.objects.update_or_create(
        section=section, inventory_item=inventory_item14, **audit_fields)
    catalog_item15, _ = CatalogItem.objects.update_or_create(
        section=section, inventory_item=inventory_item15, **audit_fields)
    catalog_item16, _ = CatalogItem.objects.update_or_create(
        section=section, inventory_item=inventory_item16, **audit_fields)
    catalog_item17, _ = CatalogItem.objects.update_or_create(
        section=section, inventory_item=inventory_item17, **audit_fields)
    catalog_item18, _ = CatalogItem.objects.update_or_create(
        section=section, inventory_item=inventory_item18, **audit_fields)
    catalog_item19, _ = CatalogItem.objects.update_or_create(
        section=section, inventory_item=inventory_item19, **audit_fields)
    catalog_item20, _ = CatalogItem.objects.update_or_create(
        section=section, inventory_item=inventory_item20, **audit_fields)

    CatalogCatalogItem.objects.update_or_create(
        catalog=standard_catalog, catalog_item=catalog_item1, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=standard_catalog, catalog_item=catalog_item2, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=standard_catalog, catalog_item=catalog_item3, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=standard_catalog, catalog_item=catalog_item4, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=standard_catalog, catalog_item=catalog_item5, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=standard_catalog, catalog_item=catalog_item6, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=standard_catalog, catalog_item=catalog_item7, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=standard_catalog, catalog_item=catalog_item8, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=standard_catalog, catalog_item=catalog_item9, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=standard_catalog, catalog_item=catalog_item10, **audit_fields)

    CatalogCatalogItem.objects.update_or_create(
        catalog=standard_catalog, catalog_item=catalog_item11, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=standard_catalog, catalog_item=catalog_item12, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=standard_catalog, catalog_item=catalog_item13, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=standard_catalog, catalog_item=catalog_item14, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=standard_catalog, catalog_item=catalog_item15, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=standard_catalog, catalog_item=catalog_item16, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=standard_catalog, catalog_item=catalog_item17, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=standard_catalog, catalog_item=catalog_item18, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=standard_catalog, catalog_item=catalog_item19, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=standard_catalog, catalog_item=catalog_item20, **audit_fields)

    default_customer, _ = Customer.objects.update_or_create(
        customer_number=87656, first_name='Jack', last_name='Reacher',
        other_names='Mbyad', enterprise_user=user, is_enterprise=True,
        phone_no='+25478765434', email='jackreacher@reacher.com', **audit_fields)
    customer, _ = Customer.objects.update_or_create(
        customer_number=9876, first_name='John', last_name='Wick', other_names='Baba Yaga',
        is_enterprise=False, phone_no='+254753746372', email='johnwick@parabellum.com',
        **audit_fields)

    enterprise_audit_fields = {
        'created_by': user.id,
        'updated_by': user.id
    }
    supplier1, _ = Enterprise.objects.update_or_create(
        name='LG DEALER', enterprise_type='SUPPLIER', **enterprise_audit_fields)
    supplier2, _ = Enterprise.objects.update_or_create(
        name='SAMSUNG DEALER', enterprise_type='SUPPLIER', **enterprise_audit_fields)
    supplier3, _ = Enterprise.objects.update_or_create(
        name='SONY DEALER', enterprise_type='SUPPLIER', **enterprise_audit_fields)
    supplier4, _ = Enterprise.objects.update_or_create(
        name='TECNO DEALER', enterprise_type='SUPPLIER', **enterprise_audit_fields)

    billing = [
        {
            'catalog_item': str(catalog_item1.id),
            'item_name': catalog_item1.inventory_item.item.item_name,
            'quantity': 2,
            'unit_price': 3500,
            'total': 7000,
            'deposit': None,
            'sale_type': 'INSTANT'
        },
        {
            'catalog_item': str(catalog_item2.id),
            'item_name': catalog_item2.inventory_item.item.item_name,
            'quantity': 3,
            'unit_price': 2500,
            'deposit': 3000,
            'total': 7500,
            'sale_type': 'INSTALLMENT'
        },
    ]
    payments = [
        {
            'means': 'CASH',
            'amount': 5000
        },
        {
            'means': 'MPESA TILL',
            'amount': 10000
        }
    ]

    encounter_payload = {
        'customer': customer,
        'billing': billing,
        'payments': payments,
        }

    process_customer_encounter.delay = mock.MagicMock()
    encounter = Encounter.objects.create(**encounter_payload, **audit_fields)
    process_customer_encounter(encounter.id)

    from random import randint

    order = Order.objects.first()
    sale = Sale.objects.create(sale_code=f'C-{randint(3000,9999)}', order=order, **audit_fields)
    saleitem1 = SaleItem.objects.create(
        sale=sale, catalog_item=catalog_item1, quantity_sold=4, **audit_fields)
    saleitem2 = SaleItem.objects.create(
        sale=sale, catalog_item=catalog_item2, quantity_sold=5, **audit_fields)
    saleitem3 = SaleItem.objects.create(
        sale=sale, catalog_item=catalog_item3, quantity_sold=6, **audit_fields)
    saleitem4 = SaleItem.objects.create(
        sale=sale, catalog_item=catalog_item4, quantity_sold=9, **audit_fields)
    saleitem5 = SaleItem.objects.create(
        sale=sale, catalog_item=catalog_item5, quantity_sold=3, **audit_fields)
    saleitem6 = SaleItem.objects.create(
        sale=sale, catalog_item=catalog_item6, quantity_sold=8, **audit_fields)
    saleitem7 = SaleItem.objects.create(
        sale=sale, catalog_item=catalog_item7, quantity_sold=6, **audit_fields)
