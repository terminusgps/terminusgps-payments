import logging
from datetime import date
from unittest.mock import Mock

from authorizenet import apicontrollers
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
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
    ]

    def setUp(self):
        self.customerprofile = CustomerProfile.objects.get(pk=1)

    def test___str__(self):
        """Fails if the customer profile's :py:meth:`__str__` method returned unexpected values."""
        self.assertEqual(
            str(self.customerprofile), str(self.customerprofile.merchant_id)
        )
        self.customerprofile.merchant_id = ""
        self.assertIn(str(self.customerprofile.pk), str(self.customerprofile))

    def test_push_create(self):
        """Fails if :py:meth:`push` used an Authorizenet API contoller other than :py:obj:`~authorizenet.apicontrollers.createCustomerProfileController`."""
        mock_service = Mock(AuthorizenetService)

        self.customerprofile.pk = None
        self.customerprofile.push(mock_service)

        expected = apicontrollers.createCustomerProfileController
        controller = mock_service.execute.call_args.args[0][1]
        self.assertEqual(controller, expected)

    def test_push_update(self):
        """Fails if :py:meth:`push` used an Authorizenet API contoller other than :py:obj:`~authorizenet.apicontrollers.updateCustomerProfileController`."""
        mock_service = Mock(AuthorizenetService)

        self.customerprofile.pk = 1
        self.customerprofile.push(mock_service)

        expected = apicontrollers.updateCustomerProfileController
        controller = mock_service.execute.call_args.args[0][1]
        self.assertEqual(controller, expected)

    def test_pull(self):
        """Fails if :py:meth:`pull` used an Authorizenet API contoller other than :py:obj:`~authorizenet.apicontrollers.getCustomerProfileController`."""
        mock_service = Mock(AuthorizenetService)

        self.customerprofile.pk = 1
        self.customerprofile.pull(mock_service)

        expected = apicontrollers.getCustomerProfileController
        controller = mock_service.execute.call_args.args[0][1]
        self.assertEqual(controller, expected)

    def test_sync(self):
        """Fails if :py:attr:`email`, :py:attr:`merchant_id` or :py:attr:`description` weren't synced on :py:meth:`sync`."""
        merchant_id = "merchantId"
        email = "email@domain.com"
        description = "description"

        self.customerprofile.sync(
            elem=objectify.E.root(
                objectify.E.profile(
                    objectify.E.merchantCustomerId(merchant_id),
                    objectify.E.email(email),
                    objectify.E.description(description),
                )
            )
        )

        self.assertEqual(self.customerprofile.email, email)
        self.assertEqual(self.customerprofile.merchant_id, merchant_id)
        self.assertEqual(self.customerprofile.description, description)

    def test__delete_in_authorizenet(self):
        """Fails if :py:meth:`_delete_in_authorizenet` used an Authorizenet API contoller other than :py:obj:`~authorizenet.apicontrollers.deleteCustomerProfileController`."""
        mock_service = Mock(AuthorizenetService)

        self.customerprofile.pk = 1
        self.customerprofile._delete_in_authorizenet(mock_service)

        expected = apicontrollers.deleteCustomerProfileController
        controller = mock_service.execute.call_args.args[0][1]
        self.assertEqual(controller, expected)

    def test__extract_authorizenet_id(self):
        """Fails if :py:meth:`_extract_authorizenet_id` returns a non-integer."""
        expected = 1
        mock_element = objectify.E.root(
            objectify.E.customerProfileId(str(expected))
        )

        result = self.customerprofile._extract_authorizenet_id(mock_element)
        self.assertIsInstance(result, int)
        self.assertEqual(result, 1)


class CustomerAddressProfileTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
        "terminusgps_payments/tests/test_customeraddressprofile.json",
    ]

    def setUp(self):
        self.customeraddressprofile = CustomerAddressProfile.objects.get(pk=1)

    def test___str__(self):
        """Fails if the address profile's :py:meth:`__str__` method returned unexpected values."""
        self.assertEqual(
            str(self.customeraddressprofile),
            str(self.customeraddressprofile.address),
        )
        self.customeraddressprofile.pk = 1
        self.customeraddressprofile.address = ""
        self.assertEqual(
            str(self.customeraddressprofile), "CustomerAddressProfile #1"
        )

    def test_push_create(self):
        """Fails if :py:meth:`push` used an Authorizenet API contoller other than :py:obj:`~authorizenet.apicontrollers.createCustomerShippingAddressController`."""
        mock_service = Mock(AuthorizenetService)

        self.customeraddressprofile.pk = None
        self.customeraddressprofile.push(mock_service)

        expected = apicontrollers.createCustomerShippingAddressController
        controller = mock_service.execute.call_args.args[0][1]
        self.assertEqual(controller, expected)

    def test_push_update(self):
        """Fails if :py:meth:`push` used an Authorizenet API contoller other than :py:obj:`~authorizenet.apicontrollers.updateCustomerShippingAddressController`."""
        mock_service = Mock(AuthorizenetService)

        self.customeraddressprofile.pk = 1
        self.customeraddressprofile.push(mock_service)

        expected = apicontrollers.updateCustomerShippingAddressController
        controller = mock_service.execute.call_args.args[0][1]
        self.assertEqual(controller, expected)

    def test_pull(self):
        """Fails if :py:meth:`pull` used an Authorizenet API contoller other than :py:obj:`~authorizenet.apicontrollers.getCustomerShippingAddressController`."""
        mock_service = Mock(AuthorizenetService)

        self.customeraddressprofile.pk = 1
        self.customeraddressprofile.pull(mock_service)

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

        self.customeraddressprofile.sync(
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

        self.assertEqual(self.customeraddressprofile.first_name, first_name)
        self.assertEqual(self.customeraddressprofile.last_name, last_name)
        self.assertEqual(self.customeraddressprofile.company, company)
        self.assertEqual(self.customeraddressprofile.address, address)
        self.assertEqual(self.customeraddressprofile.city, city)
        self.assertEqual(self.customeraddressprofile.state, state)
        self.assertEqual(self.customeraddressprofile.country, country)
        self.assertEqual(self.customeraddressprofile.zip, zip)
        self.assertEqual(
            self.customeraddressprofile.phone_number, phone_number
        )

    def test__delete_in_authorizenet(self):
        """Fails if :py:meth:`_delete_in_authorizenet` used an Authorizenet API contoller other than :py:obj:`~authorizenet.apicontrollers.deleteCustomerShippingAddressController`."""
        mock_service = Mock(AuthorizenetService)

        self.customeraddressprofile.pk = 1
        self.customeraddressprofile._delete_in_authorizenet(mock_service)

        expected = apicontrollers.deleteCustomerShippingAddressController
        controller = mock_service.execute.call_args.args[0][1]
        self.assertEqual(controller, expected)

    def test__extract_authorizenet_id(self):
        """Fails if :py:meth:`_extract_authorizenet_id` returns a non-integer."""
        expected = 1
        mock_element = objectify.E.root(
            objectify.E.customerAddressId(str(expected))
        )

        result = self.customeraddressprofile._extract_authorizenet_id(
            mock_element
        )
        self.assertIsInstance(result, int)
        self.assertEqual(result, 1)


class CustomerPaymentProfileTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
        "terminusgps_payments/tests/test_customerpaymentprofile.json",
    ]

    def test___str__(self):
        """Fails if the payment profile's :py:meth:`__str__` method returned unexpected values."""
        cc_customerpaymentprofile = CustomerPaymentProfile.objects.get(pk=1)
        ba_customerpaymentprofile = CustomerPaymentProfile.objects.get(pk=2)
        self.assertEqual(
            str(cc_customerpaymentprofile), "TestCardType XXXX1111"
        )
        self.assertEqual(
            str(ba_customerpaymentprofile), "TestBankName checking"
        )
        cc_customerpaymentprofile.card_number = ""
        cc_customerpaymentprofile.card_type = ""
        self.assertEqual(
            str(cc_customerpaymentprofile), "CustomerPaymentProfile #1"
        )

    def test_push_create_credit_card(self):
        """Fails if :py:meth:`push` used an Authorizenet API contoller other than :py:obj:`~authorizenet.apicontrollers.createCustomerPaymentProfileController` for a credit card."""
        mock_service = Mock(AuthorizenetService)
        customerpaymentprofile = CustomerPaymentProfile.objects.get(pk=1)

        customerpaymentprofile.pk = None
        customerpaymentprofile.push(mock_service)

        expected = apicontrollers.createCustomerPaymentProfileController
        controller = mock_service.execute.call_args.args[0][1]
        self.assertEqual(controller, expected)

    def test_push_create_bank_account(self):
        """Fails if :py:meth:`push` used an Authorizenet API contoller other than :py:obj:`~authorizenet.apicontrollers.createCustomerPaymentProfileController` for a bank account."""
        mock_service = Mock(AuthorizenetService)
        customerpaymentprofile = CustomerPaymentProfile.objects.get(pk=2)

        customerpaymentprofile.pk = None
        customerpaymentprofile.push(mock_service)

        expected = apicontrollers.createCustomerPaymentProfileController
        controller = mock_service.execute.call_args.args[0][1]
        self.assertEqual(controller, expected)

    def test_push_update(self):
        """Fails if :py:meth:`push` used an Authorizenet API contoller other than :py:obj:`~authorizenet.apicontrollers.updateCustomerPaymentProfileController`."""
        mock_service = Mock(AuthorizenetService)
        customerpaymentprofile = CustomerPaymentProfile.objects.get(pk=1)

        customerpaymentprofile.push(mock_service)

        expected = apicontrollers.updateCustomerPaymentProfileController
        controller = mock_service.execute.call_args.args[0][1]
        self.assertEqual(controller, expected)

    def test_pull(self):
        """Fails if :py:meth:`pull` used an Authorizenet API contoller other than :py:obj:`~authorizenet.apicontrollers.getCustomerPaymentProfileController`."""
        mock_service = Mock(AuthorizenetService)
        customerpaymentprofile = CustomerPaymentProfile.objects.get(pk=1)

        customerpaymentprofile.pull(mock_service)

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

        customerpaymentprofile = CustomerPaymentProfile.objects.get(pk=2)
        customerpaymentprofile.sync(
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

        self.assertEqual(customerpaymentprofile.first_name, first_name)
        self.assertEqual(customerpaymentprofile.last_name, last_name)
        self.assertEqual(customerpaymentprofile.company, company)
        self.assertEqual(customerpaymentprofile.address, address)
        self.assertEqual(customerpaymentprofile.city, city)
        self.assertEqual(customerpaymentprofile.state, state)
        self.assertEqual(customerpaymentprofile.country, country)
        self.assertEqual(customerpaymentprofile.zip, zip)
        self.assertEqual(customerpaymentprofile.phone_number, phone_number)
        self.assertEqual(customerpaymentprofile.account_type, account_type)
        self.assertEqual(customerpaymentprofile.account_number, account_number)
        self.assertEqual(customerpaymentprofile.routing_number, routing_number)
        self.assertEqual(customerpaymentprofile.account_name, account_name)
        self.assertEqual(customerpaymentprofile.echeck_type, echeck_type)
        self.assertEqual(customerpaymentprofile.bank_name, bank_name)

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

        customerpaymentprofile = CustomerPaymentProfile.objects.get(pk=1)
        customerpaymentprofile.sync(
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

        self.assertEqual(customerpaymentprofile.first_name, first_name)
        self.assertEqual(customerpaymentprofile.last_name, last_name)
        self.assertEqual(customerpaymentprofile.company, company)
        self.assertEqual(customerpaymentprofile.address, address)
        self.assertEqual(customerpaymentprofile.city, city)
        self.assertEqual(customerpaymentprofile.state, state)
        self.assertEqual(customerpaymentprofile.country, country)
        self.assertEqual(customerpaymentprofile.zip, zip)
        self.assertEqual(customerpaymentprofile.phone_number, phone_number)
        self.assertEqual(customerpaymentprofile.card_number, card_number)
        self.assertEqual(customerpaymentprofile.card_type, card_type)

    def test__delete_in_authorizenet(self):
        """Fails if :py:meth:`_delete_in_authorizenet` used an Authorizenet API contoller other than :py:obj:`~authorizenet.apicontrollers.deleteCustomerPaymentProfileController`."""
        mock_service = Mock(AuthorizenetService)
        customerpaymentprofile = CustomerPaymentProfile.objects.get(pk=1)

        customerpaymentprofile._delete_in_authorizenet(mock_service)

        expected = apicontrollers.deleteCustomerPaymentProfileController
        controller = mock_service.execute.call_args.args[0][1]
        self.assertEqual(controller, expected)

    def test__extract_authorizenet_id(self):
        """Fails if :py:meth:`_extract_authorizenet_id` returns a non-integer."""
        customerpaymentprofile = CustomerPaymentProfile.objects.get(pk=1)
        expected_pk = 123
        mock_element = objectify.E.root(
            objectify.E.customerPaymentProfileId(str(expected_pk))
        )

        result = customerpaymentprofile._extract_authorizenet_id(mock_element)
        self.assertIsInstance(result, int)
        self.assertEqual(result, expected_pk)


class SubscriptionTestCase(TestCase):
    fixtures = [
        "terminusgps_payments/tests/test_user.json",
        "terminusgps_payments/tests/test_customerprofile.json",
        "terminusgps_payments/tests/test_customerpaymentprofile.json",
        "terminusgps_payments/tests/test_customeraddressprofile.json",
        "terminusgps_payments/tests/test_subscription.json",
    ]

    def test_pull(self):
        """Fails if :py:meth:`pull` used an Authorizenet API contoller other than :py:obj:`~authorizenet.apicontrollers.getCustomerProfileController`."""
        mock_service = Mock(AuthorizenetService)
        subscription = Subscription.objects.get(pk=1)
        subscription.pull(mock_service)

        expected = apicontrollers.ARBGetSubscriptionController
        controller = mock_service.execute.call_args.args[0][1]
        self.assertEqual(controller, expected)

    def test_push_create(self):
        """Fails if :py:meth:`push` used an Authorizenet API contoller other than :py:obj:`~authorizenet.apicontrollers.createCustomerProfileController`."""
        mock_service = Mock(AuthorizenetService)
        subscription = Subscription.objects.get(pk=1)
        subscription.pk = None

        subscription.push(mock_service)

        expected = apicontrollers.ARBCreateSubscriptionController
        controller = mock_service.execute.call_args.args[0][1]
        self.assertEqual(controller, expected)

    def test_push_update(self):
        """Fails if :py:meth:`push` used an Authorizenet API contoller other than :py:obj:`~authorizenet.apicontrollers.updateCustomerProfileController`."""
        mock_service = Mock(AuthorizenetService)
        subscription = Subscription.objects.get(pk=1)

        subscription.push(mock_service)

        expected = apicontrollers.ARBUpdateSubscriptionController
        controller = mock_service.execute.call_args.args[0][1]
        self.assertEqual(controller, expected)

    def test_sync(self):
        """Fails if subscription attributes weren't synced on :py:meth:`sync`."""
        subscription = Subscription.objects.get(pk=1)
        name = "TestName"
        amount = "TestAmount"
        trial_amount = "TestTrialAmount"
        status = "TestStatus"
        total_occurrences = 9999
        trial_occurrences = 0
        start_date = date(2039, 12, 1)

        subscription.sync(
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

        self.assertEqual(subscription.name, name)
        self.assertEqual(subscription.amount, amount)
        self.assertEqual(subscription.trial_amount, trial_amount)
        self.assertEqual(subscription.status, status)
        self.assertEqual(subscription.total_occurrences, total_occurrences)
        self.assertEqual(subscription.trial_occurrences, trial_occurrences)
        self.assertEqual(subscription.start_date, start_date)

    def test__delete_in_authorizenet(self):
        """Fails if :py:meth:`_delete_in_authorizenet` used an Authorizenet API contoller other than :py:obj:`~authorizenet.apicontrollers.deleteCustomerShippingAddressController`."""
        mock_service = Mock(AuthorizenetService)
        subscription = Subscription.objects.get(pk=1)

        subscription._delete_in_authorizenet(mock_service)

        expected = apicontrollers.ARBCancelSubscriptionController
        controller = mock_service.execute.call_args.args[0][1]
        self.assertEqual(controller, expected)

    def test__extract_authorizenet_id(self):
        """Fails if :py:meth:`_extract_authorizenet_id` returns a non-integer."""
        subscription = Subscription.objects.get(pk=1)
        expected = 1
        mock_element = objectify.E.root(
            objectify.E.subscriptionId(str(expected))
        )

        result = subscription._extract_authorizenet_id(mock_element)

        self.assertIsInstance(result, int)
        self.assertEqual(result, 1)
