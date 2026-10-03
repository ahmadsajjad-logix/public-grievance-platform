from pathlib import Path
from grievance.channels import complaint_links
from grievance.catalog import DEPARTMENTS
from grievance.guidance import department_guide, PROFILES


def test_coverage_and_source_provenance():
    assert set(PROFILES) == set(DEPARTMENTS)
    for id in DEPARTMENTS:
        guide = department_guide(id)
        assert guide["laws"] and guide["procedure"] and guide["requirements"]
        assert all(law["source"].startswith("https://") for law in guide["laws"])
        assert all(c["source"] in guide["sources"] for c in guide["channels"])


def test_actual_forms_are_distinct_from_portals_and_information():
    assert complaint_links(department_guide("nccia"))[0]["label"] == "Open official complaint form"
    assert complaint_links(department_guide("pta"))[0]["label"] == "Open official complaint portal"
    assert all(link["kind"] != "form" for link in complaint_links(department_guide("pemra")))
    assert complaint_links(department_guide("sngpl"))[0]["url"].endswith("complaints.jsp?mdids=89")
    assert "Karachi" in complaint_links(department_guide("sindh-1"))[0]["label"]
    assert all(link["kind"] != "form" for link in complaint_links(department_guide("punjab-5")))


def test_unknown_and_unsafe_links_are_not_promoted():
    assert not complaint_links({"channels": [dict(kind="portal", value="javascript:alert(1)")]})


def test_directory_renders_all_routes_without_duplicate_widget_failure():
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
    app.sidebar.radio[0].set_value("Department Directory").run(timeout=30)
    assert not app.exception
    buttons = app.get("link_button")
    assert any(b.proto.url == "https://complaint.nccia.gov.pk/" for b in buttons)
    assert any(b.proto.url == "https://suthra.punjab.gov.pk/complaint.php" for b in buttons)
