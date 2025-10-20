from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.db.models.signals import post_delete, post_save


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
        post_save.connect(
            signals.hydrate_subscription_status, sender=models.Subscription
        )
        post_save.connect(
            signals.get_or_create_customer_profile_for_user,
            sender=get_user_model(),
        )
        post_delete.connect(
            signals.delete_customer_profile_in_authorizenet,
            sender=models.CustomerProfile,
        )
        post_delete.connect(
            signals.delete_address_profile_in_authorizenet,
            sender=models.AddressProfile,
        )
        post_delete.connect(
            signals.delete_payment_profile_in_authorizenet,
            sender=models.PaymentProfile,
        )
