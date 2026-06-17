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
