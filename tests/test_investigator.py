from agent import investigator


def test_get_current_health(monkeypatch):

    values = {
        "app_cpu_usage_percent": 95.0,
        "app_memory_usage_percent": 92.0,
        "app_incident_mode": 1.0,
        "sum(app_errors_total)": 10.0,
        "sum(app_requests_total)": 20.0,
        "sum(increase(app_requests_total[5m]))": 20.0,
        "sum(increase(app_errors_total[5m]))": 5.0,
        """
        histogram_quantile(
            0.95,
            sum(
                rate(app_request_latency_seconds_bucket[5m])
            ) by (le)
        )
        """: 0.25,
    }

    def mock_get_metric_value(query):
        return values.get(query)

    def mock_get_error_logs(limit):
        return [
            "ERROR test error"
        ]

    def mock_get_kubernetes_health(namespace="noc-demo"):
        return {
            "status": "available",
            "pods": [],
            "deployments": [],
            "restarts": {},
            "broken_pod": "noc-broken-pod",
            "broken_pod_description": "",
            "broken_pod_events": "",
        }

    monkeypatch.setattr(
        investigator,
        "get_metric_value",
        mock_get_metric_value
    )

    monkeypatch.setattr(
        investigator,
        "get_error_logs",
        mock_get_error_logs
    )

    monkeypatch.setattr(
        investigator,
        "get_kubernetes_health",
        mock_get_kubernetes_health
    )

    health = investigator.get_current_health()

    assert health["cpu"] == 95.0
    assert health["memory"] == 92.0
    assert health["incident_mode"] == 1
    assert health["total_errors"] == 10.0
    assert health["total_requests"] == 20.0
    assert health["recent_requests"] == 20.0
    assert health["recent_errors"] == 5.0
    assert health["error_percentage"] == 25.0
    assert health["p95_latency"] == 0.25
    assert health["severity"] == "CRITICAL"
    assert health["recent_error_logs"] == [
        "ERROR test error"
    ]
    assert health["kubernetes"]["status"] == "available"
