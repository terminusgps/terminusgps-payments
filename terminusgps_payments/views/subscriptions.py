import typing

from authorizenet import apicontractsv1
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, DetailView, ListView, UpdateView
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
)
from terminusgps.mixins import HtmxTemplateResponseMixin

from terminusgps_payments.models import (
    AddressProfile,
    PaymentProfile,
    Subscription,
)
from terminusgps_payments.services import SubscriptionService


class SubscriptionDetailView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    http_method_names = ["get"]
    model = Subscription
    partial_template_name = (
        "terminusgps_payments/subscriptions/partials/_detail.html"
    )
    permission_denied_message = "Please login to view this content."
    pk_url_kwarg = "subscription_pk"
    template_name = "terminusgps_payments/subscriptions/detail.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        if subscription := kwargs.get("object"):
            include_transactions = self.request.GET.get("transactions")
            service = SubscriptionService()
            context["profile"] = service.get(
                subscription,
                include_transactions=True
                if str(include_transactions) == "on"
                else False,
            )
        return context

    def get_queryset(self) -> QuerySet:
        return Subscription.objects.for_user(self.request.user).select_related(
            "address_profile", "payment_profile"
        )


class SubscriptionUpdateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, UpdateView
):
    content_type = "text/html"
    fields = ["payment_profile", "address_profile"]
    http_method_names = ["get", "post"]
    model = Subscription
    partial_template_name = (
        "terminusgps_payments/subscriptions/partials/_update.html"
    )
    permission_denied_message = "Please login to view this content."
    pk_url_kwarg = "subscription_pk"
    template_name = "terminusgps_payments/subscriptions/update.html"

    def get_queryset(self) -> QuerySet:
        return Subscription.objects.for_user(self.request.user).select_related(
            "address_profile", "payment_profile"
        )

    def get_form(self, form_class: forms.Form | None = None) -> forms.Form:
        form = super().get_form(form_class=form_class)
        payment_qs = PaymentProfile.objects.for_user(self.request.user)
        address_qs = AddressProfile.objects.for_user(self.request.user)
        form.fields["payment_profile"].queryset = payment_qs
        form.fields["address_profile"].queryset = address_qs
        form.fields["payment_profile"].empty_label = None
        form.fields["address_profile"].empty_label = None
        return form

    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        try:
            subscription = self.get_object()
            address_updated = "address_profile" in form.changed_data
            payment_updated = "payment_profile" in form.changed_data

            if address_updated or payment_updated:
                profile = apicontractsv1.customerProfileIdType()
                profile.customerProfileId = str(
                    subscription.customer_profile.pk
                )
                if address_updated:
                    pk = form.cleaned_data["address_profile"].pk
                    profile.customerAddressId = str(pk)
                if payment_updated:
                    pk = form.cleaned_data["payment_profile"].pk
                    profile.customerPaymentProfileId = str(pk)

                anet_subscription = apicontractsv1.ARBSubscriptionType()
                anet_subscription.profile = profile
                service = SubscriptionService()
                # Call Authorizenet API
                service.update(subscription, anet_subscription)
            return super().form_valid(form=form)
        except AuthorizenetControllerExecutionError as e:
            match e.code:
                case _:
                    form.add_error(
                        None,
                        ValidationError(
                            _("%(code)s: '%(message)s'"),
                            code="invalid",
                            params={"code": e.code, "message": e.message},
                        ),
                    )
            return self.form_invalid(form=form)


class SubscriptionDeleteView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DeleteView
):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    model = Subscription
    partial_template_name = (
        "terminusgps_payments/subscriptions/partials/_delete.html"
    )
    permission_denied_message = "Please login to view this content."
    pk_url_kwarg = "subscription_pk"
    template_name = "terminusgps_payments/subscriptions/delete.html"

    def get_queryset(self) -> QuerySet:
        return Subscription.objects.for_user(self.request.user)


class SubscriptionListView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    allow_empty = True
    content_type = "text/html"
    http_method_names = ["get"]
    model = Subscription
    paginate_by = 4
    partial_template_name = (
        "terminusgps_payments/subscriptions/partials/_list.html"
    )
    template_name = "terminusgps_payments/subscriptions/list.html"
    ordering = "name"

    def get_queryset(self) -> QuerySet:
        return Subscription.objects.for_user(self.request.user).order_by(
            self.get_ordering()
        )
