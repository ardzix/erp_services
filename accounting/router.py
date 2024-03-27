from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, AccountViewSet, TaxViewSet, TransactionViewSet, JournalEntryViewSet, GeneralLedgerViewSet
from .views.reports import TransactionSaleReportViewSet

router = DefaultRouter()
router.register('category', CategoryViewSet, basename='category')
router.register('account', AccountViewSet, basename='account')
router.register('tax', TaxViewSet, basename='tax')
router.register('transaction', TransactionViewSet, basename='transaction')
router.register('journal_entry', JournalEntryViewSet, basename='journal_entry')
router.register('general_ledger', GeneralLedgerViewSet, basename='general_ledger')
router.register('transaction_report', TransactionSaleReportViewSet, basename='transaction_report')
