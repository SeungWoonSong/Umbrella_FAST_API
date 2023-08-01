from sqlalchemy.orm import Session
from . import models, schemas
from pytz import timezone
from datetime import datetime

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
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

def get_user_with_umbrella(db: Session, user_name: str):
    user_db = db.query(models.User).filter(models.User.name == user_name).first()
    umbrella_db = db.query(models.Umbrella).filter(models.Umbrella.owner_name == user_db.id).first()

    user = schemas.User.from_orm(user_db) # User ORM 객체를 Pydantic 모델로 변환
    umbrella = schemas.Umbrella.from_orm(umbrella_db) if umbrella_db else None # Umbrella ORM 객체를 Pydantic 모델로 변환

    if umbrella:
        logger.info("UMBRELLA")
        return schemas.UserWithUmbrella(user=user, umbrella=umbrella, status="borrowed")
    else:
        logger.info("NO UMBERELLA")
        return schemas.UserWithUmbrella(user=user, umbrella=None, status="available")

def borrow_umbrella(db: Session, borrow_data: schemas.BorrowUmbrella):
    user = db.query(models.User).filter(models.User.name == borrow_data.user_name).first()
    umbrella = db.query(models.Umbrella).filter(models.Umbrella.id == borrow_data.umbrella_id).first()

    user.status = "borrowed"
    umbrella.status = "borrowed"
    
    umbrella_history = models.UmbrellaHistory(
        umbrella_id=borrow_data.umbrella_id,
        user_id=borrow_data.user_id,
        borrowed_at=datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')
    )
    db.add(umbrella_history)
    db.commit()

    return {"name": user.name, "umbrella_id": umbrella.id}

def return_umbrella(db: Session, return_data: schemas.ReturnUmbrella):
    user = db.query(models.User).filter(models.User.name == return_data.user_name).first()
    umbrella = db.query(models.Umbrella).filter(models.Umbrella.id == return_data.umbrella_id).first()

    user.status = "available"
    umbrella.status = "available"
    
    umbrella_history = db.query(models.UmbrellaHistory).filter(
        models.UmbrellaHistory.umbrella_id == return_data.umbrella_id,
        models.UmbrellaHistory.returned_at == None
    ).first()
    umbrella_history.returned_at = datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')

    db.commit()

    return {"name": user.name, "umbrella_id": umbrella.id}

# 'available', 'borrowed', 'lost'