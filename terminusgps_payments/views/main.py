from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.views.generic import TemplateView
from terminusgps.mixins import HtmxTemplateResponseMixin

from terminusgps_payments.models import CustomerProfile
from terminusgps_payments.services import CustomerProfileService


class AccountView(LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    http_method_names = ["get"]
    partial_template_name = "terminusgps_payments/partials/_account.html"
    permission_denied_message = "Please login to view this content."
    template_name = "terminusgps_payments/account.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Creates a customer profile for the user if they don't have one already."""
        try:
            customer_profile = CustomerProfile.objects.get(user=request.user)
        except CustomerProfile.DoesNotExist:
            service = CustomerProfileService()
            customer_profile = CustomerProfile(user=request.user)
            customer_profile = service.create(customer_profile)
            customer_profile.save()
        return super().get(request, *args, **kwargs)
