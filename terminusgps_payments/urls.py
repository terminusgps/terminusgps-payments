from django.urls import path, reverse_lazy
from django.utils.translation import gettext_lazy as _

from . import forms, models
from .views.generic import (
    AuthorizenetCreateView,
    AuthorizenetDeleteView,
    AuthorizenetDetailView,
    AuthorizenetListView,
    AuthorizenetSyncView,
    HtmxTemplateView,
)

app_name = "terminusgps_payments"
urlpatterns = [
    path(
        "address-profiles/create/",
        AuthorizenetCreateView.as_view(
            form_class=forms.CustomerAddressProfileCreateForm,
            model=models.CustomerAddressProfile,
            success_url=reverse_lazy(
                "terminusgps_payments:list address profiles"
            ),
            template_name="terminusgps_payments/customeraddressprofile_create.html",
        ),
        name="create address profiles",
    ),
    path(
        "address-profiles/list/",
        AuthorizenetListView.as_view(
            allow_empty=True,
            model=models.CustomerAddressProfile,
            ordering="pk",
            paginate_by=4,
            template_name="terminusgps_payments/customeraddressprofile_list.html",
        ),
        name="list address profiles",
    ),
    path(
        "address-profiles/sync/",
        AuthorizenetSyncView.as_view(
            id_attr="customerAddressId",
            list_attr="shipToList",
            model=models.CustomerAddressProfile,
        ),
        name="sync address profiles",
    ),
    path(
        "address-profiles/<int:pk>/detail/",
        AuthorizenetDetailView.as_view(
            model=models.CustomerAddressProfile,
            template_name="terminusgps_payments/customeraddressprofile_detail.html",
        ),
        name="detail address profiles",
    ),
    path(
        "address-profiles/<int:pk>/delete/",
        AuthorizenetDeleteView.as_view(
            model=models.CustomerAddressProfile,
            template_name="terminusgps_payments/customeraddressprofile_delete.html",
            success_url=reverse_lazy(
                "terminusgps_payments:delete address profiles success"
            ),
        ),
        name="delete address profiles",
    ),
    path(
        "address-profiles/delete/success/",
        HtmxTemplateView.as_view(
            template_name="terminusgps_payments/customeraddressprofile_delete_success.html"
        ),
        name="delete address profiles success",
    ),
    path(
        "payment-profiles/create/",
        AuthorizenetCreateView.as_view(
            model=models.CustomerPaymentProfile,
            form_class=forms.CustomerPaymentProfileCreateForm,
            success_url=reverse_lazy(
                "terminusgps_payments:list payment profiles"
            ),
            template_name="terminusgps_payments/customerpaymentprofile_create.html",
        ),
        name="create payment profiles",
    ),
    path(
        "payment-profiles/list/",
        AuthorizenetListView.as_view(
            allow_empty=True,
            model=models.CustomerPaymentProfile,
            ordering="pk",
            paginate_by=4,
            template_name="terminusgps_payments/customerpaymentprofile_list.html",
        ),
        name="list payment profiles",
    ),
    path(
        "payment-profiles/sync/",
        AuthorizenetSyncView.as_view(
            id_attr="customerPaymentProfileId",
            list_attr="paymentProfiles",
            model=models.CustomerPaymentProfile,
        ),
        name="sync payment profiles",
    ),
    path(
        "payment-profiles/<int:pk>/detail/",
        AuthorizenetDetailView.as_view(
            model=models.CustomerPaymentProfile,
            template_name="terminusgps_payments/customerpaymentprofile_detail.html",
        ),
        name="detail payment profiles",
    ),
    path(
        "payment-profiles/<int:pk>/delete/",
        AuthorizenetDeleteView.as_view(
            model=models.CustomerPaymentProfile,
            template_name="terminusgps_payments/customerpaymentprofile_delete.html",
            success_url=reverse_lazy(
                "terminusgps_payments:delete payment profiles success"
            ),
        ),
        name="delete payment profiles",
    ),
    path(
        "payment-profiles/delete/success/",
        HtmxTemplateView.as_view(
            template_name="terminusgps_payments/customerpaymentprofile_delete_success.html"
        ),
        name="delete payment profiles success",
    ),
    path(
        "subscriptions/<int:pk>/detail/",
        AuthorizenetDetailView.as_view(
            model=models.Subscription,
            template_name="terminusgps_payments/subscription_detail.html",
        ),
        name="detail subscriptions",
    ),
    path(
        "subscriptions/<int:pk>/delete/",
        AuthorizenetDeleteView.as_view(
            model=models.Subscription,
            template_name="terminusgps_payments/subscription_delete.html",
            success_url=reverse_lazy(
                "terminusgps_payments:delete subscriptions success"
            ),
        ),
        name="delete subscriptions",
    ),
    path(
        "subscriptions/delete/success/",
        HtmxTemplateView.as_view(
            template_name="terminusgps_payments/subscription_delete_success.html",
            extra_context={
                "message": _("Your subscription was successfully canceled.")
            },
        ),
        name="delete subscriptions success",
    ),
]
