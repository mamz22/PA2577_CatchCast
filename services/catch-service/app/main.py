from datetime import datetime, timezone

import httpx
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(
    title="Catch Service",
    version="0.1.0",
)

WEATHER_SERVICE_URL = "http://127.0.0.1:8001" # local address, if production: make env var


class CatchCreate(BaseModel):
    species: str = Field(min_length=1, max_length=100)
    length_cm: float = Field(gt=0, le=500)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "catch-service",}

@app.post("/api/catches", status_code=status.HTTP_201_CREATED)
async def create_catch(catch: CatchCreate):
    caught_at = datetime.now(timezone.utc)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{WEATHER_SERVICE_URL}/api/weather/current",
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

    weather = response.json()

    return {
        "species": catch.species,
        "length_cm": catch.length_cm,
        "latitude": catch.latitude,
        "longitude": catch.longitude,
        "caught_at": caught_at,
        "weather": weather,
    }