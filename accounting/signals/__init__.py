from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from ..models import JournalEntry, Transaction
from ..helpers.transaction import update_general_ledger
from ..helpers.constant import *


@receiver(post_save, sender=Transaction)
def generate_journal_entry(sender, instance, created, **kwargs):
    if created:
        JournalEntry.objects.create(
            transaction = instance,
            account = instance.account,
            journal = f'{instance.transaction_type} of {instance.account.name}',
            amount = instance.amount,
            debit_credit = DEBIT if instance.transaction_type == CASH_OUT else CREDIT,
            is_allocation = False
        )

@receiver(post_save, sender=JournalEntry)
def assign_debit_credit(sender, instance, created, **kwargs):
    commit = False
    if not instance.debit_credit:
        instance.debit_credit = DEBIT if instance.transaction.transaction_type == CASH_IN else CREDIT
        commit = True
        
    if created:
        update_general_ledger(instance.account, instance.amount, instance.debit_credit)
        if commit:
            instance.save()

