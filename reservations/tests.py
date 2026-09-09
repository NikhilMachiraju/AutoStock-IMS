from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from customers.models import Customer
from inventory.models import Brand, CarModel, Variant, Vehicle
from reservations.models import Reservation


class ReservationModelTests(TestCase):

    def setUp(self):

        # ------------------------------
        # Create test customer
        # ------------------------------

        self.customer = Customer.objects.create(
            first_name='Test',
            last_name='Customer',
            phone='9999999999',
            email='testcustomer@example.com'
        )

        # ------------------------------
        # Create vehicle master data
        # ------------------------------

        self.brand = Brand.objects.create(
            name='Test Brand'
        )

        self.car_model = CarModel.objects.create(
            brand=self.brand,
            name='Test Model'
        )

        self.variant = Variant.objects.create(
            car_model=self.car_model,
            name='Test Variant'
        )

        # ------------------------------
        # Create test vehicle
        # ------------------------------

        self.vehicle = Vehicle.objects.create(
            vin_number='TESTVIN123456789',
            registration_number='TS09TEST1234',
            engine_number='TESTENGINE123456',

            brand=self.brand,
            car_model=self.car_model,
            vehicle_variant=self.variant,

            manufacturing_year=2026,
            color='White',
            fuel_type='PETROL',
            transmission='MANUAL',
            mileage=0,

            purchase_price=Decimal('1000000.00'),
            selling_price=Decimal('1200000.00'),

            status='IN_STOCK',
            arrival_date=timezone.localdate()
        )

    # ==================================
    # HELPER METHOD
    # ==================================

    def create_reservation(
        self,
        reservation_number='RES-001',
        vehicle=None,
        expiry_date=None,
        deposit_amount=Decimal('1000.00'),
        status='ACTIVE'
    ):

        return Reservation(
            reservation_number=reservation_number,
            customer=self.customer,
            vehicle=vehicle or self.vehicle,
            expiry_date=expiry_date or (
                timezone.localdate() + timedelta(days=7)
            ),
            deposit_amount=deposit_amount,
            status=status
        )

    # ==================================
    # TEST 1
    # ==================================

    def test_past_expiry_date_is_invalid(self):

        reservation = self.create_reservation(
            expiry_date=timezone.localdate() - timedelta(days=1)
        )

        with self.assertRaises(ValidationError):
            reservation.full_clean()

    # ==================================
    # TEST 2
    # ==================================

    def test_negative_deposit_is_invalid(self):

        reservation = self.create_reservation(
            deposit_amount=Decimal('-100.00')
        )

        with self.assertRaises(ValidationError):
            reservation.full_clean()

    # ==================================
    # TEST 3
    # ==================================

    def test_only_one_active_reservation_per_vehicle(self):

        Reservation.objects.create(
            reservation_number='RES-001',
            customer=self.customer,
            vehicle=self.vehicle,
            expiry_date=timezone.localdate() + timedelta(days=7),
            deposit_amount=Decimal('1000.00'),
            status='ACTIVE'
        )

        second_reservation = self.create_reservation(
            reservation_number='RES-002'
        )

        with self.assertRaises(ValidationError):
            second_reservation.full_clean()

                # ==================================
    # TEST 4
    # ==================================

    def test_active_reservation_reserves_vehicle(self):

        reservation = self.create_reservation(
            reservation_number='RES-003'
        )

        reservation.save()

        self.vehicle.refresh_from_db()

        self.assertEqual(
            self.vehicle.status,
            'RESERVED'
        )

    # ==================================
    # TEST 5
    # ==================================

    def test_cancelled_reservation_releases_vehicle(self):

        reservation = self.create_reservation(
            reservation_number='RES-004'
        )

        reservation.save()

        self.vehicle.refresh_from_db()

        self.assertEqual(
            self.vehicle.status,
            'RESERVED'
        )

        reservation.status = 'CANCELLED'
        reservation.save()

        self.vehicle.refresh_from_db()

        self.assertEqual(
            self.vehicle.status,
            'IN_STOCK'
        )