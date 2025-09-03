from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView
from terminusgps.authorizenet import subscriptions
from terminusgps.authorizenet.controllers import (
    AuthorizenetControllerExecutionError,
)
from terminusgps.django.mixins import HtmxTemplateResponseMixin

from terminusgps_payments.models import Subscription


class SubscriptionCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, CreateView
):
    content_type = "text/html"
    fields = [
        "name",
        "customer_profile",
        "payment_profile",
        "address_profile",
        "schedule",
        "amount",
    ]
    http_method_names = ["get", "post"]
    model = Subscription
    partial_template_name = (
        "terminusgps_payments/subscriptions/partials/_create.html"
    )
    success_url = reverse_lazy("payments:create subscription")
    template_name = "terminusgps_payments/subscriptions/create.html"

    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        try:
            sub = Subscription(
                name=form.cleaned_data["name"],
                schedule=form.cleaned_data["schedule"],
                amount=form.cleaned_data["amount"],
                trial_amount=form.cleaned_data["trial_amount"],
                customer_profile=form.cleaned_data["customer_profile"],
                payment_profile=form.cleaned_data["payment_profile"],
                address_profile=form.cleaned_data["address_profile"],
            )
            response = subscriptions.create_subscription(
                subscription_obj=sub.to_xml()
            )
            sub.pk = int(response.subscriptionId)
            sub.save()
            return HttpResponseRedirect(self.get_success_url())
        except AuthorizenetControllerExecutionError as e:
            match e.code:
                case _:
                    form.add_error(
                        None,
                        ValidationError(
                            _("Whoops! '%(message)s'"),
                            code="invalid",
                            params={"message": e.message},
                        ),
                    )
            return self.form_invalid(form=form)
