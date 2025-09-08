from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from terminusgps.authorizenet import api as anet


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

    def save(self, **kwargs) -> None:
        """Sets :py:attr:`street` if necessary before saving."""
        if self._needs_authorizenet_hydration():
            response = self.get_authorizenet_profile()
            if response is not None and all(
                [
                    hasattr(response, "address"),
                    hasattr(response.address, "address"),
                ]
            ):
                self.street = str(response.address.address)
        return super().save(**kwargs)

    def get_absolute_url(self) -> str:
        return reverse(
            "payments:detail address profile", kwargs={"profile_pk": self.pk}
        )

    def get_authorizenet_profile(self):
        """Returns the customer shipping address profile from Authorizenet."""
        if self.customer_profile.pk and self.pk:
            return anet.get_customer_shipping_address(
                customer_profile_id=self.customer_profile.pk,
                address_profile_id=self.pk,
            )

    def _needs_authorizenet_hydration(self) -> bool:
        """Whether the shipping address needs to retrieve data from Authorizenet."""
        return not all([self.street])
