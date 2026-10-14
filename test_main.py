
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def mock_openai_response(category: str, response: str):
    mock_result = Mock()
    mock_result.category = category
    mock_result.response = response

    mock_response = Mock()
    mock_response.output_parsed = mock_result

    return mock_response


def test_home_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "AI Support Agent is running"


@patch("main.client.responses.parse")
def test_email_request(mock_parse):
    mock_parse.return_value = mock_openai_response(
        "email", "Check your outgoing mail settings."
    )
    response = client.post(
        "/support",
        json={"message": "I can receive messages, but cannot send them."},
    )
    assert response.status_code == 200
    assert response.json()["category"] == "email"
    assert "outgoing mail settings" in response.json()["response"]


@patch("main.client.responses.parse")
def test_network_request(mock_parse):
    mock_parse.return_value = mock_openai_response(
        "network", "Check your network connection."
    )
    response = client.post(
        "/support",
        json={"message": "I cannot connect to Wi-Fi"},
    )
    assert response.status_code == 200
    assert response.json()["category"] == "network"


@patch("main.client.responses.parse")
def test_performance_request(mock_parse):
    mock_parse.return_value = mock_openai_response(
        "performance", "Check resource usage."
    )
    response = client.post(
        "/support",
        json={"message": "My laptop is running slowly"},
    )
    assert response.status_code == 200
    assert response.json()["category"] == "performance"


@patch("main.client.responses.parse")
def test_general_request(mock_parse):
    mock_parse.return_value = mock_openai_response(
        "general", "Please describe the issue in more detail."
    )
    response = client.post(
        "/support",
        json={"message": "I need help with something"},
    )
    assert response.status_code == 200
    assert response.json()["category"] == "general"


def test_missing_message():
    response = client.post("/support", json={})
    assert response.status_code == 422


@patch("main.client.responses.parse")
def test_openai_failure(mock_parse):
    mock_parse.side_effect = Exception("Simulated API failure")
    response = client.post(
        "/support",
        json={"message": "My computer is not working"},
    )
    assert response.status_code == 502
    assert response.json()["detail"] == (
        "The AI support service is temporarily unavailable."
    )


def test_message_too_short():
    response = client.post("/support", json={"message": "Hi"})
    assert response.status_code == 422


def test_message_too_long():
    response = client.post("/support", json={"message": "a" * 2001})
    assert response.status_code == 422


def test_message_with_empty_string():
    response = client.post("/support", json={"message": ""})
    assert response.status_code == 422
