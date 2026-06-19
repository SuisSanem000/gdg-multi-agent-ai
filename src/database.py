"""
File Name: src/database.py
Purpose: Database setup and session memory operations.
Relation to Project: The core data persistence layer for seeded contacts and relationship facts. It stores mock contacts and remembers relationship preferences across conversational turns.
Responsibilities:
  - Seeds the SQLite `contacts` table with mock contact details.
  - Creates the `session_memories` key-value table.
  - Saves, retrieves, and clears session memory variables for context engineering.
"""

import sqlite3

def setup_database():
    """Initializes an in-memory SQLite database and seeds it with mock contacts."""
    # We use an in-memory database for local test runs
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id TEXT PRIMARY KEY,
            name TEXT,
            details TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS session_memories (
            session_id TEXT,
            key TEXT,
            value TEXT,
            PRIMARY KEY (session_id, key)
        )
    ''')
    
    # Seeding mock contacts for the Smart Contact Notebook
    contacts_data = [
        (
            'contact-john',
            'John Doe',
            'Role: VP of Marketing at TechCorp. Email: john@techcorp.com. Background: Met at GDG Yerevan AI Workshop. Interested in integrating multi-agent AI systems into marketing workflows.'
        ),
        (
            'contact-jane',
            'Jane Smith',
            'Role: Managing Partner at Yerevan Ventures. Email: jane@yerevan.vc. Background: Looking to fund pre-seed AI startups in Armenia. Prefers communication via Telegram.'
        )
    ]
    
    cursor.executemany(
        'INSERT OR REPLACE INTO contacts (id, name, details) VALUES (?, ?, ?)',
        contacts_data
    )
    conn.commit()
    return conn

def save_session_memory(conn, session_id: str, key: str, value: str):
    """Saves or updates a fact in SQLite session memories."""
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO session_memories (session_id, key, value)
        VALUES (?, ?, ?)
    ''', (session_id, key.strip().lower(), value.strip()))
    conn.commit()

def get_session_memories(conn, session_id: str) -> dict:
    """Retrieves all memory facts stored for a session as a key-value dictionary."""
    cursor = conn.cursor()
    cursor.execute('SELECT key, value FROM session_memories WHERE session_id = ?', (session_id,))
    rows = cursor.fetchall()
    return {row[0]: row[1] for row in rows}

def clear_session_memories(conn, session_id: str):
    """Deletes all memory facts for a session."""
    cursor = conn.cursor()
    cursor.execute('DELETE FROM session_memories WHERE session_id = ?', (session_id,))
    conn.commit()
