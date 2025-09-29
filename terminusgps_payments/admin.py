from django.contrib import admin

from . import models


@admin.register(models.CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "user"]


@admin.register(models.AddressProfile)
class AddressProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "customer_profile"]


@admin.register(models.PaymentProfile)
class PaymentProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "customer_profile"]


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "customer_profile",
        "payment_profile",
        "address_profile",
    ]
