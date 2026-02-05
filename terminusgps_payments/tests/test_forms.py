from django.test import TestCase

from terminusgps_payments.forms import CustomerPaymentProfileCreateForm


class CustomerPaymentProfileCreateFormTestCase(TestCase):
    def setUp(self):
        self.form_cls = CustomerPaymentProfileCreateForm

    def test_clean(self):
        """Fails if :py:meth:`clean` doesn't add expected errors to the form."""
        self.skipTest("TODO")
