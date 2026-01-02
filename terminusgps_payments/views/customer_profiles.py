from django.views.generic import DetailView
from terminusgps.mixins import HtmxTemplateResponseMixin

from ..models import CustomerProfile
from .mixins import CustomerProfileExclusiveMixin


class CustomerProfileDetailView(
    CustomerProfileExclusiveMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    model = CustomerProfile
    partial_template_name = (
        "terminusgps_payments/customer_profiles/partials/_detail.html"
    )
    pk_url_kwarg = "customerprofile_pk"
    template_name = "terminusgps_payments/customer_profiles/detail.html"
