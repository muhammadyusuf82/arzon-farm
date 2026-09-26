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

### `GET|POST /api/auth/begin-validation/<phone_number>`

Start signup: send SMS verification code to the phone number.

**Path params:**

| Param | Example |
|-------|---------|
| `phone_number` | `901234567` |

**Body:** none required.

**Responds `200`:**

```json
{
  "detail": "code sent successfully",
  "code": "code_sent_successfully"
}
```

**Errors:**

| Status | `code` | When |
|--------|--------|------|
| `400` | `phone_number_exists` | User already registered |
| `425` | `wait_to_resend` | Code already sent; wait for `resend_time` |

Example `425` body:

```json
{
  "detail": "a code was already sent",
  "resend_time": "2026-09-18 10:00:00.000000+00:00",
  "code": "wait_to_resend"
}
```

---

### `GET|POST /api/auth/validate-phone-number/<phone_number>/<code>`

Confirm SMS code and receive a one-time `user_create_key`.

**Path params:** `phone_number`, `code` (4-digit SMS code).

**Responds `200`:**

```json
{
  "detail": "Congratulations! Here is your user_create_key. If there was a previous one, it is already overwritten.",
  "user_create_key": "<uuid>",
  "code": "user_create_key_received"
}
```

**Errors:**

| Status | `code` |
|--------|--------|
| `400` | `no_validation_requested` |
| `400` | `incorrect_code` |
| `400` | `expired` |

---

### `POST /api/auth/create-user-via-key/<phone_number>/<user_create_key>`

Create account after phone validation. Returns JWT tokens.

**Path params:** `phone_number`, `user_create_key`.

**Send (JSON body):**

```json
{
  "password": "secret123",
  "email": "optional@example.com",
  "metadata": {}
}
```

| Field | Required | Notes |
|-------|----------|-------|
| `password` | yes | write-only |
| `email` | no | |
| `metadata` | no | JSON object |

`phone_number` comes from the URL (not the body).

**Responds `201`:**

```json
{
  "detail": "I am soo proud of you!! These tokens are for all your effort!",
  "refresh": "<refresh_token>",
  "access": "<access_token>",
  "code": "signup_success"
}
```

**Errors:** `400` with `code: wrong_user_create_key`, or serializer validation errors.

---

### `GET /api/auth/view-profile/`

View the authenticated user's profile.

**Auth:** required.

**Responds `200`:**

```json
{
  "phone_number": "901234567",
  "role": "user",
  "metadata": null,
  "email": "user@example.com",
  "is_staff": false,
  "is_superuser": false
}
```

**Errors:** `401` with `code: not_authenticated`.

---

### `PUT|PATCH /api/auth/update-profile/`

Update profile fields.

**Auth:** required.

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
| `PUT` | treated as partial in current code (`partial=True` when method is PUT) |

**Responds `200`:** updated user data (`email`, `metadata`).

**Errors:** `401` not authenticated; `400` validation errors.

---

### `GET|POST /api/auth/update-password-request/`

Request an SMS code to change password.

**Auth:** required.

**Body:** none.

**Responds `200`:**

```json
{
  "detail": "Check your SMS, the code should be there.",
  "code": "sent"
}
```

If a code was already sent recently:

```json
{
  "resend_time": "<datetime>",
  "code": "resend"
}
```

**Errors:** `403` with `code: not_authenticated`.

---

### `GET|POST /api/auth/update-password/<code>/<new_password>`

Set a new password using the SMS code.

**Auth:** required.

**Path params:** `code`, `new_password`.

**Responds `200`:**

```json
{
  "detail": "your new password has been set",
  "code": "success"
}
```

**Errors:**

| Status | `code` |
|--------|--------|
| `401` | `not_authenticated` |
| `400` | `no_code_found` |
| `200`* | `incorrect_code` |
| `400` | `expired` |

\*Incorrect code currently returns HTTP `200` with `code: incorrect_code`.

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

**Body (create/update):** all `User` model fields (`fields = '__all__'`). `password` is write-only and hashed on update.

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
| `POST` | `/api/auth/token/` | public |
| `POST` | `/api/auth/token/refresh/` | public |
| `GET\|POST` | `/api/auth/begin-validation/<phone>/` | public |
| `GET\|POST` | `/api/auth/validate-phone-number/<phone>/<code>/` | public |
| `POST` | `/api/auth/create-user-via-key/<phone>/<key>/` | public |
| `GET` | `/api/auth/view-profile/` | JWT |
| `PUT\|PATCH` | `/api/auth/update-profile/` | JWT |
| `GET\|POST` | `/api/auth/update-password-request/` | JWT |
| `GET\|POST` | `/api/auth/update-password/<code>/<new_password>/` | JWT |
| `CRUD` | `/api/auth/users/` | staff |
| `CRUD` | `/api/tags/` | read public / write staff |
| `CRUD` | `/api/drugs/` | read public / write staff |
| `CRUD` | `/api/pharmacies/` | read public / write auth + owner rules |
| `CRUD` | `/api/stocks/` | read public / write owner rules |
| `CRUD` | `/api/carts/` | JWT |
| `GET` | `/swagger/` | public |
| `GET` | `/redoc/` | public |
