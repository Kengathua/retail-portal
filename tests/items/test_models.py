"""."""

import uuid
import pytest
from django.test import TestCase
from elites_franchise_portal.debit.models import (
    Inventory, InventoryItem, InventoryInventoryItem)
from elites_franchise_portal.warehouses.models import Warehouse
from elites_franchise_portal.catalog.models import Catalog
from elites_franchise_portal.users.models import User
from elites_franchise_portal.enterprises.models import Enterprise
from elites_franchise_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemAttribute, ItemImage,
    ItemModel, ItemType, ItemUnits, UnitsItemType, Units)
from django.core.exceptions import ValidationError
from elites_franchise_portal.enterprise_mgt.models import EnterpriseSetupRules

from model_bakery import baker
from model_bakery.recipe import Recipe


class TestCategory(TestCase):
    """."""

    def test_create_category(self):
        """."""
        enterprise = baker.make(Enterprise, name='Franchise Number One')
        cat = baker.make(
            Category, category_name='Cat One',
            enterprise=enterprise.enterprise_code)
        assert cat
        assert cat.category_code == 'FNO-MB/C-CO/2201'
        assert Category.objects.count() == 1


class TestItemType(TestCase):
    """."""

    def test_create_item_type(self):
        """."""
        enterprise = baker.make(Enterprise, name='Elites Age Supermarket')
        cat = baker.make(
            Category, category_name='Cat One',
            enterprise=enterprise.enterprise_code)
        item_type = baker.make(
            ItemType, category=cat, type_name='Cooker',
            enterprise=enterprise.enterprise_code)

        assert item_type
        assert item_type.type_code == 'EAS-MB/T-C/2201'
        assert ItemType.objects.count() == 1


class TestBrand(TestCase):
    """."""

    def test_create_brand(self):
        """."""
        enterprise = baker.make(Enterprise, name='Elites Age Supermarket')
        brand = baker.make(
            Brand, brand_name='Samsung', enterprise=enterprise.enterprise_code)

        assert brand
        assert brand.brand_code == 'EAS-MB/B-S/2201'
        assert Brand.objects.count() == 1


class TestBrandItemType(TestCase):
    """."""

    def test_create_brand_item_type(self):
        """."""
        enterprise = baker.make(Enterprise, name='Elites Age Supermarket')
        cat = baker.make(
            Category, category_name='Cat One',
            enterprise=enterprise.enterprise_code)
        item_type1 = baker.make(
            ItemType, category=cat, type_name='Cooker',
            enterprise=enterprise.enterprise_code)
        item_type2 = baker.make(
            ItemType, category=cat, type_name='Microwave',
            enterprise=enterprise.enterprise_code)
        brand = baker.make(
            Brand, brand_name='Samsung', enterprise=enterprise.enterprise_code)
        brand_item = baker.make(
            BrandItemType, brand=brand, item_type=item_type1,
            enterprise=enterprise.enterprise_code)
        brand_item = baker.make(
            BrandItemType, brand=brand, item_type=item_type2,
            enterprise=enterprise.enterprise_code)
        assert brand_item
        assert set(
            [item_type for item_type in brand.item_types.all()]).issuperset(set(
                [item_type1, item_type2]))
        assert set(
            [item_type for item_type in brand.item_types.all()]) == set([item_type1, item_type2])


class TestItemModel(TestCase):
    """."""

    def test_create_item_model(self):
        """."""
        enterprise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = enterprise.enterprise_code
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
        model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            enterprise=enterprise_code)

        assert model
        assert model.model_code == 'EAS-MB/M-GS/2201'
        assert ItemModel.objects.count() == 1


class TestItem(TestCase):
    """."""

    def test_create_item(self):
        """."""
        enterprise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = enterprise.enterprise_code
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

        assert item
        assert item.item_name == 'SAMSUNG GE731K-B SUT COOKER'
        assert item.item_code == 'EAS-MB/I-SGSC/2201'
        assert Item.objects.count() == 1

    def test_activate_item(self):
        """."""
        enterprise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = enterprise.enterprise_code
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
        assert not item.is_active

        user = baker.make(
            User, email='testuser@email.com', first_name='Test', last_name='User',
            guid=uuid.uuid4(), enterprise=enterprise_code)
        master_inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Working Stock Inventory',
            is_master=True, is_active=True, inventory_type='WORKING STOCK',
            enterprise=enterprise_code)
        default_inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Available Inventory',
            is_active=True, inventory_type='AVAILABLE', enterprise=enterprise_code)
        standard_catalog = baker.make(
            Catalog, catalog_name='Elites Age Supermarket Standard Catalog',
            description='Standard Catalog', is_standard=True, enterprise=enterprise_code)
        receiving_warehouse = baker.make(
            Warehouse, warehouse_name='Elites Private Warehouse', is_default=True,
            enterprise=enterprise_code)
        enterprise_setup_rules = baker.make(
            EnterpriseSetupRules, master_inventory=master_inventory,
            default_inventory=default_inventory, receiving_warehouse=receiving_warehouse,
            default_warehouse=receiving_warehouse, standard_catalog=standard_catalog,
            default_catalog=standard_catalog, is_active=True, enterprise=enterprise_code)
        with pytest.raises(ValidationError) as ve:
            item.activate(user)
        msg = 'SAMSUNG GE731K-B SUT COOKER does not have Units assigned to it. '\
            'Please hook that up first'
        assert msg in ve.value.messages

        s_units = baker.make(Units, units_name='5 Gas', enterprise=enterprise_code)
        baker.make(UnitsItemType, item_type=item_type, units=s_units, enterprise=enterprise_code)
        s_units.item_types.set([item_type])
        s_units.save()
        p_units = baker.make(Units, units_name='5 Gas', enterprise=enterprise_code)
        baker.make(UnitsItemType, item_type=item_type, units=p_units, enterprise=enterprise_code)
        p_units.item_types.set([item_type])
        p_units.save()
        baker.make(
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
            quantity_of_sale_units_per_purchase_unit=1, enterprise=enterprise_code)

        item.activate(user)
        item.refresh_from_db()

        assert item.is_active
        assert enterprise_setup_rules
        assert Inventory.objects.count() == 2
        assert InventoryItem.objects.count() == 1
        assert InventoryInventoryItem.objects.count() == 2


class TestItemAttribute(TestCase):
    """."""

    def test_create_item(self):
        """."""
        enterprise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = enterprise.enterprise_code
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
        item_attrs1 = baker.make(
            ItemAttribute, item=item, attribute_type='SPECIAL OFFER',
            attribute_value='Special Offer One', enterprise=enterprise_code)
        item_attrs2 = baker.make(
            ItemAttribute, item=item, attribute_type='SPECIAL FEATURE',
            attribute_value='Special Feature One', enterprise=enterprise_code)
        item_attrs3 = baker.make(
            ItemAttribute, item=item, attribute_type='SPECIFICATION',
            attribute_value='Specification One', enterprise=enterprise_code)
        item_attrs4 = baker.make(
            ItemAttribute, item=item, attribute_type='DESCRIPTION',
            attribute_value='Description', enterprise=enterprise_code)

        assert ItemAttribute.objects.count() == 4
        assert item_attrs1.special_offers == ['Special Offer One']
        assert item_attrs2.special_features == ['Special Feature One']
        assert item_attrs3.specifications == ['Specification One']
        assert item_attrs4.description == ['Description']


class TestUnits(TestCase):
    """."""

    def test_create_units(self):
        """."""
        enterprise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = enterprise.enterprise_code
        cat = baker.make(
            Category, category_name='Cat One',
            enterprise=enterprise_code)
        item_type = baker.make(
            ItemType, category=cat, type_name='Cooker',
            enterprise=enterprise_code)
        units = baker.make(Units, units_name='5 Gas', enterprise=enterprise_code)
        baker.make(UnitsItemType, item_type=item_type, units=units, enterprise=enterprise_code)
        units.item_types.set([item_type])
        units.save()

        assert units
        assert units.units_code == 'EAS-MB/U-5G/2201'
        assert Units.objects.count() == 1


class TestItemUnits(TestCase):
    """."""

    def test_create_item_units(self):
        """."""
        enterprise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = enterprise.enterprise_code
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
        s_units = baker.make(Units, units_name='5 Gas', enterprise=enterprise_code)
        baker.make(UnitsItemType, item_type=item_type, units=s_units, enterprise=enterprise_code)
        s_units.item_types.set([item_type])
        s_units.save()
        p_units = baker.make(Units, units_name='5 Gas', enterprise=enterprise_code)
        baker.make(UnitsItemType, item_type=item_type, units=p_units, enterprise=enterprise_code)
        p_units.item_types.set([item_type])
        p_units.save()
        item_units1 = baker.make(
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
            quantity_of_sale_units_per_purchase_unit=1, enterprise=enterprise_code)
        assert item_units1
        assert ItemUnits.objects.count() == 1
    
        item_units2 = Recipe(
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
            quantity_of_sale_units_per_purchase_unit=1, enterprise=enterprise_code)

        with pytest.raises(ValidationError) as ve:
            item_units2.make()
        msg = 'This item already has an active units instance registered to it. '\
            'Kindly deactivate the existing units registered to it or select a different item'
        assert msg in ve.value.messages

        item_units1.is_active = False
        item_units1.save()
        s_units.is_active = False
        s_units.save()
        with pytest.raises(ValidationError) as ve:
            item_units2.make()
        msg = 'Sales Units 5 Gas has been deactivated. '\
            'Kindly activate it or select the correct units to register'
        assert msg in ve.value.messages
        s_units.is_active = True
        s_units.save()
        p_units.is_active = False
        p_units.save()
        with pytest.raises(ValidationError) as ve:
            item_units2.make()
        msg = 'Purchases Units 5 Gas has been deactivated. '\
            'Kindly activate it or select the correct units to register'
        assert msg in ve.value.messages


class TestItemImage(TestCase):
    """."""

    def test_create_item_image(self):
        """."""
        enterprise = baker.make(Enterprise, name='Elites Age Supermarket')
        enterprise_code = enterprise.enterprise_code
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
        item_image = baker.make(
            ItemImage, item=item, image='file.png', is_hero_image=True,
            enterprise=enterprise_code)
        assert item_image
        assert ItemImage.objects.count() == 1
