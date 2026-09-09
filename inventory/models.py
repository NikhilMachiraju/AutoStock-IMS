from django.db import models


class Brand(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    def __str__(self):
        return self.name


class CarModel(models.Model):
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='models'
    )

    name = models.CharField(
        max_length=100
    )

    def __str__(self):
        return f"{self.brand.name} {self.name}"


class Variant(models.Model):
    car_model = models.ForeignKey(
        CarModel,
        on_delete=models.CASCADE,
        related_name='variants'
    )

    name = models.CharField(
        max_length=100
    )

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['car_model', 'name'],
                name='unique_variant_per_model'
            )
        ]

    def __str__(self):
        return f"{self.car_model} - {self.name}"


class Vehicle(models.Model):

    STATUS_CHOICES = [
        ('IN_STOCK', 'In Stock'),
        ('IN_TRANSIT', 'In Transit'),
        ('RESERVED', 'Reserved'),
        ('TEST_DRIVE', 'Test Drive'),
        ('SOLD', 'Sold'),
        ('DELIVERED', 'Delivered'),
        ('SERVICE', 'Service'),
        ('DAMAGED', 'Damaged'),
    ]

    FUEL_CHOICES = [
        ('PETROL', 'Petrol'),
        ('DIESEL', 'Diesel'),
        ('CNG', 'CNG'),
        ('ELECTRIC', 'Electric'),
        ('HYBRID', 'Hybrid'),
    ]

    TRANSMISSION_CHOICES = [
        ('MANUAL', 'Manual'),
        ('AUTOMATIC', 'Automatic'),
        ('AMT', 'AMT'),
    ]

    # ==============================
    # VEHICLE IDENTIFICATION
    # ==============================

    vin_number = models.CharField(
        max_length=50,
        unique=True
    )

    registration_number = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True
    )

    engine_number = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True
    )

    # ==============================
    # VEHICLE INFORMATION
    # ==============================

    current_location = models.ForeignKey(
        'locations.Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vehicles',
        help_text='Current location of this vehicle'
    )

    brand = models.ForeignKey(
        Brand,
        on_delete=models.PROTECT
    )

    car_model = models.ForeignKey(
        CarModel,
        on_delete=models.PROTECT
    )

    vehicle_variant = models.ForeignKey(
        Variant,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='vehicles'
    )

    # Temporary old variant field.
    # We will remove this after migrating existing data.
    variant = models.CharField(
        max_length=100,
        blank=True
    )

    manufacturing_year = models.PositiveIntegerField()

    color = models.CharField(
        max_length=50
    )

    fuel_type = models.CharField(
        max_length=20,
        choices=FUEL_CHOICES
    )

    transmission = models.CharField(
        max_length=20,
        choices=TRANSMISSION_CHOICES
    )

    mileage = models.PositiveIntegerField(
        default=0
    )

    # ==============================
    # FINANCIAL INFORMATION
    # ==============================

    purchase_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    selling_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    # ==============================
    # INVENTORY INFORMATION
    # ==============================

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='IN_STOCK'
    )

    location = models.CharField(
        max_length=100,
        blank=True
    )

    arrival_date = models.DateField()

    # ==============================
    # OWNERSHIP & REGISTRATION
    # ==============================

    ownership_count = models.PositiveIntegerField(
        default=1
    )

    purchase_date = models.DateField(
        null=True,
        blank=True
    )

    registration_date = models.DateField(
        null=True,
        blank=True
    )

    # ==============================
    # DOCUMENTS
    # ==============================

    insurance_expiry = models.DateField(
        null=True,
        blank=True
    )

    puc_expiry = models.DateField(
        null=True,
        blank=True
    )

    # ==============================
    # MEDIA
    # ==============================

    image_url = models.URLField(
        blank=True,
        null=True
    )

    description = models.TextField(
        blank=True
    )

    is_featured = models.BooleanField(
        default=False
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

    # ==============================
    # METHODS
    # ==============================

    def __str__(self):
        return f"{self.brand} {self.car_model} - {self.vin_number}"

    def can_change_status_to(self, new_status):
        """
        Check whether this vehicle is allowed to move
        from its current status to the requested status.
        """

        allowed_transitions = {

            'IN_STOCK': {
                'IN_STOCK',
                'IN_TRANSIT',
                'RESERVED',
                'TEST_DRIVE',
                'SERVICE',
                'DAMAGED',
            },

            'IN_TRANSIT': {
                'IN_TRANSIT',
                'IN_STOCK',
                'SERVICE',
                'DAMAGED',
            },

            'RESERVED': {
                'RESERVED',
                'IN_STOCK',
                'SOLD',
            },

            'TEST_DRIVE': {
                'TEST_DRIVE',
                'IN_STOCK',
                'SERVICE',
                'DAMAGED',
            },

            'SOLD': {
                'SOLD',
                'DELIVERED',
            },

            'DELIVERED': {
                'DELIVERED',
            },

            'SERVICE': {
                'SERVICE',
                'IN_STOCK',
                'DAMAGED',
            },

            'DAMAGED': {
                'DAMAGED',
                'SERVICE',
                'IN_STOCK',
            },
        }

        allowed_statuses = allowed_transitions.get(
            self.status,
            set()
        )

        return new_status in allowed_statuses

    def change_status(self, new_status):
        """
        Change the vehicle status only when the transition
        is allowed.
        """

        if new_status not in dict(self.STATUS_CHOICES):
            raise ValueError(
                f"Invalid vehicle status: {new_status}"
            )

        if not self.can_change_status_to(new_status):
            raise ValueError(
                f"Vehicle status cannot change "
                f"from {self.status} to {new_status}."
            )

        self.status = new_status
        self.save(update_fields=['status', 'updated_at'])

    @property
    def profit(self):
        if self.selling_price is None or self.purchase_price is None:
            return 0

        return self.selling_price - self.purchase_price


class VehicleMovement(models.Model):

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='movements'
    )

    from_location = models.ForeignKey(
        'locations.Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vehicle_movements_from'
    )

    to_location = models.ForeignKey(
        'locations.Location',
        on_delete=models.PROTECT,
        related_name='vehicle_movements_to'
    )

    transfer_date = models.DateTimeField(
        auto_now_add=True
    )

    reason = models.CharField(
        max_length=200,
        blank=True
    )

    remarks = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-transfer_date']

    def save(self, *args, **kwargs):

        if not self.from_location_id:
            self.from_location = self.vehicle.current_location

        super().save(*args, **kwargs)

        if self.vehicle.current_location_id != self.to_location_id:
            self.vehicle.current_location = self.to_location
            self.vehicle.save(
                update_fields=[
                    'current_location',
                    'updated_at'
                ]
            )

    def __str__(self):
        from_name = (
            self.from_location.name
            if self.from_location
            else 'Initial Location'
        )

        return (
            f"{self.vehicle.vin_number}: "
            f"{from_name} → {self.to_location.name}"
        )