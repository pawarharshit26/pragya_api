# Pragya API — Backend Plan

## Context

FastAPI backend for Pragya — a personal growth tracker. Implements the hierarchy:

**Vision → Themes → Tracks → Goals → Phases → Daily Commitments → Execution Logs**

Each layer narrows from abstract identity to concrete daily action. One user owns one Vision; all other entities cascade from it.

Reference docs:
- `CLAUDE.md` — architecture, patterns, conventions
- `schema_evolution.md` — all locked schema decisions (the why behind each field)

---

## Architecture (Locked)

4-layer stack per domain:

```
app/entities/<domain>.py          Pydantic input/output models — shared across all layers
app/repositories/<domain>.py      All SQL/ORM — returns entities, never ORM objects
app/services/<domain>.py          Business logic — orchestrates repos, raises domain exceptions
app/interactors/<domain>/<action> One file per endpoint — catches service exceptions, re-raises
app/apis/v1/<domain>.py           Route handlers — calls interactor, maps to HTTP status
app/dependencies.py               All DI providers in one place
```

Request lifecycle:
```
HTTP Request
  → Middleware (RequestID + Logging)
  → Route handler
    → Interactor.execute()
      → Service method
        → Repository → DB
  → ResponseEntity[T]
```

Exception isolation per layer (service → interactor → API), each layer only knows its own exceptions.

---

## Domain Model

| Model | Key constraints |
|---|---|
| `Vision` | One active per user (`user_id` unique). `title + description` only. |
| `Theme` | 3–6 per Vision. Has `preset_key` (frontend resolves to glyph+color). |
| `Track` | Has `cadence_per_week`, `is_paused`, `paused_at`. |
| `Goal` | Has `horizon: str | None`. No description (→ blocks Phase 3). |
| `Phase` | `lifecycle` enum (draft/active/paused/complete/abandoned). **1 active per goal** (partial unique index). |
| `DailyCommitment` | `mve_minutes = max(5, round(expected_minutes / 3))` — frozen at write time. |
| `ExecutionLog` | 1-to-1 with DailyCommitment. `energy_level` 1–5 (DB check constraint). |
| `DailyReflection` | Day-level mood. Unique on `(user_id, date)`. |
| `Block` | Polymorphic rich content (Phase 3). |

---

## Roadmap

### Phase 1 — Infrastructure + User ✅ COMPLETE (2026-05-03)

1. **Project scaffold** ✅ — FastAPI + SQLAlchemy async + Alembic + structlog + HashId
2. **Core layer** ✅ — config, JWT, security, logging, middlewares, exceptions, HashId
3. **DB models** ✅ — all 11 models defined with locked schema deltas applied
4. **Initial migration** ✅ — single clean migration (`ae1fac635ff8_initial.py`)
   - Tables: user, auth_token, vision, theme, track, goal, phase, daily_commitment, execution_log, daily_reflection, block
   - Postgres types: `phase_lifecycle`, `mood`
   - Partial unique index: `ix_phase_one_active_per_goal`
   - Check constraint: `ck_execution_log_energy_level_range`
   - Unique constraint: `uq_daily_reflection_user_date`
5. **Architecture refactor** ✅ — migrated from 2-layer (service+router) to 4-layer (entities/repositories/services/interactors)
6. **User domain** ✅ — full CRUD: signup, signin, signout, get_me
   - `app/entities/user.py`
   - `app/repositories/user.py`
   - `app/services/user.py`
   - `app/interactors/user/` (signup, signin, signout, get_me)
   - `app/apis/v1/user.py`
   - `app/dependencies.py` (user providers + `get_current_user_id`)
   - Fixed: `sign_in` null-ref bug; `create_user` wrong return type

---

### Phase 2 — Domain Services ✅ COMPLETE (2026-05-04)

Built read-only endpoints only (frontend-driven scope). Write/CRUD endpoints deferred to Phase 4 when frontend write flows are built.

Build all 8 remaining domains following the 4-layer pattern. Each domain needs:
entities → repository → service → interactors → router → register in dependencies + base.

#### Status per layer:

| Layer | vision | structure | goal | today |
|---|---|---|---|---|
| entities | ✅ | ✅ | ✅ | ✅ |
| repository | ✅ | ✅ (theme+track) | ✅ (goal+phase) | ✅ (commitment+log+reflection) |
| service | ✅ | ✅ | ✅ | ✅ |
| interactors | ✅ | ✅ | ✅ (list+detail) | ✅ |
| router | ✅ | ✅ | ✅ | ✅ |
| wired up | ✅ | ✅ | ✅ | ✅ |

#### Endpoints planned per domain:

**Vision** (`/api/v1/vision/`)
- `GET /me` — get user's active vision
- `POST /` — create
- `PATCH /{id}` — update title/description
- `DELETE /{id}` — soft delete

**Theme** (`/api/v1/theme/`)
- `GET /` — list user's themes
- `POST /` — create
- `PATCH /{id}` — update name/description/preset_key/is_active
- `DELETE /{id}` — soft delete

**Track** (`/api/v1/track/`)
- `GET /` — list (optional `?theme_id=`)
- `POST /` — create
- `PATCH /{id}` — update name/description/cadence_per_week/is_active
- `POST /{id}/pause` — pause
- `POST /{id}/resume` — resume
- `DELETE /{id}` — soft delete

**Goal** (`/api/v1/goal/`)
- `GET /` — list (optional `?track_id=`)
- `POST /` — create
- `PATCH /{id}` — update title/horizon
- `DELETE /{id}` — soft delete

**Phase** (`/api/v1/phase/`)
- `GET /` — list (optional `?goal_id=`)
- `POST /` — create
- `PATCH /{id}` — update title/dates/lifecycle/outcome
- `DELETE /{id}` — soft delete

**Commitment** (`/api/v1/commitment/`)
- `GET /` — list (optional `?date=`, `?phase_id=`)
- `POST /` — create (auto-computes `mve_minutes = max(5, round(expected/3))` if not provided)
- `PATCH /{id}` — update intent/expected_minutes/mve_minutes
- `DELETE /{id}` — soft delete

**ExecutionLog** (`/api/v1/log/`)
- `GET /by-commitment/{commitment_id}` — get by commitment
- `POST /` — create
- `PATCH /{id}` — update actual_minutes/energy_level/note
- `DELETE /{id}` — soft delete

**DailyReflection** (`/api/v1/reflection/`)
- `GET /{date}` — get by date (ISO `YYYY-MM-DD`)
- `PUT /{date}` — upsert mood

---

### Phase 3 — Block Service (later)

9. **Block domain** — rich content CRUD for Goal, Phase, ExecutionLog, DailyReflection.
   Block model already exists; service + API deferred to when TipTap editor ships on frontend.

---

### Phase 4 — Insights (later)

10. Cadence adherence, MVE-hit rate, mood vs execution correlation, weekly aggregations.

---

## Key Patterns

### Ownership verification

Every repo method verifies entity belongs to current user via JOIN chain back to `vision.user_id`:

```python
# Track (2 hops)
select(Track)
    .join(Theme, Track.theme_id == Theme.id)
    .join(Vision, Theme.vision_id == Vision.id)
    .where(Vision.user_id == user_id, ...)

# Phase (4 hops)
select(Phase)
    .join(Goal, ...).join(Track, ...).join(Theme, ...).join(Vision, ...)
    .where(Vision.user_id == user_id, ...)
```

### MVE formula (frozen at write time)
```python
mve_minutes = max(5, round(expected_minutes / 3))
```
Computed in CommitmentService if `mve_minutes` not explicitly provided. No retroactive recompute on update.

### Phase ACTIVE uniqueness
Partial unique index `ix_phase_one_active_per_goal` enforces 1 active phase per goal at DB level.
PhaseRepository catches `IntegrityError` on lifecycle=ACTIVE conflicts and re-raises as `PhaseActiveConflictException`.

### Soft delete pattern
All deletes set `deleted_at = datetime.utcnow()` and `deleter_id = user_id`. All queries filter `deleted_at.is_(None)`.

---

## File Tree (current state)

```
pragya_api/
├── PLAN.md
├── CLAUDE.md
├── schema_evolution.md
├── app/
│   ├── core/                        ✅ config, jwt, security, logging, middlewares, hash_ids
│   ├── db/
│   │   ├── base.py                  ✅
│   │   └── models/                  ✅ all 11 models
│   ├── entities/
│   │   ├── base.py                  ✅
│   │   ├── user.py                  ✅
│   │   ├── vision.py                ✅
│   │   ├── theme.py                 ✅
│   │   ├── track.py                 ✅
│   │   ├── goal.py (extended with GoalDetailEntity) ✅
│   │   ├── phase.py                 ✅
│   │   ├── commitment.py            ✅
│   │   ├── execution_log.py         ✅
│   │   ├── reflection.py            ✅
│   │   ├── structure.py             ✅
│   │   └── today.py                 ✅
│   ├── repositories/
│   │   ├── base.py                  ✅
│   │   ├── user.py                  ✅
│   │   ├── vision.py                ✅
│   │   ├── theme.py                 ✅
│   │   ├── track.py                 ✅
│   │   ├── goal.py                  ✅
│   │   ├── phase.py                 ✅
│   │   ├── commitment.py            ✅
│   │   ├── execution_log.py         ✅
│   │   └── reflection.py            ✅
│   ├── services/
│   │   ├── base.py                  ✅
│   │   ├── user.py                  ✅
│   │   ├── vision.py                ✅
│   │   ├── structure.py             ✅
│   │   ├── goal.py                  ✅
│   │   └── today.py                 ✅
│   ├── interactors/
│   │   ├── base.py                  ✅
│   │   ├── user/                    ✅ signup, signin, signout, get_me
│   │   ├── vision/                  ✅
│   │   ├── structure/               ✅
│   │   ├── goal/                    ✅
│   │   └── today/                   ✅
│   ├── apis/
│   │   ├── exceptions.py
│   │   ├── response.py
│   │   └── v1/
│   │       ├── base.py              # router registration
│   │       ├── user.py              ✅
│   │       ├── vision.py            ✅
│   │       ├── structure.py         ✅
│   │       ├── goal.py              ✅
│   │       └── today.py             ✅
│   ├── dependencies.py              ✅
│   ├── migrations/                  ✅ single clean initial migration
│   └── main.py                      ✅
```

---

## Locked Schema Decisions (summary)

Full rationale in `schema_evolution.md`.

| Decision | Rule |
|---|---|
| MVE | `max(5, round(expected_minutes / 3))` — frozen at write |
| Track cadence | `cadence_per_week: int | None` (7 = daily) + `is_paused` |
| Phase lifecycle | enum `draft/active/paused/complete/abandoned` + partial unique index on ACTIVE |
| Theme visuals | `preset_key` only — frontend resolves to glyph+color |
| Goal/Phase rich text | Blocks (Phase 3) — no `description` field on Goal |
| ExecutionLog | `actual_minutes`, `energy_level (1-5)`, `note` (short) — rich reflection via blocks |
| DailyReflection | `mood` enum only (day-level) — blocks for rich content |
