import typing

from authorizenet import apicontractsv1
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet
from django.forms import Form
from django.http import HttpResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, FormView, ListView
from lxml.objectify import ObjectifiedElement
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
)
from terminusgps.mixins import HtmxTemplateResponseMixin

from ..forms import (
    CustomerPaymentProfileBankAccountCreateForm,
    CustomerPaymentProfileCreditCardCreateForm,
)
from ..models import CustomerPaymentProfile, CustomerProfile


class CustomerPaymentProfileCreateView(HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    partial_template_name = (
        "terminusgps_payments/payment_profiles/partials/_create.html"
    )
    template_name = "terminusgps_payments/payment_profiles/create.html"

    def get_success_url(self) -> str:
        return reverse(
            "terminusgps_payments:list payment profiles",
            kwargs={"customerprofile_pk": self.kwargs["customerprofile_pk"]},
        )

    @transaction.atomic
    def form_valid(self, form: Form) -> HttpResponse:
        try:
            cprofile = CustomerProfile.objects.get(
                pk=self.kwargs["customerprofile_pk"]
            )

            contract = self.generate_payment_profile_contract(form)
            pprofile = CustomerPaymentProfile(cprofile=cprofile)
            pprofile.payment = contract.payment
            pprofile.address = contract.billTo
            pprofile.save()
            return super().form_valid(form=form)
        except CustomerProfile.DoesNotExist:
            form.add_error(
                None,
                ValidationError(
                    _(
                        "Whoops! Something went wrong on our end, please try again later."
                    ),
                    code="invalid",
                ),
            )
            return self.form_invalid(form=form)
        except AuthorizenetControllerExecutionError as error:
            match error.code:
                case _:
                    form.add_error(
                        None,
                        ValidationError(
                            _("Whoops! %(error)s"),
                            code="invalid",
                            params={"error": error},
                        ),
                    )
            return self.form_invalid(form=form)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customerprofile"] = CustomerProfile.objects.get(
            pk=self.kwargs["customerprofile_pk"]
        )
        return context

    def get_form_class(self) -> type[Form]:
        if "form" in self.request.GET:
            input = self.request.GET.get("form")
        elif "form" in self.request.POST:
            input = self.request.POST.get("form")
        else:
            input = "credit-card"

        match input:
            case "credit-card":
                return CustomerPaymentProfileCreditCardCreateForm
            case "bank-account":
                return CustomerPaymentProfileBankAccountCreateForm
            case _:
                return Form

    def generate_payment_profile_contract(
        self, form: Form
    ) -> ObjectifiedElement:
        payment = apicontractsv1.paymentType()
        if "credit_card" in form.cleaned_data:
            payment.creditCard = form.cleaned_data["credit_card"]
        elif "bank_account" in form.cleaned_data:
            payment.bankAccount = form.cleaned_data["bank_account"]

        contract = apicontractsv1.customerPaymentProfileType()
        contract.payment = payment
        contract.billTo = form.cleaned_data["address"]
        return contract


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
