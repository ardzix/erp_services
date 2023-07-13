from django.db import models
from django.utils.translation import gettext_lazy as _
from libs.base_model import BaseModelGeneric, User

class Account(BaseModelGeneric):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    # Add any other fields specific to your account model

    def __str__(self):
        return f"Account #{self.id32} - {self.name}"

    class Meta:
        verbose_name = _("Account")
        verbose_name_plural = _("Accounts")


class Transaction(BaseModelGeneric):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    transaction_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    # Add any other fields specific to your transaction model

    def __str__(self):
        return f"Transaction #{self.id32} - {self.account}"

    class Meta:
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")


class JournalEntry(BaseModelGeneric):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    journal = models.CharField(max_length=100)
    # Add any other fields specific to your journal entry model

    def __str__(self):
        return f"Journal Entry #{self.id32} - {self.transaction}"

    class Meta:
        verbose_name = _("Journal Entry")
        verbose_name_plural = _("Journal Entries")


class GeneralLedger(BaseModelGeneric):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    # Add any other fields specific to your general ledger model

    def __str__(self):
        return f"General Ledger #{self.id32} - {self.account}"

    class Meta:
        verbose_name = _("General Ledger")
        verbose_name_plural = _("General Ledgers")


class FinancialStatement(BaseModelGeneric):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    # Add any other fields specific to your financial statement model

    def __str__(self):
        return f"Financial Statement #{self.id32} - {self.name}"

    class Meta:
        verbose_name = _("Financial Statement")
        verbose_name_plural = _("Financial Statements")


class FinancialEntry(BaseModelGeneric):
    financial_statement = models.ForeignKey(FinancialStatement, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # Add any other fields specific to your financial entry model

    def __str__(self):
        return f"Financial Entry #{self.id32} - {self.financial_statement}"

    class Meta:
        verbose_name = _("Financial Entry")
        verbose_name_plural = _("Financial Entries")
