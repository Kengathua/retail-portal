"""Sales helper file."""

import pytz
import datetime

from elites_retail_portal.debit.models import Sale, SaleItem


def get_sale_item_data(sale_item):
    """Get sale item data."""
    return {
        'sale_date': sale_item.sale.sale_date.strftime("%Y-%m-%d"),
        'receipt_number': sale_item.sale.receipt_number,
        'customer': sale_item.sale.customer.full_name if sale_item.sale.customer else '',
        'order_number': sale_item.sale.order.order_number if sale_item.sale.order else '',
        'amount_paid': float(sale_item.amount_paid),
        'item': sale_item.catalog_item.inventory_item.item.item_name,
        'status': 'CLEARED' if sale_item.is_cleared else 'NOT CLEARED',
        'processing_status': sale_item.processing_status,
        'quantity_sold': sale_item.quantity_sold,
        'sale_type': sale_item.sale_type,
        'selling_price': float(sale_item.selling_price),
        'total_price': float(sale_item.total_amount),
    }


def create_report_data(sale_items):
    """Create sales data."""
    sales_data = []
    totals_data = {}
    total_amount_paid = 0
    total_price = 0
    total_quantity = 0
    for sale_item in sale_items:
        data = get_sale_item_data(sale_item)
        sales_data.append(data)
        total_amount_paid += data['amount_paid']
        total_price += data['total_price']
        total_quantity += data['quantity_sold']

    totals_data['amount_paid'] = total_amount_paid
    totals_data['total_price'] = total_price
    totals_data['total_quantity'] = total_quantity

    return {
        "sales_data": sales_data,
        "totals_data": totals_data,
        }


def generate_sales_report(enterprise_code, item=None, start_date=None, end_date=None):
    """Generate sales report."""
    if not start_date and not end_date:
        today = datetime.datetime.now(tz=pytz.timezone('Africa/Nairobi')).date()
        sales = Sale.objects.filter(enterprise=enterprise_code, sale_date__gte=today)
        sale_items = SaleItem.objects.filter(sale__in=sales).order_by('-sale__sale_date')
        if item:
            sale_items = sale_items.filter(catalog_item__inventory_item__item=item)
        return create_report_data(sale_items)

    if start_date and end_date:
        sales = Sale.objects.filter(
            enterprise=enterprise_code, sale_date__gte=start_date,
            sale_date__lte=end_date).order_by('-sale_date')
        sale_items = SaleItem.objects.filter(sale__in=sales).order_by('-sale__sale_date')
        if item:
            sale_items = sale_items.filter(catalog_item__inventory_item__item=item)
        return create_report_data(sale_items)

    if start_date and not end_date:
        sales = Sale.objects.filter(
            enterprise=enterprise_code, sale_date__gte=start_date).order_by('-sale_date')
        sale_items = SaleItem.objects.filter(sale__in=sales).order_by('-sale__sale_date')
        if item:
            sale_items = sale_items.filter(catalog_item__inventory_item__item=item)
        return create_report_data(sale_items)

    # Has end date and no start date
    sales = Sale.objects.filter(
        enterprise=enterprise_code, sale_date__lte=end_date).order_by('-sale_date')
    sale_items = SaleItem.objects.filter(sale__in=sales).order_by('-sale__sale_date')
    if item:
        sale_items = sale_items.filter(catalog_item__inventory_item__item=item)
    return create_report_data(sale_items)
