from django.contrib.auth import get_user_model
from django.test import TestCase

from terminusgps_payments.forms import (
    CustomerAddressProfileCreateForm,
    CustomerPaymentProfileCreateForm,
)
from terminusgps_payments.models import (
    CustomerAddressProfile,
    CustomerPaymentProfile,
)
from terminusgps_payments.views import AuthorizenetCreateView


class CustomerAddressProfileCreateTestView(AuthorizenetCreateView):
    model = CustomerAddressProfile
    form_class = CustomerAddressProfileCreateForm


class CustomerPaymentProfileCreateTestView(AuthorizenetCreateView):
    model = CustomerPaymentProfile
    form_class = CustomerPaymentProfileCreateForm


class AuthorizenetCreateViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {
            "first_name": "TestFirstName",
            "last_name": "TestLastName",
            "email": "test@domain.com",
            "username": "testusername",
            "password": "super_secure_password1!",
        }
        cls.user = get_user_model().objects.create_user(**cls.user_data)

    def test_get_initial(self):
        """Fails if required context variables weren't present in the view context."""
        self.skipTest("TODO")

    def test_form_valid_customeraddressprofile(self):
        """Fails if a customer address profile wasn't created despite a valid form."""
        self.skipTest("TODO")

    def test_form_valid_customerpaymentprofile(self):
        """Fails if a customer payment profile wasn't created despite a valid form."""
        self.skipTest("TODO")
