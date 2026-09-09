from django.test import TestCase

from inventory.models import Brand, CarModel, Variant, Vehicle
from .models import Location


class LocationModelTest(TestCase):

    def setUp(self):
        self.location = Location.objects.create(
            name='Main Stockyard',
            location_type='STOCKYARD',
            address='Main Vehicle Storage',
            city='Vijayawada',
            contact_person='Manager',
            phone='9999999999',
            is_active=True
        )

    def test_location_created_successfully(self):
        self.assertEqual(
            self.location.name,
            'Main Stockyard'
        )

        self.assertEqual(
            self.location.location_type,
            'STOCKYARD'
        )

        self.assertTrue(
            self.location.is_active
        )

    def test_location_string_representation(self):
        self.assertEqual(
            str(self.location),
            'Main Stockyard - Stockyard'
        )


class VehicleLocationTest(TestCase):

    def setUp(self):
        self.brand = Brand.objects.create(
            name='Toyota'
        )

        self.car_model = CarModel.objects.create(
            name='Fortuner',
            brand=self.brand
        )

        self.variant = Variant.objects.create(
            name='Legender',
            car_model=self.car_model
        )

        self.location = Location.objects.create(
            name='Vijayawada Showroom',
            location_type='SHOWROOM',
            city='Vijayawada'
        )

        self.vehicle = Vehicle.objects.create(
            vin_number='TESTVIN12345678901',
            registration_number='AP39TEST1234',
            engine_number='TESTENGINE12345',
            brand=self.brand,
            car_model=self.car_model,
            vehicle_variant=self.variant,
            arrival_date='2026-09-01',
            manufacturing_year=2024,
            color='Black',
            fuel_type='PETROL',
            transmission='AUTOMATIC',
            mileage=1000,
            purchase_price=3000000,
            selling_price=3500000,
            status='AVAILABLE',
            current_location=self.location
        )

    def test_vehicle_has_current_location(self):
        self.assertEqual(
            self.vehicle.current_location,
            self.location
        )

        self.assertEqual(
            self.location.vehicles.count(),
            1
        )

    def test_vehicle_current_location_set_null_when_deleted(self):
        self.location.delete()

        self.vehicle.refresh_from_db()

        self.assertIsNone(
            self.vehicle.current_location
        )