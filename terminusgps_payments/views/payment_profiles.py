from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, DetailView, FormView, ListView
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
)
from terminusgps.mixins import HtmxTemplateResponseMixin

from terminusgps_payments.forms import PaymentProfileCreationForm
from terminusgps_payments.models import CustomerProfile, PaymentProfile
from terminusgps_payments.services import AuthorizenetService


class PaymentProfileCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    form_class = PaymentProfileCreationForm
    http_method_names = ["get", "post"]
    partial_template_name = (
        "terminusgps_payments/payment_profiles/partials/_create.html"
    )
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    success_url = reverse_lazy("terminusgps_payments:list payment profile")
    template_name = "terminusgps_payments/payment_profiles/create.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.anet_service = AuthorizenetService()

    @transaction.atomic
    def form_valid(self, form: PaymentProfileCreationForm) -> HttpResponse:
        customer_profile = CustomerProfile.objects.get(user=self.request.user)
        payment_profile = PaymentProfile(customer_profile=customer_profile)

        try:
            anet_response = self.anet_service.create_payment_profile(
                payment_profile,
                address=form.cleaned_data["address"],
                credit_card=form.cleaned_data["credit_card"],
                default=form.cleaned_data["default"],
            )
            payment_profile.pk = int(anet_response.customerPaymentProfileId)
            payment_profile.save()
            return HttpResponse(
                status=200,
                headers={
                    "HX-Reselect": "#payment-profiles-list",
                    "HX-Refresh": "true",
                },
            )
        except AuthorizenetControllerExecutionError as e:
            match e.code:
                case "E00039":
                    form.add_error(
                        None,
                        ValidationError(
                            _(
                                "Whoops! A payment method with a card ending in '%(last_4)s' already exists on your account."
                            ),
                            code="invalid",
                            params={
                                "last_4": str(
                                    form.cleaned_data["credit_card"].cardNumber
                                )[-4:]
                            },
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


class PaymentProfileDetailView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    http_method_names = ["get"]
    model = PaymentProfile
    partial_template_name = (
        "terminusgps_payments/payment_profiles/partials/_detail.html"
    )
    permission_denied_message = "Please login to view this content."
    pk_url_kwarg = "profile_pk"
    raise_exception = False
    template_name = "terminusgps_payments/payment_profiles/detail.html"

    def get_queryset(self) -> QuerySet:
        return PaymentProfile.objects.for_user(
            self.request.user
        ).select_related("customer_profile")


class PaymentProfileDeleteView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DeleteView
):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    model = PaymentProfile
    partial_template_name = (
        "terminusgps_payments/payment_profiles/partials/_delete.html"
    )
    permission_denied_message = "Please login to view this content."
    pk_url_kwarg = "profile_pk"
    raise_exception = False
    template_name = "terminusgps_payments/payment_profiles/delete.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.anet_service = AuthorizenetService()

    def get_queryset(self) -> QuerySet:
        return PaymentProfile.objects.for_user(
            self.request.user
        ).select_related("customer_profile")

    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        try:
            payment_profile = self.get_object()
            self.anet_service.delete_payment_profile(payment_profile)
            payment_profile.delete()
            return HttpResponse(
                status=200,
                headers={
                    "HX-Reselect": "#payment-profiles-list",
                    "HX-Refresh": "true",
                },
            )
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


class PaymentProfileListView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    allow_empty = True
    content_type = "text/html"
    http_method_names = ["get"]
    model = PaymentProfile
    ordering = "pk"
    paginate_by = 4
    partial_template_name = (
        "terminusgps_payments/payment_profiles/partials/_list.html"
    )
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_payments/payment_profiles/list.html"

    def get_queryset(self) -> QuerySet:
        return (
            PaymentProfile.objects.for_user(self.request.user)
            .select_related("customer_profile")
            .order_by(self.get_ordering())
        )
