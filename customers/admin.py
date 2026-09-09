from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'customer_name',
        'customer_type',
        'phone',
        'email',
        'city',
        'status',
        'created_at',
    )

    list_filter = (
        'customer_type',
        'status',
        'city',
        'created_at',
    )

    search_fields = (
        'first_name',
        'last_name',
        'company_name',
        'phone',
        'alternate_phone',
        'email',
        'pan_number',
        'gst_number',
        'city',
    )

    ordering = (
        '-created_at',
    )

    list_per_page = 20

    fieldsets = (

        (
            'Customer Information',
            {
                'fields': (
                    'customer_type',
                    'first_name',
                    'last_name',
                    'company_name',
                )
            }
        ),

        (
            'Contact Information',
            {
                'fields': (
                    'phone',
                    'alternate_phone',
                    'email',
                )
            }
        ),

        (
            'Address',
            {
                'fields': (
                    'address',
                    'city',
                    'state',
                    'postal_code',
                )
            }
        ),

        (
            'Identity & Tax Information',
            {
                'fields': (
                    'pan_number',
                    'gst_number',
                )
            }
        ),

        (
            'Customer Status',
            {
                'fields': (
                    'status',
                    'notes',
                )
            }
        ),

        (
            'System Information',
            {
                'fields': (
                    'created_at',
                    'updated_at',
                )
            }
        ),
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    def customer_name(self, obj):

        if obj.customer_type == 'BUSINESS' and obj.company_name:
            return obj.company_name

        return f"{obj.first_name} {obj.last_name}".strip()

    customer_name.short_description = 'Customer'