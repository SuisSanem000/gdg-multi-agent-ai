"""
File Name: src/main.py
Purpose: CLI Runner and Developer Testing Script.
Relation to Project: Standalone developer test script verifying the multi-agent orchestration, tool usage, routing, and SQLite session memory loops in the console terminal.
Responsibilities:
  - Reads local environment credentials.
  - Launches mock database and orchestrator instances.
  - Executes sequential test queries simulating profile retrieval and email drafting tasks.
  - Prints the formatted agent thought traces to verify correct operation.
"""

import os
import sys
from dotenv import load_dotenv
from database import setup_database, get_session_memories
from agent import SmartNotebookOrchestrator

# Load local environment configuration
load_dotenv()

def main():
    # Force UTF-8 encoding on standard output for Windows command prompts printing emojis
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
    print("==================================================")
    print("GDG Yerevan Workshop - Smart Contact Notebook Demo")
    print("==================================================")
    
    # Check if Vertex credentials/project is configured
    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id or project_id == "your-gcp-project-id":
        print("[WARNING] 'GCP_PROJECT_ID' is not configured in .env.")
        print("Please configure it with a valid GCP Project ID before executing Vertex AI calls.")
        print("Continuing initialization (will fail at Vertex AI calls if credentials are missing)...")
        print("--------------------------------------------------")

    print("Setting up local SQLite database with Contacts...")
    db_conn = setup_database()
    
    print("Initializing Multi-Agent System (SmartNotebookOrchestrator)...")
    try:
        agent = SmartNotebookOrchestrator(db_conn)
        session_id = "cli-test-session"
        
        # Test Query 1: Relationship Coaching & SQLite Memory Writing
        query_1 = "Draft a short follow-up email for a new contact named John Doe who works at TechCorp."
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
        
        print(f"\n--- Final Coach Answer ---\n{response_1}")
        
        print("\n--------------------------------------------------")
        
        # Inspect SQLite memories directly to prove it was saved in SQLite
        mems = get_session_memories(db_conn, session_id)
        print(f"SQLite Saved Memories for session '{session_id}':")
        for k, v in mems.items():
            print(f"  - {k}: {v}")
            
        print("--------------------------------------------------")
        
        # Test Query 2: Retrieve fact from SQLite Memory
        query_2 = "What was the name of the contact we just drafted an email for, and what company do they work at?"
        print(f"\n>>> Running Query 2: {query_2}")
        
        trace_2 = []
        response_2 = agent.run(query_2, session_id=session_id, trace=trace_2)
        print(f"\n--- Final Coach Answer ---\n{response_2}")
        
        print("--------------------------------------------------")
        
        # Test Query 3: Direct Profile lookup (triggers Routing to ContactAnalystAgent)
        query_3 = "Get details for contact-jane"
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
