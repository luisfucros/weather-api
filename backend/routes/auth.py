from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend import schemas
from backend.database import database, models
from backend.utils import oauth2, utils

router = APIRouter(tags=['Authentication'])

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=schemas.Token)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
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

@router.post('/login', response_model=schemas.Token)
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