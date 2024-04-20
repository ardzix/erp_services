from django.contrib import admin
from libs.admin import ApproveRejectMixin, BaseAdmin
from ..models import UserProfile, Contact, Brand

@admin.register(UserProfile)
class UserProfileAdmin(BaseAdmin):
    list_display = ['profile_picture', 'bio', 'contact_number', 'owned_by_email']
    list_filter = []
    search_fields = ['owned_by__email']
    fields = ['owned_by', 'profile_picture', 'bio', 'contact_number']

    def owned_by_email(self, obj):
        return obj.owned_by.email
    owned_by_email.short_description = 'Owned by'

@admin.register(Contact)
class ContactAdmin(BaseAdmin):
    list_display = ['id32', 'name', 'address', 'contact_number']
    list_filter = []
    search_fields = ['name']
    fields = ['id32', 'name', 'address', 'contact_number']


@admin.register(Brand)
class BrandProfileAdmin(BaseAdmin):
    list_display = ['name', 'address', 'contact_number']
    list_filter = []
    search_fields = ['name']
    fields = ['name', 'address', 'contact_number', 'description']
