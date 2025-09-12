from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class PaymentProfile(models.Model):
    """An Authorizenet customer payment profile."""

    id = models.BigIntegerField(primary_key=True)
    """Authorizenet payment profile id."""
    customer_profile = models.ForeignKey(
        "terminusgps_payments.CustomerProfile",
        on_delete=models.CASCADE,
        related_name="payment_profiles",
    )
    """Associated customer."""

    class Meta:
        verbose_name = _("payment profile")
        verbose_name_plural = _("payment profiles")

    def __str__(self) -> str:
        """Returns 'Payment Profile #<pk>'."""
        return f"Payment Profile #{self.pk}"

    def get_absolute_url(self) -> str:
        return reverse(
            "terminusgps_payments:detail payment profile",
            kwargs={"profile_pk": self.pk},
        )
