from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import DetailView
from terminusgps.mixins import HtmxTemplateResponseMixin

from ..models import CustomerProfile


class CustomerProfileDetailView(
    UserPassesTestMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    model = CustomerProfile
    partial_template_name = (
        "terminusgps_payments/customer_profiles/partials/_detail.html"
    )
    pk_url_kwarg = "customerprofile_pk"
    template_name = "terminusgps_payments/customer_profiles/detail.html"

    def test_func(self):
        return (
            self.request.user.is_staff
            or self.get_object().user.pk == self.request.user.pk
        )
