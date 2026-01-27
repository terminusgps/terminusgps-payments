from lxml.objectify import ObjectifiedElement
from terminusgps.authorizenet.service import AuthorizenetService

from .models import (
    CustomerAddressProfile,
    CustomerPaymentProfile,
    CustomerProfile,
)


def sync_customer_subprofile(
    customer_profile: CustomerProfile,
    anet_data: ObjectifiedElement,
    model: type[CustomerAddressProfile] | type[CustomerPaymentProfile],
) -> None:
    """Syncs customer payment/address profiles for the provided customer profile with Authorizenet."""
    if model == CustomerAddressProfile:
        list_attr = "shipToList"
        id_attr = "customerAddressId"
    elif model == CustomerPaymentProfile:
        list_attr = "paymentProfiles"
        id_attr = "customerPaymentProfileId"
    else:
        raise ValueError(f"Invalid model: '{model}'.")

    if hasattr(anet_data, "profile"):
        qs = model.objects.filter(customer_profile=customer_profile)
        if not hasattr(anet_data.profile, list_attr):
            qs.delete()
        else:
            ids = [
                int(getattr(subprofile, id_attr))
                for subprofile in getattr(anet_data.profile, list_attr)
            ]
            for id in ids:
                obj = model()
                obj.pk = id
                obj.customer_profile = customer_profile
                obj.save(push=False)
            qs.exclude(id__in=ids).delete()


def sync_customer_profile(pk: int) -> None:
    """Syncs a customer profile with Authorizenet by primary key."""
    service = AuthorizenetService()
    customer_profile = CustomerProfile.objects.get(pk=pk)
    anet_data = customer_profile.pull(service, reference_id=None)
    sync_customer_subprofile(
        customer_profile=customer_profile,
        anet_data=anet_data,
        model=CustomerPaymentProfile,
    )
    sync_customer_subprofile(
        customer_profile=customer_profile,
        anet_data=anet_data,
        model=CustomerAddressProfile,
    )
