import openai
import os
import re
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def nl_to_sql_with_understanding(user_query):
    """Convert natural language to SQL with understanding explanation"""
    # First get the understanding of the query
    understanding_prompt = f"""
Database Schema (with all column names):
Customer (customer_id INTEGER, name TEXT, email TEXT)
Product (product_id INTEGER, name TEXT, category TEXT, price REAL)
"Order" (order_id INTEGER, customer_id INTEGER, product_id INTEGER, order_date DATE, quantity INTEGER, total_amount REAL)

For the following natural language query, explain in a short 2-3 sentence summary what the query is asking for.
This explanation will be shown to the user to verify their query was understood correctly.
Be clear about what tables and fields are involved and any filters or aggregations.

Example:
Query: "Show me all purchases by John Doe in March 2024"
Understanding: "You're looking for all purchases made by the customer 'John Doe' during March 2024. This will find orders with the specified customer name and filter by the order_date field for March 2024."

Query: "{user_query}"
"""
    understanding_response = openai.ChatCompletion.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": understanding_prompt}]
    )
    
    understanding = understanding_response.choices[0].message.content.strip()
    
    # Now get the SQL query
    sql_prompt = f"""
Database Schema (with all column names):
Customer (customer_id INTEGER, name TEXT, email TEXT)
Product (product_id INTEGER, name TEXT, category TEXT, price REAL)
"Order" (order_id INTEGER, customer_id INTEGER, product_id INTEGER, order_date DATE, quantity INTEGER, total_amount REAL)

This is a SQLite database. Convert this natural language query into a valid SQLite SQL query.
Return ONLY the SQL query without any explanation or markdown formatting.

Important SQLite syntax notes:
1. "Order" is a reserved keyword in SQL and must ALWAYS be enclosed in double quotes like "Order" when used as a table name.
2. Here are the correct column names for each table:
   - Customer: customer_id, name, email
   - Product: product_id, name, category, price
   - "Order": order_id, customer_id, product_id, order_date, quantity, total_amount
3. When joining tables, use table aliases and specify the join conditions clearly.
4. Example: Customer AS C JOIN "Order" AS O ON C.customer_id = O.customer_id JOIN Product AS P ON O.product_id = P.product_id
5. Use double quotes for table/column identifiers and single quotes for string literals.
6. SQLite date format should be 'YYYY-MM-DD' format like '2024-03-15'.

Example correct queries:
- SELECT O.order_id, C.name AS customer_name, P.name AS product_name, O.order_date, O.quantity, O.total_amount 
  FROM "Order" AS O 
  JOIN Customer AS C ON O.customer_id = C.customer_id 
  JOIN Product AS P ON O.product_id = P.product_id 
  WHERE C.name = 'John Doe';

- SELECT C.name, SUM(O.total_amount) AS total_spent 
  FROM Customer AS C 
  JOIN "Order" AS O ON C.customer_id = O.customer_id 
  GROUP BY C.name 
  ORDER BY total_spent DESC 
  LIMIT 3;

Query: "{user_query}"
"""
    sql_response = openai.ChatCompletion.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": sql_prompt}]
    )
    
    # Extract the response
    sql_with_possible_extra = sql_response.choices[0].message.content.strip()
    
    # Try to extract just the SQL code
    # Look for SQL between triple backticks
    sql_match = re.search(r"```sql\s*(.*?)\s*```", sql_with_possible_extra, re.DOTALL)
    if sql_match:
        sql = sql_match.group(1).strip()
    else:
        # If no backticks with sql, try just backticks
        sql_match = re.search(r"```\s*(.*?)\s*```", sql_with_possible_extra, re.DOTALL)
        if sql_match:
            sql = sql_match.group(1).strip()
        else:
            # Otherwise use the whole response
            sql = sql_with_possible_extra
    
    return {
        "understanding": understanding,
        "sql": sql
    }

def nl_to_sql(user_query):
    """Legacy function for backward compatibility"""
    result = nl_to_sql_with_understanding(user_query)
    return result["sql"]
