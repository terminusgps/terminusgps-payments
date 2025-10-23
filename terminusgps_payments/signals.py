import logging

from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
)

from terminusgps_payments.models import CustomerProfile
from terminusgps_payments.services import AuthorizenetService

logger = logging.getLogger(__name__)
service = AuthorizenetService()


def delete_address_profile_in_authorizenet(sender, **kwargs):
    try:
        if address_profile := kwargs.get("instance"):
            if pk := address_profile.pk and hasattr(
                address_profile, "customer_profile"
            ):
                logger.debug(
                    f"Deleting AddressProfile #{pk} in Authorizenet..."
                )
                service.delete_address_profile(address_profile)
                logger.info(
                    f"Successfully deleted AddressProfile #{pk} in Authorizenet."
                )
    except (AuthorizenetControllerExecutionError, ValueError) as e:
        if hasattr(e, "code"):
            if getattr(e, "code") == "E00040":
                logger.info(
                    f"AddressProfile #{pk} was already deleted in Authorizenet."
                )
                return
        logger.critical(e)
        raise


def delete_payment_profile_in_authorizenet(sender, **kwargs):
    try:
        if payment_profile := kwargs.get("instance"):
            if pk := payment_profile.pk and hasattr(
                payment_profile, "customer_profile"
            ):
                logger.debug(
                    f"Deleting PaymentProfile #{pk} in Authorizenet..."
                )
                service.delete_payment_profile(payment_profile)
                logger.info(
                    f"Successfully deleted PaymentProfile #{pk} in Authorizenet."
                )
    except (AuthorizenetControllerExecutionError, ValueError) as e:
        if hasattr(e, "code"):
            if getattr(e, "code") == "E00040":
                logger.info(
                    f"PaymentProfile #{pk} was already deleted in Authorizenet."
                )
                return
        logger.critical(e)
        raise


def delete_customer_profile_in_authorizenet(sender, **kwargs):
    try:
        if customer_profile := kwargs.get("instance"):
            if pk := customer_profile.pk:
                logger.debug(
                    f"Deleting CustomerProfile #{pk} in Authorizenet..."
                )
                service.delete_customer_profile(customer_profile)
                logger.info(
                    f"Successfully deleted CustomerProfile #{pk} in Authorizenet."
                )
    except (AuthorizenetControllerExecutionError, ValueError) as e:
        if hasattr(e, "code"):
            if getattr(e, "code") == "E00040":
                # Already gone in Authorizenet
                logger.info(
                    f"CustomerProfile #{pk} was already deleted in Authorizenet."
                )
                return
        logger.critical(e)
        raise


def hydrate_address_profile(sender, **kwargs):
    try:
        if address_profile := kwargs.get("instance"):
            if (
                pk := address_profile.pk
                and address_profile.address is not None
            ):
                logger.info(
                    f"Hydrating AddressProfile #{pk} with Authorizenet..."
                )

                resp = service.get_address_profile(address_profile)
                address_profile.address = getattr(resp, "address")
                address_profile.save(update_fields=["address"])

                logger.info(
                    f"Successfully hydrated AddressProfile #{pk} with Authorizenet."
                )
    except (AuthorizenetControllerExecutionError, ValueError) as e:
        logger.critical(e)
        raise


def hydrate_payment_profile(sender, **kwargs):
    try:
        if payment_profile := kwargs.get("instance"):
            if pk := payment_profile.pk and any(
                [
                    payment_profile.credit_card is None,
                    payment_profile.address is None,
                ]
            ):
                logger.info(
                    f"Hydrating PaymentProfile #{pk} with Authorizenet..."
                )
                resp = service.get_payment_profile(payment_profile)
                payment_profile.credit_card = getattr(
                    resp.paymentProfile.payment, "creditCard"
                )
                payment_profile.address = getattr(
                    resp.paymentProfile, "billTo"
                )
                payment_profile.save(update_fields=["credit_card", "address"])
                logger.info(
                    f"Successfully hydrated PaymentProfile #{pk} with Authorizenet."
                )
    except (AuthorizenetControllerExecutionError, ValueError) as e:
        logger.critical(e)
        raise


def hydrate_subscription_status(sender, **kwargs):
    try:
        if subscription := kwargs.get("instance"):
            if pk := subscription.pk:
                logger.info(
                    f"Hydrating Subscription #{pk} status with Authorizenet..."
                )
                resp = service.get_subscription_status(subscription)
                subscription.status = getattr(resp, "status")
                subscription.save(update_fields=["status"])
                logger.info(
                    f"Successfully hydrated Subscription #{pk} status with Authorizenet."
                )
    except (AuthorizenetControllerExecutionError, ValueError) as e:
        logger.critical(e)
        raise


def get_or_create_customer_profile_for_user(sender, **kwargs):
    try:
        if user := kwargs.get("instance"):
            if hasattr(user, "email") and not hasattr(
                user, "customer_profile"
            ):
                logger.info(
                    f"Getting/creating CustomerProfile for '{user}' from Authorizenet..."
                )
                customer_profile = CustomerProfile(user=user)
                try:
                    resp = service.get_customer_profile_by_user(user)
                    pk = int(getattr(resp.profile, "customerProfileId"))
                    customer_profile.pk = pk
                    customer_profile.save()
                    logger.info(
                        f"Successfully retrieved CustomerProfile #{pk} for '{user}' in Authorizenet."
                    )
                except AuthorizenetControllerExecutionError as e:
                    if e.code != "E00040":
                        raise
                    resp = service.create_customer_profile(customer_profile)
                    pk = int(getattr(resp, "customerProfileId"))
                    customer_profile.pk = pk
                    customer_profile.save()
                    logger.info(
                        f"Successfully created CustomerProfile #{pk} for '{user}' in Authorizenet."
                    )
    except (AuthorizenetControllerExecutionError, ValueError) as e:
        logger.critical(e)
        raise
