from agent.investigator import get_current_health
from agent.correlation import (
    correlate_signals,
    print_correlation_result,
)


def test_real_environment_correlation():
    print("\n")
    print("=" * 60)
    print("   REAL ENVIRONMENT CORRELATION TEST")
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
        f"Error Percentage: "
        f"{health.get('error_percentage')}"
    )
    print(
        f"Recent Errors: "
        f"{health.get('recent_errors')}"
    )

    kubernetes = health.get(
        "kubernetes",
        {}
    )

    print(
        f"Kubernetes Status: "
        f"{kubernetes.get('status')}"
    )

    print("\nRunning correlation engine...")

    result = correlate_signals(
        health
    )

    print_correlation_result(
        result
    )

    print("\n")
    print("=" * 60)
    print("REAL ENVIRONMENT TEST COMPLETED")
    print("=" * 60)

    assert result is not None


if __name__ == "__main__":
    test_real_environment_correlation()
