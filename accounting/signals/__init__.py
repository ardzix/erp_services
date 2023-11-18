from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from ..models import Transaction
from ..helpers.transaction import create_journal_entry
from ..helpers.constant import *


@receiver(post_save, sender=Transaction)
def generate_journal_entry(sender, instance, created, **kwargs):
    account_type = instance.transaction_type
    account_name = instance.account.name
    amount = instance.amount
    if created and instance.generate_journal and account_type in dict(JOURNAL_DEBIT_MAP):
        debit_account_name = dict(JOURNAL_DEBIT_MAP).get(account_type)
        create_journal_entry(instance, amount, debit_account_name, DEBIT)
        create_journal_entry(instance, amount, account_name, CREDIT)
