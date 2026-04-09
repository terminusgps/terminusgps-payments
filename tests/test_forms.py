from string import ascii_lowercase

from django.test import TestCase

from terminusgps_payments.forms import (
    AddressForm,
    BankAccountForm,
    CreditCardForm,
    luhn_check,
)


class LuhnCheckTestCase(TestCase):
    def test_valid_card_number_passes(self):
        """Fails if a valid card number fails the luhn check."""
        result = luhn_check("4111111111111111")
        self.assertTrue(result)
        result = luhn_check("4242424242424242")
        self.assertTrue(result)

    def test_invalid_card_number_fails(self):
        """Fails if an invalid card number passes the luhn check."""
        result = luhn_check("4111111111111110")
        self.assertFalse(result)

    def test_empty_card_number_fails(self):
        """Fails if an empty string passes the luhn check."""
        result = luhn_check("")
        self.assertFalse(result)

    def test_non_digit_card_number_fails(self):
        """Fails if a non-digit card number passes the luhn check."""
        result = luhn_check(ascii_lowercase[:16])
        self.assertFalse(result)

    def test_double_card_number_fails(self):
        """Fails if a double card number passes the luhn check."""
        result = luhn_check("4111111111111111" * 2)
        self.assertFalse(result)

    def test_short_card_number_fails(self):
        """Fails if a short card number passes the luhn check"""
        result = luhn_check("411111111111")
        self.assertFalse(result)
        result = luhn_check("41111111")
        self.assertFalse(result)


class AddressFormTestCase(TestCase):
    def test_build_contract_with_missing_required_fields_raises_valuerror(
        self,
    ):
        """Fails if :py:meth:`build_contract` doesn't raise :py:exec:`ValueError` when called with missing form fields."""
        form = AddressForm(data={})
        with self.assertRaises(ValueError):
            form.build_contract()


class CreditCardFormTestCase(TestCase):
    def test_build_contract_with_missing_required_fields_raises_valueerror(
        self,
    ):
        """Fails if :py:meth:`build_contract` doesn't raise :py:exec:`ValueError` when called with missing form fields."""
        form = CreditCardForm(data={})
        with self.assertRaises(ValueError):
            form.build_contract()

    def test_clean_adds_error_on_invalid_card_number(self):
        """Fails if :py:meth:`clean` doesn't add an error when provided with an invalid card number."""
        form = CreditCardForm(
            data={
                "cardNumber": "4111111111111110",
                "cardCode": "444",
                "expirationDate": "2049-04",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("cardNumber", form.errors)


class BankAccountFormTestCase(TestCase):
    def test_build_contract_with_missing_required_fields_raises_valueerror(
        self,
    ):
        """Fails if :py:meth:`build_contract` doesn't raise :py:exec:`ValueError` when called with missing form fields."""
        form = BankAccountForm(data={})
        with self.assertRaises(ValueError):
            form.build_contract()
