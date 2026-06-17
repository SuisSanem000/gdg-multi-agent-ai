import sqlite3

def setup_database():
    """Initializes an in-memory SQLite database and seeds it with statutes."""
    # We use in-memory database for local test runs
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS statutes (
            id TEXT PRIMARY KEY,
            title TEXT,
            clause TEXT
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
    
    # Seeding Australian Corporations Act statutory definition data
    statutes_data = [
        (
            'corp-181',
            'Corporations Act Section 181',
            'Good faith: A director or other officer of a corporation must exercise their powers and discharge their duties in good faith in the best interests of the corporation and for a proper purpose.'
        ),
        (
            'corp-182',
            'Corporations Act Section 182',
            'Use of position: A director, secretary, other officer or employee of a corporation must not improperly use their position to gain an advantage for themselves or someone else or cause detriment to the corporation.'
        )
    ]
    
    cursor.executemany(
        'INSERT OR REPLACE INTO statutes (id, title, clause) VALUES (?, ?, ?)',
        statutes_data
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

