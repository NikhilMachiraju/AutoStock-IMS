from django.test import TestCase

from .models import Customer


class CustomerModelTests(TestCase):

    def test_individual_customer_can_be_created(self):

        customer = Customer.objects.create(
            customer_type='INDIVIDUAL',
            first_name='Nikhil',
            last_name='Test',
            phone='9876543210',
            email='nikhil@example.com',
            city='Vijayawada',
            state='Andhra Pradesh',
            postal_code='520001',
        )

        self.assertEqual(
            Customer.objects.count(),
            1
        )

        self.assertEqual(
            customer.customer_type,
            'INDIVIDUAL'
        )

        self.assertEqual(
            str(customer),
            'Nikhil Test'
        )


    def test_business_customer_can_be_created(self):

        customer = Customer.objects.create(
            customer_type='BUSINESS',
            first_name='Business',
            company_name='Test Motors',
            phone='9876543211',
            email='business@example.com',
            city='Hyderabad',
            state='Telangana',
        )

        self.assertEqual(
            Customer.objects.count(),
            1
        )

        self.assertEqual(
            str(customer),
            'Test Motors'
        )


    def test_customer_defaults_to_active(self):

        customer = Customer.objects.create(
            first_name='Active',
            last_name='Customer',
            phone='9876543212',
        )

        self.assertEqual(
            customer.status,
            'ACTIVE'
        )


    def test_customer_can_be_marked_inactive(self):

        customer = Customer.objects.create(
            first_name='Inactive',
            last_name='Customer',
            phone='9876543213',
            status='INACTIVE',
        )

        self.assertEqual(
            customer.status,
            'INACTIVE'
        )


    def test_optional_fields_can_be_blank(self):

        customer = Customer.objects.create(
            first_name='Minimal',
            phone='9876543214',
        )

        self.assertEqual(
            customer.last_name,
            ''
        )

        self.assertEqual(
            customer.email,
            ''
        )

        self.assertEqual(
            customer.city,
            ''
        )