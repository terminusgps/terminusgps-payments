from authorizenet import apicontractsv1
from django.db import models
from django.utils.translation import gettext_lazy as _
from lxml.objectify import ObjectifiedElement
from terminusgps.authorizenet import api
from terminusgps.authorizenet.service import AuthorizenetService

from .base import AuthorizenetModel


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
            return self.address
        return str(self.pk)

    def _extract_id(self, elem: ObjectifiedElement) -> int:
        return int(elem.customerAddressId)

    def _get_contract(self) -> apicontractsv1.customerAddressType:
        contract = apicontractsv1.customerAddressType()
        contract.firstName = str(self.first_name)
        contract.lastName = str(self.last_name)
        contract.company = str(self.company)
        contract.address = str(self.address)
        contract.city = str(self.city)
        contract.state = str(self.state)
        contract.zip = str(self.zip)
        contract.country = str(self.country)
        contract.phoneNumber = str(self.phone_number)
        return contract

    def push(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> ObjectifiedElement:
        if not self.pk:
            return service.execute(
                api.create_customer_shipping_address(
                    customer_profile_id=self.customer_profile.pk,
                    address=self._get_contract(),
                    default=self.is_default,
                ),
                reference_id=reference_id,
            )
        else:
            return service.execute(
                api.update_customer_shipping_address(
                    customer_profile_id=self.customer_profile.pk,
                    address_profile_id=self.pk,
                    address=self._get_contract(),
                    default=self.is_default,
                ),
                reference_id=reference_id,
            )

    def pull(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> ObjectifiedElement:
        return service.execute(
            api.get_customer_shipping_address(
                customer_profile_id=self.customer_profile.pk,
                address_profile_id=self.pk,
            ),
            reference_id=reference_id,
        )

    def sync(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> None:
        resp = self.pull(service, reference_id=reference_id)
        if hasattr(resp, "defaultShippingAddress"):
            self.is_default = bool(resp.defaultShippingAddress)
        if hasattr(resp, "address"):
            elem = resp.address
            self.first_name = str(getattr(elem, "firstName", ""))
            self.last_name = str(getattr(elem, "lastName", ""))
            self.company = str(getattr(elem, "company", ""))
            self.address = str(getattr(elem, "address", ""))
            self.city = str(getattr(elem, "city", ""))
            self.state = str(getattr(elem, "state", ""))
            self.country = str(getattr(elem, "country", ""))
            self.zip = str(getattr(elem, "zip", ""))
            self.phone_number = str(getattr(elem, "phoneNumber", ""))
        return
