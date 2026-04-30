import os
import json
import time
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

GROQ_MODEL = "llama-3.1-8b-instant"
AI2_API_BASE = os.getenv("AI2_API_BASE", "http://localhost:8001")


def call_groq_json(prompt):
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You return only valid JSON. No markdown. No explanation."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)


def load_prompt():
    current_dir = os.path.dirname(__file__)
    prompt_path = os.path.join(current_dir, "..", "prompts", "lead_research.txt")
    prompt_path = os.path.abspath(prompt_path)

    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def get_lead_from_ai2(lead_id):
    if not lead_id:
        return {}

    url = f"{AI2_API_BASE}/leads/{lead_id}"
    print(f"\nAI-2 URL CALLED:\n{url}")

    try:
        r = requests.get(url, timeout=10)
        print(f"\nAI-2 STATUS CODE:\n{r.status_code}")

        if r.status_code == 200:
            return r.json()

        print("\nAI-2 RAW RESPONSE:\n", r.text[:500])

    except Exception as e:
        print(f"\nAI-2 REQUEST FAILED:\n{str(e)}")

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

    headers = {"User-Agent": "Mozilla/5.0"}

    for url in possible_urls:
        try:
            response = requests.get(url, timeout=10, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            for tag in soup(["script", "style", "nav", "footer"]):
                tag.decompose()

            paragraphs = soup.find_all("p")
            headings = soup.find_all(["h1", "h2", "h3"])

            text_parts = []

            for tag in headings + paragraphs:
                text = tag.get_text(strip=True)
                if text:
                    text_parts.append(text)

            final_text = " ".join(text_parts)

            if final_text.strip():
                return final_text[:1500]

        except Exception:
            continue

    return "Website content not available"


def build_input_text_from_ai2(ai2_data):
    if not ai2_data:
        return ""

    name = ai2_data.get("name") or ai2_data.get("institution_name") or "Not available"
    location = ai2_data.get("location", "Not available")
    description = ai2_data.get("description", "Not available")
    email = ai2_data.get("email", "Not available")
    phone = ai2_data.get("phone", "Not available")

    return f"""
Name: {name}
Location: {location}
Description: {description}
Email: {email}
Phone: {phone}
""".strip()


def get_fallback_output(input_text, ai2_data=None):
    detected_name = "Not available"
    detected_location = "Not available"

    if ai2_data:
        detected_name = ai2_data.get("name") or ai2_data.get("institution_name") or "Not available"
        detected_location = ai2_data.get("location", "Not available")
    else:
        lines = [line.strip() for line in input_text.splitlines() if line.strip()]
        if lines:
            detected_name = lines[0]

        if "Hyderabad" in input_text:
            detected_location = "Hyderabad"
        elif "Bangalore" in input_text:
            detected_location = "Bangalore"
        elif "Mumbai" in input_text:
            detected_location = "Mumbai"
        elif "Delhi" in input_text:
            detected_location = "Delhi"

    return {
        "name": detected_name,
        "location": detected_location,
        "size": "Not available",
        "contacts": "Not available",
        "pain_points": [
            "AI insights temporarily unavailable",
            "Institution-specific analysis is pending",
            "Full research output will be available once API access resumes"
        ],
        "recommended_approach": "Not available"
    }


def run_lead_research(input_text="", website=None, lead_id=None):
    prompt = load_prompt()

    ai2_data = get_lead_from_ai2(lead_id) if lead_id else {}
    print("\nAI-2 DATA RECEIVED:\n", ai2_data)

    if ai2_data and not input_text:
        input_text = build_input_text_from_ai2(ai2_data)

    if ai2_data and not website:
        website = ai2_data.get("website")

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
            parsed_output = call_groq_json(final_prompt)

            return {
                "success": True,
                "data": parsed_output,
                "error": None
            }

        except Exception as e:
            error_message = str(e)

            if "429" in error_message or "rate_limit" in error_message.lower():
                if attempt < retries:
                    time.sleep(20)
                    continue

                return {
                    "success": True,
                    "data": get_fallback_output(input_text, ai2_data),
                    "error": "Groq rate limit reached"
                }

            return {
                "success": False,
                "data": {},
                "error": error_message
            }


if __name__ == "__main__":
    TEST_MODE = "manual"

    if TEST_MODE == "manual":
        sample_input = """
Delhi Public School Bangalore is a CBSE school in Bangalore with a large student population, strong academics, and emphasis on science and digital education.
"""
        website = "https://dpsbangalore.edu.in"

        result = run_lead_research(
            input_text=sample_input,
            website=website
        )

    elif TEST_MODE == "api":
        result = run_lead_research(lead_id=1)

    print("\n--- FINAL OUTPUT ---\n")
    print(json.dumps(result, indent=4))