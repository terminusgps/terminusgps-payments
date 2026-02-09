import typing

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import CreateView, DeleteView, DetailView, ListView
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
    AuthorizenetService,
)

from terminusgps_payments.models import CustomerProfile
from terminusgps_payments.views.mixins import (
    AuthorizenetMultipleObjectMixin,
    AuthorizenetSingleObjectMixin,
    HtmxTemplateResponseMixin,
)


class AuthorizenetCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, CreateView
):
    content_type = "text/html"
    form_class = None
    http_method_names = ["get", "post"]
    model = None

    def get_success_url(self):
        return self.success_url

    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        try:
            self.object = form.save(commit=False)
            self.object.save(push=True)
            return HttpResponseRedirect(self.get_success_url())
        except AuthorizenetControllerExecutionError as error:
            form.add_error(
                None,
                ValidationError(
                    "%(error)s", code="invalid", params={"error": str(error)}
                ),
            )
            return self.form_invalid(form=form)

    def get_initial(self, **kwargs) -> dict[str, typing.Any]:
        initial: dict[str, typing.Any] = super().get_initial(**kwargs)
        try:
            initial["customer_profile"] = (
                CustomerProfile.objects.get(user=self.request.user)
                if hasattr(self.request, "user")
                else None
            )
        except CustomerProfile.DoesNotExist:
            initial["customer_profile"] = None
        return initial


class AuthorizenetListView(
    LoginRequiredMixin,
    HtmxTemplateResponseMixin,
    AuthorizenetMultipleObjectMixin,
    ListView,
):
    allow_empty = True
    content_type = "text/html"
    http_method_names = ["get"]
    ordering = "pk"
    paginate_by = 4


class AuthorizenetDeleteView(
    LoginRequiredMixin,
    HtmxTemplateResponseMixin,
    AuthorizenetSingleObjectMixin,
    DeleteView,
):
    content_type = "text/html"
    http_method_names = ["get", "post"]

    def get_success_url(self):
        return self.success_url

    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        try:
            service = AuthorizenetService()
            success_url = self.get_success_url()
            self.object._delete_in_authorizenet(service=service)
            self.object.delete()
            return HttpResponseRedirect(success_url)
        except AuthorizenetControllerExecutionError as error:
            form.add_error(
                None,
                ValidationError(
                    "%(error)s", code="invalid", params={"error": str(error)}
                ),
            )
            return self.form_invalid(form=form)


class AuthorizenetDetailView(
    LoginRequiredMixin,
    HtmxTemplateResponseMixin,
    AuthorizenetSingleObjectMixin,
    DetailView,
):
    content_type = "text/html"
    http_method_names = ["get"]
