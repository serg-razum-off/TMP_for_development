# FastAPI Server Specification

This document provides detailed specifications for all FastAPI routers and endpoints in the Financial Tracker application.

## 📋 Overview

The application uses **FastAPI ≥0.129.0** with **Uvicorn ≥0.40.0** as the ASGI server.

**Key Files**:
- [[main.py]] - Application entry point
- [[create_app.py]] - Application factory
- [[base.py]] - Root endpoint
- [[users.py]] - User endpoints
- [[transactions.py]] - Transaction endpoints

---

## 🏭 Application Factory

**File**: [[create_app.py]]

### `create_app()` Function

```python
def create_app() -> FastAPI:
    """Create FastAPI financial tracker application."""
    app = FastAPI(
        title="Financial Tracker",
        description="Financial tracker API application with CRUD operations",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.include_router(users_router)
    app.include_router(base_router)
    app.include_router(transaction_router)
    return app
```

**Application Metadata**:
- **Title**: "Financial Tracker"
- **Description**: "Financial tracker API application with CRUD operations"
- **Version**: "0.1.0"
- **Docs URL**: `/docs` (Swagger UI)
- **ReDoc URL**: `/redoc`

### Lifespan Management

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI application."""
    logger.info(f">> \n  🔧 Project is starting up on {HOST}:{PORT}")
    try:
        logger.info(">> \n 🔧 Checking database status...")
        with DBManager() as db:
            logger.info("✅ Database is ready and tables are verified.")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    try:
        yield
    finally:
        logger.info(f">> \n  ❌ Project is shutting down on {HOST}:{PORT}")
```

**Startup Actions**:
1. Log startup message with host and port
2. Create database connection to verify database exists
3. If database doesn't exist, [[db_manager.py]] creates it via [[init_db]]
4. Log success or failure
5. Raise exception if database initialization fails

**Shutdown Actions**:
1. Log shutdown message

---

## 🚀 Main Entry Point

**File**: [[main.py]]

```python
import uvicorn
from fin_app import create_app
from fin_app.settings.config import HOST, PORT

app = create_app()

if __name__ == "__main__":
    server_port = int(PORT)  # SR: for docker
    uvicorn.run("fin_app.main:app", host=HOST, port=server_port, reload=True)
```

**Configuration**:
- **Module**: `fin_app.main:app`
- **Host**: From [[config.py]] (default: 127.0.0.1)
- **Port**: From [[config.py]] (default: 8000)
- **Reload**: `True` (auto-reload on code changes)

---

## 🏠 Base Router

**File**: [[base.py]]

### Root Endpoint

```python
@base_router.get("/", response_class=HTMLResponse)
def read_root():
    return """<html>...</html>"""
```

| Property | Value |
|----------|-------|
| **Method** | GET |
| **Path** | `/` |
| **Response Type** | HTMLResponse |
| **Authentication** | None |

**Response**: HTML welcome page with:
- Title: "Financial Tracker API"
- Welcome message
- Link to `/docs` for interactive API documentation

**Use Case**: Landing page for the API, provides user-friendly entry point

---

## 👥 Users Router

**File**: [[users.py]]

### Router Configuration

```python
users_router = APIRouter()
```

No prefix or tags configured. All endpoints are at root level.

---

### 1. Create User

```python
@users_router.post("/users")
def add_user(name: str, email: str):
    with DBManager() as db:
        user = db.add_user(name, email)
    return user
```

| Property | Value |
|----------|-------|
| **Method** | POST |
| **Path** | `/users` |
| **Parameters** | `name` (query), `email` (query) |
| **Returns** | [[User]] model |
| **Status Codes** | 200 (success) |

**Request Example**:
```bash
POST /users?name=Alice&email=alice@example.com
```

**Response Example**:
```json
{
  "id": 1,
  "name": "Alice",
  "email": "alice@example.com",
  "created": "2026-02-16T18:00:00",
  "updated": "2026-02-16T18:00:00"
}
```

**Database Operation**: [[DBManager.add_user]]

---

### 2. Get User by ID

```python
@users_router.get("/user/{user_id}")
def get_user(user_id: int):
    with DBManager() as db:
        user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

| Property | Value |
|----------|-------|
| **Method** | GET |
| **Path** | `/user/{user_id}` |
| **Parameters** | `user_id` (path) |
| **Returns** | [[User]] model |
| **Status Codes** | 200 (success), 404 (not found) |

**Request Example**:
```bash
GET /user/1
```

**Response Example** (Success):
```json
{
  "id": 1,
  "name": "Alice",
  "email": "alice@example.com",
  "created": "2026-02-16T18:00:00",
  "updated": "2026-02-16T18:00:00"
}
```

**Response Example** (Not Found):
```json
{
  "detail": "User not found"
}
```

**Database Operation**: [[DBManager.get_user]]

---

### 3. List All Users

```python
@users_router.get("/users")
def get_list_users():
    with DBManager() as db:
        users = db.list_users()
    return users
```

| Property | Value |
|----------|-------|
| **Method** | GET |
| **Path** | `/users` |
| **Parameters** | None |
| **Returns** | List of [[User]] models |
| **Status Codes** | 200 (success) |

**Request Example**:
```bash
GET /users
```

**Response Example**:
```json
[
  {
    "id": 1,
    "name": "Alice",
    "email": "alice@example.com",
    "created": "2026-02-16T18:00:00",
    "updated": "2026-02-16T18:00:00"
  },
  {
    "id": 2,
    "name": "Bob",
    "email": "bob@example.com",
    "created": "2026-02-16T18:05:00",
    "updated": "2026-02-16T18:05:00"
  }
]
```

**Database Operation**: [[DBManager.list_users]]

---

### 4. Update User

```python
@users_router.put("/users/{user_id}")
def update_user(user_id: int, name: str, email: str):
    with DBManager() as db:
        user = db.update_user(user_id, name, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

| Property | Value |
|----------|-------|
| **Method** | PUT |
| **Path** | `/users/{user_id}` |
| **Parameters** | `user_id` (path), `name` (query), `email` (query) |
| **Returns** | [[User]] model |
| **Status Codes** | 200 (success), 404 (not found) |

**Request Example**:
```bash
PUT /users/1?name=Alice%20Smith&email=alice.smith@example.com
```

**Response Example** (Success):
```json
{
  "id": 1,
  "name": "Alice Smith",
  "email": "alice.smith@example.com",
  "created": "2026-02-16T18:00:00",
  "updated": "2026-02-16T18:30:00"
}
```

**Note**: The `updated` timestamp is automatically updated by the database.

**Database Operation**: [[DBManager.update_user]]

---

### 5. Delete User

```python
@users_router.delete("/users/{user_id}")
def delete_user(user_id: int):
    with DBManager() as db:
        success = db.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully", "user_id": user_id}
```

| Property | Value |
|----------|-------|
| **Method** | DELETE |
| **Path** | `/users/{user_id}` |
| **Parameters** | `user_id` (path) |
| **Returns** | Success message dict |
| **Status Codes** | 200 (success), 404 (not found) |

**Request Example**:
```bash
DELETE /users/1
```

**Response Example** (Success):
```json
{
  "message": "User deleted successfully",
  "user_id": 1
}
```

**Database Operation**: [[DBManager.delete_user]]

> [!WARNING]
> Deleting a user does not cascade delete their transactions due to foreign key constraints. This will cause a database error if the user has transactions.

---

## 💰 Transactions Router

**File**: [[transactions.py]]

### Router Configuration

```python
transaction_router = APIRouter()
```

---

### 1. Create Transaction

```python
@transaction_router.post("/transaction")
def add_transaction(user_id: int, amount: float, category: str, description: str):
    with DBManager() as db:
        transaction = db.add_transaction(user_id, amount, category, description)
    return transaction
```

| Property | Value |
|----------|-------|
| **Method** | POST |
| **Path** | `/transaction` |
| **Parameters** | `user_id`, `amount`, `category`, `description` (all query) |
| **Returns** | [[Transaction]] model or None |
| **Status Codes** | 200 (success) |

**Request Example**:
```bash
POST /transaction?user_id=1&amount=50.0&category=Food&description=Lunch
```

**Response Example**:
```json
{
  "id": 1,
  "user_id": 1,
  "amount": 50.0,
  "description": "Lunch",
  "category": "Food",
  "created": "2026-02-16T18:00:00",
  "updated": "2026-02-16T18:00:00"
}
```

**Validation**: [[Transaction]] model validates category against [[Category]] enum

**Database Operation**: [[DBManager.add_transaction]]

---

### 2. Get Transaction by ID

```python
@transaction_router.get("/transaction/{transaction_id}")
def get_transaction(transaction_id: int):
    with DBManager() as db:
        transaction = db.get_transaction(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction
```

| Property | Value |
|----------|-------|
| **Method** | GET |
| **Path** | `/transaction/{transaction_id}` |
| **Parameters** | `transaction_id` (path) |
| **Returns** | [[Transaction]] model |
| **Status Codes** | 200 (success), 404 (not found) |

**Request Example**:
```bash
GET /transaction/1
```

**Database Operation**: [[DBManager.get_transaction]]

---

### 3. List All Transactions

```python
@transaction_router.get("/transactions")
def list_transactions():
    with DBManager() as db:
        transactions = db.list_transactions()
    return transactions
```

| Property | Value |
|----------|-------|
| **Method** | GET |
| **Path** | `/transactions` |
| **Parameters** | None |
| **Returns** | List of [[Transaction]] models |
| **Status Codes** | 200 (success) |

**Request Example**:
```bash
GET /transactions
```

**Database Operation**: [[DBManager.list_transactions]]

---

### 4. Update Transaction

```python
@transaction_router.put("/transaction/{transaction_id}")
def update_transaction(
    transaction_id: int, user_id: int, amount: float, category: str, description: str
):
    with DBManager() as db:
        transaction = db.update_transaction(
            transaction_id, user_id, amount, category, description
        )
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction
```

| Property | Value |
|----------|-------|
| **Method** | PUT |
| **Path** | `/transaction/{transaction_id}` |
| **Parameters** | `transaction_id` (path), `user_id`, `amount`, `category`, `description` (query) |
| **Returns** | [[Transaction]] model |
| **Status Codes** | 200 (success), 404 (not found) |

**Request Example**:
```bash
PUT /transaction/1?user_id=1&amount=75.0&category=Transport&description=Taxi
```

**Database Operation**: [[DBManager.update_transaction]]

---

### 5. Delete Transaction

```python
@transaction_router.delete("/transaction/{transaction_id}")
def delete_transaction(transaction_id: int):
    with DBManager() as db:
        success = db.delete_transaction(transaction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {
        "message": "Transaction deleted successfully",
        "transaction_id": transaction_id,
    }
```

| Property | Value |
|----------|-------|
| **Method** | DELETE |
| **Path** | `/transaction/{transaction_id}` |
| **Parameters** | `transaction_id` (path) |
| **Returns** | Success message dict |
| **Status Codes** | 200 (success), 404 (not found) |

**Request Example**:
```bash
DELETE /transaction/1
```

**Database Operation**: [[DBManager.delete_transaction]]

---

## 📊 Endpoint Summary

### Users Endpoints

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| POST | `/users` | Create user | None |
| GET | `/user/{user_id}` | Get user | None |
| GET | `/users` | List users | None |
| PUT | `/users/{user_id}` | Update user | None |
| DELETE | `/users/{user_id}` | Delete user | None |

### Transactions Endpoints

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| POST | `/transaction` | Create transaction | None |
| GET | `/transaction/{transaction_id}` | Get transaction | None |
| GET | `/transactions` | List transactions | None |
| PUT | `/transaction/{transaction_id}` | Update transaction | None |
| DELETE | `/transaction/{transaction_id}` | Delete transaction | None |

---

## 🔒 Security Considerations

> [!CAUTION]
> **No Authentication**: The API currently has no authentication or authorization. Anyone can:
> - Create, read, update, delete any user
> - Create, read, update, delete any transaction
> - Access all data

**Recommendations**:
1. Add authentication (OAuth2, JWT, API keys)
2. Implement user-specific data access
3. Add rate limiting
4. Validate user ownership of transactions

---

## 🎯 Best Practices Observed

### 1. Context Manager Pattern
All database operations use `with DBManager() as db:` ensuring proper resource cleanup.

### 2. Consistent Error Handling
404 errors for non-existent resources with descriptive messages.

### 3. RESTful Design
- POST for creation
- GET for retrieval
- PUT for updates
- DELETE for deletion

---

## 📚 Related Documentation

- **Data Models**: [[spec_pydantic.md]]
- **Database Layer**: [[spec_database.md]]
- **Data Flow**: [[02_Data_Flow.md]]
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
