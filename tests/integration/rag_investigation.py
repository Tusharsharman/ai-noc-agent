from agent.investigator import get_current_health
from agent.correlation import correlate_signals
from agent.llm import ask_llm
from rag.search import search_runbooks


def build_rag_investigation_prompt(
    health: dict,
    correlation: dict,
    runbook_results: list,
):
    runbook_context = ""

    for index, result in enumerate(
        runbook_results,
        start=1
    ):
        runbook_context += (
            f"\n--- Runbook Result {index} ---\n"
            f"Source: {result.get('source')}\n"
            f"Content:\n{result.get('document')}\n"
        )

    kubernetes = health.get(
        "kubernetes",
        {}
    )

    prompt = f"""
You are an AI NOC investigation assistant.

Use ONLY the evidence and runbook information
provided below.

Do not invent facts.

Clearly distinguish:
- Confirmed observations
- Possible contributing factors
- Root cause status
- Recommended read-only diagnostic next steps

The runbook is diagnostic guidance.
It is NOT proof of root cause.

Do not recommend destructive or state-changing
actions such as:
- deleting pods
- restarting services
- changing configuration
- scaling infrastructure
- changing deployments

Any remediation requires human approval.

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

Recent Errors:
{health.get("recent_errors")}

Error Percentage:
{health.get("error_percentage")}

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
CORRELATED SIGNALS
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
RELEVANT RUNBOOK KNOWLEDGE
==================================================

{runbook_context}

==================================================
INVESTIGATION RULES
==================================================

1. Treat Kubernetes ImagePullBackOff and
   ErrImagePull as confirmed observations only
   when supported by the Kubernetes evidence.

2. Treat HTTP 500 errors as confirmed application
   observations when supported by the evidence.

3. Do not automatically connect a Kubernetes
   ImagePullBackOff issue to application HTTP 500
   errors without evidence establishing causality.

4. High CPU or memory usage indicates resource
   pressure but does not automatically prove root
   cause.

5. Use the retrieved runbook as diagnostic guidance,
   not as evidence that a specific cause occurred.

6. Do not invent historical incidents or remediation.

==================================================
REQUIRED OUTPUT
==================================================

**Incident Summary:**

Summarize the current situation.

**Confirmed Observations:**

List only facts supported by the current evidence.

**Correlated Signals:**

Explain which signals were grouped together.

**Runbook Guidance:**

Summarize the relevant diagnostic guidance retrieved
from the runbook.

**Possible Contributing Factors:**

List possible factors and clearly mark them as
possible.

**Root Cause Status:**

State either:
- Confirmed
- Not Confirmed

Explain why.

**Recommended Read-Only Diagnostic Next Steps:**

Provide safe diagnostic checks based on the evidence
and retrieved runbook.

**Risk / Safety Note:**

State that remediation requires human approval.
"""

    return prompt


def main():
    print("\n")
    print("=" * 60)
    print("       RAG + OLLAMA INVESTIGATION TEST")
    print("=" * 60)

    print("\nCollecting current system health...")

    health = get_current_health()

    print("\nCurrent Health:")
    print(f"CPU: {health.get('cpu')}%")
    print(f"Memory: {health.get('memory')}%")
    print(
        f"Incident Mode: "
        f"{health.get('incident_mode')}"
    )
    print(
        f"Severity: "
        f"{health.get('severity')}"
    )
    print(
        f"Error Percentage: "
        f"{health.get('error_percentage')}"
    )

    print("\nRunning alert correlation...")

    correlation = correlate_signals(
        health
    )

    print(
        f"Correlated: "
        f"{correlation.get('correlated')}"
    )

    print(
        f"Signal Count: "
        f"{correlation.get('signal_count')}"
    )

    print(
        f"Correlation Severity: "
        f"{correlation.get('severity')}"
    )

    query_parts = []

    if (
        health.get("error_percentage") is not None
        and health.get("error_percentage") > 0
    ):
        query_parts.append(
            "application HTTP 500 errors"
        )

    kubernetes = health.get(
        "kubernetes",
        {}
    )

    kubernetes_text = (
        str(
            kubernetes.get(
                "broken_pod_description",
                ""
            )
        )
        + " "
        + str(
            kubernetes.get(
                "broken_pod_events",
                ""
            )
        )
    )

    if (
        "ImagePullBackOff"
        in kubernetes_text
        or
        "ErrImagePull"
        in kubernetes_text
    ):
        query_parts.append(
            "Kubernetes ImagePullBackOff "
            "and ErrImagePull"
        )

    if not query_parts:
        query_parts.append(
            "Kubernetes application "
            "incident diagnostic guidance"
        )

    rag_query = " ".join(
        query_parts
    )

    print(
        f"\nRAG Query:\n{rag_query}"
    )

    print(
        "\nSearching runbooks..."
    )

    runbook_results = search_runbooks(
        query=rag_query,
        n_results=3,
    )

    print(
        f"Runbook results: "
        f"{len(runbook_results)}"
    )

    for index, result in enumerate(
        runbook_results,
        start=1
    ):
        print(
            f"{index}. "
            f"{result.get('source')}"
        )

    print(
        "\nBuilding AI investigation prompt..."
    )

    prompt = build_rag_investigation_prompt(
        health=health,
        correlation=correlation,
        runbook_results=runbook_results,
    )

    print(
        "\nSending evidence + runbook "
        "knowledge to local Ollama..."
    )

    analysis = ask_llm(
        prompt
    )

    print("\n")
    print("=" * 60)
    print("       RAG AI INVESTIGATION")
    print("=" * 60)

    print("\n" + analysis)

    print("\n")
    print("=" * 60)
    print("RAG + OLLAMA TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
