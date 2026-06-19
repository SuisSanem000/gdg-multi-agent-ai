================================================
FILE: README.md
================================================
# GDG Yerevan AI Multi-Agent Workshop (June 20, 2026)
## Pre-Workshop Preparation & Readiness Hub (Python Edition)

---

## ✅ Local Machine Preparation Status (Completed)

Your local machine is fully configured and verified for the workshop:
*   **[x] Python Environment:** Aligned your VS Code interpreter to Python 3.13.13.
*   **[x] Package Dependencies:** Installed `google-cloud-aiplatform`, `flask`, `python-dotenv`, and `gunicorn`.
*   **[x] Google Cloud CLI:** Installed the `gcloud` tool suite under your local AppData folder.
*   **[x] GCP Authentication:** Logged into your Google account and generated local Application Default Credentials (ADC).
*   **[x] Quota Project & APIs:** Linked your quota project to `gdg-agent-sayen-2026` and successfully enabled the Google Cloud Vertex AI API (`aiplatform.googleapis.com`).
*   **[x] Playground Codebase:** Refactored the database schema with statutes and key-value session memories, created a collaborative multi-agent chain, and set up a local CLI runner and premium developer dashboard.

---

This project is configured as a fully functional **Multi-Agent & Session Memory Playground** with a premium web dashboard. It is designed to get you up to speed on the core concepts of the workshop:
1. **Cloud & Infrastructure (Rohan Singh)** — Cloud Run deployments and Vertex AI integration.
2. **Agentic Layer & Orchestration (Armen Vardanyan)** — Tool calling, function declarations, and collaborative agent chains.
3. **Agent Memory & Context Engineering (Vadim Patsev)** — SQLite session variables and context-injected session memories.

---

## 📅 Workshop Details
* **Date & Time:** June 20, 2026 | 10:30 AM - 05:30 PM
* **Location:** Yandex Hall (Moskovyan 35, Yerevan)
* **Registration:** [Forms Link](https://forms.gle/owUAq9eEU48LASmk6)
* **Goal:** Learn, run, and deploy a multi-agent system on Google Cloud, and extend it with custom agent roles.

---

## 🛠️ Step 1: Align Your Python Interpreter (VS Code)

To ensure VS Code correctly recognizes the libraries installed during setup (preventing import errors or yellow underlines):

1. **Verify Python Installation:** Python 3.13 (or 3.11) is already installed.
2. **Select VS Code Interpreter:**
   - In VS Code, open the **Command Palette** by pressing `Ctrl + Shift + P` (or `Cmd + Shift + P` on macOS).
   - Type **`Python: Select Interpreter`** and select it.
   - Choose the path pointing to **`C:\Users\Sayen\AppData\Local\Microsoft\WindowsApps\python.exe`** (or enter the exact path where you execute python).
3. We have updated your workspace [.vscode/settings.json](file:///h:/Programming/dev/gdg-multi-agent-ai/.vscode/settings.json) to target this python path by default.

---

## 💻 Step 2: Playground Directory Structure

The project has been expanded into a complete web app with a visual, responsive dashboard:
```text
gdg-multi-agent-ai/
├── README.md               # This unified learning guide
├── requirements.txt        # Package dependencies (Vertex AI, Flask, Gunicorn)
├── .env.example            # Environment variables template
├── .env                    # Local environment config (GCP credentials)
├── Dockerfile              # Container configuration for Cloud Run
├── walkthrough.md          # Step-by-step code architecture walkthrough
└── src/
    ├── __init__.py
    ├── database.py         # SQLite setup: Statutes + Persistent Session Memory
    ├── agent.py            # Multi-agent system (LegalAnalyst, ComplianceAuditor, Orchestrator)
    ├── main.py             # CLI runner script verifying traces and SQLite storage
    ├── app.py              # Flask server hosting REST APIs and serving UI
    └── static/
        ├── index.html      # Premium Developer Dashboard UI HTML
        ├── style.css       # Sleek dark-mode glassmorphic styling
        └── app.js          # JavaScript controller for API fetches and trace rendering
```

---

## 🤖 Step 3: Understanding the Basics (Pre-Workshop Study)

Before you attend the event, read through these three components in the code to understand the concepts:

### A. Agentic Layer & Orchestration (Armen's Session)
Look at [src/agent.py](file:///h:/Programming/dev/gdg-multi-agent-ai/src/agent.py):
- **Function Declarations:** We define the schema of what tools are available (e.g. `get_statute_definition`, `query_legal_analyst`, `store_fact`, `recall_fact`) using `FunctionDeclaration`.
- **Tool Packaging:** We bind these declarations into `Tool` objects and pass them to the `GenerativeModel`.
- **Multi-Agent Collaboration:** We showcase a **Tool-as-an-Agent** pattern. The `ComplianceAuditorAgent` is responsible for transaction audits. It does *not* have direct database access. Instead, it has a tool called `query_legal_analyst` which delegates legal searches by calling the `LegalAnalystAgent.run()` method.
- **Routing:** The `LegalAgent` class acts as the main gateway (Orchestrator). It inspects the input query: if it's a direct law lookup, it routes to the `LegalAnalystAgent`; if it's a scenario audit, it routes to the `ComplianceAuditorAgent`.

### B. Agent Memory & Context Engineering (Vadim's Session)
Look at [src/database.py](file:///h:/Programming/dev/gdg-multi-agent-ai/src/database.py) and [src/agent.py](file:///h:/Programming/dev/gdg-multi-agent-ai/src/agent.py):
- **SQLite Database Memory:** We use a local SQLite table (`session_memories`) to store key variables across different conversation turns (e.g. key: `director_name`, value: `Alice`).
- **Context Injection:** On every query turn, the Compliance Auditor calls `get_session_memories` to pull all variables stored for that session ID. It inserts them dynamically into its **System Instruction** before sending the chat turn to Gemini. This allows the model to recall names, dates, or assets even in a fresh chat session without bloating the context window with raw transcripts.
- **Memory Tools:** The agent uses tools `store_fact(key, value)` and `recall_fact(key)` to decide when it should read or write variables.

### C. Cloud Run & Infrastructure (Rohan's Session)
Look at [src/app.py](file:///h:/Programming/dev/gdg-multi-agent-ai/src/app.py) and [Dockerfile](file:///h:/Programming/dev/gdg-multi-agent-ai/Dockerfile):
- **Flask Web Server:** To run a containerized agent on Google Cloud Run, we wrap it in a REST API. It listens on the `PORT` environment variable (default: `8080`).
- **Dockerfile:** Packages our python environment, installs dependencies, copies the source code, and runs a production WSGI server (`gunicorn --bind 0.0.0.0:8080 src.app:app`).
- **Application Default Credentials (ADC):** When deploying to Cloud Run, Vertex AI requests will authenticate automatically using the Cloud Run Service Account. Locally, we authenticate using `gcloud auth application-default login` which saves credentials locally for the Vertex AI SDK to fetch.

---

## ⚡ Step 4: Running the Code Locally

### 1. Authenticate Local SDK
Open your terminal (PowerShell / Command Prompt) and run:
```powershell
gcloud auth login
gcloud auth application-default login
```
*This shares your user credentials with the local Vertex AI client.*

### 2. Configure project env
Open [.env](file:///h:/Programming/dev/gdg-multi-agent-ai/.env) and update it with your GCP Project ID:
```env
GCP_PROJECT_ID=gdg-agent-sayen-2026
GCP_LOCATION=us-central1
```

### 3. Run the CLI Test
Verify the multi-agent orchestration and persistent SQLite memory work in the console:
```powershell
python src/main.py
```
*You will see trace logs showing `ComplianceAuditorAgent` calling `query_legal_analyst` which triggers `LegalAnalystAgent`, retrieves Section 181 from SQLite, and finally prints the audit report. It will then fetch the saved director's name in a subsequent query.*

### 4. Open the Web Dashboard
Run the Flask server locally:
```powershell
python src/app.py
```
Open your browser and navigate to:
👉 **[http://127.0.0.1:8080](http://127.0.0.1:8080)**

You will see:
- A responsive, animated **Chat Box** to test scenarios.
- **Live Thought Stream** showcasing real-time tool calls and agent routing.
- **SQLite Session Memory Inspector** listing all key-value entries stored in the database.
- Visual diagram of the architecture map.

---

## ☁️ Step 5: Containerization & Cloud Run Deployment

Once you are ready to deploy your agent to Google Cloud Run, run the single command below from the project root:

```powershell
gcloud run deploy legal-analyst-agent `
  --source . `
  --region us-central1 `
  --allow-unauthenticated
```
This command will package the project using the [Dockerfile](file:///h:/Programming/dev/gdg-multi-agent-ai/Dockerfile), upload it to Artifact Registry, build it, and deploy it to a serverless endpoint on Cloud Run.

---

## 💡 Workshop Pro Tips
1. **Model Choices:** Use `gemini-1.5-flash` for fast, low-cost orchestrations, routing decisions, and tool calls. Keep `gemini-1.5-pro` for synthesizing huge reports or multi-document comparison.
2. **Context vs Storage:** Gemini 1.5 has a 1M+ token context window. In Vadim's session, pay attention to the comparison between holding entire user sessions in the context window (convenient but higher latency/token costs) vs using lightweight SQLite caches to inject only summarized context facts (cost-effective, low latency).
3. **Structured Schemas:** When agents send data to each other, use structured schemas (like JSON properties in tool calls) to prevent formatting inconsistencies.



================================================
FILE: Dockerfile
================================================
FROM python:3.11-slim

WORKDIR /app

# Prevent Python from writing .pyc files to disc
ENV PYTHONDONTWRITEBYTECODE=1
# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source files
COPY src/ src/

# Expose default port
EXPOSE 8080

# Run Flask using production WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "src.app:app"]



================================================
FILE: requirements.txt
================================================
google-cloud-aiplatform
python-dotenv
flask
gunicorn



================================================
FILE: .env.example
================================================
GCP_PROJECT_ID=your-gcp-project-id
GCP_LOCATION=us-central1



================================================
FILE: _document/chat history with agent.md
================================================
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



================================================
FILE: _document/walkthrough.md
================================================
[Binary file]


================================================
FILE: src/__init__.py
================================================
# Legal Analyst Micro-Agent package.



================================================
FILE: src/agent.py
================================================
import os
import vertexai
from vertexai.generative_models import GenerativeModel, Tool, FunctionDeclaration, Part

def _extract_function_call(response):
    """Safely extracts function call from Vertex AI response candidates."""
    try:
        candidates = response.candidates
        if candidates and len(candidates) > 0:
            candidate = candidates[0]
            if hasattr(candidate, 'function_calls') and candidate.function_calls:
                return candidate.function_calls[0]
            elif hasattr(candidate, 'content') and candidate.content.parts:
                part = candidate.content.parts[0]
                if hasattr(part, 'function_call') and part.function_call:
                    return part.function_call
    except Exception as e:
        print(f"DEBUG: Error parsing function calls: {e}")
    return None

class LegalAnalystAgent:
    def __init__(self, db_conn):
        self.db = db_conn
        
        # Define the Function Tool declaration
        self.get_statute_declaration = FunctionDeclaration(
            name="get_statute_definition",
            description="Retrieves the official text/clause of a specific Corporations Act section using its statute ID.",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "statute_id": {
                        "type": "STRING",
                        "description": 'The unique ID of the statute, e.g., "corp-181" or "corp-182".',
                    }
                },
                "required": ["statute_id"],
            }
        )
        self.db_tool = Tool(function_declarations=[self.get_statute_declaration])
        
        self.model = GenerativeModel(
            model_name="gemini-1.5-flash",
            tools=[self.db_tool],
            system_instruction=(
                "You are a Legal Analyst Agent specializing in Australian Corporations Law. "
                "Your job is to answer statutory questions using the 'get_statute_definition' tool. "
                "Always use this tool to retrieve exact text. Be precise and cite the sections."
            )
        )

    def _execute_db_query(self, statute_id: str) -> str:
        """Executes a local SQL search based on tool parameters requested by Gemini."""
        cursor = self.db.cursor()
        cursor.execute("SELECT clause FROM statutes WHERE id = ?", (statute_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        return f"Statute '{statute_id}' not found in database."

    def run(self, user_input: str, trace: list = None) -> str:
        if trace is None:
            trace = []
            
        trace.append({
            "agent": "LegalAnalystAgent",
            "action": "received_query",
            "message": f"Processing legal query: '{user_input}'"
        })
        
        chat = self.model.start_chat()
        response = chat.send_message(user_input)
        
        while True:
            function_call = _extract_function_call(response)
            if not function_call:
                break
                
            if function_call.name == "get_statute_definition":
                statute_id = function_call.args.get("statute_id")
                trace.append({
                    "agent": "LegalAnalystAgent",
                    "action": "call_tool",
                    "tool": "get_statute_definition",
                    "args": {"statute_id": statute_id}
                })
                
                tool_output = self._execute_db_query(statute_id)
                trace.append({
                    "agent": "LegalAnalystAgent",
                    "action": "tool_output",
                    "tool": "get_statute_definition",
                    "output": tool_output
                })
                
                response = chat.send_message(
                    Part.from_function_response(
                        name=function_call.name,
                        response={"result": tool_output}
                    )
                )
            else:
                break
                
        final_text = response.text
        trace.append({
            "agent": "LegalAnalystAgent",
            "action": "final_response",
            "message": final_text
        })
        return final_text


class ComplianceAuditorAgent:
    def __init__(self, db_conn, analyst_agent):
        self.db = db_conn
        self.analyst = analyst_agent
        
        # Tools definitions
        self.query_analyst_declaration = FunctionDeclaration(
            name="query_legal_analyst",
            description="Queries the Legal Analyst agent to retrieve official statute details or ask specific legal compliance questions about Australian Corporations law.",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "query": {
                        "type": "STRING",
                        "description": "The specific query to send to the Legal Analyst, e.g. 'What does Section 181 say?' or 'Search for regulations on conflict of interest'.",
                    }
                },
                "required": ["query"],
            }
        )
        
        self.recall_fact_declaration = FunctionDeclaration(
            name="recall_fact",
            description="Retrieves a previously saved fact or context information by its key (e.g., 'director_name', 'company_name', 'transaction_value'). Useful for remembering details from earlier in the session.",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "key": {
                        "type": "STRING",
                        "description": "The key identifier of the fact to recall.",
                    }
                },
                "required": ["key"],
            }
        )
        
        self.store_fact_declaration = FunctionDeclaration(
            name="store_fact",
            description="Saves an important fact or context variable into the session memory to refer to later (e.g. key='director_name', value='David'). Always store key facts you discover during conversation.",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "key": {
                        "type": "STRING",
                        "description": "The key identifier for the fact.",
                    },
                    "value": {
                        "type": "STRING",
                        "description": "The value of the fact to store.",
                    }
                },
                "required": ["key", "value"],
            }
        )
        
        self.tools = Tool(function_declarations=[
            self.query_analyst_declaration,
            self.recall_fact_declaration,
            self.store_fact_declaration
        ])
        
    def _get_model(self, session_id: str) -> GenerativeModel:
        # Fetch current SQLite memories for context injection (Context Engineering)
        from database import get_session_memories
        memories = get_session_memories(self.db, session_id)
        
        memory_str = ""
        if memories:
            memory_str = "\nActive Session Memories (retrieved from SQLite):\n"
            for k, v in memories.items():
                memory_str += f"- {k}: {v}\n"
                
        system_instruction = (
            "You are a Compliance Auditor Agent. Your job is to audit company transactions and director decisions "
            "(like potential conflicts of interest, good faith, or use of position). You must retrieve the relevant "
            "legal statutes by calling the 'query_legal_analyst' tool. You should also remember key details (like names, "
            "companies, values) by storing them in session memory (using 'store_fact') or retrieving them (using 'recall_fact'). "
            "Synthesize a professional audit report outlining any compliance issues. Refer to stored memories to personalize replies.\n"
            f"{memory_str}"
        )
        
        return GenerativeModel(
            model_name="gemini-1.5-flash",
            tools=[self.tools],
            system_instruction=system_instruction
        )

    def run(self, user_input: str, session_id: str = "default", trace: list = None) -> str:
        if trace is None:
            trace = []
            
        trace.append({
            "agent": "ComplianceAuditorAgent",
            "action": "received_query",
            "message": f"Auditing query: '{user_input}'"
        })
        
        model = self._get_model(session_id)
        chat = model.start_chat()
        response = chat.send_message(user_input)
        
        max_turns = 10
        turn = 0
        while turn < max_turns:
            turn += 1
            function_call = _extract_function_call(response)
            if not function_call:
                break
                
            tool_name = function_call.name
            args = function_call.args
            
            trace.append({
                "agent": "ComplianceAuditorAgent",
                "action": "call_tool",
                "tool": tool_name,
                "args": dict(args)
            })
            
            tool_output = ""
            if tool_name == "query_legal_analyst":
                sub_query = args.get("query")
                tool_output = self.analyst.run(sub_query, trace=trace)
            elif tool_name == "recall_fact":
                key = args.get("key", "").strip().lower()
                from database import get_session_memories
                mems = get_session_memories(self.db, session_id)
                tool_output = mems.get(key, f"Fact with key '{key}' not found in memory.")
            elif tool_name == "store_fact":
                key = args.get("key", "").strip().lower()
                value = args.get("value", "").strip()
                from database import save_session_memory
                save_session_memory(self.db, session_id, key, value)
                tool_output = f"Successfully stored fact: '{key}' = '{value}'"
            else:
                tool_output = f"Unknown tool: {tool_name}"
                
            trace.append({
                "agent": "ComplianceAuditorAgent",
                "action": "tool_output",
                "tool": tool_name,
                "output": tool_output
            })
            
            response = chat.send_message(
                Part.from_function_response(
                    name=tool_name,
                    response={"result": tool_output}
                )
            )
            
        final_text = response.text
        trace.append({
            "agent": "ComplianceAuditorAgent",
            "action": "final_response",
            "message": final_text
        })
        return final_text


class LegalAgent:
    """Orchestrator class that maintains backward compatibility while routing requests."""
    def __init__(self, db_conn):
        self.db = db_conn
        
        # Initialize Vertex AI
        project = os.getenv("GCP_PROJECT_ID", "your-gcp-project-id")
        location = os.getenv("GCP_LOCATION", "us-central1")
        vertexai.init(project=project, location=location)

        # Instantiate sub-agents
        self.analyst = LegalAnalystAgent(db_conn)
        self.auditor = ComplianceAuditorAgent(db_conn, self.analyst)

    def run(self, user_input: str, session_id: str = "default", trace: list = None) -> str:
        if trace is None:
            trace = []
            
        lower_input = user_input.lower()
        # Simple routing logic: if looking for exact sections/clauses, use Analyst. Otherwise, use Auditor.
        if "section" in lower_input or "statute" in lower_input or "corp-" in lower_input:
            print(f"[Orchestrator] Routing direct statute query to LegalAnalystAgent")
            return self.analyst.run(user_input, trace=trace)
        else:
            print(f"[Orchestrator] Routing scenario/audit query to ComplianceAuditorAgent")
            return self.auditor.run(user_input, session_id=session_id, trace=trace)




================================================
FILE: src/app.py
================================================
import os
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
from database import setup_database, get_session_memories, clear_session_memories
from agent import LegalAgent

# Load environment variables
load_dotenv()

# We specify static_folder to serve the web UI dashboard from src/static
app = Flask(__name__, static_folder="static")

# Initialize database and agent globally on startup
print("Initializing persistent SQLite database & LegalAgent on startup...")
db_conn = setup_database()
agent = LegalAgent(db_conn)

@app.route("/", methods=["GET"])
def index():
    """Serves the index.html frontend dashboard from the static folder."""
    return send_from_directory(app.static_folder, "index.html")

@app.route("/query", methods=["POST"])
def handle_query():
    """Handles multi-agent queries, passing trace arrays and session IDs."""
    data = request.get_json() or {}
    user_input = data.get("query")
    session_id = data.get("session_id", "default").strip()
    
    if not user_input:
        return jsonify({"error": "Missing required 'query' field in JSON request body."}), 400
    
    try:
        trace_logs = []
        # Run agent with session_id and trace array
        response_text = agent.run(user_input, session_id=session_id, trace=trace_logs)
        
        # Fetch current SQLite session memories to return to frontend
        memories = get_session_memories(db_conn, session_id)
        
        return jsonify({
            "query": user_input,
            "response": response_text,
            "trace": trace_logs,
            "memory": memories
        })
    except Exception as e:
        print(f"Error handling query request: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/memory", methods=["GET"])
def handle_get_memory():
    """Returns the current key-value memories for a session."""
    session_id = request.args.get("session_id", "default").strip()
    try:
        memories = get_session_memories(db_conn, session_id)
        return jsonify({
            "session_id": session_id,
            "memory": memories
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/clear", methods=["POST"])
def handle_clear_memory():
    """Clears all SQLite session memories for a specific session."""
    data = request.get_json() or {}
    session_id = data.get("session_id", "default").strip()
    try:
        clear_session_memories(db_conn, session_id)
        return jsonify({
            "status": "success",
            "message": f"Memory for session '{session_id}' has been cleared successfully."
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Cloud Run/standard container runners expect listening on the PORT environment variable
    port = int(os.getenv("PORT", 8080))
    print(f"Starting server on port {port}...")
    app.run(host="0.0.0.0", port=port)




================================================
FILE: src/database.py
================================================
import sqlite3

def setup_database():
    """Initializes an in-memory SQLite database and seeds it with statutes."""
    # We use in-memory database for local test runs
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS statutes (
            id TEXT PRIMARY KEY,
            title TEXT,
            clause TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS session_memories (
            session_id TEXT,
            key TEXT,
            value TEXT,
            PRIMARY KEY (session_id, key)
        )
    ''')
    
    # Seeding Australian Corporations Act statutory definition data
    statutes_data = [
        (
            'corp-181',
            'Corporations Act Section 181',
            'Good faith: A director or other officer of a corporation must exercise their powers and discharge their duties in good faith in the best interests of the corporation and for a proper purpose.'
        ),
        (
            'corp-182',
            'Corporations Act Section 182',
            'Use of position: A director, secretary, other officer or employee of a corporation must not improperly use their position to gain an advantage for themselves or someone else or cause detriment to the corporation.'
        )
    ]
    
    cursor.executemany(
        'INSERT OR REPLACE INTO statutes (id, title, clause) VALUES (?, ?, ?)',
        statutes_data
    )
    conn.commit()
    return conn

def save_session_memory(conn, session_id: str, key: str, value: str):
    """Saves or updates a fact in SQLite session memories."""
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO session_memories (session_id, key, value)
        VALUES (?, ?, ?)
    ''', (session_id, key.strip().lower(), value.strip()))
    conn.commit()

def get_session_memories(conn, session_id: str) -> dict:
    """Retrieves all memory facts stored for a session as a key-value dictionary."""
    cursor = conn.cursor()
    cursor.execute('SELECT key, value FROM session_memories WHERE session_id = ?', (session_id,))
    rows = cursor.fetchall()
    return {row[0]: row[1] for row in rows}

def clear_session_memories(conn, session_id: str):
    """Deletes all memory facts for a session."""
    cursor = conn.cursor()
    cursor.execute('DELETE FROM session_memories WHERE session_id = ?', (session_id,))
    conn.commit()




================================================
FILE: src/main.py
================================================
import os
from dotenv import load_dotenv
from database import setup_database, get_session_memories
from agent import LegalAgent

# Load local environment configuration
load_dotenv()

def main():
    print("==================================================")
    print("GDG Yerevan Workshop - Multi-Agent & Memory CLI Demo")
    print("==================================================")
    
    # Check if Vertex credentials/project is configured
    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id or project_id == "your-gcp-project-id":
        print("[WARNING] 'GCP_PROJECT_ID' is not configured in .env.")
        print("Please configure it with a valid GCP Project ID before executing Vertex AI calls.")
        print("Continuing initialization (will fail at Vertex AI calls if credentials are missing)...")
        print("--------------------------------------------------")

    print("Setting up local SQLite database with Statutes...")
    db_conn = setup_database()
    
    print("Initializing Multi-Agent System (LegalAgent Orchestrator)...")
    try:
        agent = LegalAgent(db_conn)
        session_id = "cli-test-session"
        
        # Test Query 1: Multi-Agent Audit & SQLite Memory Writing
        query_1 = "Audit this scenario: A director named Alice wants to approve a $200k contract for her husband's business."
        print(f"\n>>> Running Query 1: {query_1}")
        
        trace_1 = []
        response_1 = agent.run(query_1, session_id=session_id, trace=trace_1)
        
        print("\n--- Agent Execution Trace (Query 1) ---")
        for step in trace_1:
            if step['action'] == 'call_tool':
                print(f"[{step['agent']}] 🔧 CALL TOOL: {step['tool']}({step.get('args', '')})")
            elif step['action'] == 'tool_output':
                # Truncate output for readability
                out = str(step['output'])
                trunc_out = out[:80] + "..." if len(out) > 80 else out
                print(f"[{step['agent']}] 🔧 TOOL OUTPUT: {trunc_out}")
            elif step['action'] == 'received_query':
                print(f"[{step['agent']}] 📥 RECEIVED: {step['message']}")
        
        print(f"\n--- Final Auditor Answer ---\n{response_1}")
        
        print("\n--------------------------------------------------")
        
        # Inspect SQLite memories directly to prove it was saved in SQLite
        mems = get_session_memories(db_conn, session_id)
        print(f"SQLite Saved Memories for session '{session_id}':")
        for k, v in mems.items():
            print(f"  - {k}: {v}")
            
        print("--------------------------------------------------")
        
        # Test Query 2: Retrieve fact from SQLite Memory
        query_2 = "What was the name of the director we audited in the previous query and what was the value of the transaction?"
        print(f"\n>>> Running Query 2: {query_2}")
        
        trace_2 = []
        response_2 = agent.run(query_2, session_id=session_id, trace=trace_2)
        print(f"\n--- Final Auditor Answer ---\n{response_2}")
        
        print("--------------------------------------------------")
        
        # Test Query 3: Direct Statute lookup (triggers Routing to LegalAnalystAgent)
        query_3 = "What does Corporations Act Section 181 state?"
        print(f"\n>>> Running Query 3: {query_3}")
        
        trace_3 = []
        response_3 = agent.run(query_3, session_id=session_id, trace=trace_3)
        print(f"\n--- Final Analyst Answer ---\n{response_3}")

    except Exception as e:
        print(f"\n[ERROR] Failed to run agent: {e}")
        print("Ensure you have authenticated with: gcloud auth application-default login")

    finally:
        db_conn.close()
        print("\nDatabase connection closed.")
        print("==================================================")

if __name__ == "__main__":
    main()




================================================
FILE: src/static/app.js
================================================
document.addEventListener('DOMContentLoaded', () => {
    // Selectors
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const chatMessages = document.getElementById('chat-messages');
    const sessionIdInput = document.getElementById('session-id');
    const clearMemoryBtn = document.getElementById('clear-memory-btn');
    const thoughtLogs = document.getElementById('thought-logs');
    const dbVariables = document.getElementById('db-variables');
    const sampleBtns = document.querySelectorAll('.sample-btn');

    // State
    let isGenerating = false;

    // Helper: Scroll chat to bottom
    const scrollToBottom = () => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    // Helper: Formats basic markdown elements (bold, bullet lists, sections) into HTML
    const formatResponseText = (text) => {
        if (!text) return '';
        let html = text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");
        
        // Headers
        html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
        html = html.replace(/^## (.*$)/gim, '<h3>$1</h3>');
        
        // Bold
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Lists
        html = html.replace(/^\s*[\-\*]\s+(.*$)/gim, '<li>$1</li>');
        html = html.replace(/(<li>.*<\/li>)/gim, '<ul>$1</ul>');
        html = html.replace(/<\/ul>\s*<ul>/g, ''); // Join adjacent lists
        
        // Linebreaks (preserve double breaks, convert single breaks)
        html = html.replace(/\n\n/g, '</p><p>');
        html = html.replace(/\n/g, '<br>');
        
        return `<p>${html}</p>`;
    };

    // Load active session memory
    const loadSessionMemory = async () => {
        const sessionId = sessionIdInput.value.trim() || 'default';
        try {
            const response = await fetch(`/memory?session_id=${encodeURIComponent(sessionId)}`);
            const data = await response.json();
            if (response.ok) {
                renderMemory(data.memory);
            }
        } catch (error) {
            console.error('Failed to load session memory:', error);
        }
    };

    // Render SQLite Memory items
    const renderMemory = (memory) => {
        if (!memory || Object.keys(memory).length === 0) {
            dbVariables.innerHTML = `
                <div class="empty-state-db">
                    <p>No variables saved in SQLite yet. As you audit, the auditor agent will call <code>store_fact()</code> to remember things.</p>
                </div>
            `;
            return;
        }

        let html = '<div class="db-grid">';
        for (const [key, val] of Object.entries(memory)) {
            html += `
                <div class="db-row">
                    <span class="db-key"><i class="fa-solid fa-tag"></i> ${key}</span>
                    <span class="db-val" title="${val}">${val}</span>
                </div>
            `;
        }
        html += '</div>';
        dbVariables.innerHTML = html;
    };

    // Render step-by-step trace logs
    const renderTraceLogs = (trace) => {
        if (!trace || trace.length === 0) {
            thoughtLogs.innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-spinner"></i>
                    <p>Send a message to see agent routing, collaborative thought logs, and local tool executions in real-time.</p>
                </div>
            `;
            return;
        }

        thoughtLogs.innerHTML = '';
        trace.forEach(entry => {
            const entryDiv = document.createElement('div');
            
            // Assign class based on the executing agent
            const agentClass = entry.agent === 'LegalAnalystAgent' ? 'analyst' : 'auditor';
            entryDiv.className = `trace-entry ${agentClass}`;
            
            let contentHtml = '';
            
            // Parse different action types
            if (entry.action === 'received_query') {
                contentHtml = `
                    <div class="trace-header">
                        <span class="agent-tag"><i class="fa-solid fa-user-gear"></i> ${entry.agent}</span>
                        <span class="action-tag">Receive</span>
                    </div>
                    <div class="trace-desc">${entry.message}</div>
                `;
            } else if (entry.action === 'call_tool') {
                contentHtml = `
                    <div class="trace-header">
                        <span class="agent-tag"><i class="fa-solid fa-gears"></i> ${entry.agent}</span>
                        <span class="action-tag">Call Tool</span>
                    </div>
                    <div class="trace-desc">Invoked <strong>${entry.tool}</strong>:</div>
                    <div class="trace-code">${JSON.stringify(entry.args, null, 2)}</div>
                `;
            } else if (entry.action === 'tool_output') {
                contentHtml = `
                    <div class="trace-header">
                        <span class="agent-tag"><i class="fa-solid fa-database"></i> ${entry.agent}</span>
                        <span class="action-tag">Tool Result</span>
                    </div>
                    <div class="trace-desc">Returned data from local system:</div>
                    <div class="trace-code">${entry.output}</div>
                `;
            } else if (entry.action === 'final_response') {
                contentHtml = `
                    <div class="trace-header">
                        <span class="agent-tag"><i class="fa-solid fa-circle-check"></i> ${entry.agent}</span>
                        <span class="action-tag">Output</span>
                    </div>
                    <div class="trace-desc">${entry.message.substring(0, 150)}${entry.message.length > 150 ? '...' : ''}</div>
                `;
            }
            
            entryDiv.innerHTML = contentHtml;
            thoughtLogs.appendChild(entryDiv);
        });
        
        // Scroll trace to bottom
        thoughtLogs.scrollTop = thoughtLogs.scrollHeight;
    };

    // Send chat query to server
    const sendQuery = async (queryText) => {
        if (!queryText.trim() || isGenerating) return;
        
        isGenerating = true;
        chatInput.value = '';
        chatInput.style.height = 'auto'; // Reset size
        sendBtn.disabled = true;

        // 1. Add User Message
        const userDiv = document.createElement('div');
        userDiv.className = 'message user-message';
        userDiv.textContent = queryText;
        chatMessages.appendChild(userDiv);
        scrollToBottom();

        // 2. Add Typing Indicator
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message agent-message typing-indicator-container';
        typingDiv.innerHTML = `
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        chatMessages.appendChild(typingDiv);
        scrollToBottom();

        // Reset thought stream for current run
        thoughtLogs.innerHTML = `
            <div class="empty-state">
                <i class="fa-solid fa-spinner" style="animation: rotate 1s linear infinite;"></i>
                <p>Executing agents in Vertex AI and scanning SQLite schema...</p>
            </div>
        `;

        const sessionId = sessionIdInput.value.trim() || 'default';

        try {
            const response = await fetch('/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: queryText, session_id: sessionId })
            });
            
            const data = await response.json();
            
            // Remove typing indicator
            typingDiv.remove();
            
            if (response.ok) {
                // 3. Render Agent Reply
                const agentDiv = document.createElement('div');
                agentDiv.className = 'message agent-message';
                agentDiv.innerHTML = formatResponseText(data.response);
                chatMessages.appendChild(agentDiv);
                
                // 4. Update Trace Logs and Database Variables
                renderTraceLogs(data.trace);
                renderMemory(data.memory);
            } else {
                // Render Error
                const errorDiv = document.createElement('div');
                errorDiv.className = 'message agent-message system-message';
                errorDiv.style.borderLeft = '3px solid var(--danger-color)';
                errorDiv.innerHTML = `<p><strong>Error:</strong> ${data.error || 'Server error occurred.'}</p>`;
                chatMessages.appendChild(errorDiv);
                
                thoughtLogs.innerHTML = `
                    <div class="empty-state" style="color: var(--danger-color);">
                        <i class="fa-solid fa-triangle-exclamation"></i>
                        <p>Execution failed. Please make sure you authenticated using GCP application-default login.</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('API Error:', error);
            typingDiv.remove();
            
            const errorDiv = document.createElement('div');
            errorDiv.className = 'message agent-message system-message';
            errorDiv.style.borderLeft = '3px solid var(--danger-color)';
            errorDiv.innerHTML = `<p><strong>Network Error:</strong> Failed to communicate with the Flask API server.</p>`;
            chatMessages.appendChild(errorDiv);
        } finally {
            isGenerating = false;
            sendBtn.disabled = false;
            scrollToBottom();
        }
    };

    // Event Listeners
    sendBtn.addEventListener('click', () => {
        sendQuery(chatInput.value);
    });

    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendQuery(chatInput.value);
        }
    });

    // Textarea Auto-grow
    chatInput.addEventListener('input', () => {
        chatInput.style.height = 'auto';
        chatInput.style.height = (chatInput.scrollHeight) + 'px';
    });

    // Session Change triggers memory load
    sessionIdInput.addEventListener('change', () => {
        loadSessionMemory();
        thoughtLogs.innerHTML = `
            <div class="empty-state">
                <i class="fa-solid fa-spinner"></i>
                <p>Switched session. Send a message to trace agent interactions.</p>
            </div>
        `;
    });

    // Clear session memory
    clearMemoryBtn.addEventListener('click', async () => {
        const sessionId = sessionIdInput.value.trim() || 'default';
        if (confirm(`Are you sure you want to clear the SQLite session memory for: "${sessionId}"?`)) {
            try {
                const response = await fetch('/clear', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ session_id: sessionId })
                });
                const data = await response.json();
                if (response.ok) {
                    alert(data.message);
                    renderMemory({});
                    
                    // Add system note to chat
                    const sysDiv = document.createElement('div');
                    sysDiv.className = 'message system-message';
                    sysDiv.innerHTML = `<p><i class="fa-solid fa-circle-info"></i> Session memory wiped in database for <strong>${sessionId}</strong>.</p>`;
                    chatMessages.appendChild(sysDiv);
                    scrollToBottom();
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (err) {
                console.error(err);
                alert('Failed to clear memory');
            }
        }
    });

    // Sample prompts trigger
    sampleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const qText = btn.getAttribute('data-query');
            sendQuery(qText);
        });
    });

    // Initial Load
    loadSessionMemory();
});



================================================
FILE: src/static/index.html
================================================
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GDG Yerevan AI Multi-Agent Workshop Prep Hub</title>
    <!-- Modern Premium Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <!-- FontAwesome for Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="app-container">
        <!-- TOP DECORATION GLOWS -->
        <div class="glow-orb top-left"></div>
        <div class="glow-orb top-right"></div>

        <!-- HEADER -->
        <header class="app-header">
            <div class="logo-area">
                <i class="fa-solid fa-network-wired logo-icon"></i>
                <div class="logo-text">
                    <h1>GDG Yerevan AI Workshop</h1>
                    <p>Multi-Agent & Session Memory Prep Hub</p>
                </div>
            </div>
            <div class="session-controls">
                <div class="input-group">
                    <label for="session-id"><i class="fa-solid fa-fingerprint"></i> Session ID:</label>
                    <input type="text" id="session-id" value="gdg-yerevan-demo" placeholder="e.g. session-1">
                </div>
                <button id="clear-memory-btn" class="btn btn-secondary" title="Clear SQLite memory for this session">
                    <i class="fa-solid fa-trash-can"></i> Clear Memory
                </button>
            </div>
        </header>

        <!-- MAIN LAYOUT -->
        <main class="app-body">
            
            <!-- LEFT COLUMN: WORKSHOP ROADMAP & ARCHITECTURE MAP -->
            <section class="panel-left card">
                <div class="card-header">
                    <h2><i class="fa-solid fa-graduation-cap"></i> Workshop Prep Checklist</h2>
                </div>
                <div class="card-body scrollable">
                    <div class="roadmap-checklist">
                        <div class="checklist-item done">
                            <input type="checkbox" id="check-gcp" checked disabled>
                            <label for="check-gcp">
                                <strong>Cloud & Infrastructure (Rohan)</strong>
                                <span class="desc">GCP CLI, auth login, Cloud Run deployment readiness</span>
                            </label>
                        </div>
                        <div class="checklist-item done">
                            <input type="checkbox" id="check-tool" checked disabled>
                            <label for="check-tool">
                                <strong>Agentic Layer & Tools (Armen)</strong>
                                <span class="desc">Function declaration definitions, tool calling workflows</span>
                            </label>
                        </div>
                        <div class="checklist-item done">
                            <input type="checkbox" id="check-orchestration" checked disabled>
                            <label for="check-orchestration">
                                <strong>Multi-Agent Collaboration</strong>
                                <span class="desc">Auditor calling Legal Analyst tool-as-an-agent pattern</span>
                            </label>
                        </div>
                        <div class="checklist-item done">
                            <input type="checkbox" id="check-memory" checked disabled>
                            <label for="check-memory">
                                <strong>Memory & Context (Vadim)</strong>
                                <span class="desc">SQLite key-value persistence & context-injected engineering</span>
                            </label>
                        </div>
                    </div>

                    <div class="arch-section">
                        <h3><i class="fa-solid fa-diagram-project"></i> System Architecture</h3>
                        <div class="arch-diagram">
                            <div class="arch-node user">
                                <i class="fa-solid fa-desktop"></i>
                                <span>Browser UI</span>
                            </div>
                            <div class="arch-arrow"><i class="fa-solid fa-arrow-right"></i></div>
                            <div class="arch-node flask">
                                <i class="fa-brands fa-python"></i>
                                <span>Flask API<br><small>(Cloud Run)</small></span>
                            </div>
                            <div class="arch-arrow"><i class="fa-solid fa-arrow-right"></i></div>
                            <div class="arch-subsystem">
                                <div class="subsystem-node vertex">
                                    <i class="fa-solid fa-brain"></i>
                                    <span>Vertex AI<br><small>(Gemini 1.5)</small></span>
                                </div>
                                <div class="subsystem-node db">
                                    <i class="fa-solid fa-database"></i>
                                    <span>SQLite<br><small>(Session Memory)</small></span>
                                </div>
                            </div>
                        </div>
                        <p class="arch-info">When you ask a question, the Flask backend coordinates the Auditor agent. The Auditor pulls current memories from SQLite and dynamically communicates with the Legal Analyst agent and SQLite db using tools.</p>
                    </div>
                </div>
            </section>

            <!-- MIDDLE COLUMN: INTERACTIVE CHAT PLAYGROUND -->
            <section class="panel-center card">
                <div class="card-header chat-header">
                    <div class="header-left">
                        <span class="status-indicator online"></span>
                        <h2><i class="fa-solid fa-robot"></i> Compliance Auditor Agent</h2>
                    </div>
                    <span class="badge">gemini-1.5-flash</span>
                </div>
                <div class="card-body chat-messages-container" id="chat-messages">
                    <div class="message system-message">
                        <p>Welcome! Try sending a compliance query to check conflicts of interest, or test persistent session memory across turns. Here are some prompts to try:</p>
                        <div class="sample-prompts">
                            <button class="sample-btn" data-query="Let's audit a scenario. A director named Alice wants to hire her sister's agency for a $200k contract. Analyze this.">
                                <i class="fa-solid fa-play"></i> Audit Alice
                            </button>
                            <button class="sample-btn" data-query="Do you remember the director's name and the transaction size from our previous query?">
                                <i class="fa-solid fa-clock-rotate-left"></i> Recall Director Details
                            </button>
                            <button class="sample-btn" data-query="What does Corporations Act Section 182 state?">
                                <i class="fa-solid fa-book-open"></i> Query Section 182
                            </button>
                        </div>
                    </div>
                </div>
                <div class="chat-input-area">
                    <textarea id="chat-input" placeholder="Type a compliance scenario or ask questions..." rows="1"></textarea>
                    <button id="send-btn" class="btn btn-primary"><i class="fa-solid fa-paper-plane"></i> Send</button>
                </div>
            </section>

            <!-- RIGHT COLUMN: TRACE WRITER & SQL MEMORY OBSERVER -->
            <section class="panel-right">
                
                <!-- TOP PANEL: THOUGHT STREAM / COLLABORATION LOGS -->
                <div class="card panel-thought-stream">
                    <div class="card-header">
                        <h2><i class="fa-solid fa-wand-magic-sparkles"></i> Live Agent Thought Stream</h2>
                    </div>
                    <div class="card-body scrollable thought-logs" id="thought-logs">
                        <div class="empty-state">
                            <i class="fa-solid fa-spinner"></i>
                            <p>Send a message to see agent routing, collaborative thought logs, and local tool executions in real-time.</p>
                        </div>
                    </div>
                </div>

                <!-- BOTTOM PANEL: SQLite PERSISTED FACT INSPECTOR -->
                <div class="card panel-db-memory">
                    <div class="card-header">
                        <h2><i class="fa-solid fa-database"></i> SQLite Session Memory</h2>
                    </div>
                    <div class="card-body scrollable db-variables" id="db-variables">
                        <div class="empty-state-db">
                            <p>No variables saved in SQLite yet. As you audit, the auditor agent will call <code>store_fact()</code> to remember things.</p>
                        </div>
                    </div>
                </div>

            </section>

        </main>
        
        <!-- FOOTER INFO -->
        <footer class="app-footer">
            <p>GDG Yerevan AI Multi-Agent Workshop prep application | Built with Vertex AI, Flask & SQLite</p>
        </footer>
    </div>

    <!-- MAIN APP SCRIPT -->
    <script src="app.js"></script>
</body>
</html>



================================================
FILE: src/static/style.css
================================================
/* Global Theme & Tokens */
:root {
    --bg-app: #090b11;
    --bg-card: rgba(18, 22, 35, 0.7);
    --bg-card-hover: rgba(26, 32, 53, 0.8);
    --border-color: rgba(255, 255, 255, 0.08);
    
    --primary-color: #3b82f6; /* Modern Blue */
    --primary-glow: rgba(59, 130, 246, 0.15);
    --secondary-color: #6366f1; /* Modern Indigo */
    --accent-color: #a855f7; /* Modern Purple */
    --success-color: #10b981; /* Modern Green */
    --warning-color: #f59e0b; /* Modern Amber */
    --danger-color: #ef4444;
    
    --text-primary: #f3f4f6;
    --text-muted: #9ca3af;
    --text-dark: #1f2937;
    
    --font-heading: 'Outfit', sans-serif;
    --font-body: 'Inter', sans-serif;
    
    --transition-fast: 0.2s ease;
    --transition-normal: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    
    --shadow-premium: 0 10px 30px -10px rgba(0, 0, 0, 0.7);
}

/* Reset & Base Styles */
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    background-color: var(--bg-app);
    color: var(--text-primary);
    font-family: var(--font-body);
    overflow-x: hidden;
    height: 100vh;
    width: 100vw;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.2);
}
::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.3);
}

/* Decorative Background Glows */
.glow-orb {
    position: absolute;
    width: 500px;
    height: 500px;
    border-radius: 50%;
    filter: blur(150px);
    opacity: 0.15;
    z-index: 0;
    pointer-events: none;
}
.glow-orb.top-left {
    background: radial-gradient(circle, var(--primary-color) 0%, transparent 70%);
    top: -200px;
    left: -200px;
}
.glow-orb.top-right {
    background: radial-gradient(circle, var(--accent-color) 0%, transparent 70%);
    top: -200px;
    right: -200px;
}

/* Main Container */
.app-container {
    position: relative;
    z-index: 1;
    display: flex;
    flex-direction: column;
    height: 100vh;
    max-width: 1600px;
    margin: 0 auto;
    padding: 1rem;
}

/* Header */
.app-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1.25rem;
    margin-bottom: 1rem;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    backdrop-filter: blur(10px);
    box-shadow: var(--shadow-premium);
}

.logo-area {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.logo-icon {
    font-size: 1.75rem;
    color: var(--primary-color);
    text-shadow: 0 0 10px var(--primary-glow);
}

.logo-text h1 {
    font-family: var(--font-heading);
    font-size: 1.25rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, var(--text-primary) 30%, var(--text-muted) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.logo-text p {
    font-size: 0.8rem;
    color: var(--text-muted);
}

.session-controls {
    display: flex;
    align-items: center;
    gap: 1.25rem;
}

.session-controls .input-group {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.session-controls label {
    font-size: 0.85rem;
    color: var(--text-muted);
    font-weight: 500;
}

.session-controls input {
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    padding: 0.4rem 0.75rem;
    border-radius: 6px;
    font-family: var(--font-body);
    font-size: 0.85rem;
    outline: none;
    transition: var(--transition-fast);
}

.session-controls input:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 8px var(--primary-glow);
}

/* Button UI */
.btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    font-family: var(--font-body);
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    border: none;
    transition: var(--transition-fast);
}

.btn-primary {
    background: var(--primary-color);
    color: #fff;
}
.btn-primary:hover {
    background: #2563eb;
    box-shadow: 0 0 12px var(--primary-glow);
}

.btn-secondary {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
}
.btn-secondary:hover {
    background: rgba(255, 255, 255, 0.1);
}

/* Main Body Layout */
.app-body {
    display: grid;
    grid-template-columns: 280px 1fr 350px;
    gap: 1rem;
    flex: 1;
    min-height: 0; /* Important for flex child scrollability */
}

/* Card layout */
.card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    backdrop-filter: blur(10px);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    box-shadow: var(--shadow-premium);
}

.card-header {
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.card-header h2 {
    font-family: var(--font-heading);
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.card-body {
    padding: 1rem;
    flex: 1;
    min-height: 0;
}

.scrollable {
    overflow-y: auto;
}

/* LEFT PANEL styles */
.roadmap-checklist {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    margin-bottom: 1.25rem;
}

.checklist-item {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.65rem 0.75rem;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: 8px;
    transition: var(--transition-fast);
}

.checklist-item:hover {
    background: rgba(255, 255, 255, 0.04);
}

.checklist-item input[type="checkbox"] {
    margin-top: 0.25rem;
    accent-color: var(--success-color);
}

.checklist-item label {
    display: flex;
    flex-direction: column;
    cursor: not-allowed;
}

.checklist-item label strong {
    font-size: 0.8rem;
    font-weight: 600;
}

.checklist-item label .desc {
    font-size: 0.7rem;
    color: var(--text-muted);
    margin-top: 0.1rem;
}

.arch-section {
    border-top: 1px solid var(--border-color);
    padding-top: 1rem;
}

.arch-section h3 {
    font-family: var(--font-heading);
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 0.75rem;
    color: var(--secondary-color);
}

.arch-diagram {
    background: rgba(0, 0, 0, 0.2);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 0.75rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.4rem;
    margin-bottom: 0.75rem;
}

.arch-node {
    width: 100%;
    padding: 0.5rem;
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--border-color);
    text-align: center;
    font-size: 0.75rem;
    font-weight: 500;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.2rem;
}

.arch-node.user i { color: var(--accent-color); }
.arch-node.flask i { color: var(--primary-color); }

.arch-arrow {
    font-size: 0.65rem;
    color: var(--text-muted);
    transform: rotate(90deg);
    margin: 0.1rem 0;
}

.arch-subsystem {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem;
    width: 100%;
}

.subsystem-node {
    padding: 0.5rem;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--border-color);
    border-radius: 6px;
    text-align: center;
    font-size: 0.65rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
}
.subsystem-node.vertex i { color: var(--warning-color); }
.subsystem-node.db i { color: var(--success-color); }

.subsystem-node small, .arch-node small {
    color: var(--text-muted);
    font-size: 0.55rem;
}

.arch-info {
    font-size: 0.7rem;
    color: var(--text-muted);
    line-height: 1.35;
}

/* CENTER PANEL: CHAT PLAYGROUND */
.status-indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
}
.status-indicator.online {
    background-color: var(--success-color);
    box-shadow: 0 0 6px var(--success-color);
}

.badge {
    background: rgba(59, 130, 246, 0.15);
    color: var(--primary-color);
    font-size: 0.7rem;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    font-family: monospace;
    border: 1px solid rgba(59, 130, 246, 0.3);
}

.chat-messages-container {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    background: rgba(0, 0, 0, 0.15);
}

.message {
    max-width: 80%;
    padding: 0.75rem 1rem;
    border-radius: 10px;
    font-size: 0.85rem;
    line-height: 1.45;
    animation: slideUp 0.3s ease-out;
}

.message.user-message {
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
    align-self: flex-end;
    color: #fff;
    border-bottom-right-radius: 2px;
}

.message.agent-message {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid var(--border-color);
    align-self: flex-start;
    border-bottom-left-radius: 2px;
}

.message.system-message {
    background: rgba(99, 102, 241, 0.05);
    border: 1px solid rgba(99, 102, 241, 0.15);
    max-width: 100%;
    border-radius: 8px;
    color: var(--text-primary);
}

.message.system-message p {
    margin-bottom: 0.75rem;
}

.sample-prompts {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.sample-btn {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    padding: 0.4rem 0.75rem;
    border-radius: 6px;
    font-size: 0.75rem;
    cursor: pointer;
    transition: var(--transition-fast);
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
}

.sample-btn:hover {
    background: rgba(255, 255, 255, 0.08);
    border-color: var(--primary-color);
    color: var(--primary-color);
}

/* Chat Input Area */
.chat-input-area {
    padding: 0.75rem;
    border-top: 1px solid var(--border-color);
    display: flex;
    gap: 0.5rem;
    align-items: flex-end;
    background: rgba(0, 0, 0, 0.2);
}

.chat-input-area textarea {
    flex: 1;
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 0.6rem 0.8rem;
    color: var(--text-primary);
    font-family: var(--font-body);
    font-size: 0.85rem;
    outline: none;
    resize: none;
    max-height: 120px;
    transition: var(--transition-fast);
}

.chat-input-area textarea:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 8px var(--primary-glow);
}

/* RIGHT PANEL: THOUGHTS & SQL memories */
.panel-right {
    display: grid;
    grid-template-rows: 60% 40%;
    gap: 1rem;
    min-height: 0;
}

.thought-logs {
    background: rgba(0, 0, 0, 0.2);
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.empty-state, .empty-state-db {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    height: 100%;
    color: var(--text-muted);
    padding: 2rem;
    gap: 1rem;
}

.empty-state i {
    font-size: 1.5rem;
    animation: rotate 2s linear infinite;
    color: var(--primary-color);
}

.empty-state p, .empty-state-db p {
    font-size: 0.75rem;
    line-height: 1.4;
}

/* Thought log entries */
.trace-entry {
    border-left: 2px solid var(--border-color);
    padding-left: 0.75rem;
    margin-bottom: 0.5rem;
    animation: fadeIn 0.25s ease-out;
}

.trace-entry.analyst {
    border-color: var(--warning-color);
}

.trace-entry.auditor {
    border-color: var(--secondary-color);
}

.trace-header {
    display: flex;
    justify-content: space-between;
    font-size: 0.7rem;
    font-weight: 600;
    margin-bottom: 0.25rem;
}

.trace-header .agent-tag {
    color: var(--text-primary);
}

.trace-header .action-tag {
    font-family: monospace;
    text-transform: uppercase;
}

.trace-entry.analyst .trace-header .action-tag { color: var(--warning-color); }
.trace-entry.auditor .trace-header .action-tag { color: var(--secondary-color); }

.trace-desc {
    font-size: 0.75rem;
    color: var(--text-muted);
    word-break: break-word;
}

.trace-code {
    font-family: monospace;
    font-size: 0.7rem;
    background: rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.05);
    padding: 0.4rem;
    border-radius: 4px;
    margin-top: 0.25rem;
    color: #a7f3d0; /* Soft mint */
    white-space: pre-wrap;
    word-break: break-all;
    max-height: 120px;
    overflow-y: auto;
}

/* DB persistent memory panel */
.db-variables {
    background: rgba(0, 0, 0, 0.2);
}

.db-grid {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 0.5rem;
    align-items: center;
}

.db-row {
    grid-column: span 2;
    display: flex;
    align-items: center;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid var(--border-color);
    padding: 0.4rem 0.6rem;
    border-radius: 6px;
    justify-content: space-between;
    animation: fadeIn 0.3s ease-out;
}

.db-key {
    font-family: monospace;
    font-weight: 600;
    color: var(--accent-color);
    font-size: 0.75rem;
}

.db-val {
    font-size: 0.75rem;
    color: var(--text-primary);
    background: rgba(0, 0, 0, 0.3);
    padding: 0.15rem 0.4rem;
    border-radius: 4px;
    max-width: 60%;
    text-overflow: ellipsis;
    overflow: hidden;
    white-space: nowrap;
}

/* Typing indicator spinner */
.typing-indicator {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.5rem 0.75rem;
}

.typing-indicator span {
    width: 6px;
    height: 6px;
    background-color: var(--text-muted);
    border-radius: 50%;
    animation: bounce 1.4s infinite ease-in-out both;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

/* Footer */
.app-footer {
    text-align: center;
    padding: 0.5rem 0;
    font-size: 0.7rem;
    color: var(--text-muted);
    margin-top: 1rem;
    border-top: 1px solid var(--border-color);
}

/* Animations */
@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes rotate {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

@keyframes bounce {
    0%, 80%, 100% { transform: scale(0); }
    40% { transform: scale(1); }
}

/* Markdown parsing classes (for response formatting) */
.agent-message p {
    margin-bottom: 0.5rem;
}
.agent-message strong {
    color: #fff;
}
.agent-message ul {
    margin-left: 1.25rem;
    margin-bottom: 0.5rem;
}
.agent-message li {
    margin-bottom: 0.25rem;
}
.agent-message h3 {
    font-size: 0.95rem;
    font-weight: 600;
    margin-top: 0.5rem;
    margin-bottom: 0.25rem;
    color: var(--primary-color);
}


