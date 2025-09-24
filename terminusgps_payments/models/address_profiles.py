from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .fields import AuthorizenetAddressField
from .managers import UserExclusiveManager


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

    address = AuthorizenetAddressField(default=None, null=True, blank=True)
    objects = UserExclusiveManager()

    class Meta:
        verbose_name = _("address profile")
        verbose_name_plural = _("address profiles")

    def __str__(self) -> str:
        """Returns the address profile id."""
        return str(self.pk)

    def get_absolute_url(self) -> str:
        return reverse(
            "terminusgps_payments:detail address profile",
            kwargs={"profile_pk": self.pk},
        )
