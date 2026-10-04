import json
from pathlib import Path
from datetime import date

import pytest

from grievance import llm, agents
from grievance.knowledge import route


def test_settings_do_not_reuse_openai_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "unrelated")
    assert llm.settings({})[0] == ""
    assert llm.settings({"GROQ_API_KEY": "private-key"})[0] == "private-key"


def test_sensitive_patterns_are_masked():
    text = llm.redact("Ali 12345-1234567-1 03001234567 ali@example.com", ["Ali"])
    assert "12345" not in text and "0300" not in text and "ali@example.com" not in text


def test_suggestion_rejects_cross_province_and_unknown_ids(monkeypatch):
    for id in ("invented", "pemra-karachi"):
        monkeypatch.setattr(llm, "request_json", lambda *a, id=id: llm.Suggestion(
            category="Electronic Media (Radio, TV, Cable TV, etc.)", department_id=id, explanation="", questions=[]))
        with pytest.raises(llm.AIUnavailable):
            llm.suggest("TV drama", "Punjab", "test")


def test_request_uses_strict_schema_and_hides_errors(monkeypatch):
    captured = {}
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self, size):
            return json.dumps({"choices": [{"finish_reason": "stop", "message": {"content": json.dumps(dict(
                category="Telecom", department_id="jazz", explanation="Operator complaint", questions=[]))}}]}).encode()
    def call(request, timeout):
        captured.update(json.loads(request.data))
        assert request.full_url == llm.ENDPOINT and timeout == 35
        return Response()
    monkeypatch.setattr(llm, "urlopen", call)
    result = llm.suggest("Jazz complaint 03001234567", "Punjab", "secret")
    assert result.department_id == "jazz"
    assert captured["response_format"]["json_schema"]["strict"]
    assert "03001234567" not in str(captured)
    monkeypatch.setattr(llm, "urlopen", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("secret private complaint")))
    with pytest.raises(llm.AIUnavailable) as exc:
        llm.suggest("Jazz complaint", "Punjab", "secret")
    assert "secret" not in str(exc.value) and "private complaint" not in str(exc.value)


def test_draft_excludes_identity_uploads_and_rejects_invented_sources(monkeypatch):
    case = agents.new_case("Private Person", "Punjab", "Correct bill", "ACCOUNT-PRIVATE", 14)
    case.update(identity={"cnic": "12345-1234567-1", "mobile": "03001234567"},
                intake=agents.intake("Private Person Jazz bill ACCOUNT-PRIVATE", {}),
                route=route("Jazz bill", "Telecom", [], department_id="jazz"),
                attachments=["PRIVATE-UPLOAD"])
    def response(key, model, system, payload, output_type):
        assert all(value not in str(payload) for value in ["Private Person", "ACCOUNT-PRIVATE", "12345-1234567-1", "03001234567", "PRIVATE-UPLOAD"])
        return llm.Draft(statement="Review this bill", remedy="Correct it", source_ids=[999], questions=[])
    monkeypatch.setattr(llm, "request_json", response)
    with pytest.raises(llm.AIUnavailable):
        llm.draft(case, "test")
    case["ai_draft"] = {"statement": "UNREVIEWED"}
    assert "UNREVIEWED" not in agents.filing_text(case)
    case["reviewed_statement"] = "Reviewed statement"
    assert "Reviewed statement" in agents.filing_text(case)


def test_ui_ai_falls_back_without_breaking_manual_workflow(monkeypatch):
    from streamlit.testing.v1 import AppTest
    monkeypatch.setenv("GROQ_API_KEY", "fake-test-key")
    def fail(*a, **k): raise llm.AIUnavailable("AI temporarily unavailable")
    monkeypatch.setattr(llm, "suggest", fail)
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
    app.checkbox(key="ai_enabled").set_value(True)
    app.text_area(key="narrative").set_value("Jazz billing complaint")
    next(b for b in app.button if b.label == "suggest Complaint based relevant department").click().run()
    assert not app.exception
    assert app.selectbox(key="department").value == "jazz"


def test_drafting_requires_opt_in_and_review(monkeypatch):
    from streamlit.testing.v1 import AppTest
    monkeypatch.setenv("GROQ_API_KEY", "fake-test-key")
    calls = []
    def fake_draft(*args):
        calls.append(True)
        return llm.Draft(statement="Please examine the disputed bill.", remedy="Correct the bill.", source_ids=[], questions=[])
    monkeypatch.setattr(llm, "draft", fake_draft)
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
    app.text_area(key="narrative").set_value("My electricity bill is incorrect")
    app.selectbox(key="department").set_value("iesco").run()
    app.text_input(key="applicant_name").set_value("Test Person")
    app.text_input(key="cnic").set_value("12345-1234567-1")
    app.text_input(key="mobile").set_value("03001234567")
    app.date_input(key="cnic_expiry").set_value(date(2030, 1, 1))
    next(b for b in app.button if b.label == "Prepare my grievance").click().run(timeout=20)
    assert not app.exception and not calls
    app.checkbox(key="ai_enabled").set_value(True).run()
    next(b for b in app.button if b.label == "Prepare my grievance").click().run(timeout=20)
    assert not app.exception and len(calls) == 1
    assert "reviewed_statement" not in app.session_state["current"]
    next(b for b in app.button if b.label == "Use this reviewed wording in my petition").click().run(timeout=20)
    case = app.session_state["current"]
    assert not app.exception and case["reviewed_statement"] == "Please examine the disputed bill."
    assert case["intake"]["text"] == "My electricity bill is incorrect"
    assert len(calls) == 1  # Reruns and review must not make extra API requests.
