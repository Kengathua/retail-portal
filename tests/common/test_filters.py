import uuid
from rest_framework.test import APITestCase
from tests.utils import LoggedInMixin
from tests.utils.login_mixins import authenticate_test_user


from elites_retail_portal.enterprises.models import Enterprise
from elites_retail_portal.catalog.models import Section

from django.urls import reverse

from model_bakery import baker


class TestComboboxFilter(LoggedInMixin, APITestCase):
    """."""

    def setUp(self):
        """."""
        self.enterprise = baker.make(
            Enterprise, reg_no='BS-9049444', name='Enterprise One',
            enterprise_code='EAL-E/EO-MB/2301-01', business_type='SHOP')
        enterprise_code = self.enterprise.enterprise_code
        self.client = authenticate_test_user()

    url = reverse('v1:catalog:section-list')

    def test_multiselect(self):
        """."""
        uuids = [str(uuid.uuid4()) for _ in range(3)]
        multiselect_url = self.url + '?combobox={}'.format(*uuids)
        enterprise_code = self.enterprise.enterprise_code
        baker.make(Section, id=uuids[0], enterprise=enterprise_code)
        baker.make(Section, id=uuids[1], enterprise=enterprise_code)
        baker.make(Section, id=uuids[2], enterprise=enterprise_code)

        resp = self.client.get(multiselect_url)
        assert resp.status_code == 200
        assert len(resp.data['results']) == 3

    def test_combobox(self):
        """."""
        combo_url = self.url + "?combobox=cdd113cc-5157-44a5-988e-69f8855a7f47"
        enterprise_code = self.enterprise.enterprise_code
        baker.make(
            Section, id='cdd113cc-5157-44a5-988e-69f8855a7f47', enterprise=enterprise_code)
        resp = self.client.get(combo_url)
        assert resp.status_code == 200
        assert len(resp.data['results']) == 1

    def test_search(self):
        """."""
        search_url = self.url + "?search=Section A"
        enterprise_code = self.enterprise.enterprise_code
        baker.make(
            Section, section_name='Section A', enterprise=enterprise_code)
        baker.make(
            Section, section_name='Section B', enterprise=enterprise_code)
        baker.make(
            Section, section_name='Section C', enterprise=enterprise_code)
        resp = self.client.get(search_url)
        assert resp.status_code == 200
        assert len(resp.data['results']) == 1
