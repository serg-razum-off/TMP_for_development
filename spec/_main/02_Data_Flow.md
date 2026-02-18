# Data Flow

This document traces the complete lifecycle of data through the Financial Tracker application, from HTTP request to database and back.

## 🔄 Request-Response Lifecycle

### High-Level Flow

```mermaid
sequenceDiagram
    participant Client
    participant Uvicorn
    participant FastAPI
    participant Router
    participant DBManager
    participant SQLite
    participant Pydantic

    Client->>Uvicorn: HTTP Request
    Uvicorn->>FastAPI: ASGI Request
    FastAPI->>Router: Route to endpoint
    Router->>DBManager: Call DB method
    DBManager->>SQLite: Execute SQL
    SQLite-->>DBManager: Raw row data
    DBManager->>Pydantic: Validate & serialize
    Pydantic-->>DBManager: Model instance
    DBManager-->>Router: Return model
    Router-->>FastAPI: Return response
    FastAPI-->>Uvicorn: ASGI Response
    Uvicorn-->>Client: HTTP Response
```

---

## 📥 Input Processing

### 1. User Creation Flow

**Endpoint**: `POST /users?name=John&email=john@example.com`

```mermaid
graph TD
    A[Client sends POST /users] --> B[FastAPI receives request]
    B --> C[Router: add_user function]
    C --> D[Extract query params: name, email]
    D --> E[Create DBManager context]
    E --> F[DBManager.add_user]
    F --> G[Execute INSERT SQL]
    G --> H[Get lastrowid]
    H --> I[DBManager.get_user]
    I --> J[Fetch user row]
    J --> K[Convert sqlite3.Row to dict]
    K --> L[Pydantic User model validation]
    L --> M[Return User instance]
    M --> N[FastAPI serializes to JSON]
    N --> O[Return HTTP 200 with user data]
    
    style A fill:#e1f5ff
    style F fill:#fff4e1
    style L fill:#e8f5e9
    style O fill:#f3e5f5
```

**Code Path**:
1. `routers/users.py::add_user()` - Receives request
2. `db/db_manager.py::add_user()` - Inserts into database
3. `db/db_manager.py::get_user()` - Retrieves created user
4. `models/user.py::User` - Validates and serializes data

**Data Transformations**:
```
Query Params (str, str)
  ↓
SQL Parameters (?, ?)
  ↓
sqlite3.Row (database row)
  ↓
dict (Python dictionary)
  ↓
User (Pydantic model)
  ↓
JSON (HTTP response)
```

---

### 2. Transaction Creation Flow

**Endpoint**: `POST /transaction?user_id=1&amount=50.0&category=Food&description=Lunch`

```mermaid
graph TD
    A[Client sends POST /transaction] --> B[Router: add_transaction]
    B --> C[Extract params: user_id, amount, category, description]
    C --> D[DBManager.add_transaction]
    D --> E{Pydantic Validation}
    E -->|Valid| F[Execute INSERT SQL]
    E -->|Invalid| G[Return None]
    F --> H[Get lastrowid]
    H --> I[DBManager.get_transaction]
    I --> J[Fetch transaction row]
    J --> K[Convert to dict]
    K --> L[Pydantic Transaction model]
    L --> M[Return Transaction instance]
    G --> N[Return validation error]
    
    style E fill:#fff9c4
    style F fill:#c8e6c9
    style G fill:#ffcdd2
    style L fill:#e8f5e9
```

**Validation Layer**:
- **Pre-insert validation**: Transaction model validates data before SQL execution
- **Category validation**: Enum ensures only valid categories (Food, Transport, Housing, Entertainment, Other)
- **Type validation**: Pydantic ensures correct types (int, float, str)

**Code Path**:
1. `routers/transactions.py::add_transaction()` - Receives request
2. `db/db_manager.py::add_transaction()` - Validates with Pydantic
3. If valid: Insert into database
4. `db/db_manager.py::get_transaction()` - Retrieves created transaction
5. `models/transaction.py::Transaction` - Final validation and serialization

---

## 📤 Output Processing

### 3. User Retrieval Flow

**Endpoint**: `GET /user/1`

```mermaid
graph TD
    A[Client sends GET /user/1] --> B[Router: get_user]
    B --> C[Extract path param: user_id]
    C --> D[DBManager.get_user]
    D --> E[Execute SELECT SQL]
    E --> F{User exists?}
    F -->|Yes| G[sqlite3.Row]
    F -->|No| H[Return None]
    G --> I[Convert to dict]
    I --> J[Pydantic User model]
    J --> K[Return User instance]
    K --> L[FastAPI serializes to JSON]
    L --> M[HTTP 200 with user data]
    H --> N[Router raises HTTPException]
    N --> O[HTTP 404 Not Found]
    
    style F fill:#fff9c4
    style J fill:#e8f5e9
    style M fill:#c8e6c9
    style O fill:#ffcdd2
```

**Error Handling**:
- Database returns `None` if user not found
- Router checks for `None` and raises `HTTPException(status_code=404)`
- FastAPI converts exception to proper HTTP response

---

### 4. List Operations Flow

**Endpoint**: `GET /users`

```mermaid
graph TD
    A[Client sends GET /users] --> B[Router: get_list_users]
    B --> C[DBManager.list_users]
    C --> D[Execute SELECT * SQL]
    D --> E[Fetch all rows]
    E --> F[List of sqlite3.Row objects]
    F --> G[Iterate over rows]
    G --> H[Convert each row to dict]
    H --> I[Pydantic User model for each]
    I --> J[List of User instances]
    J --> K[FastAPI serializes list to JSON array]
    K --> L[HTTP 200 with users array]
    
    style F fill:#e1f5ff
    style I fill:#e8f5e9
    style L fill:#c8e6c9
```

**Data Transformation**:
```
SQL Query
  ↓
List[sqlite3.Row]
  ↓
List[dict]
  ↓
List[User]
  ↓
JSON Array
```

---

## 🔄 Update Operations

### 5. User Update Flow

**Endpoint**: `PUT /users/1?name=Jane&email=jane@example.com`

```mermaid
graph TD
    A[Client sends PUT /users/1] --> B[Router: update_user]
    B --> C[Extract user_id, name, email]
    C --> D[DBManager.update_user]
    D --> E[Execute UPDATE SQL]
    E --> F[Commit transaction]
    F --> G[DBManager.get_user]
    G --> H{User exists?}
    H -->|Yes| I[Return updated User]
    H -->|No| J[Return None]
    I --> K[HTTP 200 with updated user]
    J --> L[Router raises HTTPException]
    L --> M[HTTP 404 Not Found]
    
    style E fill:#fff4e1
    style I fill:#c8e6c9
    style M fill:#ffcdd2
```

**Important Notes**:
- Update uses `CURRENT_TIMESTAMP` for `updated` field automatically
- Returns full user object after update for verification
- Validates existence after update to ensure operation succeeded

---

### 6. Transaction Update Flow

**Endpoint**: `PUT /transaction/1?user_id=1&amount=75.0&category=Transport&description=Taxi`

```mermaid
graph TD
    A[Client sends PUT /transaction/1] --> B[Router: update_transaction]
    B --> C[Extract all parameters]
    C --> D[DBManager.update_transaction]
    D --> E{Pydantic Validation}
    E -->|Valid| F[Execute UPDATE SQL]
    E -->|Invalid| G[Print error, return None]
    F --> H[Commit with updated timestamp]
    H --> I[DBManager.get_transaction]
    I --> J{Transaction exists?}
    J -->|Yes| K[Return updated Transaction]
    J -->|No| L[Return None]
    K --> M[HTTP 200 with updated transaction]
    G --> N[Router raises HTTPException]
    L --> N
    N --> O[HTTP 404 Not Found]
    
    style E fill:#fff9c4
    style F fill:#fff4e1
    style K fill:#c8e6c9
    style O fill:#ffcdd2
```

**Validation**:
- Pre-update validation ensures data integrity
- Prevents invalid data from reaching database
- Validation errors are logged but return generic 404 to client

---

## 🗑️ Delete Operations

### 7. Delete Flow

**Endpoint**: `DELETE /users/1` or `DELETE /transaction/1`

```mermaid
graph TD
    A[Client sends DELETE request] --> B[Router: delete function]
    B --> C[Extract ID from path]
    C --> D[DBManager.delete_* method]
    D --> E[Execute DELETE SQL]
    E --> F[Check cursor.rowcount]
    F --> G{Rows deleted > 0?}
    G -->|Yes| H[Commit, return True]
    G -->|No| I[Commit, return False]
    H --> J[Return success message with ID]
    I --> K[Router raises HTTPException]
    K --> L[HTTP 404 Not Found]
    
    style F fill:#fff9c4
    style J fill:#c8e6c9
    style L fill:#ffcdd2
```

**Response Format** (Success):
```json
{
  "message": "User deleted successfully",
  "user_id": 1
}
```

---

## 🚀 Application Lifecycle

### Startup Sequence

```mermaid
sequenceDiagram
    participant Main
    participant Uvicorn
    participant FastAPI
    participant Lifespan
    participant DBManager
    participant init_db

    Main->>Uvicorn: uvicorn.run()
    Uvicorn->>FastAPI: Start application
    FastAPI->>Lifespan: Enter lifespan context
    Lifespan->>Lifespan: Log startup message
    Lifespan->>DBManager: Create context manager
    DBManager->>DBManager: Check if DB exists
    alt DB does not exist
        DBManager->>init_db: Initialize database
        init_db->>init_db: Create tables
    end
    DBManager->>Lifespan: Connection successful
    Lifespan->>Lifespan: Log success
    Lifespan->>FastAPI: Ready to serve
    FastAPI-->>Uvicorn: Application ready
```

**Key Steps**:
1. `main.py` starts uvicorn server
2. FastAPI application created by `create_app()`
3. Lifespan context manager enters
4. Database connection tested
5. If database doesn't exist, `init_db()` creates it
6. Application ready to accept requests

---

### Shutdown Sequence

```mermaid
sequenceDiagram
    participant Signal
    participant Uvicorn
    participant FastAPI
    participant Lifespan

    Signal->>Uvicorn: SIGTERM/SIGINT
    Uvicorn->>FastAPI: Shutdown signal
    FastAPI->>Lifespan: Exit lifespan context
    Lifespan->>Lifespan: Log shutdown message
    Lifespan-->>FastAPI: Cleanup complete
    FastAPI-->>Uvicorn: Shutdown complete
```

---

## 🔐 Data Validation Points

### Validation Layers

```mermaid
graph TD
    A[Client Input] --> B{FastAPI Path/Query Validation}
    B -->|Valid| C[Router Function]
    B -->|Invalid| D[422 Unprocessable Entity]
    C --> E{Pydantic Model Validation}
    E -->|Valid| F[Database Operation]
    E -->|Invalid| G[Return None / Error]
    F --> H{Database Constraints}
    H -->|Valid| I[Success]
    H -->|Invalid| J[SQL Error]
    
    style B fill:#fff9c4
    style E fill:#fff9c4
    style H fill:#fff9c4
    style I fill:#c8e6c9
    style D fill:#ffcdd2
    style G fill:#ffcdd2
    style J fill:#ffcdd2
```

**Three Validation Layers**:
1. **FastAPI**: Type validation for path/query parameters
2. **Pydantic**: Model validation before database operations
3. **Database**: Constraints (foreign keys, NOT NULL, etc.)

---

## 📊 Data Format Transformations

### Complete Transformation Chain

```
HTTP Request (JSON/Query Params)
  ↓ FastAPI parsing
Python primitives (str, int, float)
  ↓ Pydantic validation (for transactions)
Pydantic Model (optional pre-insert)
  ↓ SQL parameter binding
SQL Parameters (?, ?, ?)
  ↓ SQLite execution
Database Row (sqlite3.Row)
  ↓ dict() conversion
Python Dictionary
  ↓ Pydantic model instantiation
Pydantic Model Instance
  ↓ FastAPI serialization
JSON Response
  ↓ HTTP
Client receives JSON
```

---

## 🔍 Key Observations

### Design Patterns
1. **Context Manager**: Ensures database connections are properly closed
2. **Repository Pattern**: DBManager abstracts database operations
3. **Data Transfer Objects**: Pydantic models serve as DTOs
4. **Validation Pipeline**: Multiple validation layers ensure data integrity

### Data Consistency
- Timestamps (`created`, `updated`) managed by database
- Foreign key constraints ensure referential integrity
- Pydantic validation prevents invalid data entry
- Transaction commits ensure atomic operations

### Error Propagation
- Database returns `None` for not-found cases
- Routers convert `None` to HTTP 404
- Validation errors logged but not exposed to client
- SQL errors would propagate as 500 errors (not currently handled)

---

For implementation details, see:
- [[spec_server.md]] - Router implementations
- [[spec_database.md]] - Database operations
- [[spec_pydantic.md]] - Model validation rules
