from datetime import date
from pathlib import Path
import pytest
from grievance.identity import validate_identity


def test_identity_normalizes_formats():
    result = validate_identity("1234512345671", date(2030, 1, 1), "+92 300-1234567")
    assert result == {"cnic": "12345-1234567-1", "cnic_expiry": "2030-01-01", "mobile": "03001234567"}


@pytest.mark.parametrize("cnic,expiry,mobile", [
    ("", date(2030, 1, 1), "03001234567"),
    ("12345-1234567-1", None, "03001234567"),
    ("12345-1234567-1", date(2030, 1, 1), ""),
    ("123451234567x", date(2030, 1, 1), "03001234567"),
    ("1234512345671", date(2030, 1, 1), "12345678901"),
])
def test_invalid_identity_is_rejected(cnic, expiry, mobile):
    with pytest.raises(ValueError):
        validate_identity(cnic, expiry, mobile)


def test_text_only_app_blocks_missing_identity():
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
    assert not app.exception
    assert not any(r.label == "Input method" for r in app.radio)
    assert not any(b.label == "Transcribe audio" for b in app.button)
    app.text_area(key="narrative").set_value("IESCO billing complaint")
    app.selectbox(key="department").set_value("iesco").run()
    next(b for b in app.button if b.label == "Prepare my grievance").click().run()
    assert app.session_state["current"] is None
    assert any("13-digit CNIC" in e.value for e in app.error)
