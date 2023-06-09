import os
from pathlib import Path
from dotenv import load_dotenv

DOTENV_PATH = Path('.') / '.env'
load_dotenv(DOTENV_PATH)


class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    SERVER_ADDRESS = os.getenv('SERVER_ADDRESS')
    DEVICE_ID = os.getenv('DEVICE_ID')
