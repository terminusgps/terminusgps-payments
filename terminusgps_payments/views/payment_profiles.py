from django.urls import reverse_lazy

from terminusgps_payments.forms import CustomerPaymentProfileCreateForm
from terminusgps_payments.models import CustomerPaymentProfile
from terminusgps_payments.views.generic import (
    AuthorizenetCreateView,
    AuthorizenetDeleteView,
    AuthorizenetDetailView,
    AuthorizenetListView,
    AuthorizenetSyncView,
)


class CustomerPaymentProfileSyncView(AuthorizenetSyncView):
    content_type = "text/html"
    http_method_names = ["get"]
    id_attr = "customerPaymentProfileId"
    list_attr = "paymentProfiles"
    model = CustomerPaymentProfile


class CustomerPaymentProfileCreateView(AuthorizenetCreateView):
    content_type = "text/html"
    form_class = CustomerPaymentProfileCreateForm
    http_method_names = ["get", "post"]
    model = CustomerPaymentProfile
    success_url = reverse_lazy("terminusgps_payments:list payment profiles")
    template_name = "terminusgps_payments/customerpaymentprofile_create.html"


class CustomerPaymentProfileDeleteView(AuthorizenetDeleteView):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    model = CustomerPaymentProfile
    success_url = reverse_lazy("terminusgps_payments:list payment profiles")
    template_name = "terminusgps_payments/customerpaymentprofile_delete.html"


class CustomerPaymentProfileDetailView(AuthorizenetDetailView):
    content_type = "text/html"
    http_method_names = ["get"]
    model = CustomerPaymentProfile
    template_name = "terminusgps_payments/customerpaymentprofile_detail.html"


class CustomerPaymentProfileListView(AuthorizenetListView):
    allow_empty = True
    content_type = "text/html"
    http_method_names = ["get"]
    model = CustomerPaymentProfile
    ordering = "pk"
    paginate_by = 4
    template_name = "terminusgps_payments/customerpaymentprofile_list.html"
