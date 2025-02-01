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

# Move schema to module level
SCHEMA = """You are an SQL expert, this is the schema of all the tables of the models of the application.

Schema:
**Contextual Meaning for Each Column in the Provided Tables**

### **Table: sessions**
**Context:** Stores user session details, tracking website visits and user interactions.

| **Column Name** | **Contextual Meaning** |
|---------------|--------------------|
| `id` | Unique identifier for each user session. |
| `trackingId` | Identifier to track a specific user across multiple sessions. |
| `entryPage` | First page visited in the session. |
| `exitPage` | Last page visited in the session. |
| `timeSpent` | Total time spent in the session. |
| `utm_source` | Source of the traffic (e.g., Google, Facebook). |
| `utm_medium` | Marketing medium used (e.g., email, CPC, referral). |
| `utm_campaign_name` | Name of the marketing campaign. |
| `utm_campaign_id` | Unique identifier for the campaign. |
| `utm_term` | Keyword used in paid campaigns. |
| `utm_content` | Specific ad or link clicked by the user. |
| `os` | Operating system of the user’s device. |
| `device` | Type of device used (e.g., mobile, desktop). |
| `browser` | Browser used to access the website. |
| `longitude` | Geographic longitude of the user. |
| `latitude` | Geographic latitude of the user. |
| `city` | City from which the user accessed the website. |
| `country` | Country of the user. |
| `createdAt` | Time when the session started. |
| `updatedAt` | Last updated timestamp of the session. |

### **Table: signup**
**Context:** Stores information about users who have signed up.

| **Column Name** | **Contextual Meaning** |
|---------------|--------------------|
| `id` | Unique identifier for each signup record. |
| `sessionId` | Links the signup to a specific user session. |
| `userId` | Identifier of the user who signed up. |
| `timestamp` | Time when the user signed up. |

### **Table: search_bar**
**Context:** Stores user searches performed on the website.

| **Column Name** | **Contextual Meaning** |
|---------------|--------------------|
| `id` | Unique identifier for each search event. |
| `sessionId` | Links the search event to a user session. |
| `userId` | Identifier of the user who performed the search. |
| `searchTerm` | Search query entered by the user. |
| `timestamp` | Time when the search was performed. |

### **Table: proceed_to_payment**
**Context:** Logs the last step before purchase completion.

| **Column Name** | **Contextual Meaning** |
|---------------|--------------------|
| `id` | Unique identifier for each payment attempt. |
| `sessionId` | Links the action to a specific session. |
| `productIds` | List of product IDs included in the purchase. |
| `cartValue` | Total value of the cart at checkout. |
| `currency` | Currency used for the transaction. |
| `productName` | Name of the purchased product(s). |
| `userId` | Identifier of the user who proceeded to payment. |
| `timestamp` | Time when the user proceeded to payment. |
| `createdAt` | Record creation timestamp. |
| `updatedAt` | Last modification timestamp. |

### **Table: proceed_to_checkout**
**Context:** Logs the step before proceeding to payment.

| **Column Name** | **Contextual Meaning** |
|---------------|--------------------|
| `id` | Unique identifier for each checkout event. |
| `sessionId` | Links the action to a specific session. |
| `productIds` | List of product IDs being purchased. |
| `cartValue` | Total value of the cart at checkout. |
| `currency` | Currency used for the purchase. |
| `productName` | Name of the product(s) in the cart. |
| `userId` | Identifier of the user proceeding to checkout. |
| `timestamp` | Time when the user proceeded to checkout. |

### **Table: feature_products**
**Context:** Stores details of products featured on the website.

| **Column Name** | **Contextual Meaning** |
|---------------|--------------------|
| `id` | Unique identifier for each featured product record. |
| `sessionId` | Links the product display event to a session. |
| `productId` | Unique identifier for the featured product. |
| `productCost` | Price of the featured product. |
| `currency` | Currency in which the price is displayed. |
| `productName` | Name of the featured product. |
| `userId` | Identifier of the user viewing the featured product. |
| `timestamp` | Time when the product was featured. |

### **Table: events**
**Context:** Logs user interactions and platform activities.

| **Column Name** | **Contextual Meaning** |
|---------------|--------------------|
| `id` | Unique identifier for each event. |
| `sessionId` | Links the event to a specific session. |
| `eventName` | Name of the event (e.g., "Click", "Scroll"). |
| `eventType` | Type of event (e.g., "Navigation", "UI Interaction"). |
| `additionalData` | Metadata related to the event. |
| `timestamp` | Time when the event occurred. |
| `createdAt` | Record creation timestamp. |
| `updatedAt` | Last modification timestamp. |

### **Table: conversions**
**Context:** Logs user-defined conversion events.

| **Column Name** | **Contextual Meaning** |
|---------------|--------------------|
| `id` | Unique identifier for each conversion event. |
| `sessionId` | Links the conversion to a specific session. |
| `conversionType` | Type of conversion (e.g., "Purchase", "Lead"). |
| `conversionValue` | Value associated with the conversion. |
| `timestamp` | Time when the conversion occurred. |
| `createdAt` | Record creation timestamp. |
| `updatedAt` | Last modification timestamp. |

### **Table: add_to_favourites**
**Context:** Logs products added to user favorites.

| **Column Name** | **Contextual Meaning** |
|---------------|--------------------|
| `id` | Unique identifier for each favorite action. |
| `sessionId` | Links the action to a specific session. |
| `userId` | Identifier of the user adding the favorite. |
| `pageUrl` | URL of the page where the product was favorited. |
| `productName` | Name of the favorited product. |
| `productId` | Unique identifier of the favorited product. |
| `timestamp` | Time when the product was favorited. |

### **Table: add_to_cart**
**Context:** Logs products added to the shopping cart.

| **Column Name** | **Contextual Meaning** |
|---------------|--------------------|
| `id` | Unique identifier for each add-to-cart action. |
| `sessionId` | Links the action to a specific session. |
| `productId` | Unique identifier for the product. |
| `productCost` | Price of the product at the time of addition. |
| `currency` | Currency in which the price is displayed. |
| `productName` | Name of the product added. |
| `userId` | Identifier of the user adding the product. |
| `timestamp` | Time when the product was added to cart. |

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

Here’s an enhanced context description that will optimize the prompt for GPT models:

---

### **Application Schema & Context Overview**  

This schema represents a **user interaction tracking system** that monitors various user activities throughout their journey on the platform. The system is designed to collect **session-based analytics**, tracking everything from initial engagement to purchase behavior.  

#### **Core Concepts**  
- **Session-Based Tracking:** Each user interaction is linked to a unique `sessionId` in the `sessions` table, making it the central reference point for tracking user journeys.  
- **Event-Driven Architecture:** The schema captures **specific actions** like signing up, searching for products, adding items to cart, checking out, and making payments.  
- **Marketing Attribution:** The schema stores UTM parameters for tracking traffic sources and campaign effectiveness.  
- **Conversion Tracking:** Custom user-defined conversions are stored separately for better analytics.  
- **Geolocation & Device Tracking:** The system collects OS, browser, device, and location data to enhance user experience and optimize marketing strategies.  

---

### **Table Relationships & Use Cases**  

#### **1. `sessions` (Central Table)**
- Stores core session details for each user, including tracking ID, entry/exit pages, time spent, geolocation, device info, and marketing campaign data.  
- **Indexes:** `trackingId`, `createdAt` for efficient lookups and performance optimization.  

#### **2. `signup` (User Registration Events)**
- Tracks when users sign up, associating them with a session for attribution analysis.  

#### **3. `search_bar` (Search Behavior)**
- Captures user search queries and timestamps, allowing analysis of search trends and intent.  

#### **4. `add_to_cart` (First Step in Buying Journey)**
- Tracks product additions to the cart, storing product details, currency, and user information.  

#### **5. `proceed_to_checkout` (Second to Last Step in Buying Journey)**
- Captures users who proceed to checkout, storing cart value, product details, and currency.  

#### **6. `proceed_to_payment` (Final Step Before Purchase)**
- Logs checkout-to-payment transitions, including product details, total cart value, and user ID.  

#### **7. `feature_products` (Promoted Product Tracking)**
- Monitors featured products viewed by users, useful for A/B testing and recommendations.  

#### **8. `add_to_favourites` (Wishlist Actions)**
- Tracks products added to favorites for interest analysis and retargeting.  

#### **9. `events` (General User Activity Tracking)**
- Captures custom platform events, including event types and additional metadata in JSON format.  
- **Indexes:** `sessionId`, `timestamp` for quick retrieval.  

#### **10. `conversions` (User-Defined Conversion Tracking)**
- Stores custom conversion events with assigned values, useful for marketing performance measurement.  
- **Indexes:** `sessionId`, `timestamp` for efficient reporting.  

---

### **Common Schema Patterns**  
- **Session-Based Relationships:** Almost all tables link to `sessions` via `sessionId`, making it the central tracking entity.  
- **Timestamped Events:** Every action has a timestamp for chronological event tracking.  
- **Product Information Consistency:** Product-related tables (`add_to_cart`, `proceed_to_checkout`, `proceed_to_payment`, `feature_products`) share a similar structure for uniformity.  
- **Indexing for Performance:** Key tables include indexes on `sessionId`, `timestamp`, and `trackingId` for optimized queries.  

This schema **enables comprehensive user journey tracking**, supporting analytics, conversion optimization, and personalized experiences.

"""

def get_sql_query(question):
    messages = [
        ("system", f"You are an SQL expert. Generate ONLY the SQL query without any text or 'SQL:' prefix. {SCHEMA}"),
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
        {SCHEMA}"""),
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