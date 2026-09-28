from math import isnan

from tools.prometheus import get_metric_value
from tools.logs import get_error_logs
from tools.kubernetes import (
    get_pods,
    get_deployments,
    get_pod_restarts,
    get_pod_description,
    get_pod_events,
)


def safe_metric_value(query: str):
    value = get_metric_value(query)

    if value is None:
        return None

    if isinstance(value, float) and isnan(value):
        return None

    return value


def get_kubernetes_health(namespace="noc-demo"):
    """
    Collect read-only Kubernetes health information.
    """

    try:
        pods = get_pods(namespace)
        deployments = get_deployments(namespace)
        restarts = get_pod_restarts(namespace)

        broken_pod = "noc-broken-pod"

        try:
            broken_pod_description = get_pod_description(
                broken_pod,
                namespace
            )
        except Exception as exc:
            broken_pod_description = (
                f"Unable to get pod description: {exc}"
            )

        try:
            broken_pod_events = get_pod_events(
                broken_pod,
                namespace
            )
        except Exception as exc:
            broken_pod_events = (
                f"Unable to get pod events: {exc}"
            )

        return {
            "status": "available",
            "pods": pods,
            "deployments": deployments,
            "restarts": restarts,
            "broken_pod": broken_pod,
            "broken_pod_description": broken_pod_description,
            "broken_pod_events": broken_pod_events,
        }

    except Exception as exc:

        return {
            "status": "unavailable",
            "error": str(exc),
        }


def get_current_health():

    cpu = safe_metric_value(
        "app_cpu_usage_percent"
    )

    memory = safe_metric_value(
        "app_memory_usage_percent"
    )

    incident = safe_metric_value(
        "app_incident_mode"
    )

    total_errors = safe_metric_value(
        "sum(app_errors_total)"
    )

    total_requests = safe_metric_value(
        "sum(app_requests_total)"
    )

    recent_requests = safe_metric_value(
        "sum(increase(app_requests_total[5m]))"
    )

    recent_errors = safe_metric_value(
        "sum(increase(app_errors_total[5m]))"
    )

    error_percentage = None

    if (
        recent_requests is not None
        and recent_requests > 0
        and recent_errors is not None
    ):
        error_percentage = (
            recent_errors / recent_requests
        ) * 100

    p95_latency = safe_metric_value(
        """
        histogram_quantile(
            0.95,
            sum(
                rate(app_request_latency_seconds_bucket[5m])
            ) by (le)
        )
        """
    )

    recent_error_logs = get_error_logs(50)

    if (
        (cpu is not None and cpu >= 90)
        or
        (memory is not None and memory >= 90)
    ):
        severity = "CRITICAL"

    elif (
        (cpu is not None and cpu >= 75)
        or
        (memory is not None and memory >= 75)
    ):
        severity = "HIGH"

    else:
        severity = "NORMAL"

    kubernetes = get_kubernetes_health(
        namespace="noc-demo"
    )

    return {
        "cpu": cpu,
        "memory": memory,
        "incident_mode": (
            int(incident)
            if incident is not None
            else None
        ),
        "total_errors": total_errors,
        "total_requests": total_requests,
        "recent_requests": recent_requests,
        "recent_errors": recent_errors,
        "error_percentage": error_percentage,
        "p95_latency": p95_latency,
        "recent_error_logs": recent_error_logs,
        "severity": severity,
        "kubernetes": kubernetes,
    }


if __name__ == "__main__":

    health = get_current_health()

    print("\n========================================")
    print("        CURRENT SYSTEM HEALTH")
    print("========================================")

    print("\nCPU:", health["cpu"])
    print("Memory:", health["memory"])
    print("Severity:", health["severity"])

    print("\n========================================")
    print("        KUBERNETES HEALTH")
    print("========================================")

    kubernetes = health["kubernetes"]

    print("Status:", kubernetes["status"])

    if kubernetes["status"] == "available":

        print("\n--- PODS ---")
        print(kubernetes["pods"])

        print("\n--- DEPLOYMENTS ---")
        print(kubernetes["deployments"])

        print("\n--- RESTARTS ---")
        print(kubernetes["restarts"])

        print("\n--- BROKEN POD DESCRIPTION ---")
        print(kubernetes["broken_pod_description"])

        print("\n--- BROKEN POD EVENTS ---")
        print(kubernetes["broken_pod_events"])

    else:

        print("\nKubernetes error:")
        print(kubernetes["error"])
