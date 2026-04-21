from agents.base import llm

response = llm.invoke("Explain AI in one line")

print(response.content)