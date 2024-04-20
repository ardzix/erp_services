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


class Contact(BaseModelGeneric):
    name = models.CharField(
        max_length=100, help_text=_("Name of the contact"))
    address = models.TextField(help_text=_("Contact's address"))
    contact_number = models.CharField(
        max_length=15, help_text=_("Contact's contact number"))
    role = models.CharField(max_length=25, default="Contact")

    def __str__(self, *args, **kwargs):
        return f'{self.role}: {self.name}'

    class Meta:
        verbose_name = _("Company Profile")
        verbose_name_plural = _("Company Profiles")


class Brand(Contact):
    description = models.TextField(
        blank=True, help_text=_("Enter the brand description"))

    def __str__(self):
        return _("Brand #{brand_id} - {brand_name}").format(brand_id=self.id32, brand_name=self.name)
    
    def save(self, *args, **kwargs):
        self.role = "Brand"
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Brand")
        verbose_name_plural = _("Brands")