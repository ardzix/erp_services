from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date, timedelta
from sales.models import OQMDaily, SalesOrder, SellingMarginDaily


def oqm_daily_task(aggregate_date: date = None):
    print("oqm_daily_task is running ....")
    if not aggregate_date:
        aggregate_date = date.today()

    sales_orders = SalesOrder.objects.filter(order_date=aggregate_date)
    daily_quantity = 0
    daily_omzet = 0
    daily_margin = 0

    selling_margin = {}
    for so in sales_orders:
        margin = so.margin_amount
        omzet = so.total_omzet
        qty = so.total_qty

        sales_id = so.created_by_id
        if selling_margin.get(sales_id):
            selling_margin[sales_id] += margin
        else:
            selling_margin[sales_id] = margin

        daily_margin += margin
        daily_quantity += qty
        daily_omzet += omzet

    try:
        daily_margin_percentage = round(daily_margin / daily_omzet, 2) * 100
    except:
        daily_margin_percentage = 0

    # handle if rerun 2x. prevent create/update
    obj, created = OQMDaily.objects.update_or_create(
        date=aggregate_date,
        defaults={
            "daily_omzet": daily_omzet,
            "daily_quantity": daily_quantity,
            "daily_margin": daily_margin,
            "daily_margin_percentage": daily_margin_percentage,
        },
    )

    for sales_id, margin in selling_margin.items():
        obj, created = SellingMarginDaily.objects.update_or_create(
            date=aggregate_date,
            sales_id=sales_id,
            defaults={
                "daily_margin": margin,
            },
        )
    print("oqm_daily_task done ....")



def start_oqm_daily_scheduler():
    scheduler = BackgroundScheduler()

    yesterday = date.today() - timedelta(days=1)
    # run every 00:10 server time
    cron_kwargs = {
        "hour": 0,
        "minute": 10,
    }

    scheduler.add_job(oqm_daily_task, "cron", [yesterday], **cron_kwargs)
    scheduler.start()
