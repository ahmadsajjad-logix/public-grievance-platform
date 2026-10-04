"""Local retrieval: hashed multilingual features, FAISS when available.

This is lexical retrieval, not a pretrained semantic embedding model.
Uploaded manuals are reference material, never executable instructions.
"""
import hashlib
import re
import unicodedata
from .catalog import CATEGORIES, DEPARTMENTS, STAGES, available_departments, starter_documents, REVIEW_DATE
from .pemra import is_pemra, council_id

AUTHORITIES = {
    "Electricity": ("NEPRA", "https://nepra.org.pk/CAD-Database/CMS-CAD/home.php", "NEPRA Complaint Handling & Dispute Resolution Procedure Rules, 2015", "https://nepra.org.pk/"),
    "Telecom": ("PTA", "https://complaint.pta.gov.pk/userlogin.aspx", "PTA complaint management guidance", "https://complaint.pta.gov.pk/Usermanual/User_Manual_CMS_Web.pdf"),
    "Electronic Media (Radio, TV, Cable TV, etc.)": ("PEMRA", "https://pemra.gov.pk/", "Consult current PEMRA complaint guidance", "https://pemra.gov.pk/"),
    "Federal administration": ("Wafaqi Mohtasib", "https://complaints.mohtasib.gov.pk/", "Federal ombudsman jurisdiction requires eligibility review", "https://www.mohtasib.gov.pk/"),
    "Municipal services": ("Local municipal authority", "", "Local jurisdiction and provincial service rules require verification", ""),
}
KEYWORDS = {
    "Banking": "bank|banking|bank account|atm|debit card|credit card|remittance|microfinance|jazzcash|easypaisa|upaisa|بینک|بینک اکاؤنٹ|اے ٹی ایم|ایزی پیسہ|جاز کیش",
    "Electricity": "electricity|electric|load shedding|loadshedding|bijli|wapda|بجلی|لوڈ شیڈنگ",
    "Gas & petroleum": "gas|petrol|petroleum|lpg|cng|گیس|پٹرول",
    "Telecom": "telecom|internet|mobile network|sim|spam|انٹرنیٹ|سم|اسپیم",
    "Electronic Media (Radio, TV, Cable TV, etc.)": "broadcast|television|tv channel|cable|drama|drama serial|نشریات|کیبل|ٹی وی|ڈرامہ",
    "Federal administration": "federal|pension|passport|nadra|وفاقی|پنشن|پاسپورٹ|نادرا",
    "Tax administration": "tax refund|income tax|customs|fbr|tax|ٹیکس|کسٹمز",
    "Cybercrime": "cybercrime|hacking|hacked|online harassment|online fraud|identity theft|blackmail|فراڈ|ہیک|بلیک میل|آن لائن ہراسانی",
    "Municipal & sanitation": "garbage|kachra|sanitation|manhole|street light|کچرا|کوڑا|صفائی|مین ہول",
    "Water & sewerage": "water|sewer|sewage|pani|gutter|پانی|سیوریج|گٹر",
    "Police & public safety": "police|fir|thana|پولیس|تھانہ|ایف آئی آر",
    "Traffic & safe cities": "traffic|parking|signal|safe city|ٹریفک|پارکنگ|چالان",
    "Food safety": "food|adulterated|expired|restaurant|milawat|کھانا|ملاوٹ|ریسٹورنٹ|زائد المیعاد",
    "Consumer rights & pricing": "consumer|overpricing|rate list|defective|refund product|صارف|مہنگا|ناقص سامان",
    "Revenue & land": "land|fard|patwari|tehsildar|encroachment|housing scheme|zameen|زمین|فرد|پٹواری|تجاوزات",
    "Health": "hospital|doctor|medicine|sehat|ہسپتال|اسپتال|ڈاکٹر|دوائی|ادویات",
    "Education": "school|teacher|school fees|taleem|سکول|اسکول|استاد|تعلیم",
    "Public service delays": "domicile|birth certificate|driving license|rts|ڈومیسائل|پیدائش کا سرٹیفکیٹ|ڈرائیونگ لائسنس",
    "Provincial maladministration": "provincial ombudsman|subai mohtasib|صوبائی محتسب",
}


def normalize(text):
    text = unicodedata.normalize("NFKC", text).casefold().translate(str.maketrans({"ي": "ی", "ك": "ک", "ى": "ی", "أ": "ا", "إ": "ا"}))
    return " ".join(re.findall(r"\w+", text))


def contains(text, phrase):
    return f" {normalize(phrase)} " in f" {normalize(text)} "


def detect(text, region):
    """Return candidates instead of silently choosing between competing scopes."""
    named = [d for d in DEPARTMENTS.values() if any(contains(text, a) for a in d.aliases)]
    # Brand names can appear in wallet complaints; never send money disputes to PTA.
    if any(contains(text, word) for word in ("jazzcash", "jazz cash", "easypaisa", "easy paisa", "upaisa", "جاز کیش", "ایزی پیسہ")):
        return "Banking", None
    categories = list(dict.fromkeys(d.category for d in named))
    if len(categories) == 1:
        selected = named[0].id if len(named) == 1 else None
        if selected == "pemra":
            selected = council_id(region) or selected
        return categories[0], selected
    if len(categories) > 1:
        raise ValueError("More than one department is mentioned. Choose one service category and department for this complaint.")
    scores = {k: sum(1 + len(term.split()) for term in terms.split("|") if contains(text, term)) for k, terms in KEYWORDS.items()}
    best = max(scores.values(), default=0)
    winners = [k for k, score in scores.items() if score == best and score > 0]
    if len(winners) != 1:
        raise ValueError("Jurisdiction is unclear. Select the service category and department.")
    return winners[0], None

def tokens(text):
    return re.findall(r"\w+", text.casefold())

def retrieve(query, documents, limit=3):
    if not documents:
        return [], "No manuals loaded"
    try:
        import numpy as np
        def vector(text):
            v = np.zeros(512, dtype="float32")
            for token in tokens(text):
                v[int.from_bytes(hashlib.sha256(token.encode()).digest()[:4], "big") % 512] += 1
            norm = np.linalg.norm(v)
            return v / norm if norm else v
        matrix = np.stack([vector(d["text"]) for d in documents])
        q = vector(query).reshape(1, -1)
        try:
            import faiss
            index = faiss.IndexFlatIP(512)
            index.add(matrix)
            scores, indices = index.search(q, min(limit, len(documents)))
            pairs = zip(scores[0], indices[0])
            backend = "FAISS / hashed lexical features"
        except ImportError:
            scores = matrix @ q[0]
            pairs = [(scores[i], i) for i in np.argsort(-scores)[:limit]]
            backend = "NumPy lexical fallback"
        return [dict(documents[int(i)], score=round(float(s), 3)) for s, i in pairs if s > 0], backend
    except ImportError:
        q = set(tokens(query))
        ranked = sorted(documents, key=lambda d: len(q & set(tokens(d["text"]))), reverse=True)
        return [dict(d, score=len(q & set(tokens(d["text"])))) for d in ranked[:limit] if q & set(tokens(d["text"]))], "Keyword fallback"

def route(text, category, documents, region="Punjab", department_id=None,
          stage="First complaint", city="", prior_reference="", in_court=False, complaint_kind=None):
    if stage not in STAGES:
        raise ValueError("Choose a valid complaint stage.")
    inferred = None
    if category == "Detect automatically":
        category, inferred = detect(text, region)
    if category not in CATEGORIES:
        raise ValueError("Choose a supported service category.")
    department_id = department_id or inferred
    if not department_id:
        named = [d for d in available_departments(category, region) if any(contains(text, a) for a in d.aliases)]
        if len(named) == 1:
            department_id = named[0].id
        else:
            raise ValueError(f"Choose the department for {category}; the app will not guess your provider or district office.")
    if department_id not in DEPARTMENTS:
        raise ValueError("The selected department is not in the directory.")
    department = DEPARTMENTS[department_id]
    if department.category != category:
        raise ValueError("The selected department does not match the service category.")
    if department.regions and region not in department.regions:
        raise ValueError(f"{department.name} is not listed for {region}. Check the location of the complaint or choose the correct department.")
    target = department
    escalation = DEPARTMENTS.get(department.escalation)
    notes = [department.caveat] if department.caveat else []
    if category == "Banking":
        notes.append("Use Sunwai to complain to the financial institution first. Select BMP only after checking commercial-bank eligibility; SBP handles specified cases and is not an automatic appeal from BMP.")
    review = department.review_required or in_court or stage == "Challenge a formal decision"
    if department.review_required and not city.strip():
        notes.append("District and exact office were not supplied. Confirm the local office before submission.")
    if stage != "First complaint" and not prior_reference.strip():
        review = True
        notes.append("Earlier complaint or decision reference was not supplied. Add it before seeking escalation; the draft remains addressed to the selected office.")
    if stage == "Unresolved earlier complaint" and escalation and not in_court and prior_reference.strip():
        target = escalation
        review = review or target.review_required
        notes.append("Suggested escalation for administrative redress, subject to the receiving forum's eligibility checks.")
        if target.caveat:
            notes.append(target.caveat)
    if in_court:
        notes.append("This matter is already before a court/tribunal. Obtain advice on the proper forum; no automatic ombudsman escalation is selected.")
    if stage == "Challenge a formal decision":
        notes.append("A formal appeal needs the decision, applicable law and appeal deadline. This draft requests review; it does not identify or file a statutory appeal.")
    if department.locality:
        notes.append(f"Service-area check: {department.locality}. Confirm the address lies within the authority's jurisdiction.")
    if category == "Gas & petroleum" and any(contains(text, s) for s in ("leak", "leakage", "گیس لیک", "gas leak")):
        notes.append("For a current gas leak, move away from the hazard and contact the utility's emergency service immediately. Do not wait for a complaint draft.")
    allowed_ids = {department.id, target.id}
    if is_pemra(department.id):
        allowed_ids.add("pemra")  # Shared PEMRA laws and supplied source documents.
    from .guidance import research_documents, department_guide
    from .reference_library import scoped_references
    scoped = [d for d in [*research_documents(), *starter_documents(), *documents]
              if d["category"] == category or d.get("department_id") in allowed_ids]
    scoped = [d for d in scoped if (not d.get("region") or region in d["region"])
              and (not d.get("department_id") or d["department_id"] in allowed_ids)]
    scoped.extend(scoped_references(allowed_ids, region))
    hits, backend = retrieve(text + " " + department.name, scoped, limit=5)
    from .legal import filing_profile
    profile = filing_profile(target.id, region, text, complaint_kind)
    if stage == "Challenge a formal decision":
        profile.update(endpoint_verified=False, legal_provisions=[], legal_status="Formal appeal recipient, provisions and limitation period require decision-specific review")
    if in_court and target.id in ("wafaqi", "omb-kp", "banking-mohtasib"):
        profile.update(endpoint_verified=False, legal_provisions=[], legal_status="Pending court proceedings: ombudsman admissibility requires individual review")
    guide = department_guide(target.id, region, profile)
    return {**profile, "filing_guide": guide, "category": category, "body": profile["recipient"] or target.name, "portal": target.url,
            "department_id": department.id, "department": department.name, "target_id": target.id,
            "guidance": target.scope, "source": target.url, "channel": target.channel,
            "matches": hits, "backend": backend, "stage": stage, "notes": notes,
            "escalation": escalation.name if escalation else "Requires case-specific review",
            "escalation_url": escalation.url if escalation else "",
            "appellate_forum": "Formal appellate forum requires the decision and applicable law",
            "statutory_deadline": None, "review_required": review,
            "reviewed": REVIEW_DATE, "prior_reference": prior_reference}
