import logging
from datetime import date
from unittest.mock import Mock

from authorizenet import apicontrollers
from django.contrib.auth import get_user_model
from django.test import TestCase
from lxml import objectify
from terminusgps.authorizenet.service import AuthorizenetService

from terminusgps_payments.models import (
    CustomerAddressProfile,
    CustomerPaymentProfile,
    CustomerProfile,
    Subscription,
)
from terminusgps_payments.models.base import AuthorizenetModel

logging.disable(logging.CRITICAL)


class AuthorizenetTestModel(AuthorizenetModel):
    pass


class AuthorizenetModelTestCase(TestCase):
    def setUp(self):
        self.model = AuthorizenetTestModel()

    def test__delete_in_authorizenet(self):
        """Fails if :py:meth:`_extract_authorizenet_id` doesn't raise :py:exec:`NotImplementedError`."""
        with self.assertRaises(NotImplementedError):
            self.model._delete_in_authorizenet(Mock())

    def test__extract_authorizenet_id(self):
        """Fails if :py:meth:`_extract_authorizenet_id` doesn't raise :py:exec:`NotImplementedError`."""
        with self.assertRaises(NotImplementedError):
            self.model._extract_authorizenet_id(Mock())

    def test_push(self):
        """Fails if :py:meth:`push` doesn't raise :py:exec:`NotImplementedError`."""
        with self.assertRaises(NotImplementedError):
            self.model.push(Mock())

    def test_pull(self):
        """Fails if :py:meth:`pull` doesn't raise :py:exec:`NotImplementedError`."""
        with self.assertRaises(NotImplementedError):
            self.model.pull(Mock())

    def test_sync(self):
        """Fails if :py:meth:`sync` doesn't raise :py:exec:`NotImplementedError`."""
        with self.assertRaises(NotImplementedError):
            self.model.sync(Mock())


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

    def setUp(self):
        self.obj = CustomerProfile()
        self.obj.email = self.user_data["email"]
        self.obj.merchant_id = self.user_data["first_name"]
        self.obj.description = self.user_data["first_name"]

    def test___str__(self):
        """Fails if the customer profile's :py:meth:`__str__` method returned unexpected values."""
        self.assertEqual(str(self.obj), str(self.obj.merchant_id))
        self.obj.merchant_id = ""
        self.assertIn(str(self.obj.pk), str(self.obj))

    def test_push_create(self):
        """Fails if :py:meth:`push` used an Authorizenet API contoller other than :py:obj:`~authorizenet.apicontrollers.createCustomerProfileController`."""
        mock_service = Mock(AuthorizenetService)

        self.obj.push(mock_service)

        expected = apicontrollers.createCustomerProfileController
        controller = mock_service.execute.call_args.args[0][1]
        self.assertEqual(controller, expected)

    def test_push_update(self):
        """Fails if :py:meth:`push` used an Authorizenet API contoller other than :py:obj:`~authorizenet.apicontrollers.updateCustomerProfileController`."""
        mock_service = Mock(AuthorizenetService)

        self.obj.pk = 1
        self.obj.push(mock_service)

        expected = apicontrollers.updateCustomerProfileController
        controller = mock_service.execute.call_args.args[0][1]
        self.assertEqual(controller, expected)

    def test_pull(self):
        """Fails if :py:meth:`pull` used an Authorizenet API contoller other than :py:obj:`~authorizenet.apicontrollers.getCustomerProfileController`."""
        mock_service = Mock(AuthorizenetService)

        self.obj.pk = 1
        self.obj.pull(mock_service)

        expected = apicontrollers.getCustomerProfileController
        controller = mock_service.execute.call_args.args[0][1]
        self.assertEqual(controller, expected)

    def test_sync(self):
        """Fails if :py:attr:`email`, :py:attr:`merchant_id` or :py:attr:`description` weren't synced on :py:meth:`sync`."""
        merchant_id = "merchantId"
        email = "email@domain.com"
        description = "description"

        self.obj.sync(
            elem=objectify.E.root(
                objectify.E.profile(
                    objectify.E.merchantCustomerId(merchant_id),
                    objectify.E.email(email),
                    objectify.E.description(description),
                )
            )
        )

        self.assertEqual(self.obj.email, email)
        self.assertEqual(self.obj.merchant_id, merchant_id)
        self.assertEqual(self.obj.description, description)

    def test__delete_in_authorizenet(self):
        """Fails if :py:meth:`_delete_in_authorizenet` used an Authorizenet API contoller other than :py:obj:`~authorizenet.apicontrollers.deleteCustomerProfileController`."""
        mock_service = Mock(AuthorizenetService)

        self.obj.pk = 1
        self.obj._delete_in_authorizenet(mock_service)

        expected = apicontrollers.deleteCustomerProfileController
        controller = mock_service.execute.call_args.args[0][1]
        self.assertEqual(controller, expected)

    def test__extract_authorizenet_id(self):
        """Fails if :py:meth:`_extract_authorizenet_id` returns a non-integer."""
        expected = 1
        mock_element = objectify.E.root(
            objectify.E.customerProfileId(str(expected))
        )

        result = self.obj._extract_authorizenet_id(mock_element)
        self.assertIsInstance(result, int)
        self.assertEqual(result, 1)


class CustomerAddressProfileTestCase(TestCase):
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
        cls.customer_profile = CustomerProfile()
        cls.customer_profile.pk = 1
        cls.customer_profile.user = cls.user
        cls.customer_profile.email = cls.user_data["email"]
        cls.customer_profile.merchant_id = cls.user_data["first_name"]
        cls.customer_profile.description = cls.user_data["first_name"]

    def setUp(self):
        self.obj = CustomerAddressProfile()
        self.obj.customer_profile = self.customer_profile
        self.obj.first_name = "TestFirstName"
        self.obj.last_name = "TestLastName"
        self.obj.company = "TestCompany"
        self.obj.address = "TestAddress"
        self.obj.city = "TestCity"
        self.obj.state = "TestState"
        self.obj.country = "TestCountry"
        self.obj.zip = "TestZip"
        self.obj.phone_number = "TestPhoneNumber"

    def test___str__(self):
        """Fails if the address profile's :py:meth:`__str__` method returned unexpected values."""
        self.assertEqual(str(self.obj), str(self.obj.address))
        self.obj.pk = 1
        self.obj.address = ""
        self.assertEqual(str(self.obj), "CustomerAddressProfile #1")

    def test_push_create(self):
        """Fails if :py:meth:`push` used an Authorizenet API contoller other than :py:obj:`~authorizenet.apicontrollers.createCustomerShippingAddressController`."""
        mock_service = Mock(AuthorizenetService)

        self.obj.push(mock_service)

        expected = apicontrollers.createCustomerShippingAddressController
        controller = mock_service.execute.call_args.args[0][1]
        self.assertEqual(controller, expected)

    def test_push_update(self):
        """Fails if :py:meth:`push` used an Authorizenet API contoller other than :py:obj:`~authorizenet.apicontrollers.updateCustomerShippingAddressController`."""
        mock_service = Mock(AuthorizenetService)

        self.obj.pk = 1
        self.obj.push(mock_service)

        expected = apicontrollers.updateCustomerShippingAddressController
        controller = mock_service.execute.call_args.args[0][1]
        self.assertEqual(controller, expected)

    def test_pull(self):
        """Fails if :py:meth:`pull` used an Authorizenet API contoller other than :py:obj:`~authorizenet.apicontrollers.getCustomerShippingAddressController`."""
        mock_service = Mock(AuthorizenetService)

        self.obj.pk = 1
        self.obj.pull(mock_service)

        expected = apicontrollers.getCustomerShippingAddressController
        controller = mock_service.execute.call_args.args[0][1]
        self.assertEqual(controller, expected)

    def test_sync(self):
        """Fails if address profile attributes weren't synced on :py:meth:`sync`."""
        first_name = "firstName"
        last_name = "lastName"
        company = "company"
        address = "address"
        city = "city"
        state = "state"
        country = "country"
        zip = "zip"
        phone_number = "phoneNumber"

        self.obj.sync(
            elem=objectify.E.root(
                objectify.E.defaultShippingAddress(1),
                objectify.E.address(
                    objectify.E.firstName(first_name),
                    objectify.E.lastName(last_name),
                    objectify.E.company(company),
                    objectify.E.address(address),
                    objectify.E.city(city),
                    objectify.E.state(state),
                    objectify.E.country(country),
                    objectify.E.zip(zip),
                    objectify.E.phoneNumber(phone_number),
                ),
            )
        )

        self.assertEqual(self.obj.first_name, first_name)
        self.assertEqual(self.obj.last_name, last_name)
        self.assertEqual(self.obj.company, company)
        self.assertEqual(self.obj.address, address)
        self.assertEqual(self.obj.city, city)
        self.assertEqual(self.obj.state, state)
        self.assertEqual(self.obj.country, country)
        self.assertEqual(self.obj.zip, zip)
        self.assertEqual(self.obj.phone_number, phone_number)

    def test__delete_in_authorizenet(self):
        """Fails if :py:meth:`_delete_in_authorizenet` used an Authorizenet API contoller other than :py:obj:`~authorizenet.apicontrollers.deleteCustomerShippingAddressController`."""
        mock_service = Mock(AuthorizenetService)

        self.obj.pk = 1
        self.obj._delete_in_authorizenet(mock_service)

        expected = apicontrollers.deleteCustomerShippingAddressController
        controller = mock_service.execute.call_args.args[0][1]
        self.assertEqual(controller, expected)

    def test__extract_authorizenet_id(self):
        """Fails if :py:meth:`_extract_authorizenet_id` returns a non-integer."""
        expected = 1
        mock_element = objectify.E.root(
            objectify.E.customerAddressId(str(expected))
        )

        result = self.obj._extract_authorizenet_id(mock_element)
        self.assertIsInstance(result, int)
        self.assertEqual(result, 1)


class CustomerPaymentProfileTestCase(TestCase):
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
        cls.customer_profile = CustomerProfile()
        cls.customer_profile.pk = 1
        cls.customer_profile.user = cls.user
        cls.customer_profile.email = cls.user_data["email"]
        cls.customer_profile.merchant_id = cls.user_data["first_name"]
        cls.customer_profile.description = cls.user_data["first_name"]

    def setUp(self):
        self.obj = CustomerPaymentProfile()
        self.obj.customer_profile = self.customer_profile
        self.obj.first_name = "TestFirst"
        self.obj.last_name = "TestLast"
        self.obj.company = "TestCompany"
        self.obj.address = "123 Main St"
        self.obj.city = "Houston"
        self.obj.state = "TX"
        self.obj.country = "USA"
        self.obj.zip = "77065"
        self.obj.phone_number = "17139045260"

    def test___str__(self):
        """Fails if the payment profile's :py:meth:`__str__` method returned unexpected values."""
        self.obj.pk = 1
        self.assertEqual(str(self.obj), "CustomerPaymentProfile #1")
        self.obj.card_number = "XXXX1111"
        self.obj.card_type = "Test"
        self.assertEqual(str(self.obj), "Test XXXX1111")
        self.obj.card_number = ""
        self.obj.card_type = ""
        self.obj.bank_name = "Test"
        self.obj.account_type = "checking"
        self.assertEqual(str(self.obj), "Test checking")

    def test_push_create(self):
        """Fails if :py:meth:`push` used an Authorizenet API contoller other than :py:obj:`~authorizenet.apicontrollers.createCustomerPaymentProfileController` for a credit card."""
        mock_service = Mock(AuthorizenetService)

        self.obj.card_number = "4111111111111111"
        self.obj.card_expiry = date(2039, 12, 1)
        self.obj.card_code = "411"
        self.obj.account_type = "checking"
        self.obj.account_number = "41111111111111111"
        self.obj.routing_number = "411111111"
        self.obj.account_name = "TestAccountName"
        self.obj.bank_name = "TestBankName"
        self.obj.echeck_type = "PPD"
        self.obj.push(mock_service)

        expected = apicontrollers.createCustomerPaymentProfileController
        controller = mock_service.execute.call_args.args[0][1]
        self.assertEqual(controller, expected)

    def test_push_update(self):
        """Fails if :py:meth:`push` used an Authorizenet API contoller other than :py:obj:`~authorizenet.apicontrollers.updateCustomerPaymentProfileController`."""
        mock_service = Mock(AuthorizenetService)

        self.obj.pk = 1
        self.obj.card_number = "4111111111111111"
        self.obj.card_expiry = date(2039, 12, 1)
        self.obj.card_code = "411"
        self.obj.account_type = "checking"
        self.obj.account_number = "41111111111111111"
        self.obj.routing_number = "411111111"
        self.obj.account_name = "TestAccountName"
        self.obj.bank_name = "TestBankName"
        self.obj.echeck_type = "PPD"
        self.obj.push(mock_service)

        expected = apicontrollers.updateCustomerPaymentProfileController
        controller = mock_service.execute.call_args.args[0][1]
        self.assertEqual(controller, expected)

    def test_pull(self):
        """Fails if :py:meth:`pull` used an Authorizenet API contoller other than :py:obj:`~authorizenet.apicontrollers.getCustomerPaymentProfileController`."""
        mock_service = Mock(AuthorizenetService)

        self.obj.pk = 1
        self.obj.pull(mock_service)

        expected = apicontrollers.getCustomerPaymentProfileController
        controller = mock_service.execute.call_args.args[0][1]
        self.assertEqual(controller, expected)

    def test_sync_bank_account(self):
        """Fails if payment profile attributes weren't synced on :py:meth:`sync` with a bank account."""
        first_name = "firstName"
        last_name = "lastName"
        company = "company"
        address = "address"
        city = "city"
        state = "state"
        country = "country"
        zip = "zip"
        phone_number = "phoneNumber"
        account_type = "accountType"
        account_number = "accountNumber"
        routing_number = "routingNumber"
        account_name = "nameOnAccount"
        echeck_type = "eCheckType"
        bank_name = "bankName"

        self.obj.sync(
            elem=objectify.E.root(
                objectify.E.defaultPaymentProfile(1),
                objectify.E.billTo(
                    objectify.E.firstName(first_name),
                    objectify.E.lastName(last_name),
                    objectify.E.company(company),
                    objectify.E.address(address),
                    objectify.E.city(city),
                    objectify.E.state(state),
                    objectify.E.country(country),
                    objectify.E.zip(zip),
                    objectify.E.phoneNumber(phone_number),
                ),
                objectify.E.paymentProfile(
                    objectify.E.payment(
                        objectify.E.bankAccount(
                            objectify.E.accountType(account_type),
                            objectify.E.accountNumber(account_number),
                            objectify.E.routingNumber(routing_number),
                            objectify.E.nameOnAccount(account_name),
                            objectify.E.eCheckType(echeck_type),
                            objectify.E.bankName(bank_name),
                        )
                    )
                ),
            )
        )

        self.assertEqual(self.obj.first_name, first_name)
        self.assertEqual(self.obj.last_name, last_name)
        self.assertEqual(self.obj.company, company)
        self.assertEqual(self.obj.address, address)
        self.assertEqual(self.obj.city, city)
        self.assertEqual(self.obj.state, state)
        self.assertEqual(self.obj.country, country)
        self.assertEqual(self.obj.zip, zip)
        self.assertEqual(self.obj.phone_number, phone_number)
        self.assertEqual(self.obj.account_type, account_type)
        self.assertEqual(self.obj.account_number, account_number)
        self.assertEqual(self.obj.routing_number, routing_number)
        self.assertEqual(self.obj.account_name, account_name)
        self.assertEqual(self.obj.echeck_type, echeck_type)
        self.assertEqual(self.obj.bank_name, bank_name)

    def test_sync_credit_card(self):
        """Fails if payment profile attributes weren't synced on :py:meth:`sync` with a credit card."""
        first_name = "firstName"
        last_name = "lastName"
        company = "company"
        address = "address"
        city = "city"
        state = "state"
        country = "country"
        zip = "zip"
        phone_number = "phoneNumber"
        card_number = "cardNumber"
        card_type = "cardType"

        self.obj.sync(
            elem=objectify.E.root(
                objectify.E.defaultPaymentProfile(1),
                objectify.E.billTo(
                    objectify.E.firstName(first_name),
                    objectify.E.lastName(last_name),
                    objectify.E.company(company),
                    objectify.E.address(address),
                    objectify.E.city(city),
                    objectify.E.state(state),
                    objectify.E.country(country),
                    objectify.E.zip(zip),
                    objectify.E.phoneNumber(phone_number),
                ),
                objectify.E.paymentProfile(
                    objectify.E.payment(
                        objectify.E.creditCard(
                            objectify.E.cardNumber(card_number),
                            objectify.E.cardType(card_type),
                        )
                    )
                ),
            )
        )

        self.assertEqual(self.obj.first_name, first_name)
        self.assertEqual(self.obj.last_name, last_name)
        self.assertEqual(self.obj.company, company)
        self.assertEqual(self.obj.address, address)
        self.assertEqual(self.obj.city, city)
        self.assertEqual(self.obj.state, state)
        self.assertEqual(self.obj.country, country)
        self.assertEqual(self.obj.zip, zip)
        self.assertEqual(self.obj.phone_number, phone_number)
        self.assertEqual(self.obj.card_number, card_number)
        self.assertEqual(self.obj.card_type, card_type)

    def test__delete_in_authorizenet(self):
        """Fails if :py:meth:`_delete_in_authorizenet` used an Authorizenet API contoller other than :py:obj:`~authorizenet.apicontrollers.deleteCustomerPaymentProfileController`."""
        mock_service = Mock(AuthorizenetService)

        self.obj.pk = 1
        self.obj._delete_in_authorizenet(mock_service)

        expected = apicontrollers.deleteCustomerPaymentProfileController
        controller = mock_service.execute.call_args.args[0][1]
        self.assertEqual(controller, expected)

    def test__extract_authorizenet_id(self):
        """Fails if :py:meth:`_extract_authorizenet_id` returns a non-integer."""
        expected = 1
        mock_element = objectify.E.root(
            objectify.E.customerPaymentProfileId(str(expected))
        )

        result = self.obj._extract_authorizenet_id(mock_element)
        self.assertIsInstance(result, int)
        self.assertEqual(result, 1)

    def test_save_obfuscates_credit_card(self):
        """Fails if a credit card wasn't obfuscated after calling :py:meth:`save`."""
        self.skipTest("TODO")


class SubscriptionTestCase(TestCase):
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
        cls.customer_profile = CustomerProfile()
        cls.customer_profile.pk = 1
        cls.customer_profile.user = cls.user
        cls.customer_profile.email = cls.user_data["email"]
        cls.customer_profile.merchant_id = cls.user_data["first_name"]
        cls.customer_profile.description = cls.user_data["first_name"]

        cls.address_profile = CustomerAddressProfile()
        cls.address_profile.customer_profile = cls.customer_profile
        cls.address_profile.pk = 1
        cls.address_profile.first_name = "TestFirstName"
        cls.address_profile.last_name = "TestLastName"
        cls.address_profile.company = "TestCompany"
        cls.address_profile.address = "TestAddress"
        cls.address_profile.city = "TestCity"
        cls.address_profile.state = "TestState"
        cls.address_profile.country = "TestCountry"
        cls.address_profile.zip = "TestZip"
        cls.address_profile.phone_number = "TestPhoneNumber"

        cls.payment_profile = CustomerPaymentProfile()
        cls.payment_profile.customer_profile = cls.customer_profile
        cls.payment_profile.pk = 1
        cls.payment_profile.first_name = "TestFirstName"
        cls.payment_profile.last_name = "TestLastName"
        cls.payment_profile.company = "TestCompany"
        cls.payment_profile.address = "TestAddress"
        cls.payment_profile.city = "TestCity"
        cls.payment_profile.state = "TestState"
        cls.payment_profile.country = "TestCountry"
        cls.payment_profile.zip = "TestZip"
        cls.payment_profile.phone_number = "TestPhoneNumber"
        cls.payment_profile.card_number = "TestCardNumber"
        cls.payment_profile.card_type = "TestCardType"

    def setUp(self):
        self.obj = Subscription()
        self.obj.customer_profile = self.customer_profile
        self.obj.address_profile = self.address_profile
        self.obj.payment_profile = self.payment_profile

    def test_pull(self):
        """Fails if :py:meth:`pull` used an Authorizenet API contoller other than :py:obj:`~authorizenet.apicontrollers.getCustomerProfileController`."""
        mock_service = Mock(AuthorizenetService)

        self.obj.pk = 1
        self.obj.pull(mock_service)

        expected = apicontrollers.ARBGetSubscriptionController
        controller = mock_service.execute.call_args.args[0][1]
        self.assertEqual(controller, expected)

    def test_push_create(self):
        """Fails if :py:meth:`push` used an Authorizenet API contoller other than :py:obj:`~authorizenet.apicontrollers.createCustomerProfileController`."""
        mock_service = Mock(AuthorizenetService)

        self.obj.push(mock_service)

        expected = apicontrollers.ARBCreateSubscriptionController
        controller = mock_service.execute.call_args.args[0][1]
        self.assertEqual(controller, expected)

    def test_push_update(self):
        """Fails if :py:meth:`push` used an Authorizenet API contoller other than :py:obj:`~authorizenet.apicontrollers.updateCustomerProfileController`."""
        mock_service = Mock(AuthorizenetService)

        self.obj.pk = 1
        self.obj.push(mock_service)

        expected = apicontrollers.ARBUpdateSubscriptionController
        controller = mock_service.execute.call_args.args[0][1]
        self.assertEqual(controller, expected)

    def test_sync(self):
        """Fails if subscription attributes weren't synced on :py:meth:`sync`."""
        name = "TestName"
        amount = "TestAmount"
        trial_amount = "TestTrialAmount"
        status = "TestStatus"
        total_occurrences = 9999
        trial_occurrences = 0
        start_date = date(2039, 12, 1)

        self.obj.sync(
            elem=objectify.E.root(
                objectify.E.subscription(
                    objectify.E.name(name),
                    objectify.E.amount(amount),
                    objectify.E.trialAmount(trial_amount),
                    objectify.E.status(status),
                    objectify.E.paymentSchedule(
                        objectify.E.totalOccurrences(total_occurrences),
                        objectify.E.trialOccurrences(trial_occurrences),
                        objectify.E.startDate(start_date.strftime("%Y-%m-%d")),
                    ),
                )
            )
        )

        self.assertEqual(self.obj.name, name)
        self.assertEqual(self.obj.amount, amount)
        self.assertEqual(self.obj.trial_amount, trial_amount)
        self.assertEqual(self.obj.status, status)
        self.assertEqual(self.obj.total_occurrences, total_occurrences)
        self.assertEqual(self.obj.trial_occurrences, trial_occurrences)
        self.assertEqual(self.obj.start_date, start_date)

    def test__delete_in_authorizenet(self):
        """Fails if :py:meth:`_delete_in_authorizenet` used an Authorizenet API contoller other than :py:obj:`~authorizenet.apicontrollers.deleteCustomerShippingAddressController`."""
        mock_service = Mock(AuthorizenetService)

        self.obj.pk = 1
        self.obj._delete_in_authorizenet(mock_service)

        expected = apicontrollers.ARBCancelSubscriptionController
        controller = mock_service.execute.call_args.args[0][1]
        self.assertEqual(controller, expected)

    def test__extract_authorizenet_id(self):
        """Fails if :py:meth:`_extract_authorizenet_id` returns a non-integer."""
        expected = 1
        mock_element = objectify.E.root(
            objectify.E.subscriptionId(str(expected))
        )

        result = self.obj._extract_authorizenet_id(mock_element)
        self.assertIsInstance(result, int)
        self.assertEqual(result, 1)
