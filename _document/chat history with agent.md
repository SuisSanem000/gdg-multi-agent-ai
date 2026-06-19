# GDG Yerevan Workshop Preparation: Project Scope & History

This document serves as a persistent record of the project state, scope, architectural decisions, and setup updates for the multi-agent workshop. It serves as context for new agent sessions when running the project in the Antigravity IDE.

---

## 📅 Key Dates & Event Context
* **Workshop Date:** June 20, 2026 (10:30 AM - 05:30 PM)
* **Location:** Yandex Hall, Moskovyan 35, Yerevan, Armenia
* **Core Goal:** Build, run, and deploy a multi-agent system on Google Cloud Run, using Vertex AI SDK and SQLite for session memory context engineering.

---

## 🎯 Project Scope & Concept
Initially focused on a corporate compliance auditing template, the project has been refactored into a **Smart Contact Notebook & Relationship Coach (Personal CRM)**. 

This provides a simpler, more intuitive AI playground while utilizing the exact same high-level libraries and deployment structure:
* **Web Server:** Flask with Gunicorn.
* **AI Brain:** `google-cloud-aiplatform` (Gemini 1.5) with function tools.
* **Memory & Database:** SQLite in-memory database with key-value session memories.

---

## 🏛️ Codebase State & Architecture

The project has been expanded into a fully functional web dashboard with the following structure:
1. **Mock Database ([src/database.py](src/database.py)):**
   * Uses `sqlite3` to host an in-memory database.
   * Seeds a `contacts` table with mock professionals ([John Doe](src/database.py#L26) and [Jane Smith](src/database.py#L30)).
   * Manages a `session_memories` table to persist relationship facts (such as user name or preferences) across conversational turns.
2. **Multi-Agent Engine ([src/agent.py](src/agent.py)):**
   * **[ContactAnalystAgent](src/agent.py#L21):** Responsible for looking up detailed contact records using database tools.
   * **[RelationshipCoachAgent](src/agent.py#L114):** Responsible for relationship advice, drafting follow-up emails, and saving context variables. Uses `query_contact_analyst` as an agent-as-a-tool pattern, delegating data lookups to the Analyst.
   * **[SmartNotebookOrchestrator](src/agent.py#L274):** Gateway/router routing direct contact lookups to the Analyst, and conversational or coaching requests to the Coach.
3. **Flask Web Server ([src/app.py](src/app.py)):**
   * Serves static dashboard resources and handles API queries (`POST /query`, `GET /memory`, `POST /clear`).
   * Configured with absolute paths for the `static` folder to prevent path resolution 404 errors.
4. **Developer Dashboard ([src/static/index.html](src/static/index.html) & [src/static/app.js](src/static/app.js)):**
   * Implements a clean, minimal Solarized Light UI.
   * Features a chat playground, live agent thought logs parser, and real-time SQLite database variable inspector.
5. **CLI Runner ([src/main.py](src/main.py)):**
   * Simplifies CLI testing by querying the coach, saving relationship facts to memory, retrieving them, and searching direct contact records.
6. **Unified Roadmap ([README.md](README.md)):**
   * Unified documentation, setup guides, checklists, and run instructions in a single root file.
   * Configured entirely with relative links for clean, portable rendering on other machines.

---

## ⚙️ Global Environment & IDE Setup

### 1. Python Interpreter Alignment
* **Issue:** Prompting user to select a Python interpreter was recurring.
* **Fix:** Configured the default interpreter path globally in the Antigravity IDE User settings ([C:\Users\sanem\AppData\Roaming\Antigravity IDE\User\settings.json](file:///C:/Users/sanem/AppData/Roaming/Antigravity%20IDE/User/settings.json)) using `"python.defaultInterpreterPath": "C:\\Users\\sanem\\AppData\\Local\\Programs\\Python\\Python313\\python.exe"`.
* **Clean Repo:** No interpreter paths or local virtual env variables are stored inside the project workspace settings, ensuring no machine-specific paths are committed or pushed.

### 2. Git Status Cleanup
* **Fix:** `.vscode/` settings directories and local environment secrets `.env` are fully ignored in the repository's [.gitignore](.gitignore).

---

## 🚀 Running & Verification Instructions

### 1. Authenticate with Google Cloud
Ensure your local terminal has active Vertex AI SDK credentials:
```powershell
gcloud auth login
gcloud auth application-default login
```

### 2. Configure Environment Secrets
Ensure `.env` exists in the project root:
```env
GCP_PROJECT_ID=gdg-agent-sayen-2026
GCP_LOCATION=us-central1
```

### 3. Start the Web Dashboard
```powershell
python src/app.py
```
Open your browser and navigate to **[http://127.0.0.1:8080](http://127.0.0.1:8080)** to test the chat and SQLite memory variables.
