# Arzon Farm API

Base URL (local): `http://127.0.0.1:8000`

Interactive docs:

- Swagger UI: [`/swagger/`](http://127.0.0.1:8000/swagger/)
- ReDoc: [`/redoc/`](http://127.0.0.1:8000/redoc/)

## Authentication

Most write endpoints require a JWT access token.

```http
Authorization: Bearer <access_token>
```

Token lifetimes (current settings):

- Access token: **1 day**
- Refresh token: **4 days**

User roles: `user` | `pharmacy` | `courier`

---

## Authorization (`/api/auth/`)

No SMS verification. Sign up with `POST /api/auth/register/` if the phone number is free; log in with tokens.

### `POST /api/auth/register/`

Create a user when that phone number does not exist yet. Returns JWT tokens.

**Auth:** public.

**Send (JSON body):**

```json
{
  "phone_number": "901234567",
  "password": "secret12",
  "email": "optional@example.com",
  "role": "user",
  "metadata": { "name": "Ali" }
}
```

| Field | Required | Notes |
|-------|----------|-------|
| `phone_number` | yes | unique, max 9 chars |
| `password` | yes | write-only, min 6 chars |
| `email` | no | |
| `role` | no | `user` (default), `pharmacy`, or `courier` |
| `metadata` | no | JSON object |

**Responds `201`:**

```json
{
  "detail": "user created successfully",
  "code": "signup_success",
  "refresh": "<refresh_token>",
  "access": "<access_token>",
  "user": {
    "id": 7,
    "phone_number": "901234567",
    "email": "optional@example.com",
    "role": "user",
    "metadata": { "name": "Ali" }
  }
}
```

**Errors `400`:** phone already taken or validation errors, e.g.

```json
{
  "phone_number": ["user with this phone number already exists."]
}
```

---

### `POST /api/auth/token/`

Login. Obtain JWT access + refresh tokens.

**Send (JSON body):**

```json
{
  "phone_number": "901234567",
  "password": "your_password"
}
```

> `USERNAME_FIELD` is `phone_number` (not username).

**Responds `200`:**

```json
{
  "refresh": "<refresh_token>",
  "access": "<access_token>"
}
```

**Errors:** `401` invalid credentials.

---

### `POST /api/auth/token/refresh/`

Renew access token.

**Send:**

```json
{
  "refresh": "<refresh_token>"
}
```

**Responds `200`:**

```json
{
  "access": "<new_access_token>"
}
```

---

### `GET /api/auth/view-profile/`

View the authenticated user's profile.

**Auth:** JWT required.

**Responds `200`:**

```json
{
  "id": 7,
  "phone_number": "901234567",
  "role": "user",
  "metadata": null,
  "email": "user@example.com",
  "is_staff": false,
  "is_superuser": false
}
```

**Errors:** `401` if not authenticated.

---

### `PUT|PATCH /api/auth/update-profile/`

Update profile fields.

**Auth:** JWT required.

**Send:**

```json
{
  "email": "new@example.com",
  "metadata": { "name": "Ali" }
}
```

| Method | Behavior |
|--------|----------|
| `PATCH` | partial update (only sent fields) |
| `PUT` | full update of serializer fields |

**Responds `200`:**

```json
{
  "email": "new@example.com",
  "metadata": { "name": "Ali" }
}
```

**Errors:** `401` not authenticated; `400` validation errors.

---

### `POST /api/auth/change-password/`

Change password for the authenticated user (no SMS).

**Auth:** JWT required.

**Send:**

```json
{
  "old_password": "secret12",
  "new_password": "newpass99"
}
```

| Field | Required | Notes |
|-------|----------|-------|
| `old_password` | yes | must match current password |
| `new_password` | yes | min 6 chars |

**Responds `200`:**

```json
{
  "detail": "password updated successfully",
  "code": "success"
}
```

**Errors:** `401` not authenticated; `400` if `old_password` is wrong or `new_password` is too short.

---

### Users admin CRUD (`/api/auth/users/`)

Admin-only (`IsAdminUser` / staff). Full ModelViewSet.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/auth/users/` | List all users |
| `POST` | `/api/auth/users/` | Create user |
| `GET` | `/api/auth/users/{id}/` | Retrieve user |
| `PUT` | `/api/auth/users/{id}/` | Full update |
| `PATCH` | `/api/auth/users/{id}/` | Partial update |
| `DELETE` | `/api/auth/users/{id}/` | Delete user |

**Auth:** staff/admin JWT required.

**Body (create/update):** all `User` model fields (`fields = '__all__'`). `password` is write-only and hashed on create/update.

**Response:** user object (password never returned).

---

## Pharmacies app (`/api/`)

Standard DRF pagination is not configured — list endpoints return a JSON array (or paginated shape if you add pagination later).

### Tags — `/api/tags/`

| Method | Endpoint | Auth |
|--------|----------|------|
| `GET` | `/api/tags/` | public (read) |
| `GET` | `/api/tags/{id}/` | public (read) |
| `POST` | `/api/tags/` | staff |
| `PUT`/`PATCH` | `/api/tags/{id}/` | staff |
| `DELETE` | `/api/tags/{id}/` | staff |

**Permissions:** `IsAuthenticatedOrReadOnly` + `IsAdmin` (writes need `is_staff`).

**Send (create/update):**

```json
{
  "name": "antibiotics",
  "slug": "antibiotics"
}
```

| Field | Required | Notes |
|-------|----------|-------|
| `name` | yes | unique |
| `slug` | no | unique, nullable |

**Responds:**

```json
{
  "id": 1,
  "slug": "antibiotics",
  "name": "antibiotics"
}
```

---

### Drugs — `/api/drugs/`

| Method | Endpoint | Auth |
|--------|----------|------|
| `GET` | `/api/drugs/` | public |
| `GET` | `/api/drugs/{id}/` | public |
| `POST` | `/api/drugs/` | staff |
| `PUT`/`PATCH` | `/api/drugs/{id}/` | staff |
| `DELETE` | `/api/drugs/{id}/` | staff |

**Permissions:** `IsAuthenticatedOrReadOnly` + `IsAdmin`.

**Send (create/update):**

```json
{
  "name": "Aspirin",
  "inn": "Acetylsalicylic acid",
  "barcode": "4600000000001",
  "manufacturer": "Bayer",
  "is_prescription_required": false,
  "tags_ids": [1, 2]
}
```

| Field | Required | Notes |
|-------|----------|-------|
| `name` | yes | |
| `inn` | yes | International Nonproprietary Name |
| `barcode` | no | unique if set |
| `manufacturer` | yes | |
| `is_prescription_required` | no | default `false` |
| `tags_ids` | no | write-only list of tag PKs |

**Responds:**

```json
{
  "id": 1,
  "name": "Aspirin",
  "inn": "Acetylsalicylic acid",
  "barcode": "4600000000001",
  "manufacturer": "Bayer",
  "is_prescription_required": false,
  "tags": [
    { "id": 1, "slug": "pain", "name": "pain" }
  ]
}
```

`tags` is read-only nested data. Use `tags_ids` to assign tags on write.

---

### Pharmacies — `/api/pharmacies/`

| Method | Endpoint | Auth |
|--------|----------|------|
| `GET` | `/api/pharmacies/` | public |
| `GET` | `/api/pharmacies/{id}/` | public |
| `POST` | `/api/pharmacies/` | authenticated |
| `PUT`/`PATCH` | `/api/pharmacies/{id}/` | owner or staff |
| `DELETE` | `/api/pharmacies/{id}/` | owner or staff |

**Permissions:** `IsAuthenticatedOrReadOnly` + `IsPharmacyOwner` (object-level for unsafe methods).

**Send (create/update):**

```json
{
  "name": "Pharmacy 24/7",
  "address": "Tashkent, Amir Temur 1"
}
```

| Field | Required | Notes |
|-------|----------|-------|
| `name` | yes | |
| `address` | yes | |
| `owner` | — | **read-only**; set automatically to the authenticated user on create |
| `created_at` | — | read-only |

**Responds:**

```json
{
  "id": 1,
  "owner": 5,
  "name": "Pharmacy 24/7",
  "address": "Tashkent, Amir Temur 1",
  "created_at": "2026-09-18T05:00:00Z"
}
```

**Business rules:**

- One pharmacy per owner (`OneToOne`). Creating a second pharmacy for the same user returns validation error: `"you already have pharmacy accaunt"`.
- Staff can list/update any pharmacy; normal users only see their own for write-related queryset filtering (list/retrieve are public).

---

### Pharmacy stock — `/api/stocks/`

| Method | Endpoint | Auth |
|--------|----------|------|
| `GET` | `/api/stocks/` | public |
| `GET` | `/api/stocks/{id}/` | public |
| `POST` | `/api/stocks/` | authenticated (must own pharmacy) |
| `PUT`/`PATCH` | `/api/stocks/{id}/` | pharmacy owner or staff |
| `DELETE` | `/api/stocks/{id}/` | pharmacy owner or staff |

**Permissions:** `IsAuthenticatedOrReadOnly` + `IsStockOwner`.

**Send (create/update):**

```json
{
  "pharmacy": 1,
  "drug": 3,
  "price": "12500.000",
  "quantity": 50,
  "is_available": true
}
```

| Field | Required | Notes |
|-------|----------|-------|
| `pharmacy` | yes | FK id |
| `drug` | yes | FK id |
| `price` | yes | decimal, max 10 digits, 3 places |
| `quantity` | no | default `0` |
| `is_available` | no | default `true` |

Unique together: `(pharmacy, drug)`.

**Responds:** full stock object with the same fields + `id`.

**Business rules:**

- On create, `pharmacy.owner` must be the current user (otherwise `"you are not the owner"`).
- Staff can manage all stocks.

---

### Carts — `/api/carts/`

| Method | Endpoint | Auth |
|--------|----------|------|
| `GET` | `/api/carts/` | authenticated |
| `GET` | `/api/carts/{id}/` | authenticated (own carts only) |
| `POST` | `/api/carts/` | authenticated |
| `PUT`/`PATCH` | `/api/carts/{id}/` | authenticated (own carts) |
| `DELETE` | `/api/carts/{id}/` | authenticated (own carts) |

**Permissions:** `IsAuthenticated`.

**Send (create/update):**

```json
{
  "pharmacy": 1
}
```

| Field | Required | Notes |
|-------|----------|-------|
| `pharmacy` | yes | FK id |
| `client` | — | read-only; set to current user |
| `created_at` | — | read-only |
| `items` | — | read-only nested list |

**Responds:**

```json
{
  "id": 10,
  "client": 5,
  "pharmacy": 1,
  "created_at": "2026-09-18T05:00:00Z",
  "items": [
    {
      "id": 1,
      "stock_item": 7,
      "quantity": 2,
      "price_at_purchase": "12500.000"
    }
  ]
}
```

**Notes:**

- Users only see their own carts.
- Nested `items` are **read-only** in the API. There is currently no separate cart-item endpoint to add/update items via REST; items would need to be managed in admin/code or a future endpoint.
- Cart item shape (when present): `id`, `stock_item`, `quantity`, `price_at_purchase` (`price_at_purchase` is read-only).

---

## Delivery app (not routed yet)

`delivery` has models/views/serializers for **Couriers** and **Orders**, but they are **not registered** in `core/urls.py` yet, so these endpoints are not reachable until URLs are added.

Intended behavior (from `delivery/views.py`):

| Resource | Methods | Notes |
|----------|---------|-------|
| Couriers | list, retrieve | authenticated; staff sees all, others see active only |
| Orders | full CRUD | authenticated; staff / pharmacy owner / client scoped queryset |
| `PATCH .../orders/{id}/update-status/` | custom action | pharmacy order manager / staff; body: `status`, `courier` |

**Create order body (when wired):**

```json
{
  "cart_id": 10,
  "delivery_type": "delivery",
  "delivery_address": "Street 1",
  "prescription_image": "<file>"
}
```

`delivery_type`: `self_delivery` | `delivery`

Order `status` values: `pending_receipt`, `reviewing`, `approved_assembling`, `ready`, `on_the_way`, `delivered`, `rejected`

---

## Quick reference

| Method | Endpoint | Auth |
|--------|----------|------|
| `POST` | `/api/auth/register/` | public |
| `POST` | `/api/auth/token/` | public |
| `POST` | `/api/auth/token/refresh/` | public |
| `GET` | `/api/auth/view-profile/` | JWT |
| `PUT\|PATCH` | `/api/auth/update-profile/` | JWT |
| `POST` | `/api/auth/change-password/` | JWT |
| `CRUD` | `/api/auth/users/` | staff |
| `CRUD` | `/api/tags/` | read public / write staff |
| `CRUD` | `/api/drugs/` | read public / write staff |
| `CRUD` | `/api/pharmacies/` | read public / write auth + owner rules |
| `CRUD` | `/api/stocks/` | read public / write owner rules |
| `CRUD` | `/api/carts/` | JWT |
| `GET` | `/swagger/` | public |
| `GET` | `/redoc/` | public |
