"""Encounters helper file."""

from elites_retail_portal.encounters.models import Encounter

UNPROCESSED_ENCOUNTERS_STATUS = ['PENDING', 'ONGOING']


def process_billing(encounter):
    """Process encounter billing."""
    pass


def get_all_unprocessed_encounters(enterprise_code, catalog_item=None):
    """."""
    encounters = Encounter.objects.filter(
        enterprise=enterprise_code, processing_status__in=UNPROCESSED_ENCOUNTERS_STATUS)
    if catalog_item and encounters.exists():
        catalog_item_encounter_ids = []
        for encounter in encounters:
            encounter_id = [
                str(encounter.id) for data in encounter.billing
                if data['catalog_item'] == str(catalog_item.id)]
            catalog_item_encounter_ids.extend(encounter_id)

        if catalog_item_encounter_ids:
            encounters = encounters.filter(id__in=catalog_item_encounter_ids)

    return encounters
