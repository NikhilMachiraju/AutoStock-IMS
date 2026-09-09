from django.contrib import admin
from django.contrib import messages

from .models import Supplier, Purchase, PurchaseItem


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "contact_person",
        "phone",
        "email",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "contact_person",
        "phone",
        "email",
    )

    ordering = (
        "name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "purchase_number",
        "supplier",
        "purchase_date",
        "status",
        "invoice_number",
        "created_at",
    )

    list_filter = (
        "status",
        "purchase_date",
        "supplier",
    )

    search_fields = (
        "purchase_number",
        "invoice_number",
        "supplier__name",
    )

    ordering = (
        "-purchase_date",
        "-id",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    actions = (
        "mark_as_ordered",
        "mark_as_received",
        "mark_as_completed",
        "cancel_selected_purchases",
    )

    @admin.action(
        description="Mark selected purchases as Ordered"
    )
    def mark_as_ordered(self, request, queryset):
        success_count = 0
        error_count = 0

        for purchase in queryset:
            try:
                purchase.change_status("ORDERED")
                success_count += 1

            except Exception as exc:
                error_count += 1

                self.message_user(
                    request,
                    f"Could not order "
                    f"{purchase}: {exc}",
                    level=messages.ERROR,
                )

        if success_count:
            self.message_user(
                request,
                f"{success_count} purchase(s) marked as Ordered.",
                level=messages.SUCCESS,
            )

        if error_count:
            self.message_user(
                request,
                f"{error_count} purchase(s) could not be ordered.",
                level=messages.WARNING,
            )

    @admin.action(
        description="Mark selected purchases as Received"
    )
    def mark_as_received(self, request, queryset):
        success_count = 0
        error_count = 0

        for purchase in queryset:
            try:
                purchase.change_status("RECEIVED")
                success_count += 1

            except Exception as exc:
                error_count += 1

                self.message_user(
                    request,
                    f"Could not receive "
                    f"{purchase}: {exc}",
                    level=messages.ERROR,
                )

        if success_count:
            self.message_user(
                request,
                f"{success_count} purchase(s) marked as Received.",
                level=messages.SUCCESS,
            )

        if error_count:
            self.message_user(
                request,
                f"{error_count} purchase(s) could not be received.",
                level=messages.WARNING,
            )

    @admin.action(
        description="Mark selected purchases as Completed"
    )
    def mark_as_completed(self, request, queryset):
        success_count = 0
        error_count = 0

        for purchase in queryset:
            try:
                purchase.change_status("COMPLETED")
                success_count += 1

            except Exception as exc:
                error_count += 1

                self.message_user(
                    request,
                    f"Could not complete "
                    f"{purchase}: {exc}",
                    level=messages.ERROR,
                )

        if success_count:
            self.message_user(
                request,
                f"{success_count} purchase(s) marked as Completed.",
                level=messages.SUCCESS,
            )

        if error_count:
            self.message_user(
                request,
                f"{error_count} purchase(s) could not be completed.",
                level=messages.WARNING,
            )

    @admin.action(
        description="Cancel selected purchases"
    )
    def cancel_selected_purchases(self, request, queryset):
        success_count = 0
        error_count = 0

        for purchase in queryset:
            try:
                purchase.change_status("CANCELLED")
                success_count += 1

            except Exception as exc:
                error_count += 1

                self.message_user(
                    request,
                    f"Could not cancel "
                    f"{purchase}: {exc}",
                    level=messages.ERROR,
                )

        if success_count:
            self.message_user(
                request,
                f"{success_count} purchase(s) cancelled.",
                level=messages.SUCCESS,
            )

        if error_count:
            self.message_user(
                request,
                f"{error_count} purchase(s) could not be cancelled.",
                level=messages.WARNING,
            )


@admin.register(PurchaseItem)
class PurchaseItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "purchase",
        "vehicle",
        "vehicle_status",
        "purchase_price",
        "created_at",
    )

    list_filter = (
        "purchase__status",
        "vehicle__status",
        "purchase",
    )

    search_fields = (
        "purchase__purchase_number",
        "vehicle__vin_number",
        "vehicle__registration_number",
    )

    ordering = (
        "-id",
    )

    readonly_fields = (
        "created_at",
    )

    actions = (
        "receive_selected_vehicles",
    )

    @admin.display(
        description="Vehicle Status"
    )
    def vehicle_status(self, obj):
        return obj.vehicle.status

    @admin.action(
        description="Receive selected vehicles"
    )
    def receive_selected_vehicles(self, request, queryset):
        success_count = 0
        error_count = 0

        for item in queryset:
            try:
                item.receive_vehicle()
                success_count += 1

            except Exception as exc:
                error_count += 1

                self.message_user(
                    request,
                    f"Could not receive "
                    f"{item.vehicle}: {exc}",
                    level=messages.ERROR,
                )

        if success_count:
            self.message_user(
                request,
                f"{success_count} vehicle(s) received successfully.",
                level=messages.SUCCESS,
            )

        if error_count:
            self.message_user(
                request,
                f"{error_count} vehicle(s) could not be received.",
                level=messages.WARNING,
            )