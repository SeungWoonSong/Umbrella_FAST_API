import logging
import os
from dotenv import load_dotenv
import requests
import jwt
from fastapi import HTTPException

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
        raise HTTPException(status_code=400, detail="Failed to get token")
    return response.json().get("access_token")

def get_user_name(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(USER_INFO_URL, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get user info")
    return response.json().get("name")

def generate_jwt_token(username: str):
    payload = {"username": username}
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token