import logging

import httpx
from fastapi import FastAPI, HTTPException, Query

from app.settings import settings

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Weather Service",
    version="0.2.0"
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "weather-service"}

async def get_location_name(
    client: httpx.AsyncClient,
    latitude: float,
    longitude: float,
) -> str:
    try:
        response = await client.get(
            settings.geocoding_api_url,
            params={
                "lat": latitude,
                "lon": longitude,
                "format": "jsonv2",
                "zoom": 12,
                "addressdetails": 1,
            },
            headers={
                "User-Agent": settings.geocoding_user_agent,
            },
        )

        response.raise_for_status()
        data = response.json()

        return data.get(
            "display_name",
            f"{latitude:.5f}, {longitude:.5f}",
        )

    except (httpx.HTTPError, ValueError) as error:
        logger.warning(
            "Could not reverse geocode coordinates: %s",
            error,
        )

        # A geocoding failure should not prevent saving the catch.
        return f"{latitude:.5f}, {longitude:.5f}"

@app.get("/api/weather/current")
async def get_current_weather(
    latitude: float = Query(ge=-90, le=90),
    longitude: float = Query(ge=-180, le=180),
):

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "wind_speed_10m"
        ),
        "wind_speed_unit": "ms",
    }
    # Calling the Weather API expecting 200 OK otherwise 502
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            weather_response = await client.get(
                settings.weather_api_url,
                params=params,
            )
            weather_response.raise_for_status()

            location_name = await get_location_name(
                client,
                latitude,
                longitude,
            )

    except httpx.HTTPError as error:
        logger.error(
            "Could not retrieve weather data: %s",
            error,
        )

        raise HTTPException(
            status_code=502,
            detail="Could not retrieve weather data",
        ) from error

    try:
        data = weather_response.json()
    except ValueError as error:
        raise HTTPException(
            status_code=502,
            detail="Weather API returned invalid JSON.",
        ) from error

    current = data.get("current")

    if current is None:
        raise HTTPException(
            status_code=502,
            detail="Weather API returned unexpected response",
        )
    # Return the data from the Weather API
    return {
        "latitude": data["latitude"],
        "longitude": data["longitude"],
        "location_name": location_name,
        "temperature_c": current["temperature_2m"],
        "humidity_percent": current["relative_humidity_2m"],
        "wind_speed_mps": current["wind_speed_10m"],
        "observed_at": current["time"],
    }
