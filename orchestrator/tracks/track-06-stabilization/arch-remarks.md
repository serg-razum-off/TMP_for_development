# Architecture Remarks — Code Review
> Track: `track-06-stabilization`
> Reviewed: 2026-04-25
> Scope: Major issues only (learning project — minor style issues omitted)

---

## R-01 · `tasks.py` — Logic Bug: Temp File Never Written → JSONL Always Cleared

**Severity:** 🔴 Bug (data loss risk)

**File:** `orders/tasks.py`

**Problem:**
The temp file is opened for writing but **nothing is ever written to it**. After `os.replace(temp_file.name, jsonl_path)`, the JSONL file is unconditionally replaced by an empty file. This means every task run wipes the queue regardless of success or failure. If the Celery worker crashes mid-run, all unprocessed records are gone.

The long comment block in the file itself acknowledges the confusion ("Wait, if we remove everything..."), which confirms the logic was never resolved.

**Fix — decide on the intended contract and implement explicitly:**

- **Option A (clear on success, keep failures for retry):**
```python
try:
    with open(jsonl_path, "r") as f:
        for record_str in f:
            record_str = record_str.strip()
            if not record_str:
                continue
            try:
                record = json.loads(record_str)
                Order.objects.create(...)
                processed_count += 1
            except (KeyError, ValidationError) as e:
                errored_count += 1
                temp_file.write(record_str + "\n")  # keep for retry
    temp_file.flush()
    os.replace(temp_file.name, jsonl_path)
```

---

## R-02 · `tasks.py` — Runtime Bug: Wrong Field Names on `UserMessage.objects.create`

**Severity:** 🔴 Bug (runtime `TypeError`)

**File:** `orders/tasks.py` · error-handling block

**Problem:**
```python
UserMessage.objects.create(
    user_id=...,
    message=f"...",   # ← model field is `message_body`
    is_error=True,    # ← field does not exist on UserMessage
)
```

`UserMessage` has `message_body` (not `message`) and no `is_error` field. Django will raise a `TypeError` immediately. The error-notification path has never successfully executed.

**Fix:**
```python
UserMessage.objects.create(
    user_id=record.get("created_by_id"),
    message_body=f"Failed to process mobile order: {str(e)}",
)
```

If `is_error` is a real requirement, add it to the model:
```python
is_error = models.BooleanField(default=False)
```
and create a migration.

---

## R-03 · `tasks.py` — Fragile `"record" in locals()` Guard

**Severity:** 🟠 Reliability

**File:** `orders/tasks.py` · error-handling block

**Problem:**
```python
user_id=record.get("created_by_id", 1)
if "record" in locals()
else 1,
```

`locals()` introspection is fragile and hard to read.  `record` is only unbound for `json.JSONDecodeError`; for `KeyError`/`ValidationError` it is always defined. The fallback `user_id=1` hard-codes an assumption about the DB state (user 1 may not exist).

**Fix:** Split the except clause:
```python
except json.JSONDecodeError as e:
    logger.error("Malformed JSON line, skipping: %s", e)
    errored_count += 1
    continue  # no record → skip UserMessage

except (KeyError, ValidationError) as e:
    logger.error("Failed to process mobile order: %s", e)
    errored_count += 1
    UserMessage.objects.create(
        user_id=record.get("created_by_id"),
        message_body=f"Failed to process mobile order: {e}",
    )
```

---

## R-04 · `streaming_server/main.py` — Naive `datetime.now()` (Timezone-Unaware)

**Severity:** 🟠 Consistency

**File:** `streaming_server/main.py` · Line 17

**Problem:**
```python
order_data["created_at"] = datetime.now().isoformat()
```

The Django side uses `USE_TZ = True` and writes UTC-aware datetimes. The FastAPI service writes naive local-time strings. Timestamps will be inconsistent, especially in non-UTC environments. This contradicts the timezone-safety fix applied in track-06 task 4 to `tasks.py` but not propagated here.

**Fix:**
```python
from datetime import datetime, timezone

order_data["created_at"] = datetime.now(timezone.utc).isoformat()
```

---

## R-05 · `streaming_server/main.py` — Bare `except Exception` Swallows All Errors

**Severity:** 🟠 Observability

**File:** `streaming_server/main.py` · endpoint body

**Problem:**
```python
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
```

Converts every failure (disk full, permission error, programming bugs) to a generic 500 with no logging and possibly sensitive internal paths in `str(e)`.

**Fix:**
```python
import logging
logger = logging.getLogger(__name__)

except OSError as e:
    logger.error("Failed to write order to JSONL: %s", e)
    raise HTTPException(status_code=500, detail="Storage error. Please try again later.")
```

Let unexpected exceptions propagate naturally — FastAPI will return 500 with full tracebacks in logs.

---

## R-06 · `views.py` — `_get_product_prices_data` Duplicated in Two Views

**Severity:** 🟡 Maintainability

**File:** `orders/views.py` · `OrderCreateView` and `OrderUpdateView`

**Problem:**
The `_get_product_prices_data` private method is copy-pasted identically into both views. Any future change (e.g. filtering by `is_active`) must be applied in two places.

**Fix:** Extract to a shared mixin or module-level helper:
```python
def _get_product_prices() -> dict:
    """Returns {product_id: price} for client-side total calculation."""
    return {item.id: float(item.price) for item in Inventory.objects.all()}

class OrderPriceMixin:
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["product_prices"] = _get_product_prices()
        return data

class OrderCreateView(LoginRequiredMixin, OrderPriceMixin, CreateView): ...
class OrderUpdateView(LoginRequiredMixin, OrderPriceMixin, UpdateView): ...
```

---

## R-07 · `middleware.py` — Dead Class `SimpleLoggingMiddleware`

**Severity:** 🟡 Cleanliness

**File:** `orders/middleware.py`

**Problem:**
`SimpleLoggingMiddleware` is defined but never registered in `settings.MIDDLEWARE`. It uses `print()` and is fully superseded by `RequestTelemetryMiddleware`.

**Fix:** Delete `SimpleLoggingMiddleware`.

---

## R-08 · `middleware.py` — `print()` in Production Middleware

**Severity:** 🟠 Observability

**File:** `orders/middleware.py` · `RequestTelemetryMiddleware.__call__`

**Problem:**
```python
print(f">>: [{request.request_id}] {request.method} {request.path} - {duration:.4f}s")
```

`print()` writes to stdout unconditionally with no log level, no filtering, and no integration with Django's logging framework. In Docker/production log aggregators this output cannot be levelled or silenced.

**Fix:**
```python
import logging
logger = logging.getLogger(__name__)

logger.info("[%s] %s %s - %.4fs", request.request_id, request.method, request.path, duration)
```

Add `orders.middleware` to `LOGGING` in `settings.py` if specific routing is needed.

---

## R-09 · `settings.py` — Hard-Coded Secret Key + `DEBUG=True` + `ALLOWED_HOSTS=["*"]`

**Severity:** 🔴 Security (acceptable for learning only — must not reach any shared environment)

**File:** `myproject/settings.py`

**Problem:**
```python
SECRET_KEY = "django-insecure-teaching-key"
DEBUG = True
ALLOWED_HOSTS = ["*"]
```

The three settings together:
1. Sign sessions/CSRF tokens with a publicly known key.
2. Expose full stack traces to any HTTP client on errors.
3. Accept any `Host` header (Host header injection).

**Fix (minimum for any environment beyond a solo local dev machine):**
```python
import os
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]          # fail loudly if unset
DEBUG = os.environ.get("DJANGO_DEBUG", "False") == "True"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost").split(",")
```

Set the env vars in `docker-compose.yml` for development, and in CI/CD secrets for deployment.

---

## R-10 · `views.py` — `user_lookup` Endpoint Is Unauthenticated

**Severity:** 🔴 Security

**File:** `orders/views.py` · `user_lookup`

**Problem:**
```python
@require_http_methods(["GET"])
def user_lookup(request):
    """Internal API endpoint - no authentication required for Celery task access."""
    user_ids = request.GET.get("user_ids", "").split(",")
    users = User.objects.filter(id__in=user_ids).values("id", "username")
```

Any unauthenticated HTTP client can enumerate all usernames by iterating `user_ids`. The "internal" comment does not make it so — the endpoint is publicly exposed.

**Fix options:**
- **If only staff should access it:** add `@login_required` + `is_staff` check.
- **If it's a service-to-service call:** validate a shared secret header
  (`X-Internal-Token` checked against an env var).
- **Preferred refactor:** eliminate the endpoint entirely by embedding the username in the JSONL payload when the streaming server writes it (requires a lookup at write time in the FastAPI service, but removes the back-channel HTTP call from the Celery task entirely).

---

## Summary Table

| ID | File | Severity | Issue |
|----|------|----------|-------|
| R-01 | `orders/tasks.py` | 🔴 Bug | Temp file never written → JSONL always wiped |
| R-02 | `orders/tasks.py` | 🔴 Bug | Wrong field names on `UserMessage.objects.create` |
| R-03 | `orders/tasks.py` | 🟠 Reliability | Fragile `"record" in locals()` guard |
| R-04 | `streaming_server/main.py` | 🟠 Consistency | Naive `datetime.now()` — timezone unaware |
| R-05 | `streaming_server/main.py` | 🟠 Observability | Bare `except Exception` swallows all errors |
| R-06 | `orders/views.py` | 🟡 Maintainability | `_get_product_prices_data` duplicated in two views |
| R-07 | `orders/middleware.py` | 🟡 Cleanliness | Dead class `SimpleLoggingMiddleware` |
| R-08 | `orders/middleware.py` | 🟠 Observability | `print()` used in production middleware |
| R-09 | `myproject/settings.py` | 🔴 Security | Hard-coded secret key + `DEBUG=True` + `ALLOWED_HOSTS=["*"]` |
| R-10 | `orders/views.py` | 🔴 Security | `user_lookup` endpoint has no authentication |
