import logging

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
            return str(self.pk)

    def save(self, **kwargs) -> None:
        super().save(**kwargs)
        if self.pk and self.card_number:
            self.card_code = ""
            if not str(self.card_number).startswith("XXXX"):
                self.card_number = f"XXXX{self.card_number[-4:]}"
        super().save(**kwargs)
        return

    def get_absolute_url(self) -> str:
        return reverse(
            "terminusgps_manager:detail payment profiles",
            kwargs={"pk": self.pk},
        )

    def delete(self, *args, **kwargs):
        logger.debug(f"Deleting #{self.pk} in Authorizenet...")
        service = AuthorizenetService()
        deleted = self._delete_in_authorizenet(service)
        logger.debug(
            f"Deleted #{self.pk} in Authorizenet."
            if deleted
            else f"Failed to delete #{self.pk} in Authorizenet. It was already gone."
        )
        return super().delete(*args, **kwargs)

    def _delete_in_authorizenet(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> bool:
        try:
            service.execute(
                api.delete_customer_payment_profile(
                    customer_profile_id=self.customer_profile.pk,
                    payment_profile_id=self.pk,
                ),
                reference_id=reference_id,
            )
            return True
        except AuthorizenetControllerExecutionError as error:
            if error.code == "E00040":
                return False
            else:
                raise

    def _extract_authorizenet_id(self, elem: ObjectifiedElement) -> int:
        return int(elem.customerPaymentProfileId)

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
            return service.execute(
                api.create_customer_payment_profile(
                    customer_profile_id=self.customer_profile.pk,
                    payment=payment,
                    address=address,
                    default=self.is_default,
                ),
                reference_id=reference_id,
            )
        else:
            return service.execute(
                api.update_customer_payment_profile(
                    customer_profile_id=self.customer_profile.pk,
                    payment_profile_id=self.pk,
                    payment=payment,
                    address=address,
                    default=self.is_default,
                ),
                reference_id=reference_id,
            )

    def pull(
        self,
        service: AuthorizenetService,
        reference_id: str | None = None,
        include_issuer_info: bool = False,
    ) -> ObjectifiedElement:
        return service.execute(
            api.get_customer_payment_profile(
                customer_profile_id=self.customer_profile.pk,
                payment_profile_id=self.pk,
                include_issuer_info=include_issuer_info,
            ),
            reference_id=reference_id,
        )

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
