"""Enterprise filters file."""

from elites_franchise_portal.common.filters import SearchComboboxBaseFilter
from elites_franchise_portal.enterprises import models


class EnterpriseFilter(SearchComboboxBaseFilter):
    """Filter individual item store."""

    class Meta:
        """Restrict filter fields."""

        model = models.Enterprise
        fields = '__all__'
