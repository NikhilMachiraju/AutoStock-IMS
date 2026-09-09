from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Reservation(models.Model):

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('CANCELLED', 'Cancelled'),
        ('CONVERTED', 'Converted to Sale'),
    ]

    # ==============================
    # RESERVATION IDENTIFICATION
    # ==============================

    reservation_number = models.CharField(
        max_length=50,
        unique=True
    )

    # ==============================
    # CUSTOMER & VEHICLE
    # ==============================

    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.PROTECT,
        related_name='reservations'
    )

    vehicle = models.ForeignKey(
        'inventory.Vehicle',
        on_delete=models.PROTECT,
        related_name='reservations'
    )

    # ==============================
    # RESERVATION DATES
    # ==============================

    reservation_date = models.DateField(
        auto_now_add=True
    )

    expiry_date = models.DateField()

    # ==============================
    # PAYMENT / DEPOSIT
    # ==============================

    deposit_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    # ==============================
    # STATUS
    # ==============================

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE'
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
        return self.reservation_number

    @property
    def is_active(self):
        return self.status == 'ACTIVE'

    # ==============================
    # VALIDATION / BUSINESS RULES
    # ==============================

    def clean(self):
        super().clean()

        errors = {}

        # Expiry date cannot be in the past.
        if self.expiry_date and self.expiry_date < timezone.localdate():
            errors['expiry_date'] = (
                'Expiry date cannot be in the past.'
            )

        # Deposit cannot be negative.
        if (
            self.deposit_amount is not None
            and self.deposit_amount < Decimal('0.00')
        ):
            errors['deposit_amount'] = (
                'Deposit amount cannot be negative.'
            )

        # A vehicle can have only one ACTIVE reservation.
        if self.vehicle_id and self.status == 'ACTIVE':
            active_reservation_exists = Reservation.objects.filter(
                vehicle=self.vehicle,
                status='ACTIVE'
            ).exclude(
                pk=self.pk
            ).exists()

            if active_reservation_exists:
                errors['vehicle'] = (
                    'This vehicle already has an active reservation.'
                )

        if errors:
            raise ValidationError(errors)

    # ==============================
    # SAVE / VEHICLE STATUS
    # ==============================

    def save(self, *args, **kwargs):

        old_status = None

        if self.pk:
            old_status = (
                Reservation.objects
                .filter(pk=self.pk)
                .values_list('status', flat=True)
                .first()
            )

        self.full_clean()

        super().save(*args, **kwargs)

        # ACTIVE reservation → RESERVED vehicle
        if self.status == 'ACTIVE':

            if self.vehicle.status == 'IN_STOCK':
                self.vehicle.change_status('RESERVED')

        # Cancelled or expired reservation
        # → return vehicle to IN_STOCK
        elif old_status == 'ACTIVE' and self.status in {
            'CANCELLED',
            'EXPIRED',
        }:

            if self.vehicle.status == 'RESERVED':
                self.vehicle.change_status('IN_STOCK')