# FairFound Ecommerce Backend Spec (Django REST API)

This document defines the backend requirements that the Ecommerce frontend will consume. The frontend must use real data only — no dummy data. All data is fetched via Django REST API endpoints described here.

## Scope
- Ecommerce domain: products, categories, attributes/variants, pricing, promotions, inventory, orders, carts/checkout, customers, reviews/ratings, analytics snapshots.
- Auth: JWT (SimpleJWT) for login and protected operations.

## Tech Assumptions
- Django 5.x
- Django REST Framework
- PostgreSQL
- `djangorestframework-simplejwt`
- Optional: `django-filter` for filtering, `drf-spectacular` for API docs.

## Environment & Setup
- Required env vars:
  - `DATABASE_URL` or `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
  - `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
- Setup:
  ```powershell
  cd "c:\Users\DELL\Desktop\FairFound\FairFound_Backend_Freelancer"
  python -m venv .venv; .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  python manage.py migrate
  python manage.py runserver
  ```
- Auth: `POST /api/auth/login/` returns JWT tokens. Use `Authorization: Bearer <token>` for protected endpoints.

## Data Models (Ecommerce)
Define these models in an `ecommerce` Django app. Field types are suggestions meant to be practical and DRF-friendly.

### Customer
```
id: UUID (pk)
user: FK(account.User|null)  # allow guest checkout later
email: Email
name: Char(150)
phone: Char(30)|null
created_at: DateTime(auto)
updated_at: DateTime(auto)
```

### Category
```
id: UUID (pk)
slug: Slug(unique)
name: Char(120)
description: Text|null
parent: FK(Category|null)
created_at: DateTime(auto)
```

### Product
```
id: UUID (pk)
slug: Slug(unique)
name: Char(160)
summary: Text
description: Text
category: FK(Category)
images: JSON[list[str]]
attributes: JSON[dict]        # e.g., {color: ["red","blue"], size: ["S","M","L"]}
status: Enum[active|draft|archived]
created_at: DateTime(auto)
updated_at: DateTime(auto)
```

### Variant (SKU)
```
id: UUID (pk)
product: FK(Product, related_name="variants")
sku: Char(80) unique
name: Char(160)|null          # e.g., "Blue / M"
price: Decimal(10,2)
sale_price: Decimal(10,2)|null
currency: Char(3)
stock: Integer                # on-hand
attributes: JSON[dict]        # e.g., {color: "blue", size: "M"}
```

### PricingRule
```
id: UUID (pk)
name: Char(160)
type: Enum[percentage|fixed]
value: Decimal(10,2)          # percentage for type=percentage
applies_to: JSON[dict]        # product/variant IDs or category filter
active: Bool
starts_at: DateTime|null
ends_at: DateTime|null
```

### Promotion
```
id: UUID (pk)
code: Char(40) unique
name: Char(160)
description: Text|null
rule: FK(PricingRule)
active: Bool
usage_limit: Integer|null
used_count: Integer default=0
```

### InventoryMovement
```
id: UUID (pk)
variant: FK(Variant)
change: Integer               # +inbound, -outbound
reason: Char(80)              # sale|refund|adjustment|supplier
metadata: JSON[dict]
created_at: DateTime(auto)
```

### Cart
```
id: UUID (pk)
customer: FK(Customer|null)   # guest carts allowed via token
status: Enum[open|converted|abandoned]
created_at: DateTime(auto)
updated_at: DateTime(auto)
```

### CartItem
```
id: UUID (pk)
cart: FK(Cart, related_name="items")
variant: FK(Variant)
qty: Integer
price_at_add: Decimal(10,2)
```

### Order
```
id: UUID (pk)
order_number: Char(20) unique
customer: FK(Customer|null)
status: Enum[pending|paid|fulfilled|cancelled|refunded]
subtotal: Decimal(10,2)
discount_total: Decimal(10,2)
shipping_total: Decimal(10,2)
tax_total: Decimal(10,2)
grand_total: Decimal(10,2)
currency: Char(3)
payment_ref: Char(80)|null
shipping_address: JSON[dict]
billing_address: JSON[dict]
created_at: DateTime(auto)
updated_at: DateTime(auto)
```

### OrderItem
```
id: UUID (pk)
order: FK(Order, related_name="items")
variant: FK(Variant)
qty: Integer
unit_price: Decimal(10,2)
line_total: Decimal(10,2)
```

### Review
```
id: UUID (pk)
product: FK(Product, related_name="reviews")
customer: FK(Customer|null)
rating: SmallInt (1-5)
comment: Text
created_at: DateTime(auto)
```

### AnalyticsSnapshot
```
id: UUID (pk)
metric: Char(40)      # visibility|conversion_rate|engagement|revenue
value: Decimal(12,2)
breakdown: JSON[dict]
period: Char(20)      # e.g., 2025-11 or week-48
created_at: DateTime(auto)
```

## REST API Endpoints (Ecommerce)
Base: `/api/ecommerce/` (recommended app namespace). Use DRF ViewSets with routers. All endpoints are JWT-protected unless noted.

### Auth (shared)
- `POST /api/auth/login/` — JWT token
- `POST /api/auth/register/` — Register

### Categories
- `GET /api/ecommerce/categories/` — List categories
- `POST /api/ecommerce/categories/` — Create (admin)
- `GET /api/ecommerce/categories/{id}/` — Retrieve
- `PATCH /api/ecommerce/categories/{id}/` — Update (admin)
- `DELETE /api/ecommerce/categories/{id}/` — Delete (admin)

### Products
- `GET /api/ecommerce/products/` — List (filters: `category`, `search`, `status`, `ordering`)
- `POST /api/ecommerce/products/` — Create (admin)
- `GET /api/ecommerce/products/{id}/` — Retrieve
- `PATCH /api/ecommerce/products/{id}/` — Update (admin)
- `DELETE /api/ecommerce/products/{id}/` — Delete (admin)
- `GET /api/ecommerce/products/{id}/variants/` — List variants for product
- `GET /api/ecommerce/products/{slug}/` — Optional slug route

### Variants
- `GET /api/ecommerce/variants/` — List
- `POST /api/ecommerce/variants/` — Create (admin)
- `GET /api/ecommerce/variants/{id}/` — Retrieve
- `PATCH /api/ecommerce/variants/{id}/` — Update (admin)
- `DELETE /api/ecommerce/variants/{id}/` — Delete (admin)

### Pricing & Promotions
- `GET /api/ecommerce/pricing-rules/`
- `POST /api/ecommerce/pricing-rules/` (admin)
- `GET /api/ecommerce/promotions/`
- `POST /api/ecommerce/promotions/` (admin)
- `POST /api/ecommerce/promotions/apply/` — Preview price with a code

### Inventory
- `GET /api/ecommerce/inventory/movements/` — List
- `POST /api/ecommerce/inventory/movements/` — Record movement (admin)

### Carts
- `GET /api/ecommerce/carts/me/` — Get current customer cart (create if none)
- `POST /api/ecommerce/carts/me/items/` — Add item `{variant_id, qty}`
- `PATCH /api/ecommerce/carts/me/items/{id}/` — Update qty
- `DELETE /api/ecommerce/carts/me/items/{id}/` — Remove item
- `POST /api/ecommerce/carts/me/apply-promotion/` — Apply a promotion code
- `POST /api/ecommerce/carts/me/checkout/` — Create order from cart (requires addresses/payment)

### Orders
- `GET /api/ecommerce/orders/me/` — List my orders
- `GET /api/ecommerce/orders/{id}/` — Retrieve order
- `POST /api/ecommerce/orders/` — Admin/manual create
- `PATCH /api/ecommerce/orders/{id}/` — Update status (admin)

### Reviews
- `GET /api/ecommerce/products/{id}/reviews/` — List reviews
- `POST /api/ecommerce/products/{id}/reviews/` — Create review
- `DELETE /api/ecommerce/reviews/{id}/` — Delete (owner/admin)

### Analytics
- `GET /api/ecommerce/analytics/snapshots/` — List snapshots (filters: `metric`, `period`)
- `GET /api/ecommerce/analytics/metrics/` — Aggregated metrics for dashboard/roadmap

## Serializer & Response Conventions
- Use DRF serializers for type-safe responses.
- Include `id`, human-friendly fields, and nested relations where useful (e.g., product → variants).
- Paginate list endpoints; support `?page` and `?page_size`.
- Filters via query params (use `django-filter`).
- Errors: `{detail: string}` or serializer field errors dict.

## Frontend Integration Rules (No Dummy Data)
- Configure `VITE_API_BASE_URL` (e.g., `http://127.0.0.1:8000`).
- All product lists, details, cart operations, and roadmap analytics in the ecommerce frontend must call the above endpoints.
- Example fetch:
```ts
const base = import.meta.env.VITE_API_BASE_URL;
const res = await fetch(`${base}/api/ecommerce/products?category=${catId}`, {
  headers: { Authorization: `Bearer ${token}` }
});
const data = await res.json();
```
- Handle loading/errors robustly; never hardcode placeholders.

## Implementation Notes
- Use ViewSets + routers in `ecommerce/urls.py`.
- Add permissions: admin-only for write on catalog/inventory/pricing.
- Cart endpoints key off authenticated user (or a guest token strategy).
- Promotions apply via a service that computes totals.
- Analytics endpoints aggregate orders, reviews, product views (source may be augmented later).

## Developer Tasks Checklist
- Create `ecommerce` app with the models above.
- Write serializers and viewsets; register in `ecommerce/urls.py` under `/api/ecommerce/`.
- Enable CORS for the frontend origin.
- Add tests: models, serializers, endpoint flows (cart→checkout, promotions, inventory).
- Provide seed scripts for categories/products (optional, not dummy usage in UI — only for dev DB).

## References
- DRF: https://www.django-rest-framework.org/
- SimpleJWT: https://django-rest-framework-simplejwt.readthedocs.io/
- django-filter: https://django-filter.readthedocs.io/