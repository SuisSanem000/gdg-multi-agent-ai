import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from database import setup_database
from agent import LegalAgent

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize database and agent globally on startup
print("Initializing persistent SQLite database & LegalAgent on startup...")
db_conn = setup_database()
agent = LegalAgent(db_conn)

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "online",
        "message": "Legal Analyst Micro-Agent is active. Submit POST queries to /query."
    })

@app.route("/query", methods=["POST"])
def handle_query():
    data = request.get_json() or {}
    user_input = data.get("query")
    
    if not user_input:
        return jsonify({"error": "Missing required 'query' field in JSON request body."}), 400
    
    try:
        response_text = agent.run(user_input)
        return jsonify({
            "query": user_input,
            "response": response_text
        })
    except Exception as e:
        print(f"Error handling query request: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Cloud Run/standard container runners expect listening on the PORT environment variable
    port = int(os.getenv("PORT", 8080))
    print(f"Starting server on port {port}...")
    app.run(host="0.0.0.0", port=port)
