from django.contrib import admin
from .models import Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'location_type',
        'city',
        'contact_person',
        'phone',
        'is_active',
    )

    list_filter = (
        'location_type',
        'city',
        'is_active',
    )

    search_fields = (
        'name',
        'city',
        'contact_person',
        'phone',
    )

    ordering = (
        'name',
    )