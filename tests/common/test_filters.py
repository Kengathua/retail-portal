import uuid
from rest_framework.test import APITestCase
from tests.utils import LoggedInMixin
from tests.utils.login_mixins import authenticate_test_user


from elites_franchise_portal.franchises.models import Franchise
from elites_franchise_portal.catalog.models import Section

from django.urls import reverse

from model_bakery import baker

class TestComboboxFilter(LoggedInMixin, APITestCase):
    def setUp(self):
        self.franchise = baker.make(
            Franchise, reg_no='BS-9049444', name='Franchise One', elites_code='EAL-F/FO-MB/2201-01',
            partnership_type='SHOP')
        franchise_code = self.franchise.elites_code
        self.client = authenticate_test_user()

    url = reverse('v1:catalog:section-list')

    def test_multiselect(self):
        uuids = [str(uuid.uuid4()) for _ in range(3)]
        multiselect_url = self.url + '?combobox={}'.format(*uuids)
        franchise_code = self.franchise.elites_code
        baker.make(Section, id=uuids[0], franchise=franchise_code)
        baker.make(Section, id=uuids[1], franchise=franchise_code)
        baker.make(Section, id=uuids[2], franchise=franchise_code)

        resp = self.client.get(multiselect_url)
        assert resp.status_code == 200
        assert len(resp.data) == 3


    def test_combobox(self):
        combo_url = self.url + "?combobox=cdd113cc-5157-44a5-988e-69f8855a7f47"
        franchise_code = self.franchise.elites_code
        baker.make(
            Section, id='cdd113cc-5157-44a5-988e-69f8855a7f47', franchise=franchise_code)
        resp = self.client.get(combo_url)
        assert resp.status_code == 200
        assert len(resp.data) == 1


    def test_search(self):
        search_url = self.url + "?search=Section A"
        franchise_code = self.franchise.elites_code
        baker.make(
            Section, section_name='Section A', franchise=franchise_code)
        baker.make(
            Section, section_name='Section B', franchise=franchise_code)
        baker.make(
            Section, section_name='Section C', franchise=franchise_code)
        resp = self.client.get(search_url)
        assert resp.status_code == 200
        assert len(resp.data) == 1
