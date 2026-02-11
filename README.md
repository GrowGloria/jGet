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
- JWT access + refresh tokens (`/auth/refresh`).
- Env vars: `DATABASE_URL`, `JWT_SECRET`, `ACCESS_TTL` (seconds), `REFRESH_TTL` (seconds).
- Keyset pagination uses `cursor=base64("starts_at|id")`.

## API endpoints
- `POST /auth/register-parent` - Register parent user and return access/refresh tokens.
- `POST /auth/login` - Login by email/phone + password and return tokens.
- `POST /auth/check-user` [MVP] - Check if user exists by email/phone (403 if not found).
- `POST /auth/refresh` - Refresh access token using refresh token.
- `GET /me` - Get current user profile.
- `GET /me/courses` [MVP] - List user's courses (derived from groups).
- `GET /students` - List current parent's children.
- `POST /students` - Create child for current parent.
- `GET /groups` - List groups.
- `POST /groups` - Create group (admin only).
- `PATCH /groups/{group_id}` - Update group (admin only).
- `GET /lessons` [MVP] - List lessons for current user with keyset pagination (starts_at DESC, id DESC).
- `GET /lessons/{lesson_id}` [MVP] - Lesson detail with duration_minutes.
- `GET /lessons/month` [MVP] - Lessons for month (TZ Europe/Vienna) with keyset pagination (starts_at ASC, id ASC).
- `GET /lessons/range` [MVP] - Lessons in date range with keyset pagination (starts_at ASC, id ASC).
- `POST /lessons/{lesson_id}/will-go` - Set child attendance for lesson (parent only).
- `GET /materials/short` - List materials (short) for group_id with keyset pagination.
- `GET /materials` - List materials for group_id with keyset pagination.
- `POST /materials` - Create material (admin only).
- `GET /materials/{material_id}` - Material detail.
- `GET /notifications` - List notifications with keyset pagination.
- `POST /notifications/{notification_id}/read` - Mark notification as read.
- `POST /payments/create` - Create payment for a lesson (parent only).
- `POST /payments/webhook/{provider}` - Payment provider webhook callback.
- `GET /payments` - List parent payments with keyset pagination.
- `POST /device-tokens` - Register device token for push notifications.
- `DELETE /device-tokens/{token_id}` - Revoke device token.
- `GET /managers` [MVP] - List managers (auth required).
- `POST /managers` - Create/update manager (admin only).
- `POST /admin/jobs/generate-lessons` - Generate lessons from group schedule (admin only).
- `POST /admin/jobs/enqueue-reminders` - Enqueue lesson reminders (admin only).
- `GET /health` - Health check.

## Tests
pip install -r requirements-dev.txt
pytest
