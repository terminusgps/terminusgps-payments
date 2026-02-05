from authorizenet import apicontractsv1
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from lxml.objectify import ObjectifiedElement
from terminusgps.authorizenet import api
from terminusgps.authorizenet.service import AuthorizenetService

from .base import AuthorizenetModel


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
