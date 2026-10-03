from pathlib import Path
import pytest
from grievance.offences import OFFENCES, assess, report
from grievance.forms import form_guide, form_values
from grievance.guidance import department_guide, guide_text
from grievance import agents


@pytest.mark.parametrize("offence", OFFENCES)
def test_unconfirmed_and_negative_facts_never_confirm_offence(offence):
    questions = OFFENCES[offence]["questions"]
    assert "More facts" in assess(offence, ["Not sure"] * len(questions))
    assert "not all supported" in assess(offence, ["No"] + ["Yes"] * (len(questions) - 1))
    assert "do not establish" in assess(offence, ["Yes"] * len(questions))
    with pytest.raises(ValueError):
        assess(offence, [])


def test_territory_report_and_procedure_separated():
    text = report("identity", ["Yes"], "Gilgit-Baltistan", None, "Test facts")
    assert "Territorial application needs verification" in text
    assert "support considering" not in text
    assert "CrPC 154" in text and "CrPC 155" in text and "22-A(6)" in text
    assert "PECA 16(1)" in text and "complaint.nccia.gov.pk" in text
    assert "No complaint has been transmitted" in text


def test_form_help_preserves_boundaries_and_values():
    assert form_guide("nccia")["verified"]
    assert not form_guide("punjab-1")["verified"]
    guide = form_guide("kwsc")
    assert any("350" in f["help"] for f in guide["fields"])
    case = agents.new_case("PRIVATE NAME", "Sindh", "Correct service", "REF-1", 14)
    case.update(intake={"text": "My factual account"}, identity={"cnic": "PRIVATE-CNIC"},
                route={"legal_provisions": [], "prior_reference": "PRIOR-1"})
    values = form_values(case)
    assert values["reference"] == "REF-1" and values["prior_reference"] == "PRIOR-1"
    assert "PRIVATE" not in str(values)
    assert "Official form assistance" in guide_text(department_guide("nccia"))


def test_offence_ui_is_accessible_without_identity_and_keeps_answers_separate():
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
    app.sidebar.radio[0].set_value("FIR & Offence Guide").run()
    app.selectbox(key="offence").set_value("theft").run()
    assert not app.exception
    assert not app.text_input  # No identity gate for reading law/reporting guidance.
    assert all(r.value == "Not sure" for r in app.radio if r.key and r.key.startswith("fact-"))
    app.radio(key="fact-theft-0").set_value("Yes").run()
    app.selectbox(key="offence").set_value("identity").run()
    assert app.radio(key="fact-identity-0").value == "Not sure"
    assert not app.exception
    app.selectbox(key="fir_region").set_value("Azad Jammu and Kashmir").run()
    assert any("Territorial application" in i.value for i in app.info)
