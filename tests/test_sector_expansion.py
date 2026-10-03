import pytest
from grievance.catalog import CATEGORIES, DEPARTMENTS, available_departments
from grievance.guidance import department_guide
from grievance.knowledge import detect, route
from grievance.legal import filing_profile


@pytest.mark.parametrize("id,region", [("mepco", "Punjab"), ("tesco", "Khyber Pakhtunkhwa"), ("hazeco", "Khyber Pakhtunkhwa")])
def test_new_disco_first_complaint_and_escalation(id, region):
    first = route("incorrect meter reading", "Electricity", [], region=region, department_id=id)
    assert first["target_id"] == id
    assert first["legal_provisions"]
    assert department_guide(id)["channels"][0]["value"] == "https://ccms.pitc.com.pk/complaint"
    later = route("incorrect meter reading", "Electricity", [], region=region, department_id=id,
                  stage="Unresolved earlier complaint", prior_reference="TICKET-1")
    assert later["target_id"] == "nepra"


@pytest.mark.parametrize("id,text", [("jazz", "Jazz balance deducted"), ("zong", "زونگ انٹرنیٹ"),
    ("ufone", "یوفون سگنل"), ("telenor", "Telenor connection"), ("onic", "Onic activation"), ("ptcl", "پی ٹی سی ایل بل")])
def test_operator_first_then_pta(id, text):
    assert detect(text, "Punjab") == ("Telecom", id)
    first = route(text, "Detect automatically", [])
    assert first["target_id"] == id
    no_ticket = route(text, "Telecom", [], department_id=id, stage="Unresolved earlier complaint")
    assert no_ticket["target_id"] == id
    later = route(text, "Telecom", [], department_id=id, stage="Unresolved earlier complaint", prior_reference="OP-1")
    assert later["target_id"] == "pta"
    assert all(hit.get("department_id") in (id, "pta") or set(hit.get("department_ids", [])) & {id, "pta"} for hit in later["matches"])


def test_regional_and_financial_boundaries():
    assert "scom" not in [d.id for d in available_departments("Telecom", "Punjab")]
    assert "scom" in [d.id for d in available_departments("Telecom", "Gilgit-Baltistan")]
    assert available_departments("Telecom", "Punjab")[-1].id == "pta"
    assert detect("Jazz cash transaction failed", "Punjab") == ("Banking", None)
    assert {d.id for d in available_departments("Banking", "Punjab")} == {"sbp", "banking-mohtasib"}
    for id in ("banking-mohtasib", "sbp"):
        assert not DEPARTMENTS[id].escalation
        assert filing_profile(id, "Punjab", "unauthorized debit")["legal_provisions"]
    pending = route("unauthorized debit", "Banking", [], department_id="banking-mohtasib", in_court=True)
    assert not pending["legal_provisions"]
    assert "30 days" in department_guide("banking-mohtasib")["limits"]


def test_electronic_media_category():
    category = "Electronic Media (Radio, TV, Cable TV, etc.)"
    assert category in CATEGORIES and "Broadcasting" not in CATEGORIES
    assert detect("PEMRA drama complaint", "Islamabad") == (category, "pemra")
