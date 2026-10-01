"""Run with: streamlit run app.py"""
import base64
import os
import streamlit as st
from grievance import agents
from grievance.knowledge import AUTHORITIES
from grievance.storage import aggregates, save_aggregate

st.set_page_config(page_title="Civic Access | Public Grievance", page_icon="⚖️", layout="wide")
for key, default in {"cases": [], "manuals": [], "pipeline": {}, "current": None}.items():
    st.session_state.setdefault(key, default)

st.sidebar.title("⚖️ Civic Access")
st.sidebar.caption("Pak Angels • Pakistan National Impact Challenge")
page = st.sidebar.radio("Workspace", ["Submit Grievance", "Live Tracker", "Analytics & Heatmap", "Knowledge Base Admin"])
st.sidebar.info("Demo workspace. Electronic dispatch is simulated. Private case details stay in this browser session; uploaded documents are not saved to disk.")
st.title("Public Grievance & Statutory Escalation Platform")
st.caption("A clearer path from a public service problem to a prepared complaint.")

def downloads(case):
    if not case:
        st.info("Prepare a grievance to see your petition and follow-up reminder.")
        return
    st.success(f"{case['route']['body']} • {case['dispatch']['tracking_id']} • {case['dispatch']['status']}")
    st.download_button("Download draft petition", case["pdf"], f"petition-{case['id'][:8]}.pdf", "application/pdf")
    st.download_button("Download calendar reminder", case["ics"], "follow-up.ics", "text/calendar")
    st.caption(f"Personal follow-up: {case['due'].date()}. Statutory deadline: not verified. Appellate forum: requires eligibility review.")
    with st.expander("Petition preview", expanded=True):
        encoded = base64.b64encode(case["pdf"]).decode()
        st.components.v1.html(f'<iframe title="Draft petition" src="data:application/pdf;base64,{encoded}" width="100%" height="650"></iframe>', height=660)
    st.subheader("Submission guidance")
    if case["route"]["portal"]:
        st.link_button("Open authority website / portal", case["route"]["portal"])
    for i, step in enumerate(case["dispatch"]["steps"], 1):
        st.write(f"{i}. {step}")
    st.caption("Local office addresses, maps and hours must be confirmed on the authority website before travel.")

if page == "Submit Grievance":
    intake_tab, output_tab = st.tabs(["Submit Grievance", "Petition & Downloads"])
    with intake_tab:
        st.subheader("Tell us what happened")
        mode = st.radio("Input method", ["Text", "Voice"], horizontal=True)
        if mode == "Voice":
            recording = st.audio_input("Record in Urdu or English")
            audio = st.file_uploader("Or upload audio", type=["wav", "mp3", "m4a"])
            source = recording or audio
            st.caption("Transcription uses OpenAI when configured. Offline mode accepts a typed transcript. Audio is sent only when you select Transcribe.")
            if source and st.button("Transcribe audio"):
                try:
                    st.session_state["narrative"] = agents.transcribe(source.getvalue(), source.name)
                except Exception as exc:
                    st.error(str(exc) if isinstance(exc, ValueError) else "Transcription failed. Check your API configuration or enter a transcript.")
        with st.form("grievance"):
            left, right = st.columns(2)
            with left:
                name = st.text_input("Applicant name (optional)", max_chars=120)
                region = st.selectbox("Province / territory", ["Punjab", "Sindh", "Khyber Pakhtunkhwa", "Balochistan", "Islamabad", "Gilgit-Baltistan", "Azad Jammu and Kashmir"])
                category = st.selectbox("Service category", ["Detect automatically", *AUTHORITIES])
                text = st.text_area("Complaint or transcript • English, Roman Urdu or Urdu", key="narrative", height=170, max_chars=12000)
                remedy = st.text_area("What resolution do you want?", value="Please investigate this complaint, correct the service issue, and provide a written response.", max_chars=3000)
                reference = st.text_input("Reference / consumer ID (optional)", max_chars=80)
            with right:
                st.markdown("**Supporting documents**")
                uploads = {kind: st.file_uploader(label, type=["pdf", "png", "jpg", "jpeg", "txt"], key=kind) for kind, label in [("CNIC", "CNIC copy"), ("Service evidence", "Bill or service evidence"), ("Payment proof", "Payment receipt") ]}
                st.caption("OCR requires Tesseract for images. Uploaded files count toward completeness, not authenticity.")
                dispatch_mode = st.selectbox("Submission pathway", ["Electronic (simulation)", "Offline guidance"])
                days = st.number_input("Personal follow-up in days", min_value=1, max_value=365, value=14)
                consent = st.checkbox("Include this case in local aggregate analytics (category, province, date and demo status only)")
                confirmed = st.checkbox("I authorize processing these documents to prepare my draft complaint")
            run = st.form_submit_button("Prepare my grievance", type="primary")
        if run:
            st.session_state.pipeline = {stage: "Pending" for stage in agents.STAGES}
            st.session_state.current = None
            if not text.strip() or not confirmed:
                st.error("Enter your complaint and authorize document processing.")
            else:
                files = {k: {"name": v.name, "bytes": v.getvalue()} if v else None for k, v in uploads.items()}
                case = agents.new_case(name, region, remedy, reference, days)
                case["attachments"] = [k for k, v in files.items() if v]
                with st.status("Preparing your grievance", expanded=True) as status:
                    try:
                        for stage in agents.STAGES:
                            st.session_state.pipeline[stage] = "Running"
                            st.write(stage)
                            if stage == agents.STAGES[0]:
                                case["intake"] = agents.intake(text, files)
                            elif stage == agents.STAGES[1]:
                                case["route"] = agents.route(text, category, st.session_state.manuals)
                            elif stage == agents.STAGES[2]:
                                case["audit"] = agents.audit(files, case["route"]["category"])
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
                st.warning("Missing documents: " + ", ".join(case["audit"]["missing"]))
            for warning in case["intake"]["warnings"]:
                st.warning(warning)
            with st.expander("Jurisdiction evidence"):
                st.write(case["route"]["guidance"])
                st.caption(case["route"]["backend"])
                for hit in case["route"]["matches"]:
                    st.write(f"{hit['name']} • relevance {hit['score']}")
                    st.text(hit["text"][:1500])
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
else:
    st.subheader("Knowledge base workspace")
    st.caption("Session-local reference ingestion. This is a single-user demo, without administrator authentication. Manuals inform retrieval; they do not establish verified deadlines automatically.")
    category = st.selectbox("Manual jurisdiction", list(AUTHORITIES))
    manuals = st.file_uploader("Upload regulatory manuals", type=["pdf", "txt"], accept_multiple_files=True)
    if st.button("Index manuals") and manuals:
        for manual in manuals:
            try:
                text = agents.extract_document(manual.name, manual.getvalue())
                if not text.strip():
                    st.warning(f"{manual.name}: no text found. Use a searchable PDF or text file.")
                    continue
                chunks = [{"name": manual.name, "category": category, "text": text[i:i+1500]} for i in range(0, len(text), 1200)]
                st.session_state.manuals = [d for d in st.session_state.manuals if not (d["name"] == manual.name and d["category"] == category)] + chunks
                st.success(f"Indexed {manual.name}: {len(chunks)} chunks")
            except Exception:
                st.error(f"Could not read {manual.name}.")
    st.metric("Indexed reference chunks", len(st.session_state.manuals))
    if st.button("Clear session knowledge base"):
        st.session_state.manuals = []
        st.rerun()
