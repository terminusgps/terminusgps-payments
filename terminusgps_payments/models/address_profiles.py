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

    def _extract_id(self, elem: ObjectifiedElement) -> int:
        return int(elem.customerAddressId)

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
            return service.execute(
                api.create_customer_shipping_address(
                    customer_profile_id=self.customer_profile.pk,
                    address=address,
                    default=self.is_default,
                ),
                reference_id=reference_id,
            )
        else:
            return service.execute(
                api.update_customer_shipping_address(
                    customer_profile_id=self.customer_profile.pk,
                    address_profile_id=self.pk,
                    address=address,
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
        self.first_name = str(resp.address.firstName)
        self.last_name = str(resp.address.lastName)
        self.address = str(resp.address.address)
        self.city = str(resp.address.city)
        self.state = str(resp.address.state)
        self.zip = str(resp.address.zip)
        self.country = str(resp.address.country)
        if company := getattr(resp.address, "company", None):
            self.company = str(company)
        if phone := getattr(resp.address, "phoneNumber", None):
            self.phone_number = str(phone)
        if default := getattr(resp, "defaultShippingAddress", None):
            self.is_default = bool(default)
        return
