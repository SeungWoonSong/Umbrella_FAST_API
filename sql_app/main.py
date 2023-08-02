from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from . import crud, models, schemas, login
from .database import SessionLocal, engine
from typing import List

#OAuth2
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer

#CORS
from fastapi.middleware.cors import CORSMiddleware

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

models.Base.metadata.create_all(bind=engine)
app = FastAPI()
# Bearer
get_bearer_token = HTTPBearer(auto_error=False)

#Logger
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Tags
user_tags = [{"name": "Users", "description": "Operations with users"}]
umbrella_tags = [{"name": "Umbrellas", "description": "Manage umbrellas"}]
history_tags = [{"name": "History", "description": "Manage History"}]
Rent_Return = [{"name": "Rent", "description": "Manage Return and Rent"}]
Login = [{"name": "Login", "description": "Manage Login"}]

#CORS
origins = [
    "http://localhost:4200",
    "https://localhost:4200",
    "http://openumbrella.site",
    "http://openumbrella.site",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# LOGIN LOGIC
@app.get("/auth_url", tags=["Login"])
def auth_url():
    return login.login()

@app.get("/callback")
def callback(code: str = None):
    if code is None:
        raise HTTPException(status_code=400, detail="Code not provided")
    
    token = login.get_token(code)
    user_info = login.get_user_name(token)
    jwt_token = login.generate_jwt_token(user_info)
    
    # logger.debug("DECODED", login.get_current_user(jwt_token))
    return {"jwt_token": jwt_token}



@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse(url="/docs")

@app.post("/users/", response_model=schemas.User, tags=["Users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)

# 사용자 조회
@app.get("/users/{user_name}", response_model=schemas.UserWithUmbrella, tags=["Users"])
def read_user_with_umbrella(user_name: str, db: Session = Depends(get_db)):
    return crud.get_user_with_umbrella(db, user_name=user_name)

# 사용자 조회(다수))
@app.get("/users/", response_model=List[schemas.User], tags=["Users"])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_users(db, skip=skip, limit=limit)

# 핵심 로직(대여 / 반납)
@app.post("/umbrellas/borrow", response_model=schemas.BorrowReturnResponse, tags=["Rent"])
def borrow_umbrella(umbrella_id: int, userinfo = Depends(login.get_current_user), db: Session = Depends(get_db)):
    logger.debug(userinfo)
    return crud.borrow_umbrella(db, umbrella_id, userinfo["username"])

@app.post("/umbrellas/return", response_model=schemas.BorrowReturnResponse, tags=["Rent"])
def return_umbrella(umbrella_id: int, userinfo = Depends(login.get_current_user), db: Session = Depends(get_db)):
    return crud.return_umbrella(db, umbrella_id, userinfo["username"])

# 사용자 생성

# 우산 제작
@app.post("/umbrellas/", response_model=schemas.Umbrella, tags=["Umbrellas"])
def create_umbrella(umbrella: schemas.UmbrellaCreate, db: Session = Depends(get_db)):
    return crud.create_umbrella(db=db, umbrella=umbrella)

# 우산 상태 조회
@app.get("/umbrellas/{umbrella_id}", response_model=schemas.Umbrella, tags=["Umbrellas"])
def read_umbrella(umbrella_id: int, db: Session = Depends(get_db)):
    umbrella = crud.get_umbrella(db, umbrella_id=umbrella_id)
    if umbrella is None:
        raise HTTPException(status_code=404, detail="Umbrella not found")
    return umbrella

@app.get("/umbrellas/", response_model=List[schemas.Umbrella], tags=["Umbrellas"])
def get_umbrellas(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_umbrellas(db, skip=skip, limit=limit)

# UmbrellaHistory
@app.post("/umbrella-history/", response_model=schemas.UmbrellaHistory, tags=["History"])
def create_umbrella_history(history: schemas.UmbrellaHistoryCreate, db: Session = Depends(get_db)):
    return crud.create_umbrella_history(db=db, history=history)

# 우산 대여 이력 조회
@app.get("/umbrella-history/", response_model=List[schemas.UmbrellaHistory], tags=["History"])
def read_umbrella_history(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_umbrella_history(db, skip=skip, limit=limit)

@app.get("/umbrella-history/{user_name}", response_model=List[schemas.UmbrellaHistory], tags=["History"])
def get_history_username(user_name: str, db: Session = Depends(get_db)):
    return crud.get_histroy_username(user_name, db)

@app.get("/umbrella-history-id/{umbrella_id}", response_model=List[schemas.UmbrellaHistory], tags=["History"])
def get_history_umbrella_id(umbrella_id: int, db: Session = Depends(get_db)):
    return crud.get_histroy_umbrella_id(umbrella_id, db)
# @app.get("/weather")