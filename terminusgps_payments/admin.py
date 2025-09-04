from django.contrib import admin

from . import models


@admin.register(models.CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "id"]


@admin.register(models.AddressProfile)
class AddressProfileAdmin(admin.ModelAdmin):
    list_display = ["customer_profile", "id"]


@admin.register(models.PaymentProfile)
class PaymentProfileAdmin(admin.ModelAdmin):
    list_display = ["customer_profile", "id"]


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        "customer_profile__user",
        "id",
        "payment_profile",
        "address_profile",
        "schedule",
    ]


@admin.register(models.SubscriptionSchedule)
class SubscriptionScheduleAdmin(admin.ModelAdmin):
    list_display = [
        "__str__",
        "interval",
        "start_date",
        "total_occurrences",
        "trial_occurrences",
    ]


@admin.register(models.SubscriptionScheduleInterval)
class SubscriptionScheduleIntervalAdmin(admin.ModelAdmin):
    list_display = ["name", "unit", "length"]
