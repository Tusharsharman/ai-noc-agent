from agent.incident_store import list_incidents


def get_incident_history(
    exclude_incident_id=None,
    limit=5
):
    """
    Return recent historical incidents
    for AI investigation context.
    """

    incidents = list_incidents()

    filtered = []

    for incident in incidents:
        incident_id = incident.get("incident_id")

        if (
            exclude_incident_id
            and incident_id == exclude_incident_id
        ):
            continue

        filtered.append(incident)

    filtered.sort(
        key=lambda item: item.get(
            "detected_at",
            ""
        ),
        reverse=True
    )

    return filtered[:limit]


def find_similar_incidents(
    severity=None,
    cpu=None,
    memory=None,
    incident_mode=None,
    exclude_incident_id=None,
    limit=5
):
    """
    Find previous incidents with similar
    characteristics.
    """

    incidents = list_incidents()

    similar = []

    for incident in incidents:

        incident_id = incident.get(
            "incident_id"
        )

        if (
            exclude_incident_id
            and incident_id == exclude_incident_id
        ):
            continue

        score = 0

        evidence = incident.get(
            "evidence",
            {}
        )

        historical_severity = incident.get(
            "severity"
        )

        historical_cpu = evidence.get(
            "cpu"
        )

        historical_memory = evidence.get(
            "memory"
        )

        historical_mode = evidence.get(
            "incident_mode"
        )

        if (
            severity
            and historical_severity == severity
        ):
            score += 3

        if (
            incident_mode is not None
            and historical_mode == incident_mode
        ):
            score += 2

        if (
            cpu is not None
            and historical_cpu is not None
        ):
            if (
                cpu >= 90
                and historical_cpu >= 90
            ):
                score += 2

        if (
            memory is not None
            and historical_memory is not None
        ):
            if (
                memory >= 90
                and historical_memory >= 90
            ):
                score += 2

        if score > 0:
            similar.append(
                {
                    "score": score,
                    "incident": incident
                }
            )

    similar.sort(
        key=lambda item: (
            item["score"],
            item["incident"].get(
                "detected_at",
                ""
            )
        ),
        reverse=True
    )

    return [
        item["incident"]
        for item in similar[:limit]
    ]


def format_incident_history(
    incidents
):
    """
    Convert historical incidents into a
    compact text format for the AI model.
    """

    if not incidents:
        return (
            "No previous incidents are available."
        )

    lines = []

    for incident in incidents:

        incident_id = incident.get(
            "incident_id",
            "UNKNOWN"
        )

        status = incident.get(
            "status",
            "UNKNOWN"
        )

        severity = incident.get(
            "severity",
            "UNKNOWN"
        )

        detected_at = incident.get(
            "detected_at",
            "UNKNOWN"
        )

        evidence = incident.get(
            "evidence",
            {}
        )

        cpu = evidence.get(
            "cpu",
            "UNKNOWN"
        )

        memory = evidence.get(
            "memory",
            "UNKNOWN"
        )

        incident_mode = evidence.get(
            "incident_mode",
            "UNKNOWN"
        )

        investigation = incident.get(
            "investigation",
            {}
        )

        analysis = investigation.get(
            "analysis"
        )

        lines.append(
            f"Incident ID: {incident_id}\n"
            f"Status: {status}\n"
            f"Severity: {severity}\n"
            f"Detected At: {detected_at}\n"
            f"CPU: {cpu}%\n"
            f"Memory: {memory}%\n"
            f"Incident Mode: {incident_mode}\n"
            f"Investigation Completed: "
            f"{investigation.get('completed', False)}"
        )

        if analysis:
            lines.append(
                "Previous AI Analysis:\n"
                + analysis
            )

        lines.append(
            "-" * 50
        )

    return "\n".join(lines)


if __name__ == "__main__":

    print("=" * 60)
    print("AI NOC INCIDENT HISTORY TEST")
    print("=" * 60)

    print("\nRecent Incidents")
    print("-" * 60)

    recent = get_incident_history(
        limit=5
    )

    print(
        format_incident_history(
            recent
        )
    )

    print("\nSimilar Critical Incidents")
    print("-" * 60)

    similar = find_similar_incidents(
        severity="CRITICAL",
        cpu=95.0,
        memory=92.0,
        incident_mode=1,
        limit=5
    )

    print(
        format_incident_history(
            similar
        )
    )

    print("\nHistory module test completed.")
