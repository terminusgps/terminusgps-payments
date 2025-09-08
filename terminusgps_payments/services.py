from terminusgps.authorizenet import api

from terminusgps_payments import models


def authorizenet_get_customer_profile(
    customer_profile: models.CustomerProfile,
):
    if customer_profile_id := customer_profile.pk:
        return api.get_customer_profile(
            customer_profile_id=customer_profile_id
        )


def authorizenet_get_payment_profile(
    payment_profile: models.PaymentProfile, include_issuer_info: bool = False
):
    customer_profile_id = payment_profile.customer_profile.pk
    payment_profile_id = payment_profile.pk

    if customer_profile_id and payment_profile_id:
        return api.get_customer_payment_profile(
            customer_profile_id=customer_profile_id,
            payment_profile_id=payment_profile_id,
            include_issuer_info=include_issuer_info,
        )
