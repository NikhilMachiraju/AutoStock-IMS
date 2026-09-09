from django.db import models


class Customer(models.Model):

    CUSTOMER_TYPE_CHOICES = [
        ('INDIVIDUAL', 'Individual'),
        ('BUSINESS', 'Business'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
    ]

    # ==============================
    # CUSTOMER INFORMATION
    # ==============================

    customer_type = models.CharField(
        max_length=20,
        choices=CUSTOMER_TYPE_CHOICES,
        default='INDIVIDUAL'
    )

    first_name = models.CharField(
        max_length=100
    )

    last_name = models.CharField(
        max_length=100,
        blank=True
    )

    company_name = models.CharField(
        max_length=200,
        blank=True
    )

    # ==============================
    # CONTACT INFORMATION
    # ==============================

    phone = models.CharField(
        max_length=20
    )

    alternate_phone = models.CharField(
        max_length=20,
        blank=True
    )

    email = models.EmailField(
        blank=True
    )

    # ==============================
    # ADDRESS
    # ==============================

    address = models.TextField(
        blank=True
    )

    city = models.CharField(
        max_length=100,
        blank=True
    )

    state = models.CharField(
        max_length=100,
        blank=True
    )

    postal_code = models.CharField(
        max_length=20,
        blank=True
    )

    # ==============================
    # IDENTITY / TAX INFORMATION
    # ==============================

    pan_number = models.CharField(
        max_length=20,
        blank=True
    )

    gst_number = models.CharField(
        max_length=30,
        blank=True
    )

    # ==============================
    # CUSTOMER STATUS
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
        if self.customer_type == 'BUSINESS' and self.company_name:
            return self.company_name

        return f"{self.first_name} {self.last_name}".strip()