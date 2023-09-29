from django.contrib import admin, messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.core.exceptions import ValidationError
from reversion.admin import VersionAdmin
from leaflet.admin import LeafletGeoAdmin


class ApproveRejectMixin:
    change_form_template = 'admin/mymodel_change_form.html'
    readonly_fields = ['approved_by', 'approved_at', 'unapproved_by', 'unapproved_at']

    def approve(self, request, obj):
        obj.approved_by = request.user
        obj.approved_at = timezone.now()
        obj.unapproved_by = None
        obj.unapproved_at = None
        obj.save()
        return HttpResponseRedirect(reverse('admin:purchasing_purchaseorder_change', args=(obj.id,)))

    def reject(self, request, obj):
        obj.approved_by = None
        obj.approved_at = None
        obj.unapproved_by = request.user
        obj.unapproved_at = timezone.now()
        obj.save()
        return HttpResponseRedirect(reverse('admin:purchasing_purchaseorder_change', args=(obj.id,)))

    def get_extra_context(self, request, obj):
        extra_context = {}

        # Check if the Purchase Order is already approved
        is_approved = obj.approved_by is not None

        if is_approved:
            # Purchase Order is already approved, remove the "Save" and "Save and add another" buttons
            extra_context['show_save'] = False
            extra_context['show_save_and_continue'] = False
            extra_context['show_save_and_add_another'] = False
        else:
            # Purchase Order is not yet approved, add the "Approve" and "Reject" buttons
            extra_context['show_approve'] = True
            extra_context['show_save_and_continue'] = True
            extra_context['show_reject'] = True

        return extra_context

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if extra_context is None:
            extra_context = {}

        # Check if the Purchase Order is already approved
        obj = self.get_object(request, object_id)
        print(request, object_id, self, obj)
        is_approved = obj.approved_by is not None

        if is_approved:
            # Purchase Order is already approved, remove the "Save" and "Save and add another" buttons
            extra_context['show_save'] = False
            extra_context['show_save_and_continue'] = False
            extra_context['show_save_and_add_another'] = False
        else:
            # Purchase Order is not yet approved, add the "Approve" and "Reject" buttons
            extra_context['show_approve'] = True
            extra_context['show_save_and_continue'] = True
            extra_context['show_reject'] = True

        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def response_change(self, request, obj):

        if "_approve" in request.POST:
            # Approve button clicked, redirect to the change view to update the approved_by and approved_at fields
            obj.approved_by = request.user
            obj.approved_at = timezone.now()
            obj.unapproved_by = None
            obj.unapproved_at = None
            obj.save()
            return HttpResponseRedirect(reverse(f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change', args=(obj.id,)))

        if "_reject" in request.POST:
            # Reject button clicked, redirect to the change view to update the approved_by and approved_at fields
            obj.approved_by = None
            obj.approved_at = None
            obj.unapproved_by = request.user
            obj.unapproved_at = timezone.now()
            obj.save()
            return HttpResponseRedirect(reverse(f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change', args=(obj.id,)))

        return super().response_change(request, obj)
    
class BaseAdmin(LeafletGeoAdmin, VersionAdmin):

    def message_user(self, request, message, level=messages.ERROR, extra_tags='', fail_silently=False):
        if isinstance(message, ValidationError):
            level = messages.ERROR
        super().message_user(request, message, level, extra_tags, fail_silently)