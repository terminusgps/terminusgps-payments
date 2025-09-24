from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .fields import AuthorizenetAddressField, AuthorizenetCreditCardField
from .managers import UserExclusiveManager


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
    objects = UserExclusiveManager()

    credit_card = AuthorizenetCreditCardField(
        default=None, null=True, blank=True
    )
    address = AuthorizenetAddressField(default=None, null=True, blank=True)

    class Meta:
        verbose_name = _("payment profile")
        verbose_name_plural = _("payment profiles")

    def __str__(self) -> str:
        """Returns the payment profile id."""
        return str(self.pk)

    def get_absolute_url(self) -> str:
        """Returns a URL pointing to the payment profile's detail view."""
        return reverse(
            "terminusgps_payments:detail payment profile",
            kwargs={"profile_pk": self.pk},
        )

    def get_icon_url(self) -> str:
        """Returns a URL pointing to the payment profile's credit card icon."""
        icons_map = {
            "discover": "terminusgps_payments/icons/discover.svg",
            "mastercard": "terminusgps_payments/icons/mastercard.svg",
            "americanexpress": "terminusgps_payments/icons/americanexpress.svg",
            "visa": "terminusgps_payments/icons/visa.svg",
            None: "",
        }
        card_type = (
            str(getattr(self.credit_card, "cardType")).lower()
            if self.credit_card is not None
            else None
        )
        return icons_map[card_type]
