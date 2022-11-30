from django.urls import reverse
from model_bakery import recipe
from rest_framework.test import APITestCase

from elites_retail_portal.enterprises.models import Enterprise
from elites_retail_portal.items.models import Category

from tests.utils.login_mixins import LoggedInMixin
from tests.utils.login_mixins import authenticate_test_user



class TestNonPartitionedMode(LoggedInMixin, APITestCase):
    """Use enterprises model since it has not enterprise field."""

    def setUp(self):
        """."""
        super().setUp()
        self.recipe = recipe.Recipe(Enterprise, enterprises_type='FRANCHISE')
        self.url = 'v1:enterprises:enterprise'

    def test_get(self, **kwargs):
        """."""
        # All should be returned
        self.client = authenticate_test_user()
        self.recipe.make(enterprises_type='SUPPLIER')
        self.recipe.make(enterprises_type='SUPPLIER')
        self.recipe.make(enterprises_type='SUPPLIER')
        assert Enterprise.objects.count() == 4

        url = reverse(self.url + '-list')
        resp = self.client.get(url)
        assert resp.status_code == 200
        assert len(resp.data['results']) == 4


class TestPartitionedModel(LoggedInMixin, APITestCase):
    """."""

    def setUp(self):
        """."""
        super().setUp()
        self.recipe = recipe.Recipe(Category, enterprise='EAL-E/EO-MB/2201-01')
        self.url = reverse('v1:items:category' + '-list')

    def test_get(self):
        """."""
        self.client = authenticate_test_user()
        c1 = self.recipe.make()
        c2 = self.recipe.make()
        self.recipe.make(enterprise=457)
        assert Category.objects.count() == 3
        resp = self.client.get(self.url)
        assert resp.status_code == 200
        assert len(resp.data['results']) == 2
        for r in resp.data['results']:
            assert r['id'] in [str(c1.id), str(c2.id)]

    def test_get_provider_bp(self):
        """."""
        self.client = authenticate_test_user()
        self.recipe.make()
        assert Category.objects.count() == 1
        bp = Enterprise.objects.get(enterprise_code='EAL-E/EO-MB/2201-01')
        bp.enterprises_type = 'PROVIDER'
        bp.save()
        self.user.refresh_from_db()
        resp = self.client.get(self.url)
        assert resp.status_code == 200
        assert len(resp.data['results']) == 0

    def test_unknown_user_bp(self):
        """."""
        self.client = authenticate_test_user()
        self.recipe.make(enterprise=2030)
        assert Category.objects.count() == 1
        self.user.enterprise = 2030
        self.user.save()
        resp = self.client.get(self.url)
        assert resp.status_code == 200
        assert len(resp.data['results']) == 0
    