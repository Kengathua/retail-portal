"""."""

from django.core.exceptions import ValidationError
from elites_retail_portal.enterprise_mgt.helpers import get_valid_enterprise_setup_rules


def get_catalog_item_available_quantity(catalog_item, include_encounters=True):
    """Get catalog item available quantity."""
    from elites_retail_portal.encounters.helpers.encounters import (
        get_all_unprocessed_encounters)
    unprocessed_encounters_quantity = 0
    enterprise_code = catalog_item.enterprise
    enterprise_setup_rules = get_valid_enterprise_setup_rules(enterprise_code)
    default_catalog = enterprise_setup_rules.default_catalog
    catalog_item = default_catalog.catalog_items.filter(id=catalog_item.id).first()
    if not catalog_item:
        raise ValidationError(
            {'catalog_item': "The item does not exist in the default catalog"})

    if include_encounters:
        encounters = get_all_unprocessed_encounters(enterprise_code, catalog_item)
        if encounters:
            billings = encounters.values_list('billing', flat=True)
            unprocessed_encounter_quantities = []
            for billing in billings:
                quantities = [bill['quantity'] for bill in billing if bill[
                    'catalog_item'] == str(catalog_item.id)]
                unprocessed_encounter_quantities.extend(quantities)
            unprocessed_encounters_quantity = sum(unprocessed_encounter_quantities)

    quantity = catalog_item.quantity - unprocessed_encounters_quantity

    return quantity
