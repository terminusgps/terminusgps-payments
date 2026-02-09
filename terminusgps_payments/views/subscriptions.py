import datetime
import decimal
import typing

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.views.generic import UpdateView
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
)

from terminusgps_payments.models import (
    CustomerAddressProfile,
    CustomerPaymentProfile,
    Subscription,
)
from terminusgps_payments.views.generic import AuthorizenetCreateView
from terminusgps_payments.views.mixins import (
    AuthorizenetSingleObjectMixin,
    HtmxTemplateResponseMixin,
)


class SubscriptionCreateView(AuthorizenetCreateView):
    content_type = "text/html"
    fields = [
        "name",
        "interval_length",
        "interval_unit",
        "start_date",
        "total_occurrences",
        "trial_occurrences",
        "amount",
        "trial_amount",
        "customer_profile",
        "payment_profile",
        "address_profile",
    ]
    http_method_names = ["get", "post"]
    initial = {
        "amount": decimal.Decimal("24.95"),
        "name": "Terminus GPS Subscription",
        "total_occurrences": 9999,
        "trial_amount": decimal.Decimal("0.00"),
        "trial_occurrences": 0,
        "interval_length": 1,
        "interval_unit": Subscription.SubscriptionIntervalUnit.MONTHS,
    }
    model = Subscription
    template_name = "terminusgps_payments/subscription_create.html"

    def get_initial(self, **kwargs) -> dict[str, typing.Any]:
        initial: dict[str, typing.Any] = super().get_initial(**kwargs)
        initial["start_date"] = datetime.date.today()
        return initial

    def get_form(self, form_class=None) -> forms.Form:
        payment_qs = (
            CustomerPaymentProfile.objects.filter(
                customer_profile__user=self.request.user
            )
            if hasattr(self.request, "user")
            else CustomerPaymentProfile.objects.none()
        )
        address_qs = (
            CustomerAddressProfile.objects.filter(
                customer_profile__user=self.request.user
            )
            if hasattr(self.request, "user")
            else CustomerAddressProfile.objects.none()
        )

        form = super().get_form(form_class=form_class)
        form.fields["address_profile"].queryset = address_qs
        form.fields["payment_profile"].queryset = payment_qs
        form.fields["address_profile"].empty_label = None
        form.fields["payment_profile"].empty_label = None
        return form


class SubscriptionUpdateView(
    LoginRequiredMixin,
    AuthorizenetSingleObjectMixin,
    HtmxTemplateResponseMixin,
    UpdateView,
):
    content_type = "text/html"
    fields = ["payment_profile", "address_profile"]
    http_method_names = ["get", "post"]
    model = Subscription

    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        try:
            return super().form_valid(form=form)
        except AuthorizenetControllerExecutionError as error:
            form.add_error(
                None,
                ValidationError(
                    "%(error)s", code="invalid", params={"error": str(error)}
                ),
            )
            return self.form_invalid(form=form)

    def get_form(self, form_class=None) -> forms.Form:
        payment_qs = (
            CustomerPaymentProfile.objects.filter(
                customer_profile__user=self.request.user
            )
            if hasattr(self.request, "user")
            else CustomerPaymentProfile.objects.none()
        )
        address_qs = (
            CustomerAddressProfile.objects.filter(
                customer_profile__user=self.request.user
            )
            if hasattr(self.request, "user")
            else CustomerAddressProfile.objects.none()
        )

        form = super().get_form(form_class=form_class)
        form.fields["address_profile"].queryset = address_qs
        form.fields["payment_profile"].queryset = payment_qs
        form.fields["address_profile"].empty_label = None
        form.fields["payment_profile"].empty_label = None
        return form
