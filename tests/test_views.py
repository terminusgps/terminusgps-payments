from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory, TestCase, override_settings

from terminusgps_payments.models import Subscription


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
        request = factory.get(self.path, query={"include_issuer_info": "on"})
        request.user = get_user_model().objects.get(pk=1)


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

    def test_valid_form(self):
        """Fails if the subscription wasn't successfully canceled."""
        response = self.client.post(self.path)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Subscription.objects.get(pk=1).status, "canceled")


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
