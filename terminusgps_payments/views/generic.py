import typing

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)
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


class AuthorizenetSyncView(LoginRequiredMixin, View):
    content_type = "text/html"
    http_method_names = ["post"]
    id_attr = None
    list_attr = None
    model = None

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        if self.id_attr is None:
            raise ValueError("'id_attr' attribute is required.")
        if self.list_attr is None:
            raise ValueError("'list_attr' attribute is required.")
        if self.model is None:
            raise ValueError("'model' attribute is required.")
        return super().setup(request, *args, **kwargs)

    @transaction.atomic
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        try:
            customer_profile = CustomerProfile.objects.get(user=request.user)
            service = AuthorizenetService()
            data = customer_profile.pull(service=service)
            if hasattr(data, "profile"):
                qs = self.model.objects.filter(
                    customer_profile=customer_profile
                )
                if not hasattr(data.profile, self.list_attr):
                    qs.delete()
                else:
                    id_list = [
                        int(getattr(subprofile, self.id_attr))
                        for subprofile in getattr(data.profile, self.list_attr)
                    ]
                    for pk in id_list:
                        obj = self.model(
                            pk=pk, customer_profile=customer_profile
                        )
                        obj.save(push=False, service=service)
                    qs.exclude(pk__in=id_list).delete()
            return HttpResponse(status=200)
        except (
            AuthorizenetControllerExecutionError,
            CustomerProfile.DoesNotExist,
        ):
            return HttpResponse(status=400)


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


class AuthorizenetUpdateView(
    LoginRequiredMixin,
    HtmxTemplateResponseMixin,
    AuthorizenetSingleObjectMixin,
    UpdateView,
):
    content_type = "text/html"
    http_method_names = ["get"]

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
