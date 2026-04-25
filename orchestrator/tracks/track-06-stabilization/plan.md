# Track 06 - Project Stabilization and Best Practices

## Description
This track addresses code review remarks inside `orders` application to improve architecture, performance, and formatting.

## Objectives
1. **Architecture isolation:** Extract the `streaming` FastAPI service from the `orders` app into a top-level `streaming_server` directory. This makes it explicit that the streaming service is a separate entry point.
2. **Centralized background tasks:** Move the Celery beat schedule out of `orders/apps.py` and into the global settings (`myproject/celery.py` or `settings.py`) for better observability.
3. **Memory optimization:** Update the `process_mobile_orders` Celery task to read the JSONL file line-by-line rather than reading all records into memory at once. It should write remaining records line-by-line to a temporary file, and use atomic replacement.
4. **Timezone safety:** Avoid using naive datetimes (like `datetime.now()`). Use Explicit timezone execution (`datetime.now(timezone.utc)` or `django.utils.timezone.now()`) to ensure reliable timestamping.
5. **Permission Fix:** Resolve `PermissionError` for shared data files by synchronizing container user with host UID/GID in `docker-compose.yml` to maintain bind mount access.

## Execution Requirements
Ensure all updates correspond directly to the tasks inside `todo.json`. Update `todo.json` file status as tasks are finished. Test the application locally and within unit tests to ensure that these refactorings did not introduce errors.
