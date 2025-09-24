from django.contrib import admin, messages
from django.utils.translation import ngettext
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
)

from . import models, services


@admin.register(models.CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "user"]


@admin.register(models.AddressProfile)
class AddressProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "customer_profile"]
    actions = ["hydrate_address_profiles"]

    @admin.action(
        description="Hydrate selected address profiles with Authorizenet"
    )
    def hydrate_address_profiles(self, request, queryset):
        service = services.AuthorizenetService()
        skipped = []
        hydrated = []

        for address_profile in queryset:
            try:
                anet_response = service.get_address_profile(address_profile)
                address_profile.address = anet_response.address
                address_profile.save()
                hydrated.append(address_profile)
            except AuthorizenetControllerExecutionError:
                skipped.append(address_profile)
        if len(skipped) > 0:
            self.message_user(
                request,
                ngettext(
                    "%d address profile was skipped.",
                    "%d address profiles were skipped.",
                    len(skipped),
                )
                % len(skipped),
                messages.WARNING,
            )
        if len(hydrated) > 0:
            self.message_user(
                request,
                ngettext(
                    "%d address profile was hydrated.",
                    "%d address profiles were hydrated.",
                    len(hydrated),
                )
                % len(hydrated),
                messages.SUCCESS,
            )


@admin.register(models.PaymentProfile)
class PaymentProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "customer_profile"]
    actions = ["hydrate_payment_profiles"]

    @admin.action(
        description="Hydrate selected payment profiles with Authorizenet"
    )
    def hydrate_payment_profiles(self, request, queryset):
        service = services.AuthorizenetService()
        skipped = []
        hydrated = []

        for payment_profile in queryset:
            try:
                anet_response = service.get_payment_profile(payment_profile)
                payment_profile.credit_card = (
                    anet_response.paymentProfile.payment.creditCard
                )
                payment_profile.address = anet_response.paymentProfile.billTo
                payment_profile.save()
                hydrated.append(payment_profile)
            except AuthorizenetControllerExecutionError:
                skipped.append(payment_profile)
        if len(skipped) > 0:
            self.message_user(
                request,
                ngettext(
                    "%d payment profile was skipped.",
                    "%d payment profiles were skipped.",
                    len(skipped),
                )
                % len(skipped),
                messages.WARNING,
            )
        if len(hydrated) > 0:
            self.message_user(
                request,
                ngettext(
                    "%d payment profile was hydrated.",
                    "%d payment profiles were hydrated.",
                    len(hydrated),
                )
                % len(hydrated),
                messages.SUCCESS,
            )


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "customer_profile",
        "payment_profile",
        "address_profile",
    ]
