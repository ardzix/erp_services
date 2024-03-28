from django.apps import AppConfig


class AccountingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounting'
    icon_name = 'library_books'

    def ready(self):
        import accounting.signals  # noqa
