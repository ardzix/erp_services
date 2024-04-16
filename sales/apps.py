from django.apps import AppConfig


class SalesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sales'
    icon_name = 'attach_money'

    def ready(self):
        import sales.signals  
        import sales.signals.addson 

