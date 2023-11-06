from django.contrib import admin
from libs.admin import BaseAdmin

# Register your models here.
from ..models import File, Configuration



class FileAdmin(BaseAdmin):
    list_display = ["name", "file", "created_at"]
    fields = ["name", "file", "description"]

    def save_model(self, request, obj, form, change):
        if not change:  # Only set the created_by field if the object is being created
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

admin.site.register(File, FileAdmin)


@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')
    search_fields = ('key',)