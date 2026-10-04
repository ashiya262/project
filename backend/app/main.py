from fastapi import FastAPI

from app.database.base import Base
from app.database.connection import engine
from app.models import Battery, BatteryReading
from app.routes.battery import router as battery_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-Based Smart Battery Lifecycle System",
    description="Backend for battery monitoring and second-life recommendation",
    version="1.0.0",
)

app.include_router(battery_router)


@app.get("/")
def home():
    return {"message": "Smart Battery Backend is running!"}
