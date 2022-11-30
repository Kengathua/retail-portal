"""Enterprise filters file."""

from elites_retail_portal.common.filters import SearchComboboxBaseFilter
from elites_retail_portal.enterprises import models


class EnterpriseFilter(SearchComboboxBaseFilter):
    """Filter enterprise."""

    class Meta:
        """Restrict filter fields."""

        model = models.Enterprise
        fields = '__all__'


class StaffFilter(SearchComboboxBaseFilter):
    """Filter Staff."""

    class Meta:
        """Restrict filter fields."""

        model = models.Staff
        fields = '__all__'
