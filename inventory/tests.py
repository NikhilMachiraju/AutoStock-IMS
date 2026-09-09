from datetime import date
from django.db import IntegrityError
from django.test import TestCase

from .models import Brand, CarModel, Variant, Vehicle, VehicleMovement


class VehicleValidationTests(TestCase):

    def setUp(self):
        """
        Create basic data used by the tests.
        """
        self.brand = Brand.objects.create(
            name="Test Brand",
            description="Test brand for automated testing"
        )

        self.car_model = CarModel.objects.create(
            brand=self.brand,
            name="Test Model"
        )

    def create_vehicle(
        self,
        vin_number,
        registration_number=None,
        engine_number=None,
        status="IN_STOCK"
    ):
        """
        Helper function used to create a test vehicle.
        """
        return Vehicle.objects.create(
            vin_number=vin_number,
            registration_number=registration_number,
            engine_number=engine_number,
            brand=self.brand,
            car_model=self.car_model,
            manufacturing_year=2026,
            color="White",
            fuel_type="PETROL",
            transmission="MANUAL",
            mileage=0,
            purchase_price=1000000,
            selling_price=1200000,
            status=status,
            location="Test Stockyard",
            arrival_date=date.today(),
            ownership_count=1
        )

    def test_vehicle_can_be_created(self):
        """
        Verify that a valid vehicle can be created.
        """
        vehicle = self.create_vehicle(
            vin_number="TESTVIN001",
            registration_number="TESTREG001",
            engine_number="TESTENG001"
        )

        self.assertEqual(
            vehicle.vin_number,
            "TESTVIN001"
        )

        self.assertEqual(
            Vehicle.objects.count(),
            1
        )

    def test_duplicate_vin_is_rejected(self):
        """
        Verify that two vehicles cannot have the same VIN.
        """
        self.create_vehicle(
            vin_number="DUPLICATEVIN"
        )

        with self.assertRaises(IntegrityError):
            self.create_vehicle(
                vin_number="DUPLICATEVIN"
            )

    def test_duplicate_registration_number_is_rejected(self):
        """
        Verify that two vehicles cannot have the same registration number.
        """
        self.create_vehicle(
            vin_number="VIN001",
            registration_number="REG001"
        )

        with self.assertRaises(IntegrityError):
            self.create_vehicle(
                vin_number="VIN002",
                registration_number="REG001"
            )

    def test_duplicate_engine_number_is_rejected(self):
        """
        Verify that two vehicles cannot have the same engine number.
        """
        self.create_vehicle(
            vin_number="VIN003",
            engine_number="ENG001"
        )

        with self.assertRaises(IntegrityError):
            self.create_vehicle(
                vin_number="VIN004",
                engine_number="ENG001"
            )


class VehicleStatusTests(TestCase):

    def setUp(self):
        """
        Create basic data for status tests.
        """
        self.brand = Brand.objects.create(
            name="Status Test Brand"
        )

        self.car_model = CarModel.objects.create(
            brand=self.brand,
            name="Status Test Model"
        )

    def create_vehicle(self, status):
        """
        Create a vehicle with a specific status.
        """
        return Vehicle.objects.create(
            vin_number=f"VIN-{status}",
            brand=self.brand,
            car_model=self.car_model,
            manufacturing_year=2026,
            color="White",
            fuel_type="PETROL",
            transmission="MANUAL",
            mileage=0,
            purchase_price=1000000,
            selling_price=1200000,
            status=status,
            location="Test Stockyard",
            arrival_date=date.today(),
            ownership_count=1
        )

    def test_in_stock_can_be_reserved(self):
        """
        IN_STOCK → RESERVED should be allowed.
        """
        vehicle = self.create_vehicle("IN_STOCK")

        self.assertTrue(
            vehicle.can_change_status_to("RESERVED")
        )

    def test_in_stock_can_enter_transit(self):
        """
        IN_STOCK → IN_TRANSIT should be allowed.
        """
        vehicle = self.create_vehicle("IN_STOCK")

        self.assertTrue(
            vehicle.can_change_status_to("IN_TRANSIT")
        )

    def test_reserved_can_be_sold(self):
        """
        RESERVED → SOLD should be allowed.
        """
        vehicle = self.create_vehicle("RESERVED")

        self.assertTrue(
            vehicle.can_change_status_to("SOLD")
        )

    def test_sold_cannot_return_to_stock(self):
        """
        SOLD → IN_STOCK should not be allowed.
        """
        vehicle = self.create_vehicle("SOLD")

        self.assertFalse(
            vehicle.can_change_status_to("IN_STOCK")
        )

    def test_delivered_cannot_be_sold_again(self):
        """
        DELIVERED → SOLD should not be allowed.
        """
        vehicle = self.create_vehicle("DELIVERED")

        self.assertFalse(
            vehicle.can_change_status_to("SOLD")
        )

    def test_change_status_updates_vehicle(self):
        """
        Verify that change_status actually updates the vehicle.
        """
        vehicle = self.create_vehicle("IN_STOCK")

        vehicle.change_status("RESERVED")

        vehicle.refresh_from_db()

        self.assertEqual(
            vehicle.status,
            "RESERVED"
        )

    def test_invalid_status_change_raises_error(self):
        """
        Verify that an invalid transition raises ValueError.
        """
        vehicle = self.create_vehicle("SOLD")

        with self.assertRaises(ValueError):
            vehicle.change_status("IN_STOCK")

    def test_invalid_status_value_raises_error(self):
        """
        Verify that an invalid status value is rejected.
        """
        vehicle = self.create_vehicle("IN_STOCK")

        with self.assertRaises(ValueError):
            vehicle.change_status("INVALID_STATUS")


class VehicleMovementTests(TestCase):

    def setUp(self):
        self.brand = Brand.objects.create(
            name="Movement Test Brand"
        )

        self.car_model = CarModel.objects.create(
            brand=self.brand,
            name="Movement Test Model"
        )

        self.variant = Variant.objects.create(
            car_model=self.car_model,
            name="Movement Test Variant"
        )

        from locations.models import Location

        self.stockyard = Location.objects.create(
            name="Movement Stockyard",
            location_type="STOCKYARD",
            city="Vijayawada"
        )

        self.showroom = Location.objects.create(
            name="Movement Showroom",
            location_type="SHOWROOM",
            city="Vijayawada"
        )

        self.service_center = Location.objects.create(
            name="Movement Service Center",
            location_type="SERVICE_CENTER",
            city="Vijayawada"
        )

        self.vehicle = Vehicle.objects.create(
            vin_number="MOVEMENTVIN001",
            registration_number="MOVEMENTREG001",
            engine_number="MOVEMENTENG001",
            brand=self.brand,
            car_model=self.car_model,
            vehicle_variant=self.variant,
            manufacturing_year=2026,
            color="White",
            fuel_type="PETROL",
            transmission="MANUAL",
            mileage=0,
            purchase_price=1000000,
            selling_price=1200000,
            status="IN_STOCK",
            location="Movement Stockyard",
            arrival_date=date.today(),
            ownership_count=1,
            current_location=self.stockyard
        )

    def test_vehicle_movement_created(self):
        movement = VehicleMovement.objects.create(
            vehicle=self.vehicle,
            to_location=self.showroom,
            reason="Showroom display",
            remarks="Transferred for customer viewing"
        )

        self.assertEqual(
            movement.from_location,
            self.stockyard
        )

        self.assertEqual(
            movement.to_location,
            self.showroom
        )

    def test_vehicle_current_location_updates_after_movement(self):
        VehicleMovement.objects.create(
            vehicle=self.vehicle,
            to_location=self.showroom,
            reason="Showroom display"
        )

        self.vehicle.refresh_from_db()

        self.assertEqual(
            self.vehicle.current_location,
            self.showroom
        )

    def test_movement_history_is_created(self):
        VehicleMovement.objects.create(
            vehicle=self.vehicle,
            to_location=self.showroom,
            reason="Showroom display"
        )

        VehicleMovement.objects.create(
            vehicle=self.vehicle,
            to_location=self.service_center,
            reason="Service"
        )

        self.assertEqual(
            self.vehicle.movements.count(),
            2
        )

    def test_multiple_transfers_track_previous_location(self):
        first_movement = VehicleMovement.objects.create(
            vehicle=self.vehicle,
            to_location=self.showroom,
            reason="Showroom display"
        )

        second_movement = VehicleMovement.objects.create(
            vehicle=self.vehicle,
            to_location=self.service_center,
            reason="Service"
        )

        self.assertEqual(
            first_movement.from_location,
            self.stockyard
        )

        self.assertEqual(
            second_movement.from_location,
            self.showroom
        )

        self.vehicle.refresh_from_db()

        self.assertEqual(
            self.vehicle.current_location,
            self.service_center
        )