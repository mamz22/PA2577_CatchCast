import httpx
from fastapi import FastAPI, HTTPException, Query

app = FastAPI(
    title="Weather Service",
    version="0.1.0"
)

WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast" # public API key, change to env var if that changes

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "weather-service"}

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

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                WEATHER_API_URL,
                params=params,
            )
            response.raise_for_status()

    except httpx.HTTPError as error:
        raise HTTPException(
            status_code=502,
            detail="Could not retrieve weather data",
        ) from error

    data = response.json()
    current = data.get("current")

    if current is None:
        raise HTTPException(
            status_code=502,
            detail="Weather API returned unexpected response",
        )

    return {
        "latitude": data["latitude"],
        "longitude": data["longitude"],
        "temperature_c": current["temperature_2m"],
        "humidity_percent": current["relative_humidity_2m"],
        "wind_speed_mps": current["wind_speed_10m"],
        "observed_at": current["time"],
    }