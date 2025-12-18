import decimal
import logging
import pickle

from authorizenet import apicontractsv1
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from lxml.objectify import ObjectifiedElement
from terminusgps.authorizenet import api
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
    AuthorizenetService,
)

logger = logging.getLogger(__name__)


class ObjectifiedElementField(models.BinaryField):
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return pickle.loads(value)

    def to_python(self, value):
        if isinstance(value, ObjectifiedElement):
            return value
        if value is None:
            return None
        return pickle.loads(value)

    def get_prep_value(self, value):
        if value is None:
            return None
        return pickle.dumps(value)


class AuthorizenetPaymentField(ObjectifiedElementField):
    description = _("An Authorizenet payment element")


class AuthorizenetAddressField(ObjectifiedElementField):
    description = _("An Authorizenet address element")


class AuthorizenetPaymentScheduleField(ObjectifiedElementField):
    description = _("An Authorizenet payment schedule element")


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

    def save(self, **kwargs) -> None:
        """Creates/updates the customer profile in Authorizenet before saving."""
        anet_service = AuthorizenetService()
        if not self.pk:
            self.id = self._create_in_authorizenet(anet_service)
            return super().save(**kwargs)

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
    default = models.BooleanField(default=False)
    """Whether the customer payment profile is set as default."""
    payment = AuthorizenetPaymentField()
    """Authorizenet payment element."""
    address = AuthorizenetAddressField()
    """Authorizenet address element."""

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
        return reverse(
            "terminusgps_payments:detail payment profiles",
            kwargs={
                "customerprofile_pk": self.cprofile.pk,
                "paymentprofile_pk": self.pk,
            },
        )

    def save(self, **kwargs) -> None:
        """Creates/updates the payment profile in Authorizenet before saving."""
        anet_service = AuthorizenetService()
        if not self.pk:
            self.id = self._create_in_authorizenet(anet_service)
            return super().save(**kwargs)

        self._update_in_authorizenet(anet_service)
        return super().save(**kwargs)

    def delete(self, *args, **kwargs):
        """Deletes the payment profile in Authorizenet before deleting it locally."""
        if not self.pk:
            return super().delete(*args, **kwargs)

        anet_service = AuthorizenetService()
        self._delete_in_authorizenet(anet_service)
        return super().delete(*args, **kwargs)

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

    def _update_in_authorizenet(self, service: AuthorizenetService) -> None:
        """Tries to update the payment profile in Authorizenet."""
        try:
            service.execute(
                api.update_customer_payment_profile(
                    customer_profile_id=self.cprofile.pk,
                    payment_profile_id=self.pk,
                    payment=self.payment,
                    address=self.address,
                    default=self.default,
                    validation=settings.MERCHANT_AUTH_VALIDATION_MODE,
                )
            )
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
    default = models.BooleanField(default=False)
    """Whether the customer address profile is set as default."""
    address = AuthorizenetAddressField()
    """Authorizenet address element."""

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
        return reverse(
            "terminusgps_payments:detail address profiles",
            kwargs={
                "customerprofile_pk": self.cprofile.pk,
                "addressprofile_pk": self.pk,
            },
        )

    def save(self, **kwargs) -> None:
        """Creates/updates the address profile in Authorizenet before saving."""
        anet_service = AuthorizenetService()
        if not self.pk:
            self.id = self._create_in_authorizenet(anet_service)
            return super().save(**kwargs)

        self._update_in_authorizenet(anet_service)
        return super().save(**kwargs)

    def delete(self, *args, **kwargs):
        """Deletes the address profile in Authorizenet before deleting it locally."""
        if not self.pk:
            return super().delete(*args, **kwargs)

        anet_service = AuthorizenetService()
        self._delete_in_authorizenet(anet_service)
        return super().delete(*args, **kwargs)

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
    id = models.PositiveBigIntegerField(
        primary_key=True, blank=True, editable=False
    )
    """Authorizenet subscription id."""
    name = models.CharField(max_length=64)
    """Authorizenet subscription name."""
    schedule = AuthorizenetPaymentScheduleField()
    """Authorizenet subscription payment schedule."""
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    """Authorizenet subscription amount."""
    trial_amount = models.DecimalField(
        max_digits=9, decimal_places=2, default=decimal.Decimal("0.00")
    )
    """Authorizenet subscription trial amount."""

    cprofile = models.ForeignKey(
        "terminusgps_payments.CustomerProfile",
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    """Associated customer profile."""
    pprofile = models.ForeignKey(
        "terminusgps_payments.CustomerPaymentProfile",
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    """Associated payment profile."""
    aprofile = models.ForeignKey(
        "terminusgps_payments.CustomerAddressProfile",
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    """Associated customer profile."""

    class Meta:
        verbose_name = _("subscription")
        verbose_name_plural = _("subscriptions")

    def __str__(self) -> str:
        return str(self.name)
