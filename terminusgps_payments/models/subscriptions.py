import datetime
import decimal
import logging
import typing

from authorizenet import apicontractsv1
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from lxml.objectify import ObjectifiedElement
from terminusgps.authorizenet import api
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
    AuthorizenetService,
)

from .base import AuthorizenetModel

logger = logging.getLogger(__name__)


class Subscription(AuthorizenetModel):
    name = models.CharField(max_length=64)
    """Authorizenet subscription name."""
    amount = models.DecimalField(decimal_places=2, max_digits=9)
    """Authorizenet subscription amount."""
    status = models.CharField(
        choices=[
            ("active", _("Active")),
            ("expired", _("Expired")),
            ("suspended", _("Suspended")),
            ("canceled", _("Canceled")),
            ("terminated", _("Terminated")),
            ("unknown", _("Unknown")),
        ],
        default="unknown",
    )
    """Authorizenet subscription status."""
    trial_amount = models.DecimalField(
        max_digits=9, decimal_places=2, default=decimal.Decimal("0.00")
    )
    """Authorizenet subscription trial amount."""
    start_date = models.DateField(default=datetime.date.today)
    """Authorizenet subscription start date."""
    total_occurrences = models.PositiveIntegerField(default=9999)
    """Authorizenet subscription total occurrences."""
    trial_occurrences = models.PositiveIntegerField(default=0)
    """Authorizenet subscription trial occurrences."""
    interval_length = models.IntegerField(default=1, editable=False)
    """Authorizenet subscription interval length."""
    interval_unit = models.CharField(
        choices=[
            (apicontractsv1.ARBSubscriptionUnitEnum.days, _("Days")),
            (apicontractsv1.ARBSubscriptionUnitEnum.months, _("Months")),
        ],
        default=apicontractsv1.ARBSubscriptionUnitEnum.months,
        editable=False,
    )
    """Authorizenet subscription interval unit."""

    cprofile = models.ForeignKey(
        "terminusgps_payments.CustomerProfile",
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name=_("customer profile"),
    )
    """Associated customer profile."""
    pprofile = models.ForeignKey(
        "terminusgps_payments.CustomerPaymentProfile",
        on_delete=models.PROTECT,
        related_name="subscriptions",
        verbose_name=_("payment profile"),
    )
    """Associated payment profile."""
    aprofile = models.ForeignKey(
        "terminusgps_payments.CustomerAddressProfile",
        on_delete=models.PROTECT,
        related_name="subscriptions",
        verbose_name=_("address profile"),
    )
    """Associated customer profile."""

    class Meta:
        verbose_name = _("subscription")
        verbose_name_plural = _("subscriptions")

    def __str__(self) -> str:
        """Returns the subscription name."""
        return str(self.name)

    def get_absolute_url(self) -> str:
        """Returns a URL pointing to the subscription's detail view."""
        return reverse(
            "terminusgps_payments:detail subscriptions",
            kwargs={
                "customerprofile_pk": self.cprofile.pk,
                "subscription_pk": self.pk,
            },
        )

    @typing.override
    def create_in_authorizenet(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> int:
        try:
            contract = self._generate_arb_subscription()
            contract.paymentSchedule.interval = self._generate_interval()
            print(f"{contract.name = }")
            print(f"{contract.amount = }")
            print(f"{contract.trialAmount = }")
            print(f"{contract.paymentSchedule.totalOccurrences = }")
            print(f"{contract.paymentSchedule.trialOccurrences = }")
            print(f"{contract.paymentSchedule.startDate = }")
            print(f"{contract.paymentSchedule.interval.length = }")
            print(f"{contract.paymentSchedule.interval.unit = }")
            print(f"{contract.profile.customerProfileId = }")
            print(f"{contract.profile.customerAddressId = }")
            print(f"{contract.profile.customerPaymentProfileId = }")
            response = service.execute(
                api.create_subscription(subscription=contract),
                reference_id=reference_id,
            )
            return int(response.subscriptionId)
        except AuthorizenetControllerExecutionError as error:
            logger.critical(error)
            raise

    @typing.override
    def get_from_authorizenet(
        self,
        service: AuthorizenetService,
        reference_id: str | None = None,
        include_transactions: bool = False,
    ) -> ObjectifiedElement:
        try:
            return service.execute(
                api.get_subscription(
                    subscription_id=self.pk,
                    include_transactions=include_transactions,
                ),
                reference_id=reference_id,
            )
        except AuthorizenetControllerExecutionError as error:
            logger.critical(error)
            raise

    @typing.override
    def update_in_authorizenet(
        self,
        service: AuthorizenetService,
        update_fields: list[str] | None = None,
        reference_id: str | None = None,
    ) -> None:
        try:
            service.execute(
                api.update_subscription(
                    subscription_id=self.pk,
                    subscription=self._generate_arb_subscription(),
                ),
                reference_id=reference_id,
            )
        except AuthorizenetControllerExecutionError as error:
            logger.critical(error)
            raise

    @typing.override
    def delete_in_authorizenet(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> None:
        try:
            service.execute(
                api.cancel_subscription(subscription_id=self.pk),
                reference_id=reference_id,
            )
        except AuthorizenetControllerExecutionError as error:
            logger.critical(error)
            raise

    @typing.override
    def sync_with_authorizenet(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> None:
        pass

    def _generate_profile(self) -> apicontractsv1.customerProfileIdType:
        """Returns an Authorizenet customer profile id element."""
        profile = apicontractsv1.customerProfileIdType()
        profile.customerProfileId = str(self.cprofile.pk)
        profile.customerPaymentProfileId = str(self.pprofile.pk)
        profile.customerAddressId = str(self.aprofile.pk)
        return profile

    def _generate_interval(self) -> apicontractsv1.paymentScheduleTypeInterval:
        """Returns an Authorizenet payment schedule interval element."""
        interval = apicontractsv1.paymentScheduleTypeInterval()
        interval.length = str(self.interval_length)
        interval.unit = str(self.interval_unit)
        return interval

    def _generate_schedule(self) -> apicontractsv1.paymentScheduleType:
        """Returns an Authorizenet payment schedule element."""
        schedule = apicontractsv1.paymentScheduleType()
        schedule.startDate = self.start_date
        schedule.totalOccurrences = str(self.total_occurrences)
        schedule.trialOccurrences = str(self.trial_occurrences)
        return schedule

    def _generate_arb_subscription(self) -> apicontractsv1.ARBSubscriptionType:
        """Returns an Authorizenet ARBSubscription element."""
        arb_subscription = apicontractsv1.ARBSubscriptionType()
        arb_subscription.name = self.name
        arb_subscription.amount = self.amount
        arb_subscription.trialAmount = self.trial_amount
        arb_subscription.paymentSchedule = self._generate_schedule()
        arb_subscription.profile = self._generate_profile()
        return arb_subscription
