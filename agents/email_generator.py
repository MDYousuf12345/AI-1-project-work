# ============================================================
# KALNET AI-1 | Agent 3: Email Personaliser
# ============================================================

import os
import json
import re
import time
from google import genai

# ── GEMINI CLIENT SETUP ─────────────────────────────────────
from dotenv import load_dotenv
import os

load_dotenv()

google_api_key=os.getenv("GOOGLE_API_KEY")


client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
print("Gemini client ready")

# ── SYSTEM PROMPT ───────────────────────────────────────────
SYSTEM_PROMPT = """
You are a sharp, direct sales writer for KALNET — an EdTech company based in Hyderabad.

STRICT RULES:
1. Body MUST be under 120 words.
2. NEVER use: "I hope this finds you well", "synergy", "Dear Sir/Madam"
3. Use ONLY first name (e.g., Rahul, not Mr. Rahul)
4. Mention 1-2 pain points clearly
5. Offer 1 clear solution (based on given modules)
6. End with ONE clear next step (demo/call)
7. Tone: confident, simple, human — not corporate
8. MUST end EXACTLY with:
The KALNET Team | Hyderabad

Return STRICT JSON:
{
  "subject": "short subject",
  "body": "email body"
}

No extra text. No markdown. No explanation.
"""

# ── HELPER: FIRST NAME ──────────────────────────────────────
def get_first_name(name):
    if not name:
        return "there"
    name = name.replace("Mr.", "").replace("Mrs.", "").replace("Ms.", "")
    return name.strip().split()[0]

# ── GENERATE EMAIL ──────────────────────────────────────────
def generate_email(lead):
    try:
        first_name = get_first_name(lead.get("contact_name"))

        pain_points = ', '.join(lead.get('pain_points') or ["operational inefficiencies"])
        modules = ', '.join(lead.get('proposed_modules') or ["AI solutions"])
        next_step = lead.get('next_steps', ['Schedule a demo'])[0]

        prompt = f"""
Write a personalised cold email.

School: {lead.get('institution_name')}
Name: {first_name}
Role: {lead.get('contact_role')}

Pain Points:
{pain_points}

Solution:
{modules}

Next Step:
{next_step}

Return only JSON.
"""

        full_prompt = SYSTEM_PROMPT + "\n\n" + prompt

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt
        )

        raw = response.text.strip()
        raw = re.sub(r"```json|```", "", raw).strip()

        parsed = json.loads(raw)

        # VALIDATION
        if "subject" not in parsed or "body" not in parsed:
            raise ValueError("Missing subject/body")

        body = parsed["body"]

        # Ensure sign-off exists
        if "The KALNET Team | Hyderabad" not in body:
            body += "\n\nThe KALNET Team | Hyderabad"
            parsed["body"] = body

        # Word count check
        wc = len(body.split())
        if wc > 120:
            print(f"⚠️ Warning: {wc} words (limit 120)")

        return {"success": True, "data": parsed}

    except Exception as e:
        return {"success": False, "error": str(e)}

# ── RETRY HANDLER ───────────────────────────────────────────
def generate_email_with_retry(lead, retries=3):
    for i in range(retries):
        result = generate_email(lead)
        if result["success"]:
            return result

        if "429" in str(result.get("error")):
            wait = 30 * (i + 1)
            print(f"⏳ Waiting {wait}s due to rate limit...")
            time.sleep(wait)
        else:
            return result
    return result

# ── TEST DATA ───────────────────────────────────────────────
test = {
    "institution_name": "DPS Hyderabad",
    "contact_name": "Mr. Rahul Sharma",
    "contact_role": "Principal",
    "pain_points": [
        "manual attendance tracking",
        "lack of digital communication"
    ],
    "proposed_modules": [
        "AI Attendance System",
        "Parent Communication App"
    ],
    "next_steps": [
        "Schedule a 15-minute demo"
    ]
}

# ── RUN TEST ────────────────────────────────────────────────
print("\n===== FINAL OUTPUT =====")

result = generate_email_with_retry(test)

if result["success"]:
    print("\n SUBJECT:")
    print(result["data"]["subject"])

    print("\n BODY:")
    print(result["data"]["body"])

    print("\n WORD COUNT:", len(result["data"]["body"].split()))
else:
    print(" ERROR:", result["error"])
