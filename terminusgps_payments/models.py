import datetime
import decimal
import logging

from authorizenet import apicontractsv1
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.dateparse import parse_date
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from terminusgps.authorizenet import api
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
    AuthorizenetService,
)

logger = logging.getLogger(__name__)


class CustomerProfile(models.Model):
    id = models.PositiveBigIntegerField(
        primary_key=True, blank=True, editable=False
    )
    """Authorizenet customer profile id."""
    desc = models.TextField(
        max_length=1024, blank=True, verbose_name=_("description")
    )
    """Authorizenet customer profile description."""

    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="customer_profile",
    )
    """Associated Django user."""

    class Meta:
        verbose_name = _("customer profile")
        verbose_name_plural = _("customer profiles")

    def __str__(self) -> str:
        return f"{self.user}'s Customer Profile"

    @cached_property
    def merchant_id(self) -> str:
        return str(self.user.pk)

    @cached_property
    def email(self) -> str:
        return str(self.user.email)

    def get_absolute_url(self) -> str:
        """Returns a URL pointing to the customer profile's detail view."""
        return reverse(
            "terminusgps_payments:detail customer profiles",
            kwargs={"customerprofile_pk": self.pk},
        )

    def save(self, **kwargs) -> None:
        """Creates/updates the customer profile in Authorizenet before saving."""
        if not self.pk:
            anet_service = AuthorizenetService()
            self.id = self._create_in_authorizenet(anet_service)
            return super().save(**kwargs)

        anet_service = AuthorizenetService()
        self._update_in_authorizenet(anet_service)
        return super().save(**kwargs)

    def delete(self, *args, **kwargs):
        """Deletes the customer profile in Authorizenet before deleting it locally."""
        if not self.pk:
            return super().delete(*args, **kwargs)

        anet_service = AuthorizenetService()
        self._delete_in_authorizenet(anet_service)
        return super().delete(*args, **kwargs)

    def _create_in_authorizenet(self, service: AuthorizenetService) -> int:
        """Tries to create the customer profile in Authorizenet and return its id."""
        try:
            response = service.execute(
                api.create_customer_profile(
                    merchant_id=str(self.merchant_id),
                    email=str(self.email),
                    description=str(self.desc),
                )
            )
            return int(response.customerProfileId)
        except AuthorizenetControllerExecutionError as error:
            if error.code == "E00039":  # Duplicate record
                # Extract and return id from error message
                for part in str(error.message).split(" "):
                    if part.isdigit():
                        return int(part)
            raise

    def _update_in_authorizenet(self, service: AuthorizenetService) -> None:
        """Tries to update the customer profile in Authorizenet."""
        try:
            profile = apicontractsv1.customerProfileExType()
            profile.customerProfileId = str(self.pk)
            profile.merchantCustomerId = str(self.merchant_id)
            profile.email = str(self.email)
            profile.description = str(self.desc)
            service.execute(api.update_customer_profile(profile))
        except AuthorizenetControllerExecutionError:
            raise

    def _delete_in_authorizenet(self, service: AuthorizenetService) -> None:
        """Tries to delete the customer profile in Authorizenet."""
        try:
            cprofile_id = int(self.pk)
            service.execute(
                api.delete_customer_profile(customer_profile_id=cprofile_id)
            )
            return
        except AuthorizenetControllerExecutionError as e:
            if e.code == "E00040":
                logger.debug(
                    f"Failed to delete customer profile #{cprofile_id} in Authorizenet, it didn't exist (probably already deleted)."
                )
                return
            raise


class CustomerPaymentProfile(models.Model):
    id = models.PositiveBigIntegerField(
        primary_key=True, blank=True, editable=False
    )
    """Authorizenet customer payment profile id."""
    cprofile = models.ForeignKey(
        "terminusgps_payments.CustomerProfile",
        on_delete=models.CASCADE,
        related_name="payment_profiles",
        verbose_name=_("customer profile"),
    )
    """Associated Authorizenet customer profile."""
    default = models.BooleanField(default=False)
    """Whether the customer payment profile is set as default."""

    class Meta:
        verbose_name = _("payment profile")
        verbose_name_plural = _("payment profiles")

    def __str__(self) -> str:
        return f"CustomerPaymentProfile #{self.pk}"

    def get_absolute_url(self) -> str:
        return reverse(
            "terminusgps_payments:detail payment profiles",
            kwargs={
                "customerprofile_pk": self.cprofile.pk,
                "paymentprofile_pk": self.pk,
            },
        )

    def save(self, **kwargs) -> None:
        """Creates/updates the payment profile in Authorizenet before saving."""
        if not self.pk:
            anet_service = AuthorizenetService()
            self.id = self._create_in_authorizenet(anet_service)
            self._refresh_from_authorizenet(anet_service)
            return super().save(**kwargs)

        anet_service = AuthorizenetService()
        self._update_in_authorizenet(anet_service, kwargs.get("update_fields"))
        self._refresh_from_authorizenet(anet_service)
        return super().save(**kwargs)

    def delete(self, *args, **kwargs):
        """Deletes the payment profile in Authorizenet before deleting it locally."""
        if not self.pk:
            return super().delete(*args, **kwargs)

        anet_service = AuthorizenetService()
        self._delete_in_authorizenet(anet_service)
        return super().delete(*args, **kwargs)

    def _refresh_from_authorizenet(self, service: AuthorizenetService) -> None:
        """Tries to retrieve obfuscated data from Authorizenet to set locally."""
        try:
            response = service.execute(
                api.get_customer_payment_profile(
                    customer_profile_id=self.cprofile.pk,
                    payment_profile_id=self.pk,
                    include_issuer_info=True,
                )
            )
            self.payment = response.paymentProfile.payment
            self.address = response.paymentProfile.billTo
        except AuthorizenetControllerExecutionError:
            raise

    def _create_in_authorizenet(self, service: AuthorizenetService) -> int:
        """Tries to create the payment profile in Authorizenet and return its id."""
        try:
            response = service.execute(
                api.create_customer_payment_profile(
                    customer_profile_id=self.cprofile.pk,
                    payment=self.payment,
                    address=self.address,
                    default=self.default,
                    validation=settings.MERCHANT_AUTH_VALIDATION_MODE,
                )
            )
            return int(response.customerPaymentProfileId)
        except AuthorizenetControllerExecutionError as error:
            if error.code == "E00039":
                # TODO: Retrieve existing id from Authorizenet
                pass
            raise

    def _update_in_authorizenet(
        self,
        service: AuthorizenetService,
        update_fields: list[str] | None = None,
    ) -> None:
        """Tries to update the payment profile in Authorizenet."""
        try:
            kwargs = {
                "customer_profile_id": self.cprofile.pk,
                "payment_profile_id": self.pk,
                "validation": settings.MERCHANT_AUTH_VALIDATION_MODE,
            }
            if update_fields is None or "default" in update_fields:
                kwargs["default"] = self.default
            if update_fields is None or "payment" in update_fields:
                kwargs["payment"] = self.payment
            if update_fields is None or "address" in update_fields:
                kwargs["address"] = self.address

            service.execute(api.update_customer_payment_profile(**kwargs))
            return
        except AuthorizenetControllerExecutionError:
            raise

    def _delete_in_authorizenet(self, service: AuthorizenetService) -> None:
        """Tries to delete the payment profile in Authorizenet."""
        try:
            service.execute(
                api.delete_customer_payment_profile(
                    customer_profile_id=self.cprofile.pk,
                    payment_profile_id=self.pk,
                )
            )
            return
        except AuthorizenetControllerExecutionError as error:
            if error.code == "E00040":
                logger.debug(
                    f"Failed to delete payment profile #{self.pk} in Authorizenet. It was already deleted."
                )
                return
            raise


class CustomerAddressProfile(models.Model):
    id = models.PositiveBigIntegerField(
        primary_key=True, blank=True, editable=False
    )
    """Authorizenet customer address profile id."""
    cprofile = models.ForeignKey(
        "terminusgps_payments.CustomerProfile",
        on_delete=models.CASCADE,
        related_name="address_profiles",
        verbose_name=_("customer profile"),
    )
    """Associated Authorizenet customer profile."""
    default = models.BooleanField(default=False)
    """Whether the customer address profile is set as default."""

    class Meta:
        verbose_name = _("address profile")
        verbose_name_plural = _("address profiles")

    def __str__(self) -> str:
        return f"CustomerAddressProfile #{self.pk}"

    def get_absolute_url(self) -> str:
        return reverse(
            "terminusgps_payments:detail address profiles",
            kwargs={
                "customerprofile_pk": self.cprofile.pk,
                "addressprofile_pk": self.pk,
            },
        )

    def save(self, **kwargs) -> None:
        """Creates/updates the address profile in Authorizenet before saving."""
        if not self.pk:
            anet_service = AuthorizenetService()
            self.id = self._create_in_authorizenet(anet_service)
            self._refresh_from_authorizenet(anet_service)
            return super().save(**kwargs)

        anet_service = AuthorizenetService()
        self._update_in_authorizenet(anet_service)
        self._refresh_from_authorizenet(anet_service)
        return super().save(**kwargs)

    def delete(self, *args, **kwargs):
        """Deletes the address profile in Authorizenet before deleting it locally."""
        if not self.pk:
            return super().delete(*args, **kwargs)

        anet_service = AuthorizenetService()
        self._delete_in_authorizenet(anet_service)
        return super().delete(*args, **kwargs)

    def _refresh_from_authorizenet(self, service: AuthorizenetService) -> None:
        """Tries to retrieve obfuscated data from Authorizenet to set locally."""
        try:
            response = service.execute(
                api.get_customer_shipping_address(
                    customer_profile_id=self.cprofile.pk,
                    address_profile_id=self.pk,
                )
            )
            self.address = response.address
        except AuthorizenetControllerExecutionError:
            raise

    def _create_in_authorizenet(self, service: AuthorizenetService) -> int:
        """Tries to create the address profile in Authorizenet and return its id."""
        try:
            response = service.execute(
                api.create_customer_shipping_address(
                    customer_profile_id=self.cprofile.pk,
                    address=self.address,
                    default=self.default,
                )
            )
            return int(response.customerAddressId)
        except AuthorizenetControllerExecutionError as error:
            if error.code == "E00039":
                # TODO: Retrieve existing id from Authorizenet
                pass
            raise

    def _update_in_authorizenet(self, service: AuthorizenetService) -> None:
        """Tries to update the address profile in Authorizenet."""
        try:
            service.execute(
                api.update_customer_shipping_address(
                    customer_profile_id=self.cprofile.pk,
                    address_profile_id=self.pk,
                    address=self.address,
                    default=self.default,
                )
            )
        except AuthorizenetControllerExecutionError:
            raise

    def _delete_in_authorizenet(self, service: AuthorizenetService) -> None:
        """Tries to delete the address profile in Authorizenet."""
        try:
            service.execute(
                api.delete_customer_shipping_address(
                    customer_profile_id=self.cprofile.pk,
                    address_profile_id=self.pk,
                )
            )
        except AuthorizenetControllerExecutionError as error:
            if error.code == "E00040":
                logger.debug(
                    f"Failed to delete address profile #{self.pk} in Authorizenet. It was already deleted."
                )
                return
            raise


class Subscription(models.Model):
    class SubscriptionStatus(models.TextChoices):
        ACTIVE = "active", _("Active")
        """Subscription is active."""
        EXPIRED = "expired", _("Expired")
        """Subscription is expired."""
        SUSPENDED = "suspended", _("Suspended")
        """Subscription is suspended."""
        CANCELED = "canceled", _("Canceled")
        """Subscription is canceled."""
        TERMINATED = "terminated", _("Terminated")
        """Subscription is terminated."""
        UNKNOWN = "unknown", _("Unknown")
        """Subscription status is unknown."""

    id = models.PositiveBigIntegerField(
        primary_key=True, blank=True, editable=False
    )
    """Authorizenet subscription id."""
    name = models.CharField(max_length=64)
    """Authorizenet subscription name."""
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    """Authorizenet subscription amount."""
    status = models.CharField(
        max_length=12,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.UNKNOWN,
    )
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
        max_length=6,
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
        """Creates/updates the subscription in Authorizenet before saving."""
        anet_service = AuthorizenetService()
        if not self.id:
            self.id = self._create_in_authorizenet(anet_service)
            return super().save(**kwargs)

        self._update_in_authorizenet(anet_service, kwargs.get("update_fields"))
        return super().save(**kwargs)

    def delete(self, *args, **kwargs):
        """Deletes the subscription in Authorizenet before deleting it locally."""
        if not self.id:
            return super().delete(*args, **kwargs)

        anet_service = AuthorizenetService()
        self._delete_in_authorizenet(anet_service)
        return super().delete(*args, **kwargs)

    def get_contract(
        self, service: AuthorizenetService
    ) -> apicontractsv1.ARBSubscriptionType:
        """Returns the current subscription contract from Authorizenet."""
        if not self.pk:
            raise ValueError(f"Subscription pk is required, got '{self.pk}'.")

        try:
            response = service.execute(
                api.get_subscription(subscription_id=self.pk)
            )
        except AuthorizenetControllerExecutionError:
            raise

        name = response.subscription.name
        amount = response.subscription.amount[0]
        trial_amount = response.subscription.trialAmount[0]
        total_occur = response.subscription.paymentSchedule.totalOccurrences
        trial_occur = response.subscription.paymentSchedule.trialOccurrences
        start_date = parse_date(
            str(response.subscription.paymentSchedule.startDate[0])
        )
        cprofile_id = response.subscription.profile.customerProfileId
        pprofile_id = response.subscription.profile.paymentProfile.customerPaymentProfileId
        aprofile_id = (
            response.subscription.profile.shippingProfile.customerAddressId
        )

        contract = apicontractsv1.ARBSubscriptionType()
        contract.paymentSchedule = apicontractsv1.paymentScheduleType()
        contract.paymentSchedule.startDate = start_date
        contract.paymentSchedule.totalOccurrences = str(total_occur)
        contract.paymentSchedule.trialOccurrences = str(trial_occur)
        contract.profile = apicontractsv1.customerProfileIdType()
        contract.profile.customerProfileId = str(cprofile_id)
        contract.profile.customerPaymentProfileId = str(pprofile_id)
        contract.profile.customerAddressId = str(aprofile_id)
        contract.name = str(name)
        contract.amount = str(amount)
        contract.trialAmount = str(trial_amount)
        return contract

    def _create_in_authorizenet(self, service: AuthorizenetService) -> int:
        """Tries to create the subscription in Authorizenet and return its id."""
        schedule = self._generate_schedule()
        # Payment schedule interval is required for creation only
        schedule.interval = apicontractsv1.paymentScheduleTypeInterval()
        schedule.interval.length = str(self.interval_length)
        schedule.interval.unit = str(self.interval_unit)

        subscription = apicontractsv1.ARBSubscriptionType()
        subscription.name = str(self.name)
        subscription.amount = str(self.amount)
        subscription.trialAmount = str(self.trial_amount)
        subscription.profile = self._generate_profile()
        subscription.paymentSchedule = schedule

        try:
            response = service.execute(api.create_subscription(subscription))
            return int(response.subscriptionId)
        except AuthorizenetControllerExecutionError as error:
            if error.code == "E00012":
                # TODO: Retrieve ID from error code?
                pass
            raise

    def _update_in_authorizenet(
        self,
        service: AuthorizenetService,
        update_fields: list[str] | None = None,
    ) -> None:
        """Tries to update the subscription in Authorizenet."""
        try:
            contract = self.get_contract(service)
            if update_fields is None or any(
                [
                    "cprofile" in update_fields,
                    "pprofile" in update_fields,
                    "aprofile" in update_fields,
                ]
            ):
                contract.profile = self._generate_profile()
            if update_fields is None or any(
                [
                    "start_date" in update_fields,
                    "total_occurrences" in update_fields,
                    "trial_occurrences" in update_fields,
                ]
            ):
                contract.paymentSchedule = self._generate_schedule()
            if update_fields is None or "name" in update_fields:
                contract.name = str(self.name)
            if update_fields is None or "amount" in update_fields:
                contract.amount = str(self.amount)
            if update_fields is None or "trial_amount" in update_fields:
                contract.trialAmount = str(self.trial_amount)
            service.execute(
                api.update_subscription(
                    subscription_id=self.pk, subscription=contract
                )
            )
        except AuthorizenetControllerExecutionError:
            # TODO: Error logging
            raise

    def _delete_in_authorizenet(self, service: AuthorizenetService) -> None:
        """Tries to delete the subscription in Authorizenet."""
        try:
            service.execute(api.cancel_subscription(subscription_id=self.pk))
        except AuthorizenetControllerExecutionError:
            # TODO: Error logging
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
