from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from . import models, schemas
from pytz import timezone
from datetime import datetime

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# 유저 생성
def create_user(db: Session, user: schemas.UserCreate):
    # 동일한 이름을 가진 사용자가 있는지 확인
    existing_user = db.query(models.User).filter(models.User.name == user.name).first()
    if existing_user:
        # 동일한 이름을 가진 사용자가 있으면 에러 반환
        raise HTTPException(status_code=400, detail="이미 동일한 이름을 가진 사용자가 있습니다.")

    db_user = models.User(**user.dict())
    db.add(db_user)
    try:
        db.commit()
    except IntegrityError:
        # 중복 키 제약 조건과 같은 데이터베이스 오류 처리
        db.rollback()
        raise ValueError("이미 동일한 이름을 가진 사용자가 있습니다.")
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

def get_umbrella(db: Session, umbrella_id: int):
    return db.query(models.Umbrella).filter(models.Umbrella.id == umbrella_id).first()

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
    umbrella_db = db.query(models.Umbrella).filter(models.Umbrella.owner_name == user_db.name).first()

    user = schemas.User.from_orm(user_db) # User ORM 객체를 Pydantic 모델로 변환
    umbrella = schemas.Umbrella.from_orm(umbrella_db) if umbrella_db else None # Umbrella ORM 객체를 Pydantic 모델로 변환

    if umbrella:
        return schemas.UserWithUmbrella(user=user, umbrella=umbrella, status="borrowed")
    else:
        return schemas.UserWithUmbrella(user=user, umbrella=None, status="available")

def borrow_umbrella(db: Session, borrow_data: schemas.BorrowUmbrella):
    user = db.query(models.User).filter(models.User.name == borrow_data.user_name).first()
    if user is None:
        raise HTTPException(status_code=400, detail="사용자를 찾을 수 없습니다.")

    umbrella = db.query(models.Umbrella).filter(models.Umbrella.id == borrow_data.umbrella_id).first()
    if umbrella is None:
        raise HTTPException(status_code=400, detail="우산을 찾을 수 없습니다.")

    if user.umbrellas is not None:
        raise HTTPException(status_code=400, detail="우산을 2개 빌릴 수는 없습니다.")

    umbrella.status = "borrowed"
    umbrella.owner_name = user.name
    
    umbrella_history = models.UmbrellaHistory(
        umbrella_id=borrow_data.umbrella_id,
        user_name=borrow_data.user_name,
        borrowed_at=datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')
    )
    db.add(umbrella_history)
    db.commit()

    return {"user_name": user.name, "umbrella_id": umbrella.id}

def return_umbrella(db: Session, return_data: schemas.ReturnUmbrella):
    user = db.query(models.User).filter(models.User.name == return_data.user_name).first()
    if user is None:
        raise HTTPException(status_code=400, detail="사용자를 찾을 수 없습니다.")
    umbrella = db.query(models.Umbrella).filter(models.Umbrella.id == return_data.umbrella_id).first()
    if umbrella is None:
        raise HTTPException(status_code=400, detail="우산을 찾을 수 없습니다.")
    if user.umbrellas is None:
        raise HTTPException(status_code=400, detail="빌린 우산이 없습니다.")

    umbrella.status = "available"
    
    umbrella_history = db.query(models.UmbrellaHistory).filter(
        models.UmbrellaHistory.umbrella_id == return_data.umbrella_id,
        models.UmbrellaHistory.returned_at == None
    ).first()
    umbrella_history.returned_at = datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')

    db.commit()

    return {"user_name": user.name, "umbrella_id": umbrella.id}

# 'available', 'borrowed', 'lost'