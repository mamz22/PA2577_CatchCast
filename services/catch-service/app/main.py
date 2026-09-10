from contextlib import asynccontextmanager
from datetime import datetime, timezone

import httpx
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Catch
from app.settings import settings

from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Catch Service",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:8002",
        "http://127.0.0.1:8002",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# definition of each CatchCreate request object
class CatchCreate(BaseModel):
    species: str = Field(min_length=1, max_length=100)
    length_cm: float = Field(gt=0, le=500)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

# definition of each CatchResponse recieved object
class CatchResponse(BaseModel):
    id: int
    species: str
    length_cm: float
    latitude: float
    longitude: float
    caught_at: datetime
    temperature_c: float
    humidity_percent: int
    wind_speed_mps: float
    weather_observed_at: str
    location_name: str | None = None

    model_config = ConfigDict(from_attributes=True)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "catch-service",}


@app.post("/api/catches", response_model=CatchResponse, status_code=status.HTTP_201_CREATED)
def create_catch(
    catch: CatchCreate,
    database: Session = Depends(get_db),
):
    caught_at = datetime.now(timezone.utc)

    # Send cordinates to Weather service -> recives current weather status
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(
                f"{settings.weather_service_url}/api/weather/current",
                params={
                    "latitude": catch.latitude,
                    "longitude": catch.longitude,
                },
            )
            response.raise_for_status()

    except httpx.HTTPError as error:
        raise HTTPException(
            status_code=502,
            detail="Could not retrieve weather information",
        ) from error

    weather = response.json() # Saves weather

    # creates a catch_record object with the additional weather information from the weather service
    catch_record = Catch(
        species = catch.species,
        length_cm = catch.length_cm,
        latitude = catch.latitude,
        longitude = catch.longitude,
        location_name=(
            weather.get("location_name") or f"{catch.latitude:.5f}, {catch.longitude:.5f}"
        ),
        caught_at = caught_at,
        temperature_c = weather["temperature_c"],
        humidity_percent = weather["humidity_percent"],
        wind_speed_mps = weather["wind_speed_mps"],
        weather_observed_at = weather["observed_at"],
    )
    # now we try to add it into our database
    try:
        database.add(catch_record)
        database.commit()
        database.refresh(catch_record)
    except SQLAlchemyError as error:
        database.rollback()
        raise HTTPException(
            statuscode=500,
            detail="Could not save catch",
        ) from error

    return catch_record

@app.get(
    "/api/catches",
    response_model=list[CatchResponse],
)
def get_catches(database: Session = Depends(get_db)):
    statement = select(Catch).order_by(Catch.caught_at.desc())
    return list(database.scalars(statement).all())