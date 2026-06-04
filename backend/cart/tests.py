from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework import status
from rest_framework.test import APITestCase

from cart.models import Cart, CartItem
from products.models import Category, Product
from users.models import User


class CartAPITests(APITestCase):
	def setUp(self):
		self.buyer = User.objects.create_user(
			username='buyer',
			email='buyer@example.com',
			password='buyerpass123',
			role=User.BUYER,
		)
		self.seller = User.objects.create_user(
			username='seller',
			email='seller@example.com',
			password='sellerpass123',
			role=User.SELLER,
		)
		self.category = Category.objects.create(name='Electronics')
		self.product = Product.objects.create(
			seller=self.seller,
			name='Headphones',
			category=self.category,
			image=SimpleUploadedFile('headphones.jpg', b'fake-image-data', content_type='image/jpeg'),
			price=Decimal('25.00'),
			description='Wireless headphones',
		)
		self.own_product = Product.objects.create(
			seller=self.buyer,
			name='My Product',
			category=self.category,
			image=SimpleUploadedFile('my-product.jpg', b'fake-image-data', content_type='image/jpeg'),
			price=Decimal('40.00'),
			description='Owned by buyer',
		)

	def authenticate(self, user):
		self.client.force_authenticate(user=user)

	def test_add_to_cart_creates_item_and_increments_quantity(self):
		self.authenticate(self.buyer)

		add_url = '/api/cart/add/'
		first_response = self.client.post(
			add_url,
			{'product_id': self.product.id, 'quantity': 2},
			format='json',
		)
		self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(len(first_response.data['items']), 1)
		self.assertEqual(first_response.data['items'][0]['product'], self.product.id)
		self.assertEqual(first_response.data['items'][0]['quantity'], 2)
		self.assertEqual(first_response.data['total_price'], Decimal('50.00'))

		second_response = self.client.post(
			add_url,
			{'product_id': self.product.id, 'quantity': 1},
			format='json',
		)
		self.assertEqual(second_response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(second_response.data['items'][0]['quantity'], 3)
		self.assertEqual(second_response.data['total_price'], Decimal('75.00'))

		cart_item = CartItem.objects.get(cart__user=self.buyer, product=self.product)
		self.assertEqual(cart_item.quantity, 3)

	def test_view_cart_returns_cart_contents(self):
		self.authenticate(self.buyer)
		cart = Cart.objects.create(user=self.buyer)
		CartItem.objects.create(cart=cart, product=self.product, quantity=2)

		response = self.client.get('/api/cart/')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data['items']), 1)
		self.assertEqual(response.data['items'][0]['product'], self.product.id)
		self.assertEqual(response.data['items'][0]['quantity'], 2)
		self.assertEqual(response.data['total_price'], Decimal('50.00'))

	def test_update_quantity_updates_cart_item(self):
		self.authenticate(self.buyer)
		cart = Cart.objects.create(user=self.buyer)
		cart_item = CartItem.objects.create(cart=cart, product=self.product, quantity=1)

		response = self.client.patch(
			f'/api/cart/items/{cart_item.id}/',
			{'quantity': 4},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		cart_item.refresh_from_db()
		self.assertEqual(cart_item.quantity, 4)
		self.assertEqual(response.data['quantity'], 4)

	def test_remove_item_deletes_cart_item(self):
		self.authenticate(self.buyer)
		cart = Cart.objects.create(user=self.buyer)
		cart_item = CartItem.objects.create(cart=cart, product=self.product, quantity=1)

		response = self.client.delete(f'/api/cart/items/{cart_item.id}/delete/')

		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertFalse(CartItem.objects.filter(id=cart_item.id).exists())

	def test_cannot_add_own_product(self):
		self.authenticate(self.buyer)

		response = self.client.post(
			'/api/cart/add/',
			{'product_id': self.own_product.id, 'quantity': 1},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(response.data['detail'], 'You cannot add your own product to the cart.')
		self.assertFalse(Cart.objects.filter(user=self.buyer).exists())
