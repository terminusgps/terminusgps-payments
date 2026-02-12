import typing

from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
    AuthorizenetService,
)

from terminusgps_payments.forms import (
    SubscriptionCreateForm,
    SubscriptionUpdateForm,
)
from terminusgps_payments.models import CustomerProfile, Subscription
from terminusgps_payments.views.generic import (
    AuthorizenetCreateView,
    AuthorizenetDeleteView,
    AuthorizenetDetailView,
    AuthorizenetUpdateView,
    HtmxTemplateView,
)


class SubscriptionCreateView(AuthorizenetCreateView):
    content_type = "text/html"
    form_class = SubscriptionCreateForm
    http_method_names = ["get", "post"]
    model = Subscription
    template_name = "terminusgps_payments/subscription_create.html"

    def get_form_kwargs(self) -> dict[str, typing.Any]:
        kwargs = super().get_form_kwargs()
        try:
            kwargs.update(
                {
                    "customer_profile": CustomerProfile.objects.get(
                        user=self.request.user
                    )
                }
            )
            return kwargs
        except CustomerProfile.DoesNotExist:
            return kwargs

    def form_valid(self, form: SubscriptionCreateForm) -> HttpResponse:
        try:
            self.object = form.save(commit=False)
            self.object.save(push=True, service=AuthorizenetService())
            return HttpResponseRedirect(self.object.get_absolute_url())
        except AuthorizenetControllerExecutionError as error:
            match error.code:
                case _:
                    form.add_error(
                        None,
                        ValidationError(
                            "%(error)s",
                            code="invalid",
                            params={"error": error},
                        ),
                    )
            return self.form_invalid(form=form)


class SubscriptionDetailView(AuthorizenetDetailView):
    content_type = "text/html"
    http_method_names = ["get"]
    model = Subscription
    template_name = "terminusgps_payments/subscription_detail.html"


class SubscriptionUpdateView(AuthorizenetUpdateView):
    content_type = "text/html"
    form_class = SubscriptionUpdateForm
    http_method_names = ["get", "post"]
    model = Subscription
    template_name = "terminusgps_payments/subscription_update.html"


class SubscriptionDeleteView(AuthorizenetDeleteView):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    model = Subscription
    template_name = "terminusgps_payments/subscription_delete.html"


class SubscriptionDeleteSuccessView(HtmxTemplateView):
    content_type = "text/html"
    http_method_names = ["get"]
    template_name = "terminusgps_payments/subscription_delete_success.html"
