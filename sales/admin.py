from django.contrib import admin
from .models import Sale


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):

    list_display = (
        'sale_number',
        'customer',
        'vehicle',
        'sale_price',
        'final_amount',
        'amount_paid',
        'balance_amount_display',
        'payment_status',
        'sale_status',
        'delivery_status',
        'sale_date',
    )

    list_filter = (
        'payment_status',
        'sale_status',
        'delivery_status',
        'sale_date',
    )

    search_fields = (
        'sale_number',
        'customer__first_name',
        'customer__last_name',
        'customer__company_name',
        'customer__phone',
        'vehicle__vin_number',
        'vehicle__registration_number',
    )

    ordering = (
        '-sale_date',
        '-created_at',
    )

    list_per_page = 20

    fieldsets = (

        (
            'Sale Information',
            {
                'fields': (
                    'sale_number',
                    'customer',
                    'vehicle',
                    'sale_date',
                )
            }
        ),

        (
            'Pricing',
            {
                'fields': (
                    'sale_price',
                    'discount',
                    'tax_amount',
                    'final_amount',
                )
            }
        ),

        (
            'Payment',
            {
                'fields': (
                    'amount_paid',
                    'payment_status',
                )
            }
        ),

        (
            'Sale Status',
            {
                'fields': (
                    'sale_status',
                )
            }
        ),

        (
            'Delivery',
            {
                'fields': (
                    'delivery_status',
                    'delivery_date',
                )
            }
        ),

        (
            'Additional Information',
            {
                'fields': (
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
        'sale_date',
        'created_at',
        'updated_at',
    )

    def balance_amount_display(self, obj):
        return obj.balance_amount

    balance_amount_display.short_description = 'Balance'