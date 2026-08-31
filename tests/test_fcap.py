"""Tests for the FCAP platform: prompt handling, response validation, storage and routes."""

import pytest
from fastapi.testclient import TestClient

from fcap import config, database
from fcap.llm import UNAVAILABLE_MESSAGE, _clean_content, _extract_content, get_ai_response
from fcap.prompts import build_healthcare_prompt


@pytest.fixture()
def db(tmp_path, monkeypatch):
    path = str(tmp_path / "fcap.db")
    monkeypatch.setattr(config, "DB_PATH", path)
    database.init_database(path)
    return path


@pytest.fixture()
def client(db):
    from fcap import api
    return TestClient(api.app)


def test_prompt_includes_the_patient_message():
    prompt = build_healthcare_prompt("my chest hurts")
    assert "my chest hurts" in prompt
    assert "Dr. Sarah" in prompt


def test_clean_content_strips_echoed_prefix():
    assert _clean_content("Dr. Sarah's response: Please call 911.") == "Please call 911."
    assert _clean_content("Dr. Sarah: Your appointment is set.") == "Your appointment is set."


@pytest.mark.parametrize("bad", ["short", "   ", "1234567890123456789012"])
def test_clean_content_rejects_unusable_replies(bad):
    with pytest.raises(Exception):
        _clean_content(bad)


def test_extract_content_rejects_empty_response():
    with pytest.raises(Exception, match="Empty response"):
        _extract_content(None)


def test_get_ai_response_degrades_without_a_fallback_model(monkeypatch):
    import fcap.llm as llm

    def boom(_message):
        raise Exception("upstream 503")

    monkeypatch.setattr(llm, "get_gpt_oss_response", boom)
    assert llm.get_ai_response("hello") == UNAVAILABLE_MESSAGE


def test_require_token_explains_how_to_set_it(monkeypatch):
    monkeypatch.setattr(config, "HF_TOKEN", "")
    with pytest.raises(RuntimeError, match="HF_TOKEN"):
        config.require_token()


def test_appointments_round_trip(db):
    assert database.list_appointments(db) == []
    database.create_appointment("Ada Lovelace", "ada@example.com",
                                "2026-09-01", "10:00", "Dr. Smith", db_path=db)
    rows = database.list_appointments(db)
    assert len(rows) == 1
    assert rows[0]["patient_name"] == "Ada Lovelace"
    assert rows[0]["status"] == "scheduled"


def test_conversation_is_saved(db):
    database.save_conversation("s1", "hello", "hi there", db_path=db)
    import sqlite3
    with sqlite3.connect(db) as conn:
        rows = conn.execute("select session_id, message, response from conversations").fetchall()
    assert rows == [("s1", "hello", "hi there")]


@pytest.mark.parametrize("path", ["/", "/clinic", "/admin"])
def test_interfaces_render_complete_html(client, path):
    response = client.get(path)
    assert response.status_code == 200
    body = response.text.strip()
    assert body.startswith("<!DOCTYPE html>")
    assert body.endswith("</html>")


def test_appointment_endpoints(client):
    assert client.get("/appointments").json() == []
    created = client.post("/appointments", data={
        "patient_name": "Grace Hopper",
        "patient_email": "grace@example.com",
        "appointment_date": "2026-09-02",
        "appointment_time": "14:30",
    })
    assert created.status_code == 200
    listed = client.get("/appointments").json()
    assert len(listed) == 1
    # doctor_name falls back to the documented default
    assert listed[0]["doctor_name"] == "Dr. Smith"


def test_chat_endpoint_persists_the_exchange(client, monkeypatch, db):
    import fcap.api as api
    monkeypatch.setattr(api, "get_ai_response", lambda m: "Happy to help with your appointment.")
    response = client.post("/chat", json={"message": "book me in", "session_id": "abc"})
    assert response.status_code == 200
    assert response.json()["session_id"] == "abc"

    import sqlite3
    with sqlite3.connect(db) as conn:
        rows = conn.execute("select session_id, message from conversations").fetchall()
    assert rows == [("abc", "book me in")]
