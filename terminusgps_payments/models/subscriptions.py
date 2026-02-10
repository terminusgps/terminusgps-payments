import datetime
import decimal

from authorizenet import apicontractsv1
from django.db import models
from django.urls import reverse
from django.utils.dateparse import parse_date
from django.utils.translation import gettext_lazy as _
from lxml.objectify import ObjectifiedElement
from terminusgps.authorizenet import api
from terminusgps.authorizenet.service import AuthorizenetService

from .base import AuthorizenetModel


class Subscription(AuthorizenetModel):
    class SubscriptionStatus(models.TextChoices):
        ACTIVE = "active", _("Active")
        EXPIRED = "expired", _("Expired")
        SUSPENDED = "suspended", _("Suspended")
        CANCELED = "canceled", _("Canceled")
        TERMINATED = "terminated", _("Terminated")

    class SubscriptionIntervalUnit(models.TextChoices):
        DAYS = apicontractsv1.ARBSubscriptionUnitEnum.days, _("Days")
        MONTHS = apicontractsv1.ARBSubscriptionUnitEnum.months, _("Months")

    name = models.CharField(blank=True, max_length=50)
    interval_length = models.IntegerField(default=1)
    interval_unit = models.CharField(
        choices=SubscriptionIntervalUnit.choices,
        default=SubscriptionIntervalUnit.MONTHS,
    )
    start_date = models.DateField(blank=True, default=datetime.date.today)
    total_occurrences = models.IntegerField(default=9999)
    trial_occurrences = models.IntegerField(default=0)
    amount = models.DecimalField(
        decimal_places=2, default=decimal.Decimal("24.95"), max_digits=15
    )
    trial_amount = models.DecimalField(
        decimal_places=2, default=decimal.Decimal("0.00"), max_digits=15
    )
    status = models.CharField(
        choices=SubscriptionStatus.choices, default=SubscriptionStatus.ACTIVE
    )

    customer_profile = models.ForeignKey(
        "terminusgps_payments.CustomerProfile",
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    payment_profile = models.ForeignKey(
        "terminusgps_payments.CustomerPaymentProfile",
        on_delete=models.RESTRICT,
        related_name="subscriptions",
    )
    address_profile = models.ForeignKey(
        "terminusgps_payments.CustomerAddressProfile",
        on_delete=models.RESTRICT,
        related_name="subscriptions",
    )

    class Meta:
        verbose_name = _("subscription")
        verbose_name_plural = _("subscriptions")

    def get_absolute_url(self):
        return reverse(
            "terminusgps_payments:detail subscriptions", kwargs={"pk": self.pk}
        )

    def push(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> ObjectifiedElement:
        schedule = apicontractsv1.paymentScheduleType()
        schedule.startDate = self.start_date.strftime("%Y-%m-%d")
        schedule.totalOccurrences = str(self.total_occurrences)
        schedule.trialOccurrences = str(self.trial_occurrences)

        profile = apicontractsv1.customerProfileIdType()
        profile.customerProfileId = str(self.customer_profile.pk)
        profile.customerPaymentProfileId = str(self.payment_profile.pk)
        profile.customerAddressId = str(self.address_profile.pk)

        subscription = apicontractsv1.ARBSubscriptionType()
        subscription.name = str(self.name)
        subscription.paymentSchedule = schedule
        subscription.amount = str(self.amount)
        subscription.trialAmount = str(self.trial_amount)
        subscription.profile = profile

        if not self.pk:
            interval = apicontractsv1.paymentScheduleTypeInterval()
            interval.unit = str(self.interval_unit)
            interval.length = str(self.interval_length)
            subscription.paymentSchedule.interval = interval
            request = api.create_subscription(subscription=subscription)
        else:
            request = api.update_subscription(
                subscription_id=self.pk, subscription=subscription
            )
        return service.execute(request, reference_id=reference_id)

    def pull(
        self,
        service: AuthorizenetService,
        reference_id: str | None = None,
        include_transactions: bool = True,
    ) -> ObjectifiedElement:
        request = api.get_subscription(
            subscription_id=self.pk, include_transactions=include_transactions
        )
        return service.execute(request, reference_id=reference_id)

    def sync(self, elem: ObjectifiedElement) -> None:
        if hasattr(elem, "subscription"):
            self.name = getattr(elem.subscription, "name", "")
            self.amount = getattr(elem.subscription, "amount", "")
            self.trial_amount = getattr(elem.subscription, "trialAmount", "")
            self.status = getattr(elem.subscription, "status", "active")
            if hasattr(elem.subscription, "paymentSchedule"):
                sch = elem.subscription.paymentSchedule
                self.total_occurrences = int(
                    getattr(sch, "totalOccurrences", 0)
                )
                self.trial_occurrences = int(
                    getattr(sch, "trialOccurrences", 0)
                )
                start_date = str(getattr(sch, "startDate", ""))
                if start_date:
                    self.start_date = parse_date(start_date)
        return

    def _extract_authorizenet_id(self, elem: ObjectifiedElement) -> int:
        return int(elem.subscriptionId)

    def _delete_in_authorizenet(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> None:
        request = api.cancel_subscription(subscription_id=self.pk)
        return service.execute(request, reference_id=reference_id)
