import typing

from django.db.models import QuerySet
from django.views.generic import CreateView, DeleteView, DetailView, ListView
from terminusgps.mixins import HtmxTemplateResponseMixin

from ..models import CustomerAddressProfile, CustomerProfile


class CustomerAddressProfileCreateView(HtmxTemplateResponseMixin, CreateView):
    content_type = "text/html"
    fields = ["default"]
    http_method_names = ["get", "post"]
    model = CustomerAddressProfile
    partial_template_name = (
        "terminusgps_payments/address_profiles/partials/_create.html"
    )
    template_name = "terminusgps_payments/address_profiles/create.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customerprofile"] = CustomerProfile.objects.get(
            pk=self.kwargs["customerprofile_pk"]
        )
        return context


class CustomerAddressProfileListView(HtmxTemplateResponseMixin, ListView):
    content_type = "text/html"
    http_method_names = ["get"]
    model = CustomerAddressProfile
    ordering = "pk"
    partial_template_name = (
        "terminusgps_payments/address_profiles/partials/_list.html"
    )
    template_name = "terminusgps_payments/address_profiles/list.html"

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(
            cprofile__pk=self.kwargs["customerprofile_pk"]
        ).order_by(self.get_ordering())

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customerprofile"] = CustomerProfile.objects.get(
            pk=self.kwargs["customerprofile_pk"]
        )
        return context


class CustomerAddressProfileDetailView(HtmxTemplateResponseMixin, DetailView):
    content_type = "text/html"
    http_method_names = ["get"]
    model = CustomerAddressProfile
    partial_template_name = (
        "terminusgps_payments/address_profiles/partials/_detail.html"
    )
    pk_url_kwarg = "addressprofile_pk"
    template_name = "terminusgps_payments/address_profiles/detail.html"

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(
            cprofile__pk=self.kwargs["customerprofile_pk"]
        )


class CustomerAddressProfileDeleteView(HtmxTemplateResponseMixin, DeleteView):
    content_type = "text/html"
    http_method_names = ["post"]
    model = CustomerAddressProfile
    partial_template_name = (
        "terminusgps_payments/address_profiles/partials/_deleted.html"
    )
    pk_url_kwarg = "addressprofile_pk"
    template_name = "terminusgps_payments/address_profiles/deleted.html"

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(
            cprofile__pk=self.kwargs["customerprofile_pk"]
        )
