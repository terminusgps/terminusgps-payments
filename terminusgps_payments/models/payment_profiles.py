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
        self.is_default = bool(resp.paymentProfile.defaultPaymentProfile)
        self.first_name = str(resp.paymentProfile.billTo.firstName)
        self.last_name = str(resp.paymentProfile.billTo.lastName)
        self.company = str(resp.paymentProfile.billTo.company)
        self.address = str(resp.paymentProfile.billTo.address)
        self.city = str(resp.paymentProfile.billTo.city)
        self.state = str(resp.paymentProfile.billTo.state)
        self.zip = str(resp.paymentProfile.billTo.zip)
        self.country = str(resp.paymentProfile.billTo.country)
        self.phone_number = str(resp.paymentProfile.billTo.phoneNumber)
        if card := getattr(resp.paymentProfile.payment, "creditCard", None):
            self.card_number = str(card.cardNumber)
            self.card_type = str(card.cardType)
        if acc := getattr(resp.paymentProfile.payment, "bankAccount", None):
            self.account_type = str(acc.accountType)
            self.routing_number = str(acc.routingNumber)
            self.account_number = str(acc.accountNumber)
            self.account_name = str(acc.nameOnAccount)
            self.echeck_type = str(acc.eCheckType)
            self.bank_name = str(acc.bankName)
        return
