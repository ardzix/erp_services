from ..models import Job, Drop


def create_job_from_trip(instance):
    data = {
        'vehicle': instance.vehicle,
        'trip': instance,
        'date': instance.date,
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