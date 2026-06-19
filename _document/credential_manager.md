# Credential Manager & Architecture Documentation

This document provides a detailed technical breakdown of how the **Smart Contact Notebook & Relationship Coach** AI application operates, how GCP authentication is resolved, the specific code files responsible for coordinating the multi-agent system, and the differences between Google AI Studio and Vertex AI.

---

## ⚠️ CRITICAL SECURITY WARNING: Public Repository Commits
> [!WARNING]
> **DO NOT COMMIT OR PUSH your `credentials.json` or `.env` files to a public repository!**
> 
> * **Security Risk:** Public repositories are continuously crawled by malicious bots. If you push `credentials.json` (your Service Account private key), attackers will scrape it within seconds and exploit your Vertex AI access, which can lead to thousands of dollars in usage charges on your billing account.
> * **Existing Guardrails:** This project is already configured with a [.gitignore](file:///d:/projects/gdg-multi-agent-ai/.gitignore) file containing:
>   ```
>   .env
>   credentials.json
>   ```
>   This automatically prevents Git from tracking these files. Keep them strictly local on your machine.

---

## 1. How the AI Application Works (Architecture)

The application uses an **Orchestrator + Micro-Agent** architecture. It integrates a local ChromaDB vector database (in-memory) with Google Vertex AI's Gemini model.

```
                  ┌──────────────────────────────┐
                  │          Browser UI          │
                  └──────────────┬───────────────┘
                                 │ HTTP POST /query
                  ┌──────────────▼───────────────┐
                  │          Flask API           │
                  └──────────────┬───────────────┘
                                 │
                  ┌──────────────▼───────────────┐
                  │  SmartNotebookOrchestrator   │
                  └──────┬────────────────┬──────┘
                         │ (Intent-Based) │
        ┌────────────────┘                └────────────────┐
        │ Profile query                                    │ Networking query
        │                                                  │
┌───────▼────────────────┐                        ┌────────▼───────────────┐
│  ContactAnalystAgent   │                        │ RelationshipCoachAgent │
└───────┬────────────────┘                        └────────┬───────────────┘
        │                                                  │
        │ 🔧 get_contact_details                           │ 🔧 query_contact_analyst
        │ 🔧 search_contacts_semantically                  │ 🔧 store_fact / recall_fact
┌───────▼────────────────┐                        │
│     ChromaDB DB        │◄────────────────────────┘
│ (Contacts & Memories)  │
└────────────────────────┘
```

### The Three Core Orchestration Classes (`src/agent.py`)

1. **`SmartNotebookOrchestrator`:** The central gateway. It inspects the incoming user query and dynamically routes it:
   * Direct profile/contact searches (e.g. queries containing `"contact-"`, `"profile"`, or `"details"`) go to the **`ContactAnalystAgent`**.
   * Strategic networking advice, email drafting, or general requests go to the **`RelationshipCoachAgent`**.
2. **`ContactAnalystAgent` (The Data Lookup Expert):** Integrates the `get_contact_details` and `search_contacts_semantically` tool declarations. When it receives a query, it calls the tool to search the ChromaDB vector database, and returns the formatted profile.
3. **`RelationshipCoachAgent` (The Network Advisor):** Manages interactive networking goals. It has access to three function tools:
   * `query_contact_analyst` (sub-agent tool calling: queries the Analyst for details).
   * `store_fact` (writes facts dynamically discovered during conversation to the ChromaDB `session_memories` collection).
   * `recall_fact` (reads saved variables from the database to inject into system prompts).

---

## 2. How the Authentication Works (GCP & ADC)

The application uses the Google Cloud Vertex AI SDK, which relies on the standard **Application Default Credentials (ADC)** flow to secure API requests.

### The Credentials Resolution Hierarchy
When the Vertex SDK is initialized with `vertexai.init()`, the library searches for credentials in the following order:
1. **`GOOGLE_APPLICATION_CREDENTIALS` Environment Variable:** A system variable pointing to a service account JSON key file.
2. **Local ADC Cache File:** A JSON file generated on your machine by logging in via the Google Cloud CLI. On Windows, it is saved in:
   `C:\Users\sanem\AppData\Roaming\gcloud\application_default_credentials.json`
3. **Google Cloud Runtime Metadata:** Automatically resolved if running directly on GCP infrastructure (such as Cloud Run or Compute Engine).

If none of these are found, Vertex AI raises a `DefaultCredentialsError`.

---

## 3. Step-by-Step GCP Setup: From Scratch
Here is the exact step-by-step path we executed to set up native Vertex AI credentials:

### Step 1: Installed the Google Cloud CLI (gcloud)
We downloaded and silently installed the Google Cloud SDK inside your local AppData directory:
```powershell
# PowerShell script executed in background:
Invoke-WebRequest -Uri "https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe" -OutFile "$env:TEMP\GoogleCloudSDKInstaller.exe"
Start-Process -FilePath "$env:TEMP\GoogleCloudSDKInstaller.exe" -ArgumentList "/S" -Wait
```
This registered `gcloud` executables under `C:\Users\sanem\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin`.

### Step 2: Triggered Browser Authentication
We ran the OAuth user login process:
```powershell
gcloud auth application-default login
```
This opened your web browser to sign in to your Google Account. Once you authorized the access page, it generated the local cache file:
`C:\Users\sanem\AppData\Roaming\gcloud\application_default_credentials.json`

### Step 3: Configured Quota Projects & Project ID
To ensure Vertex AI requests compile billing correctly under your active GCP project, we linked the quota:
```powershell
gcloud auth application-default set-quota-project gdg-agent-sayen-2026
```

### Step 4: Switched to Repository-Isolated Key (Optional/Repo Setup)
To make the project fully self-contained without relying on system-level user configurations, you generated a **Service Account JSON key file** from the GCP console:
1. Navigated to **Service Accounts** under project `gdg-agent-sayen-2026`.
2. Created a service account, assigned it the **Vertex AI User** role, and generated a **JSON Key**.
3. Downloaded the key to the project root folder as **`credentials.json`**.
4. Linked it in the repo-level [.env](file:///d:/projects/gdg-multi-agent-ai/.env) file:
   ```env
   GCP_PROJECT_ID=gdg-agent-sayen-2026
   GCP_LOCATION=us-central1
   GOOGLE_APPLICATION_CREDENTIALS=credentials.json
   ```

---

## 4. Google AI Studio vs. Google Cloud Vertex AI
Here is the detailed difference between the two systems:

| Feature | Google AI Studio (Developer API Key) | Google Cloud Vertex AI (What we did) |
| :--- | :--- | :--- |
| **Authentication** | Simple API Key string (like ChatGPT: `AIzaSy...`) | Enterprise IAM roles, OAuth, Service Accounts, and ADC files |
| **Target Audience** | Solo developers, prototypes, quick integrations | Enterprises, teams, custom model builders, pipeline management |
| **GCP Required?** | **No** (runs inside a separate developer portal) | **Yes** (integrated directly with GCP projects & billing accounts) |
| **Setup Overhead** | 30 seconds (generate key, paste in env) | High (project setup, CLI setup, auth logins, role assignments) |
| **Security & Audits**| Basic API keys (higher risk of exposure) | Granular permissions, VPC service controls, enterprise logs |
| **Data Residency** | Shared global endpoints | Strict data placement controls (pinning datasets to region `us-central1` or EU) |

---

## 5. Related Code Mappings

### A. Initialization & Native Vertex Setup (`src/agent.py`)
```python
# Location: src/agent.py
class SmartNotebookOrchestrator:
    def __init__(self, db_conn):
        self.db = db_conn
        
        # Initialize Vertex AI globally
        project = os.getenv("GCP_PROJECT_ID", "gdg-agent-sayen-2026")
        location = os.getenv("GCP_LOCATION", "us-central1")
        
        vertexai.init(project=project, location=location)
        print("[Orchestrator] Vertex AI SDK initialized successfully.")
```

### B. Environment Loading & Server Initialization (`src/app.py`)
```python
# Location: src/app.py
import os
from flask import Flask
from dotenv import load_dotenv
from database import setup_database
from agent import SmartNotebookOrchestrator

# Load environment variables from the local .env file
load_dotenv()

db_conn = setup_database()
agent = SmartNotebookOrchestrator(db_conn)
```

### C. Workspace Settings & Environment Configuration (`.vscode/settings.json`)
```json
// Location: .vscode/settings.json
{
  "python.terminal.useEnvFile": true,
  "python.defaultInterpreterPath": "C:\\Users\\sanem\\AppData\\Local\\Programs\\Python\\Python313\\python.exe",
  "python.interpreterPath": "C:\\Users\\sanem\\AppData\\Local\\Programs\\Python\\Python313\\python.exe"
}
```
