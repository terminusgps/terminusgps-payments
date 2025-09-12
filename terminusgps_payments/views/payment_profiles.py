from authorizenet import apicontractsv1
from django import forms
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, DetailView, FormView, ListView
from terminusgps.authorizenet import api as anet_api
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
    AuthorizenetService,
)
from terminusgps.mixins import HtmxTemplateResponseMixin

from terminusgps_payments import models
from terminusgps_payments.forms import PaymentProfileCreationForm


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
    template_name = "terminusgps_payments/payment_profiles/create.html"
    success_url = reverse_lazy("terminusgps_payments:list payment profile")

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        self.anet_service = AuthorizenetService()
        return super().setup(request, *args, **kwargs)

    @transaction.atomic
    def form_valid(self, form: PaymentProfileCreationForm) -> HttpResponse:
        cprofile = models.CustomerProfile.objects.get(user=self.request.user)
        pprofile = models.PaymentProfile(customer_profile=cprofile)
        aprofile = models.AddressProfile(customer_profile=cprofile)

        try:
            anet_response = self.anet_service.call_api(
                anet_api.create_customer_payment_profile(
                    customer_profile_id=cprofile.pk,
                    payment=apicontractsv1.paymentType(
                        creditCard=form.cleaned_data["credit_card"]
                    ),
                    address=form.cleaned_data["address"],
                    default=form.cleaned_data["default"],
                    validation=settings.MERCHANT_AUTH_VALIDATION_MODE,
                )
            )
            pprofile.pk = int(anet_response.customerPaymentProfileId)
            pprofile.save()
            if form.cleaned_data["create_address_profile"]:
                anet_response = self.anet_service.call_api(
                    anet_api.create_customer_shipping_address(
                        customer_profile_id=cprofile.pk,
                        address=form.cleaned_data["address"],
                        default=form.cleaned_data["default"],
                    )
                )
                aprofile.pk = int(anet_response.customerAddressId)
                aprofile.save()
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


class PaymentProfileDetailView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    http_method_names = ["get"]
    model = models.PaymentProfile
    partial_template_name = (
        "terminusgps_payments/payment_profiles/partials/_detail.html"
    )
    permission_denied_message = "Please login to view this content."
    pk_url_kwarg = "profile_pk"
    queryset = models.PaymentProfile.objects.none()
    raise_exception = False
    template_name = "terminusgps_payments/payment_profiles/detail.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        self.anet_service = AuthorizenetService()
        return super().setup(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(
            customer_profile__user=self.request.user
        ).select_related("customer_profile")

    def get_context_data(self, **kwargs) -> dict:
        context: dict = super().get_context_data(**kwargs)
        if pprofile := kwargs.get("object"):
            anet_response = self.anet_service.call_api(
                anet_api.get_customer_payment_profile(
                    customer_profile_id=pprofile.customer_profile.pk,
                    payment_profile_id=pprofile.pk,
                    # TODO: Determine include_issuer_info via request parameters
                    include_issuer_info=False,
                )
            )
            context["anet_profile"] = anet_response.paymentProfile
        return context


class PaymentProfileDeleteView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DeleteView
):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    model = models.PaymentProfile
    partial_template_name = (
        "terminusgps_payments/payment_profiles/partials/_delete.html"
    )
    permission_denied_message = "Please login to view this content."
    pk_url_kwarg = "profile_pk"
    queryset = models.PaymentProfile.objects.none()
    raise_exception = False
    template_name = "terminusgps_payments/payment_profiles/delete.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        self.anet_service = AuthorizenetService()
        return super().setup(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(
            customer_profile__user=self.request.user
        ).select_related("customer_profile")

    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        pprofile = self.get_object()

        try:
            self.anet_service.call_api(
                anet_api.delete_customer_payment_profile(
                    customer_profile_id=pprofile.customer_profile.pk,
                    payment_profile_id=pprofile.pk,
                )
            )
            self.object.delete()
            response = HttpResponse(status=200)
            response.headers["HX-Reswap"] = "delete"
            return response
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
    model = models.PaymentProfile
    ordering = "pk"
    paginate_by = 4
    partial_template_name = (
        "terminusgps_payments/payment_profiles/partials/_list.html"
    )
    permission_denied_message = "Please login to view this content."
    queryset = models.PaymentProfile.objects.none()
    raise_exception = False
    template_name = "terminusgps_payments/payment_profiles/list.html"

    def get_queryset(self) -> QuerySet:
        return (
            self.model.objects.filter(customer_profile__user=self.request.user)
            .select_related("customer_profile")
            .order_by(self.get_ordering())
        )
