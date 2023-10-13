from django.db.models.signals import pre_save, post_save, pre_delete
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db import models
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from inventory.models import StockMovement, Product, StockMovementItem
from ..scripts import generate_invoice_pdf_for_instance
from ..models import (
    OrderItem,
    SalesOrder,
    Customer,
    Trip,
    CustomerVisit,
    CustomerVisitReport,
    TripCustomer,
    Invoice,
    SalesPayment
)


@receiver(pre_save, sender=OrderItem)
def update_product_quantity(sender, instance, **kwargs):
    if instance.pk:  # Only for existing OrderItem instances
        order_item = OrderItem.objects.get(pk=instance.pk)
        old_quantity = order_item.quantity
        quantity_diff = instance.quantity - old_quantity
        Product.objects.filter(pk=instance.product.pk).update(quantity=models.F(
            'quantity') - quantity_diff, updated_by_id=instance.updated_by_id)
        if quantity_diff != 0 and instance.order.stock_movement:
            smi, created = StockMovementItem.objects.get_or_create(
                product_id=instance.product.pk,
                stock_movement=instance.order.stock_movement,
                created_by=order_item.created_by
            )
            smi.quantity = quantity_diff
            smi.unit = instance.unit
            smi.save()


@receiver(post_save, sender=OrderItem)
def update_product_quantity(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        quantity = instance.quantity * product.purchasing_unit.conversion_to_top_level()
        product.quantity -= quantity
        product.updated_by = instance.created_by
        product.save()


@receiver(pre_save, sender=SalesOrder)
def check_salesorder_before_approved(sender, instance, **kwargs):
    instance.approved_before = False
    instance.unapproved_before = False
    so_before = SalesOrder.objects.filter(pk=instance.pk).last()
    if so_before:
        instance.approved_before = True if so_before.approved_at and so_before.approved_by else False
        instance.unapproved_before = True if so_before.unapproved_at and so_before.unapproved_by else False


@receiver(post_save, sender=SalesOrder)
def create_stock_movement(sender, instance, **kwargs):
    if not instance.approved_before and instance.approved_at:
        sm = StockMovement.objects.create(
            destination_type=ContentType.objects.get_for_model(Customer),
            destination_id=instance.customer.id,
            created_by=instance.updated_by if instance.updated_by else instance.created_by
        )
        instance.stock_movement = sm
        instance.save()
        for item in OrderItem.objects.filter(order=instance).all():
            smi, created = StockMovementItem.objects.get_or_create(
                product_id=item.product.pk,
                stock_movement=instance.stock_movement,
                created_by=item.created_by
            )
            sales_unit = item.product.sales_unit
            stock_unit = item.product.stock_unit
            quantity = abs(item.quantity) * sales_unit.conversion_to_top_level() / \
                stock_unit.conversion_to_top_level()
            smi.quantity = quantity
            smi.unit = stock_unit
            smi.save()
    if not instance.unapproved_before and instance.unapproved_at:
        sm = instance.stock_movement
        if sm.status <= 4:
            sm.delete()


@receiver(post_save, sender=OrderItem)
def create_stock_movement_item(sender, instance, created, **kwargs):
    if created and instance.order.stock_movement:
        smi, created = StockMovementItem.objects.get_or_create(
            product=instance.product,
            stock_movement=instance.order.stock_movement,
            created_by=instance.created_by
        )
        smi.quantity = instance.quantity
        smi.unit = instance.unit
        smi.save()


@receiver(pre_delete, sender=OrderItem)
def restore_product_quantity(sender, instance, **kwargs):
    Product.objects.filter(pk=instance.product.pk).update(
        quantity=models.F('quantity') + instance.quantity)


@receiver(post_save, sender=Trip)
def populate_trip_customer_from_template(sender, instance, created, **kwargs):
    if created:
        for trip_customer in TripCustomer.objects.filter(template=instance.template):
            CustomerVisit.objects.create(
                trip=instance,
                customer=trip_customer.customer,
                status=Trip.WAITING,
                order=trip_customer.order,
                created_by=instance.created_by
            )


@receiver(post_save, sender=CustomerVisit)
def generate_canvasing_report(sender, instance, **kwargs):
    if instance.status in [Trip.COMPLETED, Trip.SKIPPED]:
        # If there's an existing report, just update. Else, create a new one.
        report, created = CustomerVisitReport.objects.get_or_create(
            customer_visit=instance,
            created_by = instance.created_by,
            defaults={
                "trip": instance.trip,
                "customer": instance.customer,
                "status": instance.status,
            }
        )
        if not created:
            report.status = instance.status
            report.save()

        # Add sold products if a SalesOrder is generated
        if instance.sales_order:
            report.sold_products.set(instance.sales_order.order_items.all())


@receiver(post_save, sender=CustomerVisit)
def update_canvasing_trip_status(sender, instance, **kwargs):
    visits = CustomerVisit.objects.filter(trip=instance.trip)
    trip_count = visits.count()
    completed_count = visits.filter(status__in=[Trip.COMPLETED, Trip.SKIPPED]).count()
    if trip_count == completed_count:
        canvasing_trip = instance.trip
        canvasing_trip.status = Trip.COMPLETED
        canvasing_trip.updated_by = instance.updated_by
        canvasing_trip.save()


@receiver(pre_save, sender=SalesOrder)
def update_order_status(sender, instance, **kwargs):
    # Get the current state of the object from the database
    try:
        db_instance = SalesOrder.objects.get(pk=instance.pk)
    except SalesOrder.DoesNotExist:
        # The instance is not yet in the database (likely being created)
        db_instance = None

    # Check if the approved_at field has changed and unapproved_at has not
    if (not db_instance or instance.approved_at != db_instance.approved_at) and instance.approved_at and not instance.unapproved_at:
        instance.status = SalesOrder.APPROVED
    # Check if the unapproved_at field has changed
    elif (not db_instance or instance.unapproved_at != db_instance.unapproved_at) and instance.unapproved_at and not instance.approved_at:
        instance.status = SalesOrder.REJECTED


# Trip progress rules~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 1. Trip status cannot be changed if its vehicle warehouse is null.
@receiver(pre_save, sender=Trip)
def ensure_trip_vehicle_has_warehouse(sender, instance, **kwargs):
    if instance.status != Trip.WAITING:
        # If a trip vehicle is not specified
        if not instance.vehicle:
            raise ValidationError(_('Trip must have an associated vehicle to start the trip.'))
        # If a trip vehicle is specified but doesn't have a warehouse
        if instance.vehicle and not instance.vehicle.warehouse:
            raise ValidationError(_('Vehicle must have an associated warehouse to start the trip.'))

# 2. CustomerVisit status can only be changed if Trip status is ON_PROGRESS.
@receiver(pre_save, sender=CustomerVisit)
def ensure_trip_status_on_progress(sender, instance, **kwargs):
    if instance.status != Trip.WAITING and instance.trip.status != Trip.ON_PROGRESS:
        raise ValidationError(_('CustomerVisit status can only be changed if associated Trip status is ON_PROGRESS.'))

# 3. CustomerVisit status cannot be changed to COMPLETED if CustomerVisit sales_order and visit_evidence is null.
@receiver(pre_save, sender=CustomerVisit)
def ensure_customer_visit_sales_order_for_completion(sender, instance, **kwargs):
    if instance.status == Trip.COMPLETED:
        if not all([instance.sales_order, instance.visit_evidence]):
            raise ValidationError(_('CustomerVisit status cannot be set to COMPLETED if sales_order and visit_evidence are null.'))

    
# 4. CustomerVisit status cannot be changed to SKIPPED if notes, visit_evidence, or signature is null.
@receiver(pre_save, sender=CustomerVisit)
def ensure_fields_present_when_skipped(sender, instance, **kwargs):
    if instance.status == Trip.SKIPPED:
        if not all([instance.notes, instance.visit_evidence, instance.signature]):
            raise ValidationError(_('CustomerVisit status cannot be set to SKIPPED if notes, visit_evidence, or signature are null.'))


# 5. If CustomerVisit status is changed to COMPLETED and trip type is CANVASING, check SalesOrder, Invoice and Payment.
@receiver(pre_save, sender=CustomerVisit)
def check_canvasing_requirements(sender, instance, **kwargs):
    if instance.status == Trip.COMPLETED and instance.trip.type == Trip.CANVASING:
        if instance.sales_order.status == SalesOrder.DRAFT:
            raise ValidationError("Sales Order is in DRAFT status. Cannot set the Customer Visit to COMPLETED.")

        try:
            invoice = instance.sales_order.invoice
        except Invoice.DoesNotExist:
            raise ValidationError("The associated Sales Order doesn't have an invoice.")

        payment = SalesPayment.objects.filter(invoice=invoice).last()
        if not payment:
            raise ValidationError("The associated invoice doesn't have a payment.")

        if payment.status not in [SalesPayment.CAPTURE, SalesPayment.SETTLEMENT]:
            raise ValidationError("The payment status for the associated invoice is neither CAPTURE nor SETTLEMENT.")

# 6. If CustomerVisit status is changed to COMPLETED and trip type is TAKING_ORDER, check SalesOrder status.
@receiver(pre_save, sender=CustomerVisit)
def check_taking_order_requirements(sender, instance, **kwargs):
    if instance.status == Trip.COMPLETED and instance.trip.type == Trip.TAKING_ORDER:
        if instance.sales_order.status == SalesOrder.DRAFT:
            raise ValidationError("Sales Order is in DRAFT status. Cannot set the Customer Visit to COMPLETED.")

# Sales process singnalling ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@receiver(post_save, sender=SalesOrder)
def create_invoice_on_order_submit(sender, instance, **kwargs):
    if instance.status == SalesOrder.SUBMITTED:
        # Check if the SalesOrder doesn't already have an associated Invoice.
        # This ensures we don't generate duplicate invoices.
        if not Invoice.objects.filter(order=instance).exists():
            Invoice.objects.create(
                order=instance,
                invoice_date=timezone.now().date(),
                # Any other necessary fields can be populated here.
            )

@receiver(post_save, sender=CustomerVisit)
def handle_customer_visit_completed(sender, instance, **kwargs):
    sales_order = instance.sales_order
    # Check if the sales order is completed and call the approve method
    if instance.status == Trip.COMPLETED:
        if instance.trip.type == Trip.CANVASING:
            sales_order.status = 'completed'
        sales_order.approve(user=instance.trip.updated_by)  # assuming the approve method updates and saves the model

        # Get content types for 'customer' and 'warehouse'
        customer_content_type = ContentType.objects.get(model='customer')
        warehouse_content_type = ContentType.objects.get(model='warehouse')
        
        # Get the stock movement with the specified destination_type and destination_id
        stock_movements = StockMovement.objects.filter(
            destination_type=customer_content_type, 
            destination_id=sales_order.customer.id
        )
        
        # Update origin_type and origin_id for the fetched stock movements
        for stock_movement in stock_movements:
            stock_movement.origin_type = warehouse_content_type
            stock_movement.origin_id = instance.trip.vehicle.warehouse.id
            if instance.trip.type == Trip.CANVASING:
                stock_movement.status = 'delivered'
                stock_movement.movement_date = instance.updated_at
            if instance.trip.type == Trip.TAKING_ORDER:
                stock_movement.status = 'requested'
            stock_movement.save()

@receiver(post_save, sender=SalesOrder)
def sales_order_saved(sender, instance, **kwargs):
    # Generate PDF only if there are order items and the PDF hasn't been generated yet.
    if not instance.invoice_pdf_generated and instance.order_items.exists():
        generate_invoice_pdf_for_instance(instance)
        instance.invoice_pdf_generated = True
        instance.save()

@receiver(post_save, sender=OrderItem)
def order_item_saved(sender, instance, **kwargs):
    # If an OrderItem gets saved, we'll check its related SalesOrder to see if we need to generate the PDF.
    order = instance.order
    if not order.invoice_pdf_generated:
        generate_invoice_pdf_for_instance(order)
        order.invoice_pdf_generated = True
        order.save()