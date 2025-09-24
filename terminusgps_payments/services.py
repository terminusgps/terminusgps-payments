from authorizenet import apicontractsv1
from django.conf import settings
from lxml.objectify import ObjectifiedElement
from terminusgps.authorizenet import api
from terminusgps.authorizenet.service import (
    AuthorizenetService as AuthorizenetServiceBase,
)

from terminusgps_payments import models


class AuthorizenetService(AuthorizenetServiceBase):
    def create_customer_profile(
        self, customer_profile: models.CustomerProfile
    ) -> ObjectifiedElement:
        """
        Creates the customer profile in Authorizenet.

        :py:attr:`customer_profile.user` is expected to have :py:attr:`email`, :py:attr:`first_name` and :py:attr:`last_name`.

        :param customer_profile: A customer profile with no :py:attr:`pk` set.
        :type customer_profile: ~terminusgps_payments.models.CustomerProfile
        :raises ValueError: If the customer profile had :py:attr:`pk` set.
        :raises AuthorizenetControllerExecutionError: If something went wrong during the API call.
        :returns: The Authorizenet API response.
        :rtype: ~lxml.objectify.ObjectifiedElement

        """
        if customer_profile.pk:
            raise ValueError(
                f"'{customer_profile}' already had a pk: '{customer_profile.pk}'."
            )
        return self.execute(
            api.create_customer_profile(
                merchant_id=str(customer_profile.user.pk),
                email=str(customer_profile.user.email),
                description=f"{customer_profile.user.first_name} {customer_profile.user.last_name}",
            )
        )

    def get_customer_profile(
        self,
        customer_profile: models.CustomerProfile,
        include_issuer_info: bool = False,
    ) -> ObjectifiedElement:
        """
        Returns the customer profile from Authorizenet.

        :param customer_profile: A customer profile.
        :type customer_profile: ~terminusgps_payments.models.CustomerProfile
        :param include_issuer_info: Whether to include issuer info in the response. Default is :py:obj:`False`.
        :type include_issuer_info: bool
        :raises ValueError: If the customer profile didn't have :py:attr:`pk` set.
        :raises AuthorizenetControllerExecutionError: If something went wrong during the API call.
        :returns: The Authorizenet API response.
        :rtype: ~lxml.objectify.ObjectifiedElement

        """
        if not customer_profile.pk:
            raise ValueError(f"'{customer_profile}' didn't have a pk.")
        return self.execute(
            api.get_customer_profile(
                customer_profile_id=customer_profile.pk,
                include_issuer_info=include_issuer_info,
            )
        )

    def update_customer_profile(
        self,
        customer_profile: models.CustomerProfile,
        profile: apicontractsv1.customerProfileExType,
    ) -> ObjectifiedElement:
        """
        Updates the customer profile in Authorizenet.

        :param customer_profile: A customer profile.
        :type customer_profile: ~terminusgps_payments.models.CustomerProfile
        :param profile: An Authorizenet profile element to update the customer profile with.
        :type profile: ~authorizenet.apicontractsv1.customerProfileExType
        :raises ValueError: If the customer profile didn't have :py:attr:`pk` set.
        :raises AuthorizenetControllerExecutionError: If something went wrong during the API call.
        :returns: The Authorizenet API response.
        :rtype: ~lxml.objectify.ObjectifiedElement

        """
        if not customer_profile.pk:
            raise ValueError(f"'{customer_profile}' didn't have a pk.")
        profile.customerProfileId = customer_profile.pk
        return self.execute(api.update_customer_profile(profile=profile))

    def delete_customer_profile(
        self, customer_profile: models.CustomerProfile
    ) -> ObjectifiedElement:
        """
        Deletes the customer profile in Authorizenet.

        :param customer_profile: A customer profile.
        :type customer_profile: ~terminusgps_payments.models.CustomerProfile
        :raises ValueError: If the customer profile didn't have :py:attr:`pk` set.
        :raises AuthorizenetControllerExecutionError: If something went wrong during the API call.
        :returns: The Authorizenet API response.
        :rtype: ~lxml.objectify.ObjectifiedElement

        """
        if not customer_profile.pk:
            raise ValueError(f"'{customer_profile}' didn't have a pk.")
        return self.execute(
            api.delete_customer_profile(
                customer_profile_id=customer_profile.pk
            )
        )

    def create_address_profile(
        self,
        address_profile: models.AddressProfile,
        address: apicontractsv1.customerAddressType,
        default: bool,
    ) -> ObjectifiedElement:
        """
        Creates the address profile in Authorizenet.

        :param address_profile: An address profile with no :py:attr:`pk` set.
        :type address_profile: ~terminusgps_payments.models.AddressProfile
        :param address: An Authorizenet address element.
        :type address: ~authorizenet.apicontractsv1.customerAddressType
        :param default: Whether to set the address profile as default.
        :type default: bool
        :raises ValueError: If the address profile had :py:attr:`pk` set.
        :raises ValueError: If the address profile didn't have a customer profile.
        :raises AuthorizenetControllerExecutionError: If something went wrong during the API call.
        :returns: The Authorizenet API response.
        :rtype: ~lxml.objectify.ObjectifiedElement

        """
        if address_profile.pk:
            raise ValueError(
                f"'{address_profile}' already had a pk: '{address_profile.pk}'."
            )
        if not hasattr(address_profile, "customer_profile"):
            raise ValueError(
                f"'{address_profile}' didn't have a customer profile."
            )
        return self.execute(
            api.create_customer_shipping_address(
                customer_profile_id=address_profile.customer_profile.pk,
                address=address,
                default=default,
            )
        )

    def get_address_profile(
        self, address_profile: models.AddressProfile
    ) -> ObjectifiedElement:
        """
        Gets the address profile from Authorizenet.

        :param address_profile: An address profile.
        :type address_profile: ~terminusgps_payments.models.AddressProfile
        :raises ValueError: If the address profile didn't have :py:attr:`pk` set.
        :raises ValueError: If the address profile didn't have a customer profile.
        :raises AuthorizenetControllerExecutionError: If something went wrong during the API call.
        :returns: The Authorizenet API response.
        :rtype: ~lxml.objectify.ObjectifiedElement

        """
        if not address_profile.pk:
            raise ValueError(f"'{address_profile}' didn't have a pk.")
        if not hasattr(address_profile, "customer_profile"):
            raise ValueError(
                f"'{address_profile}' didn't have a customer profile."
            )
        return self.execute(
            api.get_customer_shipping_address(
                customer_profile_id=address_profile.customer_profile.pk,
                address_profile_id=address_profile.pk,
            )
        )

    def update_address_profile(
        self,
        address_profile: models.AddressProfile,
        address: apicontractsv1.customerAddressType,
        default: bool,
    ) -> ObjectifiedElement:
        """
        Updates the address profile in Authorizenet.

        :param address_profile: An address profile.
        :type address_profile: ~terminusgps_payments.models.AddressProfile
        :param address: An Authorizenet customer address element to update the address profile with.
        :type address: ~authorizenet.apicontractsv1.customerAddressType
        :param default: Whether to set the address profile as default.
        :type default: bool
        :raises ValueError: If the address profile didn't have :py:attr:`pk` set.
        :raises ValueError: If the address profile didn't have a customer profile.
        :raises AuthorizenetControllerExecutionError: If something went wrong during the API call.
        :returns: The Authorizenet API response.
        :rtype: ~lxml.objectify.ObjectifiedElement

        """
        if not address_profile.pk:
            raise ValueError(f"'{address_profile}' didn't have a pk.")
        if not hasattr(address_profile, "customer_profile"):
            raise ValueError(
                f"'{address_profile}' didn't have a customer profile."
            )
        return self.execute(
            api.update_customer_shipping_address(
                customer_profile_id=address_profile.customer_profile.pk,
                address=address,
                default=default,
            )
        )

    def delete_address_profile(
        self, address_profile: models.AddressProfile
    ) -> ObjectifiedElement:
        """
        Deletes the address profile in Authorizenet.

        :param address_profile: An address profile.
        :type address_profile: ~terminusgps_payments.models.AddressProfile
        :raises ValueError: If the address profile didn't have :py:attr:`pk` set.
        :raises ValueError: If the address profile didn't have a customer profile.
        :raises AuthorizenetControllerExecutionError: If something went wrong during the API call.
        :returns: The Authorizenet API response.
        :rtype: ~lxml.objectify.ObjectifiedElement

        """
        if not address_profile.pk:
            raise ValueError(f"'{address_profile}' didn't have a pk.")
        if not hasattr(address_profile, "customer_profile"):
            raise ValueError(
                f"'{address_profile}' didn't have a customer profile."
            )
        return self.execute(
            api.delete_customer_shipping_address(
                customer_profile_id=address_profile.customer_profile.pk,
                address_profile_id=address_profile.pk,
            )
        )

    def create_payment_profile(
        self,
        payment_profile: models.PaymentProfile,
        address: apicontractsv1.customerAddressType,
        credit_card: apicontractsv1.creditCardType,
        default: bool,
    ) -> ObjectifiedElement:
        """
        Creates a payment profile in Authorizenet.

        :param payment_profile: A payment profile with no :py:attr:`pk` set.
        :type payment_profile: ~terminusgps_payments.models.PaymentProfile
        :param address: A customer address.
        :type address: ~authorizenet.apicontractsv1.customerAddressType
        :param credit_card: A credit card.
        :type credit_card: ~authorizenet.apicontractsv1.creditCardType
        :param default: Whether to set the payment profile as default.
        :type default: bool
        :raises ValueError: If the payment profile had :py:attr:`pk` set.
        :raises ValueError: If the payment profile didn't have a customer profile.
        :raises AuthorizenetControllerExecutionError: If something went wrong during the API call.
        :returns: The Authorizenet API response.
        :rtype: ~lxml.objectify.ObjectifiedElement

        """
        if payment_profile.pk:
            raise ValueError(
                f"'{payment_profile}' already had a pk: '{payment_profile.pk}'."
            )
        if not hasattr(payment_profile, "customer_profile"):
            raise ValueError(
                f"'{payment_profile}' didn't have a customer profile."
            )
        return self.execute(
            api.create_customer_payment_profile(
                customer_profile_id=payment_profile.customer_profile.pk,
                payment=apicontractsv1.paymentType(creditCard=credit_card),
                address=address,
                default=default,
                validation=settings.MERCHANT_AUTH_VALIDATION_MODE,
            )
        )

    def get_payment_profile(
        self,
        payment_profile: models.PaymentProfile,
        include_issuer_info: bool = False,
    ) -> ObjectifiedElement:
        """
        Returns the payment profile from Authorizenet.

        :param payment_profile: A payment profile.
        :type payment_profile: ~terminusgps_payments.models.PaymentProfile
        :param include_issuer_info: Whether to include issuer info in the response. Default is :py:obj:`False`.
        :type include_issuer_info: bool
        :raises ValueError: If the payment profile didn't have :py:attr:`pk` set.
        :raises ValueError: If the payment profile didn't have a customer profile.
        :raises AuthorizenetControllerExecutionError: If something went wrong during the API call.
        :returns: The Authorizenet API response.
        :rtype: ~lxml.objectify.ObjectifiedElement

        """
        if not payment_profile.pk:
            raise ValueError(f"'{payment_profile}' didn't have a pk.")
        if not hasattr(payment_profile, "customer_profile"):
            raise ValueError(
                f"'{payment_profile}' didn't have a customer profile."
            )
        return self.execute(
            api.get_customer_payment_profile(
                customer_profile_id=payment_profile.customer_profile.pk,
                payment_profile_id=payment_profile.pk,
                include_issuer_info=include_issuer_info,
            )
        )

    def update_payment_profile(
        self,
        payment_profile: models.PaymentProfile,
        address: apicontractsv1.customerAddressType,
        credit_card: apicontractsv1.creditCardType,
        default: bool,
    ) -> ObjectifiedElement:
        """
        Updates the payment profile in Authorizenet.

        :param payment_profile: A payment profile.
        :type payment_profile: ~terminusgps_payments.models.PaymentProfile
        :param address: A customer address element.
        :type address: ~authorizenet.apicontractsv1.customerAddressType
        :param credit_card: A credit card element.
        :type credit_card: ~authorizenet.apicontractsv1.creditCardType
        :param default: Whether to set the payment profile as default.
        :type default: bool
        :raises ValueError: If the payment profile didn't have :py:attr:`pk` set.
        :raises ValueError: If the payment profile didn't have a customer profile.
        :raises AuthorizenetControllerExecutionError: If something went wrong during the API call.
        :returns: The Authorizenet API response.
        :rtype: ~lxml.objectify.ObjectifiedElement

        """
        if not payment_profile.pk:
            raise ValueError(f"'{payment_profile}' didn't have a pk.")
        if not hasattr(payment_profile, "customer_profile"):
            raise ValueError(
                f"'{payment_profile}' didn't have a customer profile."
            )
        return self.execute(
            api.update_customer_payment_profile(
                customer_profile_id=payment_profile.customer_profile.pk,
                payment_profile_id=payment_profile.pk,
                payment=apicontractsv1.paymentType(creditCard=credit_card),
                address=address,
                default=default,
                validation=settings.MERCHANT_AUTH_VALIDATION_MODE,
            )
        )

    def delete_payment_profile(
        self, payment_profile: models.PaymentProfile
    ) -> ObjectifiedElement:
        """
        Deletes the payment profile in Authorizenet.

        :param payment_profile: A payment profile.
        :type payment_profile: ~terminusgps_payments.models.PaymentProfile
        :raises ValueError: If the payment profile didn't have :py:attr:`pk` set.
        :raises ValueError: If the payment profile didn't have a customer profile.
        :raises AuthorizenetControllerExecutionError: If something went wrong during the API call.
        :returns: The Authorizenet API response.
        :rtype: ~lxml.objectify.ObjectifiedElement

        """
        if not payment_profile.pk:
            raise ValueError(f"'{payment_profile}' didn't have a pk.")
        if not hasattr(payment_profile, "customer_profile"):
            raise ValueError(
                f"'{payment_profile}' didn't have a customer profile."
            )
        return self.execute(
            api.delete_customer_payment_profile(
                customer_profile_id=payment_profile.customer_profile.pk,
                payment_profile_id=payment_profile.pk,
            )
        )

    def create_subscription(
        self,
        subscription: models.Subscription,
        subscription_obj: apicontractsv1.ARBSubscriptionType,
    ) -> ObjectifiedElement:
        """
        Creates a subscription in Authorizenet.

        :param subscription: A subscription.
        :type subscription: ~terminusgps_payments.models.Subscription
        :param subscription_obj: An Authorizenet ARBSubscriptionType element.
        :type subscription_obj: ~authorizenet.apicontractsv1.customerAddressType
        :raises ValueError: If the subscription had :py:attr:`pk` set.
        :raises AuthorizenetControllerExecutionError: If something went wrong during the API call.
        :returns: The Authorizenet API response.
        :rtype: ~lxml.objectify.ObjectifiedElement

        """
        if subscription.pk:
            raise ValueError(
                f"'{subscription}' already had a pk: '{subscription.pk}'."
            )
        return self.execute(
            api.create_subscription(subscription=subscription_obj)
        )

    def get_subscription(
        self,
        subscription: models.Subscription,
        include_transactions: bool = False,
    ) -> ObjectifiedElement:
        """
        Gets a subscription from Authorizenet.

        :param subscription: A subscription.
        :type subscription: ~terminusgps_payments.models.Subscription
        :param include_transactions: Whether to include transactions in the response. Default is :py:obj:`False`.
        :type include_transactions: bool
        :raises ValueError: If the subscription didn't have :py:attr:`pk` set.
        :raises AuthorizenetControllerExecutionError: If something went wrong during the API call.
        :returns: The Authorizenet API response.
        :rtype: ~lxml.objectify.ObjectifiedElement

        """
        if not subscription.pk:
            raise ValueError(f"'{subscription}' didn't have a pk.")
        return self.execute(
            api.get_subscription(
                subscription_id=subscription.pk,
                include_transactions=include_transactions,
            )
        )

    def get_subscription_status(
        self, subscription: models.Subscription
    ) -> ObjectifiedElement:
        """
        Gets a subscription's status from Authorizenet.

        :param subscription: A subscription.
        :type subscription: ~terminusgps_payments.models.Subscription
        :raises ValueError: If the subscription didn't have :py:attr:`pk` set.
        :raises AuthorizenetControllerExecutionError: If something went wrong during the API call.
        :returns: The Authorizenet API response.
        :rtype: ~lxml.objectify.ObjectifiedElement

        """
        if not subscription.pk:
            raise ValueError(f"'{subscription}' didn't have a pk.")
        return self.execute(
            api.get_subscription_status(subscription_id=subscription.pk)
        )

    def update_subscription(
        self,
        subscription: models.Subscription,
        subscription_obj: apicontractsv1.ARBSubscriptionType,
    ) -> ObjectifiedElement:
        """
        Updates a subscription in Authorizenet.

        :param subscription: A subscription.
        :type subscription: ~terminusgps_payments.models.Subscription
        :param subscription_obj: An Authorizenet ARBSubscriptionType element.
        :type subscription_obj: ~authorizenet.apicontractsv1.customerAddressType
        :raises ValueError: If the subscription didn't have :py:attr:`pk` set.
        :raises AuthorizenetControllerExecutionError: If something went wrong during the API call.
        :returns: The Authorizenet API response.
        :rtype: ~lxml.objectify.ObjectifiedElement

        """
        if not subscription.pk:
            raise ValueError(f"'{subscription}' didn't have a pk.")
        return self.execute(
            api.update_subscription(
                subscription_id=subscription.pk, subscription=subscription_obj
            )
        )

    def delete_subscription(
        self, subscription: models.Subscription
    ) -> ObjectifiedElement:
        """
        Deletes a subscription in Authorizenet.

        :param subscription: A subscription.
        :type subscription: ~terminusgps_payments.models.Subscription
        :raises ValueError: If the subscription didn't have :py:attr:`pk` set.
        :raises AuthorizenetControllerExecutionError: If something went wrong during the API call.
        :returns: The Authorizenet API response.
        :rtype: ~lxml.objectify.ObjectifiedElement

        """
        if not subscription.pk:
            raise ValueError(f"'{subscription}' didn't have a pk.")
        return self.execute(
            api.cancel_subscription(subscription_id=subscription.pk)
        )
