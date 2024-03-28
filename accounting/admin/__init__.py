from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from libs.admin import ApproveRejectMixin, BaseAdmin
from ..models import Category, Account, Transaction, JournalEntry, GeneralLedger, FinancialStatement, FinancialEntry


class ParentCategoryFilter(SimpleListFilter):
    title = 'parent'  # or use _('parent') for i18n
    parameter_name = 'parent'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each tuple is the coded value
        for the option that will appear in the URL query. The second element is the
        human-readable name for the option that will appear in the right sidebar.
        """
        # Customize this queryset to list only the parents you want to filter by
        parents = Category.objects.filter(
            parent__isnull=True).order_by('number')
        return [(parent.id, f'{parent.number} {parent.name}') for parent in parents]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value provided in the query string
        and retrievable via `self.value()`.
        """
        if self.value():
            # Filter the queryset based on the selected parent category
            return queryset.filter(parent__id=self.value())
        return queryset
class ParentCategoryAccountFilter(ParentCategoryFilter):

    def queryset(self, request, queryset):
        if self.value():
            # Filter the queryset based on the selected parent category
            return queryset.filter(category__parent__id=self.value())
        return queryset


class CategoryFilter(SimpleListFilter):
    title = 'category'  # or use _('parent') for i18n
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        # Customize this queryset to list only the parents you want to filter by
        categories = Category.objects.filter(
            parent__isnull=False).order_by('number')
        return [(category.id, f'{category.number} {category.name}') for category in categories]

    def queryset(self, request, queryset):
        if self.value():
            # Filter the queryset based on the selected parent category
            return queryset.filter(category__id=self.value())
        return queryset




@admin.register(Category)
class CategoryAdmin(BaseAdmin):
    list_display = ['number', 'name']
    list_filter = [ParentCategoryFilter]


@admin.register(Account)
class AccountAdmin(BaseAdmin):
    list_display = ['number', 'name']
    list_filter = [ParentCategoryAccountFilter, CategoryFilter]




class JournalEntryInline(admin.TabularInline):
    model = JournalEntry
    extra = 1
    fields = ['account', 'journal', 'amount', 'debit_credit', 'is_allocation']
    raw_id_fields = ['account']
    verbose_name_plural = _("Allocations")

@admin.register(Transaction)
class TransactionAdmin(BaseAdmin):
    list_display = ['account', 'transaction_date',
                    'amount', 'created_at']
    fields = ['account', 'transaction_date',
                    'origin', 'origin_id','origin_type', 
                    'amount', 'description', 'created_at']
    list_filter = ['account','transaction_type']
    raw_id_fields = ['account']
    readonly_fields = ['origin']
    inlines = [JournalEntryInline]


@admin.register(JournalEntry)
class JournalEntryAdmin(BaseAdmin):
    list_display = ['transaction', 'journal',
                    'amount', 'debit_credit', 'created_at']
    fields = ['transaction', 'journal', 'account',
                    'amount', 'debit_credit', 'is_allocation']
    
    raw_id_fields = ['transaction', 'account']
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
