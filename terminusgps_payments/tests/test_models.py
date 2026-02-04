import logging
from unittest.mock import Mock

from authorizenet import apicontrollers
from django.contrib.auth import get_user_model
from django.test import TestCase
from terminusgps.authorizenet.service import AuthorizenetService

from terminusgps_payments.models import CustomerProfile

logging.disable(logging.CRITICAL)


class CustomerProfileTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {
            "first_name": "TestFirst",
            "last_name": "TestLast",
            "username": "testuser",
            "password": "super_secure_password1!",
            "email": "testuser@domain.com",
        }
        cls.user = get_user_model().objects.create(**cls.user_data)
        cls.mock_service = Mock(AuthorizenetService)

    def setUp(self):
        self.obj = CustomerProfile()
        self.obj.email = self.user_data["email"]
        self.obj.merchant_id = self.user_data["first_name"]
        self.obj.description = self.user_data["first_name"]
        self.mock_service.reset_mock()

    def test___str__(self):
        """Fails if the customer profile's :py:meth:`__str__` method returned unexpected values."""
        self.assertEqual(str(self.obj), str(self.obj.merchant_id))
        self.obj.merchant_id = ""
        self.assertIn(str(self.obj.pk), str(self.obj))

    def test_push_create(self):
        """"""
        self.obj.push(self.mock_service)
        request_tuple = self.mock_service.execute.call_args.args[0]
        self.assertEqual(
            request_tuple[1], apicontrollers.createCustomerProfileController
        )

    def test_push_update(self):
        """"""
        self.obj.pk = 1
        self.obj.push(self.mock_service)
        request_tuple = self.mock_service.execute.call_args.args[0]
        self.assertEqual(
            request_tuple[1], apicontrollers.updateCustomerProfileController
        )

    def test_pull(self):
        """"""
        self.obj.pk = 1
        self.obj.pull(self.mock_service)
        request_tuple = self.mock_service.execute.call_args.args[0]
        self.assertEqual(
            request_tuple[1], apicontrollers.getCustomerProfileController
        )

    def test_sync(self):
        """"""
        return
