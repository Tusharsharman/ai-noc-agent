from tools import prometheus


def test_query_prometheus(monkeypatch):

    class MockResponse:

        def raise_for_status(self):
            pass

        def json(self):
            return {
                "status": "success",
                "data": {
                    "result": [
                        {
                            "metric": {
                                "__name__": "app_cpu_usage_percent"
                            },
                            "value": [
                                1234567890,
                                "95"
                            ]
                        }
                    ]
                }
            }

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(
        prometheus.requests,
        "get",
        mock_get
    )

    result = prometheus.query_prometheus(
        "app_cpu_usage_percent"
    )

    assert len(result) == 1
    assert result[0]["value"][1] == "95"
