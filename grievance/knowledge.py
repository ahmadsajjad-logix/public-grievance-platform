"""Local retrieval: hashed multilingual features, FAISS when available.

This is lexical retrieval, not a pretrained semantic embedding model.
Uploaded manuals are reference material, never executable instructions.
"""
import hashlib
import re

AUTHORITIES = {
    "Electricity": ("NEPRA", "https://nepra.org.pk/CAD-Database/CMS-CAD/home.php", "NEPRA Complaint Handling & Dispute Resolution Procedure Rules, 2015", "https://nepra.org.pk/"),
    "Telecom": ("PTA", "https://complaint.pta.gov.pk/userlogin.aspx", "PTA complaint management guidance", "https://complaint.pta.gov.pk/Usermanual/User_Manual_CMS_Web.pdf"),
    "Broadcasting": ("PEMRA", "https://pemra.gov.pk/", "Consult current PEMRA complaint guidance", "https://pemra.gov.pk/"),
    "Federal administration": ("Wafaqi Mohtasib", "https://complaints.mohtasib.gov.pk/", "Federal ombudsman jurisdiction requires eligibility review", "https://www.mohtasib.gov.pk/"),
    "Municipal services": ("Local municipal authority", "", "Local jurisdiction and provincial service rules require verification", ""),
}
KEYWORDS = {
    "Electricity": "electricity electric bill iesco k-electric kelectric nepra bijli light wapda بجلی بل",
    "Telecom": "telecom internet mobile sim pta signal network انٹرنیٹ موبائل",
    "Broadcasting": "pemra television broadcast tv channel نشریات",
    "Federal administration": "federal pension passport nadra mohtasib وفاقی پنشن",
    "Municipal services": "municipal garbage sewer water sanitation pani kachra street پانی کچرا",
}

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

def route(text, category, documents):
    if category == "Detect automatically":
        words = set(tokens(text))
        scores = {k: len(words & set(tokens(v))) for k, v in KEYWORDS.items()}
        maximum = max(scores.values())
        winners = [k for k, v in scores.items() if v == maximum]
        if maximum == 0 or len(winners) != 1:
            raise ValueError("Jurisdiction is unclear. Select the service category and retry.")
        category = winners[0]
    body, portal, guidance, source = AUTHORITIES[category]
    hits, backend = retrieve(text, [d for d in documents if d["category"] == category])
    return {"category": category, "body": body, "portal": portal, "guidance": guidance,
            "source": source, "matches": hits, "backend": backend,
            "appellate_forum": "Requires review of jurisdiction and the original decision",
            "statutory_deadline": None}
