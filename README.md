# DAM System - Digital Asset Management

A self-hosted DAM system for archiving and managing digital assets including videos, audio, photos, and documents.

## Features

- Asset upload and storage with chunked uploads
- Classification levels: PUBLIC, REGULAR, CONFIDENTIAL
- Role-Based Access Control (RBAC)
- Metadata management and full-text search
- User management with roles
- Audit logging
- Web interface
- REST API

## Tech Stack

- Backend: FastAPI (Python)
- Database: PostgreSQL (SQLite for development)
- Frontend: Server-rendered HTML with Jinja2
- Auth: JWT
- Storage: Local filesystem

## Setup

1. Clone or download the project.

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables in `.env`:
   ```
   DATABASE_URL=sqlite:///./dam.db
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

   For PostgreSQL:
   ```
   DATABASE_URL=postgresql://user:password@localhost/dam
   ```

4. Run database migrations:
   ```
   alembic upgrade head
   ```

5. Seed the database (optional):
   ```
   python -m app.seed
   ```

6. Run the application:
   ```
   uvicorn app.main:app --reload
   ```

7. Open http://localhost:8000 in your browser.

## Usage

- Register/Login as user
- Upload assets with metadata
- Search and filter assets
- Manage users and permissions (Admin only)

## Security Notes

- All file access is through the API, no direct paths
- Permissions checked server-side
- Audit logs for all actions
- Use HTTPS in production
- Store SECRET_KEY securely

## Future Improvements

- S3/NAS storage abstraction
- Video thumbnail generation
- Advanced search with Elasticsearch
- Mobile app integration
- Bulk operations