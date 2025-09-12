from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from terminusgps.authorizenet import api
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
    AuthorizenetService,
)


class CustomerProfile(models.Model):
    """An Authorizenet customer profile."""

    id = models.BigIntegerField(primary_key=True)
    """Authorizenet customer profile id."""
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    """Associated user."""

    class Meta:
        verbose_name = _("customer profile")
        verbose_name_plural = _("customer profiles")

    def __str__(self) -> str:
        """Returns the customer's username."""
        return self.user.username

    def save(self, **kwargs) -> None:
        """Creates the customer profile in Authorizenet based on the user if :py:attr:`id` wasn't set."""
        if not self.pk:
            try:
                service = AuthorizenetService()
                response = service.call_api(
                    *api.create_customer_profile(
                        merchant_id=self.merchant_id,
                        email=self.email,
                        description=self.description,
                    )
                )
                self.pk = int(response.customerProfileId)
            except AuthorizenetControllerExecutionError:
                raise
        return super().save(**kwargs)

    @property
    def merchant_id(self) -> str:
        """Merchant-designated id for Authorizenet API calls."""
        return str(self.user.pk)

    @property
    def email(self) -> str:
        """Customer email address."""
        return self.user.email

    @property
    def description(self) -> str:
        """Customer full name (first + last)."""
        return f"{self.user.first_name} {self.user.last_name}"
