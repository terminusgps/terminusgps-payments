import typing

from authorizenet import apicontractsv1
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template.defaultfilters import date
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    DeleteView,
    DetailView,
    FormView,
    TemplateView,
    UpdateView,
)
from lxml.objectify import ObjectifiedElement
from shapeshifter.views import MultiFormView
from terminusgps.authorizenet import api
from terminusgps.authorizenet.service import AuthorizenetError
from terminusgps.mixins import HtmxTemplateResponseMixin

from terminusgps_payments import forms, tasks
from terminusgps_payments.mixins import (
    AuthorizenetServiceMixin,
    CustomerProfileMixin,
)
from terminusgps_payments.models import Subscription, SubscriptionPlan


def get_payment_profile_choices(
    paymentProfiles: ObjectifiedElement,
) -> list[tuple[int, str]]:
    choices = []
    for p in paymentProfiles:
        id = p.customerPaymentProfileId
        if hasattr(p.payment, "creditCard"):
            label = f"{p.payment.creditCard.cardType} {p.payment.creditCard.cardNumber}"
            choices.append((id, label))
        if hasattr(p.payment, "bankAccount"):
            label = f"{p.payment.bankAccount.bankName} {p.payment.bankAccount.accountNumber}"
            choices.append((id, label))
    return choices


def get_shipping_profile_choices(
    shipToList: ObjectifiedElement,
) -> list[tuple[int, str]]:
    choices = []
    for p in shipToList:
        id = p.customerAddressId
        label = p.address
        choices.append((id, label))
    return choices


class AddCreditCardView(
    LoginRequiredMixin,
    HtmxTemplateResponseMixin,
    AuthorizenetServiceMixin,
    CustomerProfileMixin,
    SuccessMessageMixin,
    MultiFormView,
):
    content_type = "text/html"
    form_classes = (forms.AddressForm, forms.CreditCardForm)
    http_method_names = ["get", "post"]
    success_message = "Credit card was successfully added to your profile."
    success_url = reverse_lazy("terminusgps_payments:customer profile details")
    template_name = "terminusgps_payments/add_credit_card.html"

    def forms_valid(self) -> HttpResponse:
        forms = self.get_forms()
        billTo = forms["addressform"].build_contract()
        creditCard = forms["creditcardform"].build_contract()
        payment = apicontractsv1.paymentType()
        payment.creditCard = creditCard
        contract = apicontractsv1.customerPaymentProfileType()
        contract.billTo = billTo
        contract.payment = payment
        try:
            self.service.execute(
                api.create_customer_payment_profile(
                    customer_profile_id=self.customer_profile.pk,
                    contract=contract,
                )
            )
            return HttpResponseRedirect(self.get_success_url())
        except AuthorizenetError as error:
            messages.error(self.request, error)
            return self.forms_invalid()


class AddBankAccountView(
    LoginRequiredMixin,
    HtmxTemplateResponseMixin,
    AuthorizenetServiceMixin,
    CustomerProfileMixin,
    SuccessMessageMixin,
    MultiFormView,
):
    content_type = "text/html"
    form_classes = (forms.AddressForm, forms.BankAccountForm)
    http_method_names = ["get", "post"]
    success_message = "Bank account was successfully added to your profile."
    success_url = reverse_lazy("terminusgps_payments:customer profile details")
    template_name = "terminusgps_payments/add_bank_account.html"

    def forms_valid(self) -> HttpResponse:
        forms = self.get_forms()
        billTo = forms["addressform"].build_contract()
        payment = apicontractsv1.paymentType()
        payment.bankAccount = forms["bankaccountform"].build_contract()
        contract = apicontractsv1.customerPaymentProfileType()
        contract.billTo = billTo
        contract.payment = payment

        try:
            kwargs = {
                "customer_profile_id": self.customer_profile.pk,
                "contract": contract,
            }
            self.service.execute(api.create_customer_payment_profile(**kwargs))
            return HttpResponseRedirect(self.get_success_url())
        except AuthorizenetError as error:
            messages.error(self.request, error)
            return self.forms_invalid()


class CustomerProfileDetailView(
    LoginRequiredMixin,
    HtmxTemplateResponseMixin,
    AuthorizenetServiceMixin,
    CustomerProfileMixin,
    TemplateView,
):
    content_type = "text/html"
    http_method_names = ["get"]
    template_name = "terminusgps_payments/customerprofile_detail.html"

    def get_include_issuer_info(self) -> bool:
        return self.request.GET.get("include_issuer_info") == "on"

    def get_unmask_expiration_date(self) -> bool:
        return self.request.GET.get("unmask_expiration_date") == "on"

    def get_authorizenet_response(self) -> ObjectifiedElement | None:
        try:
            kwargs = {
                "customer_profile_id": self.customer_profile.pk,
                "include_issuer_info": self.get_include_issuer_info(),
                "unmask_expiration_date": self.get_unmask_expiration_date(),
            }
            return self.service.execute(api.get_customer_profile(**kwargs))
        except AuthorizenetError as error:
            messages.error(self.request, error)
            return

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context = super().get_context_data(**kwargs)
        context["response"] = self.get_authorizenet_response()
        return context


class SubscriptionDeleteView(
    LoginRequiredMixin,
    HtmxTemplateResponseMixin,
    AuthorizenetServiceMixin,
    CustomerProfileMixin,
    DeleteView,
):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    model = Subscription
    success_url = reverse_lazy("terminusgps_payments:customer profile details")
    template_name = "terminusgps_payments/subscription_delete.html"

    def form_valid(self, form) -> HttpResponse:
        try:
            kwargs = {"subscription_id": self.object.pk}
            self.service.execute(api.cancel_subscription(**kwargs))
            tasks.send_subscription_canceled_email.enqueue(
                recipient_list=[self.customer_profile.user.email],
                context={
                    "plan_name": form.cleaned_data["plan"].name,
                    "plan_amount": str(form.cleaned_data["plan"].amount),
                    "plan_description": form.cleaned_data["plan"].description,
                    "date": date(timezone.now(), "l, F jS, Y"),
                },
            )
            return HttpResponseRedirect(self.get_success_url())
        except AuthorizenetError as error:
            form.add_error(
                None,
                ValidationError(
                    "%(error)s", code="invalid", params={"error": error}
                ),
            )
            return self.form_invalid(form=form)


class SubscriptionUpdateView(
    LoginRequiredMixin,
    HtmxTemplateResponseMixin,
    AuthorizenetServiceMixin,
    CustomerProfileMixin,
    UpdateView,
):
    content_type = "text/html"
    form_class = forms.UpdateSubscriptionForm
    http_method_names = ["get", "post"]
    model = Subscription
    template_name = "terminusgps_payments/subscription_update.html"

    def get_authorizenet_response(self) -> ObjectifiedElement | None:
        try:
            kwargs = {
                "customer_profile_id": self.customer_profile.pk,
                "include_issuer_info": False,
                "unmask_expiration_date": False,
            }
            return self.service.execute(api.get_customer_profile(**kwargs))
        except AuthorizenetError as error:
            messages.error(self.request, error)
            return

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.pop("instance")
        return kwargs

    def get_form(self, form_class=None) -> forms.UpdateSubscriptionForm:
        form = super().get_form(form_class=form_class)
        response = self.get_authorizenet_response()
        if response is not None:
            paymentProfiles = response.profile.paymentProfiles
            shipToList = response.profile.shipToList
            if len(paymentProfiles) > 0:
                choices = get_payment_profile_choices(paymentProfiles)
                form.fields["payment_profile"].choices = choices
            if len(shipToList) > 0:
                choices = get_shipping_profile_choices(shipToList)
                form.fields["shipping_profile"].choices = choices
        return form

    def form_valid(self, form: forms.UpdateSubscriptionForm) -> HttpResponse:
        try:
            customerProfileId = self.customer_profile.pk
            customerAddressId = form.cleaned_data["shipping_profile"]
            customerPaymentProfileId = form.cleaned_data["payment_profile"]
            profile = apicontractsv1.customerProfileIdType()
            profile.customerProfileId = str(customerProfileId)
            profile.customerAddressId = str(customerAddressId)
            profile.customerPaymentProfileId = str(customerPaymentProfileId)
            contract = apicontractsv1.ARBSubscriptionType()
            contract.profile = profile
            self.service.execute(
                api.update_subscription(
                    subscription_id=self.object.pk, contract=contract
                )
            )
            return HttpResponseRedirect(self.object.get_absolute_url())
        except AuthorizenetError as error:
            form.add_error(
                None,
                ValidationError(
                    "%(error)s", code="invalid", params={"error": error}
                ),
            )
            return self.form_invalid(form=form)


class SubscriptionDetailView(
    LoginRequiredMixin,
    HtmxTemplateResponseMixin,
    AuthorizenetServiceMixin,
    CustomerProfileMixin,
    DetailView,
):
    content_type = "text/html"
    http_method_names = ["get"]
    model = Subscription

    def get_include_transactions(self) -> bool:
        return self.request.GET.get("include_transactions") == "on"

    def get_authorizenet_response(self) -> ObjectifiedElement | None:
        try:
            kwargs = {
                "subscription_id": self.object.pk,
                "include_transactions": self.get_include_transactions(),
            }
            return self.service.execute(api.get_subscription(**kwargs))
        except AuthorizenetError as error:
            messages.error(self.request, error)
            return

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context = super().get_context_data(**kwargs)
        context["response"] = self.get_authorizenet_response()
        return context


class SubscriptionCreateView(
    LoginRequiredMixin,
    HtmxTemplateResponseMixin,
    AuthorizenetServiceMixin,
    CustomerProfileMixin,
    FormView,
):
    content_type = "text/html"
    form_class = forms.CreateSubscriptionForm
    http_method_names = ["get", "post"]
    template_name = "terminusgps_payments/subscription_create.html"

    def get_authorizenet_response(self) -> ObjectifiedElement | None:
        try:
            return self.service.execute(
                api.get_customer_profile(
                    customer_profile_id=self.customer_profile.pk
                )
            )
        except AuthorizenetError as error:
            messages.error(self.request, error)
            return

    def get_plans(self) -> QuerySet:
        qs = SubscriptionPlan.objects.all()
        visible = SubscriptionPlan.SubscriptionPlanVisibility.VISIBLE
        return qs.filter(visibility=visible)

    def get_contract(
        self, form: forms.CreateSubscriptionForm
    ) -> apicontractsv1.ARBSubscriptionType:
        plan = form.cleaned_data["plan"]
        schedule = apicontractsv1.paymentScheduleType()
        schedule.totalOccurrences = plan.total_occurrences
        schedule.trialOccurrences = plan.trial_occurrences
        schedule.startDate = timezone.now()
        schedule.interval = apicontractsv1.paymentScheduleTypeInterval()
        schedule.interval.length = plan.length
        schedule.interval.unit = plan.unit
        customerProfileId = str(self.customer_profile.pk)
        customerAddressId = form.cleaned_data["shipping_profile"]
        customerPaymentProfileId = form.cleaned_data["payment_profile"]
        profile = apicontractsv1.customerProfileIdType()
        profile.customerProfileId = customerProfileId
        profile.customerAddressId = customerAddressId
        profile.customerPaymentProfileId = customerPaymentProfileId
        contract = apicontractsv1.ARBSubscriptionType()
        contract.name = plan.name
        contract.amount = plan.amount
        contract.trialAmount = plan.trial_amount
        contract.paymentSchedule = schedule
        contract.profile = profile
        return contract

    def get_form(self, form_class=None) -> forms.CreateSubscriptionForm:
        form = super().get_form(form_class=form_class)
        form.fields["plan"].queryset = self.get_plans()
        form.fields["plan"].empty_label = None
        response = self.get_authorizenet_response()
        if response is not None:
            paymentProfiles = response.profile.paymentProfiles
            shipToList = response.profile.shipToList
            if len(paymentProfiles) > 0:
                choices = get_payment_profile_choices(paymentProfiles)
                form.fields["payment_profile"].choices = choices
            if len(shipToList) > 0:
                choices = get_shipping_profile_choices(shipToList)
                form.fields["shipping_profile"].choices = choices
        return form

    def form_valid(self, form: forms.CreateSubscriptionForm) -> HttpResponse:
        try:
            contract = self.get_contract(form)
            response = self.service.execute(
                api.create_subscription(contract=contract)
            )
            tasks.send_subscription_created_email.enqueue(
                recipient_list=[self.customer_profile.user.email],
                context={
                    "plan_name": form.cleaned_data["plan"].name,
                    "plan_amount": str(form.cleaned_data["plan"].amount),
                    "plan_description": form.cleaned_data["plan"].description,
                    "date": date(timezone.now(), "l, F jS, Y"),
                },
            )
            self.object = form.save(commit=False)
            self.object.pk = response.subscriptionId
            self.object.customer_profile = self.customer_profile
            self.object.save()
            return HttpResponseRedirect(self.object.get_absolute_url())
        except AuthorizenetError as error:
            form.add_error(
                None,
                ValidationError(
                    "%(error)s", code="invalid", params={"error": error}
                ),
            )
            return self.form_invalid(form=form)


class SubscriptionPlanDetailView(HtmxTemplateResponseMixin, DetailView):
    content_type = "text/html"
    http_method_names = ["get"]
    model = SubscriptionPlan
    template_name = "terminusgps_payments/subscriptionplan_detail.html"

    def get_object(self, queryset=None) -> SubscriptionPlan:
        if queryset is None:
            queryset = self.get_queryset()
        pk = self.request.GET.get("plan")
        if pk is None:
            raise Http404()
        try:
            return queryset.get(pk=pk)
        except SubscriptionPlan.DoesNotExist:
            raise Http404()
