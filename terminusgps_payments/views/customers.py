import typing

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from terminusgps.authorizenet import profiles
from terminusgps.django.mixins import HtmxTemplateResponseMixin

from terminusgps_payments.models import CustomerProfile


class CustomerAccountView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    http_method_names = ["get"]
    partial_template_name = (
        "terminusgps_payments/customers/partials/_account.html"
    )
    template_name = "terminusgps_payments/customers/account.html"
    extra_context = {"title": "Account"}

    def get_customer_profile(self) -> CustomerProfile:
        """Returns an Authorizenet customer profile for the request user."""
        try:
            user = self.request.user
            return CustomerProfile.objects.get(user=user)
        except CustomerProfile.DoesNotExist:
            response = profiles.create_customer_profile(
                merchant_id=user.pk,
                email=user.email,
                description=f"{user.first_name} {user.last_name}",
            )
            return CustomerProfile.objects.create(
                id=int(response.customerProfileId), user=user
            )

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["profile"] = (
            self.get_customer_profile().get_authorizenet_profile()
        )
        return context
