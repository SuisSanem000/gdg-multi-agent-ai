import os
from dotenv import load_dotenv
from database import setup_database
from agent import LegalAgent

# Load local environment configuration
load_dotenv()

def main():
    print("==================================================")
    print("GDG Yerevan Workshop - Legal Agent CLI Demo")
    print("==================================================")
    
    # Check if Vertex credentials/project is configured
    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id or project_id == "your-gcp-project-id":
        print("[WARNING] 'GCP_PROJECT_ID' is not configured in .env.")
        print("Please configure it with a valid GCP Project ID before executing Vertex AI calls.")
        print("Continuing initialization (will fail at Vertex AI calls if credentials are missing)...")
        print("--------------------------------------------------")

    print("Setting up local SQLite database...")
    db_conn = setup_database()
    
    print("Initializing Legal Agent...")
    try:
        agent = LegalAgent(db_conn)
        
        # Test Query 1: Triggers SQLite tool lookup
        query_1 = "What does Corporations Act Section 181 state about good faith?"
        agent.run(query_1)
        
        print("--------------------------------------------------")
        
        # Test Query 2: General LLM knowledge (does not trigger database tool)
        query_2 = "Explain briefly what a conflict of interest is in general terms."
        agent.run(query_2)
        
    except Exception as e:
        print(f"\n[ERROR] Failed to run agent: {e}")
        print("Ensure you have authenticated with: gcloud auth application-default login")

    finally:
        db_conn.close()
        print("\nDatabase connection closed.")
        print("==================================================")

if __name__ == "__main__":
    main()
