from django.apps import AppConfig


class HrConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hr'
    icon_name = 'wc'

    def ready(self):
        import hr.signals  # noqa
