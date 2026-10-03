"""Six explicit workflow stages with offline-safe fallbacks."""
import io
import os
import re
import uuid
from datetime import datetime, timedelta, timezone
from .knowledge import route

STAGES = ["Agent 01 · Intake & OCR", "Agent 02 · Jurisdiction RAG", "Agent 03 · Audit Readiness", "Agent 04 · Petition Builder", "Agent 05 · Dispatch & Router", "Agent 06 · Tracker & Analytics"]

def extract_document(name, content):
    if name.lower().endswith(".pdf"):
        from pypdf import PdfReader
        return "\n".join(page.extract_text() or "" for page in PdfReader(io.BytesIO(content)).pages[:30])
    if name.lower().endswith(".txt"):
        return content.decode("utf-8", errors="replace")
    from PIL import Image
    import pytesseract
    return pytesseract.image_to_string(Image.open(io.BytesIO(content)), lang="eng")

def intake(text, files):
    extracted, warnings = [], []
    for kind, file in files.items():
        if file:
            try:
                value = extract_document(file["name"], file["bytes"])
                extracted.append(value)
                if not value.strip():
                    warnings.append(f"{kind}: no text extracted; review the document manually.")
            except Exception:
                warnings.append(f"{kind}: OCR unavailable or file unreadable; enter reference details manually.")
    combined = text + "\n" + "\n".join(extracted)
    refs = re.findall(r"(?:reference|consumer\s*id|account)\s*(?:no\.?|number)?\s*[:#-]?\s*(\d[\d -]{5,24})", combined, re.I)
    dates = re.findall(r"\b\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}\b", combined)
    return {"text": text.strip(), "references": refs, "dates": dates, "warnings": warnings}

def transcribe(content, name):
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("Audio transcription needs OPENAI_API_KEY. Enter your transcript in the text box to continue offline.")
    from openai import OpenAI
    return OpenAI(timeout=45, max_retries=1).audio.transcriptions.create(
        model=os.getenv("TRANSCRIPTION_MODEL", "whisper-1"), file=(name, content)).text

EVIDENCE = {
    "Electricity": "Bill, meter/reference number, outage dates or connection application",
    "Gas & petroleum": "Gas bill/application or fuel receipt, supplier and issue dates",
    "Telecom": "Operator ticket, disputed bill/SIM details, spam screenshots",
    "Broadcasting": "Channel/operator, programme, date, time and relevant clip reference",
    "Federal administration": "Application, acknowledgment and agency correspondence",
    "Tax administration": "Refund/tax reference, correspondence and relevant order",
    "Cybercrime": "Original messages, URLs, transaction IDs and dated screenshots",
    "Municipal & sanitation": "Dated photos and exact street/landmark",
    "Water & sewerage": "Consumer reference if applicable, photos and exact location",
    "Police & public safety": "Station, incident date, application/diary/FIR reference",
    "Traffic & safe cities": "Location/time and challan or incident reference",
    "Food safety": "Shop address, receipt, batch/expiry details and photos",
    "Consumer rights & pricing": "Receipt, product/service details, rate list or warranty",
    "Revenue & land": "Property/khasra details, application and revenue-office receipt",
    "Health": "Facility, dates, service record and earlier complaint (if available)",
    "Education": "School, dates, fee receipts or earlier written complaint",
    "Public service delays": "Complete service application, acknowledgment date and notified-service details",
    "Provincial maladministration": "Department application, earlier complaint and response",
}


def audit(files, category, stage="First complaint", payment_dispute=False):
    required = ["Service evidence"]
    if category in ("Federal administration", "Tax administration", "Provincial maladministration", "Public service delays"):
        required.append("CNIC")
    if stage != "First complaint":
        required.append("Earlier complaint / decision")
    if payment_dispute:
        required.append("Payment proof")
    present = [k for k in required if files.get(k) and files[k]["bytes"]]
    return {"score": round(100 * len(present) / len(required)), "missing": [k for k in required if k not in present],
            "recommended": required, "evidence_hint": EVIDENCE[category],
            "note": "Preparation checklist only. The receiving authority may require different documents; file presence does not establish authenticity."}


def petition(case):
    from .petitions import build_petition
    return build_petition(case)


def dispatch(case, mode=None):
    # Legacy callers may pass a mode; preparation never constitutes dispatch.
    return {"status": "Draft prepared - not submitted",
            "tracking_id": "DRAFT-" + case["id"][:12],
            "steps": ["Review and sign the petition; confirm authority eligibility.",
                      "Use the official website to confirm the nearest office, address and current opening hours.",
                      "Submit through the official portal or bring copies to the confirmed office.",
                      "Keep the official acknowledgment and tracking number. This app has not submitted anything."]}


def filing_text(case):
    """Portal-ready narrative without duplicating identity fields or inventing facts."""
    route = case["route"]
    parts = ["Statement of complaint", case["intake"]["text"],
             "Requested resolution", case["remedy"]]
    if case.get("reference"):
        parts.extend(["Service / application reference", case["reference"]])
    if route.get("prior_reference"):
        parts.extend(["Earlier complaint / decision", route["prior_reference"]])
    if route.get("legal_provisions"):
        parts.append("Legal provisions for consideration (subject to facts and applicability)")
        parts.extend(f"{p['citation']}: {p['purpose']} Source: {p['source']}"
                     for p in route["legal_provisions"])
    return "\n\n".join(parts)

def calendar(case):
    due = case["due"].date()
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Civic Access//Grievance Reminder//EN", "BEGIN:VEVENT",
             f"UID:{case['id']}@civic-access.local", "DTSTAMP:" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
             "DTSTART;VALUE=DATE:" + due.strftime("%Y%m%d"), "DTEND;VALUE=DATE:" + (due + timedelta(days=1)).strftime("%Y%m%d"),
             "SUMMARY:Grievance follow-up reminder", "DESCRIPTION:Personal reminder. No verified statutory deadline or automatic escalation.",
             "END:VEVENT", "END:VCALENDAR", ""]
    return "\r\n".join(lines).encode()

def new_case(name, region, remedy, reference, followup_days):
    now = datetime.now(timezone(timedelta(hours=5)))
    return {"id": uuid.uuid4().hex, "created": now, "due": now + timedelta(days=followup_days),
            "name": name, "region": region, "remedy": remedy, "reference": reference}
