import os

import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv


load_dotenv()


# =========================================================
# CONFIGURATION
# =========================================================

JIRA_CLOUD_ID = os.getenv("JIRA_CLOUD_ID")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv(
    "JIRA_PROJECT_KEY",
    "NOC"
)

JIRA_BASE_URL = (
    f"https://api.atlassian.com/ex/jira/{JIRA_CLOUD_ID}"
)


# Jira transition IDs confirmed from the project workflow
JIRA_TRANSITION_TO_DO = "21"
JIRA_TRANSITION_IN_PROGRESS = "31"
JIRA_TRANSITION_DONE = "41"


# =========================================================
# CONFIG VALIDATION
# =========================================================

def validate_config():
    required = {
        "JIRA_CLOUD_ID": JIRA_CLOUD_ID,
        "JIRA_EMAIL": JIRA_EMAIL,
        "JIRA_API_TOKEN": JIRA_API_TOKEN,
        "JIRA_PROJECT_KEY": JIRA_PROJECT_KEY,
    }

    missing = [
        key
        for key, value in required.items()
        if not value
    ]

    if missing:
        raise RuntimeError(
            "Missing Jira configuration: "
            + ", ".join(missing)
        )


# =========================================================
# GENERIC JIRA REQUEST
# =========================================================

def jira_request(
    method,
    endpoint,
    payload=None
):
    validate_config()

    url = f"{JIRA_BASE_URL}{endpoint}"

    response = requests.request(
        method=method,
        url=url,
        auth=HTTPBasicAuth(
            JIRA_EMAIL,
            JIRA_API_TOKEN
        ),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=20,
    )

    if not response.ok:
        raise RuntimeError(
            f"Jira API error "
            f"{response.status_code}: "
            f"{response.text}"
        )

    if response.text:
        return response.json()

    return {}


# =========================================================
# PROJECT
# =========================================================

def get_project():
    return jira_request(
        "GET",
        f"/rest/api/3/project/"
        f"{JIRA_PROJECT_KEY}"
    )


# =========================================================
# CREATE ISSUE
# =========================================================

def create_issue(
    summary,
    description,
    issue_type="Task"
):
    payload = {
        "fields": {
            "project": {
                "key": JIRA_PROJECT_KEY
            },
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": description
                            }
                        ]
                    }
                ]
            },
            "issuetype": {
                "name": issue_type
            }
        }
    }

    return jira_request(
        "POST",
        "/rest/api/3/issue",
        payload
    )


# =========================================================
# INCIDENT ISSUE CREATION
# =========================================================

def create_incident_issue(
    incident_id,
    severity,
    detected_at,
    cpu,
    memory,
    incident_mode,
    investigation
):
    summary = (
        f"[{severity}] "
        f"AI NOC Incident - "
        f"{incident_id}"
    )

    description = (
        "AI NOC Agent Incident\n\n"
        f"Incident ID: {incident_id}\n"
        f"Severity: {severity}\n"
        f"Detected At: {detected_at}\n\n"

        "Infrastructure Metrics\n\n"
        f"CPU Usage: {cpu}%\n"
        f"Memory Usage: {memory}%\n"
        f"Incident Mode: {incident_mode}\n\n"

        "AI Investigation\n\n"
        f"{investigation}\n\n"

        "Incident Status\n\n"
        "ACTIVE\n\n"

        "This issue was automatically "
        "created by the AI NOC Agent."
    )

    return create_issue(
        summary=summary,
        description=description,
        issue_type="Task"
    )


# =========================================================
# ADD COMMENT
# =========================================================

def add_comment(
    issue_key,
    comment
):
    payload = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": comment
                        }
                    ]
                }
            ]
        }
    }

    return jira_request(
        "POST",
        f"/rest/api/3/issue/"
        f"{issue_key}/comment",
        payload
    )


# =========================================================
# JIRA STATUS TRANSITION
# =========================================================

def transition_issue(
    issue_key,
    transition_id
):
    payload = {
        "transition": {
            "id": str(transition_id)
        }
    }

    return jira_request(
        "POST",
        f"/rest/api/3/issue/"
        f"{issue_key}/transitions",
        payload
    )


# =========================================================
# MOVE TO IN PROGRESS
# =========================================================

def move_issue_to_in_progress(
    issue_key
):
    return transition_issue(
        issue_key,
        JIRA_TRANSITION_IN_PROGRESS
    )


# =========================================================
# MOVE TO DONE
# =========================================================

def move_issue_to_done(
    issue_key
):
    return transition_issue(
        issue_key,
        JIRA_TRANSITION_DONE
    )


# =========================================================
# CONNECTION TEST
# =========================================================

def test_connection():
    print("\n==============================")
    print("JIRA CONNECTION TEST")
    print("==============================")

    project = get_project()

    print(
        "Connected successfully!"
    )

    print(
        f"Project Name: "
        f"{project.get('name')}"
    )

    print(
        f"Project Key: "
        f"{project.get('key')}"
    )


# =========================================================
# INCIDENT CREATION TEST
# =========================================================

def test_incident_creation():
    print("\n==============================")
    print("CREATING TEST NOC INCIDENT")
    print("==============================")

    issue = create_incident_issue(
        incident_id="INC-TEST-NOC-LIFECYCLE",
        severity="CRITICAL",
        detected_at="2026-09-28 12:00:00",
        cpu=95.0,
        memory=92.0,
        incident_mode=1,
        investigation=(
            "CPU and memory usage are elevated. "
            "Kubernetes has a pod in "
            "ImagePullBackOff. "
            "Kubernetes events indicate an "
            "image pull failure. "
            "The overall root cause "
            "is not confirmed."
        )
    )

    print(
        "Jira incident created successfully!"
    )

    print(
        f"Issue Key: "
        f"{issue.get('key')}"
    )

    print(
        f"Issue ID: "
        f"{issue.get('id')}"
    )

    print(
        "\nJira URL:"
        f"\nhttps://tushardevops.atlassian.net/"
        f"browse/{issue.get('key')}"
    )

    return issue.get("key")


# =========================================================
# LIFECYCLE TEST
# =========================================================

def test_incident_lifecycle():
    print("\n==============================")
    print("JIRA INCIDENT LIFECYCLE TEST")
    print("==============================")

    issue_key = test_incident_creation()

    print("\nMoving issue to In Progress...")

    move_issue_to_in_progress(
        issue_key
    )

    print(
        f"Jira issue {issue_key} "
        "moved to IN PROGRESS."
    )

    add_comment(
        issue_key,
        (
            "AI NOC Agent investigation "
            "started. Automated diagnostic "
            "analysis is in progress."
        )
    )

    print(
        "Investigation comment added."
    )

    print("\nMoving issue to Done...")

    move_issue_to_done(
        issue_key
    )

    print(
        f"Jira issue {issue_key} "
        "moved to DONE."
    )

    add_comment(
        issue_key,
        (
            "AI NOC Agent lifecycle test "
            "completed successfully."
        )
    )

    print(
        "Completion comment added."
    )

    print("\n==============================")
    print(
        "JIRA LIFECYCLE TEST PASSED"
    )
    print("==============================")


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    try:

        test_connection()

        test_incident_lifecycle()

    except Exception as exc:

        print("\n==============================")
        print("JIRA INTEGRATION FAILED")
        print("==============================")

        print(
            f"\nError:\n{exc}"
        )

        raise SystemExit(1)
