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
    # Get SQL query from LLM
    sql_query = get_sql_query(user_question)
    st.session_state.current_query = sql_query
    st.session_state.current_question = user_question
    
    # Display the generated SQL query
    st.subheader("Generated SQL Query:")
    st.code(sql_query, language="sql")
    
    # Execute button with unique key
    if st.button("Execute Query", key='execute_main_query'):
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

    # Move feedback section outside the execute button block
    if st.session_state.current_query and not st.session_state.feedback_given:
        st.markdown("---")
        st.subheader("Was this response helpful?")
        
        # Debug information
        st.sidebar.write("Debug: Current state:", {
            "current_query": st.session_state.current_query[:50] + "...",
            "current_question": st.session_state.current_question,
            "feedback_given": st.session_state.feedback_given
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("👍 Yes, it was helpful", key="feedback_good"):
                st.write("⏳ Saving feedback...")
                success = save_feedback(
                    st.session_state.current_question,
                    st.session_state.current_query,
                    True
                )
                if success:
                    st.success("✅ Thank you for your positive feedback!")
                    st.session_state.feedback_given = True
                    st.rerun()  # Changed from experimental_rerun to rerun
                else:
                    st.error("❌ Failed to save feedback")
        
        with col2:
            if st.button("👎 No, needs improvement", key="feedback_bad"):
                st.write("⏳ Saving feedback...")
                if save_feedback(st.session_state.current_question, st.session_state.current_query, False):
                    st.info("Generating an improved response...")
                    try:
                        # Get the error message from session state if it exists
                        error_msg = st.session_state.get('last_error', None)
                        improved_query = get_improved_sql_query(st.session_state.current_question, st.session_state.current_query, error_msg)
                        st.session_state.improved_query = improved_query
                        st.session_state.feedback_given = True
                        
                        # Display improved query
                        st.subheader("Improved SQL Query:")
                        st.code(improved_query, language="sql")
                        
                        
                        # Add execute button for improved query
                        if st.button("Execute Improved Query", key='execute_improved_query'):
                            try:
                                conn = get_database_connection()
                                df = pd.read_sql_query(improved_query, conn)
                                conn.close()
                                
                                st.subheader("New Query Results:")
                                st.dataframe(df)
                                
                                if not df.empty and len(df.columns) >= 2:
                                    st.bar_chart(df)
                                    
                            except Exception as e:
                                st.error(f"Error executing improved query: {str(e)}")
                    except Exception as e:
                        st.error(f"Error generating improved query: {str(e)}")
                        st.session_state.feedback_given = True

                        # Add execute button for improved query
                        if st.button("Execute Improved Query", key='execute_improved_query'):
                            try:
                                conn = get_database_connection()
                                df = pd.read_sql_query(improved_query, conn)
                                conn.close()
                                
                                st.subheader("New Query Results:")
                                st.dataframe(df)
                                
                                if not df.empty and len(df.columns) >= 2:
                                    st.bar_chart(df)
                                    
                            except Exception as e:
                                st.error(f"Error executing improved query: {str(e)}")
                    except Exception as e:
                        st.error(f"Error generating improved query: {str(e)}")
                        st.session_state.feedback_given = True
