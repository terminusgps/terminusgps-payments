from django.urls import path

from . import views

app_name = "terminusgps_payments"
urlpatterns = [
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
