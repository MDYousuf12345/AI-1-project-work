import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=api_key,
    temperature=0.3
)

def create_response(success: bool, data=None, error=None):
    return {
        "success": success,
        "data": data if data else {},
        "error": error
    }
result=llm.invoke("say hello and write a pome")
print(result)