from django.apps import AppConfig


class PurchasingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'purchasing'
    icon_name = 'add_shopping_cart'

    def ready(self):
        import purchasing.signals  # noqa
