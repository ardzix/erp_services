from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from libs.base_model import BaseModelGeneric, User
from common.models import File
from identities.models import Contact
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


class AccountCategory(BaseModelGeneric):
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
        verbose_name = _("Account Category")
        verbose_name_plural = _("Account Categories")


class Account(BaseModelGeneric):
    number = models.CharField(
        unique=True, max_length=20, help_text=_("Enter account number"), blank=True, null=True)
    category = models.ForeignKey(
        AccountCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    inverse_debit_credit = models.BooleanField(default=False)

    def __str__(self):
        return _("#{number} - {account_name}").format(number=self.number, account_name=self.name)

    def save(self, *args, **kwargs):
        """Overwrite the save method to incorporate custom logic."""

        if not self.number:
            category_number = self.category.number 
            prev = self.__class__.all_objects.order_by('id').last()
            obj_id = prev.id + 1 if prev else 1
            self.number = f'{category_number}00-00-{str(obj_id).zfill(3)}'

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Account")
        verbose_name_plural = _("Accounts")
        ordering = ['number']


class TransactionCategory(BaseModelGeneric):
    name = models.CharField(
        max_length=100, help_text=_("Enter the category name"))
    code = models.CharField(
        max_length=100, help_text=_("Enter the category code"))
    prefix = models.CharField(
        blank=True, null=True,
        max_length=20, help_text=_("Enter the category prefix"))
    description = models.TextField(
        blank=True, help_text=_("Enter the category description"))

    def __str__(self):
        return _("#{id32} - {category_name}").format(
            id32=self.id32,
            category_name=self.name
        )

    class Meta:
        ordering = ['id']
        verbose_name = _("Transaction Category")
        verbose_name_plural = _("Transaction Categories")


class Transaction(BaseModelGeneric):
    number = models.CharField(
        max_length=100,
        db_index=True,
        blank=True,
        null=True)
    transaction_type = models.ForeignKey(
        TransactionCategory, on_delete=models.CASCADE)
    account = models.ForeignKey(
        Account, on_delete=models.SET_NULL, blank=True, null=True)
    transaction_date = models.DateField()
    amount = models.DecimalField(max_digits=19, decimal_places=2)
    description = models.TextField(blank=True)
    allocations = models.ManyToManyField(Account, related_name="account_allocations",
                                         through='JournalEntry', help_text=_("Select journal entry as allocations"))
    source = models.ForeignKey(
        Contact, blank=True, null=True, on_delete=models.SET_NULL
    )
    attachment = models.ForeignKey(
        File, related_name='%(app_label)s_%(class)s_attachment', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.number

    def save(self, *args, **kwargs):
        """Overwrite the save method to incorporate custom logic."""

        if not self.number:
            category_number = self.account.category.number if self.account else '00'
            prev = self.__class__.all_objects.order_by('id').last()
            obj_id = prev.id + 1 if prev else 1
            prefix = self.transaction_type.prefix if self.transaction_type.prefix else ""
            self.number = f'{prefix}{category_number}{str(obj_id).zfill(6)}'

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")
        ordering = ['-id']


class JournalEntry(BaseModelGeneric):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    journal = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=19, decimal_places=2)
    debit_credit = models.CharField(
        max_length=10, choices=DEBIT_CREDIT_CHOICES, blank=True, null=True)
    is_allocation = models.BooleanField(default=True)

    def __str__(self):
        return _("#{entry_id} - {account}").format(entry_id=self.id32, account=self.account)

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


class ModuleAccount(BaseModelGeneric):
    name = models.CharField(
        unique=True, max_length=100, choices=TRANSACTION_MODULE_CHOICES, help_text=_("Enter the module account name"))
    transaction = models.CharField(
        max_length=25, choices=TRANSACTION_CHOICES, help_text=_("Enter the transaction"))
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    debit_credit = models.CharField(
        max_length=10, choices=DEBIT_CREDIT_CHOICES, default=DEBIT)

    def __str__(self):
        return _("Module Account #{id32} - {name}").format(id32=self.id32, name=dict(TRANSACTION_CHOICES).get(self.name))

    class Meta:
        unique_together = ('transaction', 'account')
        verbose_name = _("Module Account")
        verbose_name_plural = _("Module Accounts")
        ordering = ['name']


class FinancialStatement(BaseModelGeneric):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    categories = models.ManyToManyField(AccountCategory, through='FinancialEntry')

    def __str__(self):
        return _("Financial Statement #{statement_id} - {statement_name}").format(statement_id=self.id32, statement_name=self.name)

    class Meta:
        verbose_name = _("Financial Statement")
        verbose_name_plural = _("Financial Statements")
        ordering = ['name']


class FinancialEntry(BaseModelGeneric):
    financial_statement = models.ForeignKey(
        FinancialStatement, on_delete=models.CASCADE)
    category = models.ForeignKey(AccountCategory, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return _("{statement}: {account}").format(statement=self.financial_statement.__str__(), account=self.category.__str__())

    class Meta:
        verbose_name = _("Financial Entry")
        verbose_name_plural = _("Financial Entries")
        ordering = ['order']



class FinancialReport(BaseModelGeneric):
    financial_statement = models.ForeignKey(
        FinancialStatement, on_delete=models.CASCADE)
    start_date = models.DateField(help_text=_("Start date of the report"))
    end_date = models.DateField(help_text=_("End date of the report"))
    attachment = models.ForeignKey(
        File, related_name='%(app_label)s_%(class)s_attachment', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return _("Financial Report #{statement_id} - {statement_name} - {start_date}-{end_date}").format(
            statement_id=self.id32, 
            statement_name=self.financial_statement.name, 
            start_date=self.start_date, 
            end_date=self.end_date, )

    class Meta:
        unique_together = ('financial_statement', 'start_date', 'end_date')
        verbose_name = _("Financial Report")
        verbose_name_plural = _("Financial Reports")
        ordering = ['-id']


class FinancialReportEntry(BaseModelGeneric):
    financial_report = models.ForeignKey(
        FinancialReport, on_delete=models.CASCADE)
    entry = models.ForeignKey(FinancialEntry, on_delete=models.CASCADE)
    category = models.ForeignKey(AccountCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=19, decimal_places=2)

    def __str__(self):
        return _("{report}: {account}").format(report=self.financial_report.__str__(), account=self.category.__str__())

    class Meta:
        verbose_name = _("Financial Report Entry")
        verbose_name_plural = _("Financial Report Entries")
        ordering = ['entry__order']
