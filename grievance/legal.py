"""Source-backed filing profiles, separate from the general agency directory.

Only the profiles below have provision-level research. An agency URL alone
does not establish an exact filing recipient or a substantive legal ground.
"""
import re
from .pemra import COUNCILS, OFFICES, OFFICE_SOURCE, SOURCE as PEMRA_SOURCE, is_pemra, council_id, recipient

REVIEWED = "2026-10-03"
COC = "https://www.pemra.gov.pk/coc/"
RULES = "https://www.pemra.gov.pk/assets/uploads/legal/coc_rules_2010.pdf"
ORDINANCE = "https://pemra.gov.pk/assets/uploads/legal/Ordinance_2002.pdf"
CODE = "https://pemra.gov.pk/assets/uploads/legal/Code_of_Conduct.pdf"
GENERAL_RULES = "https://www.pemra.gov.pk/assets/uploads/legal/PEMRA_Rules_2009.pdf"
ISLAMABAD = "https://www.pemra.gov.pk/isb/"
KINDS = ["Not specified", "Programme / advertisement content", "Cable / distribution service", "Employee wages", "Other"]


def provision(citation, purpose, source, kind="Filing procedure"):
    return dict(citation=citation, purpose=purpose, source=source, kind=kind)


def filing_profile(department_id, region, text, complaint_kind=None):
    result = dict(endpoint_verified=False, recipient=None, address="",
                  endpoint_source="", legal_provisions=[], legal_reviewed=None,
                  legal_status="Directory only - exact recipient and applicable legal provisions are not verified",
                  evidence_needed=[], complaint_kind=complaint_kind)
    if not is_pemra(department_id):
        from .guidance import PROFILES
        researched = PROFILES.get(department_id)
        if researched:
            result["legal_status"] = "Filing guidance researched; exact statutory grounds require complaint-specific review"
        if department_id in ("banking-mohtasib", "sbp", "jazz", "zong", "ufone", "telenor", "onic", "ptcl", "scom"):
            result.update(legal_reviewed=researched.get("reviewed"),
                          legal_provisions=[provision(p["citation"], p["purpose"], p["source"], "Regulatory framework — applicability requires review") for p in researched["laws"]])
        if department_id == "banking-mohtasib":
            result.update(recipient="Banking Mohtasib (Ombudsman) Pakistan", endpoint_verified=True,
                          endpoint_source="https://www.bankingmohtasib.gov.pk/Website/preComplaintForm.aspx")
        if department_id in ("wafaqi", "omb-kp"):
            law = researched["laws"][0]
            result.update(legal_provisions=[provision(law["citation"], law["purpose"], law["source"])],
                          legal_reviewed=REVIEWED, legal_status="Maladministration jurisdiction provision sourced; eligibility and substantive grounds require review")
        if department_id == "ogra" and re.search(r"gas|sngpl|ssgc|گیس|سوئی", text, re.I):
            law = researched["laws"][0]
            result.update(legal_provisions=[provision(law["citation"], law["purpose"], law["source"])],
                          legal_reviewed=REVIEWED, legal_status="Gas-complaint filing provisions sourced; eligibility and substantive grounds require review")
        electricity = {"nepra", "lesco", "iesco", "fesco", "gepco", "pesco", "hesco", "sepco", "qesco", "mepco", "tesco", "hazeco", "ke"}
        if department_id in electricity:
            source = "https://nepra.org.pk/Legal.php"
            result.update(legal_reviewed=REVIEWED,
                          legal_status="Revised 2025 Consumer Service Manual complaint procedure identified; exact office and alleged breach require review")
            result["legal_provisions"] = [provision("Consumer Service Manual (26 November 2025), clause 10.1; supplied PDF page 65",
                "Consumer Service Centres and DISCO one-window offices receive complaints and provide acknowledgments with reply dates.", source)]
            if department_id == "nepra":
                result["legal_provisions"].append(provision("Consumer Service Manual (26 November 2025), clause 15.1.3; NEPRA Act section 39; supplied PDF page 81",
                    "An eligible written complaint alleging licensee contravention may be considered under the 2015 Complaint Handling and Dispute Resolution (Procedure) Rules. Identify the alleged contravention and earlier supplier response.", source))
            if re.search(r"wrong meter reading|incorrect meter reading|wrong calculation|غلط ریڈنگ", text, re.I):
                result["legal_provisions"].append(provision("Consumer Service Manual (26 November 2025), clause 10.3.1(a); supplied PDF page 65",
                    "Wrong meter-reading or charge-calculation complaints are listed for redressal/reply within seven days of receipt. Receipt by the supplier must be established; this is not a general appeal deadline.", source, "Issue-specific service standard"))
        return result
    result["recipient"] = "Regional Director, PEMRA - concerned regional office (confirm jurisdiction)"
    result["endpoint_source"] = COC
    office = OFFICES.get(department_id)
    if office and office["region"] == region:
        result.update(recipient=f"Regional Director, PEMRA {office['city']}",
                      endpoint_source=OFFICE_SOURCE, endpoint_reviewed="2026-10-04",
                      endpoint_note="Official regional office listed. Contact it to confirm complaint acceptance and the relevant Council route before filing; a separate Council at this location is not confirmed.")
    council = COUNCILS.get(council_id(region) if department_id == "pemra" else department_id)
    if council and council["region"] == region:
        result.update(recipient=recipient(council), address=council["address"],
                      endpoint_verified=True, endpoint_source=PEMRA_SOURCE,
                      endpoint_reviewed="2026-10-04")
    if not complaint_kind or complaint_kind == "Not specified":
        # Conservative fallback for existing callers; ambiguous services need selection.
        content = re.search(r"\b(drama|dramma|programme|program|advertisement|content|religious|cultural)\b|ڈرامہ|ڈراما|اشتہار|مواد", text, re.I)
        service = re.search(r"\b(bill|billing|connection|salary|wages)\b", text, re.I)
        complaint_kind = "Programme / advertisement content" if content and not service else "Not specified"
    result["complaint_kind"] = complaint_kind
    if complaint_kind != "Programme / advertisement content":
        result["legal_status"] = "PEMRA recipient researched; provisions for this complaint type still require verification"
        return result
    result["legal_reviewed"] = REVIEWED
    result["legal_status"] = "PEMRA broadcast-content filing provisions sourced; alleged breach requires evidence and review"
    result["legal_provisions"] = [
        provision("PEMRA Ordinance 2002, section 26(2), as amended in 2023",
                  "Council jurisdiction to receive and review public complaints about licensed broadcast or distributed programmes.", COC),
        provision("PEMRA (Councils of Complaints) Rules 2010, rule 8(1)",
                  "File before the Council or authorized officer where the programme or advertisement was viewed; the officer places it before the Council.", RULES),
        provision("PEMRA (Councils of Complaints) Rules 2010, rule 11(1) and (3)",
                  "The regional officer in charge acts as Council Secretary and receives complaints.", RULES),
        provision("PEMRA Rules 2009, rule 18",
                  "The Regional General Manager acts as secretary to the respective Council.", GENERAL_RULES),
        provision("PEMRA Rules 2009, rule 15(1)",
                  "Broadcast content must comply with section 20, applicable rules, the content code and licence conditions.", GENERAL_RULES),
    ]
    if re.search(r"religio|cultur|islam|مذہب|ثقافت|اسلام", text, re.I):
        result["legal_provisions"].append(
            provision("PEMRA Ordinance 2002, section 20(b)",
                      "Potential ground: preservation of national, cultural, social and religious values. The stated concern needs specific examples; a violation is not established by this draft.", ORDINANCE, "Potential substantive ground"))
    if re.search(r"religio|islam|مذہب|اسلام", text, re.I):
        result["legal_provisions"].append(
            provision("Electronic Media (Programmes and Advertisements) Code of Conduct 2015, clause 3(1)(a)",
                      "Potential ground concerning Islamic values. Ask the Council to assess identified broadcast material, rather than asserting an established breach.", CODE, "Potential substantive ground"))
    if re.search(r"indecen|obscen|vulgar|pornograph|فحش|عریاں", text, re.I):
        result["legal_provisions"].extend([
            provision("PEMRA Ordinance 2002, section 20(c)",
                      "Potential content restriction relevant to the stated decency allegation, subject to evidence and context.", ORDINANCE, "Potential substantive ground"),
            provision("Electronic Media (Programmes and Advertisements) Code of Conduct 2015, clause 3(1)(e)",
                      "Potential restriction on indecent, obscene or pornographic content; the Council must assess the actual material.", CODE, "Potential substantive ground"),
        ])
    result["evidence_needed"] = ["Identify the channel, programme, episode, broadcast date/time, and place where viewed.",
                                 "Describe the exact scenes or dialogue and explain how each alleged ground applies; include timestamps or clips if available.",
                                 "These are provisions for a complaint requesting examination, not a finding that the broadcaster broke the law."]
    return result
