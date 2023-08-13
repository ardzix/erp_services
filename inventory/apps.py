from django.apps import AppConfig


class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory'
    icon_name = 'local_convenience_store'

    def ready(self):
        import inventory.signals  # noqa

