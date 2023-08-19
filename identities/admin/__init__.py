from django.contrib import admin
from libs.admin import ApproveRejectMixin, BaseAdmin
from ..models import UserProfile, CompanyProfile, Brand

@admin.register(UserProfile)
class UserProfileAdmin(BaseAdmin):
    list_display = ['profile_picture', 'bio', 'contact_number', 'owned_by_email']
    list_filter = []
    search_fields = ['owned_by__email']
    fields = ['owned_by', 'profile_picture', 'bio', 'contact_number']

    def owned_by_email(self, obj):
        return obj.owned_by.email
    owned_by_email.short_description = 'Owned by'

@admin.register(CompanyProfile)
class CompanyProfileAdmin(BaseAdmin):
    list_display = ['id32', 'company_name', 'address', 'contact_number']
    list_filter = []
    search_fields = ['owned_by__email']
    fields = ['id32', 'owned_by', 'company_name', 'address', 'contact_number']

    def owned_by_email(self, obj):
        return obj.owned_by.email
    owned_by_email.short_description = 'Owned by'

@admin.register(Brand)
class BrandProfileAdmin(BaseAdmin):
    list_display = ['company', 'name']
    list_filter = []
    search_fields = ['name', 'company__name']
    fields = ['company', 'name', 'description']
