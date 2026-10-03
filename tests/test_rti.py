from pathlib import Path
import pytest
from grievance.rti import PROFILES, request_draft


def test_draft_requires_known_jurisdiction_and_actual_records():
    with pytest.raises(ValueError):
        request_draft("AJK / Gilgit-Baltistan / unsure", "Office", "Report", "2026", "Electronic copies")
    with pytest.raises(ValueError):
        request_draft("Federal public body", "", "Report", "2026", "Electronic copies")
    draft = request_draft("Punjab public body", "District office", "Inspection report for ABC", "September 2026", "Electronic copies")
    assert "Punjab Transparency" in draft and "Inspection report for ABC" in draft
    assert "not submitted" in draft


def test_rti_sidebar_and_all_jurisdictions_render():
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
    app.sidebar.radio[0].set_value("Right to Information (RTI)").run()
    for jurisdiction in PROFILES:
        app.selectbox[0].set_value(jurisdiction).run()
        assert not app.exception
        assert app.get("link_button")[0].proto.url == PROFILES[jurisdiction]["link"]
