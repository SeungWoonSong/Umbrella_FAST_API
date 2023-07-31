from sqlalchemy.orm import Session
from . import models, schemas

# User CRUD
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

# Umbrella CRUD
def create_umbrella(db: Session, umbrella: schemas.UmbrellaCreate):
    db_umbrella = models.Umbrella(**umbrella.dict())
    db.add(db_umbrella)
    db.commit()
    db.refresh(db_umbrella)
    return db_umbrella

def get_umbrella(db: Session, umbrella_id: int):
    return db.query(models.Umbrella).filter(models.Umbrella.id == umbrella_id).first()

def get_umbrellas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Umbrella).offset(skip).limit(limit).all()

# UmbrellaHistory CRUD
def create_umbrella_history(db: Session, history: schemas.UmbrellaHistoryCreate):
    db_history = models.UmbrellaHistory(**history.dict())
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history

def get_umbrella_history(db: Session, history_id: int):
    return db.query(models.UmbrellaHistory).filter(models.UmbrellaHistory.id == history_id).first()

def get_umbrella_histories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.UmbrellaHistory).offset(skip).limit(limit).all()
