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
    query = f"'{folder_id}' in parents and mimeType = 'application/vnd.google-apps.spreadsheet'"
    results = drive_service.files().list(q=query, pageSize=configs.MAX_SHEETS, fields="files(id, name)").execute() 

    return results.get("files", [])

def read_spreadsheet(file_id: str):
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=file_id, range="A1:Z1000"
    ).execute()

    values = result.get("values", [])
    if not values:
        return pd.DataFrame()

    headers = values[0]
    rows = values[1:]

    normalized_rows = []
    for row in rows:
        if len(row) < len(headers):
            # Pad short rows
            row += [None] * (len(headers) - len(row))
        elif len(row) > len(headers):
            # Trim long rows
            row = row[:len(headers)]
        normalized_rows.append(row)

    df = pd.DataFrame(normalized_rows, columns=headers)
    return df

def load_all_data():
    folder_id = find_folder_id(configs.SPREADSHEET_FOLDER_NAME) 

    if not folder_id:
        return []

    files = list_spreadsheets(folder_id) 
    dataframes = []
    
    for file in files:
        df = read_spreadsheet(file["id"])
        df["_source"] = file["name"]
        dataframes.append(df)
    
    return dataframes

ALL_DFS = load_all_data() 


def get_insights(ALL_DFS) -> str:
    """Returns key insights from the loaded spreadsheets."""
    if not ALL_DFS:
        return "No data found."

    insights = []
    for df in ALL_DFS:
        source = df["_source"].iloc[0]
        cols = df.columns.tolist()
        num_rows = len(df)

        summary = f"Sheet: {source}\nColumns: {', '.join(cols)}\nRows: {num_rows}\n"

        # Try to pull some insights depending on sheet type
        if "Inventory" in source:
            summary += f"→ Appears to be an inventory sheet.\n"
            if "Total Profit" in df.columns:
                try:
                    df["Total Profit"] = pd.to_numeric(df["Total Profit"], errors="coerce")
                    total_profit = df["Total Profit"].sum()
                    summary += f"→ Total Profit: {total_profit}\n"
                except:
                    summary += f"→ Couldn't parse Total Profit.\n"

        elif "Fund" in source:
            summary += f"→ Appears to be a class fund sheet.\n"
            if "Amount Collection 1" in df.columns:
                df["Amount Collection 1"] = pd.to_numeric(df["Amount Collection 1"], errors="coerce")
                total_collected = df["Amount Collection 1"].sum()
                summary += f"→ Total collected (round 1): {total_collected}\n"

        elif "Khapa" in source or "Timetable" in source:
            summary += f"→ Likely a schedule or attendance sheet.\n"
            if "Day" in df.columns:
                unique_days = df["Day"].nunique()
                summary += f"→ Number of unique days: {unique_days}\n"

        insights.append(summary)

    return "\n\n".join(insights)

def get_future_recommendations(ALL_DFS) -> str:
    """Returns future recommendations based on the data."""
    recommendations = []

    for df in ALL_DFS:
        source = df["_source"].iloc[0]
        if "Inventory" in source:
            recommendations.append(f"📦 Inventory Sheet:\n→ Consider restocking items with zero quantity.\n")
        elif "Fund" in source:
            recommendations.append(f"💰 Fund Sheet:\n→ Encourage members who haven't paid to contribute.\n")
        elif "Khapa" in source:
            recommendations.append(f"📅 Schedule Sheet:\n→ Consider filling the empty time slots or rotating team members.\n")

    return "\n\n".join(recommendations)

# def get_future_recommendations(ALL_DFS) -> str:
#     """Returns future recommendations based on spreadsheet patterns."""
#     if not ALL_DFS:
#         return "No data to generate recommendations."

#     # Dummy logic (customize with ML/stats)
#     recommendations = []
#     for df in ALL_DFS:
#         rec = f"Sheet: {df['_source'].iloc[0]} — consider monitoring columns like {df.columns[:2].tolist()}"
#         recommendations.append(rec)

#     return "\n".join(recommendations)

# def get_insights(ALL_DFS) -> str:
#     """Returns key insights from the loaded spreadsheets."""
#     if not ALL_DFS:
#         return "No data found."

#     insights = []
#     for df in ALL_DFS:
#         cols = ", ".join(map(str, df.columns))
#         insights.append(f"Sheet: {df['_source'].iloc[0]}\nColumns: {cols}\nRows: {len(df)}")
#         insights.append(f"Actual Rows: {df}")

#     return "\n\n".join(insights)

print(get_future_recommendations(ALL_DFS))
print("-------------------------------------------------") 