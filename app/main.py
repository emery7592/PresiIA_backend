from fastapi import FastAPI
from app.routers.example import router as example_router

app = FastAPI()

app.include_router(example_router)

@app.get("/")
async def root():
    return {"message": "API up!"}
