from typing import Any
import gspread
from mcp.server.fastmcp import FastMCP
from google.oauth2.service_account import Credentials

mcp = FastMCP("spreadsheet-analyzer")

# Auth and gspread client
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly", "https://www.googleapis.com/auth/drive.readonly"]
creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPES)
gc = gspread.authorize(creds)

# Tool: List spreadsheets in a folder
@mcp.tool()
async def list_spreadsheets(folder_id: str) -> str:
    """List Google Sheets in a specific folder."""
    from googleapiclient.discovery import build
    drive_service = build('drive', 'v3', credentials=creds)
    results = drive_service.files().list(
        q=f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.spreadsheet'",
        fields="files(id, name)",
    ).execute()
    files = results.get('files', [])
    if not files:
        return "No spreadsheets found."
    return "\n".join([f"{f['name']} ({f['id']})" for f in files])

# Tool: Read sheet data (first sheet)
@mcp.tool()
async def get_sheet_data(spreadsheet_id: str) -> str:
    """Get the data from the first worksheet of the spreadsheet."""
    try:
        sh = gc.open_by_key(spreadsheet_id)
        worksheet = sh.get_worksheet(0)
        data = worksheet.get_all_values()
        preview = "\n".join([", ".join(row) for row in data[:10]])
        return f"Sheet: {sh.title}\nPreview:\n{preview}"
    except Exception as e:
        return f"Error reading spreadsheet: {e}"

# Tool: Analyze data and give insights
@mcp.tool()
async def get_insights(spreadsheet_id: str) -> str:
    """Give high-level insights from spreadsheet data."""
    sh = gc.open_by_key(spreadsheet_id)
    worksheet = sh.get_worksheet(0)
    data = worksheet.get_all_values()
    headers = data[0]
    rows = data[1:]
    insights = f"Sheet has {len(rows)} rows and {len(headers)} columns. Columns: {headers}"
    # You could add more logic like stats here
    return insights

# Tool: Suggest future actions based on data
@mcp.tool()
async def get_future_recommendations(spreadsheet_id: str) -> str:
    """Suggest actions based on trends in spreadsheet data."""
    # Dummy logic for now
    return "Based on current data trends, consider reviewing rows with missing values or outliers in key metrics."

if __name__ == "__main__":
    mcp.run(transport="stdio")
