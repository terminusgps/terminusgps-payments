import datetime
import decimal
import logging

from authorizenet import apicontractsv1
from dateutil.relativedelta import relativedelta
from django.db import models
from django.utils.dateparse import parse_date
from django.utils.translation import gettext_lazy as _
from lxml.objectify import ObjectifiedElement
from terminusgps.authorizenet import api
from terminusgps.authorizenet.service import AuthorizenetService

from .base import AuthorizenetModel

logger = logging.getLogger(__name__)


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
    start_date = models.DateField(blank=True, default=None, null=True)
    total_occurrences = models.IntegerField(default=9999)
    trial_occurrences = models.IntegerField(default=0)
    amount = models.DecimalField(blank=True, decimal_places=2, max_digits=15)
    trial_amount = models.DecimalField(
        blank=True,
        decimal_places=2,
        default=decimal.Decimal("0.00"),
        max_digits=15,
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

    def get_next_payment_date(self) -> datetime.date | None:
        if self.start_date is not None:
            return self.start_date + relativedelta(months=1)

    def get_transactions(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> ObjectifiedElement | None:
        resp = self.pull(
            service, reference_id=reference_id, include_transactions=True
        )
        return getattr(resp, "arbTransactions", None)

    def _extract_id(self, elem: ObjectifiedElement) -> int:
        return int(elem.subscriptionId)

    def pull(
        self,
        service: AuthorizenetService,
        reference_id: str | None = None,
        include_transactions: bool = True,
    ) -> ObjectifiedElement:
        return service.execute(
            api.get_subscription(
                subscription_id=self.pk,
                include_transactions=include_transactions,
            ),
            reference_id=reference_id,
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
            return service.execute(
                api.create_subscription(subscription=subscription),
                reference_id=reference_id,
            )
        else:
            return service.execute(
                api.update_subscription(
                    subscription_id=self.pk, subscription=subscription
                ),
                reference_id=reference_id,
            )

    def sync(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> None:
        resp = self.pull(service, reference_id=reference_id)
        self.name = str(resp.subscription.name)
        self.amount = str(resp.subscription.amount)
        self.trial_amount = str(resp.subscription.trialAmount)
        self.status = str(resp.subscription.status)
        self.total_occurrences = int(
            resp.subscription.paymentSchedule.totalOccurrences
        )
        self.trial_occurrences = int(
            resp.subscription.paymentSchedule.trialOccurrences
        )
        self.start_date = parse_date(
            str(resp.subscription.paymentSchedule.startDate)
        )
        return
