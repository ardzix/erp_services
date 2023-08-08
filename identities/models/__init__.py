from django.db import models
from django.utils.translation import gettext_lazy as _

from libs.base_model import BaseModelGeneric
from common.models import File

class UserProfile(BaseModelGeneric):
    profile_picture = models.ForeignKey(File, blank=True, null=True, on_delete=models.CASCADE)
    bio = models.TextField()
    contact_number = models.CharField(max_length=15)
    # Add any other user-specific fields you need

    def __str__(self, *args, **kwargs):
        return self.owned_by.email

    class Meta:
        verbose_name = _("User Profile")
        verbose_name_plural = _("User Profiles")


class CompanyProfile(BaseModelGeneric):
    company_name = models.CharField(max_length=100)
    address = models.TextField()
    contact_number = models.CharField(max_length=15)
    # Add any other company-specific fields you need

    def __str__(self, *args, **kwargs):
        return self.company_name

    class Meta:
        verbose_name = _("Company Profile")
        verbose_name_plural = _("Company Profiles")


class Brand(BaseModelGeneric):
    company = models.ForeignKey(CompanyProfile, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=100, help_text=_("Enter the brand name"))
    description = models.TextField(blank=True, help_text=_("Enter the brand description"))

    def __str__(self):
        return f"Brand #{self.id32} - {self.name}"

    class Meta:
        verbose_name = _("Brand")
        verbose_name_plural = _("Brands")