import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

class Configurations:
    CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_PATH", BASE_DIR / "secrets.json")
    SPREADSHEET_IDS_DIR = os.getenv("SPREADSHEET_IDS_DIR", BASE_DIR / "spreadsheets")
    DEFAULT_SHEET_RANGE = os.getenv("DEFAULT_SHEET_RANGE", "Sheet1!A1:Z1000")  

    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly"
    ]

    SERVER_NAME = os.getenv("MCP_SERVER_NAME", "spreadsheet-analyzer")
    SERVER_VERSION = os.getenv("MCP_SERVER_VERSION", "0.1.0")
    SUPPORTED_TOOLS = ["get_insights", "get_future_recommendations"]
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
    ANTHROPIC_MAX_TOKENS = int(os.getenv("ANTHROPIC_MAX_TOKENS", "1000"))
    DEFAULT_NUM_ROWS_FOR_ANALYSIS = int(os.getenv("NUM_ROWS_FOR_ANALYSIS", 500))
    SPREADSHEET_FOLDER_NAME = os.getenv("SPREADSHEET_FOLDER_NAME", "Khaapa_Directory")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    MAX_SHEETS = int(os.getenv("MAX_SHEETS", 100))

