from agent.investigator import get_current_health
from agent.llm import ask_llm
from agent.correlation import correlate_signals
from agent.history import find_similar_incidents

from rag.search import search_runbooks


def format_rag_results(results):
    if not results:
        return "No relevant runbook content was found."

    sections = []

    for index, result in enumerate(results, start=1):
        sections.append(
            f"""
Runbook Result {index}

Source:
{result.get("source")}

Chunk:
{result.get("chunk_index")}

Similarity Distance:
{result.get("distance")}

Content:
{result.get("document")}
"""
        )

    return "\n".join(sections)


def format_historical_results(results):
    if not results:
        return "No similar historical incidents were found."

    sections = []

    for index, incident in enumerate(results, start=1):
        sections.append(
            f"""
Historical Incident {index}

Incident ID:
{incident.get("incident_id")}

Status:
{incident.get("status")}

Severity:
{incident.get("severity")}

Detected At:
{incident.get("detected_at")}

Summary:
{incident.get("summary")}

Root Cause Status:
{incident.get("root_cause_status")}
"""
        )

    return "\n".join(sections)


def build_rag_query(health, correlation):
    signals = correlation.get("signals", [])

    signal_text = []

    for signal in signals:
        signal_text.append(
            f"{signal.get('type')} "
            f"{signal.get('message')}"
        )

    query = f"""
AI NOC incident investigation.

Severity:
{correlation.get("severity")}

Signals:
{" ".join(signal_text)}

CPU:
{health.get("cpu")}

Memory:
{health.get("memory")}

Incident Mode:
{health.get("incident_mode")}

Error Percentage:
{health.get("error_percentage")}

Recent Errors:
{health.get("recent_errors")}

Kubernetes Health:
{health.get("kubernetes")}
"""

    return query.strip()


def build_investigation_prompt(
    health,
    correlation,
    historical_results,
    runbook_results,
    incident_id=None,
    detected_at=None,
):
    kubernetes = health.get("kubernetes", {})

    historical_context = format_historical_results(
        historical_results
    )

    runbook_context = format_rag_results(
        runbook_results
    )

    prompt = f"""
You are investigating an infrastructure incident
for an AI-powered NOC system.

Use ONLY the evidence provided below.

Do not invent facts.

Clearly distinguish:

- Confirmed observations
- Correlated signals
- Historical incident patterns
- Runbook guidance
- Possible contributing factors
- Root cause status
- Recommended read-only diagnostic next steps

Do NOT claim a root cause unless the available
evidence clearly proves a causal relationship.

Historical incidents are references only.
They must not be treated as proof of the current
root cause.

Runbooks provide diagnostic guidance only.
They must not be treated as evidence that an
action has already been performed.

Do NOT recommend destructive or state-changing
actions such as:

- deleting pods
- restarting services
- scaling deployments
- changing configuration
- changing infrastructure

Any remediation must require human approval.

==================================================
INCIDENT INFORMATION
==================================================

Incident ID:
{incident_id}

Detected At:
{detected_at}

==================================================
CURRENT SYSTEM HEALTH
==================================================

CPU:
{health.get("cpu")}%

Memory:
{health.get("memory")}%

Incident Mode:
{health.get("incident_mode")}

Severity:
{health.get("severity")}

Total Requests:
{health.get("total_requests")}

Total Errors:
{health.get("total_errors")}

Recent Requests:
{health.get("recent_requests")}

Recent Errors:
{health.get("recent_errors")}

Error Percentage:
{health.get("error_percentage")}

P95 Latency:
{health.get("p95_latency")}

Recent Error Logs:

{health.get("recent_error_logs")}

==================================================
KUBERNETES HEALTH
==================================================

Kubernetes Status:
{kubernetes.get("status")}

Pods:
{kubernetes.get("pods")}

Deployments:
{kubernetes.get("deployments")}

Pod Restarts:
{kubernetes.get("restarts")}

Broken Pod:
{kubernetes.get("broken_pod")}

Broken Pod Description:
{kubernetes.get("broken_pod_description")}

Broken Pod Events:
{kubernetes.get("broken_pod_events")}

==================================================
ALERT CORRELATION
==================================================

Correlated:
{correlation.get("correlated")}

Signal Count:
{correlation.get("signal_count")}

Correlation Severity:
{correlation.get("severity")}

Correlation Summary:
{correlation.get("summary")}

Signals:

{correlation.get("signals")}

==================================================
HISTORICAL INCIDENT INTELLIGENCE
==================================================

{historical_context}

==================================================
RAG / RUNBOOK KNOWLEDGE
==================================================

{runbook_context}

==================================================
IMPORTANT INTERPRETATION RULES
==================================================

1. If noc-broken-pod is in ImagePullBackOff and
   Kubernetes events show ErrImagePull or
   "manifest not found", treat the image pull
   failure as a confirmed Kubernetes observation.

2. Do not automatically treat the Kubernetes
   ImagePullBackOff issue as the root cause of
   application HTTP 500 errors.

3. If application errors are simulated by the
   demo application, clearly identify them as
   simulated/test evidence.

4. High CPU or memory utilization is evidence of
   resource pressure, but do not automatically
   declare it the root cause.

5. A healthy pod must not be described as failed
   merely because another pod is broken.

6. Historical incidents are contextual evidence
   only and do not prove the current root cause.

7. Runbook content is diagnostic guidance and
   must not be represented as an action already
   executed.

8. Do not invent remediation, recovery actions,
   historical events, or causal relationships.

==================================================
REQUIRED INVESTIGATION FORMAT
==================================================

**Incident Summary:**

Briefly summarize the current incident.

**Confirmed Observations:**

List only facts directly supported by the
current evidence.

**Correlated Signals:**

Explain which signals were detected together
and grouped by the correlation engine.

**Historical Incident Patterns:**

Summarize relevant historical incidents,
if available.

Clearly state that historical incidents do
not prove the current root cause.

**Runbook Guidance:**

Summarize the most relevant diagnostic
guidance retrieved from the runbook knowledge
base.

**Possible Contributing Factors:**

List possible factors and clearly mark them
as possible rather than confirmed causes.

**Root Cause Status:**

State either:

- Confirmed
- Not Confirmed

Explain the evidence supporting that status.

**Recommended Read-Only Diagnostic Next Steps:**

Provide safe diagnostic checks only.

**Risk / Safety Note:**

State that remediation requires human approval.
"""

    return prompt


def investigate_incident(
    return_analysis=False,
    incident_id=None,
    detected_at=None,
):
    print("\nCollecting system health...")

    health = get_current_health()

    print("\nRunning alert correlation...")

    correlation = correlate_signals(
        health
    )

    print(
        f"Correlation signals detected: "
        f"{correlation.get('signal_count')}"
    )

    print("\nSearching historical incidents...")

    try:
        historical_results = find_similar_incidents(
            health
        )
    except Exception as exc:
        print(
            "Historical intelligence unavailable:"
        )
        print(exc)
        historical_results = []

    print("\nSearching runbooks...")

    rag_query = build_rag_query(
        health,
        correlation
    )

    try:
        runbook_results = search_runbooks(
            query=rag_query,
            n_results=3,
        )
    except Exception as exc:
        print(
            "RAG search unavailable:"
        )
        print(exc)
        runbook_results = []

    print(
        f"Runbooks retrieved: "
        f"{len(runbook_results)}"
    )

    prompt = build_investigation_prompt(
        health=health,
        correlation=correlation,
        historical_results=historical_results,
        runbook_results=runbook_results,
        incident_id=incident_id,
        detected_at=detected_at,
    )

    print(
        "\nSending evidence + correlation + "
        "historical + runbook context to local AI..."
    )

    analysis = ask_llm(prompt)

    if return_analysis:
        return analysis

    print("\n")
    print("=" * 60)
    print("🤖 AI NOC INVESTIGATION")
    print("=" * 60)

    if incident_id:
        print(
            f"Incident ID: {incident_id}"
        )

    if detected_at:
        print(
            f"Detected At: {detected_at}"
        )

    print("\n" + analysis)

    print("=" * 60)

    return analysis


if __name__ == "__main__":
    investigate_incident()
