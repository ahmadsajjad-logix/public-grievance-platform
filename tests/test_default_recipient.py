import io
from pathlib import Path

from pypdf import PdfReader
from grievance import agents
from grievance.catalog import DEPARTMENTS
from grievance.guidance import department_guide
from grievance.knowledge import route
from grievance.legal import filing_profile


def test_every_department_has_a_recipient_without_a_regional_requirement():
    for id, department in DEPARTMENTS.items():
        region = department.regions[0] if department.regions else "Punjab"
        profile = filing_profile(id, region, "Service complaint")
        assert profile["recipient"]
        if not profile["endpoint_verified"] and id != "pemra":
            assert profile["recipient"] == department.name
        assert department_guide(id, region, profile)["recipient"] == profile["recipient"]


def test_jazz_uses_provider_in_app_and_pdf():
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
    app.selectbox(key="category").set_value("Telecom").run()
    app.selectbox(key="department").set_value("jazz").run()
    assert not app.exception
    assert not app.warning
    result = route("Jazz billing complaint", "Telecom", [], region="Punjab", department_id="jazz")
    assert result["body"] == DEPARTMENTS["jazz"].name
    assert result["filing_guide"]["recipient"] == result["body"]
    case = agents.new_case("Applicant", "Punjab", "Correct the bill", "", 14)
    case.update(intake=agents.intake("Jazz billing complaint", {}), route=result, attachments=[])
    text = "\n".join(p.extract_text() for p in PdfReader(io.BytesIO(agents.petition(case))).pages)
    assert "Jazz" in text
    assert "Exact recipient / territorial jurisdiction requires verification" not in text


def test_regional_recipient_and_appeal_safeguards_remain():
    profile = filing_profile("pemra-gujranwala", "Punjab", "drama")
    assert profile["recipient"] == "Regional Director, PEMRA Gujranwala"
    result = route("Jazz billing complaint", "Telecom", [], department_id="jazz",
                   stage="Challenge a formal decision", prior_reference="Decision 1")
    assert "decision-specific review" in result["legal_status"]
