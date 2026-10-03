# Civic Access — Public Grievance Platform

A Streamlit application with six specialist workflow modules: Intake & OCR, Jurisdiction RAG, Audit Readiness, Petition Builder, Dispatch & Router, and Tracker & Analytics. These are explicit Python workflow stages, not six autonomous LLMs. The current dispatch stage provides filing guidance and external channels; it does not submit complaints.

## Run locally

Requires Python 3.11–3.13.

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m streamlit run app.py
```

No API key is needed. Type your complaint in Urdu, Roman Urdu or English and confirm the department. CNIC number, CNIC expiry date and Pakistani mobile number are required identity fields. Name, location, reference details and all uploads are optional. Identity fields are checked for format only, without NADRA or phone-owner verification. They appear in the draft PDF and stay in session memory, outside aggregate analytics.

Audio input has been withdrawn because Urdu transcription accuracy was insufficient. The archived speech module is not used by the app and no speech model downloads occur in the deployed workflow.

## Deploy on Streamlit Community Cloud

Deploy `ahmadsajjad-logix/public-grievance-platform`, branch `main`, entrypoint `app.py`, with Python **3.13**. No API secrets are needed. The live app is https://public-grievance-platform.streamlit.app/.

Bundled Noto fonts provide Urdu PDF shaping; PDF previews render directly as images. OCR uses Tesseract, installed by `packages.txt` on Cloud. All attachments are optional. A missing local office or earlier reference produces review guidance without blocking the draft. An unresolved complaint without an earlier reference stays addressed to the selected office pending review.

Community Cloud's local disk is ephemeral; analytics may be lost after a redeployment. Case details remain session-local.

## Data and operating limits

### Filing coverage (2026-10-03)

All 71 directory entries now have source-linked framework and filing guidance, plus the supplied departmental reference library. This is **not 71 fully verified legal filing routes**: broad provincial categories still require the actual provider/district, some references cover institutional powers rather than a complaint-specific entitlement, and some electronic endpoints or court filing details remain unverified. Guides explain ambit, exclusions, filing steps, documented channels and preparation. The exact regional receiving officer is verified only for PEMRA Islamabad; other office details and provision-level coverage vary.

Each department guide prominently presents its official complaint form or portal before petition preparation, without requiring identity details in this app. Forms, sign-in portals, WhatsApp contacts, complaint instructions and office directories have separate labels. General government portals are identified as administrative routes; they are not substitutes for judicial or statutory appeals. City-specific routes such as KWSC and private-school-only routes such as PEPRIS state their scope. Opening a link sends no case data and does not file a complaint.

## Offence screening and official form assistance

The FIR & Offence Guide contains 13 common incident scenarios with English/Urdu labels, source-linked PPC/PECA provisions, fact questions, distinctions from civil disputes, evidence preparation and downloadable text guidance. Answers default to Not sure. Negative or missing elements are not treated as supported charges. AJK/GB territorial application is flagged separately. CrPC 154/155 and the locally applicable 22-A route explain procedure, separately from substantive offences. The app does not determine guilt, guarantee FIR registration, infer cognizability for every offence, or cover every criminal/special/provincial law. Incident-date amendments and legal review remain necessary.

NCCIA, NEPRA and KWSC have source-reviewed public form field guides, with copyable prepared content where applicable. Other entries show explicitly generic preparation help. Portal fields and requirements can change. No browser automation, external autofill, credential handling, CAPTCHA bypass or automatic submission is implemented. Identity and declarations are completed on the receiving site; its requirements can exceed this app's optional fields. Legal framework and available rights/remedies appear before filing steps in the department guide and its downloads.

The user-supplied Hugging Face link was inspected: AyeshaJadoon/Pakistan_Laws_Dataset is an ODC-BY legal text dataset, not a hosted LLM. The downloaded file contains 967 records (card says 969), with `file_name` and `text` keys. Its PECA record is older than the official 39-page consolidation reviewed for this feature. `data/huggingface_source_review.json` records provenance and the decision to use it for research discovery only; the 46.9 MB raw download remains ignored locally. The linked Phi-3 LoRA adapter requires a base model and has no listed hosted inference provider. Neither dataset text nor model output is automatically promoted into current legal advice.

Agent 02 retrieves both reviewed summaries and page-cited local documents through FAISS hashed lexical vectors (NumPy fallback). This is lexical retrieval, not semantic multilingual understanding. Department selection, region and stage constrain retrieval; conflicting or ambiguous jurisdiction needs user confirmation. Unreviewed source text never automatically becomes a petition clause.

Run `python -m scripts.research_sources` to perform bounded discovery from every directory entry's official starting URL. `data/source_access_report.json` records access outcomes; downloaded candidates stay local and require review. The initial pass produced 109 access results across 46 seed URLs: 92 successful fetches and 17 failures, including duplicate page visits. Retrieval success is not legal verification. Research runs during knowledge-base maintenance, not during every citizen request.

Run `python -m scripts.index_department_documents` to rebuild `data/department_documents.json` from `Relevant Departmental Downloads`. The 18 PDFs produce page-cited chunks with hashes, scope and version warnings. Image-only pages are recorded as requiring OCR. A visually reviewed PTA poster summary is included. Historical tariff/standards documents and FIA/banking material outside current routing scope are not automatically routed. The original user folder is not committed; the extracted reference corpus is bundled for Cloud.

The supplied Punjab RTS filename says 2018 but the Act text says 2019. The KP amendment file concerns commission appointments rather than service notifications. The OGRA regulation and portal disagree on the 90-day starting event, so the guide flags the conflict. The revised 2025 Consumer Service Manual supports specific electricity procedure citations; no old tariff is assumed current.

PEMRA profiles distinguish filing procedure (Ordinance section 26(2), Council Rules 8(1), 11(1)/(3), PEMRA Rules 18 and 15(1)) from potential substantive grounds (section 20(b)/Code 3(1)(a) for stated cultural/religious concerns; section 20(c)/Code 3(1)(e) for stated decency concerns). Sources accompany each provision in the PDF. Keyword matching does not establish a legal breach. Cable service, employee wages and statutory appeals do not reuse the broadcast-content provisions. Programme dates, scenes and viewing location need factual review. Optional uploads remain optional.

Sources: https://www.pemra.gov.pk/coc/ ; https://www.pemra.gov.pk/isb/ ; https://www.pemra.gov.pk/assets/uploads/legal/coc_rules_2010.pdf ; https://pemra.gov.pk/assets/uploads/legal/Ordinance_2002.pdf ; https://pemra.gov.pk/assets/uploads/legal/Code_of_Conduct.pdf ; https://www.pemra.gov.pk/assets/uploads/legal/PEMRA_Rules_2009.pdf . The 2023 amendment is reflected in PEMRA's current Council guidance; old fine limits and generic deadlines are not generated.

Names, narratives and supporting documents remain in Streamlit session memory and are not written to disk. With explicit consent, SQLite stores a random case identifier, day, category, province and demo dispatch status. Analytics receives grouped counts only. Session case records are lost when the session ends; database aggregates survive restarts. Do not expose this single-user prototype publicly with sensitive documents.

Electronic simulation has been removed. Users receive a petition, copyable complaint and downloadable department/filing guide. Links open an external channel without transferring case data. Official acknowledgment references are user-reported session records, not live government tracking. Reminder dates remain user-selected, not statutory deadlines; unsupported statutory date calculations are not generated. No automatic appeal or escalation is filed. WhatsApp numbers are shown only where source-reviewed. Office maps are address searches, not confirmed geocoded entrances; hours remain unknown unless sourced.

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
