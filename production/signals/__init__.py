from hashlib import blake2b
from itertools import product
from django.db import models
from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from inventory.models import StockMovement, Warehouse, WarehouseStock, StockMovementItem
from inventory.serializers import warehouse
from ..models import *


@receiver(pre_save, sender=ProductionOrder)
def validate_production_order(sender, instance, **kwargs):
    product = instance.product

    # Check if the product has a BillOfMaterials
    bom_product = BOMProduct.objects.filter(product=product)
    bom = bom_product.first().bom
    if not bom:
        raise ValidationError(
            {"product": _("Product must have a BillOfMaterials to create a ProductionOrder")})

    # Check if the product has any BOMComponent
    if not bom.components.exists():
        raise ValidationError({"product": _(
            "Product must have at least one BOMComponent to create a ProductionOrder")})


def get_work_order_component_quantity(component, work_order):
    # Calculate the required quantity based on the BOM and work order quantity
    return component.quantity * work_order.production_order.quantity


def get_stock(warehouse, component):
    try:
        return WarehouseStock.objects.get(warehouse=warehouse, product=component.component)
    except WarehouseStock.DoesNotExist:
        raise ValidationError({"work_center_warehouse": _(
            f'Warehouse stock has not been set for this component (#{component.component})')})


@receiver(post_save, sender=WorkOrder)
def move_materials_to_workcenter(sender, instance, created, **kwargs):
    if created:
        # Fetch the BOM components for the associated product of the production order
        bom_product = BOMProduct.objects.filter(
            product=instance.production_order.product)
        bom = bom_product.first().bom
        bom_components = BOMComponent.objects.filter(bom=bom)

        # Iterate over the BOM components and deduct stocks
        for component in bom_components:
            quantity = get_work_order_component_quantity(component, instance)
            product = component.component
            product.quantity -= quantity
            product.updated_by = instance.created_by
            product.save()

            stock = get_stock(instance.work_center_warehouse, component)
            stock.quantity -= quantity
            stock.updated_by = instance.created_by
            stock.save()


@receiver(pre_save, sender=WorkOrder)
def check_workorder_before_started(sender, instance, **kwargs):
    if not instance.pk:
        product = instance.production_order.product
        warehouse = instance.work_center_warehouse
        bom_product = BOMProduct.objects.filter(product=product)
        bom = bom_product.first().bom
        bom_components = BOMComponent.objects.filter(bom=bom)
        # Iterate over the BOM components and check for stocks
        for component in bom_components:
            quantity = get_work_order_component_quantity(component, instance)
            stock = get_stock(warehouse, component)
            if stock.quantity < quantity:
                raise ValidationError({"product": _(
                    f'Stock {component.component} is lower than quantity needed to produce {product}')})


@receiver(pre_save, sender=ProductionTracking)
def check_production_tracking(sender, instance, **kwargs):
    work_order = instance.work_order
    if not work_order:
        return
    if not work_order.start_time:
        raise ValidationError(
            {"work_order": _('Work order has not been started')})
    if work_order.end_time:
        raise ValidationError(
            {"work_order": _('Work order has been finished')})


@receiver(pre_save, sender=ProductionTracking)
def check_workcenter(sender, instance, **kwargs):
    if not instance.work_center_warehouse and instance.work_order:
        instance.work_center_warehouse = instance.work_order.work_center_warehouse
    if not instance.work_center_warehouse:
        raise ValidationError({"work_center_warehouse": _(
            'Work center warehouse should be set either directly or via work order')})


@receiver(pre_save, sender=ProductionTracking)
def set_tracking_time(sender, instance, **kwargs):
    instance.start_time = instance.work_order.start_time if instance.work_order else instance.created_at


@receiver(pre_save, sender=ComponentItem)
def check_component_stock(sender, instance, **kwargs):
    stock_qs = WarehouseStock.objects.filter(
        warehouse=instance.production.work_center_warehouse,
        product=instance.item,
        unit=instance.unit)
    stocks = stock_qs.values(
        'product__name', 'unit__symbol'
    ).annotate(total_quantity=models.Sum('quantity'))
    if not stocks.exists():
        instance.production.delete()
        raise ValidationError({"component_items": _(
            f'Warehouse stock has not been set for this (#{instance.item}) & (#{instance.production.work_center_warehouse})')})
    if stocks[0].get('total_quantity') < instance.quantity:
        instance.production.delete()
        raise ValidationError({"component_items": _(
            f'This product (#{instance.item}) is out of stock')})
    instance.stock_qs = stock_qs


@receiver(post_save, sender=ComponentItem)
def deduct_component_stock(sender, instance, created, **kwargs):
    if created:
        quantity_remaining = instance.quantity
        for stock in instance.stock_qs:
            quantity = quantity_remaining if quantity_remaining <= stock.quantity else stock.quantity
            stock.quantity -= quantity
            stock.save()
            quantity_remaining -= quantity
            if quantity_remaining <= 0:
                break


@receiver(post_save, sender=ProducedItem)
def add_produced_item_stock(sender, instance, created, **kwargs):
    stock, created = WarehouseStock.objects.get_or_create(
        warehouse=instance.production.work_center_warehouse,
        product=instance.item,
        unit=instance.unit,
        expire_date=instance.expire_date)
    stock.quantity += instance.quantity
    stock.save()


@receiver(post_save, sender=ProductionTracking)
def update_work_order(sender, instance, created, **kwargs):
    if created and instance.work_order:
        work_order = instance.work_order
        work_order.end_time = instance.end_time
        work_order.updated_by = instance.created_by
        work_order.save()
