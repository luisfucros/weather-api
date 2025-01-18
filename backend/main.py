from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from backend.database import models
from backend.database.database import engine
from backend.rate_limit import lifespan
from fastapi_limiter.depends import RateLimiter
from backend.routes import auth, weather


models.Base.metadata.create_all(bind=engine)

app = FastAPI(lifespan=lifespan, dependencies=[Depends(RateLimiter(times=5, seconds=10))])

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(weather.router)


@app.get("/")
def health_check():
    return {"status": "ok"}
