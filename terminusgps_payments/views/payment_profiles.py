import os
import typing

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.staticfiles import finders
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, DetailView, FormView, ListView
from lxml.objectify import ObjectifiedElement
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
)
from terminusgps.mixins import HtmxTemplateResponseMixin

from terminusgps_payments.forms import PaymentProfileCreationForm
from terminusgps_payments.models import (
    AddressProfile,
    CustomerProfile,
    PaymentProfile,
)
from terminusgps_payments.services import (
    AddressProfileService,
    PaymentProfileService,
)


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

    @transaction.atomic
    def form_valid(self, form: PaymentProfileCreationForm) -> HttpResponse:
        customer_profile = CustomerProfile.objects.get(user=self.request.user)
        payment_profile = PaymentProfile(customer_profile=customer_profile)
        address_profile = AddressProfile(customer_profile=customer_profile)

        address = form.cleaned_data["address"]
        credit_card = form.cleaned_data["credit_card"]
        default = form.cleaned_data["default"]
        create_address = form.cleaned_data["create_address_profile"]

        try:
            service = PaymentProfileService()
            payment_profile = service.create(
                payment_profile,
                address=address,
                credit_card=credit_card,
                default=default,
            )
            payment_profile.save()
            if create_address:
                service = AddressProfileService()
                address_profile = service.create(
                    address_profile, address=address, default=default
                )
                address_profile.save()
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
    queryset = PaymentProfile.objects.none()
    raise_exception = False
    template_name = "terminusgps_payments/payment_profiles/detail.html"

    def get_credit_card_svg_icon(
        self, payment_profile_response: ObjectifiedElement
    ) -> str | None:
        card_type = str(
            payment_profile_response.paymentProfile.payment.creditCard.cardType
        ).lower()

        cache_key = f"get_credit_card_svg_icon:{card_type}"
        if cached_icon := cache.get(cache_key):
            return cached_icon

        path = finders.find(
            f"terminusgps_payments/icons/{card_type}.svg", find_all=False
        )
        if os.path.exists(path):
            with open(path, "r") as f:
                icon = f.read()

        cache.set(cache_key, icon, timeout=60 * 15)
        return icon

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(
            customer_profile__user=self.request.user
        ).select_related("customer_profile")

    def get_context_data(self, **kwargs) -> dict:
        context: dict = super().get_context_data(**kwargs)
        if payment_profile := kwargs.get("object"):
            service = PaymentProfileService()
            profile = service.get(payment_profile)

            context["profile"] = profile
            context["icon_svg"] = self.get_credit_card_svg_icon(profile)
        return context


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
    queryset = PaymentProfile.objects.none()
    raise_exception = False
    template_name = "terminusgps_payments/payment_profiles/delete.html"

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(
            customer_profile__user=self.request.user
        ).select_related("customer_profile")

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        if payment_profile := kwargs.get("object"):
            service = PaymentProfileService()
            context["profile"] = service.get(payment_profile)
        return context

    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        try:
            service = PaymentProfileService()
            payment_profile = self.get_object()

            service.delete(payment_profile)
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
    queryset = PaymentProfile.objects.none()
    raise_exception = False
    template_name = "terminusgps_payments/payment_profiles/list.html"

    def get_queryset(self) -> QuerySet:
        return (
            self.model.objects.filter(customer_profile__user=self.request.user)
            .select_related("customer_profile")
            .order_by(self.get_ordering())
        )
