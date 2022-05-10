from elites_franchise_portal.franchises.models import Franchise
from tests.utils import APITests

from rest_framework.test import APITestCase

class TestFranchiseViewSet(APITests, APITestCase):
    url = 'v1:franchises:franchise'
    model = Franchise
