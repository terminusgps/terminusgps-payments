from django.contrib import admin

from . import models


@admin.register(models.CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "merchant_id", "description"]


@admin.register(models.Subscription)
class Subscription(admin.ModelAdmin):
    list_display = ["customer_profile"]


@admin.register(models.SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ["name", "amount", "visibility", "description"]
    list_filter = ["visibility"]
    ordering = ["amount", "name"]
