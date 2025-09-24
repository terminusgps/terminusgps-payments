from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, DetailView, FormView, ListView
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
)
from terminusgps.mixins import HtmxTemplateResponseMixin

from terminusgps_payments.forms import AddressProfileCreationForm
from terminusgps_payments.models import AddressProfile, CustomerProfile
from terminusgps_payments.services import AuthorizenetService


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

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.anet_service = AuthorizenetService()

    @transaction.atomic
    def form_valid(self, form: AddressProfileCreationForm) -> HttpResponse:
        customer_profile = CustomerProfile.objects.get(user=self.request.user)
        address_profile = AddressProfile(customer_profile=customer_profile)

        try:
            anet_response = self.anet_service.create_address_profile(
                address_profile,
                address=form.cleaned_data["address"],
                default=form.cleaned_data["default"],
            )
            address_profile.pk = int(anet_response.customerAddressId)
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

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.anet_service = AuthorizenetService()

    def get_queryset(self) -> QuerySet:
        return AddressProfile.objects.for_user(
            self.request.user
        ).select_related("customer_profile")

    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        try:
            address_profile = self.get_object()
            self.anet_service.delete_address_profile(address_profile)
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
