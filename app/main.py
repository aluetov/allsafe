from fastapi import FastAPI
from contextlib import asynccontextmanager
from .routers import scanner
from .db.db import create_tables

@asynccontextmanager
async def lifespan(app:FastAPI):
    await create_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(scanner.router)

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
