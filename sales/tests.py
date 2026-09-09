from django.test import TestCase
from decimal import Decimal
from datetime import date

from customers.models import Customer
from inventory.models import Brand, CarModel, Vehicle

from .models import Sale


class SaleModelTests(TestCase):

    def setUp(self):

        self.customer = Customer.objects.create(
            customer_type='INDIVIDUAL',
            first_name='Test',
            last_name='Customer',
            phone='9876543210',
            email='test@example.com',
        )

        self.brand = Brand.objects.create(
            name='Test Brand'
        )

        self.car_model = CarModel.objects.create(
            brand=self.brand,
            name='Test Model'
        )

        self.vehicle = Vehicle.objects.create(
            vin_number='SALETESTVIN001',
            registration_number='SALETESTREG001',
            engine_number='SALETESTENG001',
            brand=self.brand,
            car_model=self.car_model,
            manufacturing_year=2026,
            color='White',
            fuel_type='PETROL',
            transmission='MANUAL',
            mileage=0,
            purchase_price=Decimal('1000000.00'),
            selling_price=Decimal('1200000.00'),
            status='IN_STOCK',
            location='Test Stockyard',
            arrival_date=date.today(),
            ownership_count=1,
        )

    def create_sale(self):

        return Sale.objects.create(
            sale_number='SALE-001',
            customer=self.customer,
            vehicle=self.vehicle,
            sale_price=Decimal('1200000.00'),
            discount=Decimal('50000.00'),
            tax_amount=Decimal('207000.00'),
            final_amount=Decimal('1357000.00'),
            amount_paid=Decimal('500000.00'),
        )

    def test_sale_can_be_created(self):

        sale = self.create_sale()

        self.assertEqual(
            Sale.objects.count(),
            1
        )

        self.assertEqual(
            sale.sale_number,
            'SALE-001'
        )

    def test_balance_amount_is_calculated(self):

        sale = self.create_sale()

        self.assertEqual(
            sale.balance_amount,
            Decimal('857000.00')
        )

    def test_sale_profit_is_calculated(self):

        sale = self.create_sale()

        self.assertEqual(
            sale.profit,
            Decimal('357000.00')
        )

    def test_sale_defaults_to_pending_payment(self):

        sale = self.create_sale()

        self.assertEqual(
            sale.payment_status,
            'PENDING'
        )

    def test_sale_defaults_to_draft(self):

        sale = self.create_sale()

        self.assertEqual(
            sale.sale_status,
            'DRAFT'
        )

    def test_sale_defaults_to_pending_delivery(self):

        sale = self.create_sale()

        self.assertEqual(
            sale.delivery_status,
            'PENDING'
        )

    def test_vehicle_can_have_only_one_sale(self):

        self.create_sale()

        with self.assertRaises(Exception):

            Sale.objects.create(
                sale_number='SALE-002',
                customer=self.customer,
                vehicle=self.vehicle,
                sale_price=Decimal('1200000.00'),
                final_amount=Decimal('1200000.00'),
            )