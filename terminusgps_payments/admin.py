from django.contrib import admin

from . import models


@admin.register(models.CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "user"]


@admin.register(models.CustomerPaymentProfile)
class CustomerPaymentProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "cprofile__user"]


@admin.register(models.CustomerAddressProfile)
class CustomerAddressProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "cprofile__user"]


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["id", "cprofile__user"]
