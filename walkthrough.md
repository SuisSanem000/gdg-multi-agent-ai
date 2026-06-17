# Walkthrough: GDG Yerevan AI Workshop Preparation (Expanded Edition)

Here is a detailed walkthrough of the **Multi-Agent and Session Memory Playground** built to prepare you for the workshop on June 20, 2026.

---

## 🛠️ What Was Accomplished

We expanded the project to demonstrate all three key themes of the workshop: Cloud Run deployment, multi-agent orchestration, and context/session memory engineering.

### 1. File Structure Update
```text
gdg-multi-agent-ai/
├── README.md               # Unified roadmap & prep guide
├── requirements.txt        # Package dependencies (Vertex AI, Flask, dotenv, Gunicorn)
├── .env.example            # Environment variables template
├── .env                    # Local environment config
├── Dockerfile              # Docker configuration for Cloud Run
├── walkthrough.md          # Local copy of the walkthrough
└── src/
    ├── __init__.py
    ├── database.py         # SQLite setup: Statutes + Session Memory
    ├── agent.py            # Multi-agent layer: Analyst, Auditor, and Orchestrator
    ├── main.py             # CLI runner script with trace output
    ├── app.py              # Flask app serving static frontend and API endpoints
    └── static/
        ├── index.html      # Premium developer dashboard HTML
        ├── style.css       # Custom glassmorphism dark-mode stylesheet
        └── app.js          # Interactive UI driver (fetch APIs and logs parser)
```

---

## 2. Core Architecture & Concept Walkthrough

### 🗄️ Database & Memory ([src/database.py](file:///h:/Programming/dev/gdg-multi-agent-ai/src/database.py))
- **Statutes Table:** Persists the Corporations Act rules (Sections 181 and 182).
- **Session Memories Table:** A key-value table: `(session_id, key, value)`. This stores persistent facts (e.g. director names, transactions, audit histories) across turns.
- **Context Injection:** When the auditor agent runs, we retrieve all key-value memories for the current `session_id` and inject them directly into the system instructions. This demonstrates **Context Engineering** (Vadim Patsev's session).

### 🤖 Multi-Agent Orchestration ([src/agent.py](file:///h:/Programming/dev/gdg-multi-agent-ai/src/agent.py))
We moved from a single agent to a collaborative multi-agent loop:
1. **LegalAnalystAgent:** Accesses the SQLite database using the `get_statute_definition` function tool to retrieve clauses.
2. **ComplianceAuditorAgent:** Audits business scenarios. Rather than accessing the database directly, it has a tool-as-an-agent called `query_legal_analyst`. When it decides it needs legal sections, it calls this tool, which queries `LegalAnalystAgent`. It also reads/writes facts using the `recall_fact` and `store_fact` memory tools.
3. **LegalAgent (Orchestrator):** Routes direct statutory questions to the Legal Analyst, and complex scenarios or conversational statements to the Compliance Auditor.

---

## 3. Web Dashboard

We built a single-page developer dashboard served directly by the Flask server:
- **Interactive Chat Interface:** Submit scenario audits to the Compliance Auditor.
- **Live Agent Thought Stream:** Displays step-by-step traces of agent interactions, showing exactly when the Auditor calls the Legal Analyst, when SQLite tools execute, and the returned data.
- **SQLite Session Memory Inspector:** Shows a real-time list of key-value pairs stored in the SQLite database for the active session.
- **Cloud Architecture & Prep Guide:** Visual diagram and checklist for the workshop.

---

## ⚡ How to Run the Prep Playground Locally

### 1. Authenticate with Google Cloud
Ensure your local environment has active Vertex AI credentials:
```powershell
gcloud auth application-default login
```

### 2. Configure Environment Variable
In your local [.env](file:///h:/Programming/dev/gdg-multi-agent-ai/.env) file, configure your GCP Project ID:
```env
GCP_PROJECT_ID=your-actual-gcp-project-id
GCP_LOCATION=us-central1
```

### 3. Run the CLI Demo
Execute the CLI testing run which simulates an audit, stores facts in SQLite, and retrieves them in a subsequent query:
```powershell
python src/main.py
```

### 4. Run the Web Dashboard
Start the local web server:
```powershell
python src/app.py
```
Open your browser to [http://127.0.0.1:8080](http://127.0.0.1:8080) to interact with the dashboard.
