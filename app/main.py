from fastapi import FastAPI
from app.core.config import settings
import requests
from app.api.endpoints import router as api_router


app = FastAPI()


@app.get("/")
def simple_api():
    return {"message": "Hello, World!"}

app.include_router(api_router)