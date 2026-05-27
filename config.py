from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    FH2_URL = os.getenv("FH2_URL")
    FH2_USER_TOKEN = os.getenv("FH2_USER_TOKEN")
    FH2_PROJECT_UUID = os.getenv("FH2_PROJECT_UUID")
    FH2_WORKFLOW_UUID = os.getenv("FH2_WORKFLOW_UUID")
    FH2_CREATOR_ID = os.getenv("FH2_CREATOR_ID")
    FH2_HOST_HEADER = os.getenv("FH2_HOST_HEADER")

    DEFAULT_LATITUDE = float(os.getenv("DEFAULT_LATITUDE", "0"))
    DEFAULT_LONGITUDE = float(os.getenv("DEFAULT_LONGITUDE", "0"))
    DEFAULT_LEVEL = int(os.getenv("DEFAULT_LEVEL", "5"))
    DEFAULT_DESCRIPTION = os.getenv(
        "DEFAULT_DESCRIPTION",
        "Movimiento detectado por HikCentral"
    )