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
        # We check both candidate.function_calls and content.parts[0].function_call for compatibility
        function_call = None
        try:
            candidates = response.candidates
            if candidates and len(candidates) > 0:
                candidate = candidates[0]
                # Try direct function_calls list
                if hasattr(candidate, 'function_calls') and candidate.function_calls:
                    function_call = candidate.function_calls[0]
                # Try parts structure
                elif hasattr(candidate, 'content') and candidate.content.parts:
                    part = candidate.content.parts[0]
                    if hasattr(part, 'function_call') and part.function_call:
                        function_call = part.function_call
        except Exception as e:
            print(f"DEBUG: Error parsing function calls: {e}")

        if function_call:
            print(f"🤖 Agent Decided to Call Tool: {function_call.name}")
            
            # Extract arguments and invoke local function
            # Some SDKs return args as a Map-like object, get() is safe
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
