from django.test import TestCase
from elites_franchise_portal.debit.models.inventory import (
    Inventory, InventoryItem, InventoryInventoryItem)

from elites_franchise_portal.franchises.models import Franchise
from elites_franchise_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemAttribute, ItemImage,
    ItemModel, ItemType, ItemUnits, UnitsItemType, Units)

from model_bakery import baker
from model_bakery.recipe import Recipe


class TestCategory(TestCase):
    """."""

    def test_create_category(self):
        """."""
        franchise = baker.make(Franchise, name='Franchise Number One')
        cat = baker.make(
            Category, category_name='Cat One',
            franchise=franchise.elites_code)
        assert cat
        assert cat.category_code == 'FNO-MB/C-CO/2201'
        assert Category.objects.count() == 1


class TestItemType(TestCase):
    """."""

    def test_create_item_type(self):
        """."""
        franchise = baker.make(Franchise, name='Elites Age Supermarket')
        cat = baker.make(
            Category, category_name='Cat One',
            franchise=franchise.elites_code)
        item_type = baker.make(
            ItemType, category=cat, type_name='Cooker',
            franchise=franchise.elites_code)

        assert item_type
        assert item_type.type_code == 'EAS-MB/T-C/2201'
        assert ItemType.objects.count() == 1


class TestBrand(TestCase):
    """."""

    def test_create_brand(self):
        """."""
        franchise = baker.make(Franchise, name='Elites Age Supermarket')
        brand = baker.make(
            Brand, brand_name='Samsung', franchise=franchise.elites_code)

        assert brand
        assert brand.brand_code == 'EAS-MB/B-S/2201'
        assert Brand.objects.count() == 1


class TestBrandItemType(TestCase):
    """."""

    def test_create_brand_item_type(self):
        """."""
        franchise = baker.make(Franchise, name='Elites Age Supermarket')
        cat = baker.make(
            Category, category_name='Cat One',
            franchise=franchise.elites_code)
        item_type1 = baker.make(
            ItemType, category=cat, type_name='Cooker',
            franchise=franchise.elites_code)
        item_type2 = baker.make(
            ItemType, category=cat, type_name='Microwave',
            franchise=franchise.elites_code)
        brand = baker.make(
            Brand, brand_name='Samsung', franchise=franchise.elites_code)
        brand_item = baker.make(
            BrandItemType, brand=brand, item_type=item_type1,
            franchise=franchise.elites_code)
        brand_item = baker.make(
            BrandItemType, brand=brand, item_type=item_type2,
            franchise=franchise.elites_code)
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
        franchise = baker.make(Franchise, name='Elites Age Supermarket')
        franchise_code = franchise.elites_code
        cat = baker.make(
            Category, category_name='Cat One',
            franchise=franchise_code)
        item_type = baker.make(
            ItemType, category=cat, type_name='Cooker',
            franchise=franchise_code)
        brand = baker.make(
            Brand, brand_name='Samsung', franchise=franchise_code)
        baker.make(
            BrandItemType, brand=brand, item_type=item_type,
            franchise=franchise_code)
        model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            franchise=franchise_code)

        assert model
        assert model.model_code == 'EAS-MB/M-GS/2201'
        assert ItemModel.objects.count() == 1


class TestItem(TestCase):
    """."""

    def test_create_item(self):
        """."""
        franchise = baker.make(Franchise, name='Elites Age Supermarket')
        franchise_code = franchise.elites_code
        cat = baker.make(
            Category, category_name='Cat One',
            franchise=franchise_code)
        item_type = baker.make(
            ItemType, category=cat, type_name='Cooker',
            franchise=franchise_code)
        brand = baker.make(
            Brand, brand_name='Samsung', franchise=franchise_code)
        baker.make(
            BrandItemType, brand=brand, item_type=item_type,
            franchise=franchise_code)
        item_model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            franchise=franchise_code)
        inventory = baker.make(
            Inventory, inventory_name='Elites Age Supermarket Working Stock Inventory',
            inventory_type='WORKING STOCK', is_master=True, is_active=True, franchise=franchise_code)

        item = baker.make(Item, item_model=item_model, barcode='83838388383', make_year=2020, franchise=franchise_code)

        assert item
        assert item.item_name == 'Samsung GE731K-B SUT Cooker'
        assert item.item_code == 'EAS-MB/I-SGSC/2201'
        assert Item.objects.count() == 1

        inventory_inventory_item = InventoryInventoryItem.objects.get(
            inventory=inventory, inventory__is_master=True, inventory__is_active=True)
        assert inventory_inventory_item.inventory_item.item == item
        assert inventory.inventory_items.filter(item=item)


class TestItemAttribute(TestCase):
    """."""

    def test_create_item(self):
        """."""
        franchise = baker.make(Franchise, name='Elites Age Supermarket')
        franchise_code = franchise.elites_code
        cat = baker.make(
            Category, category_name='Cat One',
            franchise=franchise_code)
        item_type = baker.make(
            ItemType, category=cat, type_name='Cooker',
            franchise=franchise_code)
        brand = baker.make(
            Brand, brand_name='Samsung', franchise=franchise_code)
        baker.make(
            BrandItemType, brand=brand, item_type=item_type,
            franchise=franchise_code)
        item_model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            franchise=franchise_code)
        item = baker.make(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
            franchise=franchise_code)
        item_attrs1 = baker.make(
            ItemAttribute, item=item, attribute_type='SPECIAL OFFER',
            attribute_value='Special Offer One', franchise=franchise_code)
        item_attrs2 = baker.make(
            ItemAttribute, item=item, attribute_type='SPECIAL FEATURE',
            attribute_value='Special Feature One', franchise=franchise_code)
        item_attrs3 = baker.make(
            ItemAttribute, item=item, attribute_type='SPECIFICATION',
            attribute_value='Specification One', franchise=franchise_code)
        item_attrs4 = baker.make(
            ItemAttribute, item=item, attribute_type='DESCRIPTION',
            attribute_value='Description', franchise=franchise_code)

        assert ItemAttribute.objects.count() == 4
        assert item_attrs1.special_offers == ['Special Offer One']
        assert item_attrs2.special_features == ['Special Feature One']
        assert item_attrs3.specifications == ['Specification One']
        assert item_attrs4.description == ['Description']


class TestUnits(TestCase):
    """."""

    def test_create_units(self):
        """."""
        franchise = baker.make(Franchise, name='Elites Age Supermarket')
        franchise_code = franchise.elites_code
        cat = baker.make(
            Category, category_name='Cat One',
            franchise=franchise_code)
        item_type = baker.make(
            ItemType, category=cat, type_name='Cooker',
            franchise=franchise_code)
        units = baker.make(Units, units_name='5 Gas', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=units, franchise=franchise_code)
        units.item_types.set([item_type])
        units.save()

        assert units
        assert units.units_code == 'EAS-MB/U-5G/2201'
        assert Units.objects.count() == 1


class TestItemUnits(TestCase):
    """."""

    def test_create_item_units(self):
        """."""
        franchise = baker.make(Franchise, name='Elites Age Supermarket')
        franchise_code = franchise.elites_code
        cat = baker.make(
            Category, category_name='Cat One',
            franchise=franchise_code)
        item_type = baker.make(
            ItemType, category=cat, type_name='Cooker',
            franchise=franchise_code)
        brand = baker.make(
            Brand, brand_name='Samsung', franchise=franchise_code)
        baker.make(
            BrandItemType, brand=brand, item_type=item_type,
            franchise=franchise_code)
        item_model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            franchise=franchise_code)
        item = baker.make(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
            franchise=franchise_code)
        s_units = baker.make(Units, units_name='5 Gas', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=s_units, franchise=franchise_code)
        s_units.item_types.set([item_type])
        s_units.save()
        p_units = baker.make(Units, units_name='5 Gas', franchise=franchise_code)
        baker.make(UnitsItemType, item_type=item_type, units=p_units, franchise=franchise_code)
        p_units.item_types.set([item_type])
        p_units.save()
        item_units = baker.make(
            ItemUnits, item=item, sales_units=s_units, purchases_units=p_units,
            items_per_purchase_unit=1, franchise=franchise_code)

        assert item_units
        assert ItemUnits.objects.count() == 1


class TestItemImage(TestCase):
    """."""

    def test_create_item_image(self):
        """."""
        franchise = baker.make(Franchise, name='Elites Age Supermarket')
        franchise_code = franchise.elites_code
        cat = baker.make(
            Category, category_name='Cat One',
            franchise=franchise_code)
        item_type = baker.make(
            ItemType, category=cat, type_name='Cooker',
            franchise=franchise_code)
        brand = baker.make(
            Brand, brand_name='Samsung', franchise=franchise_code)
        baker.make(
            BrandItemType, brand=brand, item_type=item_type,
            franchise=franchise_code)
        item_model = baker.make(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            franchise=franchise_code)
        item = baker.make(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
            franchise=franchise_code)
        item_image = baker.make(
            ItemImage, item=item, image='file.png', is_hero_image=True,
            franchise=franchise_code)
        assert item_image
        assert ItemImage.objects.count() == 1
