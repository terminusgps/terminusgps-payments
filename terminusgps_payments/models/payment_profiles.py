import logging
import typing

from django.db import models
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


class CustomerPaymentProfile(AuthorizenetModel):
    cprofile = models.ForeignKey(
        "terminusgps_payments.CustomerProfile",
        on_delete=models.CASCADE,
        related_name="payment_profiles",
        verbose_name=_("customer profile"),
    )
    """Associated Authorizenet customer profile."""

    class Meta:
        verbose_name = _("payment profile")
        verbose_name_plural = _("payment profiles")

    def __str__(self) -> str:
        return f"CustomerPaymentProfile #{self.pk}"

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
    def create_in_authorizenet(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> None:
        return

    @typing.override
    def get_from_authorizenet(
        self,
        service: AuthorizenetService,
        include_issuer_info: bool = False,
        reference_id: str | None = None,
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
        self,
        service: AuthorizenetService,
        update_fields: list[str] | None = None,
        reference_id: str | None = None,
    ) -> None:
        return

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
            logger.critical(error)
            raise
