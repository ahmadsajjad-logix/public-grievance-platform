import io
from pypdf import PdfReader
from grievance import agents
from grievance.catalog import DEPARTMENTS
from grievance.guidance import department_guide, research_documents, guide_sections, PROFILES
from grievance.knowledge import route
from grievance.petitions import build_petition
from grievance.reference_library import library, scoped_references


def test_every_directory_entry_has_honest_guidance():
    for id in DEPARTMENTS:
        g = department_guide(id)
        assert g["can"] and g["cannot"] and g["procedure"] and g["sources"]
        if id not in PROFILES:
            assert g["reviewed"] is None
            assert g["channels"][0]["kind"] == "directory"
    assert department_guide("kwsc")["character_limit"] == 350
    assert department_guide("ke")["channels"][0]["value"] == "+923480000118"


def test_reference_library_is_scoped_and_does_not_promote_old_documents():
    assert len(library()["documents"]) == 18
    refs = scoped_references({"pta"}, "Sindh")
    assert refs and any("visually reviewed" in r["evidence_type"] for r in refs)
    assert all("pta" in r["department_ids"] for r in refs)
    refs = scoped_references({"iesco"}, "Islamabad")
    assert any("2025" in r["name"] and r["page"] == 65 for r in refs)
    assert not any("Notification-SRO" in r["name"] for r in refs)
    assert all(not r["trusted"] for r in refs)
    assert not scoped_references({"punjab-rts"}, "Sindh")


def test_escalation_guide_describes_receiving_authority():
    r = route("IESCO wrong meter reading", "Electricity", [], region="Islamabad", department_id="iesco",
              stage="Unresolved earlier complaint", prior_reference="TEST-1")
    assert r["filing_guide"]["department_id"] == "nepra"
    assert any("10.3.1(a)" in p["citation"] for p in r["legal_provisions"])
    other = route("IESCO supply interruption", "Electricity", [], region="Islamabad", department_id="iesco")
    assert not any("10.3.1(a)" in p["citation"] for p in other["legal_provisions"])


def test_guidance_pdf_has_ambit_channels_sources_and_no_case_identity():
    case = agents.new_case("PRIVATE TEST NAME", "Sindh", "PRIVATE REMEDY", "PRIVATE-REF", 14)
    case["intake"] = agents.intake("PRIVATE NARRATIVE", {})
    case["route"] = route("K-Electric billing", "Electricity", [], region="Sindh", department_id="ke")
    case["attachments"] = []
    result = build_petition(case, guide_sections(case["route"]["filing_guide"]))
    text = "\n".join(p.extract_text() for p in PdfReader(io.BytesIO(result)).pages)
    for expected in ("What this authority can help with", "Limits and exclusions", "+923480000118", "ke.com.pk", "Opening hours not verified"):
        assert expected in text
    assert "PRIVATE" not in text


def test_research_corpus_and_conflict_are_visible():
    assert {d["department_id"] for d in research_documents()} >= {"nepra", "pta", "pemra", "wafaqi"}
    assert "Source conflict" in department_guide("ogra")["limits"]
    assert "commencement" in department_guide("punjab-rts")["procedure"][0]
