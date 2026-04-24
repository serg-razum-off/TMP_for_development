# ARCHITECHT_GUIDE: State, Governance & Workflow

This document is the **Unified Protocol** for the Django project state management and execution. All actions must comply with this hierarchy.

## 📋 1. System Map & Protocols

| File                      | Location        | Role                  | Read/Update Protocol                                                |
| ------------------------- | --------------- | --------------------- | ------------------------------------------------------------------- |
| `tracks.md`               | `orchestrator/` | **Milestone Map**     | **Read:** Session start. **Update:** Epic start/completion.         |
| `security.md`             | `orchestrator/` | Security              | **Read:** Session start.                                            |
| `plan.md`                 | `tracks/<id>/`  | **Blueprint (Truth)** | **Read:** Every task. **Update:** BEFORE code changes.              |
| `todo.json`               | `tracks/<id>/`  | **Execution Engine**  | **Read:** Get next task. **Update:** Task state change.             |
| `product-spec.md`         | `orchestrator/` | **Requirements**      | **Read:** Feature start. **Update:** Requirement shifts.            |
| other `*.md` (cold files) | `orchestrator/` | **Static Policy**     | **Read:** As needed (Glossary, Security, Tech-Stack).               |

## 1.1. 🌡️ Context Temperature Matrix

| **Tier** | **Priority**      | **Files**                                                                                                                    | **Operational Trigger**                                                          |
| -------- | ----------------- | ---------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| **HOT**  | **Active Memory** | `todo.json`, `plan.md`                                                                                                       | **Read/Update:** Every task cycle. The immediate execution truth.                |
| **WARM** | **Working Set**   | `tracks.md`, `security.md`, `ARCHITECHT_GUIDE.md`, `0 onboarding.md`, `tech-stack.md`                                        | **Read:** Session start. Establishes roadmap, safety boundaries, and governance. |
| **COLD** | **Reference**     | `product-spec.md`, `testing-strategy.md`, `code-styleguides.md`, `glossary.md`, `core-processes outline.md`                  | **Read:** As needed. Used for domain depth, tool validation, or track archival.  |

## 🔄 2. The Integrated Development Loop

1. **Initialize:** Identify `active_track` in `tracks.md`. Sync with `plan.md` and `product-spec.md`.
2. **Red Phase (TDD):** Pull `pending` task from `todo.json`. Write failing Django tests (utilizing `django.test.TestCase`).
3. **Logic Lock:** If implementation deviates from the plan, update `plan.md` **before** writing production code.
4. **Green Phase:** Implement minimum code to pass tests. Adhere to Django Class-Based View patterns and query optimizations (`select_related`/`prefetch_related`).
5. **Verify:** Ensure all tests pass. Align with `code-styleguides.md`.
6. **Sync:** Update `todo.json` to `completed`.

## ⚠️ 3. Critical Constraints & Safety

* **Logic First:** `plan.md` is the **Absolute Source of Truth**. Logic changes must precede code changes.
* **ORM Excellence:** Always check for N+1 query problems. Use `select_related` for ForeignKeys and `prefetch_related` for ManyToMany/Reverse FKs.
* **No Ghost Features:** Every change must map to a `todo.json` task and a `tracks.md` entry.
* **Telemetry Awareness:** New critical endpoints should be reflected in or monitored by the `RequestTelemetryMiddleware` logic.

## 🛠 4. Execution Engine (`todo.json`)

All updates must validate against this schema:

```json
{
  "type": "object",
  "properties": {
    "track_id": { "type": "string" },
    "tasks": {
      "type": "array",
      "items": {
        "properties": {
          "id": { "type": "integer" },
          "task": { "type": "string" },
          "status": { "enum": ["pending", "in-progress", "completed", "blocked"] },
          "file_targets": { "type": "array", "items": { "type": "string" } }
        },
        "required": ["id", "task", "status"]
      }
    }
  },
  "required": ["track_id", "tasks"]
}
```

## ✅ 5. Definition of Done (DoD)

* [ ] Queries are optimized (No N+1).
* [ ] All tests pass.
* [ ] Public methods have docstrings/type hints.
* [ ] `plan.md` updated with task status.
