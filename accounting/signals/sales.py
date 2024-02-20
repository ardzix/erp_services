from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from sales.models import Invoice, SalesPayment
from ..helpers.transaction import create_transaction, create_journal_entry
from ..helpers.constant import *


@receiver(post_save, sender=Invoice)
def record_sales_order_transaction(sender, instance, created, **kwargs):
    """
    Record a transaction for a sales order, including tax calculations.
    """

    subtotal = instance.subtotal

    if subtotal <= 0:
        return

    tax_amount = instance.vat_amount

    transaction = create_transaction(SALES_ACCOUNT, subtotal, SALE, description=_(
        f"Sales of #{instance.order.id32} (Inv #{instance.id32})"), external_id32=instance.order.id32)
    create_journal_entry(transaction, subtotal, AR_ACCOUNT, DEBIT)
    create_journal_entry(transaction, subtotal, SALES_ACCOUNT, CREDIT)

    if tax_amount > 0:
        vat_transaction = create_transaction(TAX_LIAB_ACCOUNT, tax_amount, TAX_PAYMENT, description=_(
            f"VAT of Sales #{instance.order.id32} (Inv #{instance.id32})"))
        create_journal_entry(vat_transaction, tax_amount, AR_ACCOUNT, DEBIT)
        create_journal_entry(vat_transaction, tax_amount, TAX_LIAB_ACCOUNT, CREDIT)


@receiver(pre_save, sender=SalesPayment)
def check_payment_status_before(sender, instance, **kwargs):
    """
    Logs the StockMovement's current status before any change is made.
    """
    payment = SalesPayment.objects.filter(pk=instance.pk).last()
    instance.status_before = payment.status if payment else SalesPayment.PENDING


@receiver(post_save, sender=SalesPayment)
def record_payment_transaction(sender, instance, **kwargs):
    if instance.status == SalesPayment.SETTLEMENT and instance.status_before != SalesPayment.SETTLEMENT:
        payment_difference = instance.amount - instance.invoice.total
        transaction = create_transaction(CASH_ACCOUNT, instance.amount, INCOME, description=_(
            f"Receipt of payment #{instance.id32} for Invoice #{instance.invoice.id32})"))
        create_journal_entry(transaction, instance.amount, CASH_ACCOUNT, DEBIT)
        create_journal_entry(transaction, instance.invoice.total, AR_ACCOUNT, CREDIT)
        if payment_difference !=0:
            create_journal_entry(transaction, payment_difference, ROUNDING_ACCOUNT, CREDIT)
