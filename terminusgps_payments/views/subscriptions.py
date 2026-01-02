import typing

from django import forms
from django.http import HttpRequest
from django.urls import reverse
from django.views.generic import CreateView, DetailView, UpdateView
from terminusgps.mixins import HtmxTemplateResponseMixin

from ..models import CustomerProfile, Subscription
from .mixins import CustomerProfileExclusiveMixin


class SubscriptionCreateView(
    CustomerProfileExclusiveMixin, HtmxTemplateResponseMixin, CreateView
):
    content_type = "text/html"
    fields = [
        "name",
        "amount",
        "trial_amount",
        "total_occurrences",
        "trial_occurrences",
        "aprofile",
        "pprofile",
    ]
    http_method_names = ["get", "post"]
    model = Subscription
    partial_template_name = (
        "terminusgps_payments/subscriptions/partials/_create.html"
    )
    template_name = "terminusgps_payments/subscriptions/create.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        try:
            self.cprofile = CustomerProfile.objects.get(
                pk=kwargs["customerprofile_pk"]
            )
        except CustomerProfile.DoesNotExist:
            self.cprofile = None
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customerprofile"] = self.cprofile
        return context

    def get_form(self, form_class=None) -> forms.Form:
        form = super().get_form(form_class=form_class)
        payment_qs = self.cprofile.payment_profiles.all()
        address_qs = self.cprofile.address_profiles.all()
        form.fields["pprofile"].queryset = payment_qs
        form.fields["aprofile"].queryset = address_qs
        form.fields["pprofile"].empty_label = None
        form.fields["aprofile"].empty_label = None
        form.fields["pprofile"].widget.attrs.update(
            {
                "hx-get": reverse(
                    "terminusgps_payments:choice payment profiles",
                    kwargs={"customerprofile_pk": self.cprofile.pk},
                ),
                "hx-target": "this",
                "hx-trigger": "load once",
                "hx-swap": "innerHTML",
            }
        )
        form.fields["aprofile"].widget.attrs.update(
            {
                "hx-get": reverse(
                    "terminusgps_payments:choice address profiles",
                    kwargs={"customerprofile_pk": self.cprofile.pk},
                ),
                "hx-target": "this",
                "hx-trigger": "load once",
                "hx-swap": "innerHTML",
            }
        )
        return form


class SubscriptionDetailView(
    CustomerProfileExclusiveMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    http_method_names = ["get"]
    model = Subscription
    partial_template_name = (
        "terminusgps_payments/subscriptions/partials/_detail.html"
    )
    pk_url_kwarg = "subscription_pk"
    template_name = "terminusgps_payments/subscriptions/detail.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        try:
            self.cprofile = CustomerProfile.objects.get(
                pk=kwargs["customerprofile_pk"]
            )
        except CustomerProfile.DoesNotExist:
            self.cprofile = None
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customerprofile"] = self.cprofile
        return context


class SubscriptionUpdateView(
    CustomerProfileExclusiveMixin, HtmxTemplateResponseMixin, UpdateView
):
    content_type = "text/html"
    fields = ["aprofile", "pprofile"]
    http_method_names = ["get", "post"]
    model = Subscription
    partial_template_name = (
        "terminusgps_payments/subscriptions/partials/_update.html"
    )
    pk_url_kwarg = "subscription_pk"
    template_name = "terminusgps_payments/subscriptions/update.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        try:
            self.cprofile = CustomerProfile.objects.get(
                pk=kwargs["customerprofile_pk"]
            )
        except CustomerProfile.DoesNotExist:
            self.cprofile = None
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customerprofile"] = self.cprofile
        return context

    def get_form(self, form_class=None) -> forms.Form:
        form = super().get_form(form_class=form_class)
        payment_qs = self.cprofile.payment_profiles.all()
        address_qs = self.cprofile.address_profiles.all()
        form.fields["pprofile"].queryset = payment_qs
        form.fields["aprofile"].queryset = address_qs
        form.fields["pprofile"].empty_label = None
        form.fields["aprofile"].empty_label = None
        form.fields["pprofile"].widget.attrs.update(
            {
                "hx-get": reverse(
                    "terminusgps_payments:choice payment profiles",
                    kwargs={"customerprofile_pk": self.cprofile.pk},
                ),
                "hx-target": "this",
                "hx-trigger": "load once",
                "hx-swap": "innerHTML",
            }
        )
        form.fields["aprofile"].widget.attrs.update(
            {
                "hx-get": reverse(
                    "terminusgps_payments:choice address profiles",
                    kwargs={"customerprofile_pk": self.cprofile.pk},
                ),
                "hx-target": "this",
                "hx-trigger": "load once",
                "hx-swap": "innerHTML",
            }
        )
        return form
