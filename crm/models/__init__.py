from django.db import models
from django.utils.translation import gettext_lazy as _
from libs.base_model import BaseModelGeneric

class Lead(BaseModelGeneric):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    source = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=[
            ('new', 'New'),
            ('contacted', 'Contacted'),
            ('qualified', 'Qualified'),
            ('converted', 'Converted'),
            ('closed', 'Closed'),
        ],
        default='new'
    )
    # Add any other fields specific to your lead model

    def __str__(self):
        return f"Lead #{self.id62} - {self.name}"

    class Meta:
        verbose_name = _("Lead")
        verbose_name_plural = _("Leads")


class Contact(BaseModelGeneric):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    # Add any other fields specific to your contact model

    def __str__(self):
        return f"Contact #{self.id62} - {self.first_name} {self.last_name}"

    class Meta:
        verbose_name = _("Contact")
        verbose_name_plural = _("Contacts")


class Account(BaseModelGeneric):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    # Add any other fields specific to your account model

    def __str__(self):
        return f"Account #{self.id62} - {self.name}"

    class Meta:
        verbose_name = _("Account")
        verbose_name_plural = _("Accounts")


class Opportunity(BaseModelGeneric):
    name = models.CharField(max_length=100)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    probability = models.PositiveIntegerField()
    stage = models.CharField(
        max_length=100,
        choices=[
            ('prospect', 'Prospect'),
            ('qualified', 'Qualified'),
            ('proposal', 'Proposal'),
            ('negotiation', 'Negotiation'),
            ('closed', 'Closed'),
        ]
    )
    # Add any other fields specific to your opportunity model

    def __str__(self):
        return f"Opportunity #{self.id62} - {self.name}"

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

    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    due_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('planned', 'Planned'),
            ('completed', 'Completed'),
            ('canceled', 'Canceled'),
        ],
        default='planned'
    )
    # Add any other fields specific to your activity model

    def __str__(self):
        return f"Activity #{self.id62} - {self.get_type_display()}"

    class Meta:
        verbose_name = _("Activity")
        verbose_name_plural = _("Activities")
