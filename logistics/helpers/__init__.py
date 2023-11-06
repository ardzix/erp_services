from datetime import timedelta
from libs.utils import get_config_value, TRUE
from ..models import Job, Drop

def add_one_day(trip_date):
    job_date = trip_date + timedelta(days=1)

    if get_config_value('driver_work_only_weekday') in TRUE:
        # If the job_date falls on a Saturday (5), add two more days to make it Monday
        if job_date.weekday() == 5:
            job_date += timedelta(days=2)
        # If the job_date falls on a Sunday (6), add one more day to make it Monday
        elif job_date.weekday() == 6:
            job_date += timedelta(days=1)

    return job_date

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
            order=visit.order,
            sales_visit=visit
        )