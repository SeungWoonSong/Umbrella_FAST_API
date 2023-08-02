import logging
import os
from dotenv import load_dotenv
import requests
import jwt
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# ENV VALUES
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
AUTHORIZATION_URL = os.getenv("AUTHORIZATION_URL")
TOKEN_URL = os.getenv("TOKEN_URL")
USER_INFO_URL = os.getenv("USER_INFO_URL")
JWT_SECRET = os.getenv("JWT_SECRET")

def login():
	auth_url = f"{AUTHORIZATION_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code"
	return {"auth_url": auth_url}

def get_token(code: str):
    payload = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    response = requests.post(TOKEN_URL, data=payload)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="토큰 발급에 실패했습니다.")
    return response.json().get("access_token")


def get_user_42name(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(USER_INFO_URL, headers=headers)
    # logger.debug(response.json())
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="사용자 정보를 가져올 수 없습니다.")
    return {"username" : response.json().get("login"), "email" : response.json().get("email")}


def generate_jwt_token(user_info: dict):
    logger.info("JWT TOKEN GENERATE")
    payload = {"username": user_info["username"], "email": user_info["email"]}
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token

def get_current_user(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        # userinfo = payload.get("username")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload