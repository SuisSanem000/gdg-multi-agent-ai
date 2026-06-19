"""
File Name: src/agent.py
Purpose: Multi-Agent & Routing Orchestrator layer using ChromaDB.
Relation to Project: The core cognitive model of the application. It coordinates Google Gemini model configurations, function calling tools, and context engineering prompts.
Responsibilities:
  - Initializes the Google Cloud Vertex AI client using environment variables.
  - Implements `ContactAnalystAgent` to query ChromaDB contact detail values and run semantic searches.
  - Implements `RelationshipCoachAgent` with context memory facts (read/write) and sub-agent queries.
  - Implements `SmartNotebookOrchestrator` to route queries based on intent.
"""

import os
import vertexai
from vertexai.generative_models import GenerativeModel, Tool, FunctionDeclaration, Part

# =====================================================================
# Helpers
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


# =====================================================================
# Main Agent Classes
# =====================================================================

class ContactAnalystAgent:
    def __init__(self, db_client):
        self.db = db_client
        
        # Define get_contact_details declaration
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

        # Define search_contacts_semantically declaration
        self.search_contacts_declaration = FunctionDeclaration(
            name="search_contacts_semantically",
            description="Searches for contact records semantically using a natural language query. Returns matching contact details.",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "query": {
                        "type": "STRING",
                        "description": "The search query, e.g. 'Yerevan investor' or 'VP of Marketing'.",
                    }
                },
                "required": ["query"],
            }
        )
        self.db_tool = Tool(function_declarations=[self.get_contact_declaration, self.search_contacts_declaration])
        
        self.model = GenerativeModel(
            model_name="gemini-1.5-flash",
            tools=[self.db_tool],
            system_instruction=(
                "You are a Contact Analyst Agent. Your job is to answer questions about contacts using "
                "the 'get_contact_details' and 'search_contacts_semantically' tools. If you are given a specific "
                "contact ID, use 'get_contact_details'. If you are asked a semantic or descriptive question (like "
                "'find the Yerevan investor'), use 'search_contacts_semantically' to locate the correct profile."
            )
        )

    def _execute_db_query(self, contact_id: str) -> str:
        """Executes a search in ChromaDB by contact ID."""
        contacts_col = self.db.get_or_create_collection(name="contacts")
        result = contacts_col.get(ids=[contact_id])
        if result and 'documents' in result and result['documents']:
            return result['documents'][0]
        return f"Contact '{contact_id}' not found in database."

    def _search_contacts_semantically(self, query: str) -> str:
        """Searches ChromaDB semantically using query text embeddings."""
        contacts_col = self.db.get_or_create_collection(name="contacts")
        # ChromaDB automatically embeds the query and compares it with contact documents
        results = contacts_col.query(query_texts=[query], n_results=1)
        if results and 'documents' in results and results['documents'] and results['documents'][0]:
            doc = results['documents'][0][0]
            meta = results['metadatas'][0][0]
            cid = results['ids'][0][0]
            return f"Found Contact: {meta['name']} (ID: {cid}). Details: {doc}"
        return "No matching contacts found."

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
                
            tool_name = function_call.name
            args = function_call.args
            
            if tool_name == "get_contact_details":
                contact_id = args.get("contact_id")
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
            elif tool_name == "search_contacts_semantically":
                query = args.get("query")
                trace.append({
                    "agent": "ContactAnalystAgent",
                    "action": "call_tool",
                    "tool": "search_contacts_semantically",
                    "args": {"query": query}
                })
                
                tool_output = self._search_contacts_semantically(query)
                trace.append({
                    "agent": "ContactAnalystAgent",
                    "action": "tool_output",
                    "tool": "search_contacts_semantically",
                    "output": tool_output
                })
            else:
                break
                
            response = chat.send_message(
                Part.from_function_response(
                    name=tool_name,
                    response={"result": tool_output}
                )
            )
                
        final_text = response.text
        trace.append({
            "agent": "ContactAnalystAgent",
            "action": "final_response",
            "message": final_text
        })
        return final_text


class RelationshipCoachAgent:
    def __init__(self, db_client, analyst_agent):
        self.db = db_client
        self.analyst = analyst_agent
        
        # Tools definitions
        self.query_analyst_declaration = FunctionDeclaration(
            name="query_contact_analyst",
            description="Queries the Contact Analyst agent to retrieve official background details, run semantic searches, or ask specific profile questions.",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "query": {
                        "type": "STRING",
                        "description": "The specific query to send to the Contact Analyst, e.g. 'find the Yerevan investor' or 'What are the details of contact-john?'.",
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
        # Fetch current memories for context injection (Context Engineering)
        from database import get_session_memories
        memories = get_session_memories(self.db, session_id)
        
        memory_str = ""
        if memories:
            memory_str = "\nActive Session Memories (retrieved from database):\n"
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
    def __init__(self, db_client):
        self.db = db_client
        
        # Initialize Vertex AI
        project = os.getenv("GCP_PROJECT_ID", "gdg-agent-sayen-2026")
        location = os.getenv("GCP_LOCATION", "us-central1")
        
        vertexai.init(project=project, location=location)
        print("[Orchestrator] Vertex AI SDK initialized successfully.")

        # Instantiate sub-agents
        self.analyst = ContactAnalystAgent(db_client)
        self.auditor = RelationshipCoachAgent(db_client, self.analyst)

    def run(self, user_input: str, session_id: str = "default", trace: list = None) -> str:
        if trace is None:
            trace = []
            
        lower_input = user_input.lower()
        # Routing logic: if looking for specific contact profiles or semantic lookups, use ContactAnalystAgent.
        # Otherwise, route to RelationshipCoachAgent.
        if "contact-" in lower_input or "profile" in lower_input or "details" in lower_input or "find" in lower_input or "search" in lower_input:
            print(f"[Orchestrator] Routing profile/search query to ContactAnalystAgent")
            return self.analyst.run(user_input, trace=trace)
        else:
            print(f"[Orchestrator] Routing networking/coaching query to RelationshipCoachAgent")
            return self.auditor.run(user_input, session_id=session_id, trace=trace)
