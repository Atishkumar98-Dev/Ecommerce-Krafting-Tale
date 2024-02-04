# tests.py
from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Order, OrderItem, Product, ProductVariant, Customer, Category
from rest_framework import status
import json

class CartViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Admin12', password='Admin12')
        self.customer = Customer.objects.create(user=self.user)
        self.product = Product.objects.create(name='Test Product')
        self.variant = ProductVariant.objects.create(product=self.product, price=10)
        self.order = Order.objects.create(customer=self.customer, status='Pending')
        self.order_item = OrderItem.objects.create(order=self.order, product_variant=self.variant, quantity=2)

    def test_html_rendering(self):
        client = Client()
        client.login(username='Admin', password='123')
        response = client.get('/cart/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart.html')
        self.assertInHTML('<div>Total Price: 20</div>', response.content.decode('utf-8'))

    def test_api_response(self):
        client = Client()
        client.login(username='Admin12', password='Admin12')
        response = client.get('/cart/', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content.decode('utf-8'))
        self.assertIn('order_items', data)
        self.assertIn('total_price', data)
        self.assertEqual(len(data['order_items']), 1)
        self.assertEqual(data['total_price'], 20)
