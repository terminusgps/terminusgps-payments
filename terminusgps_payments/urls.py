from django.urls import path, reverse_lazy

from . import forms, models, views

app_name = "terminusgps_payments"
urlpatterns = [
    path(
        "address-profiles/create/",
        views.AuthorizenetCreateView.as_view(
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
        views.AuthorizenetListView.as_view(
            model=models.CustomerAddressProfile
        ),
        name="list address profiles",
    ),
    path(
        "address-profiles/<int:pk>/detail/",
        views.AuthorizenetDetailView.as_view(
            model=models.CustomerAddressProfile,
            template_name="terminusgps_payments/customeraddressprofile_detail.html",
        ),
        name="detail address profiles",
    ),
    path(
        "address-profiles/<int:pk>/delete/",
        views.AuthorizenetDeleteView.as_view(
            model=models.CustomerAddressProfile,
            success_url=reverse_lazy(
                "terminusgps_payments:list address profiles"
            ),
        ),
        name="delete address profiles",
    ),
    path(
        "payment-profiles/create/",
        views.AuthorizenetCreateView.as_view(
            form_class=forms.CustomerPaymentProfileCreateForm,
            model=models.CustomerPaymentProfile,
            success_url=reverse_lazy(
                "terminusgps_payments:list payment profiles"
            ),
            template_name="terminusgps_payments/customerpaymentprofile_create.html",
        ),
        name="create payment profiles",
    ),
    path(
        "payment-profiles/list/",
        views.AuthorizenetListView.as_view(
            model=models.CustomerPaymentProfile
        ),
        name="list payment profiles",
    ),
    path(
        "payment-profiles/<int:pk>/detail/",
        views.AuthorizenetDetailView.as_view(
            model=models.CustomerPaymentProfile,
            template_name="terminusgps_payments/customerpaymentprofile_detail.html",
        ),
        name="detail payment profiles",
    ),
    path(
        "payment-profiles/<int:pk>/delete/",
        views.AuthorizenetDeleteView.as_view(
            model=models.CustomerPaymentProfile,
            success_url=reverse_lazy(
                "terminusgps_payments:list payment profiles"
            ),
        ),
        name="delete payment profiles",
    ),
]
