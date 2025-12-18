from django.urls import path

from . import views

app_name = "terminusgps_payments"
urlpatterns = [
    path(
        "customer-profiles/<int:customerprofile_pk>/",
        views.CustomerProfileDetailView.as_view(),
        name="detail customer profiles",
    ),
    path(
        "address-profiles/<int:customerprofile_pk>/list/",
        views.CustomerAddressProfileListView.as_view(),
        name="list address profiles",
    ),
    path(
        "address-profiles/<int:customerprofile_pk>/create/",
        views.CustomerAddressProfileCreateView.as_view(),
        name="create address profiles",
    ),
    path(
        "address-profiles/<int:customerprofile_pk>/<int:addressprofile_pk>/",
        views.CustomerAddressProfileDetailView.as_view(),
        name="detail address profiles",
    ),
    path(
        "payment-profiles/<int:customerprofile_pk>/list/",
        views.CustomerPaymentProfileListView.as_view(),
        name="list payment profiles",
    ),
    path(
        "payment-profiles/<int:customerprofile_pk>/create/bank-account/",
        views.CustomerPaymentProfileBankAccountCreateView.as_view(),
        name="create bank account payment profiles",
    ),
    path(
        "payment-profiles/<int:customerprofile_pk>/create/credit-card/",
        views.CustomerPaymentProfileCreditCardCreateView.as_view(),
        name="create credit card payment profiles",
    ),
    path(
        "payment-profiles/<int:customerprofile_pk>/<int:paymentprofile_pk>/",
        views.CustomerPaymentProfileDetailView.as_view(),
        name="detail payment profiles",
    ),
]
