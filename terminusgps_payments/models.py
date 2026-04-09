import decimal
import logging
from functools import cached_property

from authorizenet import apicontractsv1
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class AuthorizenetModel(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f"{type(self).__name__} #{self.pk}"


class CustomerProfile(AuthorizenetModel):
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="customer_profile",
    )
    merchant_id = models.CharField(max_length=20, blank=True)
    description = models.TextField(max_length=254, blank=True)

    class Meta:
        verbose_name = _("customer profile")
        verbose_name_plural = _("customer profiles")

    def __str__(self) -> str:
        return str(self.user)

    def get_absolute_url(self) -> str:
        return reverse("terminusgps_payments:customer profile details")

    @cached_property
    def email(self) -> str:
        return str(self.user.email)


class Subscription(AuthorizenetModel):
    class SubscriptionStatus(models.TextChoices):
        ACTIVE = "active", _("Active")
        EXPIRED = "expired", _("Expired")
        SUSPENDED = "suspended", _("Suspended")
        CANCELED = "canceled", _("Canceled")
        TERMINATED = "terminated", _("Terminated")

    status = models.CharField(blank=True, choices=SubscriptionStatus.choices)
    expires_on = models.DateField(blank=True, null=True, default=None)
    customer_profile = models.ForeignKey(
        "terminusgps_payments.CustomerProfile",
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    plan = models.ForeignKey(
        "terminusgps_payments.SubscriptionPlan",
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )

    class Meta:
        verbose_name = _("subscription")
        verbose_name_plural = _("subscriptions")

    def get_absolute_url(self) -> str:
        return reverse(
            "terminusgps_payments:subscription details", kwargs={"pk": self.pk}
        )


class SubscriptionPlan(models.Model):
    class SubscriptionPlanVisibility(models.TextChoices):
        VISIBLE = "vis", _("Visible")
        HIDDEN = "hid", _("Hidden")

    name = models.CharField(max_length=50)
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    trial_amount = models.DecimalField(
        decimal_places=2, default=decimal.Decimal("0.00"), max_digits=12
    )
    total_occurrences = models.IntegerField(default=9999)
    trial_occurrences = models.IntegerField(default=0)
    length = models.IntegerField(default=1)
    unit = models.CharField(
        choices=[
            (apicontractsv1.ARBSubscriptionUnitEnum.months, _("Months")),
            (apicontractsv1.ARBSubscriptionUnitEnum.days, _("Days")),
        ],
        default=apicontractsv1.ARBSubscriptionUnitEnum.months,
    )
    description = models.TextField(blank=True)
    visibility = models.CharField(
        choices=SubscriptionPlanVisibility.choices,
        default=SubscriptionPlanVisibility.VISIBLE,
        max_length=3,
    )

    class Meta:
        verbose_name = _("subscription plan")
        verbose_name_plural = _("subscription plans")

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse(
            "terminusgps_payments:subscription plan details",
            query={"pk": self.pk},
        )
