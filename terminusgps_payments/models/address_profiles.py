from django.db import models
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

    street = models.CharField(
        max_length=24, default=None, null=True, blank=True
    )
    """Address street."""

    class Meta:
        verbose_name = _("address profile")
        verbose_name_plural = _("address profiles")

    def __str__(self) -> str:
        """Returns '<street>' or 'Address Profile #<pk>'."""
        return (
            str(self.street) if self.street else f"Address Profile #{self.pk}"
        )

    def needs_authorizenet_hydration(self) -> bool:
        """Whether the shipping address needs to retrieve data from Authorizenet."""
        return not all([self.street])
