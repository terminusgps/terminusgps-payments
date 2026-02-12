import typing

from django import forms
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
    AuthorizenetService,
)

from terminusgps_payments.models import (
    CustomerAddressProfile,
    CustomerPaymentProfile,
    CustomerProfile,
    Subscription,
)
from terminusgps_payments.views.generic import (
    AuthorizenetCreateView,
    AuthorizenetDeleteView,
    AuthorizenetDetailView,
    AuthorizenetUpdateView,
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
    model = Subscription
    template_name = "terminusgps_payments/subscription_create.html"

    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        try:
            self.object = form.save(commit=False)
            self.object.save(push=True)
            return HttpResponseRedirect(self.object.get_absolute_url())
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

    def get_initial(self, **kwargs) -> dict[str, typing.Any]:
        try:
            customer_profile = CustomerProfile.objects.get(
                user=self.request.user
            )
        except CustomerProfile.DoesNotExist:
            customer_profile = None

        initial: dict[str, typing.Any] = super().get_initial(**kwargs)
        initial["customer_profile"] = customer_profile
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
        form.fields["payment_profile"].queryset = payment_qs
        form.fields["address_profile"].queryset = address_qs
        form.fields["payment_profile"].empty_label = None
        form.fields["address_profile"].empty_label = None
        return form


class SubscriptionDetailView(AuthorizenetDetailView):
    content_type = "text/html"
    http_method_names = ["get"]
    model = Subscription
    template_name = "terminusgps_payments/subscription_detail.html"


class SubscriptionDeleteView(AuthorizenetDeleteView):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    model = Subscription
    success_url = reverse_lazy("terminusgps_payments:create subscriptions")
    template_name = "terminusgps_payments/subscription_delete.html"

    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        try:
            service = AuthorizenetService()
            self.object._delete_in_authorizenet(service=service)
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
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


class SubscriptionUpdateView(AuthorizenetUpdateView):
    content_type = "text/html"
    fields = ["address_profile", "payment_profile"]
    http_method_names = ["get", "post"]
    model = Subscription
    template_name = "terminusgps_payments/subscription_update.html"

    def get_success_url(self):
        return self.object.get_absolute_url()

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
        form.fields["payment_profile"].queryset = payment_qs
        form.fields["address_profile"].queryset = address_qs
        form.fields["payment_profile"].empty_label = None
        form.fields["address_profile"].empty_label = None
        return form
