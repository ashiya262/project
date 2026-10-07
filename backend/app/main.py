from fastapi import FastAPI

from app.database.base import Base
from app.database.connection import engine
import app.models  # noqa: F401
from app.routes.alerts import router as alerts_router
from app.routes.analytics import router as analytics_router
from app.routes.auth import router as auth_router
from app.routes.battery import router as battery_router
from app.routes.readings import router as readings_router


app = FastAPI(
    title="AI-Based Smart Battery Lifecycle System",
    description="Battery monitoring, lifecycle assessment and second-life recommendations.",
    version="1.0.0",
)


@app.on_event("startup")
def initialize_database():
    Base.metadata.create_all(bind=engine)


app.include_router(auth_router)
app.include_router(battery_router)
app.include_router(readings_router)
app.include_router(alerts_router)
app.include_router(analytics_router)


@app.get("/")
def home():
    return {"message": "Smart Battery Backend is running"}
