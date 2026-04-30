# agents/proposal_generator.py

import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# Load environment variables
load_dotenv()

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.3,
    response_mime_type="application/json"
)


def load_prompt():
    """Load prompt from txt file"""
    prompt_path = os.path.join("prompts", "proposal_generator.txt")
    with open(prompt_path, "r", encoding="utf-8") as file:
        return file.read()


def generate_proposal(user_input: str):
    """
    Takes plain client requirement text and returns structured proposal
    """

    try:
        # Load prompt template
        prompt_template = load_prompt()

        # Format prompt using LangChain
        template = PromptTemplate.from_template(prompt_template)
        prompt = template.format(input=user_input)

        # Call LLM
        response = llm.invoke(prompt)

        # Parse JSON output
        data = json.loads(response.content)

        return {
            "success": True,
            "data": data,
            "error": None
        }

    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": str(e)
        }