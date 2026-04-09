import typing

from django.http import HttpRequest
from terminusgps.authorizenet.service import AuthorizenetService

from terminusgps_payments.models import CustomerProfile


class AuthorizenetServiceMixin:
    """Adds Authorizenet service to the view's :py:attr:`service` attribute."""

    service_class: type[AuthorizenetService] = AuthorizenetService
    service_kwargs: dict[str, typing.Any] = {}

    def get_service_class(self) -> type[AuthorizenetService]:
        return self.service_class

    def get_service_kwargs(self) -> dict[str, typing.Any]:
        return self.service_kwargs.copy()

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
