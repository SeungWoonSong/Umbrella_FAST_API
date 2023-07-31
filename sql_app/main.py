from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import SessionLocal, engine
from typing import List


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to Umbrella API!"}

# User Endpoints
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)

@app.get("/users/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user(db, user_id=user_id)

@app.get("/users/", response_model=List[schemas.User])
def get_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_users(db, skip=skip, limit=limit)

# Umbrella Endpoints
@app.post("/umbrellas/", response_model=schemas.Umbrella)
def create_umbrella(umbrella: schemas.UmbrellaCreate, db: Session = Depends(get_db)):
    return crud.create_umbrella(db=db, umbrella=umbrella)

@app.get("/umbrellas/{umbrella_id}", response_model=schemas.Umbrella)
def get_umbrella(umbrella_id: int, db: Session = Depends(get_db)):
    return crud.get_umbrella(db, umbrella_id=umbrella_id)

@app.get("/umbrellas/", response_model=List[schemas.Umbrella])
def get_umbrellas(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_umbrellas(db, skip=skip, limit=limit)

# UmbrellaHistory Endpoints
@app.post("/umbrella-history/", response_model=schemas.UmbrellaHistory)
def create_umbrella_history(history: schemas.UmbrellaHistoryCreate, db: Session = Depends(get_db)):
    return crud.create_umbrella_history(db=db, history=history)

@app.get("/umbrella-history/{history_id}", response_model=schemas.UmbrellaHistory)
def get_umbrella_history(history_id: int, db: Session = Depends(get_db)):
    return crud.get_umbrella_history(db, history_id=history_id)

@app.get("/umbrella-history/", response_model=List[schemas.UmbrellaHistory])
def get_umbrella_histories(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_umbrella_histories(db, skip=skip, limit=limit)
