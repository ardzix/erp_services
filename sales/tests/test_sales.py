from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework import status
from common.models import File
from ..models import SalesOrder, Invoice, OrderItem, Product, Unit, Customer
from libs.test import create_user

class SalesOrderViewSetTest(APITestCase):

    def setUp(self):
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        OrderItem.objects.all().delete()
        SalesOrder.objects.all().delete()
        Customer.objects.all().delete()
        Product.objects.all().delete()
        Unit.objects.all().delete()
        self.user.delete()

    def get_customer(self):

        data = {
            "name": "Test Customer",
            "contact_number": "0858123456789",
            "address": "string",
            "location": "1,1"
        }
        response = self.client.post(reverse('customer-list'), data, format='json')
        return Customer.objects.get(id32=response.data['id32'])

    def get_unit(self):

        data = {
            "name": "Packages",
            "symbol": "pcs",
            "conversion_factor": "1"
        }
        response = self.client.post(reverse('unit-list'), data, format='json')
        return Unit.objects.get(id32=response.data['id32'])

    def get_product(self, unit):

        data = {
            "name": "Test product",
            "sku": "string",
            "smallest_unit_id32": unit.id32,
            "product_type": "raw_material",
            "price_calculation": "fifo"
        }
        response = self.client.post(reverse('product-list'), data, format='json')
        return Unit.objects.get(id32=response.data['id32'])

    def test_create_sales_order(self):
        customer = self.get_customer()
        unit = self.get_unit()
        product = self.get_product(unit)

        data = {
            'customer_id32': customer.id32,
            'order_date': '2023-01-01',
            'order_items': [{
                'product_id32': product.id32,
                'unit_id32': unit.id32,
                'quantity': 1,
                'price': 10.0,
            }]
        }

        response = self.client.post(reverse('sales_order-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(SalesOrder.objects.filter(customer=customer).exists())
        self.assertTrue(OrderItem.objects.filter(product=product).exists())

    # def test_retrieve_sales_order(self):
    #     customer = Customer.objects.create(name="Test Customer")
    #     sales_order = SalesOrder.objects.create(customer=customer, order_date="2023-01-01")

    #     response = self.client.get(reverse('sales_order-detail', args=[sales_order.id32]))
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data['id32'], sales_order.id32)

    # def test_retrieve_invoice_for_sales_order(self):
    #     customer = Customer.objects.create(name="Test Customer")
    #     sales_order = SalesOrder.objects.create(customer=customer, order_date="2023-01-01")
    #     invoice = Invoice.objects.create(order=sales_order, invoice_date="2023-01-01")

    #     response = self.client.get(reverse('sales_order-invoice', args=[sales_order.id32]))
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data['id32'], invoice.id32)

# class SalesPaymentViewSetTest(APITestCase):

#     def setUp(self):
#         self.user = create_user()
#         self.client.force_authenticate(user=self.user)

#     def tearDown(self):
#         File.objects.all().delete()
#         Invoice.objects.all().delete()
#         SalesOrder.objects.all().delete()
#         Customer.objects.all().delete()
#         self.user.delete()

#     def test_create_sales_payment(self):
#         customer = Customer.objects.create(name="Test Customer")
#         sales_order = SalesOrder.objects.create(customer=customer, order_date="2023-01-01")
#         invoice = Invoice.objects.create(order=sales_order, invoice_date="2023-01-01")
#         file = File.objects.create(name="test_file")  # Adjust as needed for File model creation

#         data = {
#             'invoice_id32': invoice.id32,
#             'amount': 100,
#             'payment_date': '2023-01-01',
#             'payment_evidence_id32': file.id32,
#             'status': 'test_status'  # Adjust accordingly
#         }

#         response = self.client.post(reverse('sales_payment-list'), data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
