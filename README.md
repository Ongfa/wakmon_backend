# Wakmon Backend

The new backend for wakmon with FastAPI to create actual services for user authentication and useful data.

## Features

- **FastAPI** - Modern, fast web framework for building APIs
- **User Authentication** - JWT-based authentication system
- **SQLAlchemy** - SQL toolkit and ORM
- **Pydantic** - Data validation using Python type annotations
- **PostgreSQL** - Production database (SQLite for testing)
- **Docker** - Containerized deployment

## Project Structure

```
wakmon_backend/
├── app/
│   ├── api/          # API routes
│   │   └── auth.py   # Authentication endpoints
│   ├── core/         # Core functionality
│   │   ├── config.py # Configuration settings
│   │   └── security.py # Security utilities
│   ├── db/           # Database configuration
│   │   └── session.py
│   ├── models/       # Database models
│   │   └── user.py
│   ├── schemas/      # Pydantic schemas
│   │   └── user.py
│   └── main.py       # FastAPI application
├── tests/            # Test files
├── requirements.txt  # Python dependencies
├── Dockerfile        # Docker configuration
└── docker-compose.yml
```

## Setup

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/Ongfa/wakmon_backend.git
   cd wakmon_backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`
   - Interactive API docs: `http://localhost:8000/docs`
   - Alternative API docs: `http://localhost:8000/redoc`

### Docker Development

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

   The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login and get access token
- `GET /api/v1/auth/me` - Get current user info (requires authentication)

### Health Check

- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint

## Testing

Run tests with pytest:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=app tests/
```

## Environment Variables

Required environment variables (see `.env.example`):

- `DATABASE_URL` - Database connection string
- `SECRET_KEY` - Secret key for JWT token generation
- `ALGORITHM` - JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration time (default: 30)

## Security

- Passwords are hashed using bcrypt
- JWT tokens are used for authentication
- CORS is configured for secure cross-origin requests
- Environment variables for sensitive data

## Database Migrations

This project uses Alembic for database migrations.

### Creating Initial Migration

For a fresh database setup:

```bash
# Ensure your .env file has the correct DATABASE_URL
# Generate initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

### Creating Subsequent Migrations

After making changes to models:

```bash
# Generate migration based on model changes
alembic revision --autogenerate -m "Description of changes"

# Apply the migration
alembic upgrade head
```

### Rolling Back Migrations

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>
```

**Note:** For development/testing, you can use SQLite which will auto-create tables. For production, always use migrations.

## Development

### Adding New Endpoints

1. Create a new router in `app/api/`
2. Add the router to `app/api/__init__.py`
3. Create corresponding models, schemas, and tests

### Database Migrations

For production, use Alembic for database migrations:

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create a migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is private and proprietary.
