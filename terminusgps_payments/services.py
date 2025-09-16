from authorizenet import apicontractsv1
from django.conf import settings
from lxml.objectify import ObjectifiedElement
from terminusgps.authorizenet import api
from terminusgps.authorizenet.service import AuthorizenetService

from terminusgps_payments import models


class CustomerProfileService(AuthorizenetService):
    def create(
        self, customer_profile: models.CustomerProfile
    ) -> models.CustomerProfile:
        """
        Creates the customer profile in Authorizenet and sets its pk.

        :py:attr:`customer_profile.user` is expected to have :py:attr:`email`, :py:attr:`first_name` and :py:attr:`last_name`.

        :param customer_profile: A customer profile with id set to :py:obj:`None`.
        :type customer_profile: ~terminusgps_payments.models.CustomerProfile
        :returns: The customer profile with an Authorizenet generated id as its pk.
        :rtype: ~terminusgps_payments.models.CustomerProfile

        """
        if not customer_profile.pk:
            user = customer_profile.user
            response = self.execute(
                api.create_customer_profile(
                    merchant_id=str(user.pk),
                    email=str(user.email),
                    description=f"{user.first_name} {user.last_name}",
                )
            )
            customer_profile.pk = int(response.customerProfileId)
        return customer_profile

    def get(
        self,
        customer_profile: models.CustomerProfile,
        include_issuer_info: bool = False,
    ) -> ObjectifiedElement | None:
        """
        Returns the customer profile from Authorizenet.

        :param customer_profile: A customer profile to retrieve from Authorizenet.
        :type customer_profile: ~terminusgps_payments.models.CustomerProfile
        :param include_issuer_info: Whether to include issuer info in the response. Default is :py:obj:`False`.
        :type include_issuer_info: bool
        :returns: A getCustomerProfileResponse from the Authorizenet API.
        :rtype: ~lxml.objectify.ObjectifiedElement | None

        """
        if customer_profile.pk:
            return self.execute(
                api.get_customer_profile(
                    customer_profile_id=customer_profile.pk,
                    include_issuer_info=include_issuer_info,
                )
            )

    def update(
        self,
        customer_profile: models.CustomerProfile,
        profile: apicontractsv1.customerProfileExType,
    ) -> models.CustomerProfile:
        """
        Updates the customer profile in Authorizenet.

        :param customer_profile: A customer profile to update in Authorizenet.
        :type customer_profile: ~terminusgps_payments.models.CustomerProfile
        :param profile: An Authorizenet profile element to update the customer profile with.
        :type profile: ~authorizenet.apicontractsv1.customerProfileExType
        :returns: The customer profile.
        :rtype: ~terminusgps_payments.models.CustomerProfile

        """
        if customer_profile.pk:
            profile.customerProfileId = customer_profile.pk
            self.execute(api.update_customer_profile(profile=profile))
        return customer_profile

    def delete(
        self, customer_profile: models.CustomerProfile
    ) -> models.CustomerProfile:
        """
        Deletes the customer profile in Authorizenet.

        Also sets :py:attr:`customer_profile.pk` to :py:obj:`None` before returning it.

        :param customer_profile: A customer profile to delete in Authorizenet.
        :type customer_profile: ~terminusgps_payments.models.CustomerProfile
        :returns: The customer profile.
        :rtype: ~terminusgps_payments.models.CustomerProfile

        """
        if customer_profile.pk:
            self.execute(
                api.delete_customer_profile(
                    customer_profile_id=customer_profile.pk
                )
            )
            customer_profile.pk = None
        return customer_profile


class AddressProfileService(AuthorizenetService):
    def create(
        self,
        address_profile: models.AddressProfile,
        address: apicontractsv1.customerAddressType,
        default: bool,
    ) -> models.AddressProfile:
        """
        Creates the address profile in Authorizenet.

        :param address_profile: An address profile with id set to :py:obj:`None`.
        :type address_profile: ~terminusgps_payments.models.AddressProfile
        :param address: An Authorizenet address element.
        :type address: ~authorizenet.apicontractsv1.customerAddressType
        :param default: Whether to set the address profile as default.
        :type default: bool
        :returns: The address profile with an Authorizenet generated id as its pk.
        :rtype: ~terminusgps_payments.models.AddressProfile

        """
        if not address_profile.pk and address_profile.customer_profile.pk:
            response = self.execute(
                api.create_customer_shipping_address(
                    customer_profile_id=address_profile.customer_profile.pk,
                    address=address,
                    default=default,
                )
            )
            address_profile.pk = int(response.customerAddressId)
        return address_profile

    def get(
        self, address_profile: models.AddressProfile
    ) -> ObjectifiedElement | None:
        """
        Returns the address profile from Authorizenet.

        :param address_profile: An address profile to retrieve from Authorizenet.
        :type address_profile: ~terminusgps_payments.models.AddressProfile
        :returns: A getCustomerShippingAddressResponse from the Authorizenet API.
        :rtype: ~lxml.objectify.ObjectifiedElement | None

        """
        if address_profile.pk and address_profile.customer_profile.pk:
            return self.execute(
                api.get_customer_shipping_address(
                    customer_profile_id=address_profile.customer_profile.pk,
                    address_profile_id=address_profile.pk,
                )
            )

    def update(
        self,
        address_profile: models.AddressProfile,
        address: apicontractsv1.customerAddressType,
        default: bool,
    ) -> models.AddressProfile:
        """
        Updates the address profile in Authorizenet.

        :param address_profile: An address profile.
        :type address_profile: ~terminusgps_payments.models.AddressProfile
        :param address: An Authorizenet customer address element to update the address profile with.
        :type address: ~authorizenet.apicontractsv1.customerAddressType
        :param default: Whether to set the address profile as default.
        :type default: bool
        :returns: The address profile.
        :rtype: ~terminusgps_payments.models.AddressProfile

        """
        if address_profile.pk and address_profile.customer_profile.pk:
            self.execute(
                api.update_customer_shipping_address(
                    customer_profile_id=address_profile.customer_profile.pk,
                    address=address,
                    default=default,
                )
            )
        return address_profile

    def delete(
        self, address_profile: models.AddressProfile
    ) -> models.AddressProfile:
        """
        Deletes the address profile in Authorizenet.

        Also sets :py:attr:`address_profile.pk` to :py:obj:`None` before returning it.

        :param address_profile: An address profile.
        :type address_profile: ~terminusgps_payments.models.AddressProfile
        :returns: The address profile.
        :rtype: ~terminusgps_payments.models.AddressProfile

        """
        if address_profile.pk and address_profile.customer_profile.pk:
            self.execute(
                api.delete_customer_shipping_address(
                    customer_profile_id=address_profile.customer_profile.pk,
                    address_profile_id=address_profile.pk,
                )
            )
        return address_profile


class PaymentProfileService(AuthorizenetService):
    def create(
        self,
        payment_profile: models.PaymentProfile,
        address: apicontractsv1.customerAddressType,
        credit_card: apicontractsv1.creditCardType,
        default: bool,
    ) -> models.PaymentProfile:
        """
        Creates a payment profile in Authorizenet.

        :param payment_profile: A payment profile.
        :type payment_profile: ~terminusgps_payments.models.PaymentProfile
        :param address: A customer address.
        :type address: ~authorizenet.apicontractsv1.customerAddressType
        :param credit_card: A credit card.
        :type credit_card: ~authorizenet.apicontractsv1.creditCardType
        :param default: Whether to set the payment profile as default.
        :type default: bool
        :returns: The payment profile with an Authorizenet id.
        :rtype: ~terminusgps_payments.models.PaymentProfile

        """
        if not payment_profile.pk and payment_profile.customer_profile.pk:
            response = self.execute(
                api.create_customer_payment_profile(
                    customer_profile_id=payment_profile.customer_profile.pk,
                    payment=apicontractsv1.paymentType(creditCard=credit_card),
                    address=address,
                    default=default,
                    validation=settings.MERCHANT_AUTH_VALIDATION_MODE,
                )
            )
            payment_profile.pk = int(response.customerPaymentProfileId)
        return payment_profile

    def get(
        self,
        payment_profile: models.PaymentProfile,
        include_issuer_info: bool = False,
    ) -> ObjectifiedElement | None:
        """
        Returns the payment profile from Authorizenet.

        :param payment_profile: A payment profile.
        :type payment_profile: ~terminusgps_payments.models.PaymentProfile
        :param include_issuer_info: Whether to include issuer info in the response. Default is :py:obj:`False`.
        :type include_issuer_info: bool
        :returns: A getCustomerPaymentProfileResponse from the Authorizenet API.
        :rtype: ~lxml.objectify.ObjectifiedElement | None

        """
        if payment_profile.pk and payment_profile.customer_profile.pk:
            return self.execute(
                api.get_customer_payment_profile(
                    customer_profile_id=payment_profile.customer_profile.pk,
                    payment_profile_id=payment_profile.pk,
                    include_issuer_info=include_issuer_info,
                )
            )

    def update(
        self,
        payment_profile: models.PaymentProfile,
        address: apicontractsv1.customerAddressType,
        credit_card: apicontractsv1.creditCardType,
        default: bool,
    ) -> models.PaymentProfile:
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
        :returns: The payment profile.
        :rtype: ~terminusgps_payments.models.PaymentProfile

        """
        if payment_profile.pk and payment_profile.customer_profile.pk:
            self.execute(
                api.update_customer_payment_profile(
                    customer_profile_id=payment_profile.customer_profile.pk,
                    payment_profile_id=payment_profile.pk,
                    payment=apicontractsv1.paymentType(creditCard=credit_card),
                    address=address,
                    default=default,
                    validation=settings.MERCHANT_AUTH_VALIDATION_MODE,
                )
            )
        return payment_profile

    def delete(
        self, payment_profile: models.PaymentProfile
    ) -> models.PaymentProfile:
        """
        Deletes the payment profile in Authorizenet.

        Also sets :py:attr:`payment_profile.pk` to :py:obj:`None` before returning it.

        :param payment_profile: A payment profile.
        :type payment_profile: ~terminusgps_payments.models.PaymentProfile
        :returns: The payment profile.
        :rtype: ~terminusgps_payments.models.PaymentProfile

        """
        if payment_profile.pk and payment_profile.customer_profile.pk:
            self.execute(
                api.delete_customer_payment_profile(
                    customer_profile_id=payment_profile.customer_profile.pk,
                    payment_profile_id=payment_profile.pk,
                )
            )
        return payment_profile


class SubscriptionService(AuthorizenetService):
    def create(
        self,
        subscription: models.Subscription,
        subscription_obj: apicontractsv1.ARBSubscriptionType,
    ) -> models.Subscription:
        if not subscription.pk:
            response = self.execute(
                api.create_subscription(subscription=subscription_obj)
            )
            subscription.pk = int(response.subscriptionId)
        return subscription

    def get(
        self,
        subscription: models.Subscription,
        include_transactions: bool = False,
    ) -> ObjectifiedElement | None:
        if subscription.pk:
            return self.execute(
                api.get_subscription(
                    subscription_id=subscription.pk,
                    include_transactions=include_transactions,
                )
            )

    def update(
        self,
        subscription: models.Subscription,
        subscription_obj: apicontractsv1.ARBSubscriptionType,
    ) -> models.Subscription:
        if subscription.pk:
            self.execute(
                api.update_subscription(
                    subscription_id=subscription.pk,
                    subscription=subscription_obj,
                )
            )
        return subscription

    def delete(self, subscription: models.Subscription) -> models.Subscription:
        if subscription.pk:
            self.execute(
                api.cancel_subscription(subscription_id=subscription.pk)
            )
            subscription.pk = None
        return subscription
