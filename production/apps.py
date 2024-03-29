from django.apps import AppConfig


class ProductionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'production'
    icon_name = 'autorenew'

    def ready(self):
        import production.signals  # noqa