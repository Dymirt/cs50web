from django.contrib import admin
from .models import Counter, Reading

# Register your models here.
admin.site.register(Reading)


@admin.register(Counter)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("title", "user")
