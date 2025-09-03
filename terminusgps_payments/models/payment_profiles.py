from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from terminusgps.authorizenet import profiles


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

    def save(self, **kwargs) -> None:
        """Sets :py:attr:`cc_last_4` and :py:attr:`cc_type` if necessary before saving."""
        if self._needs_authorizenet_hydration():
            if self.customer_profile.pk and self.pk:
                response = self.get_authorizenet_profile()
                if response is not None and all(
                    [
                        hasattr(response, "paymentProfile"),
                        hasattr(response.paymentProfile, "payment"),
                        hasattr(response.paymentProfile.payment, "creditCard"),
                    ]
                ):
                    cc = response.paymentProfile.payment.creditCard
                    if hasattr(cc, "cardType"):
                        self.cc_type = str(cc.cardType)
                    if hasattr(cc, "cardNumber"):
                        self.cc_last_4 = str(cc.cardNumber)[-4:]
        return super().save(**kwargs)

    def get_absolute_url(self) -> str:
        return reverse(
            "payments:detail payment profile", kwargs={"payment_pk": self.pk}
        )

    def get_authorizenet_profile(self, include_issuer_info: bool = False):
        """Returns the customer payment profile from Authorizenet."""
        if self.customer_profile.pk and self.pk:
            return profiles.get_customer_payment_profile(
                customer_profile_id=self.customer_profile.pk,
                customer_payment_profile_id=self.pk,
                include_issuer_info=include_issuer_info,
            )

    def _needs_authorizenet_hydration(self) -> bool:
        """Whether the payment method needs to retrieve data from Authorizenet."""
        return not all([self.cc_last_4, self.cc_type])
