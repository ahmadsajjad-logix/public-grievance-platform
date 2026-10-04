from pathlib import Path

import pytest

from grievance.knowledge import detect, route

COMPLAINT = "Green Entertainment tv dramma mitti the bawa theme and content is against the cultural and religious norms of Pakistan"
CATEGORY = "Electronic Media (Radio, TV, Cable TV, etc.)"


@pytest.mark.parametrize("region,department", [
    ("Punjab", "pemra-lahore"), ("Sindh", "pemra-karachi"),
    ("Khyber Pakhtunkhwa", "pemra-peshawar"), ("Balochistan", "pemra-quetta"),
    ("Islamabad", "pemra-islamabad"), ("Gilgit-Baltistan", "pemra"),
    ("Azad Jammu and Kashmir", "pemra"),
])
def test_user_complaint_suggests_council(region, department):
    assert detect(COMPLAINT, region) == (CATEGORY, department)
    result = route(COMPLAINT, "Detect automatically", [], region=region)
    assert result["department_id"] == department
    assert result["endpoint_verified"] == (department != "pemra")
    assert any("20(b)" in p["citation"] for p in result["legal_provisions"])


@pytest.mark.parametrize("text", ["TV programme content is offensive", "This dramma is offensive", "ٹی وی ڈراما پر شکایت", "television advertisement complaint"])
def test_media_wording_variants(text):
    assert detect(text, "Punjab") == (CATEGORY, "pemra-lahore")


def test_generic_content_is_not_assumed_to_be_broadcast():
    with pytest.raises(ValueError, match="unclear"):
        detect("This content is against cultural and religious norms", "Punjab")
    assert detect("online harassment and blackmail", "Punjab")[0] == "Cybercrime"


def test_suggestion_button_selects_council_for_user_complaint():
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
    app.text_area(key="narrative").set_value(COMPLAINT)
    next(b for b in app.button if b.label == "suggest Complaint based relevant department").click().run()
    assert not app.exception
    assert app.selectbox(key="category").value == CATEGORY
    assert app.selectbox(key="department").value == "pemra-lahore"
    assert not any("Jurisdiction is unclear" in w.value for w in app.warning)
