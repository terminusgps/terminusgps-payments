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
        if not customer_profile.pk:
            user = customer_profile.user
            full_name = f"{user.first_name} {user.last_name}"
            response = self.execute(
                api.create_customer_profile(
                    merchant_id=str(user.pk),
                    email=user.email,
                    description=full_name,
                )
            )
            customer_profile.pk = int(response.customerProfileId)
        return customer_profile

    def get(
        self,
        customer_profile: models.CustomerProfile,
        include_issuer_info: bool = False,
    ) -> ObjectifiedElement | None:
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
        if customer_profile.pk:
            profile.customerProfileId = customer_profile.pk
            self.execute(api.update_customer_profile(profile=profile))
        return customer_profile

    def delete(
        self, customer_profile: models.CustomerProfile
    ) -> models.CustomerProfile:
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
        if payment_profile.pk and payment_profile.customer_profile.pk:
            self.execute(
                api.delete_customer_payment_profile(
                    customer_profile_id=payment_profile.customer_profile.pk,
                    payment_profile_id=payment_profile.pk,
                )
            )
        return payment_profile
