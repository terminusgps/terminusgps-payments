from django.apps import AppConfig
from django.db.models.signals import post_save


class TerminusgpsPaymentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "terminusgps_payments"
    verbose_name = "Terminus GPS Payments"

    def ready(self):
        from . import models, signals

        post_save.connect(
            signals.hydrate_address_profile, sender=models.AddressProfile
        )
        post_save.connect(
            signals.hydrate_payment_profile, sender=models.PaymentProfile
        )
