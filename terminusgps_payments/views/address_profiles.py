from django.urls import reverse_lazy

from terminusgps_payments.forms import CustomerAddressProfileCreateForm
from terminusgps_payments.models import CustomerAddressProfile
from terminusgps_payments.views.generic import (
    AuthorizenetCreateView,
    AuthorizenetDeleteView,
    AuthorizenetDetailView,
    AuthorizenetListView,
)


class CustomerAddressProfileCreateView(AuthorizenetCreateView):
    content_type = "text/html"
    form_class = CustomerAddressProfileCreateForm
    http_method_names = ["get", "post"]
    model = CustomerAddressProfile
    success_url = reverse_lazy("terminusgps_payments:list address profiles")
    template_name = "terminusgps_payments/customeraddressprofile_create.html"


class CustomerAddressProfileDeleteView(AuthorizenetDeleteView):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    model = CustomerAddressProfile
    success_url = reverse_lazy("terminusgps_payments:list address profiles")
    template_name = "terminusgps_payments/customeraddressprofile_delete.html"


class CustomerAddressProfileDetailView(AuthorizenetDetailView):
    content_type = "text/html"
    http_method_names = ["get"]
    model = CustomerAddressProfile
    template_name = "terminusgps_payments/customeraddressprofile_detail.html"


class CustomerAddressProfileListView(AuthorizenetListView):
    allow_empty = True
    content_type = "text/html"
    http_method_names = ["get"]
    model = CustomerAddressProfile
    ordering = "pk"
    paginate_by = 4
    template_name = "terminusgps_payments/customeraddressprofile_list.html"
