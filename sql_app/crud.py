from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from . import models, schemas
from pytz import timezone
from datetime import datetime


# 유저 생성
def create_user(db: Session, user: schemas.UserCreate):
    # 동일한 이름을 가진 사용자가 있는지 확인
    existing_user = db.query(models.User).filter((models.User.name == user.name) | (models.User.email == user.email)).first()
    # 동일한 이름을 가진 사용자가 있으면 에러 반환
    if existing_user is not None:
        raise HTTPException(status_code=400, detail="이미 동일한 이름을 가진 사용자가 있습니다.")

    db_user = models.User(**user.dict())
    db.add(db_user)
    try:
        db.commit()
    except IntegrityError:
        # 중복 키 제약 조건과 같은 데이터베이스 오류 처리
        db.rollback()
        raise HTTPException(status_code=400, detail="이미 동일한 이름을 가진 사용자가 있습니다.")
    db.refresh(db_user)
    return db_user

# 유저 조회
def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.name == username).first()

def create_user(db, user: schemas.UserCreate):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

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
    user = db.query(models.User).filter(models.User.name == user_name).first()

    # 사용자가 존재하는지 확인
    if not user:
        raise HTTPException(status_code=400, detail="사용자를 찾을 수 없습니다.")
    
    # 사용자가 빌린 모든 우산 가져오기
    umbrellas = db.query(models.Umbrella).filter(models.Umbrella.owner_name == user_name).all()
    
    # borrowed 상태인 우산이 있는지 검사
    borrowed_umbrellas = [umbrella for umbrella in umbrellas if umbrella.status == 'borrowed']
    
    if borrowed_umbrellas:
        # borrowed 상태인 우산이 하나라도 있을 경우
        return schemas.UserWithUmbrella(user=user, umbrella=borrowed_umbrellas[0], status="borrowed")
    else:
        return schemas.UserWithUmbrella(user=user, umbrella=None, status="available")

def borrow_umbrella(db: Session, umbrella_id: int, username: str):
    user = db.query(models.User).filter(models.User.name == username).first()
    # 사용자 존재여부 확인
    if user is None:
        raise HTTPException(status_code=400, detail="사용자를 찾을 수 없습니다.")

    umbrella = db.query(models.Umbrella).filter(models.Umbrella.id == umbrella_id).first()
    # 우산 존재 여부 확인
    if umbrella is None:
        raise HTTPException(status_code=400, detail="우산을 찾을 수 없습니다.")
    user_umbrella = db.query(models.Umbrella).filter(models.Umbrella.owner_name == user.name, models.Umbrella.status == "borrowed").first()
    # 우산 이미 빌렸는지 확인하기
    if umbrella.status == "borrowed":
        raise HTTPException(status_code=400, detail="이미 빌려간 우산입니다.")
    if user_umbrella:
        raise HTTPException(status_code=400, detail="2개의 우산을 빌릴 수 없습니다")

    try:
        # 트랜잭션 시작
        umbrella.status = "borrowed"
        umbrella.owner_name = user.name

        umbrella_history = models.UmbrellaHistory(
            umbrella_id=umbrella_id,
            user_name=username,
            borrowed_at=datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')
        )
        db.add(umbrella_history)
        # 트랜잭션 커밋
        db.commit()

    except:
        db.rollback()
        raise HTTPException(status_code=500, detail="데이터베이스 오류")


    return {"user_name": user.name, "umbrella_id": umbrella.id}

def return_umbrella(db: Session, umbrella_id: int, username: str):
    user = db.query(models.User).filter(models.User.name == username).first()
    if user is None:
        raise HTTPException(status_code=400, detail="사용자를 찾을 수 없습니다.")
    umbrella = db.query(models.Umbrella).filter(models.Umbrella.id == umbrella_id).first()
    if umbrella is None:
        raise HTTPException(status_code=400, detail="우산을 찾을 수 없습니다.")
    
    umbrella_history = db.query(models.UmbrellaHistory).filter(
        models.UmbrellaHistory.umbrella_id == umbrella_id,
        models.UmbrellaHistory.returned_at == None
    ).first()
    if umbrella_history is None:
        raise HTTPException(status_code=400, detail="대여 이력을 찾을 수 없습니다.")
    if umbrella_history.user_name != username:
        raise HTTPException(status_code=400, detail="해당 우산을 대여한 사용자가 아닙니다.")
    
    umbrella.status = "available"
    umbrella_history.returned_at = datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')

    db.commit()

    return {"user_name": user.name, "umbrella_id": umbrella.id}

def get_histroy_username(user_name : str, db: Session):
    user = db.query(models.User).filter(models.User.name == user_name).first()
    if user is None:
        raise HTTPException(status_code=400, detail="사용자를 찾을 수 없습니다.")
    umbrella_history = db.query(models.UmbrellaHistory).filter(
        models.UmbrellaHistory.user_name == user_name
    ).all()
    return umbrella_history

def get_histroy_umbrella_id(umbrella_id : int, db: Session):
    umbrella = db.query(models.Umbrella).filter(models.Umbrella.id == umbrella_id).first()
    if umbrella is None:
        raise HTTPException(status_code=400, detail="우산을 찾을 수 없습니다.")
    umbrella_history = db.query(models.UmbrellaHistory).filter(
        models.UmbrellaHistory.umbrella_id == umbrella_id
    ).all()
    return umbrella_history

def get_all_history_count(db: Session):
    umbrella_history = db.query(models.UmbrellaHistory).all()
    return len(umbrella_history)

def lost_umbrella(db: Session, umbrella_id : int):
    umbrella = db.query(models.Umbrella).filter(models.Umbrella.id == umbrella_id).first()
    if umbrella is None:
        raise HTTPException(status_code=400, detail="우산을 찾을 수 없습니다.")
    if umbrella.status == "lost":
        raise HTTPException(status_code=400, detail="이미 분실된 우산입니다.")
    umbrella.status = "lost"
    db.commit()
    return umbrella

def get_lost_umbrella(db: Session):
    umbrella = db.query(models.Umbrella).filter(models.Umbrella.status == "lost").all()
    return umbrella

def restore_umbrella(db: Session, umbrella_id : int):
    umbrella = db.query(models.Umbrella).filter(models.Umbrella.id == umbrella_id).first()
    if umbrella is None:
        raise HTTPException(status_code=400, detail="우산을 찾을 수 없습니다.")
    if umbrella.status == "available" or umbrella.status == "borrowed":
        raise HTTPException(status_code=400, detail="분실된 우산이 아닙니다.")
    umbrella.status = "available"
    db.commit()
    return umbrella
