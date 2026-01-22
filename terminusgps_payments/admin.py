from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext
from terminusgps.authorizenet.service import AuthorizenetService

from . import models


@admin.register(models.CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ["merchant_id"]
    actions = ["sync_addresses", "sync_payments"]

    @admin.action(
        description=_(
            "Sync selected customer address profiles with Authorizenet"
        )
    )
    def sync_addresses(self, request, queryset):
        synced = []
        service = AuthorizenetService()
        for customer_profile in queryset:
            data = customer_profile.pull(service)
            if addresses := getattr(data.profile, "shipToList", None):
                for address in addresses:
                    address_profile = models.CustomerAddressProfile()
                    address_profile.pk = int(address.customerAddressId)
                    address_profile.customer_profile = customer_profile
                    address_profile.save(push=False)
                    synced.append(address_profile)
        self.message_user(
            request,
            ngettext(
                _("%d address profile was synced."),
                _("%d address profiles were synced."),
                len(synced),
            )
            % len(synced),
            messages.SUCCESS,
        )
        return

    @admin.action(
        description=_(
            "Sync selected customer payment profiles with Authorizenet"
        )
    )
    def sync_payments(self, request, queryset):
        synced = []
        service = AuthorizenetService()
        for customer_profile in queryset:
            data = customer_profile.pull(service)
            if payments := getattr(data.profile, "paymentProfiles", None):
                for payment in payments:
                    payment_profile = models.CustomerPaymentProfile()
                    payment_profile.pk = int(payment.customerPaymentProfileId)
                    payment_profile.customer_profile = customer_profile
                    payment_profile.save(push=False)
                    synced.append(payment_profile)
        self.message_user(
            request,
            ngettext(
                _("%d payment profile was synced."),
                _("%d payment profiles were synced."),
                len(synced),
            )
            % len(synced),
            messages.SUCCESS,
        )
        return


@admin.register(models.CustomerPaymentProfile)
class CustomerPaymentProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "customer_profile__merchant_id"]


@admin.register(models.CustomerAddressProfile)
class CustomerAddressProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "customer_profile__merchant_id"]


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "amount",
        "status",
        "customer_profile__merchant_id",
    ]
    list_filter = ["status"]
