"""Run with: streamlit run app.py"""
from datetime import date
import streamlit as st
from grievance import agents
from grievance.identity import validate_identity
from grievance.legal import KINDS, filing_profile
from grievance.knowledge import detect
from grievance.catalog import CATEGORIES, DEPARTMENTS, REGIONS, STAGES, available_departments, REVIEW_DATE
from grievance.storage import aggregates, save_aggregate

st.set_page_config(page_title="Civic Access | Public Grievance", page_icon="⚖️", layout="wide")
for key, default in {"cases": [], "manuals": [], "pipeline": {}, "current": None}.items():
    st.session_state.setdefault(key, default)

st.sidebar.title("⚖️ Civic Access")
st.sidebar.caption("Pak Angels • Pakistan National Impact Challenge")
page = st.sidebar.radio("Workspace", ["Submit Grievance", "My drafts & filing records", "Analytics & Heatmap", "Department Directory", "Knowledge Base Admin"])
st.sidebar.info("Prepare here, submit to the authority yourself. Nothing is sent automatically. Private case details stay in this session on the app server; uploaded documents are not saved to disk.")
st.title("Public Grievance & Statutory Escalation Platform")
st.caption("A clearer path from a public service problem to a prepared complaint.")

def downloads(case):
    if not case:
        st.info("Prepare a grievance to see your petition and follow-up reminder.")
        return
    st.info(f"{case['route']['body']} • Draft prepared — not submitted by this app")
    st.caption(f"Local draft ID: {case['id'][:12]}. This is not an official tracking number.")
    st.subheader("Use your prepared complaint")
    st.write("For an online form, copy the complaint text below into its complaint/details field and the requested resolution into its relief field if separate. Complete the portal's identity and other required fields yourself.")
    prepared_text = agents.filing_text(case)
    with st.expander("Copy complaint text for an official form", expanded=True):
        st.caption("Use the copy button in the text box. Review the wording and the portal's character limit; this app does not know each portal's current limits. Identity details are kept out of this copyable text.")
        st.code(prepared_text, language=None, wrap_lines=True)
        st.write(f"{len(prepared_text):,} characters")
    st.write("Use the PDF as a supporting attachment only if the portal accepts it. Otherwise keep it as your complete written record, or sign and submit it by post/in person after confirming the receiving office and its requirements.")
    st.download_button("Download draft petition", case["pdf"], f"petition-{case['id'][:8]}.pdf", "application/pdf")
    st.download_button("Download calendar reminder", case["ics"], "follow-up.ics", "text/calendar")
    st.caption(f"Personal follow-up: {case['due'].date()}. This is not a statutory or appeal deadline.")
    st.write("Complaint concerns:", case["route"].get("department", case["route"]["body"]))
    st.warning(case["route"].get("legal_status", "Recipient and legal provisions require verification."))
    if case["route"].get("address"):
        st.write("Receiving office:", case["route"]["address"])
    for provision in case["route"].get("legal_provisions", []):
        st.write(provision["citation"] + ": " + provision["purpose"])
        st.link_button("Source: " + provision["citation"], provision["source"])
    st.write("Suggested next forum:", case["route"].get("escalation", "Review required"))
    for note in case["route"].get("notes", []):
        st.info(note)
    st.download_button("Download prepared complaint text (Urdu supported)", prepared_text.encode("utf-8-sig"), "complaint.txt", "text/plain")
    with st.expander("Petition preview", expanded=True):
        # Cloud's nested iframe blocks Chrome's PDF viewer. Render pages directly.
        from grievance.petitions import preview_pages
        for index, page_image in enumerate(preview_pages(case["pdf"])):
            st.image(page_image, caption=f"Page {index + 1}", width="stretch")
    st.subheader("Submission guidance")
    if case["route"]["portal"]:
        st.link_button(case["route"].get("channel", "Open authority website / portal"), case["route"]["portal"])
        st.caption("Opens an external authority page. Your complaint and files are not transferred or submitted by this button. A website/directory link may require you to find the complaint service; attachment support has not been verified.")
    for i, step in enumerate(case["dispatch"]["steps"], 1):
        st.write(f"{i}. {step}")
    st.caption("Local office addresses, maps and hours must be confirmed on the authority website before travel.")
    st.subheader("After you submit to the authority")
    st.caption("Save the acknowledgment on the authority's site. Record its reference here for this session only; this is your report of submission, not government confirmation or live tracking.")
    with st.form("filing-record-" + case["id"]):
        official_reference = st.text_input("Official acknowledgment / complaint reference", value=case.get("official_reference", ""), max_chars=160)
        save_filing = st.form_submit_button("Save my filing reference")
    if save_filing:
        case["official_reference"] = official_reference.strip()
    if case.get("official_reference"):
        st.info("Submission reported by you. Official reference: " + case["official_reference"])

if page == "Submit Grievance":
    intake_tab, output_tab = st.tabs(["Submit Grievance", "Petition & Downloads"])
    with intake_tab:
        st.subheader("Tell us what happened")
        region = st.selectbox("Province / territory of the complaint", REGIONS, key="region")
        st.caption("Write your complaint in Urdu, Roman Urdu or English. Select the department below or ask for a suggestion, then confirm it.")
        text = st.text_area("Complaint • English, Roman Urdu or Urdu", key="narrative", height=170, max_chars=12000)
        if st.button("Suggest department from my complaint"):
            try:
                suggested_category, suggested_id = detect(text, region)
                st.session_state["category"] = suggested_category
                options = available_departments(suggested_category, region)
                st.session_state["department"] = suggested_id if suggested_id in [d.id for d in options] else None
                if not suggested_id:
                    st.info("Service category suggested. Choose the exact provider or district office below.")
            except ValueError as exc:
                st.warning(str(exc))
        category = st.selectbox("Service category", CATEGORIES, key="category")
        departments = available_departments(category, region)
        ids = [None] + [d.id for d in departments]
        if st.session_state.get("department") not in ids:
            st.session_state["department"] = None
        department_id = st.selectbox("Department / provider", ids, key="department",
                                     format_func=lambda id: DEPARTMENTS[id].name if id else "Choose department / provider")
        if not departments:
            st.info("This region has no verified directory entry for this category yet. Choose a listed federal forum where applicable; local jurisdiction needs verification.")
        if department_id:
            department = DEPARTMENTS[department_id]
            st.caption(department.scope)
            if department.review_required:
                st.info("The district office or channel needs verification. Enter its name and location below.")
        complaint_kind = st.selectbox("PEMRA complaint type", KINDS) if department_id == "pemra" else None
        if department_id:
            filing = filing_profile(department_id, region, text, complaint_kind)
            st.info(filing["legal_status"])
            if not filing["endpoint_verified"]:
                st.warning("This entry does not yet have a verified regional filing recipient. A draft is available, but confirm the recipient and legal grounds before filing.")
            if department_id == "pemra":
                st.caption("Use the place where the programme was viewed for jurisdiction. Include channel, episode, broadcast date/time, and the specific scenes or dialogue in your complaint.")
        complaint_stage = st.selectbox("Complaint stage", STAGES)
        st.caption("First complaint goes to the selected office. An unresolved complaint may go to its regulator or eligible ombudsman. A formal appeal requires review of the decision and law.")
        with st.form("grievance"):
            left, right = st.columns(2)
            with left:
                st.markdown("**Required identity and contact details**")
                cnic = st.text_input("CNIC number (required)", placeholder="12345-1234567-1", max_chars=15, key="cnic")
                cnic_expiry = st.date_input("CNIC expiry date (required)", value=None, min_value=date(1900, 1, 1), max_value=date(2200, 12, 31), key="cnic_expiry")
                mobile = st.text_input("Mobile number (required)", placeholder="03001234567", max_chars=20, key="mobile")
                st.caption("These details stay in this session and appear in your draft PDF. They are not included in aggregate analytics. Format checks do not verify identity or phone ownership.")
                name = st.text_input("Applicant name (optional)", max_chars=120)
                city = st.text_input("City / district and exact office or facility (optional)", max_chars=240)
                remedy = st.text_area("What resolution do you want?", value="Please investigate this complaint, correct the service issue, and provide a written response.", max_chars=3000)
                reference = st.text_input("Service / consumer / application reference (optional)", max_chars=100)
                prior_reference = st.text_input("Earlier complaint or decision reference / date (optional)", max_chars=160)
                in_court = st.checkbox("This matter is already before a court or tribunal")
                payment_dispute = st.checkbox("This complaint disputes a payment or refund")
            with right:
                st.markdown("**Supporting documents (all optional)**")
                st.caption(agents.EVIDENCE[category])
                uploads = {kind: st.file_uploader(label, type=["pdf", "png", "jpg", "jpeg", "txt"], key=kind) for kind, label in [
                    ("Service evidence", "Service evidence / bill / application / incident record (optional)"),
                    ("CNIC", "CNIC copy (optional)"),
                    ("Payment proof", "Payment / fee receipt (optional)"),
                    ("Earlier complaint / decision", "Earlier complaint, acknowledgment or decision (optional)") ]}
                st.caption("Only upload relevant records. OCR assists extraction; document authenticity needs review.")
                st.caption("Preparation creates a PDF and copyable complaint text. You choose how to file with the authority afterwards.")
                days = st.number_input("Personal follow-up in days", min_value=1, max_value=365, value=14)
                consent = st.checkbox("Include this case in local aggregate analytics (category, province, date and demo status only)")
                st.caption("By selecting Prepare my grievance, you authorize processing the details and any optional files to create your draft.")
            run = st.form_submit_button("Prepare my grievance", type="primary")
        if run:
            st.session_state.pipeline = {stage: "Pending" for stage in agents.STAGES}
            st.session_state.current = None
            identity = None
            try:
                identity = validate_identity(cnic, cnic_expiry, mobile)
            except ValueError as exc:
                st.error(str(exc))
            if not text.strip() or not department_id:
                st.error("Enter your complaint and choose the department/provider.")
            elif identity is not None:
                files = {k: {"name": v.name, "bytes": v.getvalue()} if v else None for k, v in uploads.items()}
                case = agents.new_case(name, region, remedy, reference, days)
                case["identity"] = identity
                case["city"] = city
                case["attachments"] = [k for k, v in files.items() if v]
                with st.status("Preparing your grievance", expanded=True) as status:
                    try:
                        for stage in agents.STAGES:
                            st.session_state.pipeline[stage] = "Running"
                            st.write(stage)
                            if stage == agents.STAGES[0]:
                                case["intake"] = agents.intake(text, files)
                            elif stage == agents.STAGES[1]:
                                case["route"] = agents.route(text, category, st.session_state.manuals, region, department_id, complaint_stage, city, prior_reference, in_court, complaint_kind)
                            elif stage == agents.STAGES[2]:
                                case["audit"] = agents.audit(files, case["route"]["category"], complaint_stage, payment_dispute)
                            elif stage == agents.STAGES[3]:
                                case["pdf"] = agents.petition(case)
                            elif stage == agents.STAGES[4]:
                                case["dispatch"] = agents.dispatch(case)
                            else:
                                case["ics"] = agents.calendar(case)
                                if consent:
                                    save_aggregate(case)
                            st.session_state.pipeline[stage] = "Complete"
                        st.session_state.cases.append(case)
                        st.session_state.current = case
                        status.update(label="Draft and reminder ready", state="complete", expanded=False)
                    except Exception as exc:
                        st.session_state.pipeline[stage] = "Failed"
                        status.update(label="Preparation needs attention", state="error")
                        st.error(str(exc) if isinstance(exc, ValueError) else f"{stage} failed. Check dependencies or uploaded file format and retry.")
        if st.session_state.pipeline:
            for stage, state in st.session_state.pipeline.items():
                st.write(f"{'✅' if state == 'Complete' else '◻️'} {stage} — {state}")
        if st.session_state.current:
            case = st.session_state.current
            st.caption("Attachments are optional. Your draft can be prepared without uploads.")
            for warning in case["intake"]["warnings"]:
                st.warning(warning)
            with st.expander("Jurisdiction evidence"):
                st.write(case["route"]["guidance"])
                st.caption(case["route"]["backend"])
                for hit in case["route"]["matches"]:
                    st.write(f"{hit['name']} • relevance {hit['score']}")
                    st.text(hit["text"][:1500])
                    if hit.get("source"):
                        st.link_button("Official source: " + hit["name"], hit["source"])
    with output_tab:
        downloads(st.session_state.current)
elif page == "My drafts & filing records":
    st.subheader("Your session's grievances")
    st.caption("Local preparation records. Status is not synchronized with government systems. Session records disappear when the session ends.")
    if not st.session_state.cases:
        st.info("No cases prepared in this session yet.")
    else:
        selected = st.selectbox("Case", range(len(st.session_state.cases)), format_func=lambda i: "Draft " + st.session_state.cases[i]["id"][:12])
        downloads(st.session_state.cases[selected])
elif page == "Analytics & Heatmap":
    st.subheader("Community grievance overview")
    records = aggregates()
    if not records:
        st.info("No consented cases yet. Prepare a grievance and opt into aggregate analytics.")
    else:
        import pandas as pd
        df = pd.DataFrame(records)
        st.metric("Prepared cases", int(df["count"].sum()))
        a, b = st.columns(2)
        a.bar_chart(df.groupby("category")["count"].sum())
        b.bar_chart(df.groupby("status")["count"].sum())
        st.subheader("Province × service heatmap")
        matrix = df.pivot_table(index="region", columns="category", values="count", aggfunc="sum", fill_value=0)
        st.dataframe(matrix.style.background_gradient(cmap="YlGnBu"), use_container_width=True)
        st.caption("Coarse local aggregates of demo preparations; these are not official complaint statistics.")
elif page == "Department Directory":
    st.subheader("Departments and complaint routes")
    st.warning("This is a department directory, not a fully verified filing service. Provision-level research currently covers PEMRA broadcast-content complaints; an exact receiving office is verified here only for PEMRA Islamabad. Other entries require recipient and legal research.")
    st.caption(f"Directory review: {REVIEW_DATE}. A listed office is not a promise of admissibility. Local offices and statutory appeal routes may need verification.")
    region_filter = st.selectbox("Filter by province / territory", ["All", *REGIONS])
    category_filter = st.selectbox("Filter by service", ["All", *CATEGORIES])
    search = st.text_input("Search department, acronym or scope")
    for department in DEPARTMENTS.values():
        if region_filter != "All" and department.regions and region_filter not in department.regions:
            continue
        if category_filter != "All" and department.category != category_filter:
            continue
        if search and search.casefold() not in (department.name + " " + department.scope + " " + " ".join(department.aliases)).casefold():
            continue
        with st.expander(department.name):
            st.caption("PEMRA broadcast-content profile available; regional verification varies." if department.id == "pemra" else "Directory only: exact filing recipient and legal provisions not yet verified.")
            st.write(department.scope)
            st.caption("Regions: " + (", ".join(department.regions) or "Federal / nationwide"))
            st.write(department.caveat)
            if department.escalation:
                st.write("Possible escalation, subject to eligibility:", DEPARTMENTS[department.escalation].name)
            if department.review_required:
                st.warning("Local office / current operational channel requires confirmation.")
            st.link_button(department.channel, department.url)
else:
    st.subheader("Knowledge base workspace")
    st.caption("Session-local reference ingestion. This is a single-user demo, without administrator authentication. Manuals inform retrieval; they do not establish verified deadlines automatically.")
    category = st.selectbox("Manual jurisdiction", CATEGORIES)
    manual_region = st.selectbox("Manual applies in", ["All", *REGIONS])
    manual_department = st.selectbox("Manual department", [None] + [d.id for d in DEPARTMENTS.values() if d.category == category], format_func=lambda id: DEPARTMENTS[id].name if id else "Category-wide reference")
    manuals = st.file_uploader("Upload regulatory manuals", type=["pdf", "txt"], accept_multiple_files=True)
    if st.button("Index manuals") and manuals:
        for manual in manuals:
            try:
                text = agents.extract_document(manual.name, manual.getvalue())
                if not text.strip():
                    st.warning(f"{manual.name}: no text found. Use a searchable PDF or text file.")
                    continue
                chunks = [{"name": manual.name, "category": category, "department_id": manual_department, "region": () if manual_region == "All" else (manual_region,), "trusted": False, "text": text[i:i+1500]} for i in range(0, len(text), 1200)]
                st.session_state.manuals = [d for d in st.session_state.manuals if not (d["name"] == manual.name and d["category"] == category)] + chunks
                st.success(f"Indexed {manual.name}: {len(chunks)} chunks")
            except Exception:
                st.error(f"Could not read {manual.name}.")
    st.metric("Indexed reference chunks", len(st.session_state.manuals))
    if st.button("Clear session knowledge base"):
        st.session_state.manuals = []
        st.rerun()
