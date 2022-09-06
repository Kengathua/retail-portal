"""Transactions helpers file."""


def create_order_transaction(transaction, customer_orders):
    """Add and order transaction."""
    from elites_franchise_portal.orders.models import OrderTransaction
    for customer_order in customer_orders:
        transaction = transaction._meta.model.objects.get(id=transaction.id)

        order_transaction_data = {
            'amount': transaction.balance,
            'created_by': transaction.created_by,
            'enterprise': transaction.enterprise,
            'order': customer_order,
            'transaction': transaction,
            'updated_by': transaction.updated_by,
        }
        OrderTransaction.objects.create(**order_transaction_data)
