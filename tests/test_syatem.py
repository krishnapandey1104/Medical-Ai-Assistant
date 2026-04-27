from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_full_flow():
    # Create session
    res = client.get("/session")
    session_id = res.json()["session_id"]

    # Chat
    res = client.post("/chat", json={
        "message": "Explain report",
        "session_id": session_id
    })

    assert res.status_code == 200