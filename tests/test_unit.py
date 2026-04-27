from backend.core.memory import create_session, add_message, get_messages

def test_create_session():
    session_id = create_session("user1")
    assert isinstance(session_id, int)


def test_add_message():
    session_id = create_session("user1")
    add_message(session_id, "user", "Hello")

    messages = get_messages(session_id)
    assert messages[-1]["content"] == "Hello"