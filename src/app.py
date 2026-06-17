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

