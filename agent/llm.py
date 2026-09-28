import requests


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:3b"


def ask_llm(prompt: str) -> str:
    """
    Send a prompt to the local Ollama LLM.
    """

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an AI NOC assistant. "
                    "Analyze infrastructure and application incidents "
                    "using only the evidence provided. "
                    "Do not invent facts. "
                    "Clearly distinguish confirmed observations from "
                    "hypotheses and recommendations."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    return data["message"]["content"]
