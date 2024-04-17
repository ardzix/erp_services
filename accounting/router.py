from rest_framework.routers import DefaultRouter
from .views import AccountCategoryViewSet, AccountViewSet, TaxViewSet, TransactionViewSet, JournalEntryViewSet, ModuleAccountViewSet, GeneralLedgerViewSet, TransactionCategoryViewSet
from .views.reports import TransactionSaleReportViewSet

router = DefaultRouter()
router.register('account_category', AccountCategoryViewSet, basename='account_category')
router.register('account', AccountViewSet, basename='account')
router.register('general_ledger', GeneralLedgerViewSet, basename='general_ledger')
router.register('journal_entry', JournalEntryViewSet, basename='journal_entry')
router.register('module_account', ModuleAccountViewSet, basename='module_account')
router.register('tax', TaxViewSet, basename='tax')
router.register('transaction', TransactionViewSet, basename='transaction')
router.register('transaction_category', TransactionCategoryViewSet, basename='transaction_category')
router.register('transaction_report', TransactionSaleReportViewSet, basename='transaction_report')
