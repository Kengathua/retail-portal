import uuid
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from elites_franchise_portal.customers.models import Customer
from elites_franchise_portal.franchises.models import Franchise
from elites_franchise_portal.items.models import (
    Category, ItemType, Brand, BrandItemType, ItemModel, Item)
from elites_franchise_portal.debit.models import (
    InventoryItem, InventoryRecord)
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

    cate, _ = Category.objects.update_or_create(
        category_name='ELECTRONICS', **audit_fields)
    item_type, _ = ItemType.objects.update_or_create(
        category=cate, type_name='TV', **audit_fields)
    brand1, _ = Brand.objects.update_or_create(
        brand_name='Samsung', **audit_fields)
    brand_item_type1, _ = BrandItemType.objects.update_or_create(
        brand=brand1, item_type=item_type, **audit_fields)

    brand2, _ = Brand.objects.update_or_create(
        brand_name='LG', **audit_fields)
    brand_item_type2, _ = BrandItemType.objects.update_or_create(
        brand=brand2, item_type=item_type, **audit_fields)

    item_model1, _ = ItemModel.objects.update_or_create(
        brand_item_type=brand_item_type1, model_name='BGDTDDR677', **audit_fields)
    item_model2, _ = ItemModel.objects.update_or_create(
        brand_item_type=brand_item_type1, model_name='IUYTFGD678', **audit_fields)
    item_model3, _ = ItemModel.objects.update_or_create(
        brand_item_type=brand_item_type1, model_name='HGFDTYU679', **audit_fields)
    item_model4, _ = ItemModel.objects.update_or_create(
        brand_item_type=brand_item_type1, model_name='UYTRFGH680', **audit_fields)
    item_model5, _ = ItemModel.objects.update_or_create(
        brand_item_type=brand_item_type1, model_name='NBVCVBN681', **audit_fields)
    item_model6, _ = ItemModel.objects.update_or_create(
        brand_item_type=brand_item_type1, model_name='GGRFGBNM674', **audit_fields)
    item_model7, _ = ItemModel.objects.update_or_create(
        brand_item_type=brand_item_type1, model_name='FTFGHNJM676', **audit_fields)
    item_model8, _ = ItemModel.objects.update_or_create(
        brand_item_type=brand_item_type1, model_name='NBVCDFGH675', **audit_fields)
    item_model9, _ = ItemModel.objects.update_or_create(
        brand_item_type=brand_item_type1, model_name='ETRHMNVE673', **audit_fields)
    item_model10, _ = ItemModel.objects.update_or_create(
        brand_item_type=brand_item_type1, model_name='NFVDFGHJ672', **audit_fields)

    item_model11, _ = ItemModel.objects.update_or_create(
        brand_item_type=brand_item_type2, model_name='HMMDNHE677', **audit_fields)
    item_model12, _ = ItemModel.objects.update_or_create(
        brand_item_type=brand_item_type2, model_name='KJDJDYE678', **audit_fields)
    item_model13, _ = ItemModel.objects.update_or_create(
        brand_item_type=brand_item_type2, model_name='MNBFGHJK679', **audit_fields)
    item_model14, _ = ItemModel.objects.update_or_create(
        brand_item_type=brand_item_type2, model_name='VBGFYNBB680', **audit_fields)
    item_model15, _ = ItemModel.objects.update_or_create(
        brand_item_type=brand_item_type2, model_name='JHGFRTYU681', **audit_fields)
    item_model16, _ = ItemModel.objects.update_or_create(
        brand_item_type=brand_item_type2, model_name='KJHRTYUB674', **audit_fields)
    item_model17, _ = ItemModel.objects.update_or_create(
        brand_item_type=brand_item_type2, model_name='MNBVDFGE676', **audit_fields)
    item_model18, _ = ItemModel.objects.update_or_create(
        brand_item_type=brand_item_type2, model_name='RFGNMNBV675', **audit_fields)
    item_model19, _ = ItemModel.objects.update_or_create(
        brand_item_type=brand_item_type2, model_name='IUYGTFGH673', **audit_fields)
    item_model20, _ = ItemModel.objects.update_or_create(
        brand_item_type=brand_item_type2, model_name='EFHYEHEG672', **audit_fields)

    item1, _ = Item.objects.update_or_create(
        item_model=item_model1, barcode=12345678,
        make_year=2021, create_inventory_item=False, **audit_fields)
    item2, _ = Item.objects.update_or_create(
        item_model=item_model2, barcode=765433346,
        make_year=2021, create_inventory_item=False, **audit_fields)
    item3, _ = Item.objects.update_or_create(
        item_model=item_model3, barcode=6655443456,
        make_year=2021, create_inventory_item=False, **audit_fields)
    item4, _ = Item.objects.update_or_create(
        item_model=item_model4, barcode=9988776546,
        make_year=2021, create_inventory_item=False, **audit_fields)
    item5, _ = Item.objects.update_or_create(
        item_model=item_model5, barcode=4556483833,
        make_year=2021, create_inventory_item=False, **audit_fields)
    item6, _ = Item.objects.update_or_create(
        item_model=item_model6, barcode=88363636373,
        make_year=2021, create_inventory_item=False, **audit_fields)
    item7, _ = Item.objects.update_or_create(
        item_model=item_model7, barcode=83764545622,
        make_year=2021, create_inventory_item=False, **audit_fields)
    item8, _ = Item.objects.update_or_create(
        item_model=item_model8, barcode=988474747646,
        make_year=2021, create_inventory_item=False, **audit_fields)
    item9, _ = Item.objects.update_or_create(
        item_model=item_model9, barcode=77376353533,
        make_year=2021, create_inventory_item=False, **audit_fields)
    item10, _ = Item.objects.update_or_create(
        item_model=item_model10, barcode=9837365534,
        make_year=2021, create_inventory_item=False, **audit_fields)

    item11, _ = Item.objects.update_or_create(
        item_model=item_model11, barcode=92828373664,
        make_year=2021, create_inventory_item=False, **audit_fields)
    item12, _ = Item.objects.update_or_create(
        item_model=item_model12, barcode=948474645333,
        make_year=2021, create_inventory_item=False, **audit_fields)
    item13, _ = Item.objects.update_or_create(
        item_model=item_model13, barcode=938736363533,
        make_year=2021, create_inventory_item=False, **audit_fields)
    item14, _ = Item.objects.update_or_create(
        item_model=item_model14, barcode=847474646444,
        make_year=2021, create_inventory_item=False, **audit_fields)
    item15, _ = Item.objects.update_or_create(
        item_model=item_model15, barcode=948474746464,
        make_year=2021, create_inventory_item=False, **audit_fields)
    item16, _ = Item.objects.update_or_create(
        item_model=item_model16, barcode=4747464646484,
        make_year=2021, create_inventory_item=False, **audit_fields)
    item17, _ = Item.objects.update_or_create(
        item_model=item_model17, barcode=84847494039373,
        make_year=2021, create_inventory_item=False, **audit_fields)
    item18, _ = Item.objects.update_or_create(
        item_model=item_model18, barcode=8746453537494,
        make_year=2021, create_inventory_item=False, **audit_fields)
    item19, _ = Item.objects.update_or_create(
        item_model=item_model19, barcode=8373635484998,
        make_year=2021, create_inventory_item=False, **audit_fields)
    item20, _ = Item.objects.update_or_create(
        item_model=item_model20, barcode=73736363636353,
        make_year=2021, create_inventory_item=False, **audit_fields)


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

    InventoryRecord.objects.update_or_create(
        inventory_item=inventory_item1, record_type='ADD', quantity_of_stock_on_display=7,
        quantity_recorded=15, unit_price=3000, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory_item=inventory_item2, record_type='ADD', quantity_of_stock_on_display=4,
        quantity_recorded=14, unit_price=3000, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory_item=inventory_item3, record_type='ADD', quantity_of_stock_on_display=3,
        quantity_recorded=10, unit_price=3000, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory_item=inventory_item4, record_type='ADD', quantity_of_stock_on_display=14,
        quantity_recorded=25, unit_price=3000, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory_item=inventory_item5, record_type='ADD', quantity_of_stock_on_display=26,
        quantity_recorded=45, unit_price=3000, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory_item=inventory_item6, record_type='ADD', quantity_of_stock_on_display=17,
        quantity_recorded=35, unit_price=3000, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory_item=inventory_item7, record_type='ADD', quantity_of_stock_on_display=7,
        quantity_recorded=17, unit_price=3000, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory_item=inventory_item8, record_type='ADD', quantity_of_stock_on_display=5,
        quantity_recorded=13, unit_price=3000, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory_item=inventory_item9, record_type='ADD', quantity_of_stock_on_display=3,
        quantity_recorded=9, unit_price=3000, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory_item=inventory_item10, record_type='ADD', quantity_of_stock_on_display=6,
        quantity_recorded=8, unit_price=3000, **audit_fields)

    InventoryRecord.objects.update_or_create(
        inventory_item=inventory_item11, record_type='ADD', quantity_of_stock_on_display=3,
        quantity_recorded=6, unit_price=3000, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory_item=inventory_item12, record_type='ADD', quantity_of_stock_on_display=4,
        quantity_recorded=12, unit_price=3000, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory_item=inventory_item13, record_type='ADD', quantity_of_stock_on_display=7,
        quantity_recorded=16, unit_price=3000, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory_item=inventory_item14, record_type='ADD', quantity_of_stock_on_display=6,
        quantity_recorded=11, unit_price=3000, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory_item=inventory_item15, record_type='ADD', quantity_of_stock_on_display=13,
        quantity_recorded=18, unit_price=3000, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory_item=inventory_item16, record_type='ADD', quantity_of_stock_on_display=4,
        quantity_recorded=13, unit_price=3000, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory_item=inventory_item17, record_type='ADD', quantity_of_stock_on_display=7,
        quantity_recorded=15, unit_price=3000, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory_item=inventory_item18, record_type='ADD', quantity_of_stock_on_display=5,
        quantity_recorded=17, unit_price=3000, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory_item=inventory_item19, record_type='ADD', quantity_of_stock_on_display=3,
        quantity_recorded=5, unit_price=3000, **audit_fields)
    InventoryRecord.objects.update_or_create(
        inventory_item=inventory_item20, record_type='ADD', quantity_of_stock_on_display=4,
        quantity_recorded=9, unit_price=3000, **audit_fields)


    section, _ = Section.objects.update_or_create(
        section_name='Section A', **audit_fields)
    catalog, _ = Catalog.objects.update_or_create(
        name='Elites Age Standard Catalog',
        is_standard_catalog=True, **audit_fields)

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
        catalog=catalog, catalog_item=catalog_item1, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=catalog, catalog_item=catalog_item2, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=catalog, catalog_item=catalog_item3, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=catalog, catalog_item=catalog_item4, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=catalog, catalog_item=catalog_item5, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=catalog, catalog_item=catalog_item6, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=catalog, catalog_item=catalog_item7, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=catalog, catalog_item=catalog_item8, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=catalog, catalog_item=catalog_item9, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=catalog, catalog_item=catalog_item10, **audit_fields)

    CatalogCatalogItem.objects.update_or_create(
        catalog=catalog, catalog_item=catalog_item11, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=catalog, catalog_item=catalog_item12, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=catalog, catalog_item=catalog_item13, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=catalog, catalog_item=catalog_item14, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=catalog, catalog_item=catalog_item15, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=catalog, catalog_item=catalog_item16, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=catalog, catalog_item=catalog_item17, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=catalog, catalog_item=catalog_item18, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=catalog, catalog_item=catalog_item19, **audit_fields)
    CatalogCatalogItem.objects.update_or_create(
        catalog=catalog, catalog_item=catalog_item20, **audit_fields)

    default_customer, _ = Customer.objects.update_or_create(
        customer_number=87656, first_name='Jack', last_name='Reacher',
        other_names='Mbyad', franchise_user=user, is_franchise=True,
        phone_no='+25478765434', email='jackreacher@reacher.com', **audit_fields)
    customer, _ = Customer.objects.update_or_create(
        customer_number=9876, first_name='John', last_name='Wick', other_names='Baba Yaga',
        is_franchise=False, phone_no='+254753746372', email='johnwick@parabellum.com',
        **audit_fields)
    sale, _ = Sale.objects.update_or_create(customer=customer, **audit_fields)
