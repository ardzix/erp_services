from django.db import models
from django.utils.translation import gettext_lazy as _
from libs.base_model import BaseModelGeneric, User
from common.models import File
from ..helpers.constant import *


class Account(BaseModelGeneric):
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return _("Account #{account_id} - {account_name}").format(account_id=self.id32, account_name=self.name)

    class Meta:
        verbose_name = _("Account")
        verbose_name_plural = _("Accounts")


class Tax(BaseModelGeneric):
    name = models.CharField(max_length=100)
    rate = models.DecimalField(
        max_digits=5, decimal_places=2)  # As a percentage

    def __str__(self):
        return _("Tax #{tax_id} - {tax_name}").format(tax_id=self.id32, tax_name=self.name)

    class Meta:
        verbose_name = _("Tax")
        verbose_name_plural = _("Taxes")


class Transaction(BaseModelGeneric):
    TRANSACTION_TYPES = [
        (SALE, _('Sale')),
        (PURCHASE, _('Purchase')),
        (TRANSFER, _('Transfer')),
        (ADJUSTMENT, _('Adjustment')),
        (EXPENSE, _('Expense')),
        (INCOME, _('Income')),
        (DEPOSIT, _('Deposit')),
        (WITHDRAWAL, _('Withdrawal')),
        (REFUND, _('Refund')),
        (RECONCILIATION, _('Reconciliation')),
        (LOAN_PAYMENT, _('Loan Payment')),
        (LOAN_RECEIPT, _('Loan Receipt')),
        (TAX_PAYMENT, _('Tax Payment')),
        (TAX_REFUND, _('Tax Refund')),
        (INTEREST_INCOME, _('Interest Income')),
        (INTEREST_EXPENSE, _('Interest Expense')),
        (DIVIDEND, _('Dividend')),
        (FEE, _('Fee')),
        (COMMISSION, _('Commission')),
        (WRITE_OFF, _('Write Off')),
        (OTHER, _('Other')),
    ]

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    transaction_date = models.DateField()
    amount = models.DecimalField(max_digits=19, decimal_places=2)
    description = models.TextField(blank=True)
    transaction_type = models.CharField(
        max_length=20, choices=TRANSACTION_TYPES, default='OTHER')
    attachements = models.ManyToManyField(File, blank=True)
    generate_journal = models.BooleanField(default=True)

    def __str__(self):
        return _("Transaction #{transaction_id} - {transaction_account}").format(transaction_id=self.id32, transaction_account=self.account)

    class Meta:
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")


class JournalEntry(BaseModelGeneric):
    DEBIT_CREDIT_CHOICES = [
        (DEBIT, _('Debit')),
        (CREDIT, _('Credit')),
    ]

    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    journal = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=19, decimal_places=2)
    debit_credit = models.CharField(
        max_length=10, choices=DEBIT_CREDIT_CHOICES)

    def __str__(self):
        return _("Journal Entry #{entry_id} - {entry_transaction}").format(entry_id=self.id32, entry_transaction=self.transaction)

    class Meta:
        verbose_name = _("Journal Entry")
        verbose_name_plural = _("Journal Entries")


class GeneralLedger(BaseModelGeneric):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=19, decimal_places=2, default=0)

    def __str__(self):
        return _("General Ledger #{ledger_id} - {ledger_account}").format(ledger_id=self.id32, ledger_account=self.account)

    class Meta:
        verbose_name = _("General Ledger")
        verbose_name_plural = _("General Ledgers")


class FinancialStatement(BaseModelGeneric):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return _("Financial Statement #{statement_id} - {statement_name}").format(statement_id=self.id32, statement_name=self.name)

    class Meta:
        verbose_name = _("Financial Statement")
        verbose_name_plural = _("Financial Statements")


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
