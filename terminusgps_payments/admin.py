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
