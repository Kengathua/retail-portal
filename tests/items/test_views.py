import json
import pytest
from PIL import Image
import tempfile

from django.test import override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from rest_framework.test import APITestCase

from tests.utils.api import APITests
from elites_franchise_portal.items.models import (
    Brand, BrandItemType, Category, Item, ItemAttribute, ItemImage,
    ItemModel, ItemType, ItemUnits, Units)
from elites_franchise_portal.franchises.models import Franchise
from tests.utils.login_mixins import LoggedInMixin, authenticate_test_user

from model_bakery import baker
from model_bakery.recipe import Recipe, foreign_key

pytestmark = pytest.mark.django_db


class TestCategoryView(APITests, APITestCase):
    """."""

    def setUp(self):
        """."""
        franchise = baker.make(Franchise, name='Franchise One', partnership_type='SHOP')
        self.recipe = Recipe(
            Category, category_name='ELECTRONICS', franchise=franchise.elites_code)

    url = 'v1:items:category'


class TestItemTypeView(APITests, APITestCase):
    """."""

    def setUp(self):
        """."""
        franchise = baker.make(Franchise, name='Franchise One', partnership_type='SHOP')
        franchise_code = franchise.elites_code
        franchise_code = franchise.elites_code
        cat = baker.make(
            Category, category_name='Cat One',
            franchise=franchise_code)
        self.recipe = Recipe(
            ItemType, category=cat, type_name='Cooker',
            franchise=franchise_code)

    url = 'v1:items:itemtype'


class TestBrandView(APITests, APITestCase):
    """."""

    def setUp(self):
        """."""
        franchise = baker.make(Franchise, name='Franchise One', partnership_type='SHOP')
        franchise_code = franchise.elites_code
        franchise_code = franchise.elites_code
        self.recipe = Recipe(
            Brand, brand_name='Samsung', franchise=franchise_code)

    url = 'v1:items:brand'


class TestBrandItemTypeView(APITests, APITestCase):
    """."""

    def setUp(self):
        franchise = baker.make(Franchise, name='Franchise One', partnership_type='SHOP')
        franchise_code = franchise.elites_code
        cat = baker.make(
            Category, category_name='Cat One',
            franchise=franchise_code)
        item_type = baker.make(
            ItemType, category=cat, type_name='Cooker',
            franchise=franchise_code)
        brand = baker.make(
            Brand, brand_name='Samsung', franchise=franchise_code)
        self.recipe = Recipe(
            BrandItemType, brand=brand, item_type=item_type,
            franchise=franchise_code)

    url = 'v1:items:branditemtype'


class TestItemModelView(APITests, APITestCase):
    """."""

    def setUp(self):
        """."""
        franchise = baker.make(Franchise, name='Franchise One', partnership_type='SHOP')
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
        self.recipe = Recipe(
            ItemModel, brand=brand, item_type=item_type, model_name='GE731K-B SUT',
            franchise=franchise_code)

    url = 'v1:items:itemmodel'


class TestItemView(APITests, APITestCase):
    """."""

    def setUp(self):
        """."""
        franchise = baker.make(
            Franchise, name='Franchise One', partnership_type='SHOP')
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
        self.recipe = Recipe(
            Item, item_model=item_model, barcode='83838388383', make_year=2020,
            franchise=franchise_code)

    url = 'v1:items:item'

    def test_delete(self, status_code=204):
        pass


class TestItemAttributeView(APITests, APITestCase):
    """."""

    def setUp(self):
        """."""
        franchise = baker.make(
            Franchise, name='Franchise One', partnership_type='SHOP')
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
        self.recipe = Recipe(
            ItemAttribute, item=item, attribute_type='DESCRIPTION',
            attribute_value='Description', franchise=franchise_code)

    url = 'v1:items:itemattribute'


class TestUnitsView(APITests, APITestCase):
    """."""

    def setUp(self):
        """."""
        franchise = baker.make(
            Franchise, name='Franchise One', partnership_type='SHOP')
        franchise_code = franchise.elites_code
        self.recipe = Recipe(Units, units_name='5 Gas', franchise=franchise_code)

    url = 'v1:items:units'


class TestItemUnitsView(APITests, APITestCase):
    """."""

    def setUp(self):
        """."""
        franchise = baker.make(
            Franchise, name='Franchise One', partnership_type='SHOP')
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
        sales_units_recipe = baker.make(
            Units, units_name='230 L', franchise=franchise_code)
        purchases_units_recipe = baker.make(
            Units, units_name='230 L', franchise=franchise_code)
        self.recipe = Recipe(
            ItemUnits, item=item, sales_units=sales_units_recipe,
            purchases_units=purchases_units_recipe, items_per_purchase_unit=1,
            franchise=franchise_code)

    url = 'v1:items:itemunits'


def temporary_image():
    """."""
    from io import BytesIO
    bts = BytesIO()
    img = Image.new("RGB", (100, 100))
    img.save(bts, 'jpeg')
    return SimpleUploadedFile("test.jpg", bts.getvalue())


class TestItemImages(APITests, APITestCase, LoggedInMixin):
    """."""

    def setUp(self):
        """."""
        franchise = baker.make(
            Franchise, name='Franchise One', partnership_type='SHOP')
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
        test_image = temporary_image()
        self.recipe = Recipe(
            ItemImage, item=item, image=test_image,
            is_hero_image=True, franchise=franchise_code)

    url = 'v1:items:itemimage'

    def test_put(self, status_code=200):
        """."""
        pass
        # return super().test_put(status_code)

    def test_patch(self, status_code=200):
        """."""
        # return super().test_patch(status_code)
        self.client = authenticate_test_user()
        instance = self.make()
        test_data = self.patch_data()
        test_id = getattr(instance, self.id_field)
        assert test_id, test_id
        assert instance.__class__.objects.get(pk=test_id), \
            'unable to get instance with PK {}'.format(test_id)

        url = reverse(
            self.url + '-patch-uploaded-image', kwargs={self.id_field: test_id}
        )
        # resp = self.client.patch(url, test_data)
        pass

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_post(self, status_code=201):
        """."""
        self.client = authenticate_test_user()
        test_post_data = self.post_data()
        url = reverse(self.url + '-upload-image')
        resp = self.client.post(url, test_post_data)
        assert resp.status_code == status_code, '{}, {}, {}'.format(resp.content, url, test_post_data)
        if resp.status_code != 201:
            return resp

        # disparity due to image location path
        # self.compare_dicts(test_post_data, resp.data)

        return test_post_data, resp

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_post_bulk(self, status_code=201):
        """."""
        # self.client = authenticate_test_user()
        test_post_data1 = self.post_data()
        test_post_data2 = self.post_data()
        url = reverse(self.url + '-bulk-upload-images')
        test_post_list = [test_post_data1, test_post_data2]
        # resp = self.client.post(url, test_post_list)
        pass
