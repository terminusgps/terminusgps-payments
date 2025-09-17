from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from terminusgps.authorizenet.constants import SubscriptionStatus

from .managers import UserExclusiveManager


class Subscription(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    """Authorizenet subscription id."""
    name = models.CharField(max_length=31)
    """Subscription name."""
    status = models.CharField(
        max_length=16,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.ACTIVE,
    )
    """Subscription status."""
    customer_profile = models.ForeignKey(
        "terminusgps_payments.CustomerProfile",
        on_delete=models.RESTRICT,
        related_name="subscriptions",
    )
    """Associated customer profile."""
    payment_profile = models.ForeignKey(
        "terminusgps_payments.PaymentProfile",
        on_delete=models.RESTRICT,
        related_name="subscriptions",
    )
    """Associated payment profile."""
    address_profile = models.ForeignKey(
        "terminusgps_payments.AddressProfile",
        on_delete=models.RESTRICT,
        related_name="subscriptions",
    )
    """Associated address profile."""
    objects = UserExclusiveManager()

    class Meta:
        verbose_name = _("subscription")
        verbose_name_plural = _("subscriptions")

    def __str__(self) -> str:
        """Returns the subscription's name."""
        return self.name

    def get_absolute_url(self) -> str:
        """Returns a URL pointing to the subscription's detail view."""
        return reverse(
            "terminusgps_payments:detail subscription",
            kwargs={"subscription_pk": self.pk},
        )

    def get_update_url(self) -> str:
        """Returns a URL pointing to the subscription's update view."""
        return reverse(
            "terminusgps_payments:update subscription",
            kwargs={"subscription_pk": self.pk},
        )
