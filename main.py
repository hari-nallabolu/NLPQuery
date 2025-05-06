from fastapi import FastAPI
from pydantic import BaseModel
from db import execute_sql
from openai_sql import nl_to_sql_with_understanding
from pinning import setup_pinning, save_pin, get_pins, update_pin, save_query_history, get_query_history

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://redyoib.streamlit.app", "http://localhost:8501", "http://localhost:8502", "http://localhost:8503"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
setup_pinning()

class Query(BaseModel):
    user_query: str

class PinRequest(BaseModel):
    user_query: str
    sql_query: str
    understanding: str = ""
    chart_type: str = "table"

class HistoryRequest(BaseModel):
    timestamp: str
    user_query: str
    sql_query: str
    understanding: str = ""

@app.post("/query")
def run_query(q: Query):
    result_with_understanding = nl_to_sql_with_understanding(q.user_query)
    sql = result_with_understanding["sql"]
    understanding = result_with_understanding["understanding"]
    result = execute_sql(sql)
    
    # Save to query history
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_query_history(timestamp, q.user_query, sql, understanding)
    
    return {"sql": sql, "understanding": understanding, "result": result}

@app.post("/pin")
def pin_query(p: PinRequest):
    save_pin(p.user_query, p.sql_query, p.chart_type)
    return {"status": "pinned"}

@app.get("/pins")
def get_all_pins():
    return get_pins()

@app.post("/refresh_pin")
def manually_refresh_pin(pin_id: int):
    pins = get_pins()
    for pin in pins:
        if pin[0] == pin_id:
            sql = pin[2]
            result = execute_sql(sql)
            return {"result": result}
    return {"error": "Pin not found"}

@app.post("/refresh_all")
def refresh_all_pins():
    return {"status": "refresh started in background"}

@app.get("/query_history")
def get_history(limit: int = 50):
    return get_query_history(limit)
