import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file explicitly from the project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

class OTPConfig:
    EXPIRY_MINUTES = 5
    MAX_ATTEMPTS = 3
    MAX_RESENDS = 3
    RESEND_COOLDOWN_MINUTES = 1

class Settings:
    RAZORPAY_KEY_ID: str = os.getenv("RAZORPAY_KEY_ID")
    RAZORPAY_KEY_SECRET: str = os.getenv("RAZORPAY_KEY_SECRET")

settings = Settings()