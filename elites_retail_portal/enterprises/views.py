"""Enterprise views."""

from elites_retail_portal.common.views import BaseViewMixin
from elites_retail_portal.enterprises.models import Enterprise, Staff
from elites_retail_portal.enterprises import serializers
from elites_retail_portal.enterprises import filters


class EnterpriseViewSet(BaseViewMixin):
    """Enterprise ViewSet."""

    queryset = Enterprise.objects.all()
    serializer_class = serializers.EnterpriseSerializer
    filterset_class = filters.EnterpriseFilter
    search_fields = (
        'name', 'enterprise_code', 'reg_no', 'enterprise_type')


class StaffViewSet(BaseViewMixin):
    """Staff ViewSet."""

    queryset = Staff.objects.all()
    serializer_class = serializers.StaffSerializer
    filterset_class = filters.StaffFilter
    search_fields = (
        'first_name', 'last_name', 'other_names', 'gender',
        'id_no', 'staff_number', 'staff_type', 'phone_no', 'email')
