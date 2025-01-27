import os
from dotenv import load_dotenv

# Load environment variables at startup
load_dotenv()

if not os.getenv('OPENAI_API_KEY'):
    raise ValueError("OPENAI_API_KEY not found in environment variables")

from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.schema import HumanMessage, SystemMessage

class RAGApp:
    def __init__(self):
        # Set up directories
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_dir = os.path.join(self.current_dir, "db")
        self.persistent_directory = os.path.join(self.db_dir, "chroma_db_with_metadata")
        
        # Initialize embeddings with API key from environment
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        self.vectorstore = None
        
    def process_text(self, text, source_name="input.txt"):
        # Create temporary file
        temp_file = os.path.join(self.current_dir, "temp.txt")
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(text)
        
        # Load and split document
        loader = TextLoader(temp_file)
        documents = loader.load()
        
        # Add metadata to document
        for doc in documents:
            doc.metadata = {"source": source_name}
            
        text_splitter = CharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=50
        )
        docs = text_splitter.split_documents(documents)
        
        # Create and persist vector store
        os.makedirs(self.db_dir, exist_ok=True)
        self.vectorstore = Chroma.from_documents(
            docs,
            self.embeddings,
            persist_directory=self.persistent_directory
        )
        
        # Clean up
        os.remove(temp_file)
        
    def get_answer(self, question: str) -> str:
        if not self.vectorstore:
            if os.path.exists(self.persistent_directory):
                self.vectorstore = Chroma(
                    persist_directory=self.persistent_directory,
                    embedding_function=self.embeddings
                )
            else:
                raise ValueError("No vector store found. Please process some text first.")
        
        # Set up retriever with similarity search
        retriever = self.vectorstore.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"k": 3, "score_threshold": 0.2},
        )
        
        # Get relevant documents
        relevant_docs = retriever.invoke(question)
        print(relevant_docs)
        
        # Create prompt template with context
        prompt_template = """Based on the following context, please create a SQL query based on the question. 
        If the answer cannot be found in the context, say "I cannot answer this based on the provided information."
        
        Context:
        {context}
        
        Question: {question}
        
        Answer:"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # # Create QA chain with API key from environment
        # qa_chain = RetrievalQA.from_chain_type(
        #     llm=ChatOpenAI(
        #         model="gpt-4",
        #         openai_api_key=os.getenv('OPENAI_API_KEY')
        #     ),
        #     chain_type="stuff",
        #     retriever=retriever,
        #     chain_type_kwargs={"prompt": PROMPT}
        # )
        
        # return qa_chain.run(question)

if __name__ == "__main__":
    rag = RAGApp()
    
    # Example usage with metadata tracking
    sample_text = """Table: sessions
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
- id (UUID, primary key)
- sessionId (UUID, foreign key to sessions.id)
- userId (string, not null)
- timestamp (datetime, not null)

Table: search_bar
- id (UUID, primary key)
- sessionId (UUID, foreign key to sessions.id)
- userId (string, not null)
- searchTerm (string, not null)
- timestamp (datetime, not null)

Table: proceed_to_payment
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
- id (UUID, primary key)
- sessionId (UUID, foreign key to sessions.id)
- productIds (comma-separated string, stored as array)
- cartValue (float, not null)
- currency (string, not null)
- productName (string, not null)
- userId (string, not null)
- timestamp (datetime, not null)

Table: feature_products
- id (UUID, primary key)
- sessionId (UUID, foreign key to sessions.id)
- productId (string, not null)
- productCost (float, not null)
- currency (string, not null)
- productName (string, not null)
- userId (string, not null)
- timestamp (datetime, not null)

Table: events
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
- id (UUID, primary key)
- sessionId (UUID, foreign key to sessions.id)
- userId (string, not null)
- pageUrl (string, not null)
- productName (string, not null)
- productId (string, not null)
- timestamp (datetime, not null)

Table: add_to_cart
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
- Product-related actions include product details and pricing
"""
    rag.process_text(sample_text, source_name="sample_document.txt")
    
    question = "What is the best performing product in terms of revenue?"
    # answer = rag.get_answer(question)
    # print(answer)
