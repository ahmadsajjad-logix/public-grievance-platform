# Civic Access — Public Grievance Platform

A Streamlit hackathon application based on the supplied Pak Angels pitch. Six modular stages prepare a complaint, retrieve jurisdiction references, assess attachments, generate a draft PDF, simulate dispatch or provide offline guidance, and create a calendar reminder.

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

The 71 entries are directory coverage, **not 71 verified legal filing routes**. Provision-level research currently covers PEMRA programme/advertisement content complaints. The exact receiving office is verified only for PEMRA Islamabad: Regional Director / Secretary, Council of Complaints, 3rd Floor, PEMRA Headquarters, G-8/1, Mauve Area, Islamabad. Other PEMRA regions and all other departments require individual recipient and jurisdiction verification.

PEMRA profiles distinguish filing procedure (Ordinance section 26(2), Council Rules 8(1), 11(1)/(3), PEMRA Rules 18 and 15(1)) from potential substantive grounds (section 20(b)/Code 3(1)(a) for stated cultural/religious concerns; section 20(c)/Code 3(1)(e) for stated decency concerns). Sources accompany each provision in the PDF. Keyword matching does not establish a legal breach. Cable service, employee wages and statutory appeals do not reuse the broadcast-content provisions. Programme dates, scenes and viewing location need factual review. Optional uploads remain optional.

Sources: https://www.pemra.gov.pk/coc/ ; https://www.pemra.gov.pk/isb/ ; https://www.pemra.gov.pk/assets/uploads/legal/coc_rules_2010.pdf ; https://pemra.gov.pk/assets/uploads/legal/Ordinance_2002.pdf ; https://pemra.gov.pk/assets/uploads/legal/Code_of_Conduct.pdf ; https://www.pemra.gov.pk/assets/uploads/legal/PEMRA_Rules_2009.pdf . The 2023 amendment is reflected in PEMRA's current Council guidance; old fine limits and generic deadlines are not generated.

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
