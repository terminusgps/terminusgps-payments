from django.tasks import task
from terminusgps.authorizenet.service import AuthorizenetService

from .models import (
    CustomerAddressProfile,
    CustomerPaymentProfile,
    CustomerProfile,
)


@task
def sync_customer_profile_with_authorizenet(pk):
    customer_profile = CustomerProfile.objects.get(pk=pk)
    service = AuthorizenetService()
    data = customer_profile.pull(service, reference_id=None)
    if hasattr(data, "profile"):
        address_qs = CustomerAddressProfile.objects.filter(
            customer_profile=customer_profile
        )
        payment_qs = CustomerPaymentProfile.objects.filter(
            customer_profile=customer_profile
        )
        if not hasattr(data.profile, "shipToList"):
            address_qs.delete()
        else:
            address_ids = [
                int(profile.customerAddressId)
                for profile in data.profile.shipToList
            ]
            for id in address_ids:
                address_profile = CustomerAddressProfile()
                address_profile.pk = id
                address_profile.customer_profile = customer_profile
                address_profile.save(push=False)
            address_qs.exclude(id__in=address_ids).delete()
        if not hasattr(data.profile, "paymentProfiles"):
            payment_qs.delete()
        else:
            payment_ids = [
                int(profile.customerPaymentProfileId)
                for profile in data.profile.paymentProfiles
            ]
            for pk in payment_ids:
                payment_profile = CustomerPaymentProfile()
                payment_profile.pk = pk
                payment_profile.customer_profile = customer_profile
                payment_profile.save(push=False)
            payment_qs.exclude(id__in=payment_ids).delete()
