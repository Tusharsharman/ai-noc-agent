from fastapi import FastAPI, HTTPException
from prometheus_client import Gauge, generate_latest
from starlette.responses import Response

from agent.incident_store import (
    list_incidents,
    get_active_incidents,
    load_incident,
)

app = FastAPI(
    title="AI NOC Agent",
    description="AI-powered NOC incident investigation and monitoring agent",
    version="0.4.0",
)


# ============================================================
# PROMETHEUS METRICS
# ============================================================

ACTIVE_INCIDENTS = Gauge(
    "noc_active_incidents",
    "Number of currently active NOC incidents",
)

CRITICAL_INCIDENTS = Gauge(
    "noc_critical_incidents",
    "Number of currently active critical incidents",
)

HIGH_INCIDENTS = Gauge(
    "noc_high_incidents",
    "Number of currently active high severity incidents",
)

WARNING_INCIDENTS = Gauge(
    "noc_warning_incidents",
    "Number of currently active warning incidents",
)

TOTAL_INCIDENTS = Gauge(
    "noc_total_incidents",
    "Total number of incidents stored by the AI NOC agent",
)

RECOVERED_INCIDENTS = Gauge(
    "noc_recovered_incidents",
    "Number of recovered incidents stored by the AI NOC agent",
)

AI_INVESTIGATIONS_COMPLETED = Gauge(
    "noc_ai_investigations_completed",
    "Number of incidents with completed AI investigations",
)

AI_INVESTIGATIONS_FAILED = Gauge(
    "noc_ai_investigations_failed",
    "Number of incidents where AI investigation failed",
)


# ============================================================
# METRIC UPDATE LOGIC
# ============================================================

def update_metrics():
    incidents = list_incidents()
    active_incidents = get_active_incidents()

    critical_count = 0
    high_count = 0
    warning_count = 0
    recovered_count = 0
    ai_completed_count = 0
    ai_failed_count = 0

    for incident in incidents:
        status = str(
            incident.get("status", "")
        ).upper()

        severity = str(
            incident.get("severity", "")
        ).upper()

        # Recovered incidents
        if status == "RECOVERED":
            recovered_count += 1

        # Active severity counts
        if severity == "CRITICAL" and status == "ACTIVE":
            critical_count += 1

        elif severity == "HIGH" and status == "ACTIVE":
            high_count += 1

        elif severity == "WARNING" and status == "ACTIVE":
            warning_count += 1

        # AI investigation status
        investigation = incident.get(
            "investigation",
            {}
        )

        if isinstance(investigation, dict):

            if investigation.get("completed") is True:
                ai_completed_count += 1

            analysis = str(
                investigation.get(
                    "analysis",
                    ""
                )
            )

            if analysis.startswith(
                "AI investigation failed."
            ):
                ai_failed_count += 1

    ACTIVE_INCIDENTS.set(
        len(active_incidents)
    )

    CRITICAL_INCIDENTS.set(
        critical_count
    )

    HIGH_INCIDENTS.set(
        high_count
    )

    WARNING_INCIDENTS.set(
        warning_count
    )

    TOTAL_INCIDENTS.set(
        len(incidents)
    )

    RECOVERED_INCIDENTS.set(
        recovered_count
    )

    AI_INVESTIGATIONS_COMPLETED.set(
        ai_completed_count
    )

    AI_INVESTIGATIONS_FAILED.set(
        ai_failed_count
    )


# ============================================================
# ROOT / HEALTH
# ============================================================

@app.get("/")
def root():
    return {
        "service": "AI NOC Agent",
        "status": "running",
        "version": "0.4.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# ============================================================
# INCIDENT APIs
# ============================================================

@app.get("/incidents")
def get_incidents():
    incidents = list_incidents()

    return {
        "count": len(incidents),
        "incidents": incidents,
    }


@app.get("/incidents/active")
def get_active():
    incidents = get_active_incidents()

    return {
        "count": len(incidents),
        "incidents": incidents,
    }


@app.get("/incidents/summary")
def get_incident_summary():
    incidents = list_incidents()

    active_count = 0
    critical_count = 0
    high_count = 0
    warning_count = 0
    recovered_count = 0

    for incident in incidents:

        status = str(
            incident.get("status", "")
        ).upper()

        severity = str(
            incident.get("severity", "")
        ).upper()

        if status == "ACTIVE":
            active_count += 1

            if severity == "CRITICAL":
                critical_count += 1

            elif severity == "HIGH":
                high_count += 1

            elif severity == "WARNING":
                warning_count += 1

        elif status == "RECOVERED":
            recovered_count += 1

    return {
        "active": active_count,
        "critical": critical_count,
        "high": high_count,
        "warning": warning_count,
        "recovered": recovered_count,
        "total": len(incidents),
    }


@app.get("/incidents/{incident_id}")
def get_incident(
    incident_id: str
):
    incident = load_incident(
        incident_id
    )

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Incident "
                f"{incident_id} "
                f"not found"
            ),
        )

    return incident


@app.get("/incidents/similar/{incident_id}")
def get_similar_incidents(
    incident_id: str
):
    incident = load_incident(
        incident_id
    )

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Incident "
                f"{incident_id} "
                f"not found"
            ),
        )

    target_severity = incident.get(
        "severity"
    )

    similar = []

    for item in list_incidents():

        if item.get(
            "incident_id"
        ) == incident_id:
            continue

        if item.get(
            "severity"
        ) == target_severity:
            similar.append(item)

    return {
        "incident_id": incident_id,
        "severity": target_severity,
        "count": len(similar),
        "similar_incidents": similar,
    }


# ============================================================
# PROMETHEUS METRICS
# ============================================================

@app.get("/metrics")
def metrics():

    update_metrics()

    return Response(
        generate_latest(),
        media_type=(
            "text/plain; "
            "version=0.0.4; "
            "charset=utf-8"
        ),
    )