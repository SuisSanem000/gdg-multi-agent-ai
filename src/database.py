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
