# Civic Access — Public Grievance Platform

A Streamlit hackathon application based on the supplied Pak Angels pitch. Six modular stages prepare a complaint, retrieve jurisdiction references, assess attachments, generate a draft PDF, simulate dispatch or provide offline guidance, and create a calendar reminder.

## Run locally

Requires Python 3.11–3.13.

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m streamlit run app.py
```

No API key is needed for typed English/Roman Urdu complaints. Select a category, enter a complaint, authorize document processing, and select **Prepare my grievance**. The PDF and calendar appear under **Petition & Downloads**. Missing attachments are explicitly reported, but do not prevent generating a draft.

## Deploy on Streamlit Community Cloud

Deploy `ahmadsajjad-logix/public-grievance-platform`, branch `main`, entrypoint `app.py`. Select Python **3.13** in Advanced settings (the version tested locally). The root `requirements.txt` includes the speech engine, so no separate audio installation or OpenAI secret is required. A private GitHub repository needs to be accessible to your Streamlit account.

On the first transcription request, the server downloads the public `Systran/faster-whisper-base` model into `data/models/`. The model is shared across sessions in memory; recordings and transcripts are not shared. A restart may require downloading/loading it again. Download failure leaves the recording available for retry. Each request is limited to two minutes and 10 MB, and only one transcription runs at a time. Visitors are told when the server is busy. In hosted use, audio travels from the visitor's browser to the Streamlit server and is processed there in memory; it is not sent to an external transcription API.

The multilingual `base` model uses CPU INT8 to reduce memory consumption. Its Urdu accuracy can be limited, especially with noise or mixed speech; transcripts must be reviewed. On a larger host, set `WHISPER_MODEL_SIZE=small` before startup for the larger model. No resource allocation or transcription latency is guaranteed on shared hosting. Verify a representative Urdu recording on the actual deployment before the hackathon.

Community Cloud's local disk is ephemeral. The SQLite analytics database may be lost after restart/redeployment; use a hosted database before relying on durable records.

## Integrations

- Audio: the Voice screen uses multilingual Whisper on the app server's CPU. No API key or API billing is needed. The speech engine is installed by the main requirements. To pre-download the model locally (optional):

  ```powershell
  .\.venv\Scripts\python scripts/setup_audio.py
  ```

  First use needs internet access to download model weights into `data/models/` (excluded from Git). Once downloaded, transcription can work offline on that server. Choose **Voice → Urdu → Transcribe audio**. Recordings are processed in memory, retained only for the session, and can be downloaded with **Save my recording**. The optional `agents.transcribe` OpenAI adapter remains available to developers but is not called by the Voice screen.
- Image OCR: install Tesseract separately and put it on PATH. Missing OCR produces a manual-review message, not fabricated extraction. Searchable PDFs use pypdf. OCR defaults to English.
- Urdu PDF: bundled OFL-licensed Noto fonts, Arabic shaping and right-to-left line layout support Urdu and mixed English text without font configuration. Review the generated draft before submission.
- Knowledge base: upload searchable PDF/text manuals and associate their jurisdiction. FAISS indexes normalized hashed lexical features; NumPy or keyword retrieval provides an offline fallback. This does not claim semantic embeddings or legally verified interpretations.

## Data and operating limits

Names, narratives and supporting documents remain in Streamlit session memory and are not written to disk. With explicit consent, SQLite stores a random case identifier, day, category, province and demo dispatch status. Analytics receives grouped counts only. Session case records are lost when the session ends; database aggregates survive restarts. Do not expose this single-user prototype publicly with sensitive documents.

Electronic submissions are **simulated**, never sent to an authority. Reminder dates are user-selected, not statutory deadlines. No automatic appeal or escalation is filed. Exact legal sections, provincial applicability, appellate forums, deadlines, office addresses and hours require source verification and review. Retrieved manuals are shown as evidence rather than injected as unverified statutory clauses. Government links are provided for manual submission.

Before production: add authentication and administrator authorization, secure retention/deletion controls, independently validated multilingual OCR/PDF rendering, legally reviewed jurisdiction rules, verified deadline metadata, contracted dispatch integrations, durable private case storage and status reconciliation. This implementation is a working demo foundation, not a production certification.

## Verification

The department directory covers federal regulators, electricity and gas providers, provincial service departments, ombudsmen and public-service-delay routes. Select the actual provider and province; local entries require the district/office. Unresolved complaints can suggest an eligible escalation forum. Court matters and formal decisions require individual review. Directory links are distinguished from complaint portals, and unverified operational routes are labelled in the app.

```powershell
.\.venv\Scripts\python -m pytest -q
```

## GitHub

The repository ignores keys, virtual environments and the local analytics database. Review files and create a GitHub repository, then set its remote and push. Publishing requires a chosen account/repository and working GitHub authentication; no remote is assumed.

## Official reference links

- NEPRA: https://nepra.org.pk/CAD-Database/CMS-CAD/home.php
- PTA manual: https://complaint.pta.gov.pk/Usermanual/User_Manual_CMS_Web.pdf
- Wafaqi Mohtasib: https://complaints.mohtasib.gov.pk/
