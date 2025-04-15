import os
from io import BytesIO
import pandas as pd
import sys
from mcp.server.fastmcp import FastMCP

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from configs.configuration import Configurations

from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.service_account import Credentials

configs = Configurations()
mcp = FastMCP(configs.SERVER_NAME)

# Auth and gspread client
creds = Credentials.from_service_account_file(
    configs.CREDENTIALS_FILE, 
    scopes=configs.SCOPES
)

drive_service = build('drive', 'v3', credentials=creds)
sheets_service = build('sheets', 'v4', credentials=creds)

def read_excel_from_drive(file_id: str):
    request = drive_service.files().get_media(fileId=file_id)
    fh = BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()

    fh.seek(0)
    df = pd.read_excel(fh)

    return df

def find_folder_id(folder_name: str):
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder'"
    results = drive_service.files().list(q=query, fields="files(id)").execute()
    folders = results.get("files", []) 

    if folders:
        return folders[0]["id"]
    else:
        return None 

def list_spreadsheets(folder_id: str):
    query = f"'{folder_id}' in parents and mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'"
    results = drive_service.files().list(q=query, pageSize=configs.MAX_SHEETS, fields="files(id, name)").execute() 

    return results.get("files", [])

def read_spreadsheet(file_id: str):
    result = sheets_service.spreadsheets().values().get(spreadsheetId=file_id, range="A1:Z1000").execute()
    values = result.get("values", [])
    if not values:
        return pd.DataFrame()
    df = pd.DataFrame(values[1:], columns=values[0])
    return df

def load_all_data():
    folder_id = find_folder_id(configs.SPREADSHEET_FOLDER_NAME) 

    if not folder_id:
        return []

    files = list_spreadsheets(folder_id) 
    dataframes = []
    
    for file in files:
        df = read_excel_from_drive(file["id"])
        df["_source"] = file["name"]
        dataframes.append(df)
    
    return dataframes

ALL_DFS = load_all_data() 

@mcp.tool()
async def get_insights() -> str:
    """Returns key insights from the loaded spreadsheets."""
    if not ALL_DFS:
        return "No data found."

    insights = []
    for df in ALL_DFS:
        cols = ", ".join(map(str, df.columns))
        insights.append(f"Sheet: {df['_source'].iloc[0]}\nColumns: {cols}\nRows: {len(df)}")

    return "\n\n".join(insights)

@mcp.tool()
async def get_future_recommendations() -> str:
    """Returns future recommendations based on spreadsheet patterns."""
    if not ALL_DFS:
        return "No data to generate recommendations."

    # Dummy logic (customize with ML/stats)
    recommendations = []
    for df in ALL_DFS:
        rec = f"Sheet: {df['_source'].iloc[0]} — consider monitoring columns like {df.columns[:2].tolist()}"
        recommendations.append(rec)

    return "\n".join(recommendations)

if __name__ == "__main__":
    print("Running MCP server...")
    mcp.run(transport="stdio")
    print("MCP server is running.")
