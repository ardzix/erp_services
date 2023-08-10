from django.db import models
from django.utils.translation import gettext_lazy as _

from libs.base_model import BaseModelGeneric

class Lead(BaseModelGeneric):
    name = models.CharField(max_length=100, help_text=_("The name of the lead"))
    email = models.EmailField(help_text=_("The email of the lead"))
    phone_number = models.CharField(max_length=20, help_text=_("The phone number of the lead"))
    source = models.CharField(max_length=100, help_text=_("The source from where the lead originated"))
    status = models.CharField(
        max_length=20,
        choices=[
            ('new', 'New'),
            ('contacted', 'Contacted'),
            ('qualified', 'Qualified'),
            ('converted', 'Converted'),
            ('closed', 'Closed'),
        ],
        default='new',
        help_text=_("The status of the lead")
    )

    def __str__(self):
        return _("Lead #{lead_id} - {lead_name}").format(lead_id=self.id32, lead_name=self.name)

    class Meta:
        verbose_name = _("Lead")
        verbose_name_plural = _("Leads")

class Contact(BaseModelGeneric):
    first_name = models.CharField(max_length=100, help_text=_("The first name of the contact"))
    last_name = models.CharField(max_length=100, help_text=_("The last name of the contact"))
    email = models.EmailField(help_text=_("The email of the contact"))
    phone_number = models.CharField(max_length=20, help_text=_("The phone number of the contact"))

    def __str__(self):
        return _("Contact #{contact_id} - {contact_first_name} {contact_last_name}").format(contact_id=self.id32, contact_first_name=self.first_name, contact_last_name=self.last_name)

    class Meta:
        verbose_name = _("Contact")
        verbose_name_plural = _("Contacts")

class Account(BaseModelGeneric):
    name = models.CharField(max_length=100, help_text=_("The name of the account"))
    email = models.EmailField(help_text=_("The email of the account"))
    phone_number = models.CharField(max_length=20, help_text=_("The phone number of the account"))
    address = models.TextField(help_text=_("The address of the account"))

    def __str__(self):
        return _("Account #{account_id} - {account_name}").format(account_id=self.id32, account_name=self.name)

    class Meta:
        verbose_name = _("Account")
        verbose_name_plural = _("Accounts")

class Opportunity(BaseModelGeneric):
    name = models.CharField(max_length=100, help_text=_("The name of the opportunity"))
    account = models.ForeignKey(Account, on_delete=models.CASCADE, help_text=_("The associated account of the opportunity"))
    value = models.DecimalField(max_digits=10, decimal_places=2, help_text=_("The value of the opportunity"))
    probability = models.PositiveIntegerField(help_text=_("The probability percentage of closing the opportunity"))
    stage = models.CharField(
        max_length=100,
        choices=[
            ('prospect', 'Prospect'),
            ('qualified', 'Qualified'),
            ('proposal', 'Proposal'),
            ('negotiation', 'Negotiation'),
            ('closed', 'Closed'),
        ],
        help_text=_("The stage of the opportunity")
    )

    def __str__(self):
        return _("Opportunity #{opportunity_id} - {opportunity_name}").format(opportunity_id=self.id32, opportunity_name=self.name)

    class Meta:
        verbose_name = _("Opportunity")
        verbose_name_plural = _("Opportunities")

class Activity(BaseModelGeneric):
    TYPE_CHOICES = [
        ('call', 'Call'),
        ('meeting', 'Meeting'),
        ('email', 'Email'),
        ('task', 'Task'),
        ('other', 'Other'),
    ]

    type = models.CharField(max_length=20, choices=TYPE_CHOICES, help_text=_("The type of the activity"))
    due_date = models.DateField(help_text=_("The due date of the activity"))
    status = models.CharField(
        max_length=20,
        choices=[
            ('planned', 'Planned'),
            ('completed', 'Completed'),
            ('canceled', 'Canceled'),
        ],
        default='planned',
        help_text=_("The status of the activity")
    )

    def __str__(self):
        return _("Activity #{activity_id} - {activity_type}").format(activity_id=self.id32, activity_type=self.get_type_display())

    class Meta:
        verbose_name = _("Activity")
        verbose_name_plural = _("Activities")
