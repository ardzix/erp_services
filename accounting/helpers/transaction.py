

from django.utils import timezone
from decimal import Decimal
from .constant import *
from ..models import Account, Transaction, JournalEntry


def create_transaction(account_name, amount, transaction_type, description="", transaction_date=None, external_id32=None):
    """
    Create a transaction and the associated journal entries.

    Args:
    - account_name (str): The name of the account involved in the transaction.
    - amount (Decimal): The transaction amount.
    - transaction_type (str): The type of transaction (e.g., DEBIT or CREDIT).
    - description (str, optional): A description of the transaction.
    - transaction_date (date, optional): The date of the transaction.
    """

    # Ensure transaction date is set
    if transaction_date is None:
        transaction_date = timezone.now().date()

    # Retrieve or create the account
    account, _ = Account.objects.get_or_create(name=account_name)

    # Create the Transaction
    transaction = Transaction.objects.create(
        account=account,
        transaction_date=transaction_date,
        amount=amount,
        description=description,
        transaction_type=transaction_type,
        generate_journal=False,
        external_id32=external_id32
    )

    return transaction


def create_journal_entry(transaction, amount, account_name, transaction_type):
    account, _ = Account.objects.get_or_create(name=account_name)
    JournalEntry.objects.create(
        transaction=transaction,
        journal=account_name,
        debit_credit=transaction_type,
        amount=amount
    )
    update_general_ledger(account, amount, transaction_type)


def update_general_ledger(account, amount, transaction_type):
    """
    Update the general ledger for the given account and amount.

    Args:
    - account (Account): The account object.
    - amount (Decimal): The amount to update.
    - transaction_type (str): The type of transaction (e.g., DEBIT or CREDIT).
    """
    from accounting.models import GeneralLedger

    # Retrieve or create the general ledger entry for the account
    ledger, _ = GeneralLedger.objects.get_or_create(account=account)
    print(ledger, amount, transaction_type)
    # Update the ledger balance
    if transaction_type == DEBIT:
        ledger.balance += Decimal(amount)
    elif transaction_type == CREDIT:
        ledger.balance -= Decimal(amount)

    ledger.save()
