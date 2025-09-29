import logging

from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
)

from terminusgps_payments.services import AuthorizenetService

logger = logging.getLogger(__name__)
service = AuthorizenetService()


def hydrate_address_profile(sender, **kwargs):
    try:
        if address_profile := kwargs.get("instance"):
            if (
                address_profile.pk is not None
                and address_profile.address is None
            ):
                anet_response = service.get_address_profile(address_profile)
                address_profile.address = getattr(anet_response, "address")
                address_profile.save(update_fields=["address"])
    except (AuthorizenetControllerExecutionError, ValueError) as e:
        logger.critical(e)
        raise


def hydrate_payment_profile(sender, **kwargs):
    try:
        if payment_profile := kwargs.get("instance"):
            if payment_profile.pk is not None and all(
                [
                    payment_profile.credit_card is None,
                    payment_profile.address is None,
                ]
            ):
                anet_response = service.get_payment_profile(payment_profile)
                payment_profile.credit_card = getattr(
                    anet_response.paymentProfile.payment, "creditCard"
                )
                payment_profile.address = getattr(
                    anet_response.paymentProfile, "billTo"
                )
                payment_profile.save(update_fields=["credit_card", "address"])
    except (AuthorizenetControllerExecutionError, ValueError) as e:
        logger.critical(e)
        raise
