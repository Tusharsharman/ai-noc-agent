from agent.llm import ask_llm


response = ask_llm(
    "You are an AI NOC assistant. "
    "Say hello in one sentence."
)

print("\n===== OLLAMA RESPONSE =====")
print(response)