import collections.abc

from authorizenet import apicontractsv1
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from terminusgps.authorizenet import api as anet
from terminusgps.authorizenet import constants


class SubscriptionScheduleInterval(models.Model):
    name = models.CharField(max_length=64)
    """Subscription schedule interval name."""
    unit = models.CharField(
        max_length=6,
        choices=constants.AuthorizenetSubscriptionIntervalUnit.choices,
        default=constants.AuthorizenetSubscriptionIntervalUnit.MONTHS,
    )
    """Subscription schedule interval unit."""
    length = models.IntegerField(default=1)
    """Subscription schedule interval length."""

    def __str__(self) -> str:
        """Returns the subscription schedule interval name."""
        return self.name

    def to_xml(self) -> apicontractsv1.paymentScheduleTypeInterval:
        """Returns the schedule interval as an instance of :py:obj:`~authorizenet.apicontractsv1.paymentScheduleTypeInterval`."""
        return apicontractsv1.paymentScheduleTypeInterval(
            length=self.length, unit=self.unit
        )


class SubscriptionSchedule(models.Model):
    interval = models.ForeignKey(
        "terminusgps_payments.SubscriptionScheduleInterval",
        on_delete=models.RESTRICT,
        related_name="schedules",
    )
    """Authorizenet subscription interval."""
    start_date = models.DateTimeField(default=timezone.now)
    """Authorizenet subscription schedule start date."""
    total_occurrences = models.IntegerField(default=9999)
    """Authorizenet subscription schedule total occurrences."""
    trial_occurrences = models.IntegerField(default=0)
    """Authorizenet subscription schedule trial occurrences."""

    def __str__(self) -> str:
        """Returns 'Schedule #<pk>'."""
        return f"Schedule #{self.pk}"

    def to_xml(self) -> apicontractsv1.paymentScheduleType:
        """Returns the schedule as an instance of :py:obj:`~authorizenet.apicontractsv1.paymentScheduleType`."""
        return apicontractsv1.paymentScheduleType(
            interval=self.interval.to_xml(),
            startDate=self.start_date,
            totalOccurrences=self.total_occurrences,
            trialOccurrences=self.trial_occurrences,
        )


class Subscription(models.Model):
    """An Authorizenet subscription."""

    id = models.PositiveBigIntegerField(primary_key=True)
    """Authorizenet subscription id."""
    schedule = models.OneToOneField(
        "terminusgps_payments.SubscriptionSchedule",
        on_delete=models.CASCADE,
        related_name="subscription",
    )
    """Associated subscription schedule."""
    customer_profile = models.ForeignKey(
        "terminusgps_payments.CustomerProfile",
        on_delete=models.RESTRICT,
        related_name="subscriptions",
    )
    """Associated customer profile."""
    payment_profile = models.ForeignKey(
        "terminusgps_payments.PaymentProfile",
        on_delete=models.RESTRICT,
        related_name="subscriptions",
    )
    """Associated payment profile."""
    address_profile = models.ForeignKey(
        "terminusgps_payments.AddressProfile",
        on_delete=models.RESTRICT,
        related_name="subscriptions",
    )
    """Associated address profile."""

    name = models.CharField(max_length=31)
    """Authorizenet subscription name."""
    amount = models.DecimalField(max_digits=9, decimal_places=2, default=24.99)
    """Authorizenet subscription amount."""
    trial_amount = models.DecimalField(
        max_digits=9, decimal_places=2, default=0.00
    )
    """Authorizenet subscription trial amount."""
    status = models.CharField(
        max_length=12,
        default=constants.AuthorizenetSubscriptionStatus.ACTIVE,
        choices=constants.AuthorizenetSubscriptionStatus.choices,
    )
    """Authorizenet subscription status."""

    def __str__(self) -> str:
        """Returns the subscription's name or 'Subscription #<pk>'."""
        return str(self.name) if self.name else f"Subscription #{self.pk}"

    def get_absolute_url(self) -> str:
        return reverse(
            "payments:detail subscription", kwargs={"subscription_pk": self.pk}
        )

    def to_xml(
        self, fields: collections.abc.Collection[str] | None = None
    ) -> apicontractsv1.ARBSubscriptionType:
        xml = apicontractsv1.ARBSubscriptionType()
        if fields is None:
            # Add all fields to return value
            fields = [
                "name",
                "schedule",
                "amount",
                "trial_amount",
                "payment_profile",
                "address_profile",
            ]

        if "name" in fields:
            xml.name = self.name
        if "schedule" in fields:
            xml.paymentSchedule = self.schedule.to_xml()
        if "amount" in fields:
            xml.amount = self.amount
        if "trial_amount" in fields:
            xml.trialAmount = self.trial_amount
        if "address_profile" in fields or "payment_profile" in fields:
            sub_profile = apicontractsv1.customerProfileIdType()
            sub_profile.customerProfileId = str(self.customer_profile.pk)
            sub_profile.customerAddressId = str(self.address_profile.pk)
            sub_profile.customerPaymentProfileId = str(self.payment_profile.pk)
            xml.profile = sub_profile
        return xml

    @transaction.atomic
    def refresh_status(self) -> str | None:
        """Retrieves the subscription's current status from Authorizenet, sets it and returns it."""
        if new_status := self.get_anet_status():
            self.status = new_status
            return new_status

    def get_anet_status(self) -> str | None:
        """Returns the subscription's status from Authorizenet."""
        if self.pk:
            response = anet.get_subscription_status(subscription_id=self.pk)
            if response is not None and hasattr(response, "status"):
                return str(response.status)

    def get_anet_subscription(self, include_transactions: bool = False):
        """Returns the subscription from Authorizenet."""
        if self.pk:
            return anet.get_subscription(
                subscription_id=self.pk,
                include_transactions=include_transactions,
            )
