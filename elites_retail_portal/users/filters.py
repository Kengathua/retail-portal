"""Users filters file."""
from elites_retail_portal.common.filters import SearchComboboxBaseFilter
from elites_retail_portal.users import models


class GroupFilter(SearchComboboxBaseFilter):
    """Filter individual user groups."""

    class Meta:
        """Restrict filter fields."""

        model = models.Group
        fields = '__all__'


class UserFilter(SearchComboboxBaseFilter):
    """Filter individual user user."""

    class Meta:
        """Restrict filter fields."""

        model = models.User
        fields = '__all__'
