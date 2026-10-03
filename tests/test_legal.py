from grievance.knowledge import route
from grievance.legal import filing_profile
from grievance import agents
from pypdf import PdfReader
import io


def test_islamabad_content_complaint_has_recipient_and_relevant_law():
    result = route("Drama content against cultural and religious norms", "Broadcasting", [], region="Islamabad", department_id="pemra")
    assert result["body"] == "Regional Director, PEMRA Islamabad / Secretary, Council of Complaints Islamabad"
    assert result["endpoint_verified"]
    clauses = " ".join(p["citation"] for p in result["legal_provisions"])
    for expected in ("26(2)", "8(1)", "11(1)", "20(b)", "3(1)(a)"):
        assert expected in clauses
    assert "3(1)(e)" not in clauses  # Do not invent an obscenity allegation.


def test_unresearched_region_and_department_never_claim_verified_endpoint():
    assert not filing_profile("pemra", "Punjab", "drama")["endpoint_verified"]
    result = filing_profile("pta", "Islamabad", "billing")
    assert not result["endpoint_verified"] and not result["legal_provisions"]


def test_service_wage_and_appeal_do_not_reuse_content_provisions():
    for kind in ("Cable / distribution service", "Employee wages"):
        assert not filing_profile("pemra", "Islamabad", "content", kind)["legal_provisions"]
    result = route("drama", "Broadcasting", [], region="Islamabad", department_id="pemra", stage="Challenge a formal decision", prior_reference="Test decision")
    assert not result["legal_provisions"] and not result["endpoint_verified"]


def test_pdf_contains_sources_and_legal_provisions():
    case = agents.new_case("Test applicant", "Islamabad", "Please examine the identified programme", "", 14)
    case["intake"] = agents.intake("Drama content against cultural and religious norms", {})
    case["route"] = route(case["intake"]["text"], "Broadcasting", [], region="Islamabad", department_id="pemra")
    case["attachments"] = []
    text = "\n".join(p.extract_text() for p in PdfReader(io.BytesIO(agents.petition(case))).pages)
    assert "Regional Director, PEMRA Islamabad" in text
    assert "20(b)" in text and "coc_rules_2010.pdf" in text


def test_portal_text_preserves_complaint_remedy_and_law_without_identity_fields():
    case = agents.new_case("Private applicant", "Islamabad", "Examine the identified scenes", "SERVICE-42", 14)
    case["identity"] = {"cnic": "12345-1234567-1", "mobile": "03001234567"}
    case["intake"] = agents.intake("ڈرامہ مذہبی اقدار کے خلاف ہے", {})
    case["route"] = route(case["intake"]["text"], "Broadcasting", [], region="Islamabad", department_id="pemra")
    text = agents.filing_text(case)
    assert case["intake"]["text"] in text
    assert case["remedy"] in text and "SERVICE-42" in text
    assert "20(b)" in text and "Source:" in text
    assert case["identity"]["cnic"] not in text
    assert case["identity"]["mobile"] not in text
    assert case["name"] not in text
