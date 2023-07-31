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

@app.post("/umbrellas/borrow", response_model=schemas.BorrowReturnResponse)
def borrow_umbrella(borrow_data: schemas.BorrowUmbrella, db: Session = Depends(get_db)):
    return crud.borrow_umbrella(db, borrow_data=borrow_data)

@app.post("/umbrellas/return", response_model=schemas.BorrowReturnResponse)
def return_umbrella(return_data: schemas.ReturnUmbrella, db: Session = Depends(get_db)):
    """우산 반납 처리를 합니다."""
    return crud.return_umbrella(db, return_data=return_data)

# 사용자 생성
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)

@app.get("/users/{user_name}", response_model=schemas.UserWithUmbrella)
def read_user_with_umbrella(user_name: str, db: Session = Depends(get_db)):
    return crud.get_user_with_umbrella(db, user_name=user_name)

# 사용자 조회
@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_users(db, skip=skip, limit=limit)

# Umbrella Endpoints
@app.post("/umbrellas/", response_model=schemas.Umbrella)
def create_umbrella(umbrella: schemas.UmbrellaCreate, db: Session = Depends(get_db)):
    return crud.create_umbrella(db=db, umbrella=umbrella)

# 우산 상태 조회
@app.get("/umbrellas/{umbrella_id}", response_model=schemas.Umbrella)
def read_umbrella(umbrella_id: int, db: Session = Depends(get_db)):
    umbrella = crud.get_umbrella(db, umbrella_id=umbrella_id)
    if umbrella is None:
        raise HTTPException(status_code=404, detail="Umbrella not found")
    return umbrella

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

# 우산 대여 이력 조회
@app.get("/umbrella-history/", response_model=List[schemas.UmbrellaHistory])
def read_umbrella_history(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_umbrella_history(db, skip=skip, limit=limit)
