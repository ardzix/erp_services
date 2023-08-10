from django.db import models
from django.utils.translation import gettext_lazy as _

from libs.base_model import BaseModelGeneric
from common.models import File


class UserProfile(BaseModelGeneric):
    profile_picture = models.ForeignKey(
        File, blank=True, null=True, on_delete=models.CASCADE, help_text=_("Profile picture for the user"))
    bio = models.TextField(help_text=_(
        "Biographical information about the user"))
    contact_number = models.CharField(
        max_length=15, help_text=_("User's contact number"))
    # Add any other user-specific fields you need

    def __str__(self, *args, **kwargs):
        # Assuming owned_by is a field in BaseModelGeneric or inherited model
        return self.owned_by.email

    class Meta:
        verbose_name = _("User Profile")
        verbose_name_plural = _("User Profiles")


class CompanyProfile(BaseModelGeneric):
    company_name = models.CharField(
        max_length=100, help_text=_("Name of the company"))
    address = models.TextField(help_text=_("Company's address"))
    contact_number = models.CharField(
        max_length=15, help_text=_("Company's contact number"))
    # Add any other company-specific fields you need

    def __str__(self, *args, **kwargs):
        return self.company_name

    class Meta:
        verbose_name = _("Company Profile")
        verbose_name_plural = _("Company Profiles")


class Brand(BaseModelGeneric):
    company = models.ForeignKey(CompanyProfile, on_delete=models.SET_NULL,
                                blank=True, null=True, help_text=_("Company to which the brand belongs"))
    name = models.CharField(
        max_length=100, help_text=_("Enter the brand name"))
    description = models.TextField(
        blank=True, help_text=_("Enter the brand description"))

    def __str__(self):
        return _("Brand #{brand_id} - {brand_name}").format(brand_id=self.id32, brand_name=self.name)

    class Meta:
        verbose_name = _("Brand")
        verbose_name_plural = _("Brands")
