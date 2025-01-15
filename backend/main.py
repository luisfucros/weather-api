from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import redis

from backend import models
from backend.weather_client import WeatherClient
from backend.database import engine
from backend.rate_limit import lifespan
from fastapi_limiter.depends import RateLimiter
from backend.caching import get_cached_data, insert_data
from backend.config import settings
import json
import os


models.Base.metadata.create_all(bind=engine)

env = os.getenv("ENVIRONMENT", "test")
dependencies = []

if env != "test":
    dependencies.append(
        Depends(
            RateLimiter(times=5, seconds=10)
        )
    )

app = FastAPI(lifespan=lifespan, dependencies=dependencies)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

weather_client = WeatherClient()

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.get("/weather/{city}")
def get_weather(city: str):
    cached_data = get_cached_data(city)
    if cached_data:
        return json.loads(cached_data)
    
    weather_data = weather_client.get_weather(city)

    if weather_data.get('cod') == 200:
        insert_data(city, weather_data)
    
    return weather_data
