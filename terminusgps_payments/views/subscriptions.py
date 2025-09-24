from authorizenet import apicontractsv1
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
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
from terminusgps_payments.services import AuthorizenetService


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

    def get_queryset(self) -> QuerySet:
        return Subscription.objects.for_user(self.request.user)


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

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.anet_service = AuthorizenetService()

    def get_queryset(self) -> QuerySet:
        return Subscription.objects.for_user(self.request.user)

    def get_form(self, form_class=None) -> forms.ModelForm:
        form = super().get_form(form_class=form_class)
        payment_qs = PaymentProfile.objects.for_user(self.request.user)
        address_qs = AddressProfile.objects.for_user(self.request.user)
        form.fields["payment_profile"].queryset = payment_qs
        form.fields["payment_profile"].empty_label = None
        form.fields["address_profile"].queryset = address_qs
        form.fields["address_profile"].empty_label = None
        return form

    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        try:
            if any(
                [
                    "payment_profile" in form.changed_data,
                    "address_profile" in form.changed_data,
                ]
            ):
                subscription = self.get_object()
                cprofile_pk = subscription.customer_profile.pk
                pprofile_pk = form.cleaned_data["payment_profile"].pk
                aprofile_pk = form.cleaned_data["address_profile"].pk
                anet_profile = apicontractsv1.customerProfileIdType()
                anet_profile.customerProfileId = str(cprofile_pk)
                anet_profile.customerPaymentProfileId = str(pprofile_pk)
                anet_profile.customerAddressId = str(aprofile_pk)
                self.anet_service.update_subscription(
                    subscription,
                    apicontractsv1.ARBSubscriptionType(profile=anet_profile),
                )
            return super().form_valid(form=form)
        except AuthorizenetControllerExecutionError as e:
            match e.code:
                case _:
                    form.add_error(
                        None,
                        ValidationError(
                            _("%(code)s: %(message)s"),
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

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.anet_service = AuthorizenetService()

    def get_queryset(self) -> QuerySet:
        return Subscription.objects.for_user(self.request.user)

    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        try:
            subscription = self.get_object()
            self.anet_service.delete_subscription(subscription)
            subscription.delete()
            return HttpResponse(status=200)
        except AuthorizenetControllerExecutionError as e:
            match e.code:
                case "E00105":
                    form.add_error(
                        None,
                        ValidationError(
                            _(
                                "Whoops! This payment method is currently associated with an active or suspended subscription. Nothing was deleted."
                            ),
                            code="invalid",
                        ),
                    )
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
