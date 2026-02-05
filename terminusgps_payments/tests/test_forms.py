from datetime import date

from django.test import TestCase

from terminusgps_payments.forms import CustomerPaymentProfileCreateForm


class CustomerPaymentProfileCreateFormTestCase(TestCase):
    def setUp(self):
        self.form_cls = CustomerPaymentProfileCreateForm

    def test_clean(self):
        """Fails if :py:meth:`clean` doesn't add expected errors to the form."""
        self.skipTest("TODO")
        data = {
            "first_name": "TestFirstName",
            "last_name": "TestLastName",
            "company": "TestCompany",
            "address": "TestAddress",
            "city": "TestCity",
            "state": "TestState",
            "country": "TestCountry",
            "zip": "TestZip",
            "phone_number": "TestPhoneNumber",
            "card_number": "4111111111111111",
            "card_expiry": [date(2039, 12, 1), date(2039, 12, 1)],
            "card_code": "444",
        }
        form = self.form_cls(data)
