from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables at startup
load_dotenv()
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

def get_sql_query(question):
    schema = """You are an SQL expert, this is the schema of all the tables of the models of the application.

    Schema:
    Table: sessions
    Context: This stores the session of each users, sessions are unqiue but users can have multiple sessions.
- id (UUID, primary key)
- trackingId (string, not null)
- entryPage (string, not null)
- exitPage (string, nullable)
- timeSpent (integer, not null, default: 0)
- utm_source (string, nullable)
- utm_medium (string, nullable)
- utm_campaign_name (string, nullable)
- utm_campaign_id (string, nullable)
- utm_term (string, nullable)
- utm_content (string, nullable)
- os (string, nullable)
- device (string, nullable)
- browser (string, nullable)
- longitude (float, nullable)
- latitude (float, nullable)
- city (string, nullable)
- country (string, nullable)
- createdAt (datetime)
- updatedAt (datetime)
Indexes: trackingId, createdAt

Table: signup
Context: This stores the information of users who have signed up.
- id (UUID, primary key)
- sessionId (UUID, foreign key to sessions.id)
- userId (string, not null)
- timestamp (datetime, not null)

Table: search_bar
Context: This stores the information of users who have used the search bar for products.
- id (UUID, primary key)
- sessionId (UUID, foreign key to sessions.id)
- userId (string, not null)
- searchTerm (string, not null)
- timestamp (datetime, not null)

Table: proceed_to_payment
Context: This stores the information of users who have proceeded to payment. this is the last step of a Product buying journey.
- id (UUID, primary key)
- sessionId (UUID, foreign key to sessions.id)
- productIds (string array)
- cartValue (float, not null)
- currency (string, not null)
- productName (string, not null)
- userId (string, not null)
- timestamp (datetime, not null)
- createdAt (datetime)
- updatedAt (datetime)
Relationships: belongs to sessions

Table: proceed_to_checkout
Context: This stores the information of users who have proceeded to checkout. this is the second to the last step of a Product buying journey.
- id (UUID, primary key)
- sessionId (UUID, foreign key to sessions.id)
- productIds (comma-separated string, stored as array)
- cartValue (float, not null)
- currency (string, not null)
- productName (string, not null)
- userId (string, not null)
- timestamp (datetime, not null)

Table: feature_products
Context: This stores the information of products that are featured on the platform.
- id (UUID, primary key)
- sessionId (UUID, foreign key to sessions.id)
- productId (string, not null)
- productCost (float, not null)
- currency (string, not null)
- productName (string, not null)
- userId (string, not null)
- timestamp (datetime, not null)

Table: events
Context: This stores the information of different events that happen on the platform.
- id (UUID, primary key)
- sessionId (UUID, foreign key to sessions.id)
- eventName (string, not null)
- eventType (string, not null)
- additionalData (JSON, nullable)
- timestamp (datetime, not null)
- createdAt (datetime)
- updatedAt (datetime)
Indexes: sessionId, timestamp
Relationships: belongs to sessions

Table: conversions
Context: This stores the information of conversions -- this is custom defined by the consumer, that happen on the platform.
- id (UUID, primary key)
- sessionId (UUID, foreign key to sessions.id)
- conversionType (string, not null)
- conversionValue (decimal(10,2), not null)
- timestamp (datetime, not null)
- createdAt (datetime)
- updatedAt (datetime)
Indexes: sessionId, timestamp
Relationships: belongs to sessions

Table: add_to_favourites
Context: This stores the information of products who have been added to the favourites.
- id (UUID, primary key)
- sessionId (UUID, foreign key to sessions.id)
- userId (string, not null)
- pageUrl (string, not null)
- productName (string, not null)
- productId (string, not null)
- timestamp (datetime, not null)

Table: add_to_cart
Context: This stores the information of products who have been added to the cart, first step of the product buying journey.
- id (UUID, primary key)
- sessionId (UUID, foreign key to sessions.id)
- productId (string, not null)
- productCost (float, not null)
- currency (string, not null)
- productName (string, not null)
- userId (string, not null)
- timestamp (datetime, not null)

Common Relationships:
- All tables have a foreign key relationship with the sessions table through sessionId
- Sessions is the central table containing user session information
- Most tables track user actions with timestamps
- Product-related tables (add_to_cart, feature_products, proceed_to_payment, proceed_to_checkout) share similar product information structure

Common Fields:
- All tables use UUID as primary key
- Most tables include timestamp field for event timing
- User-related actions include userId
- Product-related actions include product details and pricing"""
    
    messages = [
        ("system", f"You are an SQL expert. Generate ONLY the SQL query without any text or 'SQL:' prefix. {schema}"),
        ("human", question)
    ]
    
    try:
        response = llm.invoke(messages)
        # Clean and extract just the SQL query
        sql_query = response.content.strip()
        if sql_query.upper().startswith('SQL:'):
            sql_query = sql_query[4:].strip()
        return sql_query
    except Exception as e:
        raise Exception(f"Error generating SQL query: {str(e)}")

def get_improved_sql_query(question, original_query, error_message=None):
    error_context = f"\nPrevious error: {error_message}" if error_message else ""
    
    messages = [
        ("system", f"""You are an SQL expert. A user was not satisfied with a previous SQL query.
        Original question: {question}
        Original query: {original_query}{error_context}
        Please generate an improved SQL query that might better answer their question and avoid the previous error if any.
        Generate ONLY the SQL query without any text or 'SQL:' prefix.
        {schema}"""),
        ("human", "Please generate an improved version of this SQL query.")
    ]
    
    try:
        response = llm.invoke(messages)
        sql_query = response.content.strip()
        if sql_query.upper().startswith('SQL:'):
            sql_query = sql_query[4:].strip()
        return sql_query
    except Exception as e:
        raise Exception(f"Error generating improved SQL query: {str(e)}")