from fastapi import FastAPI

from app.routers import auth
from app.routers import categories
from app.routers import ingredients
from app.routers import recipes


app = FastAPI(
    title="Recipe API",
    description="A Recipe API built with FastAPI, PostgreSQL and Async SQLAlchemy 2.0",
    version="1.0.0"
)


app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(recipes.router)
app.include_router(ingredients.router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to the Recipe API"
    }