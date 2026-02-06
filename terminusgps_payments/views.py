import datetime
import decimal
import typing

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
)

from .mixins import (
    AuthorizenetMultipleObjectMixin,
    AuthorizenetSingleObjectMixin,
    HtmxTemplateResponseMixin,
)
from .models import (
    CustomerAddressProfile,
    CustomerPaymentProfile,
    CustomerProfile,
    Subscription,
)


class AuthorizenetCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, CreateView
):
    content_type = "text/html"
    form_class = None
    http_method_names = ["get", "post"]
    model = None

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

    def get_initial(self, **kwargs) -> dict[str, typing.Any]:
        initial: dict[str, typing.Any] = super().get_initial(**kwargs)
        if hasattr(self.request, "user"):
            try:
                initial["customer_profile"] = CustomerProfile.objects.get(
                    user=self.request.user
                )
            except CustomerProfile.DoesNotExist:
                initial["customer_profile"] = None
        return initial


class AuthorizenetListView(
    LoginRequiredMixin,
    HtmxTemplateResponseMixin,
    AuthorizenetMultipleObjectMixin,
    ListView,
):
    allow_empty = True
    content_type = "text/html"
    http_method_names = ["get"]
    ordering = "pk"
    paginate_by = 4


class AuthorizenetDeleteView(
    LoginRequiredMixin,
    HtmxTemplateResponseMixin,
    AuthorizenetSingleObjectMixin,
    DeleteView,
):
    content_type = "text/html"
    http_method_names = ["get", "post"]

    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        try:
            super().form_valid(form=form)
        except AuthorizenetControllerExecutionError as error:
            form.add_error(
                None,
                ValidationError(
                    "%(error)s", code="invalid", params={"error": str(error)}
                ),
            )
            return self.form_invalid(form=form)


class AuthorizenetDetailView(
    LoginRequiredMixin,
    HtmxTemplateResponseMixin,
    AuthorizenetSingleObjectMixin,
    DetailView,
):
    content_type = "text/html"
    http_method_names = ["get"]


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
