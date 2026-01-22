import logging

from authorizenet import apicontractsv1
from django.db import models
from django.utils.translation import gettext_lazy as _
from lxml.objectify import ObjectifiedElement
from terminusgps.authorizenet import api
from terminusgps.authorizenet.service import AuthorizenetService

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
        if self.pk:
            self.card_code = ""
            if self.card_number:
                self.card_number = f"XXXX{self.card_number[-4:]}"
        super().save(**kwargs)
        return

    def _extract_id(self, elem: ObjectifiedElement) -> int:
        return int(elem.customerPaymentProfileId)

    def push(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> ObjectifiedElement:
        payment = apicontractsv1.paymentType()
        if all([self.card_number, self.card_expiry]):
            payment.creditCard = apicontractsv1.creditCardType()
            payment.creditCard.cardNumber = str(self.card_number)
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
            payment.bankAccount.accountNumber = str(self.account_number)
            payment.bankAccount.routingNumber = str(self.routing_number)
            payment.bankAccount.nameOnAccount = str(self.account_name)
            payment.bankAccount.bankName = str(self.bank_name)
            payment.bankAccount.accountType = str(self.account_type)
            payment.bankAccount.eCheckType = str(self.echeck_type)

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

    def sync(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> None:
        resp = self.pull(service, reference_id=reference_id)
        if hasattr(resp, "defaultPaymentProfile"):
            self.is_default = bool(resp.defaultPaymentProfile)
        if hasattr(resp, "paymentProfile"):
            if hasattr(resp.paymentProfile, "billTo"):
                elem = resp.paymentProfile.billTo
                self.first_name = str(getattr(elem, "firstName", ""))
                self.last_name = str(getattr(elem, "lastName", ""))
                self.company = str(getattr(elem, "company", ""))
                self.address = str(getattr(elem, "address", ""))
                self.city = str(getattr(elem, "city", ""))
                self.state = str(getattr(elem, "state", ""))
                self.country = str(getattr(elem, "country", ""))
                self.zip = str(getattr(elem, "zip", ""))
                self.phone_number = str(getattr(elem, "phoneNumber", ""))
            if hasattr(resp.paymentProfile, "payment"):
                if hasattr(resp.paymentProfile.payment, "creditCard"):
                    elem = resp.paymentProfile.payment.creditCard
                    self.card_number = getattr(elem, "cardNumber", "")
                    self.card_type = getattr(elem, "cardType", "")
                if hasattr(resp.paymentProfile.payment, "bankAccount"):
                    elem = resp.paymentProfile.payment.bankAccount
                    self.account_type = getattr(elem, "accountType", "")
                    self.account_number = getattr(elem, "accountNumber", "")
                    self.routing_number = getattr(elem, "routingNumber", "")
                    self.account_name = getattr(elem, "nameOnAccount", "")
                    self.echeck_type = getattr(elem, "eCheckType", "")
                    self.bank_name = getattr(elem, "bankName", "")
        return
