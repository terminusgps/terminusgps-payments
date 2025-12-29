import logging
import typing

from django.core.exceptions import ValidationError
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

from ..forms import CustomerAddressProfileCreateForm
from ..models import CustomerAddressProfile, CustomerProfile

logger = logging.getLogger(__name__)


class CustomerAddressProfileCreateView(HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    form_class = CustomerAddressProfileCreateForm
    http_method_names = ["get", "post"]
    partial_template_name = (
        "terminusgps_payments/address_profiles/partials/_create.html"
    )
    template_name = "terminusgps_payments/address_profiles/create.html"

    def get_success_url(self) -> str:
        return reverse(
            "terminusgps_payments:list address profiles",
            kwargs={"customerprofile_pk": self.kwargs["customerprofile_pk"]},
        )

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customerprofile"] = CustomerProfile.objects.get(
            pk=self.kwargs["customerprofile_pk"]
        )
        return context

    def form_valid(self, form: Form) -> HttpResponse:
        try:
            cprofile = CustomerProfile.objects.get(
                pk=self.kwargs["customerprofile_pk"]
            )

            service = AuthorizenetService()
            response = service.execute(
                api.create_customer_shipping_address(
                    customer_profile_id=cprofile.pk,
                    address=form.cleaned_data["address"],
                    default=form.cleaned_data["default"],
                )
            )
            aprofile = CustomerAddressProfile()
            aprofile.cprofile = cprofile
            aprofile.id = int(response.customerAddressId)
            aprofile.save()
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


class CustomerAddressProfileListView(HtmxTemplateResponseMixin, ListView):
    content_type = "text/html"
    http_method_names = ["get"]
    model = CustomerAddressProfile
    ordering = "pk"
    partial_template_name = (
        "terminusgps_payments/address_profiles/partials/_list.html"
    )
    template_name = "terminusgps_payments/address_profiles/list.html"

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


class CustomerAddressProfileDetailView(HtmxTemplateResponseMixin, DetailView):
    content_type = "text/html"
    http_method_names = ["get"]
    model = CustomerAddressProfile
    partial_template_name = (
        "terminusgps_payments/address_profiles/partials/_detail.html"
    )
    pk_url_kwarg = "addressprofile_pk"
    template_name = "terminusgps_payments/address_profiles/detail.html"

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(
            cprofile__pk=self.kwargs["customerprofile_pk"]
        )

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        try:
            service = AuthorizenetService()
            response = service.execute(
                api.get_customer_shipping_address(
                    customer_profile_id=self.object.cprofile.pk,
                    address_profile_id=self.object.pk,
                )
            )
        except AuthorizenetControllerExecutionError as error:
            response = None
            logger.warning(error)

        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["address"] = response.address if response is not None else None
        return context


class CustomerAddressProfileDeleteView(HtmxTemplateResponseMixin, DeleteView):
    content_type = "text/html"
    http_method_names = ["post"]
    model = CustomerAddressProfile
    pk_url_kwarg = "addressprofile_pk"

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(
            cprofile__pk=self.kwargs["customerprofile_pk"]
        )

    def get_success_url(self) -> str:
        return reverse(
            "terminusgps_payments:list address profiles",
            kwargs={"customerprofile_pk": self.kwargs["customerprofile_pk"]},
        )
