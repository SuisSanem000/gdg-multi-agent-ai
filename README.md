# GDG Yerevan AI Multi-Agent Workshop (June 20, 2026)
## Pre-Workshop Preparation & Roadmap (Python Edition)

Welcome to the preparation hub for the **GDG Yerevan AI Multi-Agent Workshop** at Yandex Hall Yerevan!

This guide is optimized for developers with strong **Web Backend Engineering** backgrounds who are looking to build multi-agent orchestration systems on **Google Cloud & Vertex AI** using **Python**. 

Rather than walking through basic Python syntax, this guide focuses on setting up cloud credentials, orchestrating agent tool loops using the Vertex AI SDK, managing lightweight state, and preparing for deployment.

---

## 📅 Workshop Details
* **Date & Time:** June 20, 2026 | 10:30 AM - 05:30 PM
* **Location:** Yandex Hall (Moskovyan 35, Yerevan)
* **Registration:** [Forms Link](https://forms.gle/owUAq9eEU48LASmk6)
* **Goal:** Build, configure, and deploy a multi-agent system on Google Cloud, and extend it with custom agent roles.

### 👥 Speakers & Mentors
* **Armen Vardanyan** (GDE Angular) — *Agentic Architectures & Orchestration*
* **Vadim Patsev** (Yandex Armenia) — *Agent Memory & Context Engineering*
* **Rohan Singh** (GDE Cloud) — *Cloud & Infrastructure for AI Systems*

---

## ⏰ Agenda

| Time | Session | Description |
| :--- | :--- | :--- |
| **10:30 - 11:00** | 📝 Registration & Coffee | Check-in & networking |
| **11:00 - 11:10** | 👋 Opening | Intro to the workshop, project goals, architecture overview |
| **11:10 - 11:50** | ☁️ Cloud & Infrastructure (Rohan) | Google Cloud for agents, Cloud Run, Cloud Functions, and Vertex AI basics |
| **11:50 - 12:30** | 🤖 Building the Agentic Layer (Armen) | Agent design patterns, tool calling, multi-agent communication loops |
| **12:30 - 13:00** | 🧠 Memory & Context (Vadim) | Memory trade-offs, RAG vs. lightweight storage (SQLite, Redis) |
| **13:00 - 13:20** | 🛠 Hands-on Kickoff | Starter repo walkthrough, team formation, cloud setup |
| **13:20 - 16:30** | 💻 Hands-on Coding Session | Build, configure, and deploy a multi-agent system |
| **16:30 - 17:30** | 🚀 Wrap-up & Demos | Participant presentations, Q&A, and closing remarks |

*Note: Pizza and coffee will be available continuously during the coding session.*

---

## 🚀 Step 1: GCP & Vertex AI SDK Setup (15 Minutes)

To save time during the workshop, verify your local GCP configuration beforehand:

1. **Install the Google Cloud CLI (gcloud):** Verify it is in your system PATH.
2. **Authenticate Local SDK:**
   ```powershell
   gcloud auth login
   gcloud auth application-default login
   ```
3. **Configure Project & Services:**
   Create a Google Cloud Project or select a sandbox project, then enable Vertex AI and Cloud Run services:
   ```powershell
   gcloud config set project YOUR_PROJECT_ID
   gcloud services enable aiplatform.googleapis.com run.googleapis.com
   ```

---

## 💻 Step 2: "The Legal Analyst" Python Micro-Agent Project

We've initialized a structured Python project at the root. It demonstrates how to build a **Legal Analyst Agent** that queries a local SQLite database of corporations regulations via **Vertex AI Tool Calling**.

### Project Structure
```text
gdg-multi-agent-ai/
├── README.md               # This unified guide
├── requirements.txt        # Package dependencies
├── .env.example            # Environment template
├── Dockerfile              # Docker configuration for Cloud Run
└── src/
    ├── __init__.py
    ├── database.py         # SQLite memory database initialization & data seeding
    ├── agent.py            # LegalAgent core class using Vertex AI & Tool definitions
    ├── main.py             # CLI application entrypoint for local execution
    └── app.py              # Lightweight Flask wrapper for API deployment
```

### 1. Project Dependencies (`requirements.txt`)
We use the official Google Cloud Vertex AI Python SDK, `python-dotenv` for config, and `Flask` with `gunicorn` for deployment:
```text
google-cloud-aiplatform
python-dotenv
flask
gunicorn
```

### 2. Local Database Simulation (`src/database.py`)
Simulates looking up statutory definitions (specifically, the Australian Corporations Act Sections 181 & 182) from a relational DB.
```python
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
    
    # Seeding
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
```

### 3. Agent & Tool Calling (`src/agent.py`)
This module initializes the Vertex AI client and registers the SQLite lookup function as a Tool that Gemini can call.
```python
import os
import vertexai
from vertexai.generative_models import GenerativeModel, Tool, FunctionDeclaration, Part

class LegalAgent:
    def __init__(self, db_conn):
        self.db = db_conn
        
        # Initialize Vertex AI
        project = os.getenv("GCP_PROJECT_ID", "your-gcp-project-id")
        location = os.getenv("GCP_LOCATION", "us-central1")
        vertexai.init(project=project, location=location)

        # 1. Define the Function Tool declaration
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

        # 2. Package it into a Tool configuration
        self.db_tool = Tool(function_declarations=[self.get_statute_declaration])

        # 3. Create GenerativeModel instance with tools registered
        self.model = GenerativeModel(
            model_name="gemini-1.5-flash",
            tools=[self.db_tool]
        )

    def _execute_db_query(self, statute_id: str) -> str:
        """Executes a local SQL search based on tool parameters requested by Gemini."""
        cursor = self.db.cursor()
        cursor.execute("SELECT clause FROM statutes WHERE id = ?", (statute_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        return "Statute not found in database."

    def run(self, user_input: str) -> str:
        print(f"\n[User Query]: {user_input}")
        
        # Use stateful chat interface to manage messaging flows seamlessly
        chat = self.model.start_chat()
        response = chat.send_message(user_input)
        
        # Inspect if the model decided to request tool usage
        if response.candidates[0].function_calls:
            function_call = response.candidates[0].function_calls[0]
            print(f"🤖 Agent Decided to Call Tool: {function_call.name}")
            
            # Extract arguments and invoke local function
            statute_id = function_call.args.get("statute_id")
            tool_output = self._execute_db_query(statute_id)
            print(f"🔧 Tool Executed Locally, Output: \"{tool_output}\"")
            
            # Send the tool execution result back to the model
            follow_up = chat.send_message(
                Part.from_function_response(
                    name=function_call.name,
                    response={"result": tool_output}
                )
            )
            final_text = follow_up.text
            print(f"🤖 Agent Final Answer:\n{final_text}")
            return final_text
        else:
            final_text = response.text
            print(f"🤖 Agent Final Answer:\n{final_text}")
            return final_text
```

### 4. CLI Execution (`src/main.py`)
Run queries directly from the command line:
```python
import os
from dotenv import load_dotenv
from database import setup_database
from agent import LegalAgent

load_dotenv()

def main():
    print("Setting up local SQLite database...")
    db_conn = setup_database()
    
    print("Initializing Legal Agent (Vertex AI)...")
    agent = LegalAgent(db_conn)
    
    # 1. Run a query that triggers the database tool
    agent.run("What does Corporations Act Section 181 state about good faith?")
    
    # 2. Run a query that requires general model knowledge
    agent.run("Explain briefly what a conflict of interest is in general terms.")

if __name__ == "__main__":
    main()
```

### 5. Flask Web Server Wrapper (`src/app.py`)
To deploy to Google Cloud Run, expose a lightweight POST API.
```python
import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from database import setup_database
from agent import LegalAgent

load_dotenv()

app = Flask(__name__)

# Initialize database and agent at start
db_conn = setup_database()
agent = LegalAgent(db_conn)

@app.route("/query", methods=["POST"])
def handle_query():
    data = request.get_json() or {}
    user_input = data.get("query")
    if not user_input:
        return jsonify({"error": "Missing 'query' parameter"}), 400
    
    try:
        response_text = agent.run(user_input)
        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Cloud Run expects the application to listen on PORT environment variable
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
```

---

## ☁️ Step 3: Containerization & Cloud Run Deployment

Cloud Run relies on Docker to build and scale your container.

### 1. Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ src/

# Run via high-performance production WSGI server
EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "src.app:app"]
```

### 2. Cloud Run Deployment Command
Run the single command below to package, containerize, and deploy the agent directly to Cloud Run:
```powershell
gcloud run deploy legal-analyst-agent `
  --source . `
  --region us-central1 `
  --allow-unauthenticated
```

---

## 💡 Workshop Pro Tips
1. **Design Clean Inter-Agent Protocols:** Focus on standard data exchanges (e.g., JSON schemas) rather than raw text messaging when coordinating between multiple agents.
2. **Model Tier Selection:** Use `gemini-1.5-flash` for high-speed subtasks, routing, and database queries. Save `gemini-1.5-pro` for synthesis or highly complex reasoning tasks.
3. **Evaluate Context Window vs. Databases:** Since Gemini 1.5 supports massive context lengths, discuss with Vadim Patsev about the latency and cost structures when holding user sessions in the context window compared to standard external caches.
