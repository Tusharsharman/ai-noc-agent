import json

from pathlib import Path

from datetime import datetime, timezone


INCIDENTS_DIR = Path("incidents")

INCIDENTS_DIR.mkdir(exist_ok=True)


def _incident_file(incident_id: str) -> Path:
    return INCIDENTS_DIR / f"{incident_id}.json"


def save_incident(incident: dict):
    """
    Save or update an incident record.
    """

    incident_id = incident["incident_id"]

    file_path = _incident_file(incident_id)

    with file_path.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            incident,
            file,
            indent=4,
            ensure_ascii=False
        )


def load_incident(incident_id: str):
    """
    Load an incident by incident ID.
    """

    file_path = _incident_file(incident_id)

    if not file_path.exists():
        return None

    with file_path.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def update_incident(
    incident_id: str,
    **updates
):
    """
    Update selected fields of an existing incident.
    """

    incident = load_incident(incident_id)

    if incident is None:
        return None

    incident.update(updates)

    incident["updated_at"] = datetime.now(
        timezone.utc
    ).isoformat()

    save_incident(incident)

    return incident


def list_incidents():
    """
    Return all stored incidents.
    """

    incidents = []

    for file_path in sorted(
        INCIDENTS_DIR.glob("INC-*.json")
    ):

        try:

            with file_path.open(
                "r",
                encoding="utf-8"
            ) as file:

                incidents.append(
                    json.load(file)
                )

        except Exception:

            continue

    return incidents


def get_recent_incidents(
    limit: int = 5
):
    """
    Return the most recently updated incidents.
    """

    incidents = list_incidents()

    incidents.sort(
        key=lambda incident: incident.get(
            "updated_at",
            ""
        ),
        reverse=True
    )

    return incidents[:limit]


def search_incidents(
    query: str,
    limit: int = 5
):
    """
    Search historical incidents using
    keywords from the incident record.

    The search is intentionally simple and
    deterministic so that the AI only receives
    incidents that actually exist in the store.
    """

    if not query:
        return []

    query_terms = [
        term.lower()
        for term in query.split()
        if term.strip()
    ]

    if not query_terms:
        return []

    incidents = list_incidents()

    matches = []

    for incident in incidents:

        try:

            searchable_text = json.dumps(
                incident,
                ensure_ascii=False
            ).lower()

        except Exception:

            continue

        matched_terms = 0

        for term in query_terms:

            if term in searchable_text:
                matched_terms += 1

        if matched_terms > 0:

            matches.append(
                (
                    matched_terms,
                    incident
                )
            )

    matches.sort(
        key=lambda item: (
            item[0],
            item[1].get(
                "updated_at",
                ""
            )
        ),
        reverse=True
    )

    return [
        incident
        for _, incident in matches[:limit]
    ]


def get_active_incidents():
    """
    Return incidents that are currently active.
    """

    incidents = list_incidents()

    return [
        incident
        for incident in incidents
        if incident.get("status") == "ACTIVE"
    ]


def create_incident(
    incident_id: str,
    severity: str,
    cpu,
    memory,
    incident_mode
):
    """
    Create a new incident record.
    """

    now = datetime.now(
        timezone.utc
    ).isoformat()

    incident = {

        "incident_id": incident_id,

        "status": "ACTIVE",

        "severity": severity,

        "detected_at": now,

        "updated_at": now,

        "evidence": {

            "cpu": cpu,

            "memory": memory,

            "incident_mode": incident_mode

        },

        "recovery": {

            "healthy_checks": 0,

            "required_checks": 3,

            "recovered_at": None

        },

        "investigation": {

            "completed": False,

            "analysis": None

        }

    }

    save_incident(incident)

    return incident


def mark_investigation_complete(
    incident_id: str,
    analysis: str
):
    """
    Store the AI investigation result.
    """

    incident = load_incident(
        incident_id
    )

    if incident is None:
        return None

    incident["investigation"] = {

        "completed": True,

        "analysis": analysis

    }

    incident["updated_at"] = datetime.now(
        timezone.utc
    ).isoformat()

    save_incident(incident)

    return incident


def mark_recovered(
    incident_id: str,
    cpu,
    memory,
    incident_mode,
    healthy_checks: int = 3
):
    """
    Mark an incident as recovered.
    """

    incident = load_incident(
        incident_id
    )

    if incident is None:
        return None

    recovered_at = datetime.now(
        timezone.utc
    ).isoformat()

    incident["status"] = "RECOVERED"

    incident["recovery"] = {

        "healthy_checks": healthy_checks,

        "required_checks": 3,

        "recovered_at": recovered_at,

        "recovery_evidence": {

            "cpu": cpu,

            "memory": memory,

            "incident_mode": incident_mode

        }

    }

    incident["updated_at"] = recovered_at

    save_incident(incident)

    return incident


if __name__ == "__main__":

    print(
        "========================================"
    )

    print(
        "       INCIDENT STORE TEST"
    )

    print(
        "========================================"
    )

    test_id = "INC-TEST-001"

    print(
        "\nCreating test incident..."
    )

    incident = create_incident(

        incident_id=test_id,

        severity="CRITICAL",

        cpu=95.0,

        memory=92.0,

        incident_mode=1

    )

    print(
        json.dumps(
            incident,
            indent=4
        )
    )

    print(
        "\nUpdating investigation..."
    )

    update_incident(

        test_id,

        investigation={

            "completed": True,

            "analysis": (
                "Test investigation "
                "for CPU and memory incident."
            )

        }

    )

    print(
        "\nLoading incident..."
    )

    loaded = load_incident(
        test_id
    )

    print(
        json.dumps(
            loaded,
            indent=4
        )
    )

    print(
        "\nTesting historical search..."
    )

    results = search_incidents(
        "CPU memory incident",
        limit=5
    )

    for item in results:

        print(
            item["incident_id"],
            "|",
            item["status"],
            "|",
            item["severity"]
        )

    print(
        "\nMarking incident recovered..."
    )

    recovered = mark_recovered(

        incident_id=test_id,

        cpu=20.0,

        memory=60.0,

        incident_mode=0

    )

    print(
        json.dumps(
            recovered,
            indent=4
        )
    )

    print(
        "\nRecent incidents:"
    )

    recent = get_recent_incidents(
        limit=5
    )

    for item in recent:

        print(
            item["incident_id"],
            "|",
            item["status"],
            "|",
            item["severity"]
        )

    print(
        "\nAll incidents:"
    )

    for item in list_incidents():

        print(
            item["incident_id"],
            "|",
            item["status"],
            "|",
            item["severity"]
        )
