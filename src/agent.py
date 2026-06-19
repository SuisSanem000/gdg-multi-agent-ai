"""
File Name: src/agent.py
Purpose: Multi-Agent & Routing Orchestrator layer.
Relation to Project: The core cognitive model of the application. It coordinates Google Gemini model configurations, function calling tools, and context engineering prompts.
Responsibilities:
  - Initializes the Google Cloud Vertex AI client (with auto-fallback to Mock AI if credentials are absent).
  - Implements `ContactAnalystAgent` to query SQLite contact detail values.
  - Implements `RelationshipCoachAgent` with context memory facts (read/write) and sub-agent queries.
  - Implements `SmartNotebookOrchestrator` to route queries based on intent.
"""

import os
import vertexai
from vertexai.generative_models import GenerativeModel, Tool, FunctionDeclaration, Part

# =====================================================================
# Mock AI Engine (Ensures the app runs locally without GCP credentials)
# =====================================================================

class MockFunctionCall:
    def __init__(self, name, args):
        self.name = name
        self.args = args

class MockPart:
    def __init__(self, text):
        self.text = text

class MockContent:
    def __init__(self, text):
        self.parts = [MockPart(text)] if text else []

class MockCandidate:
    def __init__(self, function_calls=None, text=None):
        self.function_calls = function_calls or []
        self.content = MockContent(text)

class MockResponse:
    def __init__(self, function_calls=None, text=None):
        self.candidates = [MockCandidate(function_calls, text)]
    
    @property
    def text(self):
        if self.candidates and self.candidates[0].content.parts:
            return self.candidates[0].content.parts[0].text
        return ""

class MockChat:
    def __init__(self, agent_type, db_conn, session_id):
        self.agent_type = agent_type
        self.db = db_conn
        self.session_id = session_id
        self.turn = 0
        self.query_topic = "default"

    def send_message(self, message):
        is_function_response = not isinstance(message, str)
        self.turn += 1
        
        if self.agent_type == "analyst":
            if self.turn == 1:
                msg_lower = str(message).lower()
                contact_id = "contact-john"
                if "jane" in msg_lower:
                    contact_id = "contact-jane"
                return MockResponse(function_calls=[MockFunctionCall("get_contact_details", {"contact_id": contact_id})])
            else:
                msg_str = str(message)
                if "jane" in msg_str.lower() or "contact-jane" in msg_str.lower():
                    return MockResponse(text="Jane Smith is the Managing Partner at Yerevan Ventures. Email: jane@yerevan.vc. Met at GDG Yerevan. Looking to fund AI startups.")
                return MockResponse(text="John Doe is the VP of Marketing at TechCorp. Email: john@techcorp.com. Met at GDG Yerevan AI Workshop. Interested in multi-agent systems.")
                
        elif self.agent_type == "coach":
            if not is_function_response:
                msg_lower = message.lower()
                if "remember" in msg_lower or "recall" in msg_lower:
                    self.query_topic = "recall"
                    return MockResponse(function_calls=[MockFunctionCall("recall_fact", {"key": "contact_name"})])
                else:
                    self.query_topic = "draft"
                    return MockResponse(function_calls=[MockFunctionCall("query_contact_analyst", {"query": "What are the details of contact-john?"})])
            else:
                if self.query_topic == "recall":
                    if self.turn == 2:
                        return MockResponse(function_calls=[MockFunctionCall("recall_fact", {"key": "company_name"})])
                    else:
                        return MockResponse(text="Based on our SQLite session memory, the contact we previously conversed about is John Doe who works at TechCorp.")
                else:
                    if self.turn == 2:
                        return MockResponse(function_calls=[MockFunctionCall("store_fact", {"key": "contact_name", "value": "John Doe"})])
                    elif self.turn == 3:
                        return MockResponse(function_calls=[MockFunctionCall("store_fact", {"key": "company_name", "value": "TechCorp"})])
                    else:
                        return MockResponse(text="Here is your follow-up email template:\n\nSubject: Following up from GDG Yerevan AI Workshop\n\nHi John,\n\nIt was great meeting you at the GDG Yerevan AI Workshop. I'd love to schedule a quick call to discuss how we can integrate multi-agent AI systems into TechCorp's marketing workflows.\n\nBest regards,\nDavid")

class MockGenerativeModel:
    def __init__(self, agent_type, db_conn):
        self.agent_type = agent_type
        self.db = db_conn
        
    def start_chat(self):
        return MockChat(self.agent_type, self.db, "default")


# =====================================================================
# Main Agent Classes
# =====================================================================

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


class ContactAnalystAgent:
    def __init__(self, db_conn, use_mock: bool = False):
        self.db = db_conn
        self.use_mock = use_mock
        
        # Define the Function Tool declaration
        self.get_contact_declaration = FunctionDeclaration(
            name="get_contact_details",
            description="Retrieves the background details, role, and email of a contact using their contact ID.",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "contact_id": {
                        "type": "STRING",
                        "description": 'The unique ID of the contact, e.g., "contact-john" or "contact-jane".',
                    }
                },
                "required": ["contact_id"],
            }
        )
        self.db_tool = Tool(function_declarations=[self.get_contact_declaration])
        
        if self.use_mock:
            self.model = MockGenerativeModel("analyst", db_conn)
        else:
            self.model = GenerativeModel(
                model_name="gemini-1.5-flash",
                tools=[self.db_tool],
                system_instruction=(
                    "You are a Contact Analyst Agent. Your job is to answer questions about contacts using "
                    "the 'get_contact_details' tool. Always use this tool to retrieve exact contact data. "
                    "Be precise and cite the contact details retrieved."
                )
            )

    def _execute_db_query(self, contact_id: str) -> str:
        """Executes a local SQL search based on tool parameters requested by Gemini."""
        cursor = self.db.cursor()
        cursor.execute("SELECT details FROM contacts WHERE id = ?", (contact_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        return f"Contact '{contact_id}' not found in database."

    def run(self, user_input: str, trace: list = None) -> str:
        if trace is None:
            trace = []
            
        trace.append({
            "agent": "ContactAnalystAgent",
            "action": "received_query",
            "message": f"Processing contact query: '{user_input}'"
        })
        
        chat = self.model.start_chat()
        response = chat.send_message(user_input)
        
        while True:
            function_call = _extract_function_call(response)
            if not function_call:
                break
                
            if function_call.name == "get_contact_details":
                contact_id = function_call.args.get("contact_id")
                trace.append({
                    "agent": "ContactAnalystAgent",
                    "action": "call_tool",
                    "tool": "get_contact_details",
                    "args": {"contact_id": contact_id}
                })
                
                tool_output = self._execute_db_query(contact_id)
                trace.append({
                    "agent": "ContactAnalystAgent",
                    "action": "tool_output",
                    "tool": "get_contact_details",
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
            "agent": "ContactAnalystAgent",
            "action": "final_response",
            "message": final_text
        })
        return final_text


class RelationshipCoachAgent:
    def __init__(self, db_conn, analyst_agent, use_mock: bool = False):
        self.db = db_conn
        self.analyst = analyst_agent
        self.use_mock = use_mock
        
        # Tools definitions
        self.query_analyst_declaration = FunctionDeclaration(
            name="query_contact_analyst",
            description="Queries the Contact Analyst agent to retrieve official background details or ask specific profile questions about a contact.",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "query": {
                        "type": "STRING",
                        "description": "The specific query to send to the Contact Analyst, e.g. 'What are the details of contact-john?'.",
                    }
                },
                "required": ["query"],
            }
        )
        
        self.recall_fact_declaration = FunctionDeclaration(
            name="recall_fact",
            description="Retrieves a previously saved relationship fact or context information by its key (e.g., 'user_name', 'last_meeting_date', 'action_item'). Useful for remembering details from earlier in the session.",
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
            description="Saves an important context variable into the session memory to refer to later (e.g. key='user_name', value='David'). Always store key facts you discover during conversation.",
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
        if self.use_mock:
            return MockGenerativeModel("coach", self.db)
            
        # Fetch current SQLite memories for context injection (Context Engineering)
        from database import get_session_memories
        memories = get_session_memories(self.db, session_id)
        
        memory_str = ""
        if memories:
            memory_str = "\nActive Session Memories (retrieved from SQLite):\n"
            for k, v in memories.items():
                memory_str += f"- {k}: {v}\n"
                
        system_instruction = (
            "You are a Relationship Coach Agent. Your job is to help users manage their professional network, "
            "draft follow-up templates, and suggest networking strategies. You must retrieve contact background info "
            "by calling the 'query_contact_analyst' tool. You should also remember key details (like user preferences, "
            "meeting outcomes, or schedules) by storing them in session memory (using 'store_fact') or retrieving them "
            "(using 'recall_fact'). Synthesize a friendly, professional response. Refer to stored memories to personalize replies.\n"
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
            "agent": "RelationshipCoachAgent",
            "action": "received_query",
            "message": f"Relationship coaching query: '{user_input}'"
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
                "agent": "RelationshipCoachAgent",
                "action": "call_tool",
                "tool": tool_name,
                "args": dict(args)
            })
            
            tool_output = ""
            if tool_name == "query_contact_analyst":
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
                "agent": "RelationshipCoachAgent",
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
            "agent": "RelationshipCoachAgent",
            "action": "final_response",
            "message": final_text
        })
        return final_text


class SmartNotebookOrchestrator:
    """Orchestrator class that maintains compatibility while routing requests."""
    def __init__(self, db_conn):
        self.db = db_conn
        
        # Initialize Vertex AI
        project = os.getenv("GCP_PROJECT_ID", "your-gcp-project-id")
        location = os.getenv("GCP_LOCATION", "us-central1")
        
        # Check if we should use Mock AI (auto-fallback if credentials are not configured)
        self.use_mock = os.getenv("MOCK_AI", "false").lower() == "true"
        
        if not self.use_mock:
            try:
                vertexai.init(project=project, location=location)
                print("[Orchestrator] Vertex AI SDK initialized successfully.")
            except Exception as e:
                print(f"[Orchestrator] Failed to initialize Vertex AI SDK: {e}. Falling back to MOCK AI mode.")
                self.use_mock = True

        # Instantiate sub-agents passing the mock configuration
        self.analyst = ContactAnalystAgent(db_conn, self.use_mock)
        self.auditor = RelationshipCoachAgent(db_conn, self.analyst, self.use_mock)

    def run(self, user_input: str, session_id: str = "default", trace: list = None) -> str:
        if trace is None:
            trace = []
            
        lower_input = user_input.lower()
        # Routing logic: if looking for specific contact profiles, use ContactAnalystAgent. Otherwise, use RelationshipCoachAgent.
        if "contact-" in lower_input or "profile" in lower_input or "contact details" in lower_input:
            print(f"[Orchestrator] Routing direct profile query to ContactAnalystAgent")
            return self.analyst.run(user_input, trace=trace)
        else:
            print(f"[Orchestrator] Routing networking/coaching query to RelationshipCoachAgent")
            return self.auditor.run(user_input, session_id=session_id, trace=trace)
