from datetime import date
from unittest.mock import Mock

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.test import TestCase

from inventory.models import Brand, CarModel, Vehicle

from .admin import PurchaseItemAdmin
from .models import Supplier, Purchase, PurchaseItem


class SupplierTests(TestCase):

    def test_supplier_creation(self):
        supplier = Supplier.objects.create(
            name="Test Supplier",
            contact_person="John",
            phone="9876543210",
            email="supplier@example.com",
        )

        self.assertEqual(
            supplier.name,
            "Test Supplier"
        )

    def test_supplier_string(self):
        supplier = Supplier.objects.create(
            name="Test Supplier",
            phone="9876543210",
        )

        self.assertEqual(
            str(supplier),
            "Test Supplier"
        )


class PurchaseTests(TestCase):

    def setUp(self):
        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            phone="9876543210",
        )

        self.brand = Brand.objects.create(
            name="Test Brand"
        )

        self.car_model = CarModel.objects.create(
            brand=self.brand,
            name="Test Model"
        )

        self.vehicle = Vehicle.objects.create(
            vin_number="VIN123456789",
            registration_number="REG123",
            engine_number="ENG123",
            brand=self.brand,
            car_model=self.car_model,
            manufacturing_year=2026,
            color="White",
            fuel_type="PETROL",
            transmission="MANUAL",
            mileage=0,
            purchase_price=500000,
            selling_price=600000,
            status="IN_TRANSIT",
            arrival_date=date.today(),
        )

        self.purchase = Purchase.objects.create(
            supplier=self.supplier,
            purchase_number="PO-001",
            purchase_date=date.today(),
        )

    def test_purchase_creation(self):
        self.assertEqual(
            self.purchase.purchase_number,
            "PO-001"
        )

        self.assertEqual(
            self.purchase.status,
            "DRAFT"
        )

    def test_purchase_string(self):
        self.assertEqual(
            str(self.purchase),
            "PO-001"
        )

    def test_draft_to_ordered(self):
        PurchaseItem.objects.create(
            purchase=self.purchase,
            vehicle=self.vehicle,
            purchase_price=500000,
        )

        self.purchase.change_status("ORDERED")

        self.purchase.refresh_from_db()

        self.assertEqual(
            self.purchase.status,
            "ORDERED"
        )

    def test_empty_purchase_cannot_be_ordered(self):
        with self.assertRaises(ValueError):
            self.purchase.change_status("ORDERED")

    def test_ordered_to_received(self):
        PurchaseItem.objects.create(
            purchase=self.purchase,
            vehicle=self.vehicle,
            purchase_price=500000,
        )

        self.purchase.change_status("ORDERED")
        self.purchase.change_status("RECEIVED")

        self.purchase.refresh_from_db()

        self.assertEqual(
            self.purchase.status,
            "RECEIVED"
        )

    def test_received_to_completed(self):
        PurchaseItem.objects.create(
            purchase=self.purchase,
            vehicle=self.vehicle,
            purchase_price=500000,
        )

        self.purchase.change_status("ORDERED")
        self.purchase.change_status("RECEIVED")

        self.vehicle.status = "IN_STOCK"
        self.vehicle.save(
            update_fields=["status"]
        )

        self.purchase.change_status("COMPLETED")

        self.purchase.refresh_from_db()

        self.assertEqual(
            self.purchase.status,
            "COMPLETED"
        )

    def test_draft_to_cancelled(self):
        self.purchase.change_status("CANCELLED")

        self.purchase.refresh_from_db()

        self.assertEqual(
            self.purchase.status,
            "CANCELLED"
        )

    def test_ordered_to_cancelled(self):
        PurchaseItem.objects.create(
            purchase=self.purchase,
            vehicle=self.vehicle,
            purchase_price=500000,
        )

        self.purchase.change_status("ORDERED")
        self.purchase.change_status("CANCELLED")

        self.purchase.refresh_from_db()

        self.assertEqual(
            self.purchase.status,
            "CANCELLED"
        )

    def test_received_cannot_be_cancelled(self):
        PurchaseItem.objects.create(
            purchase=self.purchase,
            vehicle=self.vehicle,
            purchase_price=500000,
        )

        self.purchase.change_status("ORDERED")
        self.purchase.change_status("RECEIVED")

        with self.assertRaises(ValueError):
            self.purchase.change_status("CANCELLED")

    def test_completed_cannot_be_cancelled(self):
        PurchaseItem.objects.create(
            purchase=self.purchase,
            vehicle=self.vehicle,
            purchase_price=500000,
        )

        self.purchase.change_status("ORDERED")
        self.purchase.change_status("RECEIVED")

        self.vehicle.status = "IN_STOCK"
        self.vehicle.save(
            update_fields=["status"]
        )

        self.purchase.change_status("COMPLETED")

        with self.assertRaises(ValueError):
            self.purchase.change_status("CANCELLED")

    def test_cancelled_cannot_be_ordered(self):
        self.purchase.change_status("CANCELLED")

        with self.assertRaises(ValueError):
            self.purchase.change_status("ORDERED")

    def test_cancelled_cannot_be_received(self):
        self.purchase.change_status("CANCELLED")

        with self.assertRaises(ValueError):
            self.purchase.change_status("RECEIVED")

    def test_invalid_purchase_status(self):
        with self.assertRaises(ValueError):
            self.purchase.change_status("INVALID")

    def test_invalid_purchase_transition(self):
        with self.assertRaises(ValueError):
            self.purchase.change_status("COMPLETED")

    def test_purchase_cannot_be_completed_with_unreceived_vehicle(self):
        vehicle2 = Vehicle.objects.create(
            vin_number="VIN999999999",
            registration_number="REG999",
            engine_number="ENG999",
            brand=self.brand,
            car_model=self.car_model,
            manufacturing_year=2026,
            color="Blue",
            fuel_type="PETROL",
            transmission="MANUAL",
            mileage=0,
            purchase_price=550000,
            selling_price=650000,
            status="IN_TRANSIT",
            arrival_date=date.today(),
        )

        PurchaseItem.objects.create(
            purchase=self.purchase,
            vehicle=self.vehicle,
            purchase_price=500000,
        )

        PurchaseItem.objects.create(
            purchase=self.purchase,
            vehicle=vehicle2,
            purchase_price=550000,
        )

        self.purchase.change_status("ORDERED")

        self.vehicle.status = "IN_STOCK"
        self.vehicle.save(
            update_fields=["status"]
        )

        self.purchase.status = "RECEIVED"
        self.purchase.save(
            update_fields=["status"]
        )

        with self.assertRaises(ValueError):
            self.purchase.change_status("COMPLETED")


class PurchaseItemTests(TestCase):

    def setUp(self):
        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            phone="9876543210",
        )

        self.brand = Brand.objects.create(
            name="Test Brand"
        )

        self.car_model = CarModel.objects.create(
            brand=self.brand,
            name="Test Model"
        )

        self.vehicle = Vehicle.objects.create(
            vin_number="VIN123456789",
            registration_number="REG123",
            engine_number="ENG123",
            brand=self.brand,
            car_model=self.car_model,
            manufacturing_year=2026,
            color="White",
            fuel_type="PETROL",
            transmission="MANUAL",
            mileage=0,
            purchase_price=500000,
            selling_price=600000,
            status="IN_TRANSIT",
            arrival_date=date.today(),
        )

        self.purchase = Purchase.objects.create(
            supplier=self.supplier,
            purchase_number="PO-001",
            purchase_date=date.today(),
        )

    def test_purchase_item_creation(self):
        item = PurchaseItem.objects.create(
            purchase=self.purchase,
            vehicle=self.vehicle,
            purchase_price=500000,
        )

        self.assertEqual(
            item.purchase,
            self.purchase
        )

        self.assertEqual(
            item.vehicle,
            self.vehicle
        )

    def test_purchase_item_string(self):
        item = PurchaseItem.objects.create(
            purchase=self.purchase,
            vehicle=self.vehicle,
            purchase_price=500000,
        )

        self.assertEqual(
            str(item),
            f"{self.purchase.purchase_number} - {self.vehicle}"
        )

    def test_sold_vehicle_cannot_be_added_to_purchase(self):
        self.vehicle.status = "SOLD"
        self.vehicle.save(
            update_fields=["status"]
        )

        item = PurchaseItem(
            purchase=self.purchase,
            vehicle=self.vehicle,
            purchase_price=500000,
        )

        with self.assertRaises(ValidationError):
            item.clean()

    def test_delivered_vehicle_cannot_be_added_to_purchase(self):
        self.vehicle.status = "DELIVERED"
        self.vehicle.save(
            update_fields=["status"]
        )

        item = PurchaseItem(
            purchase=self.purchase,
            vehicle=self.vehicle,
            purchase_price=500000,
        )

        with self.assertRaises(ValidationError):
            item.clean()

    def test_receive_vehicle_changes_in_transit_to_in_stock(self):
        self.purchase.status = "ORDERED"
        self.purchase.save(
            update_fields=["status"]
        )

        item = PurchaseItem.objects.create(
            purchase=self.purchase,
            vehicle=self.vehicle,
            purchase_price=500000,
        )

        item.receive_vehicle()

        self.vehicle.refresh_from_db()

        self.assertEqual(
            self.vehicle.status,
            "IN_STOCK"
        )

    def test_receive_vehicle_rejects_invalid_vehicle_status(self):
        self.purchase.status = "ORDERED"
        self.purchase.save(
            update_fields=["status"]
        )

        self.vehicle.status = "RESERVED"
        self.vehicle.save(
            update_fields=["status"]
        )

        item = PurchaseItem.objects.create(
            purchase=self.purchase,
            vehicle=self.vehicle,
            purchase_price=500000,
        )

        with self.assertRaises(ValidationError):
            item.receive_vehicle()

    def test_receive_vehicle_rejects_draft_purchase(self):
        item = PurchaseItem.objects.create(
            purchase=self.purchase,
            vehicle=self.vehicle,
            purchase_price=500000,
        )

        with self.assertRaises(ValidationError):
            item.receive_vehicle()

        self.vehicle.refresh_from_db()

        self.assertEqual(
            self.vehicle.status,
            "IN_TRANSIT"
        )

    def test_receive_vehicle_allows_ordered_purchase(self):
        item = PurchaseItem.objects.create(
            purchase=self.purchase,
            vehicle=self.vehicle,
            purchase_price=500000,
        )

        self.purchase.status = "ORDERED"
        self.purchase.save(
            update_fields=["status"]
        )

        item.receive_vehicle()

        self.vehicle.refresh_from_db()
        self.purchase.refresh_from_db()

        self.assertEqual(
            self.vehicle.status,
            "IN_STOCK"
        )

        self.assertEqual(
            self.purchase.status,
            "RECEIVED"
        )

    def test_receive_vehicle_when_already_in_stock(self):
        self.purchase.status = "ORDERED"
        self.purchase.save(
            update_fields=["status"]
        )

        self.vehicle.status = "IN_STOCK"
        self.vehicle.save(
            update_fields=["status"]
        )

        item = PurchaseItem.objects.create(
            purchase=self.purchase,
            vehicle=self.vehicle,
            purchase_price=500000,
        )

        item.receive_vehicle()

        self.purchase.refresh_from_db()

        self.assertEqual(
            self.purchase.status,
            "RECEIVED"
        )

    def test_receive_vehicle_rejects_received_purchase(self):
        self.purchase.status = "RECEIVED"
        self.purchase.save(
            update_fields=["status"]
        )

        item = PurchaseItem.objects.create(
            purchase=self.purchase,
            vehicle=self.vehicle,
            purchase_price=500000,
        )

        with self.assertRaises(ValidationError):
            item.receive_vehicle()

        self.vehicle.refresh_from_db()

        self.assertEqual(
            self.vehicle.status,
            "IN_TRANSIT"
        )

    def test_receive_vehicle_rejects_completed_purchase(self):
        self.purchase.status = "COMPLETED"
        self.purchase.save(
            update_fields=["status"]
        )

        item = PurchaseItem.objects.create(
            purchase=self.purchase,
            vehicle=self.vehicle,
            purchase_price=500000,
        )

        with self.assertRaises(ValidationError):
            item.receive_vehicle()

        self.vehicle.refresh_from_db()

        self.assertEqual(
            self.vehicle.status,
            "IN_TRANSIT"
        )

    def test_receive_vehicle_rejects_cancelled_purchase(self):
        self.purchase.status = "CANCELLED"
        self.purchase.save(
            update_fields=["status"]
        )

        item = PurchaseItem.objects.create(
            purchase=self.purchase,
            vehicle=self.vehicle,
            purchase_price=500000,
        )

        with self.assertRaises(ValidationError):
            item.receive_vehicle()

        self.vehicle.refresh_from_db()

        self.assertEqual(
            self.vehicle.status,
            "IN_TRANSIT"
        )

    def test_single_received_vehicle_changes_purchase_to_received(self):
        self.purchase.status = "ORDERED"
        self.purchase.save(
            update_fields=["status"]
        )

        item = PurchaseItem.objects.create(
            purchase=self.purchase,
            vehicle=self.vehicle,
            purchase_price=500000,
        )

        item.receive_vehicle()

        self.purchase.refresh_from_db()

        self.assertEqual(
            self.purchase.status,
            "RECEIVED"
        )

    def test_multiple_items_partial_receipt_stays_ordered(self):
        vehicle2 = Vehicle.objects.create(
            vin_number="VIN987654321",
            registration_number="REG987",
            engine_number="ENG987",
            brand=self.brand,
            car_model=self.car_model,
            manufacturing_year=2026,
            color="Black",
            fuel_type="PETROL",
            transmission="MANUAL",
            mileage=0,
            purchase_price=550000,
            selling_price=650000,
            status="IN_TRANSIT",
            arrival_date=date.today(),
        )

        self.purchase.status = "ORDERED"
        self.purchase.save(
            update_fields=["status"]
        )

        item1 = PurchaseItem.objects.create(
            purchase=self.purchase,
            vehicle=self.vehicle,
            purchase_price=500000,
        )

        PurchaseItem.objects.create(
            purchase=self.purchase,
            vehicle=vehicle2,
            purchase_price=550000,
        )

        item1.receive_vehicle()

        self.purchase.refresh_from_db()

        self.assertEqual(
            self.purchase.status,
            "ORDERED"
        )

    def test_multiple_items_all_received_changes_purchase_to_received(self):
        vehicle2 = Vehicle.objects.create(
            vin_number="VIN987654321",
            registration_number="REG987",
            engine_number="ENG987",
            brand=self.brand,
            car_model=self.car_model,
            manufacturing_year=2026,
            color="Black",
            fuel_type="PETROL",
            transmission="MANUAL",
            mileage=0,
            purchase_price=550000,
            selling_price=650000,
            status="IN_TRANSIT",
            arrival_date=date.today(),
        )

        self.purchase.status = "ORDERED"
        self.purchase.save(
            update_fields=["status"]
        )

        item1 = PurchaseItem.objects.create(
            purchase=self.purchase,
            vehicle=self.vehicle,
            purchase_price=500000,
        )

        item2 = PurchaseItem.objects.create(
            purchase=self.purchase,
            vehicle=vehicle2,
            purchase_price=550000,
        )

        item1.receive_vehicle()

        self.purchase.refresh_from_db()

        self.assertEqual(
            self.purchase.status,
            "ORDERED"
        )

        item2.receive_vehicle()

        self.purchase.refresh_from_db()

        self.assertEqual(
            self.purchase.status,
            "RECEIVED"
        )

    def test_receiving_does_not_auto_complete_purchase(self):
        self.purchase.status = "ORDERED"
        self.purchase.save(
            update_fields=["status"]
        )

        item = PurchaseItem.objects.create(
            purchase=self.purchase,
            vehicle=self.vehicle,
            purchase_price=500000,
        )

        item.receive_vehicle()

        self.purchase.refresh_from_db()

        self.assertEqual(
            self.purchase.status,
            "RECEIVED"
        )

        self.assertNotEqual(
            self.purchase.status,
            "COMPLETED"
        )


class PurchaseItemAdminTests(PurchaseItemTests):

    def test_admin_receive_selected_vehicle(self):
        self.purchase.status = "ORDERED"
        self.purchase.save(
            update_fields=["status"]
        )

        item = PurchaseItem.objects.create(
            purchase=self.purchase,
            vehicle=self.vehicle,
            purchase_price=500000,
        )

        model_admin = PurchaseItemAdmin(
            PurchaseItem,
            admin.site,
        )

        request = Mock()

        model_admin.message_user = Mock()

        queryset = PurchaseItem.objects.filter(
            id=item.id
        )

        model_admin.receive_selected_vehicles(
            request,
            queryset,
        )

        self.vehicle.refresh_from_db()
        self.purchase.refresh_from_db()

        self.assertEqual(
            self.vehicle.status,
            "IN_STOCK"
        )

        self.assertEqual(
            self.purchase.status,
            "RECEIVED"
        )

        model_admin.message_user.assert_called()