from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from libs.utils import get_config_value
from sales.models import Invoice, SalesPayment
from accounting.models import ModuleAccount, JournalEntry, Transaction, TransactionCategory
from accounting.helpers.constant import *


@receiver(post_save, sender=Invoice)
def commit_transaction_on_invoice_created(sender, instance, created, **kwargs):
    if created:
        modul_accounts = ModuleAccount.objects.filter(transaction=SALES_ORDER)
        transaction_type, created = TransactionCategory.objects.get_or_create(
            code = 'sales_order',
            defaults={
                "name": 'Sales Order',
                "prefix": 'SO'
            }
        )
        transaction = Transaction.objects.create(
            transaction_type = transaction_type,
            transaction_date = instance.order.order_date,
            amount = instance.subtotal
        )
        for ma in modul_accounts:
            JournalEntry.objects.create(
                transaction = transaction,
                account = ma.account,
                journal = instance.order.__str__(),
                amount = instance.subtotal,
                debit_credit = ma.debit_credit
            )