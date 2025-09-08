from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _


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
