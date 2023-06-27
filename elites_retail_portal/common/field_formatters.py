"""Custom field formatters for Excel export."""
from dateutil.parser import parse


class BaseFieldFormatter(object):
    """Base class for custom formatters."""

    @classmethod
    def format_field_data(cls, value):
        """Require the implementation of a field formatter in base classes."""
        raise NotImplementedError


class DefaultFormatter(BaseFieldFormatter):
    """Default no-op formatter."""

    @classmethod
    def format_field_data(cls, value):
        """Pass through (doing nothing) as a default."""
        return value


class FormatDateField(BaseFieldFormatter):
    """Format dates as strings for Excel."""

    @classmethod
    def format_field_data(cls, value):
        """Render dates as friendly strings for Excel."""
        try:
            date_object = parse(str(value))
        # not a valid date object  or date string
        except ValueError:
            return str(value)

        return "{} - {} - {}".format(
            date_object.day,
            date_object.month,
            date_object.year
        )


class CapitalizeStringField(BaseFieldFormatter):
    """Render strings in uppercase."""

    @classmethod
    def format_field_data(cls, value):
        """Capitalize the input string."""
        return value.capitalize()


class FormatBooleanField(BaseFieldFormatter):
    """Render booleans as Yes/No strings."""

    @classmethod
    def format_field_data(cls, value):
        """Render boolean fields as Yes/No/NA."""
        if value is True:
            return 'Yes'
        elif value is False:
            return 'No'
        else:
            return 'N/A'


class FormatMoneyField(BaseFieldFormatter):
    """Add a KES prefix to money fields."""

    @classmethod
    def format_field_data(cls, value):
        """Add a KES currency prefix to money fields."""
        return "KES {:,.2f}".format(value)


class FormatNumberField(BaseFieldFormatter):
    """Format numbers to 2 d.p."""

    @classmethod
    def format_field_data(cls, value):
        """Format decimal numbers to 2 places."""
        return "{:,.2f}".format(value)


FIELD_FORMATTERS = {
    None: DefaultFormatter,
    'date': FormatDateField,
    'capitalize': CapitalizeStringField,
    'boolean': FormatBooleanField,
    'money': FormatMoneyField,
    'number': FormatNumberField,
}
