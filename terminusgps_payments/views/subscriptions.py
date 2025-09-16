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

from terminusgps_payments.models import Subscription
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
    queryset = Subscription.objects.none()
    template_name = "terminusgps_payments/subscriptions/detail.html"

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(
            customer_profile__user=self.request.user
        )


class SubscriptionUpdateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, UpdateView
):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    model = Subscription
    fields = ["payment_profile", "address_profile"]
    partial_template_name = (
        "terminusgps_payments/subscriptions/partials/_update.html"
    )
    permission_denied_message = "Please login to view this content."
    pk_url_kwarg = "subscription_pk"
    queryset = Subscription.objects.none()
    template_name = "terminusgps_payments/subscriptions/update.html"

    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        try:
            subscription = self.get_object()
            address_updated = "address_profile" in form.changed_data
            payment_updated = "payment_profile" in form.changed_data

            anet_subscription = apicontractsv1.ARBSubscriptionType()
            anet_subscription.profile = apicontractsv1.customerProfileIdType()
            anet_subscription.profile.customerProfileId = str(
                subscription.customer_profile.pk
            )

            if address_updated:
                pk = form.cleaned_data["address_profile"].pk
                anet_subscription.profile.customerAddressId = str(pk)
            if payment_updated:
                pk = form.cleaned_data["payment_profile"].pk
                anet_subscription.profile.customerPaymentProfileId = str(pk)
            if address_updated or payment_updated:
                service = SubscriptionService()
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

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(
            customer_profile__user=self.request.user
        )


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
    queryset = Subscription.objects.none()
    template_name = "terminusgps_payments/subscriptions/delete.html"

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(
            customer_profile__user=self.request.user
        )


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
    queryset = Subscription.objects.none()
    template_name = "terminusgps_payments/subscriptions/list.html"

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(
            customer_profile__user=self.request.user
        )
