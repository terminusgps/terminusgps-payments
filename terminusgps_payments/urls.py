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
        "address-profiles/<int:customerprofile_pk>/choices/",
        views.CustomerAddressProfileChoiceView.as_view(),
        name="choice address profiles",
    ),
    path(
        "address-profiles/<int:customerprofile_pk>/create/",
        views.CustomerAddressProfileCreateView.as_view(),
        name="add shipping address",
    ),
    path(
        "address-profiles/<int:customerprofile_pk>/<int:addressprofile_pk>/",
        views.CustomerAddressProfileDetailView.as_view(),
        name="detail address profiles",
    ),
    path(
        "address-profiles/<int:customerprofile_pk>/<int:addressprofile_pk>/delete/",
        views.CustomerAddressProfileDeleteView.as_view(),
        name="delete address profiles",
    ),
    path(
        "payment-profiles/<int:customerprofile_pk>/list/",
        views.CustomerPaymentProfileListView.as_view(),
        name="list payment profiles",
    ),
    path(
        "payment-profiles/<int:customerprofile_pk>/choices/",
        views.CustomerPaymentProfileChoiceView.as_view(),
        name="choice payment profiles",
    ),
    path(
        "payment-profiles/<int:customerprofile_pk>/add-credit-card/",
        views.CreditCardCreateView.as_view(),
        name="add credit card",
    ),
    path(
        "payment-profiles/<int:customerprofile_pk>/add-bank-account/",
        views.BankAccountCreateView.as_view(),
        name="add bank account",
    ),
    path(
        "payment-profiles/<int:customerprofile_pk>/<int:paymentprofile_pk>/",
        views.CustomerPaymentProfileDetailView.as_view(),
        name="detail payment profiles",
    ),
    path(
        "payment-profiles/<int:customerprofile_pk>/<int:paymentprofile_pk>/delete/",
        views.CustomerPaymentProfileDeleteView.as_view(),
        name="delete payment profiles",
    ),
    path(
        "subscriptions/<int:customerprofile_pk>/create/",
        views.SubscriptionCreateView.as_view(),
        name="create subscriptions",
    ),
    path(
        "subscriptions/<int:customerprofile_pk>/<int:subscription_pk>/",
        views.SubscriptionDetailView.as_view(),
        name="detail subscriptions",
    ),
    path(
        "subscriptions/<int:customerprofile_pk>/<int:subscription_pk>/update/",
        views.SubscriptionUpdateView.as_view(),
        name="update subscriptions",
    ),
]
