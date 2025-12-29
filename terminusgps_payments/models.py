import abc
import datetime
import decimal
import logging
import typing

from authorizenet import apicontractsv1
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from lxml.objectify import ObjectifiedElement
from terminusgps.authorizenet import api
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
    AuthorizenetService,
)

logger = logging.getLogger(__name__)


class AuthorizenetModel(models.Model):
    id = models.PositiveBigIntegerField(
        primary_key=True, blank=True, editable=False
    )
    """Authorizenet object id."""

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        """Deletes the object in Authorizenet before deleting."""
        if not self.pk:
            return super().delete(*args, **kwargs)
        service = AuthorizenetService()
        self.delete_in_authorizenet(service)
        return super().delete(*args, **kwargs)

    @abc.abstractmethod
    def create_in_authorizenet(
        self, service: AuthorizenetService, **kwargs
    ) -> int:
        """Tries to create the object in Authorizenet and returns its id."""
        raise NotImplementedError("Subclasses must implement this method.")

    @abc.abstractmethod
    def get_from_authorizenet(
        self, service: AuthorizenetService, **kwargs
    ) -> ObjectifiedElement:
        """Tries to retrieve fresh object data from Authorizenet and returns it."""
        raise NotImplementedError("Subclasses must implement this method.")

    @abc.abstractmethod
    def update_in_authorizenet(
        self,
        service: AuthorizenetService,
        update_fields: list[str] | None = None,
        **kwargs,
    ) -> None:
        """Tries to update the object in Authorizenet."""
        raise NotImplementedError("Subclasses must implement this method.")

    @abc.abstractmethod
    def delete_in_authorizenet(
        self, service: AuthorizenetService, **kwargs
    ) -> None:
        """Tries to delete the object in Authorizenet."""
        raise NotImplementedError("Subclasses must implement this method.")


class CustomerProfile(AuthorizenetModel):
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="customer_profile",
    )
    """Django user."""
    desc = models.TextField(
        max_length=1024, blank=True, verbose_name=_("description")
    )
    """Customer profile description."""

    class Meta:
        verbose_name = _("customer profile")
        verbose_name_plural = _("customer profiles")

    def __str__(self) -> str:
        return f"{self.user}'s Profile"

    @property
    def merchant_id(self) -> str:
        return str(self.user.pk)

    @property
    def email(self) -> str:
        return str(self.user.email)

    def get_absolute_url(self) -> str:
        """Returns a URL pointing to the customer profile's detail view."""
        return reverse(
            "terminusgps_payments:detail customer profiles",
            kwargs={"customerprofile_pk": self.pk},
        )

    def save(self, **kwargs) -> None:
        """Creates or updates the customer profile in Authorizenet before saving."""
        service = AuthorizenetService()
        if not self.pk:
            self.id = self.create_in_authorizenet(service)
        self.update_in_authorizenet(service, kwargs.get("update_fields"))
        return super().save(**kwargs)

    @typing.override
    def create_in_authorizenet(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> int:
        """Tries to create the customer profile in Authorizenet and return its id."""
        try:
            response = service.execute(
                api.create_customer_profile(
                    merchant_id=str(self.merchant_id),
                    email=str(self.email),
                    description=str(self.desc),
                ),
                reference_id=reference_id,
            )
            return int(response.customerProfileId)
        except AuthorizenetControllerExecutionError as error:
            if error.code == "E00039":  # Duplicate record
                # Extract and return id from error message
                for part in str(error.message).split(" "):
                    if part.isdigit():
                        return int(part)
            raise

    @typing.override
    def update_in_authorizenet(
        self,
        service: AuthorizenetService,
        update_fields: list[str] | None = None,
        include_issuer_info: bool = False,
        reference_id: str | None = None,
    ) -> None:
        """Tries to update the customer profile in Authorizenet."""
        try:
            profile = self.get_from_authorizenet(service, include_issuer_info)
            if update_fields is None or "user" in update_fields:
                profile.merchantCustomerId = str(self.merchant_id)
                profile.email = str(self.email)
            if update_fields is None or "desc" in update_fields:
                profile.description = str(self.desc)
            service.execute(
                api.update_customer_profile(profile=profile),
                reference_id=reference_id,
            )
        except AuthorizenetControllerExecutionError as error:
            logger.critical(str(error))
            raise

    @typing.override
    def delete_in_authorizenet(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> None:
        """Tries to delete the customer profile in Authorizenet."""
        try:
            service.execute(
                api.delete_customer_profile(customer_profile_id=self.pk),
                reference_id=reference_id,
            )
        except AuthorizenetControllerExecutionError as error:
            if error.code == "E00040":
                logger.debug(
                    f"Tried to delete customer profile #{self.pk} but it didn't exist. It was probably already deleted."
                )
                return
            logger.critical(str(error))
            raise

    @typing.override
    def get_from_authorizenet(
        self,
        service: AuthorizenetService,
        include_issuer_info: bool = False,
        reference_id: str | None = None,
    ) -> apicontractsv1.customerProfileExType:
        """Returns a :py:obj:`~authorizenet.apicontractsv1.customerProfileExType` element for the customer profile."""
        try:
            response = service.execute(
                api.get_customer_profile(
                    customer_profile_id=int(self.pk),
                    include_issuer_info=include_issuer_info,
                ),
                reference_id=reference_id,
            )
        except AuthorizenetControllerExecutionError as error:
            logger.critical(str(error))
            raise

        profile = apicontractsv1.customerProfileExType()
        profile.customerProfileId = str(response.profile.customerProfileId)
        profile.merchantCustomerId = str(response.profile.merchantCustomerId)
        profile.email = str(response.profile.email)
        profile.description = str(response.profile.description)
        return profile


class CustomerPaymentProfile(AuthorizenetModel):
    id = models.PositiveBigIntegerField(primary_key=True, blank=True)
    """Authorizenet address profile id."""
    cprofile = models.ForeignKey(
        "terminusgps_payments.CustomerProfile",
        on_delete=models.CASCADE,
        related_name="payment_profiles",
        verbose_name=_("customer profile"),
    )
    """Associated Authorizenet customer profile."""

    class Meta:
        verbose_name = _("payment profile")
        verbose_name_plural = _("payment profiles")

    def __str__(self) -> str:
        return f"CustomerPaymentProfile #{self.pk}"

    def get_absolute_url(self) -> str:
        """Returns a URL pointing to the payment profile's detail view."""
        return reverse(
            "terminusgps_payments:detail payment profiles",
            kwargs={
                "customerprofile_pk": self.cprofile.pk,
                "paymentprofile_pk": self.pk,
            },
        )

    @typing.override
    def get_from_authorizenet(
        self,
        service: AuthorizenetService,
        include_issuer_info: bool = False,
        reference_id: str | None = None,
    ) -> ObjectifiedElement:
        try:
            response = service.execute(
                api.get_customer_payment_profile(
                    customer_profile_id=self.cprofile.pk,
                    payment_profile_id=self.pk,
                    include_issuer_info=include_issuer_info,
                ),
                reference_id=reference_id,
            )
            return response.paymentProfile
        except AuthorizenetControllerExecutionError as error:
            logger.critical(error)
            raise

    @typing.override
    def delete_in_authorizenet(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> None:
        try:
            service.execute(
                api.delete_customer_payment_profile(
                    customer_profile_id=self.cprofile.pk,
                    payment_profile_id=self.pk,
                ),
                reference_id=reference_id,
            )
        except AuthorizenetControllerExecutionError as error:
            logger.critical(error)
            raise


class CustomerAddressProfile(AuthorizenetModel):
    id = models.PositiveBigIntegerField(primary_key=True, blank=True)
    """Authorizenet address profile id."""
    cprofile = models.ForeignKey(
        "terminusgps_payments.CustomerProfile",
        on_delete=models.CASCADE,
        related_name="address_profiles",
        verbose_name=_("customer profile"),
    )
    """Associated Authorizenet customer profile."""

    class Meta:
        verbose_name = _("address profile")
        verbose_name_plural = _("address profiles")

    def __str__(self) -> str:
        return f"CustomerAddressProfile #{self.pk}"

    def get_absolute_url(self) -> str:
        """Returns a URL pointing to the address profile's detail view."""
        return reverse(
            "terminusgps_payments:detail address profiles",
            kwargs={
                "customerprofile_pk": self.cprofile.pk,
                "addressprofile_pk": self.pk,
            },
        )

    @typing.override
    def get_from_authorizenet(
        self,
        service: AuthorizenetService,
        include_issuer_info: bool = False,
        reference_id: str | None = None,
    ) -> ObjectifiedElement:
        try:
            response = service.execute(
                api.get_customer_shipping_address(
                    customer_profile_id=self.cprofile.pk,
                    address_profile_id=self.pk,
                ),
                reference_id=reference_id,
            )
            return response.address
        except AuthorizenetControllerExecutionError as error:
            logger.critical(error)
            raise

    @typing.override
    def delete_in_authorizenet(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> None:
        try:
            service.execute(
                api.delete_customer_shipping_address(
                    customer_profile_id=self.cprofile.pk,
                    address_profile_id=self.pk,
                ),
                reference_id=reference_id,
            )
        except AuthorizenetControllerExecutionError as error:
            logger.critical(error)
            raise


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
    interval_length = models.IntegerField(default=1)
    """Authorizenet subscription interval length."""
    interval_unit = models.CharField(
        choices=[
            (apicontractsv1.ARBSubscriptionUnitEnum.days, _("Days")),
            (apicontractsv1.ARBSubscriptionUnitEnum.months, _("Months")),
        ],
        default=apicontractsv1.ARBSubscriptionUnitEnum.months,
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

    def save(self, **kwargs) -> None:
        """Creates or updates the subscription in Authorizenet before saving."""
        service = AuthorizenetService()
        if not self.pk:
            self.id = self.create_in_authorizenet(service)
        self.update_in_authorizenet(service, kwargs.get("update_fields"))
        return super().save(**kwargs)

    @typing.override
    def create_in_authorizenet(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> int:
        try:
            interval = apicontractsv1.paymentScheduleTypeInterval()
            interval.length = str(self.interval_length)
            interval.unit = str(self.interval_unit)
            schedule = self._generate_schedule()
            schedule.interval = interval

            subscription = apicontractsv1.ARBSubscriptionType()
            subscription.name = str(self.name)
            subscription.paymentSchedule = schedule
            subscription.amount = self.amount
            subscription.trialAmount = self.trial_amount
            subscription.profile = self._generate_profile()

            response = service.execute(
                api.create_subscription(subscription=subscription)
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
            response = service.execute(
                api.get_subscription(
                    subscription_id=self.pk,
                    include_transactions=include_transactions,
                ),
                reference_id=reference_id,
            )
            return response.subscription
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
            subscription = self.get_from_authorizenet(
                service, reference_id=reference_id
            )
            if update_fields is None or "name" in update_fields:
                subscription.name = str(self.name)
            if update_fields is None or "amount" in update_fields:
                subscription.amount = self.amount
            if update_fields is None or "trial_amount" in update_fields:
                subscription.trialAmount = self.trial_amount
            if update_fields is None or any(
                [
                    "start_date" in update_fields,
                    "total_occurrences" in update_fields,
                    "trial_occurrences" in update_fields,
                ]
            ):
                subscription.paymentSchedule = self._generate_schedule()
            if update_fields is None or any(
                [
                    "cprofile" in update_fields,
                    "aprofile" in update_fields,
                    "pprofile" in update_fields,
                ]
            ):
                subscription.profile = self._generate_profile()

            service.execute(
                api.update_subscription(
                    subscription_id=self.pk, subscription=subscription
                )
            )
        except AuthorizenetControllerExecutionError as error:
            logger.critical(error)
            raise

    @typing.override
    def delete_in_authorizenet(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> None:
        try:
            service.execute(api.cancel_subscription(subscription_id=self.pk))
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
