"""Run with: streamlit run app.py"""
import base64
import logging
import streamlit as st
from grievance import agents
from grievance.speech import readiness, transcribe_local
from grievance.knowledge import detect
from grievance.catalog import CATEGORIES, DEPARTMENTS, REGIONS, STAGES, available_departments, REVIEW_DATE
from grievance.storage import aggregates, save_aggregate

st.set_page_config(page_title="Civic Access | Public Grievance", page_icon="⚖️", layout="wide")
for key, default in {"cases": [], "manuals": [], "pipeline": {}, "current": None}.items():
    st.session_state.setdefault(key, default)

st.sidebar.title("⚖️ Civic Access")
st.sidebar.caption("Pak Angels • Pakistan National Impact Challenge")
page = st.sidebar.radio("Workspace", ["Submit Grievance", "Live Tracker", "Analytics & Heatmap", "Department Directory", "Knowledge Base Admin"])
st.sidebar.info("Demo workspace. Electronic dispatch is simulated. Private case details stay in this session on the app server; uploaded documents are not saved to disk.")
st.title("Public Grievance & Statutory Escalation Platform")
st.caption("A clearer path from a public service problem to a prepared complaint.")

def downloads(case):
    if not case:
        st.info("Prepare a grievance to see your petition and follow-up reminder.")
        return
    st.success(f"{case['route']['body']} • {case['dispatch']['tracking_id']} • {case['dispatch']['status']}")
    st.download_button("Download draft petition", case["pdf"], f"petition-{case['id'][:8]}.pdf", "application/pdf")
    st.download_button("Download calendar reminder", case["ics"], "follow-up.ics", "text/calendar")
    st.caption(f"Personal follow-up: {case['due'].date()}. This is not a statutory or appeal deadline.")
    st.write("Complaint concerns:", case["route"].get("department", case["route"]["body"]))
    st.write("Suggested next forum:", case["route"].get("escalation", "Review required"))
    for note in case["route"].get("notes", []):
        st.info(note)
    st.download_button("Download complaint text (Urdu supported)", case["intake"]["text"].encode("utf-8-sig"), "complaint.txt", "text/plain")
    with st.expander("Petition preview", expanded=True):
        encoded = base64.b64encode(case["pdf"]).decode()
        st.components.v1.html(f'<iframe title="Draft petition" src="data:application/pdf;base64,{encoded}" width="100%" height="650"></iframe>', height=660)
    st.subheader("Submission guidance")
    if case["route"]["portal"]:
        st.link_button(case["route"].get("channel", "Open authority website / portal"), case["route"]["portal"])
    for i, step in enumerate(case["dispatch"]["steps"], 1):
        st.write(f"{i}. {step}")
    st.caption("Local office addresses, maps and hours must be confirmed on the authority website before travel.")

if page == "Submit Grievance":
    intake_tab, output_tab = st.tabs(["Submit Grievance", "Petition & Downloads"])
    with intake_tab:
        st.subheader("Tell us what happened")
        region = st.selectbox("Province / territory of the complaint", REGIONS, key="region")
        mode = st.radio("Input method", ["Text", "Voice"], horizontal=True)
        if mode == "Voice":
            ready, speech_status = readiness()
            if ready:
                st.success(speech_status)
            else:
                st.warning(speech_status)
            language = st.selectbox("Recording language", ["Urdu", "English", "Detect automatically"])
            recording = st.audio_input("Record in Urdu or English")
            audio = st.file_uploader("Or upload audio", type=["wav", "mp3", "m4a"])
            source = recording or audio
            if source:
                # Retain the recording across reruns/settings changes in this session.
                st.session_state["pending_recording"] = {"bytes": source.getvalue(), "name": source.name}
            pending = st.session_state.get("pending_recording")
            st.caption("Audio is processed on the server running this app. No OpenAI account is needed. Keep recordings under 2 minutes / 10 MB. The first request downloads the speech model and may take a few minutes.")
            if pending:
                st.audio(pending["bytes"])
                st.download_button("Save my recording", pending["bytes"], pending["name"], key="save_recording")
                if not source:
                    st.caption("Using the recording retained from this session.")
            if st.button("Transcribe audio", disabled=not ready or not pending):
                try:
                    with st.spinner("Preparing the speech model and transcribing… The first request may take a few minutes."):
                        transcript = transcribe_local(pending["bytes"], {"Urdu": "ur", "English": "en", "Detect automatically": None}[language])
                    st.session_state["narrative"] = transcript
                    st.success("Transcription is ready in the complaint box below. Please review it for accuracy.")
                except Exception as exc:
                    if not isinstance(exc, ValueError):
                        logging.getLogger(__name__).exception("Speech transcription failed")
                    st.error(str(exc) if isinstance(exc, ValueError) else "Transcription could not finish. Try a shorter WAV or MP3 recording. If it keeps failing, ask the app owner to check the server logs. Your recording has been retained.")
        text = st.text_area("Complaint or transcript • English, Roman Urdu or Urdu", key="narrative", height=170, max_chars=12000)
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
        complaint_stage = st.selectbox("Complaint stage", STAGES)
        st.caption("First complaint goes to the selected office. An unresolved complaint may go to its regulator or eligible ombudsman. A formal appeal requires review of the decision and law.")
        with st.form("grievance"):
            left, right = st.columns(2)
            with left:
                name = st.text_input("Applicant name (optional)", max_chars=120)
                city = st.text_input("City / district and exact office or facility", max_chars=240)
                remedy = st.text_area("What resolution do you want?", value="Please investigate this complaint, correct the service issue, and provide a written response.", max_chars=3000)
                reference = st.text_input("Service / consumer / application reference (optional)", max_chars=100)
                prior_reference = st.text_input("Earlier complaint or decision reference / date", max_chars=160)
                in_court = st.checkbox("This matter is already before a court or tribunal")
                payment_dispute = st.checkbox("This complaint disputes a payment or refund")
            with right:
                st.markdown("**Supporting documents**")
                st.caption(agents.EVIDENCE[category])
                uploads = {kind: st.file_uploader(label, type=["pdf", "png", "jpg", "jpeg", "txt"], key=kind) for kind, label in [
                    ("Service evidence", "Service evidence / bill / application / incident record"),
                    ("CNIC", "CNIC copy (if the receiving authority requires it)"),
                    ("Payment proof", "Payment / fee receipt (if relevant)"),
                    ("Earlier complaint / decision", "Earlier complaint, acknowledgment or decision") ]}
                st.caption("Only upload relevant records. OCR assists extraction; document authenticity needs review.")
                dispatch_mode = st.selectbox("Submission pathway", ["Offline guidance", "Electronic (simulation)"])
                days = st.number_input("Personal follow-up in days", min_value=1, max_value=365, value=14)
                consent = st.checkbox("Include this case in local aggregate analytics (category, province, date and demo status only)")
                confirmed = st.checkbox("I authorize processing these documents to prepare my draft complaint")
            run = st.form_submit_button("Prepare my grievance", type="primary")
        if run:
            st.session_state.pipeline = {stage: "Pending" for stage in agents.STAGES}
            st.session_state.current = None
            if not text.strip() or not confirmed or not department_id:
                st.error("Enter your complaint, choose the department/provider, and authorize document processing.")
            else:
                files = {k: {"name": v.name, "bytes": v.getvalue()} if v else None for k, v in uploads.items()}
                case = agents.new_case(name, region, remedy, reference, days)
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
                                case["route"] = agents.route(text, category, st.session_state.manuals, region, department_id, complaint_stage, city, prior_reference, in_court)
                            elif stage == agents.STAGES[2]:
                                case["audit"] = agents.audit(files, case["route"]["category"], complaint_stage, payment_dispute)
                            elif stage == agents.STAGES[3]:
                                case["pdf"] = agents.petition(case)
                            elif stage == agents.STAGES[4]:
                                case["dispatch"] = agents.dispatch(case, dispatch_mode)
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
            st.metric("Attachment readiness", f"{case['audit']['score']}%")
            st.caption(case["audit"]["note"])
            if case["audit"]["missing"]:
                st.warning("Suggested supporting documents still missing: " + ", ".join(case["audit"]["missing"]))
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
elif page == "Live Tracker":
    st.subheader("Your session's grievances")
    st.caption("Local preparation records. Status is not synchronized with government systems. Session records disappear when the session ends.")
    if not st.session_state.cases:
        st.info("No cases prepared in this session yet.")
    else:
        selected = st.selectbox("Case", range(len(st.session_state.cases)), format_func=lambda i: st.session_state.cases[i]["dispatch"]["tracking_id"])
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
