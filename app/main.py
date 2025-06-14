from fastapi import FastAPI

app = FastAPI()

"""Simple FastAPI application with a single endpoint."""
@app.get("/")
def simple_api():
    return {"message": "Hello, World!"}