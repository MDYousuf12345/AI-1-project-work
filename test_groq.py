import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "llama-3.1-8b-instant"

def test_groq():
    prompt = "Give 3 problems faced by schools in managing student data. Return JSON."

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Return only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        response_format={"type": "json_object"}
    )

    output = response.choices[0].message.content

    print("\n=== GROQ TEST OUTPUT ===\n")
    print(output)


if __name__ == "__main__":
    test_groq()