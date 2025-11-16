from fastapi import FastAPI
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langserve import add_routes
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OpenAI API key is missing. Put it in your .env")

# Initialize FastAPI app
app = FastAPI(
    title="Langchain Server",
    version="1.0",
    description="A simple API Server"
)

# Initialize OpenAI model
openai_chat = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

# Groq model - with better error handling
GROQ_AVAILABLE = False
groq_chat = None

if os.getenv("GROQ_API_KEY"):
    try:
        groq_chat = ChatGroq(
            model="llama-3.1-8b-instant",  # Updated to a more available model
            temperature=0.2,
            api_key=os.getenv("GROQ_API_KEY")
        )
        # Test the connection
        groq_chat.invoke("Hello")
        GROQ_AVAILABLE = True
        print("✅ Groq initialized successfully")
    except Exception as e:
        print(f"❌ Groq initialization failed: {e}")
        GROQ_AVAILABLE = False
else:
    print("⚠️  Groq API key missing. Poem feature will use OpenAI as fallback.")

# Essay prompt (using OpenAI)
prompt_essay = ChatPromptTemplate.from_template(
    "Write a concise 100-words essay about {topic}"
)

# Poem prompt 
prompt_poem = ChatPromptTemplate.from_template(
    "Write a 100 word poem about {topic} suitable for a 5 years old."
)

# Routes
add_routes(
    app,
    openai_chat,
    path="/openai"
)

add_routes(
    app,
    prompt_essay | openai_chat,
    path="/essay"
)

# Poem route with proper fallback
if GROQ_AVAILABLE and groq_chat is not None:
    add_routes(
        app,
        prompt_poem | groq_chat,
        path="/poem"
    )
    print("✅ Poem route using Groq")
else:
    add_routes(
        app,
        prompt_poem | openai_chat, 
        path="/poem"
    )
    print("✅ Poem route using OpenAI as fallback")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "openai_available": True,
        "groq_available": GROQ_AVAILABLE
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8999)