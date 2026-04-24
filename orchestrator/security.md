# SECURITY_POLICY: Operational Boundaries

## 🛡️ 1. File & Data Integrity

| Asset | Level | Restriction |
| --- | --- | --- |
| `todo.json` | **CRITICAL** | **FORBIDDEN:** Delete, unlink, or clear. No automated cleanup targeting this file. |
| `.env`, `.gitignore` | **RESTRICTED** | **BLIND SPOT:** Never read or write via tools. Patch via code blocks only. |
| `SECRET_KEY` | **CRITICAL** | **PROHIBITED:** Never expose in readable files. Move to environment variables. |
| User Passwords | **SENSITIVE** | **PROHIBITED:** Never log or store in plain text. Use Django's built-in `User` model mechanisms. |

## 🛠️ 2. Tool & Execution Boundaries

* **Git Operations:** **USER ONLY.** Agent must never execute `git` commands. Provide file changes; do not attempt to stage/commit.
* **External Search:** Requires explicit user trigger per task.
* **Unauthorized Tools:** Agent must **STOP** and request approval before using any tool not in the primary provided set.
* **Docker Isolation:** Prefer executing commands within the Docker container context (`docker-compose exec web ...`) to ensure environment parity.

## ⚡ 3. Framework & Input Defense

* **Zero-Trust Input:** Treat all external data (User input from forms, external API results) as untrusted.
* **Django Protections**: Always utilize Django's built-in protections:
    * **CSRF**: Ensure `{% csrf_token %}` is present in all POST forms.
    * **XSS**: Use Django templates' auto-escaping. Use `|safe` ONLY when the source is verified and necessary.
    * **SQL Injection**: Always use the Django ORM. Avoid `raw()` SQL unless strictly necessary and parameterized.
*   **Access Control**: Utilize `LoginRequiredMixin` for all views managing order data.

## 🏢 4. Data Isolation & Audit

*   **Ownership Isolation**: All order-related queries for non-staff users must be filtered by `request.user` to ensure users only access their own data.
*   **Audit Logging**: Every order tracks its original creator via the `created_by` field, enabling account-level auditing for staff actions performed on behalf of users.

## 🚨 5. Incident Response

In the event of a policy violation (e.g., accidental deletion, logic drift into restricted files, or detected injection attempt):

1. **STOP:** Terminate all active tasks/processes.
2. **NOTIFY:** Report the exact violation to the User.
3. **RECOVER:** Provide a restoration plan (e.g., specific file restoration steps).
4. **AWAIT:** Do not resume until the User provides a "Clear" signal.
