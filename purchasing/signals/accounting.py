from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from libs.utils import get_config_value
from purchasing.models import PurchaseOrderPayment
from accounting.models import ModuleAccount, JournalEntry, Transaction, TransactionCategory
from accounting.helpers.constant import *


@receiver(post_save, sender=PurchaseOrderPayment)
def commit_transaction_on_order_received(sender, instance, created, **kwargs): 
    pass