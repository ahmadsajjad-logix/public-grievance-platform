import io
import pytest
from pypdf import PdfReader
from grievance.catalog import DEPARTMENTS
from grievance.knowledge import route
from grievance import agents


@pytest.mark.parametrize("department", list(DEPARTMENTS.values()), ids=list(DEPARTMENTS))
def test_every_department_can_prepare_route(department):
    result = route("Service complaint", department.category, [],
                   region=department.regions[0] if department.regions else "Punjab",
                   department_id=department.id, city="District office")
    assert result["target_id"] == department.id
    assert result["statutory_deadline"] is None
    assert result["portal"].startswith("https://")


def test_escalation_and_court_safeguards():
    args = dict(region="Punjab", department_id="iesco",
                stage="Unresolved earlier complaint", prior_reference="ABC-123")
    assert route("Bill", "Electricity", [], **args)["target_id"] == "nepra"
    assert route("Bill", "Electricity", [], in_court=True, **args)["target_id"] == "iesco"
    args["stage"] = "Challenge a formal decision"
    result = route("Bill", "Electricity", [], **args)
    assert result["target_id"] == "iesco" and result["review_required"]
    args["prior_reference"] = ""
    with pytest.raises(ValueError):
        route("Bill", "Electricity", [], **args)


def test_wrong_province_rejected():
    with pytest.raises(ValueError):
        route("Bill", "Electricity", [], region="Sindh", department_id="lesco")


def test_long_urdu_pdf_embeds_fonts_and_paginates():
    case = agents.new_case("احمد", "Punjab", "بل درست کیا جائے", "12345", 14)
    case["intake"] = agents.intake("بجلی کا بل غلط ہے۔ IESCO reference 12345. " * 150, {})
    case["route"] = route("IESCO bill", "Electricity", [], department_id="iesco")
    case["attachments"] = []
    pdf = agents.petition(case)
    reader = PdfReader(io.BytesIO(pdf))
    assert len(reader.pages) > 2
    assert b"FontFile2" in pdf


def test_uploaded_manuals_cannot_cross_region_or_provider():
    manuals = [dict(name="wrong-region", category="Electricity", region=("Sindh",), text="billing"),
               dict(name="wrong-provider", category="Electricity", department_id="lesco", text="billing")]
    result = route("billing", "Electricity", manuals, department_id="iesco")
    assert not {"wrong-region", "wrong-provider"} & {hit["name"] for hit in result["matches"]}
