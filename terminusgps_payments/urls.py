from django.urls import path

# from django.views.decorators.cache import cache_page
from . import views

# cached = lambda view_func: cache_page(timeout=60 * 15)(view_func)

app_name = "terminusgps_payments"
urlpatterns = [
    path(
        "subscriptions/list/",
        views.SubscriptionListView.as_view(),
        name="list subscription",
    ),
    path(
        "subscriptions/<int:subscription_pk>/detail/",
        views.SubscriptionDetailView.as_view(),
        name="detail subscription",
    ),
    path(
        "subscriptions/<int:subscription_pk>/update/",
        views.SubscriptionUpdateView.as_view(),
        name="update subscription",
    ),
    path(
        "subscriptions/<int:subscription_pk>/delete/",
        views.SubscriptionDeleteView.as_view(),
        name="delete subscription",
    ),
    path(
        "payments/create/",
        views.PaymentProfileCreateView.as_view(),
        name="create payment profile",
    ),
    path(
        "payments/list/",
        views.PaymentProfileListView.as_view(),
        name="list payment profile",
    ),
    path(
        "payments/<int:profile_pk>/detail/",
        views.PaymentProfileDetailView.as_view(),
        name="detail payment profile",
    ),
    path(
        "payments/<int:profile_pk>/delete/",
        views.PaymentProfileDeleteView.as_view(),
        name="delete payment profile",
    ),
    path(
        "addresses/create/",
        views.AddressProfileCreateView.as_view(),
        name="create address profile",
    ),
    path(
        "addresses/list/",
        views.AddressProfileListView.as_view(),
        name="list address profile",
    ),
    path(
        "addresses/<int:profile_pk>/detail/",
        views.AddressProfileDetailView.as_view(),
        name="detail address profile",
    ),
    path(
        "addresses/<int:profile_pk>/delete/",
        views.AddressProfileDeleteView.as_view(),
        name="delete address profile",
    ),
]
