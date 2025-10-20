import logging

from terminusgps.authorizenet.constants import SubscriptionStatus
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
            if address_profile.pk and hasattr(
                address_profile, "customer_profile"
            ):
                service.delete_address_profile(address_profile)
    except (AuthorizenetControllerExecutionError, ValueError) as e:
        if hasattr(e, "code"):
            if getattr(e, "code") == "E00040":
                # Already gone in Authorizenet
                return
        logger.critical(e)
        raise


def delete_payment_profile_in_authorizenet(sender, **kwargs):
    try:
        if payment_profile := kwargs.get("instance"):
            if payment_profile.pk and hasattr(
                payment_profile, "customer_profile"
            ):
                service.delete_payment_profile(payment_profile)
    except (AuthorizenetControllerExecutionError, ValueError) as e:
        if hasattr(e, "code"):
            if getattr(e, "code") == "E00040":
                # Already gone in Authorizenet
                return
        logger.critical(e)
        raise


def delete_customer_profile_in_authorizenet(sender, **kwargs):
    try:
        if customer_profile := kwargs.get("instance"):
            if customer_profile.pk:
                service.delete_customer_profile(customer_profile)
    except (AuthorizenetControllerExecutionError, ValueError) as e:
        if hasattr(e, "code"):
            if getattr(e, "code") == "E00040":
                # Already gone in Authorizenet
                return
        logger.critical(e)
        raise


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
            if payment_profile.pk is not None and any(
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


def hydrate_subscription_status(sender, **kwargs):
    try:
        if subscription := kwargs.get("instance"):
            if (
                subscription.pk is not None
                and subscription.status == SubscriptionStatus.UNKNOWN
            ):
                anet_response = service.get_subscription_status(subscription)
                subscription.status = getattr(anet_response, "status")
                subscription.save(update_fields=["status"])
    except (AuthorizenetControllerExecutionError, ValueError) as e:
        logger.critical(e)
        raise


def get_or_create_customer_profile_for_user(sender, **kwargs):
    try:
        if user := kwargs.get("instance"):
            if hasattr(user, "email") and not hasattr(
                user, "customer_profile"
            ):
                try:
                    anet_response = service.get_customer_profile_by_user(user)
                    customer_profile = CustomerProfile(
                        pk=anet_response.profile.customerProfileId, user=user
                    )
                    customer_profile.save()
                except AuthorizenetControllerExecutionError as e:
                    if e.code != "E00040":
                        raise
                    customer_profile = CustomerProfile(user=user)
                    anet_response = service.create_customer_profile(
                        customer_profile
                    )
                    customer_profile.pk = anet_response.customerProfileId
                    customer_profile.save()
    except (AuthorizenetControllerExecutionError, ValueError) as e:
        logger.critical(e)
