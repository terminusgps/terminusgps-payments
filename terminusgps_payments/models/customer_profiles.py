from authorizenet import apicontractsv1
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
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

    def _extract_authorizenet_id(self, elem: ObjectifiedElement) -> int:
        return int(elem.customerProfileId)

    def push(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> ObjectifiedElement:
        if not self.pk:
            return service.execute(
                api.create_customer_profile(
                    merchant_id=str(self.merchant_id),
                    email=str(self.email),
                    description=str(self.description),
                ),
                reference_id=reference_id,
            )
        else:
            profile = apicontractsv1.customerProfileExType()
            profile.customerProfileId = str(self.pk)
            profile.merchantCustomerId = str(self.merchant_id)
            profile.description = str(self.description)
            profile.email = str(self.email)
            return service.execute(
                api.update_customer_profile(profile=profile),
                reference_id=reference_id,
            )

    def pull(
        self,
        service: AuthorizenetService,
        reference_id: str | None = None,
        include_issuer_info: bool = False,
    ) -> ObjectifiedElement:
        return service.execute(
            api.get_customer_profile(
                customer_profile_id=self.pk,
                include_issuer_info=include_issuer_info,
            ),
            reference_id=reference_id,
        )

    def sync(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> None:
        resp = self.pull(service, reference_id=reference_id)
        self.merchant_id = str(resp.profile.merchantCustomerId)
        self.email = str(resp.profile.email)
        self.description = str(resp.profile.description)
        return
