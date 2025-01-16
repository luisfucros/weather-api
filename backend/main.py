from fastapi import FastAPI, Depends, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend import database, models, oauth2, schemas, utils
from backend.database import get_db
from backend.weather_client import WeatherClient
from backend.database import engine
from backend.rate_limit import lifespan
from fastapi_limiter.depends import RateLimiter
from backend.caching import get_cached_data, insert_data

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

@app.post("/register", status_code=status.HTTP_201_CREATED, response_model=schemas.Token)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    user_query = db.query(models.User).filter(
        models.User.email == user.email).first()

    if user_query:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=f"User already exists")

    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = oauth2.create_access_token(data={"user_email": user.email})

    return {"access_token": access_token, "token_type": "bearer"}

@app.post('/login', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):

    user = db.query(models.User).filter(
        models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    access_token = oauth2.create_access_token(data={"user_email": user.email})

    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/weather/{city}")
def get_weather(city: str, current_user: schemas.UserOut = Depends(oauth2.get_current_user)):
    cached_data = get_cached_data(city)
    if cached_data:
        return json.loads(cached_data)
    
    weather_data = weather_client.get_weather(city)

    if weather_data.get('cod') == 200:
        insert_data(city, weather_data)
    
    return weather_data
