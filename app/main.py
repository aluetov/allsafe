from fastapi import FastAPI
from .routers import scanner

app = FastAPI()
app.include_router(scanner.router)

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
