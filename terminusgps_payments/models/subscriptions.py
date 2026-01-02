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
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name=_("payment profile"),
    )
    """Associated payment profile."""
    aprofile = models.ForeignKey(
        "terminusgps_payments.CustomerAddressProfile",
        on_delete=models.CASCADE,
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

    def save(self, **kwargs) -> None:
        """Refreshes the subscription status from Authorizenet before saving."""
        if self.pk:
            service = AuthorizenetService()
            self.status = self.get_status(service)
        return super().save(**kwargs)

    def get_status(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> str:
        """Tries to return the current subscription status from Authorizenet."""
        try:
            response = self.get_from_authorizenet(
                service, reference_id=reference_id
            )
            return str(response.subscription.status)
        except AuthorizenetControllerExecutionError as error:
            logger.critical(error)
            raise

    def get_transactions(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> ObjectifiedElement:
        try:
            response = self.get_from_authorizenet(
                service, include_transactions=True, reference_id=reference_id
            )
            print(f"{dir(response) = }")
            return response
        except AuthorizenetControllerExecutionError as error:
            logger.critical(error)
            raise

    @typing.override
    def create_in_authorizenet(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> int:
        try:
            interval = apicontractsv1.paymentScheduleTypeInterval()
            interval.length = str(self.interval_length)
            interval.unit = str(self.interval_unit)
            subscription = self._generate_contract()
            subscription.paymentSchedule.interval = interval
            response = service.execute(
                api.create_subscription(subscription=subscription),
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
        include_transactions: bool = False,
        reference_id: str | None = None,
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
                    subscription=self._generate_contract(),
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

    def _generate_profile(self) -> apicontractsv1.customerProfileIdType:
        """Returns an Authorizenet customer profile id element."""
        profile = apicontractsv1.customerProfileIdType()
        profile.customerProfileId = str(self.cprofile.pk)
        profile.customerPaymentProfileId = str(self.pprofile.pk)
        profile.customerAddressId = str(self.aprofile.pk)
        return profile

    def _generate_schedule(self) -> apicontractsv1.paymentScheduleType:
        """Returns an Authorizenet payment schedule element."""
        schedule = apicontractsv1.paymentScheduleType()
        schedule.startDate = self.start_date
        schedule.totalOccurrences = str(self.total_occurrences)
        schedule.trialOccurrences = str(self.trial_occurrences)
        return schedule

    def _generate_contract(self) -> apicontractsv1.ARBSubscriptionType:
        """Returns an Authorizenet ARBSubscription element."""
        contract = apicontractsv1.ARBSubscriptionType()
        contract.name = self.name
        contract.amount = self.amount
        contract.trialAmount = self.trial_amount
        contract.paymentSchedule = self._generate_schedule()
        contract.profile = self._generate_profile()
        return contract
