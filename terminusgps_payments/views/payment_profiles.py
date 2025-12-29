import logging
import typing

from authorizenet import apicontractsv1
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet
from django.forms import Form
from django.http import HttpResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, DetailView, FormView, ListView
from terminusgps.authorizenet import api
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
    AuthorizenetService,
)
from terminusgps.mixins import HtmxTemplateResponseMixin

from ..forms import (
    CustomerPaymentProfileBankAccountCreateForm,
    CustomerPaymentProfileCreditCardCreateForm,
)
from ..models import CustomerPaymentProfile, CustomerProfile

logger = logging.getLogger(__name__)


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

            payment = apicontractsv1.paymentType()
            if "credit_card" in form.cleaned_data:
                payment.creditCard = form.cleaned_data["credit_card"]
            elif "bank_account" in form.cleaned_data:
                payment.bankAccount = form.cleaned_data["bank_account"]

            response = AuthorizenetService().execute(
                api.create_customer_payment_profile(
                    customer_profile_id=cprofile.pk,
                    payment=payment,
                    address=form.cleaned_data["address"],
                    default=form.cleaned_data["default"],
                    validation=getattr(
                        settings, "MERCHANT_AUTH_VALIDATION_MODE", "liveMode"
                    ),
                )
            )
            pprofile = CustomerPaymentProfile()
            pprofile.cprofile = cprofile
            pprofile.pk = int(response.customerPaymentProfileId)
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

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        try:
            service = AuthorizenetService()
            response = service.execute(
                api.get_customer_payment_profile(
                    customer_profile_id=self.object.cprofile.pk,
                    payment_profile_id=self.object.pk,
                    include_issuer_info=True,
                )
            )
        except AuthorizenetControllerExecutionError as error:
            response = None
            logger.warning(error)

        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["paymentProfile"] = (
            response.paymentProfile if response is not None else None
        )
        return context


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


class CustomerPaymentProfileDeleteView(HtmxTemplateResponseMixin, DeleteView):
    content_type = "text/html"
    http_method_names = ["post"]
    model = CustomerPaymentProfile
    pk_url_kwarg = "paymentprofile_pk"

    def get_success_url(self) -> str:
        return reverse(
            "terminusgps_payments:list payment profiles",
            kwargs={"customerprofile_pk": self.kwargs["customerprofile_pk"]},
        )

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(
            cprofile__pk=self.kwargs["customerprofile_pk"]
        )
