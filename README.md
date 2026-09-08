# STUDENT NAME : OBASI CHUKWUDI
# APP-2025-47595


# Recipe API

A backend REST API built with FastAPI for managing recipes, ingredients, categories, users, authentication, recipe ownership, public recipes, search, filtering, and preparation/cooking time.

## Features

- User registration
- User login
- JWT authentication
- Access tokens
- Refresh tokens
- Password hashing
- Protected recipe endpoints
- Recipe ownership
- Public recipes
- Recipe CRUD operations
- Category management
- Ingredient management
- Multiple ingredient filtering
- Category filtering
- Preparation time filtering
- Cooking time filtering
- Combined recipe filters
- Async API testing
- Swagger API documentation

## Technologies

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy 2.0
- Async SQLAlchemy
- asyncpg
- Pydantic
- Alembic
- JWT
- pytest
- pytest-asyncio
- HTTPX

## Architecture

The project uses asynchronous programming throughout the application.

The production database uses PostgreSQL with SQLAlchemy 2.0's asynchronous API.

The ORM models use:

- `Mapped`
- `mapped_column`
- `relationship`
- `DeclarativeBase`

The application uses:

- `AsyncSession`
- `async_sessionmaker`
- `create_async_engine`

## Project Structure

```text
recipe-api/
│
├── app/
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── exceptions.py
│   │
│   ├── database/
│   │   ├── base.py
│   │   └── database.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── category.py
│   │   ├── recipe.py
│   │   ├── ingredient.py
│   │   ├── recipe_ingredient.py
│   │   └── recipe_step.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── category.py
│   │   ├── recipe.py
│   │   ├── ingredient.py
│   │   ├── recipe_ingredient.py
│   │   └── recipe_step.py
│   │
│   ├── routers/
│   │   ├── auth.py
│   │   ├── recipes.py
│   │   ├── ingredients.py
│   │   └── categories.py
│   │
│   └── dependencies/
│       ├── auth.py
│       └── database.py
│
├── tests/
│   ├── conftest.py
│   └── test_health.py
│
├── alembic/
│   ├── versions/
│   └── env.py
│
├── .env
├── .env.example
├── .gitignore
├── alembic.ini
├── pytest.ini
├── requirements.txt
└── README.md