from django.tasks import task
from terminusgps.authorizenet.service import AuthorizenetService

from .models import (
    CustomerAddressProfile,
    CustomerPaymentProfile,
    CustomerProfile,
)


@task
def sync_customer_profile_with_authorizenet(customer_profile: CustomerProfile):
    service = AuthorizenetService()
    data = customer_profile.pull(service, reference_id=None)
    if addresses := getattr(data.profile, "shipToList", None):
        for address in addresses:
            address_profile = CustomerAddressProfile()
            address_profile.pk = int(address.customerAddressId)
            address_profile.customer_profile = customer_profile
            address_profile.save(push=False)
    if payments := getattr(data.profile, "paymentProfiles", None):
        for payment in payments:
            payment_profile = CustomerPaymentProfile()
            payment_profile.pk = int(payment.customerPaymentProfileId)
            payment_profile.customer_profile = customer_profile
            payment_profile.save(push=False)
