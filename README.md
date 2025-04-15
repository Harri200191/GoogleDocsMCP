# 🧠 Google Sheets Analyzer MCP (Model Context Protocol)

This project is an implementation of a **Model Context Protocol (MCP)**-based system that allows you to:
- **Read** and analyze Google Sheets from a specific **Google Drive folder**
- Use tools like `get_insights`, `get_future_recommendations`, etc.
- Ask questions and get responses using **Claude AI** (Anthropic)

---

## 📂 Project Structure

```
├── flows/
├── lib/
│   └── server/
│       └── server.py         # Loads sheets from Google Drive and exposes MCP tools
│   └── client/
│       └── client.py         # Connects to MCP server and queries using Claude
├   └── configs/
│        └── configuration.py # Centralized config file
├── environment.yml           # Conda environment definition
├── README.md
```

---

## ⚙️ Features

- ✅ Load Google Sheets from a **specific Drive folder**
- ✅ Process and convert them into pandas DataFrames
- ✅ Tools:
  - `get_insights`: Analyze the data and summarize trends
  - `get_future_recommendations`: Suggest actions based on insights
- ✅ Chat-based interface powered by **Claude AI**
- ✅ Fully functional **MCP Server/Client architecture**

---

## 🏗️ Setup Guide

### 1. 🔐 Google Cloud API Setup

#### ✅ Enable APIs
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Enable:
  - Google Drive API
  - Google Sheets API

#### ✅ Create a Service Account
- Go to `APIs & Services > Credentials > Create Credentials > Service Account`
- Assign roles like `Viewer` or `Drive Reader`
- Click on your service account → "Keys" → Add new key → `JSON`
- Save the file as `credentials/gcp_credentials.json`

#### ✅ Share Folder with Service Account
- Copy the **client_email** from the `gcp_credentials.json`
- Go to Google Drive → open the **target folder** → Share with the client email

### 2. 🤖 Get Claude (Anthropic) API Key

1. Go to [https://console.anthropic.com](https://console.anthropic.com/)
2. Get your API key under “API Keys”
3. Set it as an environment variable:
```bash
export ANTHROPIC_API_KEY="your-api-key"
```

---

## 📦 Create & Activate Conda Environment

```bash
conda env create -f environment.yml
conda activate gsheet-mcp
```

---
 

You can override these using `.env` or `export` in your terminal.

---

## 🚀 How to Run

### 1. Start the MCP Server

```bash
python lib/server/server.py
```

It will:
- Authenticate using your Google credentials
- Load spreadsheets from the target folder
- Start a FastMCP server exposing tools like `get_insights`

### 2. Run the MCP Client

In a new terminal (same environment):

```bash
python lib/client/client.py
```

You can then start chatting with Claude and ask things like:
```
What are the top insights from the inventory sheet?
What future recommendations can you give for budgeting?
Summarize fund trends across all files.
```

---

## 🧪 Example Prompt

> "Give me future recommendations based on trends from all spreadsheets. Be concise and format your answer in bullet points."

---

## ✅ Checklist

- [x] Google Cloud project & credentials
- [x] Folder added to **My Drive**
- [x] Folder shared with service account
- [x] Anthropic key set in env
- [x] Claude model set to `claude-3-haiku-20240307`

---

## 🛠️ TODO / Ideas

- Add authentication via `gcloud auth` (for personal scripts)
- Support other Claude models via config
- Add tool for plotting charts from sheet data
- Use embeddings to auto-suggest questions

---

## 🧑‍💻 Credits

Created by [Harri200191!] to explore Claude-powered spreadsheet analytics with MCP.
