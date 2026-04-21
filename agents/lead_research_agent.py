import os
import json
import time
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.3,
    response_mime_type="application/json"
)

AI2_API_BASE = os.getenv("AI2_API_BASE", "http://localhost:8001")

def load_prompt():
    current_dir = os.path.dirname(__file__)
    prompt_path = os.path.join(current_dir, "..", "prompts", "lead_research.txt")
    prompt_path = os.path.abspath(prompt_path)

    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def get_lead_from_ai2(lead_id):
    if not lead_id:
        return {}

    try:
        url = f"{AI2_API_BASE}/leads/{lead_id}"
        r = requests.get(url, timeout=10)

        if r.status_code == 200:
            return r.json()

    except:
        pass

    return {}


def scrape_website(base_url):

    if not base_url:
        return "Website content not available"

    base_url = base_url.rstrip("/")

    possible_urls = [
        base_url + "/about",
        base_url + "/about-us",
        base_url + "/about-school",
        base_url
    ]

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for url in possible_urls:

        try:

            response = requests.get(
                url,
                timeout=10,
                headers=headers
            )

            response.raise_for_status()

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            for tag in soup(["script","style","nav","footer"]):
                tag.decompose()

            paragraphs = soup.find_all("p")

            headings = soup.find_all(
                ["h1","h2","h3"]
            )

            text_parts = []

            for tag in headings + paragraphs:

                text = tag.get_text(strip=True)

                if text:
                    text_parts.append(text)

            final_text = " ".join(text_parts)

            if final_text.strip():
                return final_text[:1500]

        except:
            continue

    return "Website content not available"


def get_fallback_output(input_text):

    return {

        "name": "Not available",

        "location": "Not available",

        "size": "Not available",

        "contacts": [
            {
                "name": "Not available",
                "role": "Not available",
                "email": None
            }
        ],

        "pain_points": [
            "AI insights temporarily unavailable due to API quota or key issue",
            "Institution-specific analysis is pending",
            "Full research output will be available once Gemini access resumes"
        ],

        "recommended_approach":
        f"Fallback mode active. Institution input received: {input_text[:200]}. Full AI-generated insights will appear once Gemini API access is restored."

    }


def run_lead_research(input_text="", website=None, lead_id=None):

    prompt = load_prompt()

    ai2_data = get_lead_from_ai2(lead_id)

    website_text = scrape_website(website) if website else "Website content not available"

    final_prompt = f"""
{prompt}

AI-2 DATABASE DATA:
{json.dumps(ai2_data, indent=2) if ai2_data else "(no data from AI-2)"}

INSTITUTION INFO:
{input_text or "(none provided)"}

WEBSITE CONTENT:
{website_text}

Return JSON only.
"""

    retries = 2

    for attempt in range(retries + 1):

        try:

            response = llm.invoke(final_prompt)

            raw_output = response.content.strip()

            if raw_output.startswith("```json"):
                raw_output = raw_output.replace("```json","").replace("```","").strip()

            elif raw_output.startswith("```"):
                raw_output = raw_output.replace("```","").strip()

            parsed_output = json.loads(raw_output)

            return {

                "success": True,

                "data": parsed_output,

                "error": None

            }

        except Exception as e:

            error_message = str(e)

            if "API_KEY_INVALID" in error_message or "API key expired" in error_message:

                return {

                    "success": False,

                    "data": {},

                    "error": "API key expired or invalid"

                }

            if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:

                if attempt < retries:

                    time.sleep(20)

                    continue

                return {

                    "success": True,

                    "data": get_fallback_output(input_text),

                    "error": "Gemini quota exhausted"

                }

            return {

                "success": False,

                "data": {},

                "error": error_message

            }


if __name__ == "__main__":

    sample_input = """
Delhi Public School Bangalore is a CBSE school with a large student population focusing on academic excellence and technology-enabled learning.
"""
    website = "https://dpsbangalore.edu.in"

    result = run_lead_research(

        input_text=sample_input,

        website=website

    )

    print(json.dumps(result, indent=4))