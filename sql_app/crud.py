from sqlalchemy.orm import Session
from . import models, schemas

# 유저 생성
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 유저 조회
def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

# 우산 생성
def create_umbrella(db: Session, umbrella: schemas.UmbrellaCreate):
    db_umbrella = models.Umbrella(**umbrella.dict())
    db.add(db_umbrella)
    db.commit()
    db.refresh(db_umbrella)
    return db_umbrella

# 우산 상태 변경
def update_umbrella_status(db: Session, umbrella_id: int, status: str):
    db_umbrella = db.query(models.Umbrella).filter(models.Umbrella.id == umbrella_id).first()
    db_umbrella.status = status
    db.commit()
    return db_umbrella

# 우산 조회
def get_umbrellas(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Umbrella).offset(skip).limit(limit).all()

# 우산 대여 이력 생성
def create_umbrella_history(db: Session, history: schemas.UmbrellaHistoryCreate):
    db_history = models.UmbrellaHistory(**history.dict())
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history

# 우산 대여 이력 조회
def get_umbrella_history(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.UmbrellaHistory).offset(skip).limit(limit).all()
