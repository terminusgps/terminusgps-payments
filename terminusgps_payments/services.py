from authorizenet import apicontractsv1
from django.conf import settings
from lxml.objectify import ObjectifiedElement
from terminusgps.authorizenet import api
from terminusgps.authorizenet.service import AuthorizenetService

from terminusgps_payments import models


class CustomerProfileService(AuthorizenetService):
    def create(
        self, customer_profile: models.CustomerProfile
    ) -> tuple[models.CustomerProfile, ObjectifiedElement | None]:
        """
        Creates the customer profile in Authorizenet.

        :py:attr:`customer_profile.user` is expected to have :py:attr:`email`, :py:attr:`first_name` and :py:attr:`last_name`.

        :param customer_profile: A customer profile with no :py:attr:`pk` set.
        :type customer_profile: ~terminusgps_payments.models.CustomerProfile
        :returns: A tuple containing the customer profile and an Authorizenet API response.
        :rtype: tuple[~terminusgps_payments.models.CustomerProfile, ~lxml.objectify.ObjectifiedElement | None]

        """
        if customer_profile.pk:
            return customer_profile, None
        return customer_profile, self.execute(
            api.create_customer_profile(
                merchant_id=str(customer_profile.user.pk),
                email=str(customer_profile.user.email),
                description=f"{customer_profile.user.first_name} {customer_profile.user.last_name}",
            )
        )

    def get(
        self,
        customer_profile: models.CustomerProfile,
        include_issuer_info: bool = False,
    ) -> tuple[models.CustomerProfile, ObjectifiedElement | None]:
        """
        Returns the customer profile from Authorizenet.

        :param customer_profile: A customer profile.
        :type customer_profile: ~terminusgps_payments.models.CustomerProfile
        :param include_issuer_info: Whether to include issuer info in the response. Default is :py:obj:`False`.
        :type include_issuer_info: bool
        :returns: A tuple containing the customer profile and an Authorizenet API response.
        :rtype: tuple[~terminusgps_payments.models.CustomerProfile, ~lxml.objectify.ObjectifiedElement | None]

        """
        if not customer_profile.pk:
            return customer_profile, None
        return customer_profile, self.execute(
            api.get_customer_profile(
                customer_profile_id=customer_profile.pk,
                include_issuer_info=include_issuer_info,
            )
        )

    def update(
        self,
        customer_profile: models.CustomerProfile,
        profile: apicontractsv1.customerProfileExType,
    ) -> tuple[models.CustomerProfile, ObjectifiedElement | None]:
        """
        Updates the customer profile in Authorizenet.

        :param customer_profile: A customer profile.
        :type customer_profile: ~terminusgps_payments.models.CustomerProfile
        :param profile: An Authorizenet profile element to update the customer profile with.
        :type profile: ~authorizenet.apicontractsv1.customerProfileExType
        :returns: A tuple containing the customer profile and an Authorizenet API response.
        :rtype: tuple[~terminusgps_payments.models.CustomerProfile, ~lxml.objectify.ObjectifiedElement | None]

        """
        if not customer_profile.pk:
            return customer_profile, None
        profile.customerProfileId = customer_profile.pk
        return customer_profile, self.execute(
            api.update_customer_profile(profile=profile)
        )

    def delete(
        self, customer_profile: models.CustomerProfile
    ) -> tuple[models.CustomerProfile, ObjectifiedElement | None]:
        """
        Deletes the customer profile in Authorizenet.

        :param customer_profile: A customer profile.
        :type customer_profile: ~terminusgps_payments.models.CustomerProfile
        :returns: A tuple containing the customer profile and an Authorizenet API response.
        :rtype: tuple[~terminusgps_payments.models.CustomerProfile, ~lxml.objectify.ObjectifiedElement | None]

        """
        if not customer_profile.pk:
            return customer_profile, None
        return customer_profile, self.execute(
            api.delete_customer_profile(
                customer_profile_id=customer_profile.pk
            )
        )


class AddressProfileService(AuthorizenetService):
    def create(
        self,
        address_profile: models.AddressProfile,
        address: apicontractsv1.customerAddressType,
        default: bool,
    ) -> tuple[models.AddressProfile, ObjectifiedElement | None]:
        """
        Creates the address profile in Authorizenet.

        :param address_profile: An address profile with no :py:attr:`pk` set.
        :type address_profile: ~terminusgps_payments.models.AddressProfile
        :param address: An Authorizenet address element.
        :type address: ~authorizenet.apicontractsv1.customerAddressType
        :param default: Whether to set the address profile as default.
        :type default: bool
        :returns: A tuple containing the address profile and an Authorizenet API response.
        :rtype: tuple[~terminusgps_payments.models.AddressProfile, ~lxml.objectify.ObjectifiedElement | None]

        """
        if address_profile.pk or not hasattr(
            address_profile, "customer_profile"
        ):
            return address_profile, None
        return address_profile, self.execute(
            api.create_customer_shipping_address(
                customer_profile_id=address_profile.customer_profile.pk,
                address=address,
                default=default,
            )
        )

    def get(
        self, address_profile: models.AddressProfile
    ) -> tuple[models.AddressProfile, ObjectifiedElement | None]:
        """
        Gets the address profile from Authorizenet.

        :param address_profile: An address profile.
        :type address_profile: ~terminusgps_payments.models.AddressProfile
        :returns: A tuple containing the address profile and an Authorizenet API response.
        :rtype: tuple[~terminusgps_payments.models.AddressProfile, ~lxml.objectify.ObjectifiedElement | None]

        """
        if not address_profile.pk or not hasattr(
            address_profile, "customer_profile"
        ):
            return address_profile, None
        return address_profile, self.execute(
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
    ) -> tuple[models.AddressProfile, ObjectifiedElement | None]:
        """
        Updates the address profile in Authorizenet.

        :param address_profile: An address profile.
        :type address_profile: ~terminusgps_payments.models.AddressProfile
        :param address: An Authorizenet customer address element to update the address profile with.
        :type address: ~authorizenet.apicontractsv1.customerAddressType
        :param default: Whether to set the address profile as default.
        :type default: bool
        :returns: A tuple containing the address profile and an Authorizenet API response.
        :rtype: tuple[~terminusgps_payments.models.AddressProfile, ~lxml.objectify.ObjectifiedElement | None]

        """
        if not address_profile.pk or not hasattr(
            address_profile, "customer_profile"
        ):
            return address_profile, None
        return address_profile, self.execute(
            api.update_customer_shipping_address(
                customer_profile_id=address_profile.customer_profile.pk,
                address=address,
                default=default,
            )
        )

    def delete(
        self, address_profile: models.AddressProfile
    ) -> tuple[models.AddressProfile, ObjectifiedElement | None]:
        """
        Deletes the address profile in Authorizenet.

        :param address_profile: An address profile.
        :type address_profile: ~terminusgps_payments.models.AddressProfile
        :returns: A tuple containing the address profile and an Authorizenet API response.
        :rtype: tuple[~terminusgps_payments.models.AddressProfile, ~lxml.objectify.ObjectifiedElement | None]

        """
        if not address_profile.pk or not hasattr(
            address_profile, "customer_profile"
        ):
            return address_profile, None
        return address_profile, self.execute(
            api.delete_customer_shipping_address(
                customer_profile_id=address_profile.customer_profile.pk,
                address_profile_id=address_profile.pk,
            )
        )


class PaymentProfileService(AuthorizenetService):
    def create(
        self,
        payment_profile: models.PaymentProfile,
        address: apicontractsv1.customerAddressType,
        credit_card: apicontractsv1.creditCardType,
        default: bool,
    ) -> tuple[models.PaymentProfile, ObjectifiedElement | None]:
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
        :returns: A tuple containing the payment profile and an Authorizenet API response.
        :rtype: tuple[~terminusgps_payments.models.PaymentProfile, ~lxml.objectify.ObjectifiedElement | None]

        """
        if payment_profile.pk or not hasattr(
            payment_profile, "customer_profile"
        ):
            return payment_profile, None
        return payment_profile, self.execute(
            api.create_customer_payment_profile(
                customer_profile_id=payment_profile.customer_profile.pk,
                payment=apicontractsv1.paymentType(creditCard=credit_card),
                address=address,
                default=default,
                validation=settings.MERCHANT_AUTH_VALIDATION_MODE,
            )
        )

    def get(
        self,
        payment_profile: models.PaymentProfile,
        include_issuer_info: bool = False,
    ) -> tuple[models.PaymentProfile, ObjectifiedElement | None]:
        """
        Returns the payment profile from Authorizenet.

        :param payment_profile: A payment profile.
        :type payment_profile: ~terminusgps_payments.models.PaymentProfile
        :param include_issuer_info: Whether to include issuer info in the response. Default is :py:obj:`False`.
        :type include_issuer_info: bool
        :returns: A tuple containing the payment profile and an Authorizenet API response.
        :rtype: tuple[~terminusgps_payments.models.PaymentProfile, ~lxml.objectify.ObjectifiedElement | None]

        """
        if not payment_profile.pk or not hasattr(
            payment_profile, "customer_profile"
        ):
            return payment_profile, None
        return payment_profile, self.execute(
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
    ) -> tuple[models.PaymentProfile, ObjectifiedElement | None]:
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
        :returns: A tuple containing the payment profile and an Authorizenet API response.
        :rtype: tuple[~terminusgps_payments.models.PaymentProfile, ~lxml.objectify.ObjectifiedElement | None]

        """
        if not payment_profile.pk or not hasattr(
            payment_profile, "customer_profile"
        ):
            return payment_profile, None
        return payment_profile, self.execute(
            api.update_customer_payment_profile(
                customer_profile_id=payment_profile.customer_profile.pk,
                payment_profile_id=payment_profile.pk,
                payment=apicontractsv1.paymentType(creditCard=credit_card),
                address=address,
                default=default,
                validation=settings.MERCHANT_AUTH_VALIDATION_MODE,
            )
        )

    def delete(
        self, payment_profile: models.PaymentProfile
    ) -> tuple[models.PaymentProfile, ObjectifiedElement | None]:
        """
        Deletes the payment profile in Authorizenet.

        :param payment_profile: A payment profile.
        :type payment_profile: ~terminusgps_payments.models.PaymentProfile
        :returns: A tuple containing the payment profile and an Authorizenet API response.
        :rtype: tuple[~terminusgps_payments.models.PaymentProfile, ~lxml.objectify.ObjectifiedElement | None]

        """
        if not payment_profile.pk or not hasattr(
            payment_profile, "customer_profile"
        ):
            return payment_profile, None
        return payment_profile, self.execute(
            api.delete_customer_payment_profile(
                customer_profile_id=payment_profile.customer_profile.pk,
                payment_profile_id=payment_profile.pk,
            )
        )


class SubscriptionService(AuthorizenetService):
    def create(
        self,
        subscription: models.Subscription,
        subscription_obj: apicontractsv1.ARBSubscriptionType,
    ) -> tuple[models.Subscription, ObjectifiedElement | None]:
        """
        Creates a subscription in Authorizenet.

        :param subscription: A subscription.
        :type subscription: ~terminusgps_payments.models.Subscription
        :param subscription_obj: An Authorizenet ARBSubscriptionType element.
        :type subscription_obj: ~authorizenet.apicontractsv1.customerAddressType
        :returns: A tuple containing the subscription and an Authorizenet API response.
        :rtype: tuple[~terminusgps_payments.models.Subscription, ~lxml.objectify.ObjectifiedElement | None]

        """
        if subscription.pk:
            return subscription, None
        return subscription, self.execute(
            api.create_subscription(subscription=subscription_obj)
        )

    def get(
        self,
        subscription: models.Subscription,
        include_transactions: bool = False,
    ) -> tuple[models.Subscription, ObjectifiedElement | None]:
        """
        Gets a subscription from Authorizenet.

        :param subscription: A subscription.
        :type subscription: ~terminusgps_payments.models.Subscription
        :returns: A tuple containing the subscription and an Authorizenet API response.
        :rtype: tuple[~terminusgps_payments.models.Subscription, ~lxml.objectify.ObjectifiedElement | None]

        """
        if not subscription.pk:
            return subscription, None
        return subscription, self.execute(
            api.get_subscription(
                subscription_id=subscription.pk,
                include_transactions=include_transactions,
            )
        )

    def update(
        self,
        subscription: models.Subscription,
        subscription_obj: apicontractsv1.ARBSubscriptionType,
    ) -> tuple[models.Subscription, ObjectifiedElement | None]:
        """
        Updates a subscription in Authorizenet.

        :param subscription: A subscription.
        :type subscription: ~terminusgps_payments.models.Subscription
        :param subscription_obj: An Authorizenet ARBSubscriptionType element.
        :type subscription_obj: ~authorizenet.apicontractsv1.customerAddressType
        :returns: A tuple containing the subscription and an Authorizenet API response.
        :rtype: tuple[~terminusgps_payments.models.Subscription, ~lxml.objectify.ObjectifiedElement | None]

        """
        if not subscription.pk:
            return subscription, None
        return subscription, self.execute(
            api.update_subscription(
                subscription_id=subscription.pk, subscription=subscription_obj
            )
        )

    def delete(
        self, subscription: models.Subscription
    ) -> tuple[models.Subscription, ObjectifiedElement | None]:
        """
        Deletes a subscription in Authorizenet.

        :param subscription: A subscription.
        :type subscription: ~terminusgps_payments.models.Subscription
        :returns: A tuple containing the subscription and an Authorizenet API response.
        :rtype: tuple[~terminusgps_payments.models.Subscription, ~lxml.objectify.ObjectifiedElement | None]

        """
        if not subscription.pk:
            return subscription, None
        return subscription, self.execute(
            api.cancel_subscription(subscription_id=subscription.pk)
        )
