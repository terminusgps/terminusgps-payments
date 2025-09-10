import typing

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, DetailView, FormView, ListView
from terminusgps.authorizenet import api
from terminusgps.authorizenet.controllers import (
    AuthorizenetControllerExecutionError,
)
from terminusgps.authorizenet.services import AuthorizenetService
from terminusgps.mixins import HtmxTemplateResponseMixin

from terminusgps_payments import forms, models


class AddressProfileCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    extra_context = {"title": "Create Payment Method"}
    form_class = forms.AddressProfileCreationForm
    http_method_names = ["get", "post"]
    partial_template_name = (
        "terminusgps_payments/address_profiles/partials/_create.html"
    )
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    success_url = reverse_lazy("payments:account")
    template_name = "terminusgps_payments/address_profiles/create.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        self.anet_service = AuthorizenetService()
        return super().setup(request, *args, **kwargs)

    def form_valid(
        self, form: forms.AddressProfileCreationForm
    ) -> HttpResponse:
        customer_profile = models.CustomerProfile.objects.get(
            user=self.request.user
        )

        try:
            response = self.anet_service.request(
                api.create_customer_shipping_address,
                customer_profile_id=customer_profile.pk,
                address=form.cleaned_data["address"],
            )
            address_profile = models.AddressProfile(
                customer_profile=customer_profile
            )
            address_profile.pk = int(response.customerAddressId)
            address_profile.street = str(response.address.address)
            address_profile.save()
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


class AddressProfileDetailView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    http_method_names = ["get"]
    model = models.AddressProfile
    partial_template_name = (
        "terminusgps_payments/address_profiles/partials/_detail.html"
    )
    permission_denied_message = "Please login to view this content."
    pk_url_kwarg = "profile_pk"
    queryset = models.AddressProfile.objects.none()
    raise_exception = False
    template_name = "terminusgps_payments/address_profiles/detail.html"

    def get_queryset(
        self,
    ) -> QuerySet[models.AddressProfile, models.AddressProfile]:
        return models.AddressProfile.objects.filter(
            customer_profile__user=self.request.user
        )

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        if address_profile := kwargs.get("object"):
            context["profile"] = address_profile.get_authorizenet_profile()
        return context


class AddressProfileDeleteView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DeleteView
):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    model = models.AddressProfile
    partial_template_name = (
        "terminusgps_payments/address_profiles/partials/_delete.html"
    )
    permission_denied_message = "Please login to view this content."
    pk_url_kwarg = "profile_pk"
    queryset = models.AddressProfile.objects.none()
    raise_exception = False
    template_name = "terminusgps_payments/address_profiles/delete.html"

    def get_queryset(
        self,
    ) -> QuerySet[models.AddressProfile, models.AddressProfile]:
        return models.AddressProfile.objects.filter(
            customer_profile__user=self.request.user
        )


class AddressProfileListView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    allow_empty = True
    content_type = "text/html"
    http_method_names = ["get"]
    model = models.AddressProfile
    ordering = "pk"
    paginate_by = 4
    partial_template_name = (
        "terminusgps_payments/address_profiles/partials/_list.html"
    )
    permission_denied_message = "Please login to view this content."
    queryset = models.AddressProfile.objects.none()
    raise_exception = False
    template_name = "terminusgps_payments/address_profiles/list.html"

    def get_queryset(
        self,
    ) -> QuerySet[models.AddressProfile, models.AddressProfile]:
        return models.AddressProfile.objects.filter(
            customer_profile__user=self.request.user
        ).order_by(self.get_ordering())
