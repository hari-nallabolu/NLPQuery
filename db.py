import sqlite3

def get_connection():
    return sqlite3.connect("genai.db", check_same_thread=False)

def execute_sql(query):
    conn = get_connection()
    conn.row_factory = sqlite3.Row  # Set row factory to return row objects
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        cols = [desc[0] for desc in cursor.description]
        
        # Convert rows to dictionaries with column names
        rows = []
        for row in cursor.fetchall():
            row_dict = {}
            for i, col in enumerate(cols):
                row_dict[col] = row[i]
            rows.append(row_dict)
            
        return {"columns": cols, "rows": rows}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()
