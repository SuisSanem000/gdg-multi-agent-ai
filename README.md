# GDG Yerevan AI Multi-Agent & Session Memory Playground

This repository is a fully functional web application built as a **Multi-Agent & Session Memory Playground** for the GDG Yerevan AI Workshop (June 20, 2026). It serves as a unified roadmap, hands-on learning environment, and readiness guide.

Since you are a web developer who knows Python syntax, you can think of this project as a standard backend API paired with a frontend dashboard, but with an AI "brain" inserted in the middle.

---

## 📌 Table of Contents
1. [✅ Local Machine Preparation Status](#-local-machine-preparation-status)
2. [📅 Workshop Details](#-workshop-details)
3. [🔍 Detailed Breakdown of Technologies & Libraries](#-detailed-breakdown-of-technologies--libraries)
   - [The Web Server & Routing](#1-the-web-server--routing-flask--gunicorn)
   - [The AI "Brain"](#2-the-ai-brain-google-cloud-vertex-ai)
   - [The Database & Memory](#3-the-database--memory-sqlite)
   - [Deployment & Infrastructure](#4-deployment--infrastructure-docker--dotenv)
4. [📂 Codebase Directory & Folder Structure](#-codebase-directory--folder-structure)
5. [🏛️ Core Architecture & Concept Walkthrough](#-core-architecture--concept-walkthrough)
   - [Database & Memory Management](#-database--memory-management)
   - [Multi-Agent Collaboration Pattern](#-multi-agent-collaboration-pattern)
   - [Orchestrator Routing](#-orchestrator-routing)
   - [Web Dashboard Features](#-web-dashboard-features)
6. [🛠️ Step-by-Step Setup Guide](#-step-by-step-setup-guide)
   - [Step 1: Align Your Python Interpreter (VS Code)](#step-1-align-your-python-interpreter-vs-code)
   - [Step 2: Authenticate Local Google Cloud SDK](#step-2-authenticate-local-google-cloud-sdk)
   - [Step 3: Configure Environment Variables](#step-3-configure-environment-variables)
7. [⚡ How to Run the Playground Locally](#-how-to-run-the-playground-locally)
   - [Running the CLI Demo](#1-running-the-cli-demo)
   - [Running the Web Dashboard](#2-running-the-web-dashboard)
8. [☁️ Containerization & Cloud Run Deployment](#-containerization--cloud-run-deployment)
9. [💡 Workshop Pro Tips](#-workshop-pro-tips)

---

## ✅ Local Machine Preparation Status

Your local machine is fully configured and verified for the workshop:
* **[x] Python Environment:** Aligned your VS Code interpreter to Python 3.11.
* **[x] Package Dependencies:** Installed [requirements.txt](file:///d:/projects/gdg-multi-agent-ai/requirements.txt) (`google-cloud-aiplatform`, `flask`, `python-dotenv`, and `gunicorn`).
* **[x] Google Cloud CLI:** Installed the `gcloud` tool suite.
* **[x] GCP Authentication:** Logged into your Google account and generated local Application Default Credentials (ADC).
* **[x] Quota Project & APIs:** Linked your quota project to `gdg-agent-sayen-2026` and successfully enabled the Google Cloud Vertex AI API (`aiplatform.googleapis.com`).
* **[x] Playground Codebase:** Refactored the database schema with statutes and key-value session memories, created a collaborative multi-agent chain, and set up a local CLI runner and premium developer dashboard.

---

## 📅 Workshop Details
* **Date & Time:** June 20, 2026 | 10:30 AM - 05:30 PM
* **Location:** Yandex Hall (Moskovyan 35, Yerevan)
* **Registration:** [Forms Link](https://forms.gle/owUAq9eEU48LASmk6)
* **Goal:** Learn, run, and deploy a multi-agent system on Google Cloud, and extend it with custom agent roles.

---

## 🔍 Detailed Breakdown of Technologies & Libraries

### 1. The Web Server & Routing (Flask & Gunicorn)
* **Flask:** This is a lightweight Python web framework. The app uses Flask (in [app.py](file:///d:/projects/gdg-multi-agent-ai/src/app.py)) to create REST API endpoints (like `POST /query` to chat, and `GET /memory` to check the database). It also serves the frontend HTML, CSS, and JS files.
* **Gunicorn:** This is a production-grade web server for Python. While Flask has a built-in server for testing, Gunicorn is used in the [Dockerfile](file:///d:/projects/gdg-multi-agent-ai/Dockerfile) to run the app robustly when deployed to the cloud.
* **The Frontend:** The user interface is built without heavy frameworks—just vanilla JavaScript ([app.js](file:///d:/projects/gdg-multi-agent-ai/src/static/app.js)), HTML ([index.html](file:///d:/projects/gdg-multi-agent-ai/src/static/index.html)), and CSS ([style.css](file:///d:/projects/gdg-multi-agent-ai/src/static/style.css)) to create a responsive chat box, a real-time "thought stream" showing what the AI is doing, and a database inspector.

### 2. The AI "Brain" (Google Cloud Vertex AI)
* **`google-cloud-aiplatform`:** This is Google's official Python library for interacting with their AI models, like `gemini-1.5-flash`.
* **Function Calling (Tools):** The app uses this library to give the AI superpowers. Using `FunctionDeclaration`, the code describes normal Python functions (like searching a database) to the AI. The AI can then intelligently decide to "call" these tools when a user asks a specific question.
* **Multi-Agent Collaboration:** Instead of one massive AI doing everything, the app routes tasks between multiple specialized agents (defined in [agent.py](file:///d:/projects/gdg-multi-agent-ai/src/agent.py)). For example, the `ComplianceAuditorAgent` talks to the user but does not have database access. Instead, it delegates legal lookups to a secondary `LegalAnalystAgent`.

### 3. The Database & Memory (SQLite)
* **`sqlite3`:** This is a database engine built directly into Python's standard library, requiring no extra installation. The project uses it (in [database.py](file:///d:/projects/gdg-multi-agent-ai/src/database.py)) to run a fast, in-memory mock database.
* **Context Engineering:** Sending an entire long chat history back and forth to an AI model uses a lot of tokens and costs more money. To optimize this, the app uses SQLite to store specific facts the user mentions (e.g., saving `director_name: Alice` as a key-value pair). Before sending a new user message to the AI, the backend pulls these facts from SQLite and invisibly injects them into the AI's "System Instructions," giving the AI a persistent memory without the huge token cost.

### 4. Deployment & Infrastructure (Docker & Dotenv)
* **Docker (`Dockerfile`):** The project is containerized using a lightweight Python image (`python:3.11-slim`). This bundles the Python code, the installed libraries, and the server together so it can be deployed seamlessly to **Google Cloud Run** (a serverless hosting environment).
* **`python-dotenv`:** A simple utility library used to load secret environment variables (like your Google Cloud Project ID) from a local `.env` file into the application.

---

## 📂 Codebase Directory & Folder Structure

The project has been expanded into a complete web app with a visual, responsive dashboard:
```text
gdg-multi-agent-ai/
├── README.md               # Unified roadmap, explanations & setup guide (this file)
├── requirements.txt        # Package dependencies (Vertex AI, Flask, dotenv, Gunicorn)
├── .env.example            # Environment variables template
├── .env                    # Local environment config (GCP credentials)
├── Dockerfile              # Docker container configuration for Cloud Run
└── src/
    ├── __init__.py
    ├── database.py         # SQLite setup: Statutes + Session Memory
    ├── agent.py            # Multi-agent system: Analyst, Auditor, and Orchestrator
    ├── main.py             # CLI runner script with trace outputs
    ├── app.py              # Flask app serving static frontend and API endpoints
    └── static/
        ├── index.html      # Premium developer dashboard HTML
        ├── style.css       # Custom glassmorphism dark-mode stylesheet
        └── app.js          # Interactive UI driver (fetch APIs and logs parser)
```

---

## 🏛️ Core Architecture & Concept Walkthrough

The project demonstrates all three key themes of the workshop: Cloud Run deployment, multi-agent orchestration, and context/session memory engineering.

### 🗄️ Database & Memory Management
* **Statutes Table:** Persists the Corporations Act rules (specifically Sections 181 and 182).
* **Session Memories Table:** A key-value table `(session_id, key, value)`. This stores persistent facts (e.g. director names, transactions, audit histories) across conversation turns.
* **Context Injection:** When the auditor agent runs, it retrieves all key-value memories for the current `session_id` using [get_session_memories](file:///d:/projects/gdg-multi-agent-ai/src/database.py#L56) and injects them directly into the system instructions. This demonstrates **Context Engineering** (Vadim Patsev's session), providing the AI with memory context without passing raw conversation transcripts.

### 🤖 Multi-Agent Collaboration Pattern
We moved from a single agent to a collaborative multi-agent loop inside [src/agent.py](file:///d:/projects/gdg-multi-agent-ai/src/agent.py):
1. **[LegalAnalystAgent](file:///d:/projects/gdg-multi-agent-ai/src/agent.py#L21):** Accesses the SQLite database using the `get_statute_definition` function tool to retrieve legal clauses.
2. **[ComplianceAuditorAgent](file:///d:/projects/gdg-multi-agent-ai/src/agent.py#L114):** Audits business scenarios. Rather than accessing the database directly, it has a tool-as-an-agent called `query_legal_analyst`. When it decides it needs legal sections, it calls this tool, which runs `LegalAnalystAgent`. It also reads/writes facts using the `recall_fact` and `store_fact` memory tools.

### 🔀 Orchestrator Routing
The **[LegalAgent](file:///d:/projects/gdg-multi-agent-ai/src/agent.py#L274)** acts as the gateway/orchestrator:
* It inspects the input query:
  * Direct statutory queries (e.g., containing "Section", "Statute", or "corp-") are routed directly to the **[LegalAnalystAgent](file:///d:/projects/gdg-multi-agent-ai/src/agent.py#L21)**.
  * Conversational queries, conflict statements, or business scenario audits are routed to the **[ComplianceAuditorAgent](file:///d:/projects/gdg-multi-agent-ai/src/agent.py#L114)**.

### 🖥️ Web Dashboard Features
We built a single-page developer dashboard served directly by the Flask server:
* **Interactive Chat Interface:** Submit scenario audits to the Compliance Auditor.
* **Live Agent Thought Stream:** Displays step-by-step traces of agent interactions, showing exactly when the Auditor calls the Legal Analyst, when SQLite tools execute, and the returned data.
* **SQLite Session Memory Inspector:** Shows a real-time list of key-value pairs stored in the SQLite database for the active session.
* **Cloud Architecture & Prep Guide:** Visual diagram and checklist for the workshop.

---

## 🛠️ Step-by-Step Setup Guide

### Step 1: Align Your Python Interpreter (VS Code)
To ensure VS Code correctly recognizes the libraries installed during setup and prevents import errors:
1. **Select VS Code Interpreter:**
   * Open the **Command Palette** by pressing `Ctrl + Shift + P` (or `Cmd + Shift + P` on macOS).
   * Type **`Python: Select Interpreter`** and select it.
   * Choose the path pointing to the Python 3.11 executable (configured under `C:\Users\sanem\AppData\Local\Programs\Python\Python311\python.exe`).
2. The workspace [.vscode/settings.json](file:///d:/projects/gdg-multi-agent-ai/.vscode/settings.json) has been configured to target this path by default.

### Step 2: Authenticate Local Google Cloud SDK
Ensure your local environment has active Vertex AI credentials. Open your terminal (PowerShell / Command Prompt) and run:
```powershell
gcloud auth login
gcloud auth application-default login
```
*This shares your user credentials with the local Vertex AI client.*

### Step 3: Configure Environment Variables
Open the [.env](file:///d:/projects/gdg-multi-agent-ai/.env) file (copied from [.env.example](file:///d:/projects/gdg-multi-agent-ai/.env.example)) and update it with your Google Cloud Project ID and Region:
```env
GCP_PROJECT_ID=gdg-agent-sayen-2026
GCP_LOCATION=us-central1
```

---

## ⚡ How to Run the Playground Locally

### 1. Running the CLI Demo
Execute the CLI testing run which simulates an audit, stores facts in SQLite, and retrieves them in a subsequent query:
```powershell
python src/main.py
```
*This runner ([main.py](file:///d:/projects/gdg-multi-agent-ai/src/main.py)) will demonstrate a compliance audit scenario, save audited variables into SQLite memory, recall those variables, and perform a direct statutory lookup using orchestrator routing.*

### 2. Running the Web Dashboard
Start the local Flask development web server:
```powershell
python src/app.py
```
Open your browser and navigate to:
👉 **[http://127.0.0.1:8080](http://127.0.0.1:8080)**

This interface lets you interact with the agent, inspect live JSON thought traces of tool executions, and inspect session key-value tables in real time.

---

## ☁️ Containerization & Cloud Run Deployment

To deploy your agent to Google Cloud Run, run the single command below from the project root:
```powershell
gcloud run deploy legal-analyst-agent `
  --source . `
  --region us-central1 `
  --allow-unauthenticated
```

### Behind the Scenes:
* **[Dockerfile](file:///d:/projects/gdg-multi-agent-ai/Dockerfile):** Builds on `python:3.11-slim`, copies the code, installs libraries, exposes port `8080`, and fires up the production WSGI server:
  `gunicorn --bind 0.0.0.0:8080 src.app:app`
* **Application Default Credentials (ADC):** When deployed to Cloud Run, Vertex AI requests authenticate automatically using the Cloud Run Service Account.

---

## 💡 Workshop Pro Tips

1. **Model Choices:** Use `gemini-1.5-flash` for fast, low-cost orchestrations, routing decisions, and tool calls. Keep `gemini-1.5-pro` for synthesizing huge reports or multi-document comparison.
2. **Context vs Storage:** Gemini 1.5 has a 1M+ token context window. Pay attention to the comparison between holding entire user sessions in the context window (convenient but higher latency/token costs) vs using lightweight SQLite caches to inject only summarized context facts (cost-effective, low latency).
3. **Structured Schemas:** When agents send data to each other, use structured schemas (like JSON properties in tool calls) to prevent formatting inconsistencies.
