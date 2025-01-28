import streamlit as st
from llm import get_sql_query, get_improved_sql_query
import pandas as pd
import pymysql
from dotenv import load_dotenv
import os
import uuid

# Load environment variables
load_dotenv()

# Add at the start of the file, after imports
if 'current_query' not in st.session_state:
    st.session_state.current_query = None
if 'current_question' not in st.session_state:
    st.session_state.current_question = None
if 'feedback_given' not in st.session_state:
    st.session_state.feedback_given = False
if 'improved_query_feedback_given' not in st.session_state:
    st.session_state.improved_query_feedback_given = False
if 'current_improved_query' not in st.session_state:
    st.session_state.current_improved_query = None
if 'saved_queries' not in st.session_state:
    st.session_state.saved_queries = []

# Database connection function - Move this to the top
def get_database_connection():
    connection_params = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'db': os.getenv('DB_NAME')
    }
    
    # Debug connection parameters (optional)
    if st.sidebar.checkbox("Debug Connection Parameters", key='debug_params_connection'):
        st.sidebar.write({k: v for k, v in connection_params.items() if k != 'password'})
    
    return pymysql.connect(**connection_params)

# Debug database connection - Move this after the function definition
if st.sidebar.checkbox("Test Database Connection", key='test_db_connection'):
    try:
        conn = get_database_connection()
        with conn.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            st.sidebar.success("Database connected successfully!")
            st.sidebar.write("Available tables:", tables)
        conn.close()
    except Exception as e:
        st.sidebar.error(f"Database connection failed: {str(e)}")

def save_query(question, query, is_good):
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        sql = "INSERT INTO query_feedback (question, sql_query, feedback) VALUES (%s, %s, %s)"
        cursor.execute(sql, (question, query, 1 if is_good else 0))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.sidebar.error(f"Error saving query: {str(e)}")
        return False

def save_feedback(question, sql_query, is_good):
    st.sidebar.write("Debug: save_feedback called with:", {
        "question": question[:50] + "...",
        "sql_query": sql_query[:50] + "...",
        "is_good": is_good
    })
    
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Debug database connection
        st.sidebar.write("Debug: Database connected")
        
        # Print the full SQL statement for debugging
        sql = "INSERT INTO query_feedback (question, sql_query, feedback) VALUES (%s, %s, %s)"
        st.sidebar.write("Debug: Executing SQL:", sql)
        st.sidebar.write("Debug: Values:", (question[:50], sql_query[:50], is_good))
        
        cursor.execute(sql, (question, sql_query, is_good))
        
        # Debug after execute
        st.sidebar.write("Debug: SQL executed")
        
        conn.commit()
        st.sidebar.write("Debug: Transaction committed")
        
        cursor.execute("SELECT LAST_INSERT_ID()")
        last_id = cursor.fetchone()[0]
        st.sidebar.write(f"Debug: Last inserted ID: {last_id}")
        
        conn.close()
        st.sidebar.write("Debug: Connection closed")
        
        if last_id:
            return True
        else:
            st.error("Error verifying feedback insertion.")
            return False
    except Exception as e:
        st.sidebar.error(f"Debug: Error in save_feedback: {str(e)}")
        import traceback
        st.sidebar.error(f"Debug: Full traceback:\n{traceback.format_exc()}")
        return False

# Initialize Streamlit app
st.title("SQL Query Assistant")

# Create input text area for user question
user_question = st.text_input("Enter your business question:")

if user_question:
    if st.session_state.current_query is None:
        st.session_state.current_query = get_sql_query(user_question)
    sql_query = st.session_state.current_query

    # Reset feedback state when a new query is generated
    if sql_query != st.session_state.get('current_query', None):
        st.session_state.feedback_given = False
        st.session_state.improved_query_feedback_given = False
        if 'improved_query' in st.session_state:
            del st.session_state.improved_query
    
    st.session_state.current_query = sql_query
    st.session_state.current_question = user_question
    
    # Display the generated SQL query
    st.subheader("Generated SQL Query:")
    st.code(sql_query, language="sql")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Execute Original Query", key='execute_main_query'):
            try:
                conn = get_database_connection()
                df = pd.read_sql_query(sql_query, conn)
                conn.close()
                
                # Display results
                st.subheader("Query Results:")
                st.dataframe(df)
                
                if not df.empty and len(df.columns) >= 2:
                    st.bar_chart(df)
                    
            except Exception as e:
                error_msg = str(e)
                st.error(f"Error executing query: {error_msg}")
                st.session_state.last_error = error_msg

    with col2:
        if st.button("🔄 Regenerate Query", key="regenerate_query"):
            try:
                error_msg = st.session_state.get('last_error', None)
                improved_query = get_improved_sql_query(user_question, sql_query, error_msg)
                st.session_state.current_query = improved_query
                st.rerun()
            except Exception as e:
                st.error(f"Error regenerating query: {str(e)}")

    # Replace the expander section with:
    st.markdown("### Save Query")
    col3, col4 = st.columns(2)
    with col3:
        if st.button("👍 Save as Good Query", key="save_good_query"):
            if save_query(user_question, sql_query, True):
                st.success("Query saved successfully as good!")
            else:
                st.error("Failed to save query")
    with col4:
        if st.button("👎 Save as Bad Query", key="save_bad_query"):
            if save_query(user_question, sql_query, False):
                st.success("Query saved successfully as bad!")
            else:
                st.error("Failed to save query")
    
    # Check if there's an improved query in the session state
    if 'improved_query' in st.session_state:
        st.subheader("Improved SQL Query:")
        st.code(st.session_state.improved_query, language="sql")
        st.session_state.current_improved_query = st.session_state.improved_query
        
        if st.button("Execute Improved Query", key='execute_improved_query_main'):
            try:
                conn = get_database_connection()
                df = pd.read_sql_query(st.session_state.improved_query, conn)
                conn.close()
                
                st.subheader("Improved Query Results:")
                st.dataframe(df)
                
                if not df.empty and len(df.columns) >= 2:
                    st.bar_chart(df)
                
            except Exception as e:
                st.error(f"Error executing improved query: {str(e)}")
    
    # Store current query as previous query for next comparison
    st.session_state.previous_query = sql_query
