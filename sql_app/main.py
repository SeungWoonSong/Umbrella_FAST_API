from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from . import crud, models, schemas, login, weather
from .database import SessionLocal, engine
from typing import List
import jwt
from dotenv import load_dotenv
import os

# OAuth2
from fastapi import Depends
from fastapi.security.http import HTTPBearer

# CORS
from fastapi.middleware.cors import CORSMiddleware

# ENV
load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")

models.Base.metadata.create_all(bind=engine)
# app = FastAPI()
app = FastAPI(debug=True)
# Tags
user_tags = [{"name": "Users", "description": "Operations with users"}]
umbrella_tags = [{"name": "Umbrellas", "description": "Manage umbrellas"}]
history_tags = [{"name": "History", "description": "Manage History"}]
Rent_Return = [{"name": "Rent", "description": "Manage Return and Rent"}]
Login = [{"name": "Login", "description": "Manage Login"}]
Weather = [{"name": "Weather", "description": "Get Weather"}]

# CORS
origins = [
    "http://localhost:4200",
    "https://localhost:4200",
    "http://openumbrella.site",
    "https://openumbrella.site",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT
get_user_token = HTTPBearer(auto_error=False)


def decode_token(token: str = Depends(get_user_token)):
    SECRET_KEY = JWT_SECRET
    ALGORITHM = "HS256"
    if token is None or token.credentials is None:
        raise HTTPException(
            status_code=401,
            detail="토큰이 제공되지 않았습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="제공한 토큰이 유효하지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse(url="/docs")


# LOGIN LOGIC
@app.get("/auth_url", tags=["Login"])
def auth_url():
    return login.login()


@app.get("/callback", tags=["Login"])
def callback(code: str = None, db: Session = Depends(get_db)):
    if code is None:
        raise HTTPException(status_code=400, detail="Code not provided")

    token = login.get_token(code)
    user_info = login.get_user_42name(token)
    jwt_token = login.generate_jwt_token(user_info)
    # if no user in db, create user
    if crud.get_user(db, user_info["username"]) is None:
        crud.create_user(
            db, schemas.UserCreate(name=user_info["username"], email=user_info["email"])
        )
    redirect_url = f"https://openumbrella.site/jwt?jwt_token={jwt_token}"

    # , httponly=True
    response = RedirectResponse(url=redirect_url)

    return response
    # return {"jwt_token": jwt_token}


@app.get("/me", tags=["Login"])
def me(payload: dict = Depends(decode_token)):
    return payload["username"]


@app.post("/users/", response_model=schemas.User, tags=["Users"])
def create_user_admin(
    user: schemas.UserCreate,
    userinfo=Depends(decode_token),
    db: Session = Depends(get_db),
):
    if userinfo["username"] not in ["susong", "seongyle"]:
        raise HTTPException(status_code=401, detail="권한이 없습니다.")
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
@app.post(
    "/umbrellas/borrow", response_model=schemas.BorrowReturnResponse, tags=["Rent"]
)
def borrow_umbrella(
    umbrella_id: int, userinfo=Depends(decode_token), db: Session = Depends(get_db)
):
    return crud.borrow_umbrella(db, umbrella_id, userinfo["username"])


@app.post(
    "/umbrellas/return", response_model=schemas.BorrowReturnResponse, tags=["Rent"]
)
def return_umbrella(
    umbrella_id: int, userinfo=Depends(decode_token), db: Session = Depends(get_db)
):
    return crud.return_umbrella(db, umbrella_id, userinfo["username"])


# 우산 제작
@app.post("/umbrellas/", response_model=schemas.Umbrella, tags=["Umbrellas"])
def create_umbrella(
    umbrella: schemas.UmbrellaCreate,
    userinfo=Depends(decode_token),
    db: Session = Depends(get_db),
):
    if userinfo["username"] not in ["susong", "seongyle"]:
        raise HTTPException(status_code=401, detail="권한이 없습니다.")
    return crud.create_umbrella(db=db, umbrella=umbrella)


# 우산 상태 조회
@app.get(
    "/umbrellas/{umbrella_id}", response_model=schemas.Umbrella, tags=["Umbrellas"]
)
def read_umbrella(umbrella_id: int, db: Session = Depends(get_db)):
    umbrella = crud.get_umbrella(db, umbrella_id=umbrella_id)
    if umbrella is None:
        raise HTTPException(status_code=404, detail="Umbrella not found")
    return umbrella


@app.get("/umbrellas/", response_model=List[schemas.Umbrella], tags=["Umbrellas"])
def get_umbrellas(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_umbrellas(db, skip=skip, limit=limit)


# UmbrellaHistory
@app.post(
    "/umbrella-history/", response_model=schemas.UmbrellaHistory, tags=["History"]
)
def create_umbrella_history(
    history: schemas.UmbrellaHistoryCreate,
    userinfo=Depends(decode_token),
    db: Session = Depends(get_db),
):
    if userinfo["username"] not in ["susong", "seongyle"]:
        raise HTTPException(status_code=401, detail="권한이 없습니다.")
    return crud.create_umbrella_history(db=db, history=history)


# 우산 대여 이력 조회
@app.get(
    "/umbrella-history/", response_model=List[schemas.UmbrellaHistory], tags=["History"]
)
def read_umbrella_history(
    skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    return crud.get_umbrella_history(db, skip=skip, limit=limit)


@app.get(
    "/umbrella-history/{user_name}",
    response_model=List[schemas.UmbrellaHistory],
    tags=["History"],
)
def get_history_username(user_name: str, db: Session = Depends(get_db)):
    return crud.get_histroy_username(user_name, db)


@app.get(
    "/umbrella-history-id/{umbrella_id}",
    response_model=List[schemas.UmbrellaHistory],
    tags=["History"],
)
def get_history_umbrella_id(umbrella_id: int, db: Session = Depends(get_db)):
    return crud.get_histroy_umbrella_id(umbrella_id, db)

@app.get(
    "/total",
    tags=["History"],
)
def get_total_history(db: Session = Depends(get_db)):
    return crud.get_all_history_count(db)



# 분실처리
@app.get("/lost", response_model=List[schemas.Umbrella], tags=["Lost/Found"])
def get_lost_umbrella(
    db: Session = Depends(get_db)
):
    return crud.get_lost_umbrella(db)

@app.post("/lost/{umbrella_id}", response_model=schemas.Umbrella, tags=["Lost/Found"])
def lost_umbrella(
    umbrella_id: int,
    userinfo=Depends(decode_token),
    db: Session = Depends(get_db),
):
    if userinfo["username"] not in ["susong", "seongyle", "jmaing"]:
        raise HTTPException(status_code=401, detail="권한이 없습니다.")
    return crud.lost_umbrella(db, umbrella_id)

@app.post("/restore/{umbrella_id}", response_model=schemas.Umbrella, tags=["Lost/Found"])
def lost_umbrella(
    umbrella_id: int,
    userinfo=Depends(decode_token),
    db: Session = Depends(get_db),
):
    if userinfo["username"] not in ["susong", "seongyle", "jmaing"]:
        raise HTTPException(status_code=401, detail="권한이 없습니다.")
    return crud.restore_umbrella(db, umbrella_id)

@app.get("/weather", response_model=schemas.WeatherCondition, tags=["Weather"])
def get_weather():
    return weather.get_weather()

