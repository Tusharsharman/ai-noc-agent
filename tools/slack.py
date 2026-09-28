import os

import requests
from dotenv import load_dotenv


load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


def send_slack_message(message: str):
    """
    Send a plain-text message to the configured Slack channel.
    """

    if not SLACK_WEBHOOK_URL:
        raise RuntimeError(
            "SLACK_WEBHOOK_URL is not configured."
        )

    response = requests.post(
        SLACK_WEBHOOK_URL,
        json={
            "text": message
        },
        timeout=10
    )

    response.raise_for_status()

    return response.text


if __name__ == "__main__":

    test_message = """🤖 AI NOC Agent Connected

Status: ONLINE
Monitoring: Prometheus
AI Engine: Ollama
Kubernetes: Connected
"""

    print("Sending test message to Slack...")

    result = send_slack_message(test_message)

    print("Slack response:", result)
    print("Slack test completed successfully.")