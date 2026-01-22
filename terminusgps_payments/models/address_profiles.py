import logging

from authorizenet import apicontractsv1
from django.db import models
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

    def delete(self, *args, **kwargs):
        if not self.pk:
            return super().delete(*args, **kwargs)
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
                api.delete_customer_shipping_address(
                    customer_profile_id=self.customer_profile.pk,
                    address_profile_id=self.pk,
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
