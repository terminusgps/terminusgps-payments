import typing

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest
from django.utils.module_loading import import_string
from terminusgps.authorizenet.service import AuthorizenetService

from terminusgps_payments.models import CustomerProfile


class AuthorizenetServiceMixin:
    """
    Adds an Authorizenet service to the view's :py:attr:`service` attribute.

    Passes `service_kwargs` to the service initializer if provided.

    """

    service_kwargs: dict[str, typing.Any] | None = None

    def get_service_class(self) -> type[AuthorizenetService]:
        if not hasattr(settings, "AUTHORIZENET_SERVICE"):
            raise ImproperlyConfigured(
                "'AUTHORIZENET_SERVICE' setting is required."
            )
        try:
            return import_string(settings.AUTHORIZENET_SERVICE)
        except ImportError as error:
            raise ImproperlyConfigured(error)

    def get_service_kwargs(self) -> dict[str, typing.Any]:
        return (
            self.service_kwargs.copy()
            if self.service_kwargs is not None
            else {}
        )

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        service_class = self.get_service_class()
        service_kwargs = self.get_service_kwargs()
        self.service = service_class(**service_kwargs)


class CustomerProfileMixin:
    """Adds an authenticated user's customer profile to the view's :py:attr:`customer_profile` attribute."""

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.customer_profile = self.get_customer_profile(request)

    @staticmethod
    def get_customer_profile(request) -> CustomerProfile | None:
        if not hasattr(request, "user"):
            return
        if request.user.is_anonymous:
            return
        try:
            return CustomerProfile.objects.get(user=request.user)
        except CustomerProfile.DoesNotExist:
            return
