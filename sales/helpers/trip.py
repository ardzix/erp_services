from libs.utils import add_one_day
from ..models import Trip, CustomerVisit


def create_collector_trip(instance):
    """
    Helper function to create a collector trip.
    """
    trip_date = instance.date
    collector = instance.template.collector_pic.last()

    return Trip.objects.create(
        template = instance.template,
        date=add_one_day(add_one_day(trip_date)),  # Assumes add_one_day function exists
        salesperson=instance.salesperson,
        collector=collector,
        type=Trip.COLLECTING,
        parent=instance,
    )

def create_customer_visits_for_collector_trip(visits, trip):
    """
    Helper function to create customer visits for the new collector trip.
    """
    for visit in visits:
        CustomerVisit.objects.create(
            trip=trip,
            customer=visit.customer,
            sales_order=visit.sales_order,
            order=visit.order,
            item_delivery_evidence=visit.item_delivery_evidence
        )