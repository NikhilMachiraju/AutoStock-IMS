from django.db import models


class Location(models.Model):

    LOCATION_TYPE_CHOICES = [
        ('STOCKYARD', 'Stockyard'),
        ('SHOWROOM', 'Showroom'),
        ('SERVICE_CENTER', 'Service Center'),
    ]

    name = models.CharField(
        max_length=150
    )

    location_type = models.CharField(
        max_length=20,
        choices=LOCATION_TYPE_CHOICES
    )

    address = models.TextField(
        blank=True
    )

    city = models.CharField(
        max_length=100
    )

    contact_person = models.CharField(
        max_length=100,
        blank=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.get_location_type_display()}"