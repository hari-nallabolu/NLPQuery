# 🧠 GenAI POC: Natural Language SQL Explorer

This project is a Proof of Concept (POC) for a GenAI-based system that allows users to ask natural language questions and retrieve answers from a structured database using GPT-4, SQL, and visualizations.

---

## 🚀 Features

- ✅ Convert Natural Language to SQL using GPT-4
- ✅ Execute queries on a SQLite database
- ✅ Return results as:
  - Text
  - Table
  - Chart (in progress)
- ✅ Pin queries for later reuse
- ✅ View and rerun pinned queries
- ✅ Ready-to-extend for auto-refresh

---

## 🧱 Tech Stack

| Layer        | Technology         |
|--------------|--------------------|
| Frontend     | Streamlit          |
| Backend      | FastAPI            |
| Database     | SQLite             |
| Gen AI Model | OpenAI GPT-4       |
| Scheduler    | APScheduler (optional) |
| Language     | Python 3.10+       |

---

## 📦 Project Structure

```
genai_poc/
│
├── app.py              # Streamlit UI
├── main.py             # FastAPI backend
├── db.py               # Database logic
├── openai_sql.py       # OpenAI NL → SQL logic
├── pinning.py          # Pinned queries
├── schema.sql          # Initial DB schema + data
├── .env                # OpenAI key
├── requirements.txt
└── README.md
```

---

## 🛠️ Setup Instructions

1. **Clone or unzip the project**
2. **Install dependencies**
```bash
pip install -r requirements.txt
```
3. **Create SQLite DB**
```bash
sqlite3 genai.db < schema.sql
```
4. **Set your OpenAI API key in `.env`**
```
OPENAI_API_KEY=sk-...
```
5. **Run FastAPI backend**
```bash
uvicorn main:app --reload
```
6. **In a new terminal, run Streamlit**
```bash
streamlit run app.py
```

---

## 💡 Sample Queries to Try

- Show purchases made by John Doe on March 15, 2024.
- List products bought by Alice in January 2024.
- Who bought AirPods Pro?
- List top 3 customers by purchase amount.

---

## 📌 Pinning Feature

Once a query is run, click **📌 Pin this query** to save it. View all pinned queries under the **📌 Pinned Reports** tab.

---

## 🧠 Future Enhancements

- Plotly-based charts for data
- Auto-refresh mechanism
- User login and access control
- Change data capture (CDC) for live data

---

Made with ❤️ for GenAI innovation tests.
