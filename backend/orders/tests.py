from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from products.models import Category, Product
from cart.models import Cart, CartItem
from orders.models import Order


class OrderAPITestCase(APITestCase):
	def setUp(self):
		User = get_user_model()
		self.user = User.objects.create_user(username='tester', email='test@example.com', password='pass')
		# create product
		self.category = Category.objects.create(name='Cat')
		image = SimpleUploadedFile('test.jpg', b'jpegcontent', content_type='image/jpeg')
		self.product = Product.objects.create(seller=self.user, name='Prod', category=self.category, image=image, price='10.00', description='desc')
		# create cart and item
		self.cart = Cart.objects.create(user=self.user)
		CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)

	def test_create_order_success(self):
		self.client.force_authenticate(user=self.user)
		url = reverse('create-order')
		resp = self.client.post(url)
		self.assertEqual(resp.status_code, 201)
		self.assertEqual(Order.objects.filter(user=self.user).count(), 1)
		# cart should be emptied
		self.assertEqual(self.cart.items.count(), 0)

	def test_create_order_empty_cart(self):
		# empty the cart
		self.cart.items.all().delete()
		self.client.force_authenticate(user=self.user)
		url = reverse('create-order')
		resp = self.client.post(url)
		self.assertEqual(resp.status_code, 400)
		self.assertIn('detail', resp.data)

	def test_order_list_and_detail(self):
		self.client.force_authenticate(user=self.user)
		# create order
		create_url = reverse('create-order')
		create_resp = self.client.post(create_url)
		self.assertEqual(create_resp.status_code, 201)
		order_id = create_resp.data['id']

		list_url = reverse('order-list')
		list_resp = self.client.get(list_url)
		self.assertEqual(list_resp.status_code, 200)
		self.assertIsInstance(list_resp.data, list)
		self.assertGreaterEqual(len(list_resp.data), 1)

		detail_url = reverse('order-detail', args=[order_id])
		detail_resp = self.client.get(detail_url)
		self.assertEqual(detail_resp.status_code, 200)
		self.assertIn('items', detail_resp.data)
