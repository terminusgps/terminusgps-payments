import decimal
import typing

from django import forms
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
)

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
    name = _("Terminus GPS Subscription")
    amount = decimal.Decimal("24.95")

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context = super().get_context_data(**kwargs)
        context["name"] = self.name
        context["amount"] = self.amount
        return context

    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        try:
            self.object = form.save(commit=False)
            self.object.name = self.name
            self.object.amount = self.amount
            self.object.save(push=True)
            return HttpResponseRedirect(self.get_success_url())
        except AuthorizenetControllerExecutionError as error:
            match error.code:
                case _:
                    form.add_error(
                        None,
                        ValidationError(
                            "%(error)s",
                            code="invalid",
                            params={"error": error},
                        ),
                    )
            return self.form_invalid(form=form)

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
