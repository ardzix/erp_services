from rest_framework.routers import DefaultRouter
from .views import AccountViewSet, TaxViewSet, TransactionViewSet, JournalEntryViewSet, GeneralLedgerViewSet

router = DefaultRouter()
router.register('accout', AccountViewSet, basename='accout')
router.register('tax', TaxViewSet, basename='tax')
router.register('transaction', TransactionViewSet, basename='transaction')
router.register('journal_entry', JournalEntryViewSet, basename='journal_entry')
router.register('general_ledger', GeneralLedgerViewSet, basename='general_ledger')
