from django.urls import path

from . import views

app_name = "terminusgps_payments"
urlpatterns = [
    path(
        "address-profiles/create/",
        views.CustomerAddressProfileCreateView.as_view(),
        name="create address profiles",
    ),
    path(
        "address-profiles/list/",
        views.CustomerAddressProfileListView.as_view(),
        name="list address profiles",
    ),
    path(
        "address-profiles/<int:pk>/detail/",
        views.CustomerAddressProfileDetailView.as_view(),
        name="detail address profiles",
    ),
    path(
        "address-profiles/<int:pk>/delete/",
        views.CustomerAddressProfileDeleteView.as_view(),
        name="delete address profiles",
    ),
    path(
        "payment-profiles/create/",
        views.CustomerPaymentProfileCreateView.as_view(),
        name="create payment profiles",
    ),
    path(
        "payment-profiles/list/",
        views.CustomerPaymentProfileListView.as_view(),
        name="list payment profiles",
    ),
    path(
        "payment-profiles/<int:pk>/detail/",
        views.CustomerPaymentProfileDetailView.as_view(),
        name="detail payment profiles",
    ),
    path(
        "payment-profiles/<int:pk>/delete/",
        views.CustomerPaymentProfileDeleteView.as_view(),
        name="delete payment profiles",
    ),
]
