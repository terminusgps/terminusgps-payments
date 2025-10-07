from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.views.generic import DetailView
from terminusgps.mixins import HtmxTemplateResponseMixin

from terminusgps_payments import models


class CustomerProfileDetailView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    http_method_names = ["get"]
    model = models.CustomerProfile
    partial_template_name = (
        "terminusgps_payments/customer_profiles/partials/_detail.html"
    )
    pk_url_kwarg = "profile_pk"
    template_name = "terminusgps_payments/customer_profiles/detail.html"

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter(user=self.request.user)
