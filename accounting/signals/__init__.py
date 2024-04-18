from django.db.models.signals import post_save, pre_save
from django.db import models
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from common.helpers import get_tenant_info
from libs.pdf import render_to_pdf, save_pdf_to_file
from ..models import AccountCategory, FinancialReportEntry, JournalEntry, Transaction, FinancialReport
from ..helpers.transaction import update_general_ledger
from ..helpers.constant import *


@receiver(post_save, sender=Transaction)
def generate_journal_entry(sender, instance, created, **kwargs):
    if created and instance.account:
        JournalEntry.objects.create(
            transaction=instance,
            account=instance.account,
            journal=f'{instance.transaction_type} of {instance.account.name}',
            amount=instance.amount,
            debit_credit=DEBIT if instance.transaction_type == CASH_OUT else CREDIT,
            is_allocation=False
        )


@receiver(post_save, sender=JournalEntry)
def assign_debit_credit(sender, instance, created, **kwargs):
    commit = False
    if not instance.debit_credit:
        instance.debit_credit = DEBIT if instance.transaction.transaction_type == CASH_IN else CREDIT
        commit = True

    if created:
        update_general_ledger(
            instance.account, instance.amount, instance.debit_credit)
        if commit:
            instance.save()


@receiver(post_save, sender=FinancialReport)
def generate_financial_report_entries(sender, instance, created, **kwargs):
    from ..serializers.report import FinancialReportSerializer
    financial_statement = instance.financial_statement
    financial_entries = financial_statement.financialentry_set.all()
    for entry in financial_entries:
        for category in AccountCategory.objects.filter(parent=entry.category):
            journals = JournalEntry.objects.filter(
                account__category=category, transaction__transaction_date__gte=instance.start_date, transaction__transaction_date__lte=instance.end_date)
            amount = journals.aggregate(
                total_amount=models.Sum('amount')).get('total_amount')
            if amount:
                FinancialReportEntry.objects.get_or_create(
                    financial_report=instance,
                    entry=entry,
                    category=category,
                    defaults={
                        "amount": amount
                    }
                )

    if not instance.attachment:
        context = FinancialReportSerializer(instance).data
        context['tenant_info'] = get_tenant_info()
        pdf_content = render_to_pdf(
            'document/financial_statement.html', context)
        if pdf_content:
            filename = f"Financial Statement_{financial_statement.__str__()}.pdf"
            file = save_pdf_to_file(pdf_content, filename)
            instance.attachment = file
            instance.save()
