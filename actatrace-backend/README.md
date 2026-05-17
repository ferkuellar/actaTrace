# ActaTrace Backend API

FastAPI backend foundation for ActaTrace, an electoral traceability and citizen audit platform. PostgreSQL is the system of record. Blockchain is reserved for future hash anchoring and verification, not data storage.

## Phase 2 Scope

Included:

- JWT authentication.
- Password hashing with bcrypt.
- Basic RBAC.
- User management.
- Acta registration.
- Document metadata registration and SHA-256 hashing.
- Chain-of-custody events.
- PREP result capture and validation.
- Append-only audit log model and audit service.
- Docker Compose for local backend and PostgreSQL.
- Pytest smoke and domain tests.

Excluded:

- Frontend.
- Production blockchain integration.
- Electronic voting.
- Vote casting.
- Real object storage integration.
- Advanced analytics or AI fraud detection.
- Microservices and Kubernetes.

## Local Setup

```bash
cd actatrace-backend
cp .env.example .env
docker compose up --build
```

API docs:

- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
- Health: `http://localhost:8000/health`

## Environment Variables

```env
DATABASE_URL=
JWT_SECRET_KEY=
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
ENVIRONMENT=local
LOG_LEVEL=INFO
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

Use a strong `JWT_SECRET_KEY` outside local development.

## Database Migrations

Generate the initial migration:

```bash
alembic revision --autogenerate -m "initial schema"
```

Apply migrations:

```bash
alembic upgrade head
```

## Run Without Docker

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Tests

```bash
pytest
```

The tests use an in-memory SQLite database through FastAPI dependency overrides. Production and Docker runs use PostgreSQL.

## API Bootstrapping

Create the first administrator:

```bash
curl -X POST http://localhost:8000/api/v1/auth/register-admin \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Admin Electoral","email":"admin@example.com","password":"ChangeMe12345","organization":"ActaTrace"}'
```

Login:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"ChangeMe12345"}'
```

## Security Notes

- No hardcoded production credentials are included.
- Passwords are hashed with bcrypt.
- JWT secrets come from the environment.
- Public citizen APIs are intentionally not implemented in Phase 2.
- Audit log update/delete endpoints are intentionally omitted.
- Do not log passwords, tokens, or document contents.
