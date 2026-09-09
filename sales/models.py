from django.db import models
from decimal import Decimal


class Sale(models.Model):

    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PARTIAL', 'Partially Paid'),
        ('PAID', 'Paid'),
        ('REFUNDED', 'Refunded'),
    ]

    SALE_STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]

    DELIVERY_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('READY', 'Ready for Delivery'),
        ('DELIVERED', 'Delivered'),
    ]

    # ==============================
    # SALE IDENTIFICATION
    # ==============================

    sale_number = models.CharField(
        max_length=50,
        unique=True
    )

    # ==============================
    # CUSTOMER & VEHICLE
    # ==============================

    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.PROTECT,
        related_name='sales'
    )

    vehicle = models.OneToOneField(
        'inventory.Vehicle',
        on_delete=models.PROTECT,
        related_name='sale'
    )

    # ==============================
    # PRICING
    # ==============================

    sale_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    discount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    final_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    # ==============================
    # PAYMENT
    # ==============================

    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='PENDING'
    )

    # ==============================
    # SALE STATUS
    # ==============================

    sale_status = models.CharField(
        max_length=20,
        choices=SALE_STATUS_CHOICES,
        default='DRAFT'
    )

    # ==============================
    # DELIVERY
    # ==============================

    delivery_status = models.CharField(
        max_length=20,
        choices=DELIVERY_STATUS_CHOICES,
        default='PENDING'
    )

    delivery_date = models.DateField(
        null=True,
        blank=True
    )

    # ==============================
    # SALE DATE
    # ==============================

    sale_date = models.DateField(
        auto_now_add=True
    )

    # ==============================
    # NOTES
    # ==============================

    notes = models.TextField(
        blank=True
    )

    # ==============================
    # SYSTEM INFORMATION
    # ==============================

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.sale_number

    @property
    def balance_amount(self):
        return self.final_amount - self.amount_paid

    @property
    def profit(self):
        return (
            self.final_amount -
            self.vehicle.purchase_price
        )