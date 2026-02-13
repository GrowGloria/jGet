# jGet Backend

FastAPI + Postgres backend for the learning app.

## Requirements
- Docker + Docker Compose
- Python 3.12 (optional for local dev)

## Quick start (Docker)
1. Start services
   docker compose up -d
2. Apply migrations
   docker compose exec api alembic upgrade head
3. Open docs
   http://localhost:8000/docs

## Run on Windows (PowerShell)
1. Start services
   docker compose up -d
2. Apply migrations
   docker compose exec api alembic upgrade head
3. Open docs
   http://localhost:8000/docs

## Run on macOS (Terminal)
1. Start services
   docker compose up -d
2. Apply migrations
   docker compose exec api alembic upgrade head
3. Open docs
   http://localhost:8000/docs

## Local dev
1. Create venv and install deps
   pip install -r requirements.txt
2. Run Postgres (docker compose) and set DATABASE_URL
3. Apply migrations
   alembic upgrade head
4. Run API
   uvicorn app.main:app --reload

## Create admin user
1. Register a parent via `POST /auth/register-parent`
2. Promote to admin via SQL:
   UPDATE users SET user_type = 'admin' WHERE id = '<USER_UUID>';

## Notes
- Authorization removed: all endpoints are public. Endpoints that need a user context accept `user_id` as a query parameter.
- Env vars: `DATABASE_URL`, `TIMEZONE`, `UPLOAD_DIR`, `LOG_LEVEL`.
- Keyset pagination uses `cursor=base64("starts_at|id")`.

## API endpoints
- `POST /auth/register-parent` - Register parent user and return user profile.
- `POST /auth/login` - Login by email/phone + password and return user profile.
- `POST /auth/check-user` [MVP] - Check if user exists by email/phone (403 if not found).
- `GET /me` - Get user profile (`user_id` query param).
- `GET /me/courses` [MVP] - List user's courses (derived from groups, `user_id` query param).
- `GET /students` - List parent's children (`user_id` query param).
- `POST /students` - Create child for parent (`user_id` query param).
- `GET /groups` - List groups.
- `POST /groups` - Create group.
- `PATCH /groups/{group_id}` - Update group.
- `GET /lessons` [MVP] - List lessons for user with keyset pagination (starts_at DESC, id DESC, `user_id` query param).
- `GET /lessons/{lesson_id}` [MVP] - Lesson detail with duration_minutes (`user_id` query param).
- `GET /lessons/month` [MVP] - Lessons for month (TZ Europe/Vienna) with keyset pagination (starts_at ASC, id ASC, `user_id` query param).
- `GET /lessons/range` [MVP] - Lessons in date range with keyset pagination (starts_at ASC, id ASC, `user_id` query param).
- `POST /lessons/{lesson_id}/will-go` - Set child attendance for lesson (`user_id` query param).
- `GET /materials/short` - List materials (short) for group_id with keyset pagination.
- `GET /materials` - List materials for group_id with keyset pagination.
- `POST /materials` - Create material.
- `GET /materials/{material_id}` - Material detail.
- `GET /notifications` - List notifications with keyset pagination (`user_id` query param).
- `POST /notifications/{notification_id}/read` - Mark notification as read (`user_id` query param).
- `POST /payments/create` - Create payment for a lesson (`user_id` query param).
- `POST /payments/webhook/{provider}` - Payment provider webhook callback.
- `GET /payments` - List parent payments with keyset pagination (`user_id` query param).
- `POST /device-tokens` - Register device token for push notifications (`user_id` query param).
- `DELETE /device-tokens/{token_id}` - Revoke device token (`user_id` query param).
- `GET /managers` [MVP] - List managers.
- `POST /managers` - Create/update manager.
- `POST /admin/jobs/generate-lessons` - Generate lessons from group schedule.
- `POST /admin/jobs/enqueue-reminders` - Enqueue lesson reminders.
- `GET /health` - Health check.

## Tests
pip install -r requirements-dev.txt
pytest
