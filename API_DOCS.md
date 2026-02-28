# EastCoast Lubricant - Authentication API Documentation

This document provides a comprehensive guide to the authentication and user management endpoints of the EastCoast Lubricant Backend.

## ── General Information ──────────────────────────────────────────

- **Base URL**: `/api/v1/auth`
- **Standard Response Format**:
    ```json
    {
      "success": true,
      "statusCode": 200,
      "message": "Success message",
      "data": { ... },
      "requestId": "uuid",
      "timestamp": "ISO-8601"
    }
    ```
- **Authentication**: JWT Bearer Token in `Authorization` header.
- **Naming Convention**: Request and Response keys use **camelCase**.

---

## ── Public Endpoints ─────────────────────────────────────────────

### 1. Register Dealer
Create a new dealer account.
- **Method**: `POST`
- **Path**: `/register`
- **Payload**:
    ```json
    {
      "email": "dealer@example.com",
      "password": "StrongPassword123!",
      "businessName": "Mega Lubricants Ltd",
      "province": "Ontario",
      "contactName": "John Doe",
      "phone": "+1 (555) 123-4567"
    }
    ```
- **Success Response (201)**: Returns the created user object.

### 2. Login
Authenticate and receive JWT tokens.
- **Method**: `POST`
- **Path**: `/login`
- **Payload**:
    ```json
    {
      "identifier": "dealer@example.com", 
      "password": "StrongPassword123!"
    }
    ```
    *Note: `identifier` can be either email or phone.*
- **Success Response (200)**:
    ```json
    {
      "data": {
        "accessToken": "eyJhbG...",
        "refreshToken": "eyJhbG...",
        "tokenType": "bearer"
      }
    }
    ```

---

## ── Authenticated Endpoints (Dealer/Admin) ─────────────────────

### 3. Get Current Profile
Fetch the profile of the logged-in user.
- **Method**: `GET`
- **Path**: `/me`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response**: Returns full user object.

### 4. Update Own Profile
- **Method**: `PATCH`
- **Path**: `/me`
- **Payload**: Any combination of `businessName`, `province`, `contactName`, `phone`.

### 5. Refresh Token
Rotate tokens using a valid refresh token.
- **Method**: `POST`
- **Path**: `/refresh`
- **Payload**:
    ```json
    {
      "refreshToken": "<current_refresh_token>"
    }
    ```
- **Success Response (200)**: Returns a new `accessToken` and a fresh `refreshToken`.

### 6. Logout
Invalidate the current session.
- **Method**: `POST`
- **Path**: `/logout`
- **Headers**: `Authorization: Bearer <access_token>`

---

## ── Admin-Only Endpoints ────────────────────────────────────────

### 7. List All Users
- **Method**: `GET`
- **Path**: `/users`
- **Query Params**:
    - `role`: `ADMIN` | `DEALER` (Optional)
    - `isActive`: `true` | `false` (Optional)
- **Response**: Array of user objects.

### 8. Create User (Privileged)
- **Method**: `POST`
- **Path**: `/users`
- **Payload**: Same as Register + `role` (`ADMIN`/`DEALER`) and `isActive`.

### 9. Update User by ID
- **Method**: `PATCH`
- **Path**: `/users/{userId}`
- **Payload**: Allows updating `role`, `isActive`, and `password` in addition to profile fields.

### 10. Soft Delete User
- **Method**: `DELETE`
- **Path**: `/users/{userId}`
- **Success Response**: `204 No Content`.

---

## ── Error Codes ──────────────────────────────────────────────────

| Error Code | Status | Description |
| :--- | :--- | :--- |
| `VALIDATION_ERROR` | 422 | Input data failed schema validation. |
| `AUTHENTICATION_ERROR`| 401 | Invalid credentials or expired token. |
| `AUTHORIZATION_ERROR` | 403 | Insufficient permissions for the action. |
| `NOT_FOUND` | 404 | The requested resource (user) does not exist. |
| `CONFLICT_ERROR` | 409 | Email or Phone already registered. |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests in a short period. |
| `INTERNAL_ERROR` | 500 | Unexpected server error. |
