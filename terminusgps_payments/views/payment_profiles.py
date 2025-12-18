import typing

from django.db.models import QuerySet
from django.views.generic import CreateView, DetailView, ListView
from terminusgps.mixins import HtmxTemplateResponseMixin

from .. import forms
from ..models import CustomerPaymentProfile, CustomerProfile


class CustomerPaymentProfileCreditCardCreateView(
    HtmxTemplateResponseMixin, CreateView
):
    content_type = "text/html"
    form_class = forms.CustomerPaymentProfileCreditCardCreateForm
    http_method_names = ["get", "post"]
    model = CustomerPaymentProfile
    partial_template_name = "terminusgps_payments/payment_profiles/partials/_create_credit_card.html"
    template_name = (
        "terminusgps_payments/payment_profiles/create_credit_card.html"
    )

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customerprofile"] = CustomerProfile.objects.get(
            pk=self.kwargs["customerprofile_pk"]
        )
        return context


class CustomerPaymentProfileBankAccountCreateView(
    HtmxTemplateResponseMixin, CreateView
):
    content_type = "text/html"
    fields = ["default"]
    http_method_names = ["get", "post"]
    model = CustomerPaymentProfile
    partial_template_name = "terminusgps_payments/payment_profiles/partials/_create_bank_account.html"
    template_name = (
        "terminusgps_payments/payment_profiles/create_bank_account.html"
    )

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customerprofile"] = CustomerProfile.objects.get(
            pk=self.kwargs["customerprofile_pk"]
        )
        return context


class CustomerPaymentProfileDetailView(HtmxTemplateResponseMixin, DetailView):
    content_type = "text/html"
    http_method_names = ["get"]
    model = CustomerPaymentProfile
    partial_template_name = (
        "terminusgps_payments/payment_profiles/partials/_detail.html"
    )
    pk_url_kwarg = "paymentprofile_pk"
    template_name = "terminusgps_payments/payment_profiles/detail.html"

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(
            cprofile__pk=self.kwargs["customerprofile_pk"]
        )


class CustomerPaymentProfileListView(HtmxTemplateResponseMixin, ListView):
    content_type = "text/html"
    http_method_names = ["get"]
    model = CustomerPaymentProfile
    ordering = "pk"
    partial_template_name = (
        "terminusgps_payments/payment_profiles/partials/_list.html"
    )
    template_name = "terminusgps_payments/payment_profiles/list.html"

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
