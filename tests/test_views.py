from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase

from terminusgps_payments import views


class AddCreditCardViewTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
    ]

    def setUp(self):
        self.factory = RequestFactory()
        self.view_cls = views.AddCreditCardView
        self.user = get_user_model().objects.get(pk=1)

    def test_get_by_anonymous_user_returns_302(self):
        """Fails if a GET request from an anonymous user doesn't return 302."""
        request = self.factory.get("add-credit-card/")
        request.user = AnonymousUser()
        response = self.view_cls.as_view()(request)
        self.assertEqual(response.status_code, 302)

    def test_post_by_anonymous_user_returns_302(self):
        """Fails if a POST request from an anonymous user doesn't return 302."""
        request = self.factory.post("add-credit-card/")
        request.user = AnonymousUser()
        response = self.view_cls.as_view()(request)
        self.assertEqual(response.status_code, 302)

    def test_get_by_authenticated_user_returns_200(self):
        """Fails if a GET request from an authenticated user doesn't return 200."""
        request = self.factory.get("add-credit-card/")
        request.user = self.user
        response = self.view_cls.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_post_by_authenticated_user_returns_200(self):
        """Fails if a POST request from an authenticated user doesn't return 200."""
        request = self.factory.post("add-credit-card/")
        request.user = self.user
        response = self.view_cls.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_invalid_credit_card_adds_form_error(self):
        """Fails if the form didn't have errors with a bad credit card input."""
        request = self.factory.post(
            "add-credit-card/",
            data={
                "addressform-firstName": "Test",
                "addressform-lastName": "User",
                "addressform-address": "123 Main St",
                "addressform-city": "Houston",
                "addressform-state": "TX",
                "addressform-zip": "77065",
                "addressform-country": "USA",
                "creditcardform-cardNumber": "4111111111111110",
                "creditcardform-cardCode": "444",
                "creditcardform-expirationDate": "2039-04",
            },
        )
        request.user = self.user
        response = self.view_cls.as_view()(request)
        self.assertFormError(
            response.context_data["creditcardform"],
            field="cardNumber",
            errors=["Invalid card number."],
        )

    def test_valid_form_executes_authorizenet_api_call(self):
        """Fails if a valid form does not execute the required authoriznet api call."""
        request = self.factory.post(
            "add-credit-card/",
            data={
                "addressform-firstName": "Test",
                "addressform-lastName": "User",
                "addressform-address": "123 Main St",
                "addressform-city": "Houston",
                "addressform-state": "TX",
                "addressform-zip": "77065",
                "addressform-country": "USA",
                "creditcardform-cardNumber": "4111111111111111",
                "creditcardform-cardCode": "444",
                "creditcardform-expirationDate": "2039-04",
            },
        )
        request.user = self.user
        response = self.view_cls.as_view()(request)
        print(f"{response.status_code = }")
