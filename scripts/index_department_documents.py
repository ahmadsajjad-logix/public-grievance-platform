"""Build page-cited reference chunks from the supplied departmental library.

These references are searchable evidence, not automatically approved clauses.
Scanned pages are reported explicitly instead of silently omitted as indexed.
"""
import hashlib
import json
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "Relevant Departmental Downloads"
VISUAL_SUMMARIES = {
    "c573ef26-6updated_public_complaints_resolution_mechanism_11062020 (pp).pdf":
        "Visually reviewed summary of scanned PTA poster, page 1: first register the complaint with the telecom operator using its helpline or written channels. The operator may request contact and CNIC details, a written application and service ownership evidence where relevant. If unresolved or unsatisfactory, approach PTA. Poster lists 0800-55055 and PTA Headquarters, F-5/1, Islamabad. Its named staff, zonal contacts and operating hours need current verification. The poster describes a further nominated-officer step on behalf of Wafaqi Mohtasib; eligibility must be independently checked.",
}


def classify(relative):
    folder, name = relative.parts[0], relative.name
    if folder.startswith("NEPRA"):
        note = "Check later amendments and complaint-specific applicability."
        if name.startswith("Notification"):
            note = "Historical 2021 tariff notification; not current general complaint law."
        elif "2005" in name:
            note = "Historical standards: NEPRA now lists 2026 distribution performance regulations; verify supersession."
        elif "2025" in name:
            note = "Revised Consumer Service Manual dated 26 November 2025; verify subsequent amendments."
        return ["nepra", "lesco", "iesco", "fesco", "gepco", "pesco", "hesco", "sepco", "qesco", "ke"], "Electricity", [], note
    if folder.startswith("PTA"):
        return ["pta"], "Telecom", [], "Scanned procedure poster dated by filename 2020; named officials and hours need current confirmation."
    if folder.startswith("PEMRA"):
        return ["pemra"], "Broadcasting", [], "Read with the 2023 Ordinance amendment; original rules alone are not the consolidated current law."
    if folder.startswith("OGRA"):
        return ["ogra", "sngpl", "ssgc"], "Gas & petroleum", [], "Check amendments; supplied regulation 4(c) and portal describe different 90-day triggers. Do not auto-calculate."
    if folder.startswith("Khyber"):
        return ["kp-rts"], "Public service delays", ["Khyber Pakhtunkhwa"], "Amendment rules concern commission appointments; not a complete list of service entitlements or deadlines."
    if folder.startswith("Punjab"):
        return ["punjab-rts"], "Public service delays", ["Punjab"], "Text is Punjab Right to Public Services Act 2019 despite filename 2018. Section 1(3) requires commencement notification; services need section 4 notifications."
    if folder.startswith("WAFAQI"):
        return ["wafaqi"], "Federal administration", [], "Blank complaint forms, not a complete jurisdiction or deadline source."
    if folder.startswith("First"):
        return ["punjab-2", "sindh-2", "kp-2", "balochistan-2"], "Police & public safety", [], "Secondary criminal investigation handbook; verify every statutory proposition against current primary law."
    if folder.startswith("FEDERAL"):
        return [], "", [], "FIA inquiry rules are not proof of current NCCIA cybercrime jurisdiction. Excluded from automatic routing."
    return [], "", [], "Banking Ombudsman material is outside the current department directory; older forms need current validation."


def main():
    manifest, chunks = [], []
    for path in sorted(LIBRARY.rglob("*.pdf")):
        relative = path.relative_to(LIBRARY)
        ids, category, regions, note = classify(relative)
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        reader = PdfReader(path)
        empty = []
        count = 0
        if path.name in VISUAL_SUMMARIES:
            chunks.append(dict(name=path.name, document_id=digest[:16], sha256=digest,
                               page=1, category=category, department_ids=ids, region=regions,
                               text=VISUAL_SUMMARIES[path.name], trusted=False,
                               evidence_type="visually reviewed summary of supplied scan", version_note=note,
                               local_reference=relative.as_posix()))
            count += 1
        for page_no, page in enumerate(reader.pages, 1):
            text = page.extract_text() or ""
            if len(text.strip()) < 30:
                empty.append(page_no)
                continue
            if not ids or "Historical" in note:
                continue
            for start in range(0, len(text), 1000):
                value = text[start:start + 1200].strip()
                if not value:
                    continue
                chunks.append(dict(name=path.name, document_id=digest[:16], sha256=digest,
                                   page=page_no, category=category, department_ids=ids, region=regions,
                                   text=value, trusted=False, evidence_type="supplied document — reference only",
                                   version_note=note, local_reference=relative.as_posix()))
                count += 1
        manifest.append(dict(document_id=digest[:16], file=relative.as_posix(), sha256=digest,
                             pages=len(reader.pages), pages_needing_ocr=empty, indexed_chunks=count,
                             visual_summary_pages=[1] if path.name in VISUAL_SUMMARIES else [],
                             department_ids=ids, category=category, version_note=note))
    (ROOT / "data" / "department_documents.json").write_text(json.dumps(dict(documents=manifest, chunks=chunks), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(manifest)} PDFs inventoried; {len(chunks)} page-cited reference chunks; {sum(bool(d['pages_needing_ocr']) for d in manifest)} documents include pages requiring OCR.")


if __name__ == "__main__":
    main()
