from django.db import models
from django.utils.translation import gettext_lazy as _
from libs.base_model import BaseModelGeneric, User


class Account(BaseModelGeneric):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return _("Account #{account_id} - {account_name}").format(account_id=self.id32, account_name=self.name)

    class Meta:
        verbose_name = _("Account")
        verbose_name_plural = _("Accounts")


class Transaction(BaseModelGeneric):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    transaction_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

    def __str__(self):
        return _("Transaction #{transaction_id} - {transaction_account}").format(transaction_id=self.id32, transaction_account=self.account)

    class Meta:
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")


class JournalEntry(BaseModelGeneric):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    journal = models.CharField(max_length=100)

    def __str__(self):
        return _("Journal Entry #{entry_id} - {entry_transaction}").format(entry_id=self.id32, entry_transaction=self.transaction)

    class Meta:
        verbose_name = _("Journal Entry")
        verbose_name_plural = _("Journal Entries")


class GeneralLedger(BaseModelGeneric):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)

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
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return _("Financial Entry #{entry_id} - {entry_statement}").format(entry_id=self.id32, entry_statement=self.financial_statement)

    class Meta:
        verbose_name = _("Financial Entry")
        verbose_name_plural = _("Financial Entries")
