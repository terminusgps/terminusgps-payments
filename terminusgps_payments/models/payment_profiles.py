import logging
import typing

from authorizenet import apicontractsv1
from django.db import models, transaction
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from lxml.objectify import ObjectifiedElement
from terminusgps.authorizenet import api
from terminusgps.authorizenet.constants import BankAccountType
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
    AuthorizenetService,
)

from .base import AuthorizenetModel

logger = logging.getLogger(__name__)


class CustomerPaymentProfile(AuthorizenetModel):
    cprofile = models.ForeignKey(
        "terminusgps_payments.CustomerProfile",
        on_delete=models.CASCADE,
        related_name="payment_profiles",
        verbose_name=_("customer profile"),
    )
    """Associated Authorizenet customer profile."""
    default = models.BooleanField(default=False)
    """Whether the payment profile is set as default."""

    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=60, blank=True)
    company_name = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=40, blank=True)
    state = models.CharField(max_length=40, blank=True)
    zip = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=60, blank=True)
    phone_number = models.CharField(max_length=25, blank=True)

    card_number = models.CharField(max_length=16, blank=True)
    expiry_date = models.DateField(blank=True)
    card_code = models.CharField(max_length=4, blank=True, null=True)
    card_type = models.CharField(blank=True)

    account_number = models.CharField(max_length=9, blank=True)
    routing_number = models.CharField(max_length=17, blank=True)
    account_name = models.CharField(max_length=22, blank=True)
    bank_name = models.CharField(max_length=50, blank=True)
    account_type = models.CharField(
        choices=BankAccountType.choices, blank=True
    )

    class Meta:
        verbose_name = _("payment profile")
        verbose_name_plural = _("payment profiles")

    def __str__(self) -> str:
        if self.card_number:
            return (
                f"{self.card_type} {self.card_number}"
                if self.card_type
                else str(self.card_number)
            )
        elif self.account_number:
            return (
                f"{self.bank_name} {self.account_number}"
                if self.bank_name
                else str(self.account_number)
            )
        else:
            return str(self.pk)

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
    def save(self, **kwargs) -> None:
        super().save(**kwargs)
        if self.pk and self.card_number:
            last_4 = self.card_number[-4:]
            self.card_number = f"XXXX{last_4}"
            self.card_code = None
        super().save(**kwargs)

    @typing.override
    def create_in_authorizenet(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> int:
        try:
            response = service.execute(
                api.create_customer_payment_profile(
                    customer_profile_id=self.cprofile.pk,
                    payment=self._generate_payment(),
                    address=self._generate_address(),
                    default=self.default,
                )
            )
            return int(response.customerPaymentProfileId)
        except AuthorizenetControllerExecutionError as error:
            logger.critical(error)
            raise

    @typing.override
    def get_from_authorizenet(
        self,
        service: AuthorizenetService,
        reference_id: str | None = None,
        include_issuer_info: bool = False,
    ) -> ObjectifiedElement:
        try:
            return service.execute(
                api.get_customer_payment_profile(
                    customer_profile_id=self.cprofile.pk,
                    payment_profile_id=self.pk,
                    include_issuer_info=include_issuer_info,
                ),
                reference_id=reference_id,
            )
        except AuthorizenetControllerExecutionError as error:
            logger.critical(error)
            raise

    @typing.override
    def update_in_authorizenet(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> None:
        try:
            return service.execute(
                api.update_customer_payment_profile(
                    customer_profile_id=self.cprofile.pk,
                    payment_profile_id=self.pk,
                    payment=self._generate_payment(),
                    address=self._generate_address(),
                    default=self.default,
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
                api.delete_customer_payment_profile(
                    customer_profile_id=self.cprofile.pk,
                    payment_profile_id=self.pk,
                ),
                reference_id=reference_id,
            )
        except AuthorizenetControllerExecutionError as error:
            if error.code == "E00040":
                logger.warning(
                    f"Tried to delete payment profile #{self.pk} but it didn't exist. It was probably already deleted."
                )
                return
            logger.critical(error)
            raise

    @typing.override
    def sync_with_authorizenet(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> None:
        try:
            response = self.get_from_authorizenet(
                service, reference_id=reference_id
            )
            self._sync_payment(response.paymentProfile.payment)
            self._sync_address(response.paymentProfile.billTo)
        except AuthorizenetControllerExecutionError as error:
            logger.critical(error)
            raise

    @transaction.atomic
    def _sync_payment(self, payment: apicontractsv1.paymentType) -> None:
        if card := getattr(payment, "creditCard", None):
            if self.card_number != str(card.cardNumber):
                self.card_number = str(card.cardNumber)
            if self.card_type != str(card.cardType):
                self.card_type = str(card.cardType)
            if self.card_code is not None:
                self.card_code = None
        if bank := getattr(payment, "bankAccount", None):
            self.account_number = str(bank.accountNumber)
            self.routing_number = str(bank.routingNumber)
            self.account_name = str(bank.nameOnAccount)
            self.bank_name = str(bank.bankName)
            self.account_type = str(bank.accountType)

    @transaction.atomic
    def _sync_address(
        self, address: apicontractsv1.customerAddressType
    ) -> None:
        if hasattr(address, "firstName"):
            self.first_name = str(address.firstName)
        if hasattr(address, "lastName"):
            self.last_name = str(address.lastName)
        if hasattr(address, "address"):
            self.address = str(address.address)
        if hasattr(address, "company"):
            self.company_name = str(address.company)
        if hasattr(address, "city"):
            self.city = str(address.city)
        if hasattr(address, "state"):
            self.state = str(address.state)
        if hasattr(address, "zip"):
            self.zip = str(address.zip)
        if hasattr(address, "country"):
            self.country = str(address.country)
        if hasattr(address, "phoneNumber"):
            self.phone_number = str(address.phoneNumber)

    def _generate_address(self) -> apicontractsv1.customerAddressType:
        address = apicontractsv1.customerAddressType()
        address.firstName = self.first_name
        address.lastName = self.last_name
        address.address = self.address
        if self.company_name:
            address.company = self.company_name
        if self.city:
            address.city = self.city
        if self.state:
            address.state = self.state
        if self.zip:
            address.zip = self.zip
        if self.country:
            address.country = self.country
        if self.phone_number:
            address.phoneNumber = self.phone_number
        return address

    def _generate_payment(self) -> apicontractsv1.paymentType:
        """Returns an Authorizenet paymentType element."""
        payment = apicontractsv1.paymentType()
        has_credit_card = all([self.card_number, self.expiry_date])
        has_bank_account = all([self.account_number, self.routing_number])
        if not any([has_credit_card, has_bank_account]):
            raise ValueError

        if has_credit_card:
            payment.creditCard = apicontractsv1.creditCardType()
            payment.creditCard.cardNumber = self.card_number
            payment.creditCard.expirationDate = self.expiry_date.strftime(
                "%Y-%m"
            )
            if self.card_code is not None:
                payment.creditCard.cardCode = self.card_code
        elif has_bank_account:
            payment.bankAccount = apicontractsv1.bankAccountType()
            payment.bankAccount.accountNumber = self.account_number
            payment.bankAccount.routingNumber = self.routing_number
            payment.bankAccount.echeckType = "PPD"
            if self.account_name:
                payment.bankAccount.nameOnAccount = self.account_name
            if self.bank_name:
                payment.bankAccount.bankName = self.bank_name
            if self.account_type:
                payment.bankAccount.accountType = self.account_type
        return payment
