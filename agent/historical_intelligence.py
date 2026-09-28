from agent.incident_store import list_incidents


# ============================================================
# CONFIGURATION
# ============================================================

MAX_HISTORICAL_RESULTS = 5


# ============================================================
# SIGNAL EXTRACTION
# ============================================================

def extract_signal_types(correlation):
    """
    Extract signal type names from correlation data.
    """

    if not isinstance(correlation, dict):
        return set()

    signals = correlation.get(
        "signals",
        []
    )

    signal_types = set()

    if not isinstance(signals, list):
        return signal_types

    for signal in signals:

        if not isinstance(signal, dict):
            continue

        signal_type = signal.get(
            "type"
        )

        if signal_type:
            signal_types.add(
                str(signal_type)
            )

    return signal_types


# ============================================================
# CURRENT INCIDENT SIGNATURE
# ============================================================

def build_current_signature(
    health,
    correlation=None
):
    """
    Build a normalized signature for
    the current incident.
    """

    if correlation is None:
        correlation = {}

    cpu = health.get(
        "cpu"
    )

    memory = health.get(
        "memory"
    )

    incident_mode = health.get(
        "incident_mode"
    )

    severity = health.get(
        "severity"
    )

    return {
        "severity": severity,
        "incident_mode": incident_mode,
        "cpu_high": (
            cpu is not None
            and cpu >= 90
        ),
        "memory_high": (
            memory is not None
            and memory >= 85
        ),
        "signal_types": extract_signal_types(
            correlation
        ),
    }


# ============================================================
# HISTORICAL INCIDENT SIGNATURE
# ============================================================

def build_historical_signature(
    incident
):
    """
    Build a normalized signature from
    a stored historical incident.
    """

    if not isinstance(incident, dict):
        return {
            "severity": None,
            "incident_mode": None,
            "cpu_high": False,
            "memory_high": False,
            "signal_types": set(),
        }

    cpu = incident.get(
        "cpu"
    )

    memory = incident.get(
        "memory"
    )

    correlation = incident.get(
        "correlation",
        {}
    )

    return {
        "severity": incident.get(
            "severity"
        ),
        "incident_mode": incident.get(
            "incident_mode"
        ),
        "cpu_high": (
            cpu is not None
            and cpu >= 90
        ),
        "memory_high": (
            memory is not None
            and memory >= 85
        ),
        "signal_types": extract_signal_types(
            correlation
        ),
    }


# ============================================================
# SIMILARITY CALCULATION
# ============================================================

def calculate_similarity(
    current_signature,
    historical_signature
):
    """
    Calculate a simple explainable similarity
    score between 0 and 100.

    This is deterministic and does not use AI.
    """

    score = 0
    reasons = []

    # --------------------------------------------------------
    # Severity
    # --------------------------------------------------------

    if (
        current_signature.get("severity")
        and
        current_signature.get("severity")
        ==
        historical_signature.get("severity")
    ):
        score += 20

        reasons.append(
            "Same severity"
        )

    # --------------------------------------------------------
    # Incident mode
    # --------------------------------------------------------

    if (
        current_signature.get(
            "incident_mode"
        )
        is not None
        and
        current_signature.get(
            "incident_mode"
        )
        ==
        historical_signature.get(
            "incident_mode"
        )
    ):
        score += 15

        reasons.append(
            "Same incident mode"
        )

    # --------------------------------------------------------
    # CPU
    # --------------------------------------------------------

    if (
        current_signature.get(
            "cpu_high"
        )
        ==
        historical_signature.get(
            "cpu_high"
        )
    ):
        score += 15

        if current_signature.get(
            "cpu_high"
        ):
            reasons.append(
                "Both incidents had high CPU"
            )
        else:
            reasons.append(
                "Both incidents had no high CPU"
            )

    # --------------------------------------------------------
    # Memory
    # --------------------------------------------------------

    if (
        current_signature.get(
            "memory_high"
        )
        ==
        historical_signature.get(
            "memory_high"
        )
    ):
        score += 15

        if current_signature.get(
            "memory_high"
        ):
            reasons.append(
                "Both incidents had high memory"
            )
        else:
            reasons.append(
                "Both incidents had no high memory"
            )

    # --------------------------------------------------------
    # Correlation signals
    # --------------------------------------------------------

    current_signals = current_signature.get(
        "signal_types",
        set()
    )

    historical_signals = historical_signature.get(
        "signal_types",
        set()
    )

    if current_signals and historical_signals:

        shared_signals = (
            current_signals
            &
            historical_signals
        )

        if shared_signals:

            signal_score = min(
                35,
                len(shared_signals) * 15
            )

            score += signal_score

            reasons.append(
                "Shared signals: "
                + ", ".join(
                    sorted(shared_signals)
                )
            )

    # --------------------------------------------------------
    # Normalize
    # --------------------------------------------------------

    score = min(
        score,
        100
    )

    return {
        "score": score,
        "reasons": reasons,
    }


# ============================================================
# FIND SIMILAR HISTORICAL INCIDENTS
# ============================================================

def find_similar_incidents(
    health,
    correlation=None,
    max_results=MAX_HISTORICAL_RESULTS
):
    """
    Search the incident store and return
    the most similar historical incidents.
    """

    current_signature = build_current_signature(
        health=health,
        correlation=correlation
    )

    historical_incidents = list_incidents()

    matches = []

    for incident in historical_incidents:

        if not isinstance(
            incident,
            dict
        ):
            continue

        historical_signature = (
            build_historical_signature(
                incident
            )
        )

        similarity = calculate_similarity(
            current_signature,
            historical_signature
        )

        matches.append(
            {
                "incident": incident,
                "similarity": similarity,
            }
        )

    # --------------------------------------------------------
    # Sort highest similarity first
    # --------------------------------------------------------

    matches.sort(
        key=lambda item: item[
            "similarity"
        ]["score"],
        reverse=True
    )

    return matches[
        :max_results
    ]


# ============================================================
# BUILD AI HISTORICAL CONTEXT
# ============================================================

def build_historical_context(
    health,
    correlation=None,
    max_results=MAX_HISTORICAL_RESULTS
):
    """
    Convert historical matches into a concise
    context block suitable for the AI investigator.
    """

    matches = find_similar_incidents(
        health=health,
        correlation=correlation,
        max_results=max_results
    )

    if not matches:

        return (
            "No historical incidents were found."
        )

    lines = []

    lines.append(
        "Historical Incident Intelligence"
    )

    lines.append(
        "--------------------------------"
    )

    for index, match in enumerate(
        matches,
        start=1
    ):

        incident = match.get(
            "incident",
            {}
        )

        similarity = match.get(
            "similarity",
            {}
        )

        incident_id = incident.get(
            "incident_id",
            "Unknown"
        )

        status = incident.get(
            "status",
            "Unknown"
        )

        severity = incident.get(
            "severity",
            "Unknown"
        )

        score = similarity.get(
            "score",
            0
        )

        reasons = similarity.get(
            "reasons",
            []
        )

        lines.append(
            f"\n{index}. {incident_id}"
        )

        lines.append(
            f"Status: {status}"
        )

        lines.append(
            f"Severity: {severity}"
        )

        lines.append(
            f"Similarity: {score}%"
        )

        if reasons:

            lines.append(
                "Similarity Reasons: "
                + "; ".join(
                    reasons
                )
            )

        analysis = incident.get(
            "investigation"
        )

        if analysis:

            lines.append(
                "Historical Investigation:"
            )

            lines.append(
                str(analysis)
            )

    return "\n".join(
        lines
    )


# ============================================================
# DISPLAY RESULTS
# ============================================================

def print_historical_results(
    matches
):
    print("\n")
    print("=" * 60)
    print(
        "       HISTORICAL INCIDENT INTELLIGENCE"
    )
    print("=" * 60)

    if not matches:

        print(
            "\nNo historical incidents found."
        )

        print("=" * 60)

        return

    for index, match in enumerate(
        matches,
        start=1
    ):

        incident = match.get(
            "incident",
            {}
        )

        similarity = match.get(
            "similarity",
            {}
        )

        print(
            f"\n{index}. "
            f"Incident ID: "
            f"{incident.get('incident_id')}"
        )

        print(
            f"   Status: "
            f"{incident.get('status')}"
        )

        print(
            f"   Severity: "
            f"{incident.get('severity')}"
        )

        print(
            f"   Similarity: "
            f"{similarity.get('score')}%"
        )

        reasons = similarity.get(
            "reasons",
            []
        )

        if reasons:

            print(
                "   Reasons:"
            )

            for reason in reasons:

                print(
                    f"   - {reason}"
                )

    print("\n" + "=" * 60)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n")
    print("=" * 60)
    print(
        "   HISTORICAL INTELLIGENCE ENGINE TEST"
    )
    print("=" * 60)

    # --------------------------------------------------------
    # Simulated current incident signature
    # --------------------------------------------------------

    test_health = {
        "cpu": 95.0,
        "memory": 92.0,
        "incident_mode": 1,
        "severity": "CRITICAL",
    }

    test_correlation = {
        "correlated": True,
        "signal_count": 4,
        "severity": "CRITICAL",
        "signals": [
            {
                "type": "CPU_HIGH",
                "severity": "CRITICAL",
                "value": 95.0,
                "message": (
                    "CPU usage is 95%"
                ),
            },
            {
                "type": "MEMORY_HIGH",
                "severity": "HIGH",
                "value": 92.0,
                "message": (
                    "Memory usage is 92%"
                ),
            },
            {
                "type": "INCIDENT_MODE",
                "severity": "CRITICAL",
                "value": 1,
                "message": (
                    "Incident simulation mode enabled"
                ),
            },
            {
                "type": "KUBERNETES_IMAGE_PULL_FAILURE",
                "severity": "HIGH",
                "value": "noc-broken-pod",
                "message": (
                    "Kubernetes ImagePullBackOff"
                ),
            },
        ],
    }

    matches = find_similar_incidents(
        health=test_health,
        correlation=test_correlation
    )

    print_historical_results(
        matches
    )

    print("\n")
    print(
        "Generating AI historical context..."
    )

    context = build_historical_context(
        health=test_health,
        correlation=test_correlation
    )

    print("\n" + context)

    print("\n")
    print("=" * 60)
    print(
        "HISTORICAL INTELLIGENCE TEST COMPLETED"
    )
    print("=" * 60)
