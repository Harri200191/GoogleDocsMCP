import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Configurations:
    CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_PATH", BASE_DIR / "credentials.json")
    SPREADSHEET_IDS_DIR = os.getenv("SPREADSHEET_IDS_DIR", BASE_DIR / "spreadsheets")
    DEFAULT_SHEET_RANGE = os.getenv("DEFAULT_SHEET_RANGE", "Sheet1!A1:Z1000")  

    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly"
    ]

    SERVER_NAME = os.getenv("MCP_SERVER_NAME", "spreadsheet-insights")
    SERVER_VERSION = os.getenv("MCP_SERVER_VERSION", "0.1.0")
    SUPPORTED_TOOLS = ["get_insights", "get_future_recommendations"]
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
    ANTHROPIC_MAX_TOKENS = int(os.getenv("ANTHROPIC_MAX_TOKENS", "1000"))
    DEFAULT_NUM_ROWS_FOR_ANALYSIS = int(os.getenv("NUM_ROWS_FOR_ANALYSIS", 500))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

