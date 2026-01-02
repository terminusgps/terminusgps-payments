import logging
import typing

from authorizenet import apicontractsv1
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from terminusgps.authorizenet import api
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
    AuthorizenetService,
)

from .base import AuthorizenetModel

logger = logging.getLogger(__name__)


class CustomerProfile(AuthorizenetModel):
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="customer_profile",
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
                    merchant_id=str(self.user.pk),
                    email=str(self.user.email),
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
        include_issuer_info: bool = False,
        reference_id: str | None = None,
    ) -> apicontractsv1.customerProfileExType:
        """Returns a :py:obj:`~authorizenet.apicontractsv1.customerProfileExType` element for the customer profile."""
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
        self,
        service: AuthorizenetService,
        update_fields: list[str] | None = None,
        include_issuer_info: bool = False,
        reference_id: str | None = None,
    ) -> None:
        """Tries to update the customer profile in Authorizenet."""
        try:
            profile = self._generate_profile(service, reference_id)
            if update_fields is None or "user" in update_fields:
                profile.merchantCustomerId = str(self.user.pk)
                profile.email = str(self.user.email)
            if update_fields is None or "desc" in update_fields:
                profile.description = str(self.desc)
            service.execute(
                api.update_customer_profile(profile=profile),
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
                logger.debug(
                    f"Tried to delete customer profile #{self.pk} but it didn't exist. It was probably already deleted."
                )
                return
            logger.critical(str(error))
            raise

    def _generate_profile(
        self, service: AuthorizenetService, reference_id: str | None = None
    ) -> apicontractsv1.customerProfileExType:
        """Returns an Authorizenet customer profile ex element."""
        response = self.get_from_authorizenet(
            service, include_issuer_info=False, reference_id=reference_id
        )
        profile = apicontractsv1.customerProfileExType()
        profile.customerProfileId = str(response.profile.customerProfileId)
        profile.merchantCustomerId = str(response.profile.merchantCustomerId)
        profile.email = str(response.profile.email)
        profile.description = str(response.profile.description)
        return profile
