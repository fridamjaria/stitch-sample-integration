import os

from dotenv import load_dotenv


# Load env variables from .env file
load_dotenv()

class Settings:
    STITCH_CLIENT_ID = os.getenv("STITCH_CLIENT_ID")
    STITCH_CLIENT_SECRET = os.getenv("STITCH_CLIENT_SECRET")

settings = Settings()
