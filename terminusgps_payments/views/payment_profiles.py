import logging
import typing

from authorizenet import apicontractsv1
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet
from django.forms import Form
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, DetailView, FormView, ListView
from lxml.objectify import ObjectifiedElement
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


class CreditCardCreateView(HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    form_class = CustomerPaymentProfileCreditCardCreateForm
    http_method_names = ["get", "post"]
    partial_template_name = "terminusgps_payments/payment_profiles/partials/_create_credit_card.html"
    template_name = (
        "terminusgps_payments/payment_profiles/create_credit_card.html"
    )

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        self.cprofile = CustomerProfile.objects.get(
            pk=kwargs["customerprofile_pk"]
        )
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customerprofile"] = self.cprofile
        return context

    def get_success_url(self) -> str:
        return reverse(
            "terminusgps_payments:list payment profiles",
            kwargs={"customerprofile_pk": self.cprofile.pk},
        )

    @transaction.atomic
    def form_valid(self, form: forms.Form) -> HttpResponse:
        try:
            payment = apicontractsv1.paymentType()
            payment.creditCard = form.cleaned_data["credit_card"]
            response = AuthorizenetService().execute(
                api.create_customer_payment_profile(
                    customer_profile_id=self.cprofile.pk,
                    payment=payment,
                    address=form.cleaned_data["address"],
                    default=form.cleaned_data["default"],
                    validation=getattr(
                        settings, "MERCHANT_AUTH_VALIDATION_MODE", "liveMode"
                    ),
                )
            )
            pprofile = CustomerPaymentProfile()
            pprofile.pk = int(response.customerPaymentProfileId)
            pprofile.cprofile = self.cprofile
            pprofile.save()
            return super().form_valid(form=form)
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


class BankAccountCreateView(HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    form_class = CustomerPaymentProfileBankAccountCreateForm
    http_method_names = ["get", "post"]
    partial_template_name = "terminusgps_payments/payment_profiles/partials/_create_bank_account.html"
    template_name = (
        "terminusgps_payments/payment_profiles/create_bank_account.html"
    )

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        self.cprofile = CustomerProfile.objects.get(
            pk=kwargs["customerprofile_pk"]
        )
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customerprofile"] = self.cprofile
        return context

    def get_success_url(self) -> str:
        return reverse(
            "terminusgps_payments:list payment profiles",
            kwargs={"customerprofile_pk": self.cprofile.pk},
        )

    @transaction.atomic
    def form_valid(self, form: forms.Form) -> HttpResponse:
        try:
            payment = apicontractsv1.paymentType()
            payment.bankAccount = form.cleaned_data["bank_account"]
            response = AuthorizenetService().execute(
                api.create_customer_payment_profile(
                    customer_profile_id=self.cprofile.pk,
                    payment=payment,
                    address=form.cleaned_data["address"],
                    default=form.cleaned_data["default"],
                    validation=getattr(
                        settings, "MERCHANT_AUTH_VALIDATION_MODE", "liveMode"
                    ),
                )
            )
            pprofile = CustomerPaymentProfile()
            pprofile.pk = int(response.customerPaymentProfileId)
            pprofile.cprofile = self.cprofile
            pprofile.save()
            return super().form_valid(form=form)
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


class CustomerPaymentProfileCreateView(HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    partial_template_name = (
        "terminusgps_payments/payment_profiles/partials/_create.html"
    )
    template_name = "terminusgps_payments/payment_profiles/create.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        self.cprofile = CustomerProfile.objects.get(
            pk=kwargs["customerprofile_pk"]
        )
        return super().setup(request, *args, **kwargs)

    def get_success_url(self) -> str:
        return reverse(
            "terminusgps_payments:list payment profiles",
            kwargs={"customerprofile_pk": self.kwargs["customerprofile_pk"]},
        )

    @transaction.atomic
    def form_valid(self, form: Form) -> HttpResponse:
        try:
            payment = apicontractsv1.paymentType()
            if "credit_card" in form.cleaned_data:
                payment.creditCard = form.cleaned_data["credit_card"]
            elif "bank_account" in form.cleaned_data:
                payment.bankAccount = form.cleaned_data["bank_account"]
            else:
                raise ValueError()

            response = AuthorizenetService().execute(
                api.create_customer_payment_profile(
                    customer_profile_id=self.cprofile.pk,
                    payment=payment,
                    address=form.cleaned_data["address"],
                    default=form.cleaned_data["default"],
                    validation=getattr(
                        settings, "MERCHANT_AUTH_VALIDATION_MODE", "liveMode"
                    ),
                )
            )
            CustomerPaymentProfile.objects.create(
                id=int(response.customerPaymentProfileId),
                cprofile=self.cprofile,
            )
            return super().form_valid(form=form)
        except ValueError as error:
            form.add_error(
                None,
                ValidationError(
                    _("Whoops! %(error)s"),
                    code="invalid",
                    params={"error": error},
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
        context["customerprofile"] = self.cprofile
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

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        try:
            self.cprofile = CustomerProfile.objects.get(
                pk=kwargs["customerprofile_pk"]
            )
        except CustomerProfile.DoesNotExist:
            self.cprofile = None
        return super().setup(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(cprofile=self.cprofile).order_by(
            self.get_ordering()
        )

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customerprofile"] = self.cprofile
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


class CustomerPaymentProfileChoiceView(HtmxTemplateResponseMixin, ListView):
    content_type = "text/html"
    http_method_names = ["get"]
    model = CustomerPaymentProfile
    partial_template_name = (
        "terminusgps_payments/payment_profiles/partials/_choices.html"
    )
    template_name = "terminusgps_payments/payment_profiles/choices.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        try:
            self.cprofile = CustomerProfile.objects.get(
                pk=kwargs["customerprofile_pk"]
            )
        except CustomerProfile.DoesNotExist:
            self.cprofile = None
        return super().setup(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(cprofile=self.cprofile)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        try:
            context: dict[str, typing.Any] = super().get_context_data(**kwargs)
            context["choices"] = self.get_choices()
        except AuthorizenetControllerExecutionError as error:
            logger.warning(error)
            context["choices"] = []
        return context

    def get_choices(self) -> list[tuple[int, str]]:
        service = AuthorizenetService()
        choices = []

        try:
            for obj in self.get_queryset():
                resp = obj.get_from_authorizenet(service)
                choice = {"value": obj.pk, "label": self._extract_label(resp)}
                choices.append(choice)
            return choices
        except AuthorizenetControllerExecutionError as error:
            logger.critical(error)
            raise

    def _extract_label(self, response: ObjectifiedElement) -> str:
        payment = response.paymentProfile.payment
        if hasattr(payment, "creditCard"):
            card_type = str(payment.creditCard.cardType)
            card_num = str(payment.creditCard.cardNumber)
            return f"{card_type} {card_num}"
        elif hasattr(payment, "bankAccount"):
            acc_type = str(payment.bankAccount.accountType)
            acc_num = str(payment.bankAccount.accountNumber)
            return f"{acc_type} {acc_num}"
        return str(response.paymentProfile.customerPaymentProfileId)
