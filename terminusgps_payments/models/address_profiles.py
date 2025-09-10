from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class AddressProfile(models.Model):
    """An Authorizenet customer address profile."""

    id = models.BigIntegerField(primary_key=True)
    """Authorizenet address profile id."""
    customer_profile = models.ForeignKey(
        "terminusgps_payments.CustomerProfile",
        on_delete=models.CASCADE,
        related_name="address_profiles",
    )
    """Associated customer."""

    class Meta:
        verbose_name = _("address profile")
        verbose_name_plural = _("address profiles")

    def __str__(self) -> str:
        """Returns 'Address Profile #<pk>'."""
        return f"Address Profile #{self.pk}"

    def get_absolute_url(self) -> str:
        return reverse(
            "payments:detail address profile", kwargs={"profile_pk": self.pk}
        )
