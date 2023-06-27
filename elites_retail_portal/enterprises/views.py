"""Enterprise views."""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from elites_retail_portal.common.views import BaseViewMixin
from elites_retail_portal.enterprises.models import Enterprise, Staff
from elites_retail_portal.enterprises import serializers
from elites_retail_portal.enterprises import filters
from elites_retail_portal.reporting.sales_persons_report import get_sales_person_sales_data


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

    @action(detail=False, methods=['post'])
    def generate_sales_person_report(self, request, *args, **kwargs):
        """Generate members upload template."""
        enterprise_code = self.request.user.enterprise
        start_date = self.request.data.get('start_date', None)
        end_date = self.request.data.get('end_date', None)
        sales_person_id = self.request.data.get('sales_person', None)
        sales_persons = Staff.objects.filter(id=sales_person_id) if sales_person_id else []

        data = get_sales_person_sales_data(enterprise_code, sales_persons, start_date, end_date)

        return Response(data=data, status=status.HTTP_201_CREATED)
