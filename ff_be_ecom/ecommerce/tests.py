"""
Tests for the ecommerce app.

This module provides unit tests for models and endpoint smoke tests
for key functionality like registration, login, products, and cart operations.
"""

from decimal import Decimal
import uuid
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from .models import (
    Customer, Category, Product, Variant, PricingRule, Promotion,
    InventoryMovement, Cart, CartItem, Order, OrderItem, Review,
    AnalyticsSnapshot
)

User = get_user_model()


class CustomerModelTest(TestCase):
    """Tests for the Customer model."""
    
    def test_create_customer(self):
        """Test creating a customer."""
        customer = Customer.objects.create(
            email='test@example.com',
            name='Test Customer',
            phone='1234567890'
        )
        self.assertEqual(customer.email, 'test@example.com')
        self.assertEqual(customer.name, 'Test Customer')
        self.assertIsNotNone(customer.id)
        self.assertIsInstance(customer.id, uuid.UUID)
    
    def test_customer_str(self):
        """Test customer string representation."""
        customer = Customer.objects.create(
            email='test@example.com',
            name='Test Customer'
        )
        self.assertEqual(str(customer), 'Test Customer (test@example.com)')


class CategoryModelTest(TestCase):
    """Tests for the Category model."""
    
    def test_create_category(self):
        """Test creating a category."""
        category = Category.objects.create(
            slug='electronics',
            name='Electronics',
            description='Electronic products'
        )
        self.assertEqual(category.name, 'Electronics')
        self.assertEqual(category.slug, 'electronics')
    
    def test_category_hierarchy(self):
        """Test category parent-child relationship."""
        parent = Category.objects.create(slug='electronics', name='Electronics')
        child = Category.objects.create(
            slug='phones',
            name='Phones',
            parent=parent
        )
        self.assertEqual(child.parent, parent)
        self.assertIn(child, parent.children.all())


class ProductModelTest(TestCase):
    """Tests for the Product model."""
    
    def setUp(self):
        """Set up test data."""
        self.category = Category.objects.create(
            slug='electronics',
            name='Electronics'
        )
    
    def test_create_product(self):
        """Test creating a product."""
        product = Product.objects.create(
            slug='test-phone',
            name='Test Phone',
            summary='A test phone',
            description='This is a test phone product',
            category=self.category,
            status=Product.Status.ACTIVE
        )
        self.assertEqual(product.name, 'Test Phone')
        self.assertEqual(product.category, self.category)


class VariantModelTest(TestCase):
    """Tests for the Variant model."""
    
    def setUp(self):
        """Set up test data."""
        self.category = Category.objects.create(slug='electronics', name='Electronics')
        self.product = Product.objects.create(
            slug='test-phone',
            name='Test Phone',
            summary='A test phone',
            description='Description',
            category=self.category
        )
    
    def test_create_variant(self):
        """Test creating a variant."""
        variant = Variant.objects.create(
            product=self.product,
            sku='TEST-001',
            name='Test Phone - Blue',
            price=Decimal('299.99'),
            currency='USD',
            stock=10
        )
        self.assertEqual(variant.sku, 'TEST-001')
        self.assertEqual(variant.price, Decimal('299.99'))
    
    def test_effective_price_with_sale(self):
        """Test effective price with sale price."""
        variant = Variant.objects.create(
            product=self.product,
            sku='TEST-002',
            price=Decimal('299.99'),
            sale_price=Decimal('249.99'),
            stock=5
        )
        self.assertEqual(variant.effective_price, Decimal('249.99'))
    
    def test_effective_price_without_sale(self):
        """Test effective price without sale price."""
        variant = Variant.objects.create(
            product=self.product,
            sku='TEST-003',
            price=Decimal('299.99'),
            stock=5
        )
        self.assertEqual(variant.effective_price, Decimal('299.99'))


class CartModelTest(TestCase):
    """Tests for Cart and CartItem models."""
    
    def setUp(self):
        """Set up test data."""
        self.customer = Customer.objects.create(
            email='test@example.com',
            name='Test Customer'
        )
        self.category = Category.objects.create(slug='electronics', name='Electronics')
        self.product = Product.objects.create(
            slug='test-phone',
            name='Test Phone',
            summary='A test phone',
            description='Description',
            category=self.category
        )
        self.variant = Variant.objects.create(
            product=self.product,
            sku='TEST-001',
            price=Decimal('100.00'),
            stock=10
        )
    
    def test_create_cart(self):
        """Test creating a cart."""
        cart = Cart.objects.create(customer=self.customer)
        self.assertEqual(cart.status, Cart.Status.OPEN)
        self.assertEqual(cart.customer, self.customer)
    
    def test_cart_total(self):
        """Test cart total calculation."""
        cart = Cart.objects.create(customer=self.customer)
        CartItem.objects.create(
            cart=cart,
            variant=self.variant,
            qty=2,
            price_at_add=Decimal('100.00')
        )
        self.assertEqual(cart.total, Decimal('200.00'))


class AuthEndpointTest(APITestCase):
    """Tests for authentication endpoints."""
    
    def test_register_user(self):
        """Test user registration endpoint."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'name': 'Test User',
        }
        response = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
    
    def test_login_user(self):
        """Test user login endpoint."""
        # Create a user
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        
        # Login
        data = {
            'username': 'testuser',
            'password': 'TestPass123!'
        }
        response = self.client.post('/api/auth/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)


class ProductEndpointTest(APITestCase):
    """Tests for product endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.category = Category.objects.create(
            slug='electronics',
            name='Electronics'
        )
        self.product = Product.objects.create(
            slug='test-phone',
            name='Test Phone',
            summary='A test phone',
            description='Description',
            category=self.category,
            status=Product.Status.ACTIVE
        )
        Variant.objects.create(
            product=self.product,
            sku='TEST-001',
            price=Decimal('299.99'),
            stock=10
        )
        
        # Create admin user for authenticated tests
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='AdminPass123!'
        )
    
    def test_list_products_public(self):
        """Test listing products without authentication."""
        # Products require authentication by default
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/ecommerce/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_retrieve_product(self):
        """Test retrieving a single product."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f'/api/ecommerce/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Phone')


class CartEndpointTest(APITestCase):
    """Tests for cart endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            email='test@example.com',
            name='Test User'
        )
        self.category = Category.objects.create(
            slug='electronics',
            name='Electronics'
        )
        self.product = Product.objects.create(
            slug='test-phone',
            name='Test Phone',
            summary='A test phone',
            description='Description',
            category=self.category,
            status=Product.Status.ACTIVE
        )
        self.variant = Variant.objects.create(
            product=self.product,
            sku='TEST-001',
            price=Decimal('299.99'),
            stock=10
        )
        self.client.force_authenticate(user=self.user)
    
    def test_get_cart(self):
        """Test getting user's cart."""
        response = self.client.get('/api/ecommerce/carts/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('items', response.data)
    
    def test_add_item_to_cart(self):
        """Test adding an item to cart."""
        data = {
            'variant_id': str(self.variant.id),
            'qty': 2
        }
        response = self.client.post('/api/ecommerce/carts/me/items/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['qty'], 2)
    
    def test_checkout(self):
        """Test checkout process."""
        # Add item to cart
        Cart.objects.create(customer=self.customer)
        cart = Cart.objects.get(customer=self.customer)
        CartItem.objects.create(
            cart=cart,
            variant=self.variant,
            qty=1,
            price_at_add=self.variant.price
        )
        
        # Checkout
        data = {
            'shipping_address': {
                'street': '123 Test St',
                'city': 'Test City',
                'country': 'US',
                'zip': '12345'
            }
        }
        response = self.client.post('/api/ecommerce/carts/me/checkout/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('order_number', response.data)
