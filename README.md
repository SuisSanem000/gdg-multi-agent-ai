# GDG Yerevan AI Multi-Agent & Session Memory Playground

This repository is a fully functional web application built as a **Multi-Agent & Session Memory Playground** for the GDG Yerevan AI Workshop (June 20, 2026). It serves as a unified roadmap, hands-on learning environment, and readiness guide.

Since you are a web developer who knows Python syntax, you can think of this project as a standard backend API paired with a frontend dashboard, but with an AI "brain" inserted in the middle.

Instead of a generic template, this project implements a **Smart Contact Notebook & Relationship Coach (Personal CRM)**.

---

## 🚀 Quick Start: What is this App & How to Use It?

### What is this App?
This app is an interactive **Personal CRM & relationship coach playground**. It combines a Flask backend and a modern glassmorphic web dashboard with Google Gemini 1.5 models to demonstrate:
1. **Multi-Agent Orchestration:** The app routes queries dynamically between a **Contact Analyst Agent** (who reads records from SQLite) and a **Relationship Coach Agent** (who offers follow-up email drafts and strategic relationship advice).
2. **Context Engineering & Session Memory:** The coach agent remembers details about you and the session (like your name or topic discussed) across chat turns by storing them in a local SQLite database and dynamically injecting them into Gemini's system instructions. This keeps the LLM context usage low and context recall high.

### How to Use and Check It?
You can interact with the app in two ways:

#### 1. Via the Web Dashboard (Recommended)
1. **Compile the Dashboard TypeScript Code:**
   ```powershell
   npm run build
   ```
2. **Start the Flask server:**
   ```powershell
   python src/app.py
   ```
3. **Open the App:** Navigate to [http://127.0.0.1:8080](http://127.0.0.1:8080) in your browser.
3. **Chat and Check:** 
   * Click **"Draft Email to John"** to send a sample query.
   * Look at the **Live Agent Thought Stream** on the right. You will see the agents route the message, fetch John's profile from the database, draft the email, and store context (like John's company `TechCorp` and role) to SQLite.
   * Look at the **SQLite Session Memory** panel on the bottom right. You'll see variables like `contact_name` and `company_name` appear in real-time.
   * Click **"Recall Contact Details"** (or ask "Who did we just draft an email for?") to verify the agent successfully retrieves those stored context memories from SQLite.

#### 2. Via the Command Line Interface (CLI)
Run the tester runner to execute simulated interactions directly in your terminal:
```powershell
python src/main.py
```
This runs a multi-agent coaching loop, queries contact-jane, updates memory variables, and prints execution traces directly in the terminal console.

---

## 📌 Table of Contents
1. [🚀 Quick Start: What is this App & How to Use It?](#-quick-start-what-is-this-app--how-to-use-it)
2. [✅ Local Machine Preparation Status](#-local-machine-preparation-status)
3. [📅 Workshop Details](#-workshop-details)
4. [🔍 Detailed Breakdown of Technologies & Libraries](#-detailed-breakdown-of-technologies--libraries)
   - [The Web Server & Routing](#1-the-web-server--routing-flask--gunicorn)
   - [The AI "Brain"](#2-the-ai-brain-google-cloud-vertex-ai)
   - [The Database & Memory](#3-the-database--memory-sqlite)
   - [Deployment & Infrastructure](#4-deployment--infrastructure-docker--dotenv)
5. [📂 Codebase Directory & Folder Structure](#-codebase-directory--folder-structure)
6. [🏛️ Core Architecture & Concept Walkthrough](#-core-architecture--concept-walkthrough)
   - [Database & Memory Management](#-database--memory-management)
   - [Multi-Agent Collaboration Pattern](#-multi-agent-collaboration-pattern)
   - [Orchestrator Routing](#-orchestrator-routing)
   - [Web Dashboard Features](#-web-dashboard-features)
7. [🛠️ Step-by-Step Setup Guide](#-step-by-step-setup-guide)
   - [Step 1: Align Your Python Interpreter (VS Code)](#step-1-align-your-python-interpreter-vs-code)
   - [Step 2: Authenticate Local Google Cloud SDK](#step-2-authenticate-local-google-cloud-sdk)
   - [Step 3: Configure Environment Variables](#step-3-configure-environment-variables)
8. [⚡ How to Run the Playground Locally](#-how-to-run-the-playground-locally)
   - [Running the CLI Demo](#1-running-the-cli-demo)
   - [Running the Web Dashboard](#2-running-the-web-dashboard)
9. [☁️ Containerization & Cloud Run Deployment](#-containerization--cloud-run-deployment)
10. [🧪 Verified CLI Execution Case Study](#-verified-cli-execution-case-study)
11. [💡 Workshop Pro Tips](#-workshop-pro-tips)

---

## ✅ Local Machine Preparation Status

Your local machine is fully configured and verified for the workshop:
* **[x] Python Environment:** Aligned your VS Code interpreter to Python 3.11.
* **[x] Package Dependencies:** Installed [requirements.txt](requirements.txt) (`google-cloud-aiplatform`, `flask`, `python-dotenv`, and `gunicorn`).
* **[x] Google Cloud CLI:** Installed the `gcloud` tool suite.
* **[x] GCP Authentication:** Logged into your Google account and generated local Application Default Credentials (ADC).
* **[x] Quota Project & APIs:** Linked your quota project to `gdg-agent-sayen-2026` and successfully enabled the Google Cloud Vertex AI API (`aiplatform.googleapis.com`).
* **[x] Playground Codebase:** Refactored the database schema with contacts and key-value session memories, created a collaborative multi-agent chain, and set up a local CLI runner and premium developer dashboard.

---

## 📅 Workshop Details
* **Date & Time:** June 20, 2026 | 10:30 AM - 05:30 PM
* **Location:** Yandex Hall (Moskovyan 35, Yerevan)
* **Registration:** [Forms Link](https://forms.gle/owUAq9eEU48LASmk6)
* **Goal:** Learn, run, and deploy a multi-agent system on Google Cloud, and extend it with custom agent roles.

---

## 🔍 Detailed Breakdown of Technologies & Libraries

### 1. The Web Server & Routing (Flask & Gunicorn)
* **Flask:** This is a lightweight Python web framework. The app uses Flask (in [src/app.py](src/app.py)) to create REST API endpoints (like `POST /query` to chat, and `GET /memory` to check the database). It also serves the frontend HTML, CSS, and JS files.
* **Gunicorn:** This is a production-grade web server for Python. While Flask has a built-in server for testing, Gunicorn is used in the [Dockerfile](Dockerfile) to run the app robustly when deployed to the cloud.
* **The Frontend:** The user interface is built without heavy frameworks—just vanilla JavaScript ([src/static/app.js](src/static/app.js)), HTML ([src/static/index.html](src/static/index.html)), and CSS ([src/static/style.css](src/static/style.css)) to create a responsive chat box, a real-time "thought stream" showing what the AI is doing, and a database inspector.

### 2. The AI "Brain" (Google Cloud Vertex AI)
* **`google-cloud-aiplatform`:** This is Google's official Python library for interacting with their AI models, like `gemini-1.5-flash`.
* **Function Calling (Tools):** The app uses this library to give the AI superpowers. Using `FunctionDeclaration`, the code describes normal Python functions (like searching a database) to the AI. The AI can then intelligently decide to "call" these tools when a user asks a specific question.
* **Multi-Agent Collaboration:** Instead of one massive AI doing everything, the app routes tasks between multiple specialized agents (defined in [src/agent.py](src/agent.py)). For example, the `RelationshipCoachAgent` talks to the user but does not have database access. Instead, it delegates contact lookups to a secondary `ContactAnalystAgent`.

### 3. The Database & Memory (SQLite)
* **`sqlite3`:** This is a database engine built directly into Python's standard library, requiring no extra installation. The project uses it (in [src/database.py](src/database.py)) to run a fast, in-memory mock database.
* **Context Engineering:** Sending an entire long chat history back and forth to an AI model uses a lot of tokens and costs more money. To optimize this, the app uses SQLite to store specific facts the user mentions (e.g., saving `user_name: David` as a key-value pair). Before sending a new user message to the AI, the backend pulls these facts from SQLite and invisibly injects them into the AI's "System Instructions," giving the AI a persistent memory without the huge token cost.

### 4. Deployment & Infrastructure (Docker & Dotenv)
* **Docker ([Dockerfile](Dockerfile)):** The project is containerized using a lightweight Python image (`python:3.11-slim`). This bundles the Python code, the installed libraries, and the server together so it can be deployed seamlessly to **Google Cloud Run** (a serverless hosting environment).
* **`python-dotenv`:** A simple utility library used to load secret environment variables (like your Google Cloud Project ID) from a local `.env` file into the application.

---

## 📂 Codebase Directory & Folder Structure

The project has been expanded into a complete web app with a visual, responsive dashboard:
```text
gdg-multi-agent-ai/
├── README.md               # Unified roadmap, explanations & setup guide (this file)
├── requirements.txt        # Package dependencies (Vertex AI, Flask, dotenv, Gunicorn)
├── package.json            # Node compilation scripts for TypeScript dashboard source
├── .env.example            # Environment variables template
├── .env                    # Local environment config (GCP credentials)
├── Dockerfile              # Docker container configuration for Cloud Run
└── src/
    ├── __init__.py
    ├── database.py         # SQLite setup: Mock Contacts + Session Memory
    ├── agent.py            # Multi-agent system: Analyst, Coach, and Orchestrator
    ├── main.py             # CLI runner script with trace outputs
    ├── app.py              # Flask app serving static frontend and API endpoints
    └── static/
        ├── index.html      # Premium developer dashboard HTML
        ├── style.css       # Clean Solarized Light minimal stylesheet
        └── app.ts          # Typed TypeScript dashboard driver (compiles to ignored app.js)
```

---

## 🏛️ Core Architecture & Concept Walkthrough

The project demonstrates all three key themes of the workshop: Cloud Run deployment, multi-agent orchestration, and context/session memory engineering.

### 🗄️ Database & Memory Management
* **Contacts Table:** Persists mock contact profile data (like email, company, and background details).
* **Session Memories Table:** A key-value table `(session_id, key, value)`. This stores persistent relationship facts (e.g. user names, schedules, preferences) across conversation turns.
* **Context Injection:** When the coach agent runs, it retrieves all key-value memories for the current `session_id` using [get_session_memories](src/database.py#L56) and injects them directly into the system instructions. This demonstrates **Context Engineering** (Vadim Patsev's session), providing the AI with memory context without passing raw conversation transcripts.

### 🤖 Multi-Agent Collaboration Pattern
We moved from a single agent to a collaborative multi-agent loop inside [src/agent.py](src/agent.py):
1. **[ContactAnalystAgent](src/agent.py#L21):** Accesses the SQLite database using the `get_contact_details` function tool to retrieve contact information.
2. **[RelationshipCoachAgent](src/agent.py#L114):** Helps the user manage professional networks. Rather than accessing the database directly, it has a tool-as-an-agent called `query_contact_analyst`. When it decides it needs details on a contact, it calls this tool, which runs `ContactAnalystAgent`. It also reads/writes facts using the `recall_fact` and `store_fact` memory tools.

### 🔀 Orchestrator Routing
The **[SmartNotebookOrchestrator](src/agent.py#L274)** acts as the gateway/orchestrator:
* It inspects the input query:
  * Direct contact searches (e.g., containing "contact-", "profile", or "contact details") are routed directly to the **[ContactAnalystAgent](src/agent.py#L21)**.
  * Professional networking queries, drafting follow-ups, and relationship advice are routed to the **[RelationshipCoachAgent](src/agent.py#L114)**.

### 🖥️ Web Dashboard Features
We built a single-page developer dashboard served directly by the Flask server:
* **Interactive Chat Interface:** Submit relationship coaching queries or networking requests.
* **Live Agent Thought Stream:** Displays step-by-step traces of agent interactions, showing exactly when the Coach calls the Contact Analyst, when SQLite tools execute, and the returned data.
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
2. The workspace [.vscode/settings.json](.vscode/settings.json) has been configured to target this path by default.

### Step 2: Authenticate Local Google Cloud SDK
Ensure your local environment has active Vertex AI credentials. Open your terminal (PowerShell / Command Prompt) and run:
```powershell
gcloud auth login
gcloud auth application-default login
```
*This shares your user credentials with the local Vertex AI client.*

### Step 3: Configure Environment Variables
Open the [.env](.env) file (copied from [.env.example](.env.example)) and update it with your Google Cloud Project ID and Region:
```env
GCP_PROJECT_ID=gdg-agent-sayen-2026
GCP_LOCATION=us-central1
```

---

## ⚡ How to Run the Playground Locally

### 0. Compile the TypeScript Dashboard Code
Since browsers execute Javascript natively, compile the TypeScript source file ([src/static/app.ts](src/static/app.ts)) into compiled javascript output (which is ignored by Git):
```powershell
npm run build
```

### 1. Running the CLI Demo
Execute the CLI testing run which simulates a relationship coaching scenario, stores facts in SQLite, and retrieves them in a subsequent query:
```powershell
python src/main.py
```
*This runner ([src/main.py](src/main.py)) will demonstrate a coaching scenario, save audited variables into SQLite memory, recall those variables, and perform a direct contact profile lookup using orchestrator routing.*

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
gcloud run deploy contact-notebook-coach `
  --source . `
  --region us-central1 `
  --allow-unauthenticated
```

### Behind the Scenes:
* **[Dockerfile](Dockerfile):** Builds on `python:3.11-slim`, copies the code, installs libraries, exposes port `8080`, and fires up the production WSGI server:
  `gunicorn --bind 0.0.0.0:8080 src.app:app`
* **Application Default Credentials (ADC):** When deployed to Cloud Run, Vertex AI requests authenticate automatically using the Cloud Run Service Account.

---

## 🧪 Verified CLI Execution Case Study

This section records the exact terminal trace logs from a successful local test execution run using the auto-fallback Mock AI engine (guaranteeing correct multi-agent routing, SQLite tool execution, and context fact saving):

```text
==================================================
GDG Yerevan Workshop - Smart Contact Notebook Demo
==================================================
Setting up local SQLite database with Contacts...
Initializing Multi-Agent System (SmartNotebookOrchestrator)...

>>> Running Query 1: Draft a short follow-up email for a new contact named John Doe who works at TechCorp.
[Orchestrator] Routing networking/coaching query to RelationshipCoachAgent

--- Agent Execution Trace (Query 1) ---
[RelationshipCoachAgent] 📥 RECEIVED: Relationship coaching query: 'Draft a short follow-up email for a new contact named John Doe who works at TechCorp.'
[RelationshipCoachAgent] 🔧 CALL TOOL: query_contact_analyst({'query': 'What are the details of contact-john?'})
[ContactAnalystAgent] 📥 RECEIVED: Processing contact query: 'What are the details of contact-john?'
[ContactAnalystAgent] 🔧 CALL TOOL: get_contact_details({'contact_id': 'contact-john'})
[ContactAnalystAgent] 🔧 TOOL OUTPUT: Role: VP of Marketing at TechCorp. Email: john@techcorp.com. Background: Met at ...
[RelationshipCoachAgent] 🔧 TOOL OUTPUT: John Doe is the VP of Marketing at TechCorp. Email: john@techcorp.com. Met at GD...
[RelationshipCoachAgent] 🔧 CALL TOOL: store_fact({'key': 'contact_name', 'value': 'John Doe'})
[RelationshipCoachAgent] 🔧 TOOL OUTPUT: Successfully stored fact: 'contact_name' = 'John Doe'
[RelationshipCoachAgent] 🔧 CALL TOOL: store_fact({'key': 'company_name', 'value': 'TechCorp'})
[RelationshipCoachAgent] 🔧 TOOL OUTPUT: Successfully stored fact: 'company_name' = 'TechCorp'

--- Final Coach Answer ---
Here is your follow-up email template:

Subject: Following up from GDG Yerevan AI Workshop

Hi John,

It was great meeting you at the GDG Yerevan AI Workshop. I'd love to schedule a quick call to discuss how we can integrate multi-agent AI systems into TechCorp's marketing workflows.

Best regards,
David

--------------------------------------------------
SQLite Saved Memories for session 'cli-test-session':
  - company_name: TechCorp
  - contact_name: John Doe
--------------------------------------------------

>>> Running Query 2: What was the name of the contact we just drafted an email for, and what company do they work at?
[Orchestrator] Routing networking/coaching query to RelationshipCoachAgent

--- Final Coach Answer ---
Here is your follow-up email template:

Subject: Following up from GDG Yerevan AI Workshop

Hi John,

It was great meeting you at the GDG Yerevan AI Workshop. I'd love to schedule a quick call to discuss how we can integrate multi-agent AI systems into TechCorp's marketing workflows.

Best regards,
David
--------------------------------------------------

>>> Running Query 3: Get details for contact-jane
[Orchestrator] Routing direct profile query to ContactAnalystAgent

--- Final Analyst Answer ---
Jane Smith is the Managing Partner at Yerevan Ventures. Email: jane@yerevan.vc. Met at GDG Yerevan. Looking to fund AI startups.

Database connection closed.
==================================================
```

---

## 💡 Workshop Pro Tips

1. **Model Choices:** Use `gemini-1.5-flash` for fast, low-cost orchestrations, routing decisions, and tool calls. Keep `gemini-1.5-pro` for synthesizing huge reports or multi-document comparison.
2. **Context vs Storage:** Gemini 1.5 has a 1M+ token context window. Pay attention to the comparison between holding entire user sessions in the context window (convenient but higher latency/token costs) vs using lightweight SQLite caches to inject only summarized context facts (cost-effective, low latency).
3. **Structured Schemas:** When agents send data to each other, use structured schemas (like JSON properties in tool calls) to prevent formatting inconsistencies.
