import typing

from terminusgps_payments.forms import (
    SubscriptionCreateForm,
    SubscriptionUpdateForm,
)
from terminusgps_payments.models import CustomerProfile, Subscription
from terminusgps_payments.views.generic import (
    AuthorizenetCreateView,
    AuthorizenetUpdateView,
)


class SubscriptionCreateView(AuthorizenetCreateView):
    form_class = SubscriptionCreateForm
    model = Subscription
    template_name = "terminusgps_payments/subscription_create.html"

    def get_form_kwargs(self) -> dict[str, typing.Any]:
        try:
            customer_profile = (
                CustomerProfile.objects.get(user=self.request.user)
                if hasattr(self.request, "user")
                else None
            )
        except CustomerProfile.DoesNotExist:
            customer_profile = None

        kwargs = super().get_form_kwargs()
        kwargs["customer_profile"] = customer_profile
        return kwargs


class SubscriptionUpdateView(AuthorizenetUpdateView):
    form_class = SubscriptionUpdateForm
    model = Subscription
    template_name = "terminusgps_payments/subscription_update.html"

    def get_form_kwargs(self) -> dict[str, typing.Any]:
        try:
            customer_profile = (
                CustomerProfile.objects.get(user=self.request.user)
                if hasattr(self.request, "user")
                else None
            )
        except CustomerProfile.DoesNotExist:
            customer_profile = None

        kwargs = super().get_form_kwargs()
        kwargs["customer_profile"] = customer_profile
        return kwargs
