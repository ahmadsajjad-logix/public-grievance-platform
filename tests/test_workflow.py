from datetime import timedelta
import pytest
from pathlib import Path
from grievance import agents
from grievance.knowledge import route, retrieve, detect

def test_routing_and_ambiguity():
    assert detect("Mera bijli bill ghalat hai", "Punjab")[0] == "Electricity"
    assert detect("بجلی کا بل", "Punjab")[0] == "Electricity"
    assert route("IESCO bill", "Detect automatically", [])["department_id"] == "iesco"
    with pytest.raises(ValueError):
        route("بجلی کا بل", "Detect automatically", [])
    with pytest.raises(ValueError):
        route("Please help", "Detect automatically", [])

def test_audit_does_not_count_empty_uploads():
    assert agents.audit({"CNIC": {"bytes": b""}}, "Electricity")["score"] == 0
    assert agents.audit({"CNIC": {"bytes": b"x"}, "Service evidence": {"bytes": b"x"}}, "Telecom")["score"] == 100

def test_pdf_calendar_and_simulation():
    case = agents.new_case("Applicant <safe>", "Sindh", "Correct the bill", "12345678", 14)
    case["intake"] = agents.intake("Excessive electricity bill", {})
    case["route"] = route(case["intake"]["text"], "Electricity", [], region="Sindh", department_id="ke")
    case["attachments"] = []
    assert agents.petition(case).startswith(b"%PDF")
    result = agents.dispatch(case, "Electronic (simulation)")
    assert result["tracking_id"].startswith("DEMO-")
    assert result["status"] == "Demo dispatch"
    content = agents.calendar(case).decode()
    assert "DTSTART;VALUE=DATE:" + case["due"].strftime("%Y%m%d") in content
    assert "DTEND;VALUE=DATE:" + (case["due"] + timedelta(days=1)).strftime("%Y%m%d") in content
    assert case["route"]["statutory_deadline"] is None

def test_reference_extraction_and_retrieval():
    result = agents.intake("Reference number: 123456789 Date 01/10/2026", {})
    assert result["references"] and result["dates"] == ["01/10/2026"]
    hits, _ = retrieve("billing", [{"text": "electricity billing rules", "name": "manual"}])
    assert hits[0]["name"] == "manual"

def test_streamlit_startup():
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
    assert not app.exception

def test_streamlit_prepares_case():
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
    app.text_area[0].set_value("My electricity bill is incorrect; please investigate.")
    app.selectbox(key="department").set_value("iesco").run()
    from datetime import date
    app.text_input(key="cnic").set_value("12345-1234567-1")
    app.date_input(key="cnic_expiry").set_value(date(2030, 1, 1))
    app.text_input(key="mobile").set_value("03001234567")
    next(b for b in app.button if b.label == "Prepare my grievance").click().run(timeout=20)
    assert not app.exception
    assert app.session_state["current"]["route"]["stage"] == "First complaint"
    assert app.session_state["current"]["pdf"].startswith(b"%PDF")
    assert all(state == "Complete" for state in app.session_state["pipeline"].values())

def test_analytics_privacy_and_idempotency(tmp_path, monkeypatch):
    from grievance import storage
    monkeypatch.setattr(storage, "DB", tmp_path / "analytics.sqlite3")
    case = agents.new_case("Private Name", "Punjab", "Private remedy", "private-id", 7)
    case["route"] = route("internet", "Telecom", [], department_id="pta")
    case["dispatch"] = agents.dispatch(case, "Electronic (simulation)")
    storage.save_aggregate(case)
    storage.save_aggregate(case)
    rows = storage.aggregates()
    assert sum(row["count"] for row in rows) == 1
    assert "Private Name" not in str(rows)
    assert "private-id" not in str(rows)

def test_manuals_stay_in_jurisdiction():
    result = route("billing", "Telecom", [{"category": "Electricity", "text": "billing", "name": "wrong-manual"}], department_id="pta")
    assert all(hit["name"] != "wrong-manual" for hit in result["matches"])
