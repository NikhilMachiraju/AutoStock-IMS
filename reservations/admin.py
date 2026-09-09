from django.contrib import admin
from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "vehicle",
        "status",
        "reservation_date",
        "expiry_date",
        "created_at",
    )

    list_filter = (
        "status",
        "reservation_date",
        "expiry_date",
    )

    search_fields = (
        "customer__first_name",
        "customer__last_name",
        "customer__phone",
        "vehicle__vin",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )