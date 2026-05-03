# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development Server
```bash
uv run uvicorn app.main:app --reload
```

### Database (Docker)
```bash
docker-compose up -d        # Start PostgreSQL + pgAdmin
docker-compose down         # Stop
```

### Migrations (Alembic)
```bash
alembic -c app/alembic.ini upgrade head                                    # Apply pending
alembic -c app/alembic.ini revision --autogenerate -m "description"        # New migration
alembic -c app/alembic.ini downgrade -1                                    # Rollback one
```

### Formatting & Linting
```bash
make fmt                    # black app && ruff check app --fix
```

### Setup (first time)
```bash
./setup.sh                  # Creates venv, installs deps, sets up pre-commit
```

## Architecture

**Pragya API** is a personal growth tracker implementing a strict hierarchy:

**Vision → Themes → Tracks → Goals → Phases → Daily Commitments → Execution Logs**

### Layer Stack

```
app/apis/v1/          HTTP layer — routes, request parsing, exception → HTTP status mapping
app/interactors/      One interactor per endpoint — single execute() method, own exceptions
app/services/         Business logic per domain — exceptions, validation, orchestrates repos
app/repositories/     Data access — all ORM creation/queries, returns entities (no ORM leaks)
app/entities/         Shared Pydantic models — used across all layers
app/db/models/        SQLAlchemy ORM models — only imported by repositories
app/core/             Config, JWT, security, logging, HashId, middlewares
app/dependencies.py   Single DI factory — all Depends() providers in one place
```

### Request Lifecycle

```
Request
  → RequestIDMiddleware (UUID per request)
  → RequestLoggingMiddleware
  → Route handler (APIs layer)
    → Interactor.execute()
      → Service method
        → Repository method → DB
  → ResponseEntity[T] wrapper
```

All responses follow this structure:
```json
{ "code": 200, "message": "", "data": {...}, "error": null }
```

### Exception Isolation

Each layer only knows its own exceptions:

| Layer | Raises | Catches |
|-------|--------|---------|
| Repository | — | (internal only) |
| Service | `XService.XException` | — |
| Interactor | `XInteractor.XException` | re-raises service exceptions as interactor exceptions |
| API | `BaseAPIException` | catches interactor exceptions, maps to HTTP status |

**Pattern:**
```python
# service
class UserService(BaseService):
    class UserNotFoundException(BaseException):
        message = "User Not Found"

# interactor
class GetMeInteractor(BaseInteractor[int, UserEntity]):
    class UserNotFoundException(BaseInteractor.InteractorException):
        message = "User not found"

    async def execute(self, input: int) -> UserEntity:
        try:
            return await self.user_service.get_user(input)
        except UserService.UserNotFoundException as e:
            raise self.UserNotFoundException() from e

# api
except GetMeInteractor.UserNotFoundException as e:
    raise BaseAPIException(message=str(e.message), status_code=404) from e
```

### Interactor Pattern

`BaseInteractor` is generic and abstract:
```python
class BaseInteractor(ABC, Generic[InputT, OutputT]):
    class InteractorException(BaseException): ...

    @abstractmethod
    async def execute(self, input: InputT) -> OutputT: ...
```

One interactor per API endpoint. File location: `app/interactors/<domain>/<action>.py`.

### Authentication

- JWT payload: `{"sub": {"auth_token": "<random_string>"}}`
- `AuthToken` row in DB links token string to user; deleted on signout
- `get_current_user_id` in `app/dependencies.py` validates JWT + DB presence + expiry
- Inject as: `user_id: Annotated[int, Depends(get_current_user_id)]`

### ID Obfuscation

Integer PKs never exposed. `HashId` (custom Pydantic type in `app/core/hash_ids.py`) auto-converts `int ↔ hash string` at serialization. Salt from `settings.SECRET_KEY`.

### Model Mixins (`app/db/models/base.py`)

All domain models inherit `CreateUpdateDeleteModel`:
- `created_at / creator_id` — set `creator_id=user_id` in repo `create_*` calls
- `updated_at / updater_id` — set `updater_id=user_id` in repo `update_*` calls
- `deleted_at / deleter_id` — soft delete; filter with `Model.deleted_at.is_(None)`

**Important:** `creator_id / updater_id / deleter_id` are NOT auto-populated. Pass `actor_id` from the authenticated `user_id` down through interactor → service → repository. Exception: `create_user` (signup bootstrap, no authenticated user yet → `creator_id=None`).

### DI Factory (`app/dependencies.py`)

All `get_*` provider functions live here. Adding a new feature = add providers to this one file.

```python
def get_vision_repository(db) -> VisionRepository: ...
def get_vision_service(repo, ...) -> VisionService: ...
def get_create_vision_interactor(service) -> CreateVisionInteractor: ...
```

## Entities (`app/entities/`)

Pydantic models shared across all layers. No ORM types, no DB knowledge.

- `BaseEntity` — base for all entities (`app/entities/base.py`)
- Per-domain files: `app/entities/<domain>.py`
- Input entities: `CreateXEntity`, `UpdateXEntity`, `SignInEntity`
- Output entities: `XEntity` (public fields only — no passwords, no raw IDs)

## Repositories (`app/repositories/`)

Own all ORM construction and SQL. Return entities, never ORM objects.

- `BaseRepository` — holds `db: AsyncSession` (`app/repositories/base.py`)
- `BaseRecord` — Pydantic base for internal records (not exported outside repo)
- Per-domain files: `app/repositories/<domain>.py`
- Mapper functions (`_to_x_entity`) are module-private

## Domain Model Semantics

| Model | Constraint / Intent |
|-------|---------------------|
| `Vision` | Identity anchor. One per user (`user_id` unique). Rarely changes. |
| `Theme` | Life domain. 3–6 active per Vision. Has `preset_key` (resolved to glyph+color frontend-side). |
| `Track` | Focus area within Theme. Has `cadence_per_week`, `is_paused`. |
| `Goal` | Outcome direction. Has `horizon: str | None`. No description (→ blocks Phase 3). |
| `Phase` | Time-boxed focus. `lifecycle` enum (draft/active/paused/complete/abandoned). **Only 1 active per goal** (partial unique index). |
| `DailyCommitment` | Day intent. `mve_minutes = max(5, round(expected_minutes / 3))` — frozen at write time. |
| `ExecutionLog` | Actual result. 1-to-1 with `DailyCommitment`. `energy_level` 1–5 (DB check constraint). |
| `DailyReflection` | Day-level mood. Unique on `(user_id, date)`. |
| `Block` | Polymorphic rich content. `owner_type` ∈ `{goal, phase, execution_log, daily_reflection}`. |

## Adding a New Feature (Pattern)

**Reference implementation:** `app/repositories/user.py`, `app/services/user.py`, `app/interactors/user/`, `app/apis/v1/user.py`

1. **Entity** (`app/entities/<domain>.py`): input + output Pydantic models extending `BaseEntity`.
2. **Repository** (`app/repositories/<domain>.py`): subclass `BaseRepository`, return entities from all public methods, pass `creator_id/updater_id` to ORM constructors.
3. **Service** (`app/services/<domain>.py`): subclass `BaseService`, define nested exception classes, inject repository. No ORM imports.
4. **Interactors** (`app/interactors/<domain>/<action>.py`): one file per endpoint, subclass `BaseInteractor[InputT, OutputT]`, implement `execute`, catch service exceptions and re-raise as own.
5. **Providers** (`app/dependencies.py`): add `get_<domain>_repository`, `get_<domain>_service`, `get_<action>_interactor`.
6. **Router** (`app/apis/v1/<domain>.py`): one route per endpoint, call `interactor.execute()`, catch interactor exceptions, map to `BaseAPIException`.
7. **Register** router in `app/apis/v1/base.py`.
8. **Migration**: `alembic -c app/alembic.ini revision --autogenerate -m "<description>"` if models changed.

## Tech Stack

FastAPI + SQLAlchemy 2.0 async + AsyncPG + PostgreSQL + Pydantic v2 + PyJWT + structlog + Hashids + Alembic

- Use `select()` / `delete()` (SQLAlchemy 2.0 style), not legacy Query API
- Use `Mapped[T]` + `mapped_column()` for new models (not `Column()`)
- All datetimes stored as UTC timezone-naive (`datetime.utcnow()`) — columns are `DateTime` without timezone
