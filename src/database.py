"""
File Name: src/database.py
Purpose: Database setup and session memory operations using ChromaDB.
Relation to Project: The core vector database persistence layer for seeded contacts and relationship facts.
Responsibilities:
  - Seeds the ChromaDB `contacts` collection with initial contact records.
  - Implements session memory operations using metadata filtering.
"""

import chromadb

def setup_database():
    """Initializes an in-memory ephemeral ChromaDB client and seeds default contacts."""
    # EphemeralClient runs entirely in-memory (resets on application restart, no disk writes needed)
    client = chromadb.EphemeralClient()
    
    # Setup contacts collection
    contacts_col = client.get_or_create_collection(name="contacts")
    
    # Seeding contacts dataset
    contacts_data = [
        {
            "id": "contact-john",
            "document": "Role: VP of Marketing at TechCorp. Email: john@techcorp.com. Background: Met at GDG Yerevan AI Workshop. Interested in integrating multi-agent AI systems into marketing workflows.",
            "metadata": {"name": "John Doe"}
        },
        {
            "id": "contact-jane",
            "document": "Role: Managing Partner at Yerevan Ventures. Email: jane@yerevan.vc. Background: Looking to fund pre-seed AI startups in Armenia. Prefers communication via Telegram.",
            "metadata": {"name": "Jane Smith"}
        }
    ]
    
    contacts_col.add(
        ids=[c["id"] for c in contacts_data],
        documents=[c["document"] for c in contacts_data],
        metadatas=[c["metadata"] for c in contacts_data]
    )
    
    # Ensure memories collection is initialized
    client.get_or_create_collection(name="session_memories")
    
    return client

def save_session_memory(client, session_id: str, key: str, value: str):
    """Saves or updates a fact in ChromaDB session memories."""
    memories_col = client.get_or_create_collection(name="session_memories")
    mem_id = f"{session_id}_{key.strip().lower()}"
    
    memories_col.upsert(
        ids=[mem_id],
        documents=[value.strip()],
        metadatas=[{
            "session_id": session_id,
            "key": key.strip().lower(),
            "value": value.strip()
        }]
    )

def get_session_memories(client, session_id: str) -> dict:
    """Retrieves all memory facts stored for a session as a key-value dictionary."""
    memories_col = client.get_or_create_collection(name="session_memories")
    
    # Filter memories by session_id metadata field
    results = memories_col.get(where={"session_id": session_id})
    memories = {}
    
    if results and 'metadatas' in results and results['metadatas']:
        for meta in results['metadatas']:
            if meta:
                memories[meta['key']] = meta['value']
                
    return memories

def clear_session_memories(client, session_id: str):
    """Deletes all memory facts for a session."""
    memories_col = client.get_or_create_collection(name="session_memories")
    memories_col.delete(where={"session_id": session_id})
