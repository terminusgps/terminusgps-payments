from unittest.mock import MagicMock

from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory, TestCase, override_settings

from terminusgps_payments import views
from terminusgps_payments.models import Subscription, SubscriptionPlan


class GetPaymentProfileChoicesTestCase(TestCase):
    def test_choice_generation(self):
        """Fails if the function does not return choices with a valid element."""
        cc_payment = MagicMock(spec=["creditCard"])
        cc_payment.creditCard.cardNumber = "XXXX1111"
        cc_payment.creditCard.cardType = "TestCardType"
        profile_1 = MagicMock()
        profile_1.customerPaymentProfileId = 1
        profile_1.payment = cc_payment
        ba_payment = MagicMock(spec=["bankAccount"])
        ba_payment.bankAccount.bankName = "TestBankName"
        ba_payment.bankAccount.accountNumber = "XXXX1111"
        profile_2 = MagicMock()
        profile_2.customerPaymentProfileId = 2
        profile_2.payment = ba_payment
        choices = views.get_payment_profile_choices([profile_1, profile_2])
        self.assertIn((1, "TestCardType XXXX1111"), choices)
        self.assertIn((2, "TestBankName XXXX1111"), choices)


class GetShippingProfileChoicesTestCase(TestCase):
    def test_choice_generation(self):
        """Fails if the function does not return choices with a valid element."""
        profile_1 = MagicMock(spec=["customerAddressExType"])
        profile_1.customerAddressId = 1
        profile_1.firstName = "TestFirst"
        profile_1.lastName = "TestLast"
        profile_1.address = "123 Main St"
        profile_1.city = "Houston"
        profile_1.state = "TX"
        profile_1.zip = "77065"
        profile_1.country = "USA"
        profile_2 = MagicMock(spec=["customerAddressExType"])
        profile_2.customerAddressId = 2
        profile_2.firstName = "TestFirst"
        profile_2.lastName = "TestLast"
        profile_2.address = "456 Main St"
        profile_2.city = "Cypress"
        profile_2.state = "TX"
        profile_2.zip = "77433"
        profile_2.country = "USA"
        choices = views.get_shipping_profile_choices([profile_1, profile_2])
        self.assertIn((1, "123 Main St"), choices)
        self.assertIn((2, "456 Main St"), choices)


@override_settings(AUTHORIZENET_SERVICE="unittest.mock.Mock")
class AddCreditCardViewTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
    ]

    def setUp(self):
        self.path = "/customer-profile/add-credit-card/"
        self.client = Client()
        self.client.login(
            username="testuser", password="super_secure_password1!"
        )

    def test_get_by_anonymous_user_returns_302(self):
        """Fails if a GET request from an anonymous user returns anything other than 302."""
        self.client.logout()
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 302)
        self.assertIn(f"?next={self.path}", response.url)

    def test_valid_forms_return_302(self):
        """Fails if a POST request with valid form data returns anything other than 302."""
        response = self.client.post(
            self.path,
            data={
                "addressform-firstName": "TestFirst",
                "addressform-lastName": "TestLast",
                "addressform-company": "TestCompany",
                "addressform-address": "TestAddress",
                "addressform-city": "TestCity",
                "addressform-state": "TestState",
                "addressform-zip": "TestZip",
                "addressform-country": "TestCountry",
                "addressform-phoneNumber": "TestPhone",
                "creditcardform-cardNumber": "4111111111111111",
                "creditcardform-cardCode": "444",
                "creditcardform-expirationDate": "2039-04",
            },
        )
        self.assertEqual(response.status_code, 302)

    def test_invalid_credit_card_returns_error(self):
        """Fails if a POST request from an authenticated user doesn't return an error with an invalid credit card number."""
        response = self.client.post(
            self.path,
            data={
                "addressform-firstName": "TestFirst",
                "addressform-lastName": "TestLast",
                "addressform-company": "TestCompany",
                "addressform-address": "TestAddress",
                "addressform-city": "TestCity",
                "addressform-state": "TestState",
                "addressform-zip": "TestZip",
                "addressform-country": "TestCountry",
                "addressform-phoneNumber": "TestPhone",
                "creditcardform-cardNumber": "4111111111111110",
                "creditcardform-cardCode": "444",
                "creditcardform-expirationDate": "2039-04",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context_data["creditcardform"],
            "cardNumber",
            "Invalid card number.",
        )

    def test_invalid_expiration_date_returns_error(self):
        """Fails if a POST request from an authenticated user doesn't return an error with an invalid expiration date."""
        response = self.client.post(
            self.path,
            data={
                "addressform-firstName": "TestFirst",
                "addressform-lastName": "TestLast",
                "addressform-company": "TestCompany",
                "addressform-address": "TestAddress",
                "addressform-city": "TestCity",
                "addressform-state": "TestState",
                "addressform-zip": "TestZip",
                "addressform-country": "TestCountry",
                "addressform-phoneNumber": "TestPhone",
                "creditcardform-cardNumber": "4111111111111111",
                "creditcardform-cardCode": "444",
                "creditcardform-expirationDate": "2019-04",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context_data["creditcardform"],
            "expirationDate",
            "Expiration date cannot be in the past.",
        )


@override_settings(AUTHORIZENET_SERVICE="unittest.mock.Mock")
class AddBankAccountViewTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
    ]

    def setUp(self):
        self.path = "/customer-profile/add-bank-account/"
        self.client = Client()
        self.client.login(
            username="testuser", password="super_secure_password1!"
        )

    def test_requests_from_anonymous_user_returns_302(self):
        """Fails if a request from an anonymous user returns anything other than 302."""
        self.client.logout()
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 302)
        self.assertIn(f"?next={self.path}", response.url)
        response = self.client.post(self.path)
        self.assertEqual(response.status_code, 302)
        self.assertIn(f"?next={self.path}", response.url)

    def test_valid_forms_return_302(self):
        """Fails if a POST request with valid form data returns anything other than 302."""
        response = self.client.post(
            self.path,
            data={
                "addressform-firstName": "TestFirst",
                "addressform-lastName": "TestLast",
                "addressform-company": "TestCompany",
                "addressform-address": "TestAddress",
                "addressform-city": "TestCity",
                "addressform-state": "TestState",
                "addressform-zip": "TestZip",
                "addressform-country": "TestCountry",
                "addressform-phoneNumber": "TestPhone",
                "bankaccountform-accountNumber": "41111111111111111",
                "bankaccountform-routingNumber": "41111111",
                "bankaccountform-nameOnAccount": "TestAccountName",
                "bankaccountform-accountType": "checking",
                "bankaccountform-bankName": "TestBank",
            },
        )
        self.assertEqual(response.status_code, 302)


@override_settings(AUTHORIZENET_SERVICE="unittest.mock.Mock")
class CustomerProfileDetailViewTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
    ]

    def setUp(self):
        self.path = "/customer-profile/details/"
        self.client = Client()
        self.client.login(
            username="testuser", password="super_secure_password1!"
        )

    def test_requests_from_anonymous_user_returns_302(self):
        """Fails if a request from an anonymous user returns anything other than 302."""
        self.client.logout()
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 302)
        self.assertIn(f"?next={self.path}", response.url)

    def test_get_include_issuer_info(self):
        """Fails if :py:meth:`get_include_issuer_info` doesn't return expected values."""
        factory = RequestFactory()
        request = factory.get(
            self.path, query_params={"include_issuer_info": "on"}
        )
        request.user = get_user_model().objects.get(pk=1)
        view = views.CustomerProfileDetailView()
        view.setup(request)
        self.assertTrue(view.get_include_issuer_info())

        factory = RequestFactory()
        request = factory.get(
            self.path, query_params={"include_issuer_info": "off"}
        )
        request.user = get_user_model().objects.get(pk=1)
        view = views.CustomerProfileDetailView()
        view.setup(request)
        self.assertFalse(view.get_include_issuer_info())

    def test_get_unmask_expiration_date(self):
        """Fails if :py:meth:`unmask_expiration_date` doesn't return expected values."""
        factory = RequestFactory()
        request = factory.get(
            self.path, query_params={"unmask_expiration_date": "on"}
        )
        request.user = get_user_model().objects.get(pk=1)
        view = views.CustomerProfileDetailView()
        view.setup(request)
        self.assertTrue(view.get_unmask_expiration_date())

        factory = RequestFactory()
        request = factory.get(
            self.path, query_params={"unmask_expiration_date": "off"}
        )
        request.user = get_user_model().objects.get(pk=1)
        view = views.CustomerProfileDetailView()
        view.setup(request)
        self.assertFalse(view.get_unmask_expiration_date())

    def test_get_authorizenet_response(self):
        """Fails if the Authorizenet API call wasn't executed or was executed with incorrect arguments."""
        factory = RequestFactory()
        request = factory.get(self.path)
        request.user = get_user_model().objects.get(pk=1)
        view = views.CustomerProfileDetailView()
        view.setup(request)
        view.get_authorizenet_response()
        api_call = view.service.method_calls[0]
        self.assertTrue(api_call.assert_called_once)


@override_settings(AUTHORIZENET_SERVICE="unittest.mock.Mock")
class SubscriptionCancelViewTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
        "terminusgps_payments/tests/test_subscription.json",
    ]

    def setUp(self):
        self.path = "/subscriptions/1/cancel/"
        self.client = Client()
        self.client.login(
            username="testuser", password="super_secure_password1!"
        )

    def test_requests_from_anonymous_user_returns_302(self):
        """Fails if a request from an anonymous user returns anything other than 302."""
        self.client.logout()
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 302)
        self.assertIn(f"?next={self.path}", response.url)

    def test_get_request_from_other_user_returns_404(self):
        """Fails if a request from another user returns anything other than 404."""
        self.client.logout()
        self.client.login(
            **{
                "username": "testuseralt",
                "password": "super_secure_password1!",
            }
        )
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 404)

    def test_valid_form(self):
        """Fails if the subscription wasn't successfully canceled."""
        response = self.client.post(self.path)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Subscription.objects.get(pk=1).status, "canceled")
        self.assertIsNone(Subscription.objects.get(pk=1).expires_on)

    def test_get_queryset(self):
        """Fails if the queryset contains subscriptions associated with a different user."""
        factory = RequestFactory()
        request = factory.get(self.path)
        request.user = get_user_model().objects.get(pk=1)
        view = views.SubscriptionCancelView()
        view.setup(request, pk=1)
        qs = view.get_queryset()
        self.assertQuerySetEqual(
            qs, Subscription.objects.filter(customer_profile__pk=1)
        )


@override_settings(AUTHORIZENET_SERVICE="unittest.mock.Mock")
class SubscriptionUpdateViewTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
        "terminusgps_payments/tests/test_subscription.json",
    ]

    def setUp(self):
        self.path = "/subscriptions/1/update/"
        self.client = Client()
        self.client.login(
            username="testuser", password="super_secure_password1!"
        )

    def test_request_from_anonymous_user_returns_302(self):
        """Fails if a request from an anonymous user returns anything other than 302."""
        self.client.logout()
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 302)
        self.assertIn(f"?next={self.path}", response.url)

    def test_get_request_from_other_user_returns_404(self):
        """Fails if a request from another user returns anything other than 404."""
        self.client.logout()
        self.client.login(
            **{
                "username": "testuseralt",
                "password": "super_secure_password1!",
            }
        )
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 404)

    def test_get_form_kwargs(self):
        """Fails if 'instance' was in the form kwargs."""
        factory = RequestFactory()
        request = factory.get(self.path)
        request.user = get_user_model().objects.get(pk=1)
        view = views.SubscriptionUpdateView(pk=1)
        view.setup(request)
        kwargs = view.get_form_kwargs()
        self.assertNotIn("instance", kwargs)

    def test_get_queryset(self):
        """Fails if the queryset contains subscriptions associated with a different user."""
        factory = RequestFactory()
        request = factory.get(self.path)
        request.user = get_user_model().objects.get(pk=1)
        view = views.SubscriptionUpdateView(pk=1)
        view.setup(request)
        qs = view.get_queryset()
        self.assertQuerySetEqual(
            qs, Subscription.objects.filter(customer_profile__pk=1)
        )


@override_settings(AUTHORIZENET_SERVICE="unittest.mock.Mock")
class SubscriptionDetailViewTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
        "terminusgps_payments/tests/test_subscription.json",
    ]

    def setUp(self):
        self.path = "/subscriptions/1/details/"
        self.client = Client()
        self.client.login(
            username="testuser", password="super_secure_password1!"
        )

    def test_get_include_transactions(self):
        """Fails if :py:meth:`include_transactions` doesn't return expected values."""
        factory = RequestFactory()
        request = factory.get(
            self.path, query_params={"include_transactions": "on"}
        )
        request.user = get_user_model().objects.get(pk=1)
        view = views.SubscriptionDetailView()
        view.setup(request, pk=1)
        self.assertTrue(view.get_include_transactions())

        request = factory.get(
            self.path, query_params={"include_transactions": "off"}
        )
        request.user = get_user_model().objects.get(pk=1)
        view = views.SubscriptionDetailView()
        view.setup(request, pk=1)
        self.assertFalse(view.get_include_transactions())

    def test_get_authorizenet_response(self):
        """Fails if the Authorizenet API call wasn't executed or was executed with incorrect arguments."""
        factory = RequestFactory()
        request = factory.get(self.path)
        request.user = get_user_model().objects.get(pk=1)
        view = views.SubscriptionDetailView()
        view.setup(request, pk=1)
        view.object = view.get_object()
        view.get_authorizenet_response()
        api_call = view.service.method_calls[0]
        self.assertTrue(api_call.assert_called_once)
        api_request = api_call.args[0][0]
        self.assertEqual(api_request.subscriptionId, str(view.object.pk))
        self.assertEqual(
            bool(int(api_request.includeTransactions)),
            view.get_include_transactions(),
        )

    def test_get_queryset(self):
        """Fails if the queryset contains subscriptions associated with a different user."""
        factory = RequestFactory()
        request = factory.get(self.path)
        request.user = get_user_model().objects.get(pk=1)
        view = views.SubscriptionDetailView()
        view.setup(request, pk=1)
        qs = view.get_queryset()
        self.assertQuerySetEqual(
            qs, Subscription.objects.filter(customer_profile__pk=1)
        )

    def test_get_context_data(self):
        """Fails if :py:attr:`response` wasn't present in the view context."""
        factory = RequestFactory()
        request = factory.get(self.path)
        request.user = get_user_model().objects.get(pk=1)
        view = views.SubscriptionDetailView()
        view.setup(request, pk=1)
        view.object = view.get_object()
        context = view.get_context_data()
        self.assertIn("response", context.keys())


@override_settings(AUTHORIZENET_SERVICE="unittest.mock.Mock")
class SubscriptionCreateViewTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
        "terminusgps_payments/tests/test_subscription.json",
    ]

    def setUp(self):
        self.path = "/subscriptions/create/"
        self.client = Client()
        self.client.login(
            username="testuser", password="super_secure_password1!"
        )

    def test_get_authorizenet_response(self):
        """Fails if the Authorizenet API call wasn't executed or was executed with incorrect arguments."""
        factory = RequestFactory()
        request = factory.get(self.path)
        request.user = get_user_model().objects.get(pk=1)
        view = views.SubscriptionCreateView()
        view.setup(request)
        view.get_authorizenet_response()
        api_call = view.service.method_calls[0]
        self.assertTrue(api_call.assert_called_once)

    def test_get_form(self):
        """Fails if :py:meth:`get_form` returns a form with invalid..."""
        mock_api_response = MagicMock(spec=["profile"])
        mock_api_response.profile.paymentProfiles = []
        mock_api_response.profile.shipToList = []

        factory = RequestFactory()
        request = factory.get(self.path)
        request.user = get_user_model().objects.get(pk=1)
        view = views.SubscriptionCreateView()
        view.setup(request)
        view.service.execute.return_value = mock_api_response
        form = view.get_form()
        expected_qs = SubscriptionPlan.objects.filter(visibility__exact="vis")
        self.assertQuerySetEqual(
            form.fields["plan"].queryset.order_by("pk"),
            expected_qs.order_by("pk"),
        )
        self.assertFalse(form.fields["payment_profile"].choices)
        self.assertFalse(form.fields["shipping_profile"].choices)
