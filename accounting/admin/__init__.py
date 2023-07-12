from django.contrib import admin
from libs.admin import ApproveRejectMixin, BaseAdmin
from ..models import Account, Transaction, JournalEntry, GeneralLedger, FinancialStatement, FinancialEntry

@admin.register(Account)
class AccountAdmin(BaseAdmin):
    list_display = ['name', 'description']
    list_filter = []

@admin.register(Transaction)
class TransactionAdmin(BaseAdmin):
    list_display = ['account', 'transaction_date', 'amount', 'description']
    list_filter = ['account']

@admin.register(JournalEntry)
class JournalEntryAdmin(BaseAdmin):
    list_display = ['transaction', 'journal']
    list_filter = ['journal']

@admin.register(GeneralLedger)
class GeneralLedgerAdmin(BaseAdmin):
    list_display = ['account', 'balance']
    list_filter = []

@admin.register(FinancialStatement)
class FinancialStatementAdmin(BaseAdmin):
    list_display = ['name', 'description']
    list_filter = []

@admin.register(FinancialEntry)
class FinancialEntryAdmin(BaseAdmin):
    list_display = ['financial_statement', 'account', 'amount']
    list_filter = ['financial_statement']
