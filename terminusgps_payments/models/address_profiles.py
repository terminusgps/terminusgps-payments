import logging
import typing

from authorizenet import apicontractsv1
from django.db import models, transaction
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


class CustomerAddressProfile(AuthorizenetModel):
    cprofile = models.ForeignKey(
        "terminusgps_payments.CustomerProfile",
        on_delete=models.CASCADE,
        related_name="address_profiles",
        verbose_name=_("customer profile"),
    )
    """Associated Authorizenet customer profile."""
    default = models.BooleanField(default=False)

    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=60, blank=True)
    company_name = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=40, blank=True)
    state = models.CharField(max_length=40, blank=True)
    zip = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=60, blank=True)
    phone_number = models.CharField(max_length=25, blank=True)

    class Meta:
        verbose_name = _("address profile")
        verbose_name_plural = _("address profiles")

    def __str__(self) -> str:
        return str(self.address) if self.address else str(self.pk)

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
    def create_in_authorizenet(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> int:
        try:
            response = service.execute(
                api.create_customer_shipping_address(
                    customer_profile_id=self.cprofile.pk,
                    address=self._generate_address(),
                    default=self.default,
                )
            )
            return int(response.customerAddressId)
        except AuthorizenetControllerExecutionError as error:
            logger.critical(error)
            raise

    @typing.override
    def get_from_authorizenet(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> ObjectifiedElement:
        try:
            return service.execute(
                api.get_customer_shipping_address(
                    customer_profile_id=self.cprofile.pk,
                    address_profile_id=self.pk,
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
            service.execute(
                api.update_customer_shipping_address(
                    customer_profile_id=self.cprofile.pk,
                    address_profile_id=self.pk,
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
                api.delete_customer_shipping_address(
                    customer_profile_id=self.cprofile.pk,
                    address_profile_id=self.pk,
                ),
                reference_id=reference_id,
            )
        except AuthorizenetControllerExecutionError as error:
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
            self._sync_address(response.address)
        except AuthorizenetControllerExecutionError as error:
            logger.critical(error)
            raise

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
        if self.first_name:
            address.firstName = self.first_name
        if self.last_name:
            address.lastName = self.last_name
        if self.address:
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
