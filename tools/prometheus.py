import requests


PROMETHEUS_URL = "http://localhost:9090"


def query_prometheus(query: str):
    """
    Execute a PromQL query against Prometheus.
    """

    response = requests.get(
        f"{PROMETHEUS_URL}/api/v1/query",
        params={"query": query},
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    if data["status"] != "success":
        raise Exception(f"Prometheus query failed: {data}")

    return data["data"]["result"]


def get_metric_value(query: str):
    """
    Return the first Prometheus metric value as float.
    Return None if the metric is not available.
    """

    result = query_prometheus(query)

    if not result:
        return None

    return float(result[0]["value"][1])