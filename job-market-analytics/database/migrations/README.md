# Database Migrations

This directory will store database migration scripts managed by Alembic.

## Usage (Planned)
```bash
# Generate a new migration revision
alembic revision --autogenerate -m "create job postings table"

# Apply migrations
alembic upgrade head
```
