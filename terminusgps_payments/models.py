import abc
import datetime
import decimal
import logging

from authorizenet import apicontractsv1
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.dateparse import parse_date
from django.utils.translation import gettext_lazy as _
from lxml.objectify import ObjectifiedElement
from terminusgps.authorizenet import api
from terminusgps.authorizenet.service import AuthorizenetService

logger = logging.getLogger(__name__)


class AuthorizenetModel(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True, blank=True)
    """Authorizenet object id."""

    class Meta:
        abstract = True

    def save(self, **kwargs) -> None:
        service = kwargs.pop("service", AuthorizenetService())
        ref = kwargs.pop("reference_id", None)
        if not kwargs.pop("push", False) and self.pk:
            logger.debug(f"Syncing #{self.pk} with Authorizenet...")
            elem = self.pull(service, reference_id=ref)
            self.sync(elem)
            logger.debug(f"Synced #{self.pk} with Authorizenet.")
        else:
            resp = self.push(service, reference_id=ref)
            if not self.pk:
                self.pk = self._extract_authorizenet_id(resp)
            logger.debug(f"Pushed #{self.pk} to Authorizenet.")
        return super().save(**kwargs)

    @abc.abstractmethod
    def push(
        self,
        service: AuthorizenetService,
        reference_id: str | None = None,
        **kwargs,
    ) -> ObjectifiedElement:
        raise NotImplementedError("Subclasses must implement this method.")

    @abc.abstractmethod
    def pull(
        self,
        service: AuthorizenetService,
        reference_id: str | None = None,
        **kwargs,
    ) -> ObjectifiedElement:
        raise NotImplementedError("Subclasses must implement this method.")

    @abc.abstractmethod
    def sync(self, elem: ObjectifiedElement, **kwargs) -> None:
        raise NotImplementedError("Subclasses must implement this method.")

    @abc.abstractmethod
    def _extract_authorizenet_id(self, elem: ObjectifiedElement) -> int:
        raise NotImplementedError("Subclasses must implement this method.")

    @abc.abstractmethod
    def _delete_in_authorizenet(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> None:
        raise NotImplementedError("Subclasses must implement this method.")


class CustomerProfile(AuthorizenetModel):
    user = models.OneToOneField(
        get_user_model(),
        related_name="customer_profile",
        on_delete=models.CASCADE,
    )
    email = models.EmailField(blank=True, max_length=255)
    merchant_id = models.CharField(blank=True, max_length=20)
    description = models.TextField(blank=True, max_length=255)

    class Meta:
        verbose_name = _("customer profile")
        verbose_name_plural = _("customer profiles")

    def __str__(self) -> str:
        return (
            str(self.merchant_id)
            if self.merchant_id
            else f"CustomerProfile #{self.pk}"
        )

    def push(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> ObjectifiedElement:
        if not self.pk:
            request = api.create_customer_profile(
                merchant_id=str(self.merchant_id),
                email=str(self.email),
                description=str(self.description),
            )
        else:
            request = api.update_customer_profile(
                profile=apicontractsv1.customerProfileExType(
                    customerProfileId=str(self.pk),
                    merchantCustomerId=str(self.merchant_id),
                    description=str(self.description),
                    email=str(self.email),
                )
            )
        return service.execute(request, reference_id=reference_id)

    def pull(
        self,
        service: AuthorizenetService,
        reference_id: str | None = None,
        include_issuer_info: bool = False,
    ) -> ObjectifiedElement:
        request = api.get_customer_profile(
            customer_profile_id=self.pk,
            include_issuer_info=include_issuer_info,
        )
        return service.execute(request, reference_id=reference_id)

    def sync(self, elem: ObjectifiedElement) -> None:
        if hasattr(elem, "profile"):
            self.merchant_id = getattr(elem.profile, "merchantCustomerId", "")
            self.email = getattr(elem.profile, "email", "")
            self.description = getattr(elem.profile, "description", "")
        return

    def _delete_in_authorizenet(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> None:
        request = api.delete_customer_profile(customer_profile_id=self.pk)
        service.execute(request, reference_id=reference_id)
        return

    def _extract_authorizenet_id(self, elem: ObjectifiedElement) -> int:
        return int(getattr(elem, "customerProfileId"))


class CustomerAddressProfile(AuthorizenetModel):
    customer_profile = models.ForeignKey(
        "terminusgps_payments.CustomerProfile",
        on_delete=models.CASCADE,
        related_name="address_profiles",
    )

    is_default = models.BooleanField(default=False)
    first_name = models.CharField(blank=True, max_length=50)
    last_name = models.CharField(blank=True, max_length=50)
    company = models.CharField(blank=True, max_length=50)
    address = models.CharField(blank=True, max_length=60)
    city = models.CharField(blank=True, max_length=40)
    state = models.CharField(blank=True, max_length=40)
    zip = models.CharField(blank=True, max_length=20)
    country = models.CharField(blank=True, max_length=60)
    phone_number = models.CharField(blank=True, max_length=25)

    class Meta:
        verbose_name = _("address profile")
        verbose_name_plural = _("address profiles")

    def __str__(self) -> str:
        if self.address:
            return str(self.address)
        return f"CustomerAddressProfile #{self.pk}"

    def get_absolute_url(self) -> str:
        return reverse(
            "terminusgps_payments:detail address profiles",
            kwargs={"pk": self.pk},
        )

    def push(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> ObjectifiedElement:
        address = apicontractsv1.customerAddressType()
        address.firstName = str(self.first_name)
        address.lastName = str(self.last_name)
        address.company = str(self.company)
        address.address = str(self.address)
        address.city = str(self.city)
        address.state = str(self.state)
        address.zip = str(self.zip)
        address.country = str(self.country)
        address.phoneNumber = str(self.phone_number)

        if not self.pk:
            request = api.create_customer_shipping_address(
                customer_profile_id=self.customer_profile.pk,
                address=address,
                default=self.is_default,
            )
        else:
            request = api.update_customer_shipping_address(
                customer_profile_id=self.customer_profile.pk,
                address_profile_id=self.pk,
                address=address,
                default=self.is_default,
            )
        return service.execute(request, reference_id=reference_id)

    def pull(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> ObjectifiedElement:
        request = api.get_customer_shipping_address(
            customer_profile_id=self.customer_profile.pk,
            address_profile_id=self.pk,
        )
        return service.execute(request, reference_id=reference_id)

    def sync(self, elem: ObjectifiedElement) -> None:
        if hasattr(elem, "defaultShippingAddress"):
            self.is_default = bool(getattr(elem, "defaultShippingAddress"))
        if hasattr(elem, "address"):
            self.first_name = getattr(elem.address, "firstName", "")
            self.last_name = getattr(elem.address, "lastName", "")
            self.company = getattr(elem.address, "company", "")
            self.address = getattr(elem.address, "address", "")
            self.city = getattr(elem.address, "city", "")
            self.state = getattr(elem.address, "state", "")
            self.country = getattr(elem.address, "country", "")
            self.zip = getattr(elem.address, "zip", "")
            self.phone_number = getattr(elem.address, "phoneNumber", "")
        return

    def _extract_authorizenet_id(self, elem: ObjectifiedElement) -> int:
        return int(getattr(elem, "customerAddressId"))

    def _delete_in_authorizenet(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> None:
        request = api.delete_customer_shipping_address(
            customer_profile_id=self.customer_profile.pk,
            address_profile_id=self.pk,
        )
        service.execute(request, reference_id=reference_id)


class CustomerPaymentProfile(AuthorizenetModel):
    class ECheckType(models.TextChoices):
        PPD = "PPD", _("PPD")
        WEB = "WEB", _("WEB")
        CCD = "CCD", _("CCD")

    class AccountType(models.TextChoices):
        CHECKING = "checking", _("Checking")
        SAVINGS = "savings", _("Savings")
        BUSINESS_CHECKING = "businessChecking", _("Business checking")

    customer_profile = models.ForeignKey(
        "terminusgps_payments.CustomerProfile",
        on_delete=models.CASCADE,
        related_name="payment_profiles",
    )
    is_default = models.BooleanField(default=False)

    first_name = models.CharField(blank=True, max_length=50)
    last_name = models.CharField(blank=True, max_length=50)
    company = models.CharField(blank=True, max_length=50)
    address = models.CharField(blank=True, max_length=60)
    city = models.CharField(blank=True, max_length=40)
    state = models.CharField(blank=True, max_length=40)
    zip = models.CharField(blank=True, max_length=20)
    country = models.CharField(blank=True, max_length=60)
    phone_number = models.CharField(blank=True, max_length=25)

    card_number = models.CharField(blank=True, max_length=16)
    card_expiry = models.DateField(blank=True, default=None, null=True)
    card_code = models.CharField(blank=True, max_length=4)
    card_type = models.CharField(blank=True)

    account_type = models.CharField(blank=True, choices=AccountType.choices)
    account_number = models.CharField(blank=True, max_length=17)
    routing_number = models.CharField(blank=True, max_length=9)
    account_name = models.CharField(blank=True, max_length=22)
    echeck_type = models.CharField(blank=True, choices=ECheckType.choices)
    bank_name = models.CharField(blank=True, max_length=50)

    class Meta:
        verbose_name = _("payment profile")
        verbose_name_plural = _("payment profiles")

    def __str__(self) -> str:
        if self.card_number and self.card_type:
            return f"{self.card_type} {self.card_number}"
        elif self.account_type and self.bank_name:
            return f"{self.bank_name} {self.account_type}"
        else:
            return f"CustomerPaymentProfile #{self.pk}"

    def save(self, **kwargs) -> None:
        super().save(**kwargs)
        if self.pk and self.card_number:
            self.card_code = ""
            if not str(self.card_number).startswith("XXXX"):
                last_4 = str(self.card_number)[-4:]
                self.card_number = f"XXXX{last_4}"

    def get_absolute_url(self) -> str:
        return reverse(
            "terminusgps_payments:detail payment profiles",
            kwargs={"pk": self.pk},
        )

    def push(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> ObjectifiedElement:
        payment = apicontractsv1.paymentType()
        if self.card_number:
            payment.creditCard = apicontractsv1.creditCardType()
            payment.creditCard.cardNumber = str(self.card_number)
            if self.card_expiry is not None:
                payment.creditCard.expirationDate = self.card_expiry.strftime(
                    format="%Y-%m"
                )
            if self.card_code:
                payment.creditCard.cardCode = str(self.card_code)
        if all(
            [
                self.account_number,
                self.routing_number,
                self.account_name,
                self.bank_name,
                self.account_type,
                self.echeck_type,
            ]
        ):
            payment.bankAccount = apicontractsv1.bankAccountType()
            payment.bankAccount.accountType = str(self.account_type)
            payment.bankAccount.routingNumber = str(self.routing_number)
            payment.bankAccount.accountNumber = str(self.account_number)
            payment.bankAccount.nameOnAccount = str(self.account_name)
            payment.bankAccount.echeckType = str(self.echeck_type)
            payment.bankAccount.bankName = str(self.bank_name)

        address = apicontractsv1.customerAddressType()
        address.firstName = str(self.first_name)
        address.lastName = str(self.last_name)
        address.company = str(self.company)
        address.address = str(self.address)
        address.city = str(self.city)
        address.state = str(self.state)
        address.zip = str(self.zip)
        address.country = str(self.country)
        address.phoneNumber = str(self.phone_number)

        if not self.pk:
            request = api.create_customer_payment_profile(
                customer_profile_id=self.customer_profile.pk,
                payment=payment,
                address=address,
                default=self.is_default,
            )
        else:
            request = api.update_customer_payment_profile(
                customer_profile_id=self.customer_profile.pk,
                payment_profile_id=self.pk,
                payment=payment,
                address=address,
                default=self.is_default,
            )
        service.execute(request, reference_id=reference_id)

    def pull(
        self,
        service: AuthorizenetService,
        reference_id: str | None = None,
        include_issuer_info: bool = False,
    ) -> ObjectifiedElement:
        request = api.get_customer_payment_profile(
            customer_profile_id=self.customer_profile.pk,
            payment_profile_id=self.pk,
            include_issuer_info=include_issuer_info,
        )
        return service.execute(request, reference_id=reference_id)

    def sync(self, elem: ObjectifiedElement) -> None:
        if hasattr(elem, "defaultPaymentProfile"):
            self.is_default = bool(getattr(elem, "defaultPaymentProfile"))
        if hasattr(elem, "billTo"):
            self.first_name = getattr(elem.billTo, "firstName", "")
            self.last_name = getattr(elem.billTo, "lastName", "")
            self.company = getattr(elem.billTo, "company", "")
            self.address = getattr(elem.billTo, "address", "")
            self.city = getattr(elem.billTo, "city", "")
            self.state = getattr(elem.billTo, "state", "")
            self.country = getattr(elem.billTo, "country", "")
            self.zip = getattr(elem.billTo, "zip", "")
            self.phone_number = getattr(elem.billTo, "phoneNumber", "")
        if hasattr(elem, "paymentProfile"):
            if hasattr(elem.paymentProfile, "payment"):
                if hasattr(elem.paymentProfile.payment, "creditCard"):
                    ca = elem.paymentProfile.payment.creditCard
                    self.card_number = str(getattr(ca, "cardNumber", ""))
                    self.card_type = str(getattr(ca, "cardType", ""))
                if hasattr(elem.paymentProfile.payment, "bankAccount"):
                    ba = elem.paymentProfile.payment.bankAccount
                    self.account_type = str(getattr(ba, "accountType", ""))
                    self.account_number = str(getattr(ba, "accountNumber", ""))
                    self.routing_number = str(getattr(ba, "routingNumber", ""))
                    self.account_name = str(getattr(ba, "nameOnAccount", ""))
                    self.echeck_type = str(getattr(ba, "eCheckType", ""))
                    self.bank_name = str(getattr(ba, "bankName", ""))
        return

    def _extract_authorizenet_id(self, elem: ObjectifiedElement) -> int:
        return int(getattr(elem, "customerPaymentProfileId"))

    def _delete_in_authorizenet(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> None:
        request = api.delete_customer_payment_profile(
            customer_profile_id=self.customer_profile.pk,
            payment_profile_id=self.pk,
        )
        return service.execute(request, reference_id=reference_id)


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

    def __str__(self) -> str:
        return str(self.name) if self.name else f"Subscription #{self.pk}"

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
