# FairFound Ecommerce Backend - Developer Guide

This document provides instructions for setting up and running the FairFound Ecommerce Backend API.

## Prerequisites

- Python 3.11 or higher
- PostgreSQL (optional, SQLite is used by default for development)

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd FairFound_Backend_Ecommerce

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the project root or set the following environment variables:

```bash
# Required
SECRET_KEY=your-secret-key-here

# Optional (defaults shown)
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite is used if not set)
DATABASE_URL=postgres://user:password@localhost:5432/dbname
# OR
DB_NAME=dbname
DB_USER=user
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# CORS
CORS_ALLOW_ALL_ORIGINS=True
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 3. Database Setup

```bash
cd ff_be_ecom

# Run migrations
python manage.py migrate

# Create a superuser (for admin access)
python manage.py createsuperuser
```

### 4. Run the Development Server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

## API Endpoints

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register/` | POST | Register a new user |
| `/api/auth/login/` | POST | Login and get tokens |
| `/api/auth/token/refresh/` | POST | Refresh access token |
| `/api/auth/me/` | GET | Get current user info |

### Ecommerce

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ecommerce/categories/` | GET, POST | List/create categories |
| `/api/ecommerce/categories/{id}/` | GET, PATCH, DELETE | Retrieve/update/delete category |
| `/api/ecommerce/products/` | GET, POST | List/create products |
| `/api/ecommerce/products/{id}/` | GET, PATCH, DELETE | Retrieve/update/delete product |
| `/api/ecommerce/products/{id}/variants/` | GET | List product variants |
| `/api/ecommerce/products/{id}/reviews/` | GET, POST | List/create product reviews |
| `/api/ecommerce/variants/` | GET, POST | List/create variants |
| `/api/ecommerce/variants/{id}/` | GET, PATCH, DELETE | Retrieve/update/delete variant |
| `/api/ecommerce/pricing-rules/` | GET, POST | List/create pricing rules (admin) |
| `/api/ecommerce/promotions/` | GET, POST | List/create promotions |
| `/api/ecommerce/promotions/apply/` | POST | Preview promotion discount |
| `/api/ecommerce/inventory/movements/` | GET, POST | List/create inventory movements (admin) |
| `/api/ecommerce/carts/me/` | GET | Get current user's cart |
| `/api/ecommerce/carts/me/items/` | POST | Add item to cart |
| `/api/ecommerce/carts/me/items/{id}/` | PATCH, DELETE | Update/remove cart item |
| `/api/ecommerce/carts/me/apply-promotion/` | POST | Apply promotion to cart |
| `/api/ecommerce/carts/me/checkout/` | POST | Checkout and create order |
| `/api/ecommerce/orders/` | GET, POST | List orders (admin can create) |
| `/api/ecommerce/orders/me/` | GET | List current user's orders |
| `/api/ecommerce/orders/{id}/` | GET, PATCH | Retrieve/update order |
| `/api/ecommerce/reviews/` | GET | List all reviews |
| `/api/ecommerce/reviews/{id}/` | DELETE | Delete review (owner/admin) |
| `/api/ecommerce/analytics/snapshots/` | GET, POST | List/create analytics snapshots (admin) |
| `/api/ecommerce/analytics/snapshots/metrics/` | GET | Get aggregated metrics |

## Authentication

The API uses JWT (JSON Web Token) authentication via `djangorestframework-simplejwt`.

### Registration

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "user@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "name": "New User"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "SecurePass123!"
  }'
```

### Using Tokens

Include the access token in the `Authorization` header:

```bash
curl -X GET http://localhost:8000/api/ecommerce/products/ \
  -H "Authorization: Bearer <access_token>"
```

## Testing

Run tests with:

```bash
cd ff_be_ecom
python manage.py test ecommerce
```

## Admin Interface

Access the Django admin at `http://127.0.0.1:8000/admin/` using your superuser credentials.

## Project Structure

```
ff_be_ecom/
├── ff_be_ecom/           # Project settings
│   ├── settings.py       # Django settings
│   ├── urls.py          # Root URL configuration
│   └── wsgi.py          # WSGI configuration
├── ecommerce/           # Main ecommerce app
│   ├── models.py        # Data models
│   ├── serializers.py   # DRF serializers
│   ├── views.py         # ViewSets and views
│   ├── urls.py          # API routes
│   ├── admin.py         # Admin configuration
│   └── tests.py         # Unit tests
├── authentication/      # Authentication app
│   ├── serializers.py   # Auth serializers
│   ├── views.py         # Auth views
│   └── urls.py          # Auth routes
└── manage.py
```

## Models

- **Customer**: User profiles (linked to Django User)
- **Category**: Hierarchical product categories
- **Product**: Products with attributes and images
- **Variant**: Product SKUs with pricing and stock
- **PricingRule**: Discount rules (percentage or fixed)
- **Promotion**: Coupon codes linked to pricing rules
- **InventoryMovement**: Stock change tracking
- **Cart/CartItem**: Shopping cart functionality
- **Order/OrderItem**: Completed orders
- **Review**: Product ratings and comments
- **AnalyticsSnapshot**: Aggregated metrics for dashboards
