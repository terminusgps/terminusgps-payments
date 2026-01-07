import logging
import typing

from authorizenet import apicontractsv1
from django.contrib.auth import get_user_model
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


class CustomerProfile(AuthorizenetModel):
    user = models.OneToOneField(
        get_user_model(), on_delete=models.CASCADE, related_name="cprofile"
    )
    """Django user."""
    desc = models.TextField(
        max_length=1024, blank=True, verbose_name=_("description")
    )
    """Customer profile description."""

    class Meta:
        verbose_name = _("customer profile")
        verbose_name_plural = _("customer profiles")

    def __str__(self) -> str:
        """Returns the customer profile user."""
        return str(self.user)

    @property
    def merchant_id(self) -> str:
        """Returns the customer profile merchant id."""
        return str(self.user.pk)

    @property
    def email(self) -> str:
        """Returns the customer profile email."""
        return str(self.user.email)

    def get_absolute_url(self) -> str:
        """Returns a URL pointing to the customer profile's detail view."""
        return reverse(
            "terminusgps_payments:detail customer profiles",
            kwargs={"customerprofile_pk": self.pk},
        )

    @typing.override
    def create_in_authorizenet(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> int:
        """Tries to create the customer profile in Authorizenet and return its id."""
        try:
            response = service.execute(
                api.create_customer_profile(
                    merchant_id=self.merchant_id,
                    email=self.email,
                    description=str(self.desc),
                ),
                reference_id=reference_id,
            )
            return int(response.customerProfileId)
        except AuthorizenetControllerExecutionError as error:
            if error.code == "E00039":  # Duplicate record
                # Extract and return id from error message
                for part in str(error.message).split(" "):
                    if part.isdigit():
                        return int(part)
            raise

    @typing.override
    def get_from_authorizenet(
        self,
        service: AuthorizenetService,
        reference_id: str | None = None,
        include_issuer_info: bool = False,
    ) -> ObjectifiedElement:
        """Returns the customer profile data from Authorizenet."""
        try:
            return service.execute(
                api.get_customer_profile(
                    customer_profile_id=int(self.pk),
                    include_issuer_info=include_issuer_info,
                ),
                reference_id=reference_id,
            )
        except AuthorizenetControllerExecutionError as error:
            logger.critical(str(error))
            raise

    @typing.override
    def update_in_authorizenet(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> None:
        """Tries to update the customer profile in Authorizenet."""
        try:
            service.execute(
                api.update_customer_profile(profile=self._generate_profile()),
                reference_id=reference_id,
            )
        except AuthorizenetControllerExecutionError as error:
            logger.critical(str(error))
            raise

    @typing.override
    def delete_in_authorizenet(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> None:
        """Tries to delete the customer profile in Authorizenet."""
        try:
            service.execute(
                api.delete_customer_profile(customer_profile_id=self.pk),
                reference_id=reference_id,
            )
        except AuthorizenetControllerExecutionError as error:
            if error.code == "E00040":
                logger.warning(
                    f"Tried to delete customer profile #{self.pk} but it didn't exist. It was probably already deleted."
                )
                return
            logger.critical(str(error))
            raise

    def _generate_profile(self) -> apicontractsv1.customerProfileExType:
        """Returns an Authorizenet customer profile ex element."""
        profile = apicontractsv1.customerProfileExType()
        profile.merchantCustomerId = self.merchant_id
        profile.email = self.email
        profile.description = self.desc
        profile.customerProfileId = str(self.pk)
        return profile
