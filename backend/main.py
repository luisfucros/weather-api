from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from backend import models
from backend.weather_client import WeatherClient
from backend.database import engine
from backend.rate_limit import lifespan
from fastapi_limiter.depends import RateLimiter
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
    return weather_client.get_weather(city)
