from django.contrib import admin
from .models import Counter, Reading, Price, Payment


@admin.register(Counter)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("title", "user")


@admin.register(Price)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("pk", "counter", "date", "price_per_unit", "price_per_month")


@admin.register(Reading)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("pk", "counter", "date", "value")


@admin.register(Payment)
class PersonAdmin(admin.ModelAdmin):
    list_display = (
        "counter",
        "reading",
        "amount",
    )
