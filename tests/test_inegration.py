from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_session_api():
    res = client.get("/session")
    assert res.status_code == 200


def test_chat_api():
    res = client.get("/session")
    session_id = res.json()["session_id"]

    res = client.post("/chat", json={
        "message": "Hello",
        "session_id": session_id
    })

    assert res.status_code == 200
    assert "response" in res.json()