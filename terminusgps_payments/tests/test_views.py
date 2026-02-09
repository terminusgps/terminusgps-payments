from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase, override_settings

from terminusgps_payments.forms import (
    CustomerAddressProfileCreateForm,
    CustomerPaymentProfileCreateForm,
)
from terminusgps_payments.models import (
    CustomerAddressProfile,
    CustomerPaymentProfile,
)
from terminusgps_payments.views import (
    CustomerAddressProfileCreateView,
    CustomerAddressProfileDeleteView,
    CustomerAddressProfileDetailView,
    CustomerAddressProfileListView,
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
        self.factory = RequestFactory()
        self.view = CustomerAddressProfileCreateView()
        self.user = get_user_model().objects.get(pk=1)

    def test_content_type(self):
        """Fails if the view's content type was anything other than 'text/html'."""
        request = self.factory.get("/address-profiles/create/")
        request.user = self.user
        self.view.setup(request)
        self.assertEqual("text/html", self.view.content_type)

    def test_form_class(self):
        """Fails if the view's form class wasn't :py:obj:`~terminusgps_payments.forms.CustomerAddressProfileCreateForm`."""
        request = self.factory.get("/address-profiles/create/")
        request.user = self.user
        self.view.setup(request)
        form = self.view.get_form()
        self.assertIsInstance(form, CustomerAddressProfileCreateForm)

    def test_http_method_names(self):
        """Fails if 'get' and 'post' weren't present in :py:attr:`http_method_names`."""
        request = self.factory.get("/address-profiles/create/")
        request.user = self.user
        self.view.setup(request)
        self.assertIn("get", self.view.http_method_names)
        self.assertIn("post", self.view.http_method_names)

    def test_get_success_url(self):
        """Fails if :py:meth:`get_success_url` returns a URL other than '/address-profiles/list/'."""
        request = self.factory.get("/address-profiles/create/")
        request.user = self.user
        self.view.setup(request)
        self.assertEqual(
            "/address-profiles/list/", self.view.get_success_url()
        )


@override_settings(ROOT_URLCONF="src.urls")
class CustomerAddressProfileDetailViewTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
        "terminusgps_payments/tests/test_customeraddressprofile.json",
    ]

    def setUp(self):
        self.factory = RequestFactory()
        self.view = CustomerAddressProfileDetailView()
        self.user = get_user_model().objects.get(pk=1)

    def test_content_type(self):
        request = self.factory.get("/address-profiles/1/detail/")
        request.user = self.user
        self.view.setup(request)
        self.assertEqual("text/html", self.view.content_type)

    def test_http_method_names(self):
        request = self.factory.get("/address-profiles/1/detail/")
        request.user = self.user
        self.view.setup(request)
        self.assertIn("get", self.view.http_method_names)

    def test_get_queryset_authenticated_user(self):
        """Fails if :py:meth:`get_queryset` doesn't return all objects associated with the user."""
        request = self.factory.get("/address-profiles/1/detail/")
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
        request = self.factory.get("/address-profiles/1/detail/")
        self.view.setup(request)
        self.assertQuerySetEqual(
            self.view.get_queryset(),
            CustomerAddressProfile.objects.none(),
            ordered=False,
        )


@override_settings(ROOT_URLCONF="src.urls")
class CustomerAddressProfileListViewTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
        "terminusgps_payments/tests/test_customeraddressprofile.json",
    ]

    def setUp(self):
        self.factory = RequestFactory()
        self.view = CustomerAddressProfileListView()
        self.user = get_user_model().objects.get(pk=1)

    def test_content_type(self):
        request = self.factory.get("/address-profiles/list/")
        request.user = self.user
        self.view.setup(request)
        self.assertEqual("text/html", self.view.content_type)

    def test_http_method_names(self):
        request = self.factory.get("/address-profiles/list/")
        request.user = self.user
        self.view.setup(request)
        self.assertIn("get", self.view.http_method_names)

    def test_get_queryset_authenticated_user(self):
        """Fails if :py:meth:`get_queryset` doesn't return all objects associated with the user."""
        request = self.factory.get("/address-profiles/list/")
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
        request = self.factory.get("/address-profiles/list/")
        self.view.setup(request)
        self.assertQuerySetEqual(
            self.view.get_queryset(),
            CustomerAddressProfile.objects.none(),
            ordered=False,
        )


@override_settings(ROOT_URLCONF="src.urls")
class CustomerAddressProfileDeleteViewTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
        "terminusgps_payments/tests/test_customeraddressprofile.json",
    ]

    def setUp(self):
        self.view = CustomerAddressProfileDeleteView()
        request = RequestFactory().get("/address-profiles/1/delete/")
        request.user = get_user_model().objects.get(pk=1)
        self.view.setup(request)

    def test_content_type(self):
        self.assertEqual("text/html", self.view.content_type)

    def test_http_method_names(self):
        self.assertIn("get", self.view.http_method_names)
        self.assertIn("post", self.view.http_method_names)

    def test_get_success_url(self):
        self.assertEqual(
            "/address-profiles/list/", self.view.get_success_url()
        )


@override_settings(ROOT_URLCONF="src.urls")
class CustomerPaymentProfileCreateViewTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
    ]

    def setUp(self):
        self.view = CustomerPaymentProfileCreateView()
        request = RequestFactory().get("/payment-profiles/create/")
        request.user = get_user_model().objects.get(pk=1)
        self.view.setup(request)

    def test_content_type(self):
        self.assertEqual("text/html", self.view.content_type)

    def test_form_class(self):
        form = self.view.get_form()
        self.assertIsInstance(form, CustomerPaymentProfileCreateForm)

    def test_http_method_names(self):
        self.assertIn("get", self.view.http_method_names)
        self.assertIn("post", self.view.http_method_names)

    def test_get_success_url(self):
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
        self.view = CustomerPaymentProfileDetailView()
        request = RequestFactory().get("/payment-profiles/1/detail/")
        request.user = get_user_model().objects.get(pk=1)
        self.view.setup(request)

    def test_content_type(self):
        self.assertEqual("text/html", self.view.content_type)

    def test_http_method_names(self):
        self.assertIn("get", self.view.http_method_names)

    def test_get_queryset(self):
        self.assertQuerySetEqual(
            self.view.get_queryset(),
            CustomerPaymentProfile.objects.filter(
                customer_profile__user=self.view.request.user
            ),
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
