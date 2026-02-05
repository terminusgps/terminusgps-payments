from authorizenet import apicontractsv1
from django.db import models
from django.urls import reverse
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
