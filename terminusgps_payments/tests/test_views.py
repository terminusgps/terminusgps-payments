from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from terminusgps_payments.forms import CustomerAddressProfileCreateForm
from terminusgps_payments.models import (
    CustomerAddressProfile,
    CustomerPaymentProfile,
    CustomerProfile,
)
from terminusgps_payments.views import (
    AuthorizenetCreateView,
    AuthorizenetListView,
    SubscriptionCreateView,
    SubscriptionUpdateView,
)


class AuthorizenetCreateViewTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
    ]

    def setUp(self):
        self.view = AuthorizenetCreateView(
            model=CustomerAddressProfile,
            form_class=CustomerAddressProfileCreateForm,
        )
        self.user = get_user_model().objects.get(pk=1)

    def test_get_initial_with_customerprofile(self):
        request = RequestFactory().get("address-profiles/create/")
        request.user = self.user
        self.view.setup(request)
        initial = self.view.get_initial()
        self.assertIn("customer_profile", initial)
        self.assertEqual(
            CustomerProfile.objects.get(pk=1), initial["customer_profile"]
        )

    def test_get_initial_anonymous_user(self):
        request = RequestFactory().get("address-profiles/create/")
        self.view.setup(request)
        initial = self.view.get_initial()
        self.assertNotIn("customer_profile", initial)


class SubscriptionCreateViewTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
        "terminusgps_payments/tests/test_customeraddressprofile.json",
        "terminusgps_payments/tests/test_customerpaymentprofile.json",
    ]

    def setUp(self):
        self.view = SubscriptionCreateView()
        self.user = get_user_model().objects.get(pk=1)

    def test_get_initial(self):
        request = RequestFactory().get("subscriptions/create/")
        request.user = self.user
        self.view.setup(request)
        initial = self.view.get_initial()
        self.assertIn("start_date", initial)
        self.assertAlmostEqual(
            date.today(), initial["start_date"], delta=timedelta(hours=23)
        )

    def test_get_form_authenticated_user(self):
        request = RequestFactory().get("subscriptions/create/")
        request.user = self.user
        self.view.setup(request)
        form = self.view.get_form()
        self.assertQuerySetEqual(
            form.fields["payment_profile"].queryset,
            CustomerPaymentProfile.objects.filter(
                customer_profile__user=self.user
            ),
            ordered=False,
        )
        self.assertQuerySetEqual(
            form.fields["address_profile"].queryset,
            CustomerAddressProfile.objects.filter(
                customer_profile__user=self.user
            ),
            ordered=False,
        )

    def test_get_form_anonymous_user(self):
        request = RequestFactory().get("subscriptions/create/")
        self.view.setup(request)
        form = self.view.get_form()
        self.assertQuerySetEqual(
            form.fields["payment_profile"].queryset,
            CustomerPaymentProfile.objects.none(),
        )
        self.assertQuerySetEqual(
            form.fields["address_profile"].queryset,
            CustomerAddressProfile.objects.none(),
        )


class AuthorizenetListViewTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
        "terminusgps_payments/tests/test_customerpaymentprofile.json",
    ]

    def setUp(self):
        self.view_cls = AuthorizenetListView
        self.user = get_user_model().objects.get(pk=1)

    def test_get_queryset_anonymous_user(self):
        """Fails if :py:class:`AuthorizenetListView` returns data to an anonymous user."""
        request = RequestFactory().get("payment-profiles/list/")
        view = self.view_cls(
            model=CustomerPaymentProfile, template_name="test.html"
        )
        view.setup(request)
        self.assertQuerySetEqual(
            view.get_queryset(), CustomerPaymentProfile.objects.none()
        )

    def test_get_queryset_multiple_items(self):
        """Fails if :py:class:`AuthorizenetListView` fails to return all (2) objects for the authenticated user."""
        request = RequestFactory().get("payment-profiles/list/")
        request.user = self.user
        view = self.view_cls(
            model=CustomerPaymentProfile, template_name="test.html"
        )
        view.setup(request)
        qs = view.get_queryset()
        self.assertQuerySetEqual(
            qs,
            CustomerPaymentProfile.objects.filter(
                customer_profile__user=self.user
            ),
            ordered=False,
        )
        self.assertEqual(2, len(qs))

    def test_get_queryset_empty(self):
        """Fails if :py:class:`AuthorizenetListView` doesn't return an empty queryset."""
        request = RequestFactory().get("address-profiles/list/")
        request.user = self.user
        view = self.view_cls(
            model=CustomerAddressProfile, template_name="test.html"
        )
        view.setup(request)
        self.assertQuerySetEqual(
            view.get_queryset(),
            CustomerAddressProfile.objects.filter(
                customer_profile__user=self.user
            ),
        )


class SubscriptionUpdateViewTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
        "terminusgps_payments/tests/test_customeraddressprofile.json",
        "terminusgps_payments/tests/test_customerpaymentprofile.json",
        "terminusgps_payments/tests/test_subscription.json",
    ]

    def setUp(self):
        self.view = SubscriptionUpdateView()
        self.user = get_user_model().objects.get(pk=1)

    def test_get_form_authenticated_user(self):
        request = RequestFactory().get("subscriptions/1/update/")
        request.user = self.user
        self.view.setup(request)
        form = self.view.get_form()
        self.assertQuerySetEqual(
            form.fields["payment_profile"].queryset,
            CustomerPaymentProfile.objects.filter(
                customer_profile__user=self.user
            ),
            ordered=False,
        )
        self.assertQuerySetEqual(
            form.fields["address_profile"].queryset,
            CustomerAddressProfile.objects.filter(
                customer_profile__user=self.user
            ),
            ordered=False,
        )

    def test_get_form_anonymous_user(self):
        request = RequestFactory().get("subscriptions/1/update/")
        self.view.setup(request)
        form = self.view.get_form()
        self.assertQuerySetEqual(
            form.fields["payment_profile"].queryset,
            CustomerPaymentProfile.objects.none(),
        )
        self.assertQuerySetEqual(
            form.fields["address_profile"].queryset,
            CustomerAddressProfile.objects.none(),
        )
