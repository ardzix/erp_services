from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from libs.base_model import BaseModelGeneric, User
from common.models import File
from ..helpers.constant import *





class Tax(BaseModelGeneric):
    name = models.CharField(max_length=100)
    rate = models.DecimalField(
        max_digits=5, decimal_places=2)  # As a percentage

    def __str__(self):
        return _("Tax #{tax_id} - {tax_name}").format(tax_id=self.id32, tax_name=self.name)

    class Meta:
        verbose_name = _("Tax")
        verbose_name_plural = _("Taxes")


class Category(BaseModelGeneric):
    number = models.PositiveIntegerField(help_text=_("Enter category number"))
    name = models.CharField(
        max_length=100, help_text=_("Enter the category name"))
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(
        blank=True, help_text=_("Enter the category description"))

    def __str__(self):
        return _("#{number} - {category_name}").format(
            number=self.number,
            category_name=self.name
        )

    class Meta:
        ordering = ['number']
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")


class Account(BaseModelGeneric):
    number = models.CharField(
        max_length=20, help_text=_("Enter account number"))
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return _("#{number} - {account_name}").format(number=self.number, account_name=self.name)

    class Meta:
        verbose_name = _("Account")
        verbose_name_plural = _("Accounts")
        ordering = ['number']


class Transaction(BaseModelGeneric):
    TRANSACTION_TYPES = [
        (CASH_IN, _('Cash In')),
        (CASH_OUT, _('Cash Out')),
    ]

    transaction_type = models.CharField(
        max_length=20, choices=TRANSACTION_TYPES, default=CASH_IN)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    transaction_date = models.DateField()
    amount = models.DecimalField(max_digits=19, decimal_places=2)
    description = models.TextField(blank=True)
    attachements = models.ManyToManyField(File, blank=True)
    allocations = models.ManyToManyField(Account, related_name="account_allocations", through='JournalEntry', help_text=_("Select journal entry as allocations"))
    origin_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        blank=True, null=True,
        help_text=_("Select the content type of the origin")
    )
    origin_id = models.PositiveIntegerField(
        blank=True, null=True, help_text=_("Enter the ID of the origin"))
    origin = GenericForeignKey('origin_type', 'origin_id')
    

    def __str__(self):
        return _("#{transaction_id} - {transaction_account}").format(transaction_id=self.id32, transaction_account=self.account)

    class Meta:
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")
        ordering = ['-id']


class JournalEntry(BaseModelGeneric):
    DEBIT_CREDIT_CHOICES = [
        (DEBIT, _('Debit')),
        (CREDIT, _('Credit'))
    ]

    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    journal = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=19, decimal_places=2)
    debit_credit = models.CharField(
        max_length=10, choices=DEBIT_CREDIT_CHOICES, blank=True, null=True)
    is_allocation = models.BooleanField(default=True)

    def __str__(self):
        return _("#{entry_id} - {entry_transaction}").format(entry_id=self.id32, entry_transaction=self.transaction)

    class Meta:
        verbose_name = _("Journal Entry")
        verbose_name_plural = _("Journal Entries")
        ordering = ['-id']


class GeneralLedger(BaseModelGeneric):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=19, decimal_places=2, default=0)

    def __str__(self):
        return _("General Ledger #{ledger_id} - {ledger_account}").format(ledger_id=self.id32, ledger_account=self.account)

    class Meta:
        verbose_name = _("General Ledger")
        verbose_name_plural = _("General Ledgers")
        ordering = ['-id']


class FinancialStatement(BaseModelGeneric):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return _("Financial Statement #{statement_id} - {statement_name}").format(statement_id=self.id32, statement_name=self.name)

    class Meta:
        verbose_name = _("Financial Statement")
        verbose_name_plural = _("Financial Statements")
        ordering = ['-id']


class FinancialEntry(BaseModelGeneric):
    financial_statement = models.ForeignKey(
        FinancialStatement, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=19, decimal_places=2)

    def __str__(self):
        return _("Financial Entry #{entry_id} - {entry_statement}").format(entry_id=self.id32, entry_statement=self.financial_statement)

    class Meta:
        verbose_name = _("Financial Entry")
        verbose_name_plural = _("Financial Entries")
        ordering = ['-id']
