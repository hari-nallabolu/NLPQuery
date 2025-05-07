import streamlit as st
import requests
import plotly.express as px
import pandas as pd
import numpy as np
import re
import json

# Define a custom theme color palette
THEME_COLORS = {
    'primary': '#e73a5d',
    'secondary': '#1a2d4e',
    'accent': '#3a8ee7',
    'background': '#f8f9fa',
    'text': '#333333'
}

# Use a consistent color palette for all charts
CHART_COLORS = px.colors.qualitative.Bold

BACKEND_URL = "https://vigilant-chainsaw-v5jjppp7jg2wp6v-8000.app.github.dev"
print(f"[INFO] BACKEND_URL is set to: {BACKEND_URL}")

st.set_page_config(page_title="GenAI POC", layout="wide")

# Custom page title with styling
st.markdown(f"""
<h1 style='color: {THEME_COLORS['secondary']}; font-weight: 700;'>
    🧠 <span style='color: {THEME_COLORS['primary']}'>GenAI POC:</span> Natural Language SQL Explorer
</h1>
""", unsafe_allow_html=True)

# Apply custom styles to streamlit elements
st.markdown(f"""
<style>
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 24px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        color: {THEME_COLORS['text']};
        font-weight: 500;
    }}
    
    .stTabs [aria-selected="true"] {{
        color: {THEME_COLORS['primary']} !important;
        border-bottom-color: {THEME_COLORS['primary']} !important;
        font-weight: 600;
    }}
    
    /* Button styling */
    div.stButton > button {{
        background-color: {THEME_COLORS['primary']};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 500;
    }}
    
    div.stButton > button:hover {{
        background-color: #c62c4d;
    }}
    
    /* Success/info message styling */
    div.stAlert > div[data-baseweb="notification"] {{
        border-radius: 8px;
    }}
</style>
""", unsafe_allow_html=True)

# Extract chart preferences from user query
def extract_chart_preferences(query):
    preferences = {
        'chart_type': None,
        'x_column': None,
        'y_column': None
    }
    
    # Detect chart type
    chart_types = {
        'bar': ['bar chart', 'bar graph', 'column chart', 'histogram'],
        'line': ['line chart', 'line graph', 'trend', 'time series'],
        'pie': ['pie chart', 'pie graph', 'distribution', 'percentage'],
        'scatter': ['scatter plot', 'scatter chart', 'scatter graph', 'correlation'],
        'stacked bar': ['stacked', 'stack', 'stacked bar', 'stacked chart', 'stacked graph'],
        'grouped bar': ['grouped', 'group', 'grouped bar', 'side by side', 'compare products']
    }
    
    query_lower = query.lower()
    
    # Check for chart type mentions
    for chart_type, keywords in chart_types.items():
        for keyword in keywords:
            if keyword in query_lower:
                preferences['chart_type'] = chart_type
                break
        if preferences['chart_type']:
            break
    
    # Look for specific columns to visualize
    # Common patterns: "show me X by Y", "chart of X", "graph X against Y"
    
    # Check for amount/price/total mentions
    amount_keywords = ['amount', 'price', 'total', 'sum', 'value', 'cost', 'sales']
    for keyword in amount_keywords:
        if keyword in query_lower:
            preferences['y_column'] = keyword
            break
    
    # Check for time/category mentions
    category_keywords = ['date', 'month', 'year', 'customer', 'product', 'name', 'category']
    for keyword in category_keywords:
        if keyword in query_lower:
            preferences['x_column'] = keyword
            break
    
    return preferences

# Debug function to show dataframe info
def show_dataframe_info(df):
    st.write("### Data and Column Types Debug Info")
    st.write("#### DataFrame Shape:", df.shape)
    
    # Display column types
    col_types = pd.DataFrame({
        'Column': df.columns,
        'Type': df.dtypes,
        'Non-Null Count': df.count(),
        'First Value': [str(df[col].iloc[0]) if not df.empty else "N/A" for col in df.columns]
    })
    st.write("#### Column Types:")
    st.dataframe(col_types)
    
    # Show the first few rows as JSON for inspection
    st.write("#### First Row as JSON:")
    if not df.empty:
        st.code(json.dumps(df.iloc[0].to_dict(), indent=2))
    
    return

# Add this function above the create_chart function

def prepare_grouped_data(data, chart_prefs):
    """Prepare data for charting when it has grouped results"""
    import pandas as pd
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Check if this looks like grouped data (has product and time period columns)
    has_product = any('product' in col.lower() for col in df.columns)
    has_time = any(col.lower() in ['month', 'year', 'date', 'quarter'] for col in df.columns)
    has_total = any(col.lower() in ['total', 'sum', 'amount', 'sales'] for col in df.columns)
    
    # If this is grouped product data by time period, we want to reshape it for better visualization
    if has_product and has_time and has_total:
        # Identify the columns
        product_col = next((col for col in df.columns if 'product' in col.lower()), None)
        time_col = next((col for col in df.columns if col.lower() in ['month', 'year', 'date', 'quarter']), None)
        value_col = next((col for col in df.columns if col.lower() in ['total', 'sum', 'amount', 'sales']), None)
        
        if product_col and time_col and value_col:
            st.info(f"Detected product data grouped by time - using specialized chart")
            
            # Check chart preference in query
            use_stacked = 'stack' in chart_prefs.get('chart_type', '')
            
            if use_stacked or not chart_prefs.get('chart_type'):
                # For stacked bar chart - grouped by time with products stacked
                fig = px.bar(
                    df, x=time_col, y=value_col, color=product_col,
                    title=f"{value_col} by {time_col} and {product_col}",
                    barmode='stack',
                    color_discrete_sequence=CHART_COLORS
                )
            else:
                # For grouped bar chart - time and products side by side
                fig = px.bar(
                    df, x=time_col, y=value_col, color=product_col,
                    title=f"{value_col} by {time_col} and {product_col}",
                    barmode='group',
                    color_discrete_sequence=CHART_COLORS
                )
            
            # Improve appearance
            fig.update_layout(
                height=500, 
                template="plotly_white",
                legend_title=product_col,
                xaxis_title=time_col,
                yaxis_title=value_col,
                plot_bgcolor='rgba(0,0,0,0.02)',
                paper_bgcolor='rgba(0,0,0,0)',
                title_font_color=THEME_COLORS['secondary'],
                font_color=THEME_COLORS['text'],
                title_font_size=18
            )
            
            return fig
    
    # If not grouped data, return None to use standard chart creation
    return None

# Function to create chart based on data
def create_chart(data, chart_type="bar", preferred_x=None, preferred_y=None):
    if not data or len(data) == 0:
        st.warning("No data to visualize")
        return None
    
    # Since we're getting dict-type data, need to normalize it
    # Explicitly convert dict-type data to a properly structured DataFrame
    normalized_data = []
    for row in data:
        # Handle various possible row types to ensure consistent data
        if isinstance(row, dict):
            normalized_data.append(row)
        elif isinstance(row, (list, tuple)):
            # This handles raw tuple data by assuming the positions match column order
            # We'll handle column names later
            obj = {}
            for i, val in enumerate(row):
                obj[f"col_{i}"] = val
            normalized_data.append(obj)
    
    # If normalization didn't result in data, try using the raw data
    if not normalized_data and data:
        try:
            # Try directly with pandas - might work if data is already in a suitable format
            df = pd.DataFrame(data)
        except Exception as e:
            st.error(f"Failed to process data: {str(e)}")
            return None
    else:
        # Use the normalized data
        df = pd.DataFrame(normalized_data)
    
    # Check if we have data in the DataFrame
    if df.empty:
        st.warning("No data available for charting after normalization")
        return None
    
    # Debug display
    st.write("DataFrame structure after normalization:", df.shape)
    
    # Try to identify numeric columns for charts
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    # Try to convert any string columns that contain numbers to numeric
    for col in df.columns:
        if col not in numeric_cols:
            # Check if column has string data that might be numeric
            if df[col].dtype == 'object':  
                try:
                    # Convert to numeric and check if it worked
                    numeric_series = pd.to_numeric(df[col], errors='coerce')
                    # If we don't lose too many values, convert the column
                    if numeric_series.notna().sum() > 0.5 * len(df):
                        df[col] = numeric_series
                        numeric_cols.append(col)
                except:
                    pass
    
    # Special case: Handle if every column is a string (common with SQLite results)
    if not numeric_cols and len(df.columns) >= 2:
        # Try to identify a column that might contain numbers stored as strings
        for col in df.columns:
            sample = df[col].astype(str).str.strip().iloc[:5].tolist()
            # Check if they look like numbers
            if all(s.replace('.', '').replace('-', '').isdigit() for s in sample if s):
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    numeric_cols.append(col)
                except:
                    pass
    
    # If we still have no numeric columns, we can't create a chart
    if not numeric_cols:
        st.warning("No numeric data found for charting. Try a different query.")
        return None
    
    # Y-axis selection (prioritize user preference)
    y_col = None
    if preferred_y:
        # Try to find a column containing the preferred term
        for col in df.columns:
            if preferred_y.lower() in col.lower():
                # Make sure it's numeric or can be converted
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    if not df[col].isna().all():
                        y_col = col
                        st.info(f"Using '{y_col}' for Y-axis based on your request for '{preferred_y}'")
                        break
                except:
                    pass
    
    # If no preferred column found, look for common numeric columns
    if not y_col:
        for term in ['total_amount', 'amount', 'total', 'price', 'quantity', 'sum']:
            for col in df.columns:
                if term.lower() in col.lower():
                    try:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                        if not df[col].isna().all():
                            y_col = col
                            st.info(f"Automatically selected '{y_col}' for Y-axis")
                            break
                    except:
                        pass
            if y_col:
                break
    
    # If still no column found, use the first numeric column
    if not y_col and numeric_cols:
        y_col = numeric_cols[0]
        st.info(f"Selected '{y_col}' for Y-axis")
    
    # X-axis selection (categorical or date)
    x_col = None
    non_numeric_cols = [c for c in df.columns if c not in numeric_cols or c != y_col]
    
    # Try to find a good x column based on user preference
    if preferred_x:
        for col in df.columns:
            if preferred_x.lower() in col.lower():
                x_col = col
                st.info(f"Using '{x_col}' for X-axis based on your request for '{preferred_x}'")
                break
    
    # If no preferred column found, look for good candidate columns
    if not x_col:
        # Look for date/name columns first
        for term in ['date', 'name', 'customer', 'product', 'category', 'id']:
            for col in non_numeric_cols:
                if term.lower() in col.lower():
                    x_col = col
                    st.info(f"Selected '{x_col}' for X-axis")
                    break
            if x_col:
                break
        
        # If still no column, use first non-y column or index
        if not x_col:
            candidates = [c for c in df.columns if c != y_col]
            if candidates:
                x_col = candidates[0]
                st.info(f"Selected '{x_col}' for X-axis")
            else:
                x_col = df.index
                st.info("Using row index for X-axis")
    
    # Create the appropriate chart
    try:
        if chart_type == "bar":
            # For bar charts, limit to 15 categories max for readability
            if df[x_col].nunique() > 15:
                st.warning(f"Limiting to top 15 categories for readability")
                value_counts = df[x_col].value_counts().head(14)
                top_categories = value_counts.index.tolist()
                df_filtered = df[df[x_col].isin(top_categories)].copy()
                # Add an "Other" category
                other_rows = df[~df[x_col].isin(top_categories)]
                if not other_rows.empty:
                    other_sum = other_rows[y_col].sum()
                    other_row = other_rows.iloc[0].copy()
                    other_row[x_col] = "Other"
                    other_row[y_col] = other_sum
                    df_filtered = pd.concat([df_filtered, pd.DataFrame([other_row])])
                fig = px.bar(df_filtered, x=x_col, y=y_col, 
                         title=f"{y_col} by {x_col}",
                         color_discrete_sequence=CHART_COLORS)
            else:
                fig = px.bar(df, x=x_col, y=y_col, 
                         title=f"{y_col} by {x_col}",
                         color_discrete_sequence=CHART_COLORS)
        
        elif chart_type == "line":
            # For line charts, sort by x if it seems like a date
            if x_col in df.columns and ('date' in x_col.lower() or 'time' in x_col.lower()):
                df = df.sort_values(by=x_col)
            fig = px.line(df, x=x_col, y=y_col, 
                      title=f"{y_col} over {x_col}",
                      color_discrete_sequence=CHART_COLORS)
        
        elif chart_type == "pie":
            # For pie charts, limit to 8 segments max for readability
            if df[x_col].nunique() > 8:
                st.warning(f"Limiting to top 7 categories for readability")
                value_counts = df.groupby(x_col)[y_col].sum().sort_values(ascending=False).head(7)
                top_categories = value_counts.index.tolist()
                
                # Create a new DataFrame with the top categories and an "Other" category
                df_top = df[df[x_col].isin(top_categories)].copy()
                other_sum = df[~df[x_col].isin(top_categories)][y_col].sum()
                
                # Create the "Other" data point
                other_data = {x_col: "Other", y_col: other_sum}
                df_pie = pd.concat([df_top, pd.DataFrame([other_data])])
                
                fig = px.pie(df_pie, names=x_col, values=y_col, 
                         title=f"Distribution of {y_col} by {x_col}",
                         color_discrete_sequence=CHART_COLORS)
            else:
                # Use the data as is for the pie chart
                fig = px.pie(df, names=x_col, values=y_col, 
                         title=f"Distribution of {y_col} by {x_col}",
                         color_discrete_sequence=CHART_COLORS)
        
        elif chart_type == "scatter":
            # For scatter, try to use a third column for size if available
            other_numeric = [c for c in numeric_cols if c != y_col]
            size_col = other_numeric[0] if other_numeric else None
            
            # Add color grouping if we have a good categorical column
            color_col = None
            categorical_cols = [c for c in df.columns if c not in numeric_cols and c != x_col]
            if categorical_cols:
                color_col = categorical_cols[0]
            
            fig = px.scatter(df, x=x_col, y=y_col, 
                size=size_col, color=color_col,
                         title=f"{y_col} vs {x_col}",
                         color_discrete_sequence=CHART_COLORS)
        else:
            # Default to bar chart if we don't recognize the type
            fig = px.bar(df, x=x_col, y=y_col, 
                     title=f"{y_col} by {x_col}",
                     color_discrete_sequence=CHART_COLORS)
        
        # Improve chart appearance
        fig.update_layout(
            height=500,
            template="plotly_white",
            title_font_size=18,
            legend_title_font_size=14,
            title_font_family="Arial",
            xaxis_title=x_col,
            yaxis_title=y_col,
            plot_bgcolor='rgba(0,0,0,0.02)',
            paper_bgcolor='rgba(0,0,0,0)',
            title_font_color=THEME_COLORS['secondary'],
            font_color=THEME_COLORS['text']
        )
        
        # Update trace line thickness
        for trace in fig.data:
            if hasattr(trace, 'line'):
                trace.line.width = 3
        
        return fig
    
    except Exception as e:
        st.error(f"Error creating chart: {str(e)}")
        return None

tab1, tab2 = st.tabs(["💬 Query", "📌 Pinned Reports"])

# Initialize query history in session state if it doesn't exist
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
    # Try to fetch existing history from backend
    try:
        history_response = requests.get(f"{BACKEND_URL}/query_history")
        if history_response.status_code == 200:
            st.session_state.query_history = history_response.json()
    except:
        # If backend is not available, continue with empty history
        pass

# Initialize query input value
if 'query_input' not in st.session_state:
    st.session_state.query_input = ""

# Function to directly run a query when clicked from history
def run_saved_query(query_text):
    # This function will be called when a history item is clicked
    # It executes the query directly
    with st.spinner("Re-running query..."):
        response = requests.post(f"{BACKEND_URL}/query", json={"user_query": query_text})
        if response.status_code == 200:
            res = response.json()
            sql = res["sql"]
            result = res["result"]
            understanding = res.get("understanding", "")
            
            st.session_state.last_query = query_text
            st.session_state.last_sql = sql
            
            # Display the understanding first
            if understanding:
                st.markdown("#### 🧠 Understanding of your question")
                st.info(understanding)
            
            # Display SQL without using an expander (since we're already in an expander)
            st.markdown("#### 🧾 SQL Query")
            st.code(sql, language="sql")
            
            if "error" in result:
                st.error(f"SQL Error: {result['error']}")
            else:
                # Display tabs for different views
                result_tabs = st.tabs(["📊 Table", "📈 Chart"])
                
                with result_tabs[0]:
                    if result["rows"]:
                        st.dataframe(result["rows"], use_container_width=True)
                    else:
                        st.info("No data returned from query")
                    
                with result_tabs[1]:
                    # Generate chart
                    chart_prefs = extract_chart_preferences(query_text)
                    chart_type = chart_prefs.get('chart_type', 'bar')
                    
                    if result["rows"]:
                        # First try the specialized grouped data handler
                        grouped_chart = prepare_grouped_data(result["rows"], chart_prefs)
                        
                        if grouped_chart:
                            st.plotly_chart(grouped_chart, use_container_width=True)
                        else:
                            # Fall back to regular chart creation
                            chart = create_chart(
                                result["rows"], 
                                chart_type, 
                                preferred_x=chart_prefs['x_column'],
                                preferred_y=chart_prefs['y_column']
                            )
                            if chart:
                                st.plotly_chart(chart, use_container_width=True)
                            else:
                                st.warning("Could not create chart. Try a different query or chart type.")
                    else:
                        st.info("No data available for chart.")

# Function to copy query to input
def rerun_query(query):
    st.session_state.query_input = query
    
with tab1:
    st.subheader("Ask a question in Natural Language")
    user_query = st.text_input("Enter your question", value=st.session_state.query_input, 
                              placeholder="e.g. Show purchases by John Doe and chart the amount", 
                              key="user_query")

    if st.button("🔍 Run Query"):
        if user_query.strip() == "":
            st.warning("Please enter a question.")
        else:
            # Extract chart preferences from query
            chart_prefs = extract_chart_preferences(user_query)
            
            with st.spinner("Generating SQL and fetching results..."):
                response = requests.post(f"{BACKEND_URL}/query", json={"user_query": user_query})
                print(f"[INFO] BACKEND_URL is set to: {response}")
                if response.status_code == 200:
                    res = response.json()
                    sql = res["sql"]
                    result = res["result"]
                    understanding = res.get("understanding", "")
                    
                    # Add to query history
                    timestamp = pd.Timestamp.now().strftime("%H:%M:%S")
                    st.session_state.query_history.append({
                        "timestamp": timestamp,
                        "query": user_query,
                        "sql": sql,
                        "understanding": understanding
                    })
                    
                    # Display the understanding first
                    if understanding:
                        st.markdown("#### 🧠 Understanding of your question")
                        st.info(understanding)
                    
                    # Display SQL without using an expander (since we're already in an expander)
                    st.markdown("#### 🧾 SQL Query")
                    st.code(sql, language="sql")
                    
                    # Store query in session state for pinning later
                    st.session_state.last_query = user_query
                    st.session_state.last_sql = sql
                    st.session_state.chart_prefs = chart_prefs

                    if "error" in result:
                        st.error(f"SQL Error: {result['error']}")
                    else:
                        # Display tabs for different views
                        result_tabs = st.tabs(["📊 Table", "📈 Chart"])
                        
                        with result_tabs[0]:
                            if result["rows"]:
                                st.dataframe(result["rows"], use_container_width=True)
                            else:
                                st.info("No data returned from query")
                            
                        with result_tabs[1]:
                            # Use detected chart type or let user select
                            if chart_prefs['chart_type']:
                                chart_type = chart_prefs['chart_type']
                                st.info(f"Using chart type from your query: {chart_type}")
                            else:
                                chart_type = st.selectbox(
                                    "Select chart type",
                                    ["bar", "line", "pie", "scatter", "stacked bar", "grouped bar"],
                                    key="chart_type"
                                )
                            
                            # Generate chart with preferences from query
                            if result["rows"]:
                                # First try the specialized grouped data handler
                                grouped_chart = prepare_grouped_data(result["rows"], chart_prefs)
                                
                                if grouped_chart:
                                    st.plotly_chart(grouped_chart, use_container_width=True)
                                else:
                                    # Fall back to regular chart creation
                                    chart = create_chart(
                                        result["rows"], 
                                        chart_type, 
                                        preferred_x=chart_prefs['x_column'],
                                        preferred_y=chart_prefs['y_column']
                                    )
                                    if chart:
                                        st.plotly_chart(chart, use_container_width=True)
                                    else:
                                        st.warning("Could not create chart. Try a different query or chart type.")
                            else:
                                st.info("No data available for chart.")
                                
                            # Store chart type for pinning
                            st.session_state.last_chart_type = chart_type
                else:
                    st.error("Failed to connect to backend.")
    
    # Add pin button outside the Run Query button's block
    if st.session_state.get('last_query') and st.session_state.get('last_sql'):
        if st.button("📌 Pin this query"):
            chart_type = st.session_state.get('last_chart_type', 'table')
            pin_res = requests.post(f"{BACKEND_URL}/pin", json={
                "user_query": st.session_state.last_query,
                "sql_query": st.session_state.last_sql,
                "chart_type": chart_type
            })
            if pin_res.status_code == 200:
                st.success("Query pinned successfully!")
    
    # Display query history
    if st.session_state.query_history:
        st.markdown("---")
        st.subheader("📜 Query History")
        
        # Refresh history button
        if st.button("🔄 Refresh History", key="refresh_history_btn"):
            history_response = requests.get(f"{BACKEND_URL}/query_history")
            if history_response.status_code == 200:
                st.session_state.query_history = history_response.json()
                st.success("Query history refreshed")
        
        for i, hist_item in enumerate(st.session_state.query_history):
            # Use a unique prefix for history items to avoid conflict with pinned items
            hist_id = hist_item.get("id", i)
            with st.expander(f"[{hist_item['timestamp']}] {hist_item['query']}", expanded=False):
                if hist_item.get("understanding"):
                    st.markdown("##### 🧠 Understanding")
                    st.info(hist_item["understanding"])
                st.markdown("##### 🧾 SQL Query")
                st.code(hist_item["sql"], language="sql")
                
                # Add two buttons - one to copy to input, one to run directly
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"📋 Copy to input", key=f"hist_copy_{hist_id}_{i}"):
                        rerun_query(hist_item["query"])
                with col2:
                    if st.button(f"▶️ Run directly", key=f"hist_run_{hist_id}_{i}"):
                        run_saved_query(hist_item["query"])
    else:
        st.info("No query history yet. Ask some questions to build up your history.")

with tab2:
    st.subheader("📌 Pinned Reports")
    pins = requests.get(f"{BACKEND_URL}/pins").json()

    if pins:
        for pin in pins:
            # Now pins includes chart_type (id, question, sql, chart_type)
            if len(pin) >= 4:
                pin_id, question, sql, chart_type = pin
            else:
                pin_id, question, sql = pin
                chart_type = "bar"  # Default for older pins
                
            # Extract chart preferences from pinned question
            chart_prefs = extract_chart_preferences(question)
                
            with st.expander(f"📎 {question}"):
                st.markdown("##### 🧾 SQL Query")
                st.code(sql, language="sql")
                view_tabs = st.tabs(["📊 Table", "📈 Chart"])
                
                if st.button(f"▶️ Run pinned query", key=f"pinned_run_{pin_id}"):
                    result = requests.post(f"{BACKEND_URL}/query", json={"user_query": question}).json()
                    if "result" in result and "rows" in result["result"]:
                        with view_tabs[0]:
                            st.dataframe(result["result"]["rows"], use_container_width=True)
                        
                        with view_tabs[1]:
                            # First try the specialized grouped data handler
                            grouped_chart = prepare_grouped_data(result["result"]["rows"], chart_prefs)
                            
                            if grouped_chart:
                                st.plotly_chart(grouped_chart, use_container_width=True)
                            else:
                                # Fall back to the saved chart type
                                chart = create_chart(
                                    result["result"]["rows"], 
                                    chart_type,
                                    preferred_x=chart_prefs['x_column'],
                                    preferred_y=chart_prefs['y_column']
                                )
                                if chart:
                                    st.plotly_chart(chart, use_container_width=True)
                                else:
                                    # Fall back to trying different charts
                                    for alt_chart_type in ["bar", "line", "pie"]:
                                        if alt_chart_type != chart_type:
                                            chart = create_chart(
                                                result["result"]["rows"], 
                                                alt_chart_type,
                                                preferred_x=chart_prefs['x_column'],
                                                preferred_y=chart_prefs['y_column']
                                            )
                                            if chart:
                                                st.info(f"Could not create {chart_type} chart, showing {alt_chart_type} instead.")
                                                st.plotly_chart(chart, use_container_width=True)
                                                break
                                    else:
                                        st.warning("Could not generate any chart for this data.")
                    else:
                        st.warning("No results found or query failed.")
    else:
        st.info("No pinned queries yet.")
