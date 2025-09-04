from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, FormView, ListView
from terminusgps.django.mixins import HtmxTemplateResponseMixin

from terminusgps_payments import forms
from terminusgps_payments.models import PaymentProfile


class PaymentProfileCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    extra_context = {"title": "Create Payment Method"}
    form_class = forms.PaymentProfileCreationForm
    http_method_names = ["get", "post"]
    partial_template_name = (
        "terminusgps_payments/payment_profiles/partials/_create.html"
    )
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    success_url = reverse_lazy("payments:account")
    template_name = "terminusgps_payments/payment_profiles/create.html"

    def get_form(self, form_class=None) -> forms.PaymentProfileCreationForm:
        form = super().get_form(form_class=form_class)
        form.fields["address"].widget.attrs.update(
            {"class": "p-2 rounded border w-full"}
        )
        form.fields["credit_card"].widget.attrs.update(
            {"class": "p-2 rounded border w-full"}
        )
        return form


class PaymentProfileDetailView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    http_method_names = ["get"]
    model = PaymentProfile
    partial_template_name = (
        "terminusgps_payments/payment_profiles/partials/_detail.html"
    )
    permission_denied_message = "Please login to view this content."
    pk_url_kwarg = "profile_pk"
    queryset = PaymentProfile.objects.none()
    raise_exception = False
    template_name = "terminusgps_payments/payment_profiles/detail.html"

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(
            customer_profile__user=self.request.user
        )

    def get_context_data(self, **kwargs) -> dict:
        context: dict = super().get_context_data(**kwargs)
        if obj := kwargs.get("object"):
            context["profile"] = obj.get_authorizenet_profile()
        return context


class PaymentProfileDeleteView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DeleteView
):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    model = PaymentProfile
    partial_template_name = (
        "terminusgps_payments/payment_profiles/partials/_delete.html"
    )
    permission_denied_message = "Please login to view this content."
    pk_url_kwarg = "profile_pk"
    queryset = PaymentProfile.objects.none()
    raise_exception = False
    template_name = "terminusgps_payments/payment_profiles/delete.html"

    def get_queryset(self) -> QuerySet[PaymentProfile, PaymentProfile]:
        return PaymentProfile.objects.filter(
            customer_profile__user=self.request.user
        )


class PaymentProfileListView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    allow_empty = True
    content_type = "text/html"
    http_method_names = ["get"]
    model = PaymentProfile
    ordering = "pk"
    paginate_by = 4
    partial_template_name = (
        "terminusgps_payments/payment_profiles/partials/_list.html"
    )
    permission_denied_message = "Please login to view this content."
    queryset = PaymentProfile.objects.none()
    raise_exception = False
    template_name = "terminusgps_payments/payment_profiles/list.html"

    def get_queryset(self) -> QuerySet[PaymentProfile, PaymentProfile]:
        return PaymentProfile.objects.filter(
            customer_profile__user=self.request.user
        ).order_by(self.get_ordering())
