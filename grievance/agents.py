"""Six explicit workflow stages with offline-safe fallbacks."""
import io
import os
import re
import uuid
from datetime import datetime, timedelta, timezone
from html import escape
from .knowledge import route

STAGES = ["Intake & OCR", "Jurisdiction RAG", "Audit Readiness", "Petition Builder", "Dispatch & Router", "Tracker & Analytics"]

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

def audit(files, category):
    required = ["CNIC", "Service evidence"]
    if category == "Electricity":
        required.append("Payment proof")
    present = [k for k in required if files.get(k) and files[k]["bytes"]]
    return {"score": round(100 * len(present) / len(required)), "missing": [k for k in required if k not in present],
            "note": "Attachment completeness only; authenticity and legal sufficiency require review."}

def petition(case):
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    buf = io.BytesIO()
    styles = getSampleStyleSheet()
    font_path = os.getenv("PETITION_FONT_PATH")
    if font_path:
        pdfmetrics.registerFont(TTFont("PetitionUnicode", font_path))
        for style in styles.byName.values():
            style.fontName = "PetitionUnicode"
    narrative = case["intake"]["text"]
    if any(ord(c) > 127 for c in narrative) and not font_path:
        raise ValueError("For an Urdu PDF, configure PETITION_FONT_PATH or provide an English/Roman Urdu petition transcript. Original text is retained in the intake box.")
    sections = [
        ("Title", "DRAFT — Public service grievance"),
        ("Normal", f"To: {case['route']['body']} | Date: {case['created'].date()}"),
        ("Normal", f"Applicant: {case['name'] or 'Name to be supplied'} | Province/territory: {case['region']}"),
        ("Heading2", "Statement of grievance"), ("Normal", narrative),
        ("Heading2", "Requested remedy"), ("Normal", case["remedy"]),
        ("Heading2", "Service reference"), ("Normal", case["reference"] or ", ".join(case["intake"]["references"]) or "To be supplied"),
        ("Heading2", "Procedural reference"), ("Normal", case["route"]["guidance"]),
        ("Normal", f"Source for review: {case['route']['source'] or 'Local authority rules must be supplied'}"),
        ("Normal", "No statutory section or binding deadline has been verified for this case. The calendar date is a personal follow-up reminder."),
        ("Heading2", "Attachments and declaration"),
        ("Normal", "Attached: " + (", ".join(case["attachments"]) or "None")),
        ("Normal", "I confirm that the facts and supporting documents are accurate to the best of my knowledge. Signature: ____________________"),
    ]
    flow = []
    for style, value in sections:
        flow.extend([Paragraph(escape(value).replace("\n", "<br/>"), styles[style]), Spacer(1, 10)])
    SimpleDocTemplate(buf, title="Draft grievance petition").build(flow)
    return buf.getvalue()

def dispatch(case, mode):
    return {"status": "Demo dispatch" if mode == "Electronic (simulation)" else "Ready for offline submission",
            "tracking_id": "DEMO-" + case["id"][:12] if mode == "Electronic (simulation)" else "LOCAL-" + case["id"][:12],
            "steps": ["Review and sign the petition; confirm authority eligibility.",
                      "Use the official website to confirm the nearest office, address and current opening hours.",
                      "Submit through the official portal or bring copies to the confirmed office.",
                      "Keep the official acknowledgment and tracking number. This app has not submitted anything."]}

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
