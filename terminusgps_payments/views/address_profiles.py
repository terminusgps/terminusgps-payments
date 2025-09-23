import typing

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, DetailView, FormView, ListView
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
)
from terminusgps.mixins import HtmxTemplateResponseMixin

from terminusgps_payments.forms import AddressProfileCreationForm
from terminusgps_payments.models import AddressProfile, CustomerProfile
from terminusgps_payments.services import AddressProfileService


class AddressProfileCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    extra_context = {"title": "Create Address Profile"}
    form_class = AddressProfileCreationForm
    http_method_names = ["get", "post"]
    partial_template_name = (
        "terminusgps_payments/address_profiles/partials/_create.html"
    )
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_payments/address_profiles/create.html"

    @transaction.atomic
    def form_valid(self, form: AddressProfileCreationForm) -> HttpResponse:
        customer_profile = CustomerProfile.objects.get(user=self.request.user)
        address_profile = AddressProfile(customer_profile=customer_profile)

        try:
            service = AddressProfileService()
            address_profile, api_response = service.create(
                address_profile,
                address=form.cleaned_data["address"],
                default=form.cleaned_data["default"],
            )
            if api_response is None:
                raise AuthorizenetControllerExecutionError(
                    code="1",
                    message="Whoops! Something went wrong with the Authorizenet API. Please try again later.",
                )
            address_profile.pk = int(api_response.customerAddressId)
            address_profile.save()
            return HttpResponse(
                status=200,
                headers={
                    "HX-Reselect": "#address-profiles-list",
                    "HX-Refresh": "true",
                },
            )
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


class AddressProfileDetailView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    http_method_names = ["get"]
    model = AddressProfile
    partial_template_name = (
        "terminusgps_payments/address_profiles/partials/_detail.html"
    )
    permission_denied_message = "Please login to view this content."
    pk_url_kwarg = "profile_pk"
    raise_exception = False
    template_name = "terminusgps_payments/address_profiles/detail.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        if address_profile := kwargs.get("object"):
            if address_profile.address is None:
                # Retrieve address data from Authorizenet
                service = AddressProfileService()
                address_profile, api_response = service.get(address_profile)
                if api_response is not None:
                    address_profile.address = getattr(api_response, "address")
                    address_profile.save()
        return context

    def get_queryset(self) -> QuerySet:
        return AddressProfile.objects.for_user(
            self.request.user
        ).select_related("customer_profile")


class AddressProfileDeleteView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DeleteView
):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    model = AddressProfile
    partial_template_name = (
        "terminusgps_payments/address_profiles/partials/_delete.html"
    )
    permission_denied_message = "Please login to view this content."
    pk_url_kwarg = "profile_pk"
    queryset = AddressProfile.objects.none()
    raise_exception = False
    template_name = "terminusgps_payments/address_profiles/delete.html"

    def get_queryset(self) -> QuerySet:
        return AddressProfile.objects.for_user(
            self.request.user
        ).select_related("customer_profile")

    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        try:
            service = AddressProfileService()
            address_profile = self.get_object()
            address_profile, api_response = service.delete(address_profile)
            if api_response is None:
                raise AuthorizenetControllerExecutionError(
                    code="1",
                    message="Whoops! Something went wrong calling the Authorizenet API. Please try again later.",
                )
            address_profile.delete()
            return HttpResponse(
                status=200,
                headers={
                    "HX-Reselect": "#address-profiles-list",
                    "HX-Refresh": "true",
                },
            )
        except AuthorizenetControllerExecutionError as e:
            match e.code:
                case "E00107":
                    form.add_error(
                        None,
                        ValidationError(
                            _(
                                "Whoops! This shipping address is currently associated with an active or suspended subscription. Nothing was deleted."
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


class AddressProfileListView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    allow_empty = True
    content_type = "text/html"
    http_method_names = ["get"]
    model = AddressProfile
    ordering = "pk"
    paginate_by = 4
    partial_template_name = (
        "terminusgps_payments/address_profiles/partials/_list.html"
    )
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_payments/address_profiles/list.html"

    def get_queryset(self) -> QuerySet:
        return (
            AddressProfile.objects.for_user(self.request.user)
            .select_related("customer_profile")
            .order_by(self.get_ordering())
        )
