import os
from langchain.llms import OpenAI
from langchain.sql_database import SQLDatabase
from langchain.chains import SQLDatabaseSequentialChain
from langchain.chat_models import ChatOpenAI
from langchain.graphs import StateGraph
from langchain.memory import ConversationBufferMemory
import pymysql
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables at startup
load_dotenv()

# Installation Command
# Run this in your terminal before executing the script
# pip install langchain pymysql openai sqlalchemy

# Environment Variables for API Keys
# os.environ["OPENAI_API_KEY"] = "your-openai-api-key"

# Database Connection
db = SQLDatabase.from_uri("mysql+pymysql://root:mysecretpassword@pma.kalpas.in/tracker")

# Initialize LLM
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

# Define Graph States
class SQLQAState:
    def __init__(self, question: str):
        self.question = question
        self.sql_query = ""
        self.result = ""

# Define the Pipeline Graph
sg = StateGraph(SQLQAState)

def generate_sql(state: SQLQAState):
    """Generates SQL query from natural language input."""
    chain = SQLDatabaseSequentialChain.from_llm(llm, db, return_intermediate_steps=True)
    state.sql_query, _ = chain.run(state.question)
    return state

sg.add_node("GenerateSQL", generate_sql)

def execute_sql(state: SQLQAState):
    """Executes the generated SQL query."""
    with db.get_engine().connect() as conn:
        result = conn.execute(state.sql_query)
        state.result = result.fetchall()
    return state

sg.add_node("ExecuteSQL", execute_sql)

# Define Workflow
sg.add_edge("GenerateSQL", "ExecuteSQL")
sg.set_entry_point("GenerateSQL")

# Running the Pipeline
if __name__ == "__main__":
    user_question = input("Ask your question: ")
    state = SQLQAState(user_question)
    final_state = sg.run(state)
    print("Query Result:", final_state.result)

# Example Queries
# Example 1: "What were the top 5 highest-grossing campaigns last month?"
# Example 2: "How many new users signed up in the last week?"
# Example 3: "Show me the conversion rate for the last quarter."
