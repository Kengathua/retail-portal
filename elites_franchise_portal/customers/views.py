"""Customer Views file."""

from elites_franchise_portal.common.views import BaseViewMixin
from elites_franchise_portal.customers.models import Customer
from elites_franchise_portal.customers import serializers, filters


class CustomerViewSet(BaseViewMixin):
    """Customer Viewset class."""

    queryset = Customer.objects.all().order_by('first_name')
    serializer_class = serializers.CustomerSerializer
    filterset_class = filters.CustomerFilter
    search_fields = (
        'customer_number', 'account_number', 'first_name',
        'last_name', 'other_names', 'gender', 'id_no', 'phone_no', 'email')
