from django.core.exceptions import ValidationError
from django.db import models


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Purchase(models.Model):
    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("ORDERED", "Ordered"),
        ("RECEIVED", "Received"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="purchases",
    )

    purchase_number = models.CharField(
        max_length=50,
        unique=True,
    )

    purchase_date = models.DateField()

    invoice_number = models.CharField(
        max_length=100,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="DRAFT",
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "-purchase_date",
            "-id",
        ]

    def can_change_status_to(self, new_status):
        allowed_transitions = {
            "DRAFT": {
                "DRAFT",
                "ORDERED",
                "CANCELLED",
            },
            "ORDERED": {
                "ORDERED",
                "RECEIVED",
                "CANCELLED",
            },
            "RECEIVED": {
                "RECEIVED",
                "COMPLETED",
            },
            "COMPLETED": {
                "COMPLETED",
            },
            "CANCELLED": {
                "CANCELLED",
            },
        }

        allowed_statuses = allowed_transitions.get(
            self.status,
            set(),
        )

        return new_status in allowed_statuses

    def change_status(self, new_status):
        if new_status not in dict(self.STATUS_CHOICES):
            raise ValueError(
                f"Invalid purchase status: {new_status}"
            )

        if new_status == "ORDERED":
            if not self.items.exists():
                raise ValueError(
                    "A purchase must contain at least one vehicle before it can be ordered."
                )

        if new_status == "COMPLETED":
            items = self.items.all()

            if not items.exists():
                raise ValueError(
                    "A purchase must contain at least one vehicle before it can be completed."
                )

            all_received = all(
                item.vehicle.status == "IN_STOCK"
                for item in items
            )

            if not all_received:
                raise ValueError(
                    "A purchase cannot be completed until all vehicles are received."
                )

        if not self.can_change_status_to(new_status):
            raise ValueError(
                f"Purchase status cannot change "
                f"from {self.status} to {new_status}."
            )

        self.status = new_status

        self.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

    def __str__(self):
        return self.purchase_number


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name="items",
    )

    vehicle = models.OneToOneField(
        "inventory.Vehicle",
        on_delete=models.PROTECT,
        related_name="purchase_item",
    )

    purchase_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-id"]

    def clean(self):
        if self.purchase_id and self.vehicle_id:
            if self.vehicle.status == "SOLD":
                raise ValidationError(
                    "A sold vehicle cannot be added to a purchase."
                )

            if self.vehicle.status == "DELIVERED":
                raise ValidationError(
                    "A delivered vehicle cannot be added to a purchase."
                )

    def update_purchase_status(self):
        purchase = self.purchase

        if purchase.status != "ORDERED":
            return

        items = purchase.items.all()

        if not items.exists():
            return

        all_received = all(
            item.vehicle.status == "IN_STOCK"
            for item in items
        )

        if all_received:
            purchase.change_status("RECEIVED")

    def receive_vehicle(self):
        purchase = self.purchase
        vehicle = self.vehicle

        if purchase.status != "ORDERED":
            raise ValidationError(
                "A vehicle can only be received for an ordered purchase."
            )

        if vehicle.status == "IN_STOCK":
            self.update_purchase_status()
            return

        if vehicle.status != "IN_TRANSIT":
            raise ValidationError(
                "Only vehicles in transit can be received."
            )

        vehicle.change_status("IN_STOCK")

        self.update_purchase_status()

    def __str__(self):
        return f"{self.purchase.purchase_number} - {self.vehicle}"