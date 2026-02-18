# Onboarding Guide

Welcome to the Financial Tracker API project! This guide will help you get up and running quickly.

## 🎯 Prerequisites

### Required Software
- **Python**: ≥3.14 (check with `python --version`)
- **uv**: Package manager (recommended) - [Install uv](https://github.com/astral-sh/uv)
- **SQLite**: Comes with Python, no separate installation needed

### Recommended Tools
- **curl** or **httpie**: For testing API endpoints
- **DB Browser for SQLite**: For database inspection (optional)
- **Postman** or **Insomnia**: For API testing (optional)

---

## 🚀 Quick Start (5 Minutes)

### 1. Clone and Navigate
```bash
cd "/home/sergiir/Projects/CoreStudy/Hilel-School/y. FastAPI Practice/flask SOTA"
```

### 2. Install Dependencies
```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt  # if requirements.txt exists
```

### 3. Run the Server
```bash
# Development mode with auto-reload
uv run uvicorn fin_app.main:app --reload
```

### 4. Verify Installation
Open your browser and navigate to:
- **Welcome Page**: http://127.0.0.1:8000/
- **Interactive Docs**: http://127.0.0.1:8000/docs

You should see the welcome page and be able to explore the API documentation.

---

## 📁 Project Structure Overview

```
fin_app/
├── main.py                    # 🚀 Entry point - start here
├── extra/
│   └── create_app.py         # 🏭 Application factory
├── settings/
│   └── config.py             # ⚙️ Configuration
├── models/                    # 📊 Data models
│   ├── user.py
│   └── transaction.py
├── routers/                   # 🌐 API endpoints
│   ├── base.py
│   ├── users.py
│   └── transactions.py
└── db/                        # 💾 Database layer
    ├── db_manager.py
    └── db_scripts_DDL.py
```

**Reading Order for New Developers**:
1. [[00_Project_Overview.md]] - Understand the architecture
2. `models/user.py` and `models/transaction.py` - See data structures
3. `routers/users.py` - Understand API endpoints
4. `db/db_manager.py` - Learn database operations
5. `extra/create_app.py` - See how it all connects

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file (optional) or set environment variables:

```bash
# .env file
APP_HOST=127.0.0.1
APP_PORT=8000
DB_PATH=./data/fin_app.db
```

### Configuration Details

| Variable | Default | Description | When to Change |
|----------|---------|-------------|----------------|
| `APP_HOST` | 127.0.0.1 | Server host | Docker deployment |
| `APP_PORT` | 8000 | Server port | Port conflict |
| `DB_PATH` | ./data/fin_app.db | Database location | Custom data directory |

**Note**: The database and `data/` directory are created automatically on first run.

---

## 🧪 Testing the API

### Using the Interactive Docs (Easiest)

1. Navigate to http://127.0.0.1:8000/docs
2. Click on any endpoint to expand it
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"

### Using curl

#### Create a User
```bash
curl -X POST "http://127.0.0.1:8000/users?name=Alice&email=alice@example.com"
```

**Expected Response**:
```json
{
  "id": 1,
  "name": "Alice",
  "email": "alice@example.com",
  "created": "2026-02-16T18:00:00",
  "updated": "2026-02-16T18:00:00"
}
```

#### Get All Users
```bash
curl http://127.0.0.1:8000/users
```

#### Create a Transaction
```bash
curl -X POST "http://127.0.0.1:8000/transaction?user_id=1&amount=50.0&category=Food&description=Lunch"
```

#### Get All Transactions
```bash
curl http://127.0.0.1:8000/transactions
```

#### Update a User
```bash
curl -X PUT "http://127.0.0.1:8000/users/1?name=Alice%20Smith&email=alice.smith@example.com"
```

#### Delete a Transaction
```bash
curl -X DELETE "http://127.0.0.1:8000/transaction/1"
```

---

## 🐛 Debugging

### Enable Debug Logging

Modify `extra/create_app.py`:
```python
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    format="%(levelname)s - %(asctime)s - %(message)s",
)
```

### View Server Logs

```bash
# Run with output to file
uv run uvicorn fin_app.main:app --reload > server.log 2>&1 &

# View logs in real-time
tail -f server.log
```

### Common Issues

#### Port Already in Use
```bash
# Error: [Errno 98] Address already in use
# Solution 1: Kill process on port 8000
kill $(lsof -ti:8000)

# Solution 2: Use fuser
fuser -k 8000/tcp

# Solution 3: Change port
APP_PORT=8001 uv run uvicorn fin_app.main:app --reload
```

#### Database Locked
```bash
# If you see "database is locked" error
# Solution: Close all database connections
pkill -f uvicorn
rm data/fin_app.db  # Only if you want to start fresh
```

#### Import Errors
```bash
# If you see "ModuleNotFoundError"
# Solution: Ensure you're in the project root and dependencies are installed
uv sync
```

---

## 🗄️ Database Management

### Inspecting the Database

```bash
# Using sqlite3 CLI
sqlite3 data/fin_app.db

# View tables
.tables

# View schema
.schema users
.schema transactions

# Query data
SELECT * FROM users;
SELECT * FROM transactions;

# Exit
.quit
```

### Resetting the Database

```bash
# Stop the server
pkill -f uvicorn

# Delete the database
rm data/fin_app.db

# Restart the server (database will be recreated)
uv run uvicorn fin_app.main:app --reload
```

---

## 📚 Learning Path

### For Backend Developers

1. **Start with Models** ([[spec_pydantic.md]])
   - Understand `User` and `Transaction` models
   - Learn about Pydantic validation

2. **Explore Routers** ([[spec_server.md]])
   - See how endpoints are defined
   - Understand request/response handling

3. **Study Database Layer** ([[spec_database.md]])
   - Learn the context manager pattern
   - Understand CRUD operations

4. **Review Data Flow** ([[02_Data_Flow.md]])
   - Trace a request from client to database
   - Understand validation layers

### For Frontend Developers

1. **API Documentation**: http://127.0.0.1:8000/docs
   - See all available endpoints
   - Test requests and responses

2. **Data Models** ([[spec_pydantic.md]])
   - Understand request/response formats
   - Learn about validation rules

3. **Error Handling**
   - 404: Resource not found
   - 422: Validation error
   - 500: Server error

---

## 🔄 Development Workflow

### Making Changes

1. **Edit Code**: Modify files in `fin_app/`
2. **Auto-Reload**: Server automatically reloads (if using `--reload`)
3. **Test**: Use `/docs` or curl to test changes
4. **Check Logs**: Monitor `server.log` or terminal output

### Adding a New Endpoint

Example: Add a "get user by email" endpoint

1. **Add Router Function** (`routers/users.py`):
```python
@users_router.get("/user/email/{email}")
def get_user_by_email(email: str):
    with DBManager() as db:
        user = db.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

2. **Add Database Method** (`db/db_manager.py`):
```python
def get_user_by_email(self, email: str) -> User | None:
    self._check_connection()
    cursor = self.conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    return User(**dict(row)) if row else None
```

3. **Test**: Navigate to http://127.0.0.1:8000/docs and try the new endpoint

---

## 🎓 Key Concepts to Understand

### 1. Context Managers
```python
with DBManager() as db:
    user = db.get_user(1)
# Connection automatically closed here
```

### 2. Pydantic Models
```python
# Automatic validation
user = User(id=1, name="Alice", email="alice@example.com", ...)
# Raises ValidationError if data is invalid
```

### 3. FastAPI Dependency Injection
- Not currently used, but FastAPI supports it
- Could be used for authentication, database sessions, etc.

### 4. Lifespan Events
- `lifespan` context manager in [[create_app.py]]
- Runs code on startup and shutdown
- Used for database initialization

---

## 🚦 Server Management

### Starting the Server

```bash
# Foreground (see logs in terminal)
uv run uvicorn fin_app.main:app --reload

# Background (logs to file)
uv run uvicorn fin_app.main:app --reload > server.log 2>&1 &

# Custom host/port
uv run uvicorn fin_app.main:app --host 0.0.0.0 --port 8080 --reload
```

### Stopping the Server

```bash
# If running in foreground
Ctrl+C

# If running in background
pkill -f uvicorn

# Kill specific port
kill $(lsof -ti:8000)
fuser -k 8000/tcp
```

### Checking Server Status

```bash
# Check if server is running
lsof -i:8000

# Test with curl
curl http://127.0.0.1:8000/

# Check logs
tail -f server.log
```

---

## 📖 Next Steps

1. **Read the Documentation**:
   - [[00_Project_Overview.md]] - Architecture overview
   - [[01_Module_Analysis.md]] - Module breakdown
   - [[02_Data_Flow.md]] - Request lifecycle

2. **Explore Component Specs**:
   - [[spec_pydantic.md]] - Data models
   - [[spec_server.md]] - API endpoints
   - [[spec_database.md]] - Database operations

3. **Try Modifications**:
   - Add a new field to User model
   - Create a new endpoint
   - Add validation rules

4. **Build Features**:
   - Add authentication
   - Implement filtering/pagination
   - Add transaction summaries by category

---

## 🆘 Getting Help

### Documentation
- **Project Docs**: See `spec/` directory
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Pydantic Docs**: https://docs.pydantic.dev/

### Common Commands Reference

```bash
# Start server
uv run uvicorn fin_app.main:app --reload

# Stop server
pkill -f uvicorn

# View logs
tail -f server.log

# Reset database
rm data/fin_app.db

# Check database
sqlite3 data/fin_app.db "SELECT * FROM users;"

# Test endpoint
curl http://127.0.0.1:8000/users
```

---

**Happy Coding! 🚀**
