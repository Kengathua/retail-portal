"""Common views file."""

from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class DataPartitionMixin(object):
    """Determines what data to return based on user's enterprise organisation."""

    def get_queryset(self):
        """Filter data based on field attribute."""
        from elites_retail_portal.enterprises.models import Enterprise
        queryset = super(DataPartitionMixin, self).get_queryset()

        partition_spec = getattr(self, 'partition_spec', None)
        if partition_spec is None:
            return queryset

        enterprise_code = self.request.user.enterprise

        try:
            enterprise = Enterprise.objects.get(enterprise_code=enterprise_code)
        except Enterprise.DoesNotExist:
            return queryset.none()

        enterprise_spec = partition_spec.get(enterprise.enterprise_type, None)
        if enterprise_spec is None:
            return queryset.none()

        # we want to filter entries by enterprise type
        filter_field = "{}".format(enterprise_spec)
        queryset = queryset.filter(**{filter_field: enterprise.enterprise_code})
        return queryset


class BaseViewMixin(DataPartitionMixin, viewsets.ModelViewSet):
    """Base View mixin for model viewsets."""

    def get_serializer(self, *args, **kwargs):
        """Update serializer selection logic to be aware of plain (non queryset) lists."""
        if "data" in kwargs:
            data = kwargs["data"]
            if isinstance(data, list):
                kwargs["many"] = True

        return super(BaseViewMixin, self).get_serializer(*args, **kwargs)

    @action(detail=False, methods=['put'])
    def bulk_update(self, request, *args, **kwargs):
        """Implement support for bulk updates via HTTP PUT."""
        if isinstance(request.data, list):
            resp = []
            with transaction.atomic():
                for item in request.data:
                    instance = self.queryset.get(id=item['id'])
                    serializer = self.get_serializer(
                        instance, data=item, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    resp.append(serializer.data)
            return Response(data=resp, status=status.HTTP_200_OK)
        else:
            return Response(
                data={'error': "Expected list"}, status=status.HTTP_400_BAD_REQUEST)


class ReadOnlyBaseViewMixin(viewsets.ReadOnlyModelViewSet):
    """Read only vies base class."""

    pass
