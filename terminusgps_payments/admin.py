from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext

from . import models, tasks


@admin.register(models.CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ["merchant_id"]
    actions = ["queue_authorizenet_sync"]

    @admin.action(
        description=_("Sync selected customer profiles with Authorizenet")
    )
    def queue_authorizenet_sync(self, request, queryset):
        for customer_profile in queryset:
            tasks.sync_customer_profile_with_authorizenet.enqueue(
                customer_profile.pk
            )
        self.message_user(
            request,
            ngettext(
                _("%d customer profile syncronization was started."),
                _("%d customer profile syncronizations were started."),
                len(queryset),
            )
            % len(queryset),
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
