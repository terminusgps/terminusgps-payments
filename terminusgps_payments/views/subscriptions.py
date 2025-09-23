import typing

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.views.generic import DeleteView, DetailView, ListView, UpdateView
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
            service = SubscriptionService()
            subscription, api_response = service.get(
                subscription, include_transactions=True
            )
            if api_response is not None:
                context["profile"] = api_response
        return context


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

    def get_form(self, form_class=None) -> forms.ModelForm:
        form = super().get_form(form_class=form_class)
        payment_qs = PaymentProfile.objects.for_user(self.request.user)
        address_qs = AddressProfile.objects.for_user(self.request.user)
        form.fields["payment_profile"].queryset = payment_qs
        form.fields["payment_profile"].empty_label = None
        form.fields["payment_profile"].widget.attrs.update(
            {"class": "p-2 rounded border w-full"}
        )
        form.fields["address_profile"].queryset = address_qs
        form.fields["address_profile"].empty_label = None
        form.fields["address_profile"].widget.attrs.update(
            {"class": "p-2 rounded border w-full"}
        )
        return form

    def get_queryset(self) -> QuerySet:
        return Subscription.objects.for_user(self.request.user)


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
