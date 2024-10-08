import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
USE_DATABASE = os.getenv("USE_DATABASE", "False").lower() == "true"
DATABASE_URL = os.getenv("DATABASE_URL") if USE_DATABASE else None