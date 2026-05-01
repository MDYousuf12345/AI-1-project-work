# ============================================================
# KALNET AI-1 | Agent 3: Email Personaliser
# ============================================================

import os
import json
import re
from groq import Groq

# SET YOUR API KEY 
os.environ["GROQ_API_KEY"] = "your_api_key_here"

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

print("Groq client ready")

# ── SYSTEM PROMPT ───────────────────────────────────────────
SYSTEM_PROMPT = """
You are a sharp, direct sales writer for KALNET — an EdTech company based in Hyderabad.

STRICT RULES:
1. Body MUST be under 120 words
2. NEVER use: "I hope this finds you well", "synergy", "Dear Sir/Madam"
3. Use ONLY first name (NO titles like Mr, Ms, Principal)
4. Mention 1-2 pain points clearly
5. Offer 1 clear solution
6. End with ONE clear next step (demo/call)
7. Tone: confident, simple, human — NOT generic or corporate
8. MUST end EXACTLY with:
The KALNET Team | Hyderabad

Return STRICT JSON:
{
  "subject": "",
  "body": ""
}
ONLY return JSON.
"""

# ── HELPER ──────────────────────────────────────────────────
def get_first_name(name):
    if not name:
        return "there"
    name = re.sub(r"(Mr\.|Ms\.|Mrs\.)", "", name)
    return name.strip().split()[0]

# ── GENERATE EMAIL ──────────────────────────────────────────
def generate_email(lead):
    try:
        first_name = get_first_name(lead.get("contact_name"))

        prompt = f"""
Write a personalised cold email.

School: {lead.get('institution_name')}
Name: {first_name}
Role: {lead.get('contact_role')}

Pain Points:
{', '.join(lead.get('pain_points'))}

Solution:
{', '.join(lead.get('proposed_modules'))}

Next Step:
{lead.get('next_steps')[0]}
"""

        # GROQ CALL (Structured JSON)
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )

        raw = response.choices[0].message.content

        # Direct JSON parse (no regex needed)
        data = json.loads(raw)

        body = data["body"]

        # Fix formatting
        body = body.replace("\\n", "\n")

        # Remove unwanted titles if any
        body = re.sub(r"(Dear\s+)(Mr\.|Ms\.|Mrs\.|Principal)\s*", r"\1", body)

        # Ensure proper signature format
        if "The KALNET Team | Hyderabad" in body:
            body = body.replace("The KALNET Team | Hyderabad", "").strip()

        body += "\n\nThe KALNET Team | Hyderabad"

        data["body"] = body

        return {"success": True, "data": data}

    except Exception as e:
        return {"success": False, "error": str(e)}

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

# ── RUN ─────────────────────────────────────────────────────
print("\n===== FINAL OUTPUT =====")

result = generate_email(test)

if result["success"]:
    print("\nSUBJECT:\n", result["data"]["subject"])
    print("\nBODY:\n", result["data"]["body"])
    print("\nWORD COUNT:", len(result["data"]["body"].split()))
else:
    print("ERROR:", result["error"])
