from django.db.models.signals import pre_save, post_save, pre_delete
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db import models
from django.dispatch import receiver
from libs.constants import WAITING, ON_PROGRESS, COMPLETED, SKIPPED
from libs.utils import add_one_day
from inventory.models import Product, StockMovementItem, WarehouseStock
from ..helpers.sales_order import (canvasing_create_stock_movement,
                                   taking_order_create_stock_movement, handle_unapproved_sales_order,
                                   all_visits_completed_or_skipped, update_trip_status_to_completed,
                                   handle_canvasing_trip, handle_taking_order_trip,
                                   set_salesperson_able_to_checkout, explode_stock_based_on_order_item)
from ..helpers.trip import (create_collector_trip,
                            create_customer_visits_for_collector_trip,
                            create_return_stock_movement)
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

# ~Product Quantity~
# 1. update_product_quantity: Adjusts the product quantity when an OrderItem's quantity changes.
# 2. deduct_product_quantity: Deducts the product's quantity when a new OrderItem is created.
# 3. restore_product_quantity: Restores the product's quantity when an OrderItem is deleted.

# ~ Sales Order ~
# 4. check_salesorder_before_approved: Checks if a SalesOrder was previously approved or unapproved and sets flags accordingly.
# 5. create_stock_movement: Creates a StockMovement entry when a SalesOrder is approved.
# 6. create_stock_movement_item: Creates a StockMovementItem entry when a new OrderItem is created and the order has associated stock movement.
# 7. update_order_status: Before saving a `SalesOrder`, this signal checks if the approval status of the order has changed.
# 8. create_invoice_on_order_submit: After saving a `SalesOrder`, if the order's status is 'SUBMITTED' and there isn't already an associated invoice,this signal creates a new `Invoice` entry associated with the given order.
# 9. generate_invoice_pdf_from_sales_order: Generate invoice PDF if `SalesOrder` is saved
# 10. generate_invoice_pdf_from_order_items: Generate invoice PDF if `OrderItem` is saved
# 11. set_sales_order_to_processing: Associate SalesOrder's status is set to 'PROCESSING' and its approve() method is called
# 12. set_sales_order_to_completed: Set the associated CustomerVisit's SalesOrder's status is set to 'COMPLETED'

# ~ Trip ~
# 13. populate_trip_customer_from_template: Populates the trip's customers from a template when a new Trip instance is created.
# 14. generate_visit_report: Generates or updates a CustomerVisitReport when a CustomerVisit's status is either completed or skipped.
# 15. update_trip_status_if_visit_completed: Updates the associated canvasing trip's status to completed if all associated CustomerVisits are completed or skipped.
# 16. handle_customer_visit_completed: Handle logic of if customer visit is completed
# 17. assign_trip_default_vehicle: Assigns the first vehicle from the associated TripTemplate
# 18. create_collector_trip_on_taking_order_complete: Create Trip for collector after the taking order completed
# 19. create_next_trip_on_trip_complete: Create a ne Trip when a Trip changes status to 'COMPLETED'.
# 20. create_return_stock_movement_on_canvasing_complete: Create a stock movement to return items remaining in the trip's vehicle.


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
    instance.visit_before = False
    so_before = SalesOrder.objects.filter(pk=instance.pk).last()
    if so_before:
        instance.approved_before = True if so_before.approved_at and so_before.approved_by else False
        instance.unapproved_before = True if so_before.unapproved_at and so_before.unapproved_by else False
        instance.visit_before = True if so_before.visit else False


@receiver(post_save, sender=SalesOrder)
def create_stock_movement(sender, instance, **kwargs):
    """
    Creates a StockMovement entry when a SalesOrder is approved.
    Deletes the StockMovement if a SalesOrder is unapproved.
    """
    if not instance.pk:
        return

    if not instance.visit_before and instance.visit:
        visit_type = instance.visit.trip.type
        if visit_type == Trip.CANVASING:
            canvasing_create_stock_movement(instance)
        elif visit_type == Trip.TAKING_ORDER:
            taking_order_create_stock_movement(instance)

    if not instance.unapproved_before and instance.unapproved_at:
        handle_unapproved_sales_order(instance)


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
                status=WAITING,
                order=trip_customer.order,
                created_by=instance.created_by
            )


@receiver(post_save, sender=CustomerVisit)
def generate_visit_report(sender, instance, **kwargs):
    """
    Generates or updates a CustomerVisitReport when a CustomerVisit's status is either completed or skipped.
    Adds sold products to the report if there's an associated SalesOrder.
    """
    if instance.status in [COMPLETED, SKIPPED]:
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
def update_trip_status_if_visit_completed(sender, instance, **kwargs):
    """
    Updates the associated canvasing trip's status to completed if all associated CustomerVisits are completed or skipped.
    Enables the trip's salesperson to check out if all visits are done.
    """
    if all_visits_completed_or_skipped(instance.trip):
        update_trip_status_to_completed(instance)
        handle_canvasing_trip(instance)
        handle_taking_order_trip(instance)
        set_salesperson_able_to_checkout(instance)


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
    if not sales_order:
        return
    sales_order.visit = instance
    # Check if the sales order is completed and call the approve method
    if instance.status == COMPLETED:
        if instance.trip.type == Trip.CANVASING:
            sales_order.status = 'completed'
            sales_order.warehouse = instance.trip.vehicle.warehouse
        # assuming the approve method updates and saves the model
        sales_order.approve(user=instance.trip.updated_by)


@receiver(post_save, sender=SalesOrder)
def generate_invoice_pdf_from_sales_order(sender, instance, **kwargs):
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
def generate_invoice_pdf_from_order_items(sender, instance, **kwargs):
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
    if not instance.status == COMPLETED:
        return

    if (models.F('status') != COMPLETED and
            instance.trip.type == Trip.CANVASING):
        instance.sales_order.status = SalesOrder.COMPLETED
        instance.sales_order.save()


@receiver(post_save, sender=Trip)
def assign_trip_default_vehicle(sender, instance, created, **kwargs):
    """
    Assigns the first vehicle from the associated TripTemplate 
    to the Trip instance if the vehicle is None.
    """
    if created and instance.vehicle is None:
        # Fetch the first vehicle associated with the TripTemplate.
        vehicle = instance.template.vehicles.first()

        # If a vehicle was found, assign it to the Trip.
        if vehicle:
            instance.vehicle = vehicle
            instance.save()


@receiver(pre_save, sender=Trip)
def create_collector_trip_on_taking_order_complete(sender, instance, **kwargs):
    """
    Create a Collector Trip when a Trip with type 'TAKING_ORDER' changes status to 'COMPLETED'.
    Only applicable for trips where a customer with payment type credit exists.
    """
    if instance.pk and instance.status == COMPLETED and instance.type == Trip.TAKING_ORDER:
        old_instance = Trip.objects.filter(pk=instance.pk).first()

        if old_instance and old_instance.status != COMPLETED:
            credit_type_visits = instance.customervisit_set.filter(
                customer__payment_type=Customer.CREDIT)

            if credit_type_visits.exists():
                collector_trip = create_collector_trip(instance)
                create_customer_visits_for_collector_trip(
                    credit_type_visits, collector_trip)

@receiver(pre_save, sender=Trip)
def create_next_trip_on_trip_complete(sender, instance, **kwargs):
    """
    This signal triggers when a Trip instance is about to be saved. It checks if the status of the trip
    is transitioning to either 'COMPLETED' or 'SKIPPED'. If so, it creates a new Trip for the next day 
    with the same salesperson, vehicle, and type as the current one.

    Args:
    - sender: The model class that sent the signal.
    - instance: The actual instance of Trip being saved.
    - kwargs: Additional keyword arguments.
    """
    # Avoid processing for newly created instances
    if not instance.pk:
        return

    # Get the current status of the trip instance from the database
    status_before = Trip.objects.get(pk=instance.pk).status

    # Create a new trip if the current trip is transitioning to 'COMPLETED' or 'SKIPPED'
    if instance.status in [COMPLETED, SKIPPED] and status_before not in [COMPLETED, SKIPPED]:
        Trip.objects.create(
            template=instance.template,
            date=add_one_day(timezone.now()),
            salesperson=instance.salesperson,
            vehicle=instance.vehicle,
            type=instance.type,
        )

@receiver(pre_save, sender=Trip)
def create_return_stock_movement_on_canvasing_complete(sender, instance, **kwargs):
    """
    This signal is triggered before a Trip instance is saved. It checks if the canvasing trip is transitioning
    to a 'COMPLETED' or 'SKIPPED' status. If so, it initiates a process to create a stock movement 
    for returning any remaining items in the trip's vehicle.

    Args:
    - sender: The model class that sent the signal.
    - instance: The actual instance of Trip being saved.
    - kwargs: Additional keyword arguments.
    """
    # Avoid processing for newly created instances
    if not instance.pk:
        return
    
    if not instance.type == Trip.CANVASING:
        return

    # Get the current status of the trip instance from the database
    status_before = Trip.objects.get(pk=instance.pk).status

    # Initiate stock movement creation if the trip is transitioning to 'COMPLETED' or 'SKIPPED'
    if instance.status in [COMPLETED, SKIPPED] and status_before not in [COMPLETED, SKIPPED]:
        create_return_stock_movement(instance)


# ==================================================================================
# Model Validator


@receiver(pre_save, sender=Trip)
def ensure_trip_vehicle_has_warehouse(sender, instance, **kwargs):
    # 1. Trip status cannot be changed if its vehicle warehouse is null in canvassing.
    if instance.status != WAITING and instance.type == Trip.CANVASING:
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
    if instance.status != WAITING and instance.trip.status != ON_PROGRESS:
        raise ValidationError(
            _('CustomerVisit status can only be changed if associated Trip status is ON_PROGRESS.'))


@receiver(pre_save, sender=CustomerVisit)
def ensure_fields_present_when_skipped(sender, instance, **kwargs):
    # 4. CustomerVisit status cannot be changed to SKIPPED if notes, visit_evidence, or signature is null.
    if instance.status == SKIPPED and not all([instance.notes, instance.visit_evidence, instance.signature]):
        raise ValidationError(
            _('CustomerVisit status cannot be set to SKIPPED if notes, visit_evidence, or signature are null.'))


@receiver(pre_save, sender=CustomerVisit)
def check_completed_customer_visit_requirements(sender, instance, **kwargs):
    # 5. Ensure necessary requirements are met when marking a CustomerVisit as COMPLETED.
    if instance.status != COMPLETED:
        return

    if instance.trip.type == Trip.CANVASING:
        check_canvasing_requirements(instance)
        if instance.customer.payment_type in [Customer.COD, Customer.CBD]:
            check_invoice_and_payment(instance.sales_order.invoice)

    elif instance.trip.type == Trip.TAKING_ORDER:
        check_taking_order_requirements(instance)
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

    if sales_order.customer_visits.exclude(id=instance.id, trip__type=Trip.COLLECTING).exists():
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
        warehouse_stocks = WarehouseStock.objects.filter(
            product=item.product,
            warehouse=instance.trip.vehicle.warehouse
        )
        stock = 0
        for ws in warehouse_stocks:
            stock += ws.smallest_unit_quantity

        if stock < item.smallest_unit_quantity:
            raise ValidationError(
                _('CustomerVisit status cannot be set to COMPLETED because this Sales Order Item is out of stock.')
            )
        explode_stock_based_on_order_item(warehouse_stocks, item)


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
    if round(instance.amount, 0) < round(invoice_total, 0):
        raise ValidationError(
            _("The payment amount of {payment_amount} is less than the invoice total of {invoice_total}").format(
                payment_amount=instance.amount,
                invoice_total=invoice_total
            )
        )
# ==================================================================================
