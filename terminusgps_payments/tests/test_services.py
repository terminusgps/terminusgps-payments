from django.test import TestCase

from terminusgps_payments.services import sync_customer_profile


class SyncCustomerProfileTestCase(TestCase):
    def setUp(self):
        self.func = sync_customer_profile

    def test_non_existent_customer_profile_raises_valueerror(self):
        """Fails if :py:exec:`ValueError` wasn't raised when the provided pk pointed to a non-existent object."""
        with self.assertRaises(ValueError):
            self.func(pk=1)
