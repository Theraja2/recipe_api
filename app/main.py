from fastapi import FastAPI

from app.routers.recipes import router as recipes_router



app = FastAPI(
    title="Recipe API",
    description="A backend API for creating, storing, searching, and retrieving recipes.",
    version="1.0.0",
)


@app.get("/")
async def root():
    return {"message": "Welcome to the Recipe API"}


app.include_router(recipes_router)