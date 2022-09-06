"""."""

from elites_franchise_portal.enterprises.models import Enterprise
from tests.utils import APITests

from rest_framework.test import APITestCase


class TestEnterpriseViewSet(APITests, APITestCase):
    """."""

    url = 'v1:enterprises:enterprise'
    model = Enterprise
