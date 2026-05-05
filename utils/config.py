import os
from dotenv import load_dotenv

load_dotenv(override=True)

BASE_URL = os.getenv("BASE_URL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

VIDEOS_DIR = "reports/videos"
SCREENSHOTS_DIR = "reports/screenshots"
