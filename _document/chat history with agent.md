# GDG Yerevan Workshop Preparation: Project Scope & History

This document serves as a persistent record of the project state, scope, architectural decisions, and key dates discussed during the preparation for the workshop.

---

## 📅 Key Dates & Event Context
* **Workshop Date:** June 20, 2026 (10:30 AM - 05:30 PM)
* **Location:** Yandex Hall, Yerevan, Armenia
* **Preparation Period:** June 16, 2026 - June 18, 2026
* **Core Goal:** Build and deploy a multi-agent system using Google Cloud and Vertex AI.

---

## 🎯 User Profile & Project Scope
* **User Profile**: Experienced web backend developer. Proficient with Python syntax, but new to Python-specific web frameworks (e.g. Flask/FastAPI) and Python agent frameworks.
* **Scope**: Transition the starter project from the default TypeScript/Node.js template into an easy-to-read, standard Python project. Focus on clear, raw Python syntax, keeping external frameworks and libraries minimal to ensure readability, while maintaining a robust design pattern for local database function calling.

---

## 🏛️ Codebase State & Architecture

We set up a structured Python application in `src/` featuring:
1. **Mock Database (`src/database.py`)**: Utilizes standard library `sqlite3` to set up an in-memory database seeded with Corporations Act statutes (`corp-181`, `corp-182`).
2. **Legal Agent (`src/agent.py`)**: 
   - Uses the official Google Cloud Vertex AI Python SDK (`google-cloud-aiplatform`).
   - Declares the `get_statute_definition` function as a callable tool.
   - Initialises `gemini-1.5-flash` with the tool configuration.
   - Employs a stateful `chat` object (`model.start_chat()`) to manage turn history.
   - Robustly parses tool requests by checking both `candidate.function_calls` and `candidate.content.parts[0].function_call` lists (avoiding version mismatch bugs).
   - Executes local database searches and feeds results back to Gemini using `Part.from_function_response(...)`.
3. **CLI Runner (`src/main.py`)**: Exposes a command-line interface to execute sample database queries and generic queries against the agent.
4. **Flask Web Server (`src/app.py`)**: Exposes the agent via POST `/query` to make it accessible to external services and HTTP request containers.
5. **Dockerfile**: Containers the application using `python:3.11-slim` and `gunicorn` for deployment to **Google Cloud Run**.

---

## ⚙️ Environment & Tooling Decisions

### 1. Unified Documentation
- Merged the workshop agenda, schedules, and TypeScript guidelines into a single, cohesive Python-focused [README.md](file:///d:/projects/gdg-multi-agent-ai/README.md).
- Deleted the temporary `input information.md` file to prevent clutter.

### 2. Environment Selection (Global Python vs. Virtual Env)
- **Decision**: The user explicitly preferred using their local global Python interpreter rather than a virtual environment (`.venv`).
- **Actions taken**:
  - Deleted the `.venv` directory.
  - Installed all project dependencies globally using the local Python 3.11 pip runner:
    `C:\Users\sanem\AppData\Local\Programs\Python\Python311\python.exe -m pip install -r requirements.txt`
  - Created [.vscode/settings.json](file:///d:/projects/gdg-multi-agent-ai/.vscode/settings.json) to explicitly tell the workspace IDE to default to:
    `C:\Users\sanem\AppData\Local\Programs\Python\Python311\python.exe`
    This resolved the local path select/browse error.

### 3. Git Status Cleanup
- **Action**: Created [.gitignore](file:///d:/projects/gdg-multi-agent-ai/.gitignore) targeting typical Python temporary directories (`__pycache__/`), local settings (`.vscode/`), local environment keys (`.env`), and typical virtual environments (`.venv`, `venv/`).

---

## 🚀 Running & Verification Instructions

### 1. Authenticate with Google Cloud
Ensure your local command line is authenticated:
```powershell
gcloud auth login
gcloud auth application-default login
```

### 2. Configure Environment Secrets
Ensure [.env](file:///d:/projects/gdg-multi-agent-ai/.env) exists in the project root with your valid project details:
```env
GCP_PROJECT_ID=your-actual-gcp-project-id
GCP_LOCATION=us-central1
```

### 3. Test Local Executables
* **CLI Demo**: `python src/main.py`
* **API Listener**: `python src/app.py` (accessible at `http://localhost:8080/query`)
