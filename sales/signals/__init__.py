from django.db.models.signals import pre_save, post_save, pre_delete
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db import models
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from inventory.models import StockMovement, Product, StockMovementItem, Warehouse, WarehouseStock
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

# Table of Content
# 1. update_product_quantity: Adjusts the product quantity when an OrderItem's quantity changes.
# 2. deduct_product_quantity: Deducts the product's quantity when a new OrderItem is created.
# 3. check_salesorder_before_approved: Checks if a SalesOrder was previously approved or unapproved and sets flags accordingly.
# 4. create_stock_movement: Creates a StockMovement entry when a SalesOrder is approved.
# 5. create_stock_movement_item: Creates a StockMovementItem entry when a new OrderItem is created and the order has associated stock movement.
# 6. restore_product_quantity: Restores the product's quantity when an OrderItem is deleted.
# 7. populate_trip_customer_from_template: Populates the trip's customers from a template when a new Trip instance is created.
# 8. generate_canvasing_report: Generates or updates a CustomerVisitReport when a CustomerVisit's status is either completed or skipped.
# 9. update_canvasing_trip_status: Updates the associated canvasing trip's status to completed if all associated CustomerVisits are completed or skipped.
# 10. update_order_status: Before saving a `SalesOrder`, this signal checks if the approval status of the order has changed.
# 11. create_invoice_on_order_submit: After saving a `SalesOrder`, if the order's status is 'SUBMITTED' and there isn't already an associated invoice,this signal creates a new `Invoice` entry associated with the given order.
# 12. handle_customer_visit_completed: Handle logic of if customer visit is completed
# 13. sales_order_saved: Generate invoice PDF if `SalesOrder` is saved
# 14. order_item_saved: Generate invoice PDF if `OrderItem` is saved
# 15. set_sales_order_to_processing: Associate SalesOrder's status is set to 'PROCESSING' and its approve() method is called
# 16. set_sales_order_to_completed: Set the associated CustomerVisit's SalesOrder's status is set to 'COMPLETED'


@receiver(pre_save, sender=OrderItem)
def update_product_quantity(sender, instance, **kwargs):
    """
    Adjusts the product quantity when an OrderItem's quantity changes.
    Also updates related StockMovementItem if the order has associated stock movement.
    """
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
def deduct_product_quantity(sender, instance, created, **kwargs):
    """
    Deducts the product's quantity when a new OrderItem is created.
    """
    if created:
        product = instance.product
        quantity = instance.quantity * product.purchasing_unit.conversion_to_top_level()
        product.quantity -= quantity
        product.updated_by = instance.created_by
        product.save()


@receiver(pre_save, sender=SalesOrder)
def check_salesorder_before_approved(sender, instance, **kwargs):
    """
    Checks if a SalesOrder was previously approved or unapproved and sets flags accordingly.
    """
    instance.approved_before = False
    instance.unapproved_before = False
    so_before = SalesOrder.objects.filter(pk=instance.pk).last()
    if so_before:
        instance.approved_before = True if so_before.approved_at and so_before.approved_by else False
        instance.unapproved_before = True if so_before.unapproved_at and so_before.unapproved_by else False


@receiver(post_save, sender=SalesOrder)
def create_stock_movement(sender, instance, **kwargs):
    """
    Creates a StockMovement entry when a SalesOrder is approved.
    Deletes the StockMovement if a SalesOrder is unapproved and its status is below or equal to 4.
    """
    if not instance.approved_before and instance.approved_at:
        sm = StockMovement.objects.create(
            destination_type=ContentType.objects.get_for_model(Customer),
            destination_id=instance.customer.id,
            creator_type=ContentType.objects.get_for_model(SalesOrder),
            creator_id=instance.id,
        )
        instance.stock_movement = sm
        visit = CustomerVisit.objects.filter(sales_order=instance).last()
        if visit and visit.trip and visit.trip.vehicle and visit.trip.vehicle.warehouse:
            sm.origin_type = ContentType.objects.get_for_model(Warehouse)
            sm.origin_id = visit.trip.vehicle.warehouse.id
            instance.type = visit.trip.type
        instance.save()
        sm.save()

        for item in OrderItem.objects.filter(order=instance).all():
            smi, created = StockMovementItem.objects.get_or_create(
                product_id=item.product.pk,
                stock_movement=instance.stock_movement,
                created_by=item.created_by
            )
            smi.quantity = item.quantity
            smi.unit = item.unit
            smi.save()

    if not instance.unapproved_before and instance.unapproved_at:
        sm = instance.stock_movement
        if sm and sm.status <= 4:
            sm.delete()


@receiver(post_save, sender=OrderItem)
def create_stock_movement_item(sender, instance, created, **kwargs):
    """
    Creates a StockMovementItem entry when a new OrderItem is created and the order has associated stock movement.
    """
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
    """
    Restores the product's quantity when an OrderItem is deleted.
    """
    Product.objects.filter(pk=instance.product.pk).update(
        quantity=models.F('quantity') + instance.quantity)


@receiver(post_save, sender=Trip)
def populate_trip_customer_from_template(sender, instance, created, **kwargs):
    """
    Populates the trip's customers from a template when a new Trip instance is created.
    """
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
    """
    Generates or updates a CustomerVisitReport when a CustomerVisit's status is either completed or skipped.
    Adds sold products to the report if there's an associated SalesOrder.
    """
    if instance.status in [Trip.COMPLETED, Trip.SKIPPED]:
        # If there's an existing report, just update. Else, create a new one.
        report, created = CustomerVisitReport.objects.get_or_create(
            customer_visit=instance,
            created_by=instance.created_by,
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
    """
    Updates the associated canvasing trip's status to completed if all associated CustomerVisits are completed or skipped.
    Enables the trip's salesperson to check out if all visits are done.
    """
    from hr.models import Attendance
    visits = CustomerVisit.objects.filter(trip=instance.trip)
    trip_count = visits.count()
    completed_count = visits.filter(
        status__in=[Trip.COMPLETED, Trip.SKIPPED]).count()
    if trip_count == completed_count:
        canvasing_trip = instance.trip
        canvasing_trip.status = Trip.COMPLETED
        canvasing_trip.updated_by = instance.updated_by
        canvasing_trip.save()

        user = instance.trip.salesperson
        attendance = Attendance.objects.filter(
            employee__user=user, clock_out__isnull=True).last()
        if attendance:
            attendance.able_checkout = True
            attendance.save()


@receiver(pre_save, sender=SalesOrder)
def update_order_status(sender, instance, **kwargs):
    """
    Before saving a `SalesOrder`, this signal checks if the approval status of the order has changed.

    If the order has been approved (based on the `approved_at` field) and not unapproved yet, its status is set to 'APPROVED'. 
    Conversely, if the order has been unapproved (based on the `unapproved_at` field) and not approved, its status is set to 'REJECTED'.
    """
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


# Sales process singnalling ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@receiver(post_save, sender=SalesOrder)
def create_invoice_on_order_submit(sender, instance, **kwargs):
    """
    After saving a `SalesOrder`, if the order's status is 'SUBMITTED' and there isn't already an associated invoice,
    this signal creates a new `Invoice` entry associated with the given order.
    """
    if instance.status == SalesOrder.SUBMITTED and not hasattr(instance, 'invoice'):
        Invoice.objects.create(
            order=instance,
            invoice_date=timezone.now().date(),
            # Any other necessary fields can be populated here.
        )



@receiver(post_save, sender=CustomerVisit)
def handle_customer_visit_completed(sender, instance, **kwargs):
    """
    After saving a `CustomerVisit`, this signal checks if the visit has a status of 'COMPLETED'.
    If the trip type is 'CANVASING', the associated sales order's status is updated and approved.
    Based on the trip type, the related stock movements are also updated with respect to their origin and status.
    """
    sales_order = instance.sales_order
    # Check if the sales order is completed and call the approve method
    if instance.status == Trip.COMPLETED:
        if instance.trip.type == Trip.CANVASING:
            sales_order.status = 'completed'
        # assuming the approve method updates and saves the model
        sales_order.approve(user=instance.trip.updated_by)

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
    """
    After saving a `SalesOrder`, if the invoice PDF hasn't been generated and there are associated order items, 
    this signal triggers the generation of an invoice PDF for the order.
    """
    # Generate PDF only if there are order items and the PDF hasn't been generated yet.
    if not instance.invoice_pdf_generated and instance.order_items.exists():
        generate_invoice_pdf_for_instance(instance)
        instance.invoice_pdf_generated = True
        instance.save()


@receiver(post_save, sender=OrderItem)
def order_item_saved(sender, instance, **kwargs):
    """
    After saving an `OrderItem`, this signal checks the associated `SalesOrder` to determine if an invoice PDF needs to be generated.
    If the PDF hasn't been generated for the order, it triggers its generation.
    """
    # If an OrderItem gets saved, we'll check its related SalesOrder to see if we need to generate the PDF.
    order = instance.order
    if not order.invoice_pdf_generated:
        generate_invoice_pdf_for_instance(order)
        order.invoice_pdf_generated = True
        order.save()


@receiver(pre_save, sender=CustomerVisit)
def set_sales_order_to_processing(sender, instance, **kwargs):
    """
    Logic 1:
    - Triggered before saving a CustomerVisit instance.
    - Checks if the CustomerVisit type is 'canvassing' and previously had no sales_order but now has one assigned.
    - If conditions are met, the associated SalesOrder's status is set to 'PROCESSING' and its approve() method is called.
    """
    if not instance.pk:  # Ensures this is not a newly created instance
        return

    try:
        old_instance = CustomerVisit.objects.get(pk=instance.pk)
    except CustomerVisit.DoesNotExist:
        return

    # Checking the conditions for the first logic
    if (instance.trip.type == Trip.CANVASING and
            not old_instance.sales_order and instance.sales_order):
        instance.sales_order.status = SalesOrder.PROCESSING
        instance.sales_order.type = Trip.CANVASING
        instance.sales_order.approve()
        instance.sales_order.save()


@receiver(post_save, sender=CustomerVisit)
def set_sales_order_to_completed(sender, instance, **kwargs):
    """
    Logic 2:
    - Triggered after saving a CustomerVisit instance.
    - Checks if the CustomerVisit type is 'canvassing', has an associated sales_order, 
      and its status has changed to 'COMPLETED'.
    - If conditions are met, the associated SalesOrder's status is set to 'COMPLETED'.
    """
    if not instance.sales_order:
        return

    # This checks if the 'status' field has been modified in the most recent save
    if not instance.status == Trip.COMPLETED:
        return

    if (models.F('status') != Trip.COMPLETED and
            instance.trip.type == Trip.CANVASING):
        instance.sales_order.status = SalesOrder.COMPLETED
        instance.sales_order.save()


# ==================================================================================
# Model Validator
@receiver(pre_save, sender=Trip)
def ensure_trip_vehicle_has_warehouse(sender, instance, **kwargs):
    # 1. Trip status cannot be changed if its vehicle warehouse is null.
    if instance.status != Trip.WAITING:
        # If a trip vehicle is not specified
        if not instance.vehicle:
            raise ValidationError(
                _('Trip must have an associated vehicle to start the trip.'))
        # If a trip vehicle is specified but doesn't have a warehouse
        if instance.vehicle and not instance.vehicle.warehouse:
            raise ValidationError(
                _('Vehicle must have an associated warehouse to start the trip.'))


@receiver(pre_save, sender=CustomerVisit)
def ensure_trip_status_on_progress(sender, instance, **kwargs):
    # 2. CustomerVisit status can only be changed if Trip status is ON_PROGRESS.
    if instance.status != Trip.WAITING and instance.trip.status != Trip.ON_PROGRESS:
        raise ValidationError(
            _('CustomerVisit status can only be changed if associated Trip status is ON_PROGRESS.'))


@receiver(pre_save, sender=CustomerVisit)
def ensure_fields_present_when_skipped(sender, instance, **kwargs):
    # 4. CustomerVisit status cannot be changed to SKIPPED if notes, visit_evidence, or signature is null.
    if instance.status == Trip.SKIPPED:
        if not all([instance.notes, instance.visit_evidence, instance.signature]):
            raise ValidationError(
                _('CustomerVisit status cannot be set to SKIPPED if notes, visit_evidence, or signature are null.'))


@receiver(pre_save, sender=CustomerVisit)
def check_completed_customer_visit_requirements(sender, instance, **kwargs):
    # 5. Ensure necessary requirements are met when marking a CustomerVisit as COMPLETED.
    if instance.status != Trip.COMPLETED:
        return

    if instance.trip.type == Trip.CANVASING:
        check_canvasing_requirements(instance)
        check_invoice_and_payment(instance.sales_order.invoice)

    elif instance.trip.type == Trip.TAKING_ORDER:
        check_taking_order_requirements(instance)
        print(instance.customer.payment_type)
        if instance.customer.payment_type == Customer.CBD:
            check_invoice_and_payment(instance.sales_order.invoice)

    # Check common SalesOrder status
    check_sales_order_status(instance)


def check_sales_order_status(instance):
    """
    Validate SalesOrder status is not DRAFT when completing a CustomerVisit.
    """
    sales_order = instance.sales_order
    if sales_order.status == SalesOrder.DRAFT:
        raise ValidationError(
            _("Sales Order is in DRAFT status. Cannot set the Customer Visit to COMPLETED.")
        )
    
    if sales_order.customer_visits.exclude(id=instance.id).exists():
        raise ValidationError(
            _(f"Sales Order is already associated with a customer visit #{sales_order.customer_visits.last()}.")
        )


def check_invoice_and_payment(invoice):
    """
    Validate the presence of an invoice and a valid payment for the associated SalesOrder.
    """
    if not invoice:
        raise ValidationError(
            _("The associated Sales Order doesn't have an invoice.")
        )

    payment = SalesPayment.objects.filter(invoice=invoice).last()
    if not payment:
        raise ValidationError(
            _("The associated invoice doesn't have a payment.")
        )

    if payment.status not in [SalesPayment.CAPTURE, SalesPayment.SETTLEMENT]:
        raise ValidationError(
            _("The payment status for the associated invoice is neither CAPTURE nor SETTLEMENT.")
        )


def check_canvasing_requirements(instance):
    """
    Validate requirements specific to CANVASING when completing a CustomerVisit.
    """
    if not all([instance.sales_order, instance.item_delivery_evidence, instance.signature]):
        raise ValidationError(
            _('CustomerVisit status cannot be set to COMPLETED if sales_order, item_delivery_evidence and signature are null.')
        )

    for item in instance.sales_order.order_items.all():
        stocks = WarehouseStock.objects.filter(
            product=item.product, 
            unit=item.unit, 
            warehouse=instance.trip.vehicle.warehouse
        ).values('product', 'unit').annotate(quantity=models.Sum('quantity'))

        stock = stocks[0]['quantity'] if stocks else 0
        if stock < item.quantity:
            raise ValidationError(
                _('CustomerVisit status cannot be set to COMPLETED because this Sales Order Item is out of stock.')
            )


def check_taking_order_requirements(instance):
    """
    Validate requirements specific to TAKING_ORDER when completing a CustomerVisit.
    """
    if not all([instance.sales_order, instance.signature]):
        raise ValidationError(
            _('CustomerVisit status cannot be set to COMPLETED if sales_order and signature are null.')
        )



@receiver(pre_save, sender=SalesPayment)
def validate_payment_amount(sender, instance, **kwargs):
    # 6. Create new payment, its amount shall be greater than the total invoice
    invoice_total = instance.invoice.total
    if instance.amount < invoice_total:
        raise ValidationError(
            _("The payment amount of {payment_amount} is less than the invoice total of {invoice_total}").format(
                payment_amount=instance.amount,
                invoice_total=invoice_total
            )
        )
# ==================================================================================
