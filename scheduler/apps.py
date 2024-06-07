from django.apps import AppConfig


class SchedulerConfig(AppConfig):
    name = 'scheduler'

    def ready(self):
        from .tasks.oqm_daily import start_oqm_daily_scheduler

        start_oqm_daily_scheduler()