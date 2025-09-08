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

    cc_last_4 = models.CharField(
        max_length=4, default=None, null=True, blank=True
    )
    """Credit card last 4 digits."""
    cc_type = models.CharField(
        max_length=16, default=None, null=True, blank=True
    )
    """Credit card type."""

    class Meta:
        verbose_name = _("payment profile")
        verbose_name_plural = _("payment profiles")

    def __str__(self) -> str:
        """Returns '<cc_type> ending in <cc_last_4>' or 'Payment Profile #<pk>'."""
        return (
            f"{self.cc_type} ending in {self.cc_last_4}"
            if self.cc_type and self.cc_last_4
            else f"Payment Profile #{self.pk}"
        )

    def get_absolute_url(self) -> str:
        return reverse(
            "payments:detail payment profile", kwargs={"profile_pk": self.pk}
        )

    def needs_authorizenet_hydration(self) -> bool:
        """Whether the payment method needs to retrieve data from Authorizenet."""
        return not all([self.cc_last_4, self.cc_type])
