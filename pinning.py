import sqlite3
import json

def setup_pinning():
    conn = sqlite3.connect("genai.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS PinnedReports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_query TEXT,
        sql_query TEXT,
        chart_type TEXT DEFAULT 'table'
    )
    """)
    
    # Create a table for query history
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS QueryHistory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        user_query TEXT,
        sql_query TEXT,
        understanding TEXT,
        data TEXT
    )
    """)
    
    conn.commit()
    conn.close()

def save_pin(user_query, sql_query, chart_type="table"):
    conn = sqlite3.connect("genai.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO PinnedReports (user_query, sql_query, chart_type) VALUES (?, ?, ?)",
                   (user_query, sql_query, chart_type))
    conn.commit()
    conn.close()

def get_pins():
    conn = sqlite3.connect("genai.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_query, sql_query, chart_type FROM PinnedReports")
    return cursor.fetchall()

def update_pin(pin_id, chart_type=None):
    """Update a pinned report's settings"""
    conn = sqlite3.connect("genai.db")
    cursor = conn.cursor()
    if chart_type:
        cursor.execute("UPDATE PinnedReports SET chart_type = ? WHERE id = ?", 
                      (chart_type, pin_id))
    conn.commit()
    conn.close()
    return True

def save_query_history(timestamp, user_query, sql_query, understanding, data=None):
    """Save a query to history"""
    conn = sqlite3.connect("genai.db")
    cursor = conn.cursor()
    
    # Convert data to JSON if provided
    data_json = json.dumps(data) if data else None
    
    cursor.execute("""
    INSERT INTO QueryHistory (timestamp, user_query, sql_query, understanding, data) 
    VALUES (?, ?, ?, ?, ?)
    """, (timestamp, user_query, sql_query, understanding, data_json))
    
    conn.commit()
    conn.close()
    return True

def get_query_history(limit=50):
    """Get recent query history"""
    conn = sqlite3.connect("genai.db")
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, timestamp, user_query, sql_query, understanding 
    FROM QueryHistory 
    ORDER BY id DESC 
    LIMIT ?
    """, (limit,))
    
    history = cursor.fetchall()
    conn.close()
    
    # Format the results as dictionaries
    history_list = [
        {
            "id": item[0],
            "timestamp": item[1],
            "query": item[2],
            "sql": item[3],
            "understanding": item[4]
        }
        for item in history
    ]
    
    return history_list
