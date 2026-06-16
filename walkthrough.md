# Walkthrough: GDG Yerevan AI Workshop Preparation

Here is a detailed walkthrough of what has been set up to get you ready for the **GDG Yerevan AI Multi-Agent Workshop** on June 20, 2026.

---

## 🛠 What Was Accomplished

### 1. Unified Workshop Documentation & Guide
All details from the various files are now compiled into one primary [README.md](file:///d:/projects/gdg-multi-agent-ai/README.md) at the root of the workspace. It details the schedule, speakers, and step-by-step setup guides for both local execution and Cloud Run deployment.

### 2. Project Directory Structure
We initialized a standard Python project structure tailored for a web backend engineering background:
```text
gdg-multi-agent-ai/
├── README.md               # Unified guide (Python-focused)
├── .gitignore              # Standard git exclusion file (caches, .vscode, .env ignored)
├── requirements.txt        # Package dependencies (Vertex AI, dotenv, Flask, Gunicorn)
├── .env.example            # Environment variables template
├── .env                    # Local environment config (GCP Project details)
├── Dockerfile              # Docker config for Cloud Run
└── src/
    ├── __init__.py         # Package initialization
    ├── database.py         # In-memory SQLite database setup & seeding
    ├── agent.py            # LegalAgent class containing Vertex AI SDK tool definitions
    ├── main.py             # CLI runner script
    └── app.py              # Lightweight Flask API endpoint
```

---

## 3. Core Component Walkthrough

### 🗄️ Database ([src/database.py](file:///d:/projects/gdg-multi-agent-ai/src/database.py))
This module uses Python’s built-in `sqlite3` library. It initializes an in-memory database and seeds a `statutes` table with simulated regulatory clauses from the Australian Corporations Act:
- **`corp-181`**: Corporations Act Section 181 (Good Faith)
- **`corp-182`**: Corporations Act Section 182 (Use of Position)

### 🤖 Agent Layer ([src/agent.py](file:///d:/projects/gdg-multi-agent-ai/src/agent.py))
This houses the `LegalAgent` class. It manages the agent's logic:
1. **Tool Definition**: We declare `get_statute_definition` as a function tool using `vertexai.generative_models.FunctionDeclaration`.
2. **Model Instantiation**: We initialize `gemini-1.5-flash` and pass it our tool.
3. **Execution Loop**:
   - The user query is sent to Gemini using the stateful `chat.send_message(user_input)` loop.
   - If Gemini determines it needs the statute definition, it responds with a tool call request (`function_calls[0]`).
   - The agent catches this request, runs the local SQLite database query in Python, and sends the database output back to the model using `Part.from_function_response(...)`.
   - Gemini receives the database facts and outputs the final natural language answer.

### 🖥️ CLI Entrypoint ([src/main.py](file:///d:/projects/gdg-multi-agent-ai/src/main.py))
A simple script that sets up the database, initializes the agent, and runs two queries:
1. One that **requires the database tool** ("What does Corporations Act Section 181 state about good faith?").
2. One that **relies on general knowledge** ("Explain conflict of interest in general terms").

### 🌐 Web Endpoint ([src/app.py](file:///d:/projects/gdg-multi-agent-ai/src/app.py))
To deploy to Google Cloud Run, we wrapped the agent in a minimal **Flask** web application:
- Exposes a GET route `/` to verify status.
- Exposes a POST route `/query` which accepts `{"query": "..."}` and returns the agent's final reasoning.
- Uses the `PORT` environment variable required by Cloud Run.

---

## 4. Git & IDE Workspace Setup
- **IDE Interpreter**: Created [.vscode/settings.json](file:///d:/projects/gdg-multi-agent-ai/.vscode/settings.json) pointing to your local global Python executable so your editor recognizes the libraries automatically.
- **Git Hygiene**: Created [.gitignore](file:///d:/projects/gdg-multi-agent-ai/.gitignore) ignoring the `.vscode/` configuration folder, local `.env` values, virtual environment structures, and `__pycache__` artifacts so your git status remains completely clean.

---

## ⚡ How to Run the Demo Locally

1. **Authenticate CLI with Google Cloud**:
   ```powershell
   gcloud auth application-default login
   ```
2. **Configure your GCP project** in your newly created local [.env](file:///d:/projects/gdg-multi-agent-ai/.env) file:
   ```env
   GCP_PROJECT_ID=your-actual-gcp-project-id
   GCP_LOCATION=us-central1
   ```
3. **Run the CLI demo**:
   ```powershell
   python src/main.py
   ```
4. **Run the API server**:
   ```powershell
   python src/app.py
   ```
