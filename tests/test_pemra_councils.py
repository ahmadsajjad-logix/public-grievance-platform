import io
from pathlib import Path

import pytest
from pypdf import PdfReader

from grievance import agents
from grievance.catalog import available_departments
from grievance.guidance import department_guide
from grievance.knowledge import detect, route
from grievance.legal import filing_profile

CATEGORY = "Electronic Media (Radio, TV, Cable TV, etc.)"
CASES = [
    ("Punjab", "pemra-lahore", "Lahore", "319-A"),
    ("Sindh", "pemra-karachi", "Karachi", "D-71"),
    ("Khyber Pakhtunkhwa", "pemra-peshawar", "Peshawar", "Workers Welfare"),
    ("Balochistan", "pemra-quetta", "Quetta", "53/2"),
    ("Islamabad", "pemra-islamabad", "Islamabad", "G-8/1"),
]


@pytest.mark.parametrize("region,id,city,address", CASES)
def test_council_selection_routes_pdf_and_guidance(region, id, city, address):
    assert [d.id for d in available_departments(CATEGORY, region)] == [id]
    assert detect("PEMRA drama complaint", region) == (CATEGORY, id)
    result = route("Drama content against religious values", CATEGORY, [], region=region, department_id=id)
    assert result["endpoint_verified"] and city in result["body"]
    assert address in result["address"]
    assert result["legal_provisions"]
    assert filing_profile("pemra", region, "drama")["recipient"] == result["body"]
    guide = department_guide(id)
    assert guide["recipient"] == result["body"]
    assert address in guide["address"] and guide["map"]
    assert guide["local_documents"]
    case = agents.new_case("Test applicant", region, "Examine the programme", "", 14)
    case.update(intake=agents.intake("Drama content against religious values", {}), route=result, attachments=[])
    text = "\n".join(p.extract_text() for p in PdfReader(io.BytesIO(agents.petition(case))).pages)
    assert city in text and address in text and "26(2)" in text


def test_councils_do_not_bypass_territory_or_appeal_checks():
    with pytest.raises(ValueError, match="not listed"):
        route("drama", CATEGORY, [], region="Sindh", department_id="pemra-lahore")
    assert not filing_profile("pemra-lahore", "Sindh", "drama")["endpoint_verified"]
    for region in ("Gilgit-Baltistan", "Azad Jammu and Kashmir"):
        assert not filing_profile("pemra", region, "drama")["endpoint_verified"]
    result = route("drama", CATEGORY, [], region="Punjab", department_id="pemra-lahore",
                   stage="Challenge a formal decision", prior_reference="Decision 1")
    assert not result["endpoint_verified"] and not result["legal_provisions"]


def test_province_switch_clears_stale_council_and_no_missing_recipient_warning():
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
    app.selectbox(key="category").set_value(CATEGORY).run()
    for region, id, city, address in CASES:
        app.selectbox(key="region").set_value(region).run()
        assert app.selectbox(key="department").value is None
        app.selectbox(key="department").set_value(id).run()
        assert not app.exception
        assert not any("verified regional filing recipient" in w.value for w in app.warning)
        assert any(s.label == "PEMRA complaint type" for s in app.selectbox)
    for region in ("Azad Jammu and Kashmir", "Gilgit-Baltistan"):
        app.selectbox(key="region").set_value(region).run()
        app.selectbox(key="department").set_value("pemra").run()
        assert not app.exception
        assert any("verified regional filing recipient" in w.value for w in app.warning)
