from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
import os

# LOG
import requests
import json


load_dotenv()  # .env 파일에서 환경 변수를 로드합니다.
# Set up Slack bot token and channel information
slack_bot_token = os.getenv("SLACK_TOKEN")
slack_channel = os.getenv("SLACK_CHANNEL")
apiKey = os.getenv("API_KEY")
