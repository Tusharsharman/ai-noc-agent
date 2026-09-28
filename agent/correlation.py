from datetime import datetime, timezone


# ---------------------------------------------------------
# Correlation configuration
# ---------------------------------------------------------

CORRELATION_WINDOW_SECONDS = 300


# ---------------------------------------------------------
# Signal definitions
# ---------------------------------------------------------

def build_signals(health: dict):
    """
    Convert current system health into normalized
    incident signals.

    This function does not create incidents.
    It only identifies individual signals.
    """

    signals = []

    cpu = health.get("cpu")
    memory = health.get("memory")
    incident_mode = health.get("incident_mode")

    error_percentage = health.get(
        "error_percentage"
    )

    recent_errors = health.get(
        "recent_errors"
    )

    kubernetes = health.get(
        "kubernetes",
        {}
    )

    # -----------------------------------------------------
    # CPU signal
    # -----------------------------------------------------

    if cpu is not None and cpu >= 90:
        signals.append({
            "type": "CPU_HIGH",
            "severity": "CRITICAL",
            "value": cpu,
            "message": (
                f"CPU usage is {cpu}%"
            )
        })

    elif cpu is not None and cpu >= 75:
        signals.append({
            "type": "CPU_HIGH",
            "severity": "HIGH",
            "value": cpu,
            "message": (
                f"CPU usage is {cpu}%"
            )
        })

    # -----------------------------------------------------
    # Memory signal
    # -----------------------------------------------------

    if memory is not None and memory >= 95:
        signals.append({
            "type": "MEMORY_HIGH",
            "severity": "CRITICAL",
            "value": memory,
            "message": (
                f"Memory usage is {memory}%"
            )
        })

    elif memory is not None and memory >= 85:
        signals.append({
            "type": "MEMORY_HIGH",
            "severity": "HIGH",
            "value": memory,
            "message": (
                f"Memory usage is {memory}%"
            )
        })

    # -----------------------------------------------------
    # Application error signal
    # -----------------------------------------------------

    if (
        error_percentage is not None
        and error_percentage >= 5
    ):
        signals.append({
            "type": "APPLICATION_ERRORS",
            "severity": "HIGH",
            "value": error_percentage,
            "message": (
                f"Application error rate is "
                f"{error_percentage:.2f}%"
            )
        })

    elif (
        recent_errors is not None
        and recent_errors > 0
    ):
        signals.append({
            "type": "APPLICATION_ERRORS",
            "severity": "WARNING",
            "value": recent_errors,
            "message": (
                f"{recent_errors} recent "
                "application errors detected"
            )
        })

    # -----------------------------------------------------
    # Incident simulation signal
    # -----------------------------------------------------

    if incident_mode == 1:
        signals.append({
            "type": "INCIDENT_MODE",
            "severity": "CRITICAL",
            "value": 1,
            "message": (
                "Application incident simulation "
                "mode is enabled"
            )
        })

    # -----------------------------------------------------
    # Kubernetes signals
    # -----------------------------------------------------

    if kubernetes.get("status") == "available":

        broken_pod = kubernetes.get(
            "broken_pod"
        )

        broken_description = kubernetes.get(
            "broken_pod_description",
            ""
        )

        broken_events = kubernetes.get(
            "broken_pod_events",
            ""
        )

        if (
            "ImagePullBackOff"
            in broken_description
            or
            "ImagePullBackOff"
            in broken_events
        ):
            signals.append({
                "type": "KUBERNETES_IMAGE_PULL_FAILURE",
                "severity": "HIGH",
                "value": broken_pod,
                "message": (
                    f"Kubernetes pod "
                    f"{broken_pod} is experiencing "
                    "ImagePullBackOff"
                )
            })

        if (
            "ErrImagePull"
            in broken_description
            or
            "ErrImagePull"
            in broken_events
        ):
            signals.append({
                "type": "KUBERNETES_IMAGE_PULL_ERROR",
                "severity": "HIGH",
                "value": broken_pod,
                "message": (
                    f"Kubernetes reported "
                    f"ErrImagePull for pod "
                    f"{broken_pod}"
                )
            })

    return signals


# ---------------------------------------------------------
# Severity calculation
# ---------------------------------------------------------

def calculate_correlated_severity(
    signals: list
):
    """
    Calculate the highest severity represented
    by the correlated signals.
    """

    if not signals:
        return "NORMAL"

    severity_priority = {
        "NORMAL": 0,
        "WARNING": 1,
        "HIGH": 2,
        "CRITICAL": 3,
    }

    highest = max(
        signals,
        key=lambda signal: severity_priority.get(
            signal.get("severity"),
            0
        )
    )

    return highest.get(
        "severity",
        "NORMAL"
    )


# ---------------------------------------------------------
# Correlation logic
# ---------------------------------------------------------

def correlate_signals(
    health: dict,
    timestamp=None
):
    """
    Correlate all signals observed during the
    current health evaluation.

    The current implementation groups signals from
    the same health snapshot into a single
    correlated event.
    """

    if timestamp is None:
        timestamp = datetime.now(
            timezone.utc
        ).isoformat()

    signals = build_signals(
        health
    )

    severity = calculate_correlated_severity(
        signals
    )

    correlated = {
        "correlated": len(signals) > 1,
        "signal_count": len(signals),
        "severity": severity,
        "timestamp": timestamp,
        "signals": signals,
    }

    if len(signals) > 1:
        correlated["summary"] = (
            f"{len(signals)} signals detected "
            "during the same health evaluation "
            "and grouped into one correlated event."
        )

    elif len(signals) == 1:
        correlated["summary"] = (
            "One signal detected. "
            "No multi-signal correlation required."
        )

    else:
        correlated["summary"] = (
            "No active incident signals detected."
        )

    return correlated


# ---------------------------------------------------------
# Human-readable output
# ---------------------------------------------------------

def print_correlation_result(
    result: dict
):
    print("\n")
    print("=" * 60)
    print("        AI NOC ALERT CORRELATION")
    print("=" * 60)

    print(
        f"Correlated: "
        f"{result['correlated']}"
    )

    print(
        f"Signal Count: "
        f"{result['signal_count']}"
    )

    print(
        f"Severity: "
        f"{result['severity']}"
    )

    print(
        f"Timestamp: "
        f"{result['timestamp']}"
    )

    print(
        f"\nSummary:\n"
        f"{result['summary']}"
    )

    print("\nSignals:")

    if not result["signals"]:
        print("No active signals.")

    for index, signal in enumerate(
        result["signals"],
        start=1
    ):
        print(
            f"\n{index}. "
            f"{signal['type']}"
        )

        print(
            f"   Severity: "
            f"{signal['severity']}"
        )

        print(
            f"   Value: "
            f"{signal['value']}"
        )

        print(
            f"   Message: "
            f"{signal['message']}"
        )

    print("=" * 60)


# ---------------------------------------------------------
# Standalone test
# ---------------------------------------------------------

if __name__ == "__main__":

    print("\n")
    print("=" * 60)
    print("      ALERT CORRELATION ENGINE TEST")
    print("=" * 60)

    # -----------------------------------------------------
    # Test 1: Healthy system
    # -----------------------------------------------------

    healthy_health = {
        "cpu": 25.0,
        "memory": 70.0,
        "incident_mode": 0,
        "error_percentage": 0.0,
        "recent_errors": 0,
        "kubernetes": {
            "status": "available",
            "broken_pod": "noc-broken-pod",
            "broken_pod_description": "",
            "broken_pod_events": "",
        },
    }

    print("\nTEST 1: HEALTHY SYSTEM")

    result = correlate_signals(
        healthy_health
    )

    print_correlation_result(
        result
    )

    # -----------------------------------------------------
    # Test 2: Multiple application signals
    # -----------------------------------------------------

    application_incident = {
        "cpu": 95.0,
        "memory": 96.0,
        "incident_mode": 1,
        "error_percentage": 12.5,
        "recent_errors": 10,
        "kubernetes": {
            "status": "available",
            "broken_pod": "noc-broken-pod",
            "broken_pod_description": (
                "Status: ImagePullBackOff"
            ),
            "broken_pod_events": (
                "Failed to pull image\n"
                "ErrImagePull\n"
                "manifest not found"
            ),
        },
    }

    print(
        "\nTEST 2: MULTIPLE CORRELATED SIGNALS"
    )

    result = correlate_signals(
        application_incident
    )

    print_correlation_result(
        result
    )

    # -----------------------------------------------------
    # Test 3: Kubernetes-only signal
    # -----------------------------------------------------

    kubernetes_incident = {
        "cpu": 30.0,
        "memory": 70.0,
        "incident_mode": 0,
        "error_percentage": 0.0,
        "recent_errors": 0,
        "kubernetes": {
            "status": "available",
            "broken_pod": "noc-broken-pod",
            "broken_pod_description": (
                "Status: ImagePullBackOff"
            ),
            "broken_pod_events": (
                "ErrImagePull"
            ),
        },
    }

    print(
        "\nTEST 3: KUBERNETES SIGNAL"
    )

    result = correlate_signals(
        kubernetes_incident
    )

    print_correlation_result(
        result
    )

    print("\n")
    print("=" * 60)
    print("CORRELATION ENGINE TEST COMPLETED")
    print("=" * 60)
