from datetime import date

from django.test import TestCase

from terminusgps_payments.forms import (
    CustomerAddressProfileCreateForm,
    CustomerPaymentProfileCreateForm,
)
from terminusgps_payments.models import CustomerProfile


class CustomerAddressProfileCreateFormTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
    ]

    def setUp(self):
        self.form_cls = CustomerAddressProfileCreateForm
        self.address_data = {
            "first_name": "TestFirstName",
            "last_name": "TestLastName",
            "company": "TestCompany",
            "address": "TestAddress",
            "city": "TestCity",
            "state": "TestState",
            "country": "TestCountry",
            "zip": "TestZip",
            "phone_number": "TestPhoneNumber",
        }

    def test_clean_missing_address(self):
        """Fails if the form doesn't have the proper error message applied with missing address data."""
        data = {"customer_profile": CustomerProfile.objects.get(pk=1)}
        form = self.form_cls(data=data)
        self.assertFalse(form.is_valid())
        self.assertFormError(
            form, None, "Please fill out all required shipping address fields."
        )


class CustomerPaymentProfileCreateFormTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
    ]

    def setUp(self):
        self.form_cls = CustomerPaymentProfileCreateForm
        self.card_data = {
            "card_number": "4111111111111111",
            "card_expiry": [date(2039, 12, 1), date(2039, 12, 1)],
            "card_code": "444",
        }
        self.address_data = {
            "first_name": "TestFirstName",
            "last_name": "TestLastName",
            "company": "TestCompany",
            "address": "TestAddress",
            "city": "TestCity",
            "state": "TestState",
            "country": "TestCountry",
            "zip": "TestZip",
            "phone_number": "TestPhoneNumber",
        }
        self.bank_account_data = {
            "account_number": "41111111111111111",
            "routing_number": "411111111",
            "account_name": "TestAccountName",
            "account_type": "checking",
            "bank_name": "TestBankName",
        }

    def test_clean_missing_address(self):
        """Fails if the form doesn't have the proper error message applied with missing address data."""
        data = {"customer_profile": CustomerProfile.objects.get(pk=1)}
        form = self.form_cls(data=data)
        self.assertFalse(form.is_valid())
        self.assertFormError(
            form, None, "Please fill out all required billing address fields."
        )

    def test_clean_both_credit_card_and_bank_account(self):
        """Fails if the form doesn't have the proper error message applied with both credit card and bank account data."""
        data = (
            {"customer_profile": CustomerProfile.objects.get(pk=1)}
            | self.address_data.copy()
            | self.card_data.copy()
            | self.bank_account_data.copy()
        )
        form = self.form_cls(data=data)
        self.assertFalse(form.is_valid())
        self.assertFormError(
            form,
            None,
            "Please fill out all credit card fields or bank account fields, not both.",
        )

    def test_clean_credit_card(self):
        """Fails if the form doesn't have the proper error message applied with invalid credit card data."""
        data = (
            {"customer_profile": CustomerProfile.objects.get(pk=1)}
            | self.address_data.copy()
            | self.card_data.copy()
        )
        data["card_number"] = ""
        form = self.form_cls(data=data)
        self.assertFalse(form.is_valid())
        self.assertFormError(
            form, None, "Please fill out all credit card fields."
        )

    def test_clean_bank_account(self):
        """Fails if the form doesn't have the proper error message applied with invalid bank account data."""
        data = (
            {"customer_profile": CustomerProfile.objects.get(pk=1)}
            | self.address_data.copy()
            | self.bank_account_data.copy()
        )
        data["account_number"] = ""
        form = self.form_cls(data=data)
        self.assertFalse(form.is_valid())
        self.assertFormError(
            form, None, "Please fill out all bank account fields."
        )
