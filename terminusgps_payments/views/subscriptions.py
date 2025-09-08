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
from terminusgps.authorizenet import api as anet
from terminusgps.authorizenet.controllers import (
    AuthorizenetControllerExecutionError,
)
from terminusgps.django.mixins import HtmxTemplateResponseMixin

from terminusgps_payments import models


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
    model = models.Subscription
    partial_template_name = (
        "terminusgps_payments/subscriptions/partials/_create.html"
    )
    template_name = "terminusgps_payments/subscriptions/create.html"

    @transaction.atomic
    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        try:
            interval, _ = (
                models.SubscriptionScheduleInterval.objects.get_or_create(
                    name="Monthly Payment Interval",
                    length=1,
                    unit=models.SubscriptionScheduleInterval.IntervalUnit.MONTHS,
                )
            )
            subscription = models.Subscription(
                id=None,
                name=form.cleaned_data["name"],
                schedule=models.SubscriptionSchedule.objects.create(
                    interval=interval, start_date=timezone.now()
                ),
                customer_profile=form.cleaned_data["customer_profile"],
                payment_profile=form.cleaned_data["payment_profile"],
                address_profile=form.cleaned_data["address_profile"],
                amount=form.cleaned_data["amount"],
                trial_amount=form.cleaned_data["trial_amount"],
            )
            response = anet.create_subscription(subscription.to_xml())
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
    model = models.Subscription
    partial_template_name = (
        "terminusgps_payments/subscriptions/partials/_detail.html"
    )
    pk_url_kwarg = "subscription_pk"
    queryset = models.Subscription.objects.none()
    template_name = "terminusgps_payments/subscriptions/detail.html"

    def get_queryset(
        self,
    ) -> QuerySet[models.Subscription, models.Subscription]:
        return models.Subscription.objects.filter(
            customer_profile__user=self.request.user
        )


class SubscriptionListView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    allow_empty = True
    content_type = "text/html"
    http_method_names = ["get"]
    model = models.Subscription
    ordering = "name"
    paginate_by = 4
    partial_template_name = (
        "terminusgps_payments/subscriptions/partials/_list.html"
    )
    queryset = models.Subscription.objects.none()
    template_name = "terminusgps_payments/subscriptions/list.html"

    def get_queryset(
        self,
    ) -> QuerySet[models.Subscription, models.Subscription]:
        return models.Subscription.objects.filter(
            customer_profile__user=self.request.user
        ).order_by(self.get_ordering())


class SubscriptionDeleteView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DeleteView
):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    model = models.Subscription
    partial_template_name = (
        "terminusgps_payments/subscriptions/partials/_delete.html"
    )
    pk_url_kwarg = "subscription_pk"
    queryset = models.Subscription.objects.none()
    template_name = "terminusgps_payments/subscriptions/delete.html"
    success_url = reverse_lazy("payments:list subscription")

    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        anet.cancel_subscription(self.object.pk)
        return super().form_valid(form=form)

    def get_queryset(
        self,
    ) -> QuerySet[models.Subscription, models.Subscription]:
        return models.Subscription.objects.filter(
            customer_profile__user=self.request.user
        )


class SubscriptionUpdateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, UpdateView
):
    content_type = "text/html"
    fields = ["payment_profile", "address_profile"]
    http_method_names = ["get", "post"]
    model = models.Subscription
    partial_template_name = (
        "terminusgps_payments/subscriptions/partials/_update.html"
    )
    pk_url_kwarg = "subscription_pk"
    queryset = models.Subscription.objects.none()
    template_name = "terminusgps_payments/subscriptions/update.html"

    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        if form.changed_data:
            anet.update_subscription(
                self.object.pk, self.object.to_xml(fields=form.changed_data)
            )
        return super().form_valid(form=form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields[
            "payment_profile"
        ].queryset = models.PaymentProfile.objects.filter(
            customer_profile__user=self.request.user
        )
        form.fields["payment_profile"].empty_label = None
        form.fields["payment_profile"].widget.attrs.update(
            {"class": "p-2 rounded border bg-white"}
        )
        form.fields[
            "address_profile"
        ].queryset = models.AddressProfile.objects.filter(
            customer_profile__user=self.request.user
        )
        form.fields["address_profile"].empty_label = None
        form.fields["address_profile"].widget.attrs.update(
            {"class": "p-2 rounded border bg-white"}
        )
        return form

    def get_queryset(
        self,
    ) -> QuerySet[models.Subscription, models.Subscription]:
        return models.Subscription.objects.filter(
            customer_profile__user=self.request.user
        )
