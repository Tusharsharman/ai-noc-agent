from agent import llm


def test_ask_llm(monkeypatch):

    class MockResponse:

        def raise_for_status(self):
            pass

        def json(self):
            return {
                "message": {
                    "content": "Test NOC analysis response"
                }
            }

    def mock_post(*args, **kwargs):
        assert kwargs["json"]["model"] == "llama3.2:3b"
        assert kwargs["json"]["stream"] is False

        return MockResponse()

    monkeypatch.setattr(
        llm.requests,
        "post",
        mock_post
    )

    result = llm.ask_llm(
        "Test incident"
    )

    assert result == "Test NOC analysis response"
