from django.contrib import admin
from libs.admin import ApproveRejectMixin, BaseAdmin
from ..models import Lead, Contact, Account, Opportunity, Activity

@admin.register(Lead)
class LeadAdmin(BaseAdmin):
    list_display = ['name', 'email', 'phone_number', 'status']
    list_filter = ['status']

@admin.register(Contact)
class ContactAdmin(BaseAdmin):
    list_display = ['first_name', 'last_name', 'email', 'phone_number']

@admin.register(Account)
class AccountAdmin(BaseAdmin):
    list_display = ['name', 'email', 'phone_number']

@admin.register(Opportunity)
class OpportunityAdmin(BaseAdmin):
    list_display = ['name', 'account', 'value', 'stage']
    list_filter = ['stage']

@admin.register(Activity)
class ActivityAdmin(BaseAdmin):
    list_display = ['type', 'due_date', 'status']
    list_filter = ['type', 'status']
