from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase, override_settings

from terminusgps_payments.forms import CustomerPaymentProfileCreateForm
from terminusgps_payments.models import (
    CustomerAddressProfile,
    CustomerPaymentProfile,
)
from terminusgps_payments.views import (
    CustomerAddressProfileDeleteView,
    CustomerPaymentProfileCreateView,
    CustomerPaymentProfileDeleteView,
    CustomerPaymentProfileDetailView,
    CustomerPaymentProfileListView,
)


@override_settings(ROOT_URLCONF="src.urls")
class CustomerAddressProfileCreateViewTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
    ]

    def setUp(self):
        self.client.login(
            **{"username": "testuser", "password": "super_secure_password1!"}
        )

    def tearDown(self):
        self.client.logout()

    def test_get_anonymous(self):
        """Fails if a GET request from an anonymous client returns a response code other than 302."""
        self.client.logout()
        response = self.client.get("/address-profiles/create/")
        self.assertEqual(response.status_code, 302)

    def test_get_authenticated(self):
        """Fails if a GET request from an authenticated client returns a response code other than 200."""
        response = self.client.get("/address-profiles/create/")
        self.assertEqual(response.status_code, 200)

    def test_post_anonymous(self):
        """Fails if a POST request from an anonymous client returns a response code other than 302."""
        self.client.logout()
        response = self.client.post("/address-profiles/create/")
        self.assertEqual(response.status_code, 302)

    def test_post_authenticated(self):
        """Fails if a POST request from an authenticated client returns a response code other than 200."""
        response = self.client.post("/address-profiles/create/")
        self.assertEqual(response.status_code, 200)

    def test_not_allowed_http_methods(self):
        """Fails if a non-GET or non-POST request returns a response code other than 405."""
        response = self.client.put("/address-profiles/create/")
        self.assertEqual(response.status_code, 405)
        response = self.client.patch("/address-profiles/create/")
        self.assertEqual(response.status_code, 405)
        response = self.client.delete("/address-profiles/create/")
        self.assertEqual(response.status_code, 405)
        response = self.client.head("/address-profiles/create/")
        self.assertEqual(response.status_code, 405)
        response = self.client.options("/address-profiles/create/")
        self.assertEqual(response.status_code, 405)
        response = self.client.trace("/address-profiles/create/")
        self.assertEqual(response.status_code, 405)


@override_settings(ROOT_URLCONF="src.urls")
class CustomerAddressProfileDetailViewTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
        "terminusgps_payments/tests/test_customeraddressprofile.json",
    ]

    def setUp(self):
        self.client.login(
            **{"username": "testuser", "password": "super_secure_password1!"}
        )

    def tearDown(self):
        self.client.logout()

    def test_get_anonymous(self):
        """Fails if a GET request from an anonymous client returns a response code other than 302."""
        self.client.logout()
        response = self.client.get("/address-profiles/1/detail/")
        self.assertEqual(response.status_code, 302)

    def test_get_authenticated(self):
        """Fails if a GET request from an authenticated client returns a response code other than 200."""
        response = self.client.get("/address-profiles/1/detail/")
        self.assertEqual(response.status_code, 200)

    def test_not_allowed_http_methods(self):
        """Fails if a non-GET request returns a response code other than 405."""
        response = self.client.post("/address-profiles/1/detail/")
        self.assertEqual(response.status_code, 405)
        response = self.client.put("/address-profiles/1/detail/")
        self.assertEqual(response.status_code, 405)
        response = self.client.patch("/address-profiles/1/detail/")
        self.assertEqual(response.status_code, 405)
        response = self.client.delete("/address-profiles/1/detail/")
        self.assertEqual(response.status_code, 405)
        response = self.client.head("/address-profiles/1/detail/")
        self.assertEqual(response.status_code, 405)
        response = self.client.options("/address-profiles/1/detail/")
        self.assertEqual(response.status_code, 405)
        response = self.client.trace("/address-profiles/1/detail/")
        self.assertEqual(response.status_code, 405)

    def test_get_authenticated_other_user(self):
        """Fails if a GET request from another authenticated client returns a response code other than 404."""
        self.client.login(
            **{
                "username": "testuseralt",
                "password": "super_secure_password1!",
            }
        )
        response = self.client.get("/address-profiles/1/detail/")
        self.assertEqual(response.status_code, 404)
        self.client.logout()


@override_settings(ROOT_URLCONF="src.urls")
class CustomerAddressProfileListViewTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
        "terminusgps_payments/tests/test_customeraddressprofile.json",
    ]

    def setUp(self):
        self.client.login(
            **{"username": "testuser", "password": "super_secure_password1!"}
        )

    def tearDown(self):
        self.client.logout()

    def test_get_anonymous(self):
        """Fails if a GET request from an anonymous client returns a response code other than 302."""
        self.client.logout()
        response = self.client.get("/address-profiles/list/")
        self.assertEqual(response.status_code, 302)

    def test_get_authenticated(self):
        """Fails if a GET request from an authenticated client returns a response code other than 200."""
        response = self.client.get("/address-profiles/list/")
        self.assertEqual(response.status_code, 200)

    def test_not_allowed_http_methods(self):
        """Fails if a non-GET request returns a response code other than 405."""
        response = self.client.post("/address-profiles/list/")
        self.assertEqual(response.status_code, 405)
        response = self.client.put("/address-profiles/list/")
        self.assertEqual(response.status_code, 405)
        response = self.client.patch("/address-profiles/list/")
        self.assertEqual(response.status_code, 405)
        response = self.client.delete("/address-profiles/list/")
        self.assertEqual(response.status_code, 405)
        response = self.client.head("/address-profiles/list/")
        self.assertEqual(response.status_code, 405)
        response = self.client.options("/address-profiles/list/")
        self.assertEqual(response.status_code, 405)
        response = self.client.trace("/address-profiles/list/")
        self.assertEqual(response.status_code, 405)


@override_settings(ROOT_URLCONF="src.urls")
class CustomerAddressProfileDeleteViewTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
        "terminusgps_payments/tests/test_customeraddressprofile.json",
    ]

    def setUp(self):
        self.factory = RequestFactory()
        self.view = CustomerAddressProfileDeleteView()
        self.user = get_user_model().objects.get(pk=1)

    def test_content_type(self):
        request = self.factory.get("/address-profiles/1/delete/")
        request.user = self.user
        self.view.setup(request)
        self.assertEqual("text/html", self.view.content_type)

    def test_http_method_names(self):
        request = self.factory.get("/address-profiles/1/delete/")
        request.user = self.user
        self.view.setup(request)
        self.assertIn("get", self.view.http_method_names)
        self.assertIn("post", self.view.http_method_names)

    def test_get_queryset_authenticated_user(self):
        """Fails if :py:meth:`get_queryset` doesn't return all objects associated with the user."""
        request = self.factory.get("/address-profiles/1/delete/")
        request.user = self.user
        self.view.setup(request)
        self.assertQuerySetEqual(
            self.view.get_queryset(),
            CustomerAddressProfile.objects.filter(
                customer_profile__user=self.user
            ),
            ordered=False,
        )

    def test_get_queryset_anonymous_user(self):
        """Fails if :py:meth:`get_queryset` returns anything other than an empty queryset for an anonymous user."""
        request = self.factory.get("/address-profiles/1/delete/")
        self.view.setup(request)
        self.assertQuerySetEqual(
            self.view.get_queryset(),
            CustomerAddressProfile.objects.none(),
            ordered=False,
        )


@override_settings(ROOT_URLCONF="src.urls")
class CustomerPaymentProfileCreateViewTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
    ]

    def setUp(self):
        self.factory = RequestFactory()
        self.view = CustomerPaymentProfileCreateView()
        self.user = get_user_model().objects.get(pk=1)

    def test_content_type(self):
        request = self.factory.get("payment-profiles/create/")
        request.user = self.user
        self.view.setup(request)
        self.assertEqual("text/html", self.view.content_type)

    def test_form_class(self):
        request = self.factory.get("payment-profiles/create/")
        request.user = self.user
        self.view.setup(request)
        form = self.view.get_form()
        self.assertIsInstance(form, CustomerPaymentProfileCreateForm)

    def test_http_method_names(self):
        request = self.factory.get("payment-profiles/create/")
        request.user = self.user
        self.view.setup(request)
        self.assertIn("get", self.view.http_method_names)
        self.assertIn("post", self.view.http_method_names)

    def test_get_success_url(self):
        request = self.factory.get("payment-profiles/create/")
        request.user = self.user
        self.view.setup(request)
        self.assertEqual(
            "/payment-profiles/list/", self.view.get_success_url()
        )


@override_settings(ROOT_URLCONF="src.urls")
class CustomerPaymentProfileDetailViewTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
        "terminusgps_payments/tests/test_customerpaymentprofile.json",
    ]

    def setUp(self):
        self.factory = RequestFactory()
        self.view = CustomerPaymentProfileDetailView()
        self.user = get_user_model().objects.get(pk=1)

    def test_content_type(self):
        request = self.factory.get("payment-profiles/1/detail/")
        request.user = self.user
        self.view.setup(request)
        self.assertEqual("text/html", self.view.content_type)

    def test_http_method_names(self):
        request = self.factory.get("payment-profiles/1/detail/")
        request.user = self.user
        self.view.setup(request)
        self.assertIn("get", self.view.http_method_names)

    def test_get_queryset_authenticated_user(self):
        """Fails if :py:meth:`get_queryset` doesn't return all objects associated with the user."""
        request = self.factory.get("/payment-profiles/1/detail/")
        request.user = self.user
        self.view.setup(request)
        self.assertQuerySetEqual(
            self.view.get_queryset(),
            CustomerPaymentProfile.objects.filter(
                customer_profile__user=self.user
            ),
            ordered=False,
        )

    def test_get_queryset_anonymous_user(self):
        """Fails if :py:meth:`get_queryset` returns anything other than an empty queryset for an anonymous user."""
        request = self.factory.get("/payment-profiles/1/detail/")
        self.view.setup(request)
        self.assertQuerySetEqual(
            self.view.get_queryset(),
            CustomerPaymentProfile.objects.none(),
            ordered=False,
        )


@override_settings(ROOT_URLCONF="src.urls")
class CustomerPaymentProfileListViewTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
        "terminusgps_payments/tests/test_customerpaymentprofile.json",
    ]

    def setUp(self):
        self.view = CustomerPaymentProfileListView()
        request = RequestFactory().get("/payment-profiles/list/")
        request.user = get_user_model().objects.get(pk=1)
        self.view.setup(request)

    def test_content_type(self):
        self.assertEqual("text/html", self.view.content_type)

    def test_http_method_names(self):
        self.assertIn("get", self.view.http_method_names)


@override_settings(ROOT_URLCONF="src.urls")
class CustomerPaymentProfileDeleteViewTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
        "terminusgps_payments/tests/test_customerpaymentprofile.json",
    ]

    def setUp(self):
        self.view = CustomerPaymentProfileDeleteView()
        request = RequestFactory().get("/payment-profiles/1/delete/")
        request.user = get_user_model().objects.get(pk=1)
        self.view.setup(request)

    def test_content_type(self):
        self.assertEqual("text/html", self.view.content_type)

    def test_http_method_names(self):
        self.assertIn("get", self.view.http_method_names)
        self.assertIn("post", self.view.http_method_names)

    def test_get_success_url(self):
        self.assertEqual(
            "/payment-profiles/list/", self.view.get_success_url()
        )
