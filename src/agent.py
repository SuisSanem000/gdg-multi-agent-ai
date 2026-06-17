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

