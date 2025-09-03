import typing

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, FormView, ListView
from terminusgps.django.mixins import HtmxTemplateResponseMixin

from terminusgps_payments import forms
from terminusgps_payments.models import AddressProfile


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
    queryset = AddressProfile.objects.none()
    raise_exception = False
    template_name = "terminusgps_payments/address_profiles/detail.html"

    def get_queryset(self) -> QuerySet[AddressProfile, AddressProfile]:
        return AddressProfile.objects.filter(
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
    model = AddressProfile
    partial_template_name = (
        "terminusgps_payments/address_profiles/partials/_delete.html"
    )
    permission_denied_message = "Please login to view this content."
    pk_url_kwarg = "profile_pk"
    queryset = AddressProfile.objects.none()
    raise_exception = False
    template_name = "terminusgps_payments/address_profiles/delete.html"

    def get_queryset(self) -> QuerySet[AddressProfile, AddressProfile]:
        return AddressProfile.objects.filter(
            customer_profile__user=self.request.user
        )


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
    queryset = AddressProfile.objects.none()
    raise_exception = False
    template_name = "terminusgps_payments/address_profiles/list.html"

    def get_queryset(self) -> QuerySet[AddressProfile, AddressProfile]:
        return AddressProfile.objects.filter(
            customer_profile__user=self.request.user
        ).order_by(self.get_ordering())
