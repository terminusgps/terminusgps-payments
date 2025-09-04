from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from terminusgps.authorizenet import subscriptions
from terminusgps.authorizenet.controllers import (
    AuthorizenetControllerExecutionError,
)
from terminusgps.django.mixins import HtmxTemplateResponseMixin

from terminusgps_payments.models import (
    AddressProfile,
    PaymentProfile,
    Subscription,
    SubscriptionSchedule,
    SubscriptionScheduleInterval,
)


class SubscriptionCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, CreateView
):
    content_type = "text/html"
    fields = [
        "customer_profile",
        "payment_profile",
        "address_profile",
        "name",
        "amount",
        "trial_amount",
    ]
    http_method_names = ["get", "post"]
    model = Subscription
    partial_template_name = (
        "terminusgps_payments/subscriptions/partials/_create.html"
    )
    template_name = "terminusgps_payments/subscriptions/create.html"

    @transaction.atomic
    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        try:
            interval, _ = SubscriptionScheduleInterval.objects.get_or_create(
                name="Monthly Payment Interval",
                length=1,
                unit=SubscriptionScheduleInterval.IntervalUnit.MONTHS,
            )
            subscription = Subscription(
                id=None,
                name=form.cleaned_data["name"],
                schedule=SubscriptionSchedule.objects.create(
                    interval=interval, start_date=timezone.now()
                ),
                customer_profile=form.cleaned_data["customer_profile"],
                payment_profile=form.cleaned_data["payment_profile"],
                address_profile=form.cleaned_data["address_profile"],
                amount=form.cleaned_data["amount"],
                trial_amount=form.cleaned_data["trial_amount"],
            )
            response = subscriptions.create_subscription(subscription.to_xml())
            subscription.pk = int(response.subscriptionId)
            subscription.save()
            return HttpResponseRedirect(subscription.get_absolute_url())
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


class SubscriptionDetailView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    http_method_names = ["get"]
    model = Subscription
    partial_template_name = (
        "terminusgps_payments/subscriptions/partials/_detail.html"
    )
    pk_url_kwarg = "subscription_pk"
    queryset = Subscription.objects.none()
    template_name = "terminusgps_payments/subscriptions/detail.html"

    def get_queryset(self) -> QuerySet[Subscription, Subscription]:
        return Subscription.objects.filter(
            customer_profile__user=self.request.user
        )


class SubscriptionListView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    allow_empty = True
    content_type = "text/html"
    http_method_names = ["get"]
    model = Subscription
    ordering = "name"
    paginate_by = 4
    partial_template_name = (
        "terminusgps_payments/subscriptions/partials/_list.html"
    )
    queryset = Subscription.objects.none()
    template_name = "terminusgps_payments/subscriptions/list.html"

    def get_queryset(self) -> QuerySet[Subscription, Subscription]:
        return Subscription.objects.filter(
            customer_profile__user=self.request.user
        ).order_by(self.get_ordering())


class SubscriptionDeleteView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DeleteView
):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    model = Subscription
    partial_template_name = (
        "terminusgps_payments/subscriptions/partials/_delete.html"
    )
    pk_url_kwarg = "subscription_pk"
    queryset = Subscription.objects.none()
    template_name = "terminusgps_payments/subscriptions/delete.html"
    success_url = reverse_lazy("payments:list subscription")

    def get_queryset(self) -> QuerySet[Subscription, Subscription]:
        return Subscription.objects.filter(
            customer_profile__user=self.request.user
        )


class SubscriptionUpdateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, UpdateView
):
    content_type = "text/html"
    fields = ["payment_profile", "address_profile", "name"]
    http_method_names = ["get", "post"]
    model = Subscription
    partial_template_name = (
        "terminusgps_payments/subscriptions/partials/_update.html"
    )
    pk_url_kwarg = "subscription_pk"
    queryset = Subscription.objects.none()
    template_name = "terminusgps_payments/subscriptions/update.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["name"].widget.attrs.update(
            {"class": "p-2 rounded border bg-white"}
        )
        form.fields[
            "payment_profile"
        ].queryset = PaymentProfile.objects.filter(
            customer_profile__user=self.request.user
        )
        form.fields["payment_profile"].empty_label = None
        form.fields["payment_profile"].widget.attrs.update(
            {"class": "p-2 rounded border bg-white"}
        )
        form.fields[
            "address_profile"
        ].queryset = AddressProfile.objects.filter(
            customer_profile__user=self.request.user
        )
        form.fields["address_profile"].empty_label = None
        form.fields["address_profile"].widget.attrs.update(
            {"class": "p-2 rounded border bg-white"}
        )
        return form

    def get_queryset(self) -> QuerySet[Subscription, Subscription]:
        return Subscription.objects.filter(
            customer_profile__user=self.request.user
        )
