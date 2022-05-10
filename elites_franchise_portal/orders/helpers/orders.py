"""Orders helper file."""


def process_installment(installment):
    """Process installement."""
    installment_item = installment.installment_item
    installment_item.amount_paid += installment.amount
    no_of_cleared_items = int(
        float(installment_item.amount_paid) / installment_item.unit_price) if installment_item.unit_price else 0    # noqa
    installment_item.no_of_items_cleared = no_of_cleared_items
    installment_item.save()

    return installment_item
