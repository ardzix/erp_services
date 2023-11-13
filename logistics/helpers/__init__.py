
from libs.utils import add_one_day
from sales.models import Customer
from ..models import Job, Drop

def create_job_from_trip(instance):
    trip_date = instance.date
    data = {
        'vehicle': instance.vehicle,
        'trip': instance,
        'date': add_one_day(trip_date),
        'assigned_driver': instance.vehicle.driver if instance.vehicle else None
    }

    Job.objects.create(**data)


def create_drops_from_visits(job, customer_visits):
    """
    Helper function to create Drop instances from CustomerVisits.
    """
    for visit in customer_visits:
        Drop.objects.create(
            job=job,
            location_name=f"{visit.customer.name} - {visit.customer.store_name}",
            address=visit.customer.address,
            location=visit.customer.location,
            retrieve_payment=True if visit.customer.payment_type == Customer.COD else False,
            order=visit.order,
            sales_visit=visit
        )