from .models import Transaction


def add_transaction(wallet, tx_type, amount, status="pending", **kwargs):
    return Transaction.objects.create(wallet=wallet, type=tx_type, amount=amount, status=status, **kwargs)
