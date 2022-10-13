"""Encounters Validation Helpers file."""
from django.core.exceptions import ValidationError
from elites_franchise_portal.restrictions_mgt.helpers import get_valid_enterprise_setup_rules
from elites_franchise_portal.catalog.helpers import (
    get_catalog_item_available_quantity)
from elites_franchise_portal.catalog.models import CatalogItem, CatalogCatalogItem

def validate_catalog_item(item_name, enterprise_code, catalog_item=None):
    if not catalog_item:
        msg = "{} does not exist in the catalog or has been deactivated".format(item_name)
        raise ValidationError(
            {'catalog_item': msg})

    enterprise_setup_rules = get_valid_enterprise_setup_rules(enterprise_code)
    default_catalog = enterprise_setup_rules.default_catalog
    catalog_item_in_catalog = default_catalog.catalog_items.filter(id=catalog_item.id, is_active=True).first()
    if not catalog_item_in_catalog:
        audit_fields = {
            'created_by': catalog_item.created_by,
            'updated_by': catalog_item.updated_by,
            'enterprise': catalog_item.enterprise,
            }
        CatalogCatalogItem.objects.create(catalog_item=catalog_item, catalog=default_catalog, **audit_fields)


def validate_billing(encounter):
    """Valdiate new sale encounter data."""
    for bill in encounter.billing:
        catalog_items = CatalogItem.objects.filter(
            id=bill['catalog_item'], is_active=True)
        catalog_item = catalog_items.first()
        validate_catalog_item(bill['item_name'], encounter.enterprise, catalog_item)
        item_name = catalog_item.inventory_item.item.item_name

        if bill['sale_type'] == 'INSTANT':
            available_quantity = get_catalog_item_available_quantity(
                catalog_item)
            if bill['quantity'] > available_quantity:
                billed_quantity = bill['quantity']
                raise ValidationError(
                    {'quantity': '{} - Billed quantity {} is more '
                        'than the available quantity of {}'.format(
                        item_name, billed_quantity, available_quantity)})

        if bill['sale_type'] == 'INSTALLMENT':
            pass

        if float(bill['unit_price']) < float(catalog_item.threshold_price):
            raise ValidationError(
                {'price': 'The threshold price for {} is {}'.format(
                    item_name, catalog_item.threshold_price)})