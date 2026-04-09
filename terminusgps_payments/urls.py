from django.urls import path

from . import views

app_name = "terminusgps_payments"
urlpatterns = [
    path(
        "customer-profile/details/",
        views.CustomerProfileDetailView.as_view(),
        name="customer profile details",
    ),
    path(
        "customer-profile/add-credit-card/",
        views.AddCreditCardView.as_view(),
        name="add credit card",
    ),
    path(
        "customer-profile/add-bank-account/",
        views.AddBankAccountView.as_view(),
        name="add bank account",
    ),
    path(
        "subscriptions/create/",
        views.SubscriptionCreateView.as_view(),
        name="create subscription",
    ),
    path(
        "subscriptions/<int:pk>/details/",
        views.SubscriptionDetailView.as_view(),
        name="subscription details",
    ),
    path(
        "subscriptions/<int:pk>/update/",
        views.SubscriptionUpdateView.as_view(),
        name="update subscription",
    ),
    path(
        "subscriptions/<int:pk>/delete/",
        views.SubscriptionDeleteView.as_view(),
        name="delete subscription",
    ),
    path(
        "subscription-plans/details/",
        views.SubscriptionPlanDetailView.as_view(),
        name="subscription plan details",
    ),
]
