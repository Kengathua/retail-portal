"""Filters that are used by most apps in this server."""
from django.core import exceptions
from django.db.models import Case, IntegerField, Value, When
from django_filters import rest_framework as filters
from rest_framework.filters import BaseFilterBackend, SearchFilter


class EnterpriseFilterBackend(BaseFilterBackend):
    """Limit users to viewing records in their organisation."""

    def filter_queryset(self, request, queryset, view):
        """Filter all querysets by the logged in user's organization, where possible."""
        try:
            return queryset.filter(
                enterprise=request.user.enterprise)
        except exceptions.FieldError:
            # if the model does not have an 'enterprise' field, skip
            return queryset


class SearchComboboxBaseFilter(filters.FilterSet):
    """Ensure that combobox results always include the selected item.

    This should be the case even if the selected record would not ordinarily be on the first
    page of a paginated result set.
    """

    def combobox_filter(self, queryset, field, value):
        """Annotate the queryset to ensure that the selected item is always first on the list."""
        # annotate with a field called 'custom_order' that places the combobox supplied value first
        # this ensures that the selected item shows up at the top, even if there are very many
        # results
        ordering_filters = (
            'custom_order', '-updated_on') if hasattr(
                self.Meta().model, 'created_on') else ('custom_order', '-updated_on')

        return queryset.annotate(
            custom_order=Case(
                When(pk__in=value.split(','), then=Value(0)),
                output_field=IntegerField(),
                default=Value(1))).order_by(*ordering_filters)

    search = SearchFilter()
    combobox = filters.CharFilter(method='combobox_filter')


class CommaSeparatedCharFilter(filters.BaseInFilter, filters.CharFilter):
    """A filter that takes and processes comma separated input values."""

    pass
