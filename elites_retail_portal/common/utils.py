"""Common utilities file."""

import logging
import xlsxwriter
from io import BytesIO

from .field_formatters import FIELD_FORMATTERS

from django.core.exceptions import ValidationError

LOGGER = logging.getLogger(__name__)


def validate_enterprise_exists(code):
    """Validate enterprise exists."""
    from elites_retail_portal.enterprises.models import Enterprise
    enterprise_exists = Enterprise.objects.filter(enterprise_code=code).exists()
    if not enterprise_exists:
        raise ValidationError([{
            'enterprise': f'Enterprise with enterprise code {code} does not exist'
        }])


def _get_data_from_serializer_record(record, key):
    """Get value of a key from a nested data_dict.

    This supports getting values of keys nested several levels down.
    For example:
        {
            "person":{
                "details":{
                    "first_name": "Mtu",
                }
            }
        }
    To get the value of first_name supply the key as
        'person.details.first_name'
    """
    key_path = key.split('.')
    value = record
    for index, path in enumerate(key_path):
        try:
            value = value[key_path[index]]
        except KeyError:
            LOGGER.error(
                    "Unable to get the key {} while procesing {}".format(
                            key, record)
                )
            value = None
    return value


def _format_field_types(field_format, value):
    """Format a field type to a human friendly format."""
    formatter = FIELD_FORMATTERS.get(field_format)
    if formatter is None:
        formatter = FIELD_FORMATTERS.get(None)
        return formatter.format_field_data(value)
    else:
        return formatter.format_field_data(value)


def _write_excel_file(header, labels, format_fields, data):
    """Create an in-memory excel file.

    This creates an excel file in memory. This file can then be downloaded
    through content negotiation.
    """
    mem_file = BytesIO()
    workbook = xlsxwriter.Workbook(mem_file)
    format_workbook = workbook.add_format(
            {
                'bold': True,
                'font_color': 'black',
                'font_size': 12
            })

    def _add_data_to_worksheet(name='sheet1'):

        worksheet = workbook.add_worksheet(name)

        # format the row and column size
        worksheet.set_row(0, 50)
        worksheet.set_column('A:Z', 18)

        row = 0
        col = 0

        for title in header:
            label = labels.get(title)
            # write the column titles
            worksheet.write(
                    row, col, label, format_workbook)
            col = col + 1
        row = 1
        col = 0

        # now write the data to excel file
        for data_dict in data:
            for key in header:
                # format the fields to a more human readable format
                field_format = format_fields.get(key)
                formatted_value = _get_data_from_serializer_record(
                        data_dict, key)
                if field_format and formatted_value:
                    formatted_value = _format_field_types(
                            field_format,
                            _get_data_from_serializer_record(data_dict, key)
                        )

                # write the data to excel
                worksheet.write(row, col, formatted_value)
                col = col + 1

            col = 0
            row = row + 1

    _add_data_to_worksheet()
    workbook.close()
    mem_file_contents = mem_file.getvalue()
    mem_file.close()

    return mem_file_contents
