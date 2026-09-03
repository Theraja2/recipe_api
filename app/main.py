from fastapi import FastAPI


app = FastAPI(
    title="Recipe API",
    description="A backend API for creating, storing, searching, and retrieving recipes.",
    version="1.0.0",
)


@app.get("/")
async def root():
    return {"message": "Welcome to the Recipe API"}