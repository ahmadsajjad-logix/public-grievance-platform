"""Source-linked offence screening, never automatic charging or FIR registration."""
PPC = "https://pakistancode.gov.pk/pdffiles/administratord5622ea3f15bfa00b17d2cf7770a8434.pdf"
PECA = "https://www.pakistancode.gov.pk/pdffiles/administrator6a061efe0ed5bd153fa8b79b8eb4cba7.pdf"
CRPC = "https://www.kppolice.gov.pk/downloads/Code_Criminal_Procedure.pdf"
NCCIA = "https://complaint.nccia.gov.pk/"
CHECKED = "2026-10-03"
LIMITATION = ("These are possible provisions for legal review, not a finding that an offence occurred. "
              "Describe facts truthfully; do not change your account to fit a section. Police, prosecutors and courts determine "
              "the applicable charges. Provincial amendments, the incident date, exceptions and evidence may change the result. "
              "The official Pakistan Code lists PPC/CrPC as under review; this guide is not an exhaustive current-law certification.")


def entry(label, citation, source, questions, caution, evidence, cyber=False):
    return dict(label=label, citation=citation, source=source, questions=questions,
                caution=caution, evidence=evidence, cyber=cyber)


OFFENCES = {
    "theft": entry("Theft / چوری", "PPC 378 (definition), 379 (punishment)", PPC,
        ["Was movable property moved out of someone's possession without their consent?",
         "Are there facts indicating dishonest taking, rather than loss or an ownership misunderstanding?"],
        "Vehicle theft, theft in a dwelling, robbery and other special circumstances require additional provision review.",
        "Property description, serial/IMEI number if known, possession record, time/place, witnesses or CCTV."),
    "robbery": entry("Robbery / ڈکیتی یا چھینا جھپٹی", "PPC 390 (definition), 392 (punishment)", PPC,
        ["Was theft accompanied by death, hurt, restraint or fear of instant death/hurt/restraint for taking or carrying away property; OR was property delivered then and there because a present offender caused fear of instant death/hurt/restraint?"],
        "Snatching is not automatically the same legal offence in every province. Five or more participants and weapons/injury need separate assessment.",
        "Property details, exact force/threat, injuries, participant count, location/time and witnesses."),
    "extortion": entry("Extortion / بھتہ", "PPC 383 (definition), 384 (punishment)", PPC,
        ["Was someone intentionally put in fear of injury?", "Did that fear dishonestly induce delivery of property or valuable security?"],
        "A demand without delivery may involve a different provision, including attempt-related extortion provisions; do not claim completed extortion automatically.",
        "Exact demand/threat, original messages, payment records and dates."),
    "cheating": entry("Cheating involving property / دھوکے سے رقم یا مال لینا", "PPC 415 (definition), 420 (property-related cheating)", PPC,
        ["Was there deception with dishonest intent when the property transaction was induced?",
         "Did it cause delivery of property or making, alteration or destruction of a valuable security (or signed/sealed item convertible to one)?"],
        "A broken promise, unpaid debt or failed contract alone does not establish cheating.",
        "Original representation, agreement, messages, transaction receipts and facts indicating initial intent."),
    "trust": entry("Criminal breach of trust / امانت میں خیانت", "PPC 405 (definition), 406 (punishment)", PPC,
        ["Was property or control of property entrusted to the person?",
         "Was it dishonestly misappropriated, converted, used or disposed of contrary to the governing law or contract (or knowingly allowed to be so used)?"],
        "Non-payment alone is not proof of entrustment or dishonest misuse; special roles may attract other sections.",
        "Entrustment record, purpose/restrictions, accounts and evidence of misuse."),
    "threat": entry("Criminal intimidation / دھمکی", "PPC 503 (definition), 506 (punishment)", PPC,
        ["Was there a threat of injury to person, reputation or property (including a person the victim is interested in)?",
         "Was it intended to cause alarm or force an act/omission the person was not legally required to make?"],
        "An argument or insult alone does not establish criminal intimidation. Threat type and local law affect classification.",
        "Exact words, context, original recording/messages lawfully held, dates and witnesses."),
    "trespass": entry("Criminal trespass / مجرمانہ مداخلت", "PPC 441 (definition), 447 (punishment)", PPC,
        ["Was property possessed by another entered, or unlawfully remained on after lawful entry?",
         "Was the purpose to commit an offence or intimidate, insult or annoy the person in possession?"],
        "A boundary/title dispute or mere presence is not enough by itself. House-trespass has further elements.",
        "Possession record, location, entry details, conduct and witnesses."),
    "access": entry("Account/system hacking / اکاؤنٹ تک غیر مجاز رسائی", "PECA 3", PECA,
        ["Was access to a system or data obtained without authorization or beyond authorization?", "Are there facts indicating dishonest intention?"],
        "A forgotten password or public access is not proof of hacking. Copying or damaging data may require separate provisions.",
        "Account URL, login alerts, dates and original access logs where available; never disclose passwords or OTPs.", True),
    "data_copy": entry("Unauthorized data copying / ڈیٹا کی غیر مجاز نقل", "PECA 4", PECA,
        ["Was data copied or transmitted without authorization?", "Are there facts indicating dishonest intention?"],
        "Explain exactly which data was copied and how authorization was absent.",
        "Data ownership/access context, transfer evidence and timestamps.", True),
    "data_damage": entry("System/data damage / سسٹم یا ڈیٹا کو نقصان", "PECA 5", PECA,
        ["Was an information system or data interfered with or damaged?", "Are there facts indicating dishonest intention?"],
        "A technical fault alone is not evidence of an offence.",
        "Logs, before/after condition, recovery reports and dates.", True),
    "efraud": entry("Electronic fraud / آن لائن فراڈ", "PECA 14", PECA,
        ["Was a system/device/data used or interfered with, or a person induced into a relationship or deceived?",
         "Was there intent for wrongful gain and an act/omission likely to cause damage or harm?"],
        "An unsuccessful purchase or investment loss alone does not establish electronic fraud.",
        "Transaction IDs, bank/wallet reference, original chats, URLs, dates and amount; contact the payment provider promptly.", True),
    "identity": entry("Identity information misuse / شناخت کا ناجائز استعمال", "PECA 16(1)", PECA,
        ["Was another person's identity information obtained, sold, possessed, transmitted or used without authorization?"],
        "Explain whose identity information was involved and what was unauthorized. Account impersonation requires factual assessment.",
        "Profile URLs, screenshots and original notifications; avoid exposing full identity documents publicly.", True),
    "stalking": entry("Repeated unwanted online contact / آن لائن تعاقب", "PECA 24(1)(a)", PECA,
        ["Was electronic contact or attempted contact for personal interaction repeated despite a clear indication of disinterest?",
         "Are there facts indicating intent to coerce, intimidate or harass?"],
        "This entry covers repeated contact under clause (a). Monitoring, spying or harmful image distribution require separate clause review.",
        "Chronology, original communications and the indication of disinterest; preserve evidence without engaging further.", True),
}

PROCEDURE = [
    ("CrPC 154", "For information disclosing a cognizable offence, the police-station officer records oral information in writing, reads it back and obtains the informant's signature. Review the facts before signing.", CRPC + "#page=37"),
    ("CrPC 155", "For a non-cognizable case, the officer records the substance and refers the informant to a Magistrate; investigation requires the relevant Magistrate's order. Not every complaint follows the FIR route.", CRPC + "#page=37"),
    ("FIR refusal: CrPC 22-A(6), subject to local application", "An ex-officio Justice of the Peace can consider complaints concerning non-registration, investigation transfer and police neglect/excess. Retain the original police application and seek local advice on a fact-specific application; no order or FIR is guaranteed.", "https://advocategeneral.punjab.gov.pk/22A_22B"),
    ("Cybercrime reporting", "Report suspected PECA offences through NCCIA. An online complaint acknowledgment is not an FIR number. Investigation powers and cognizability require review under PECA, including sections 29 and 43.", PECA),
]


def assess(offence_id, answers):
    """Only explicitly answered facts can support a candidate, never default Yes."""
    item = OFFENCES[offence_id]
    if len(answers) != len(item["questions"]) or any(a not in ("Yes", "No", "Not sure") for a in answers):
        raise ValueError("Answer each fact question using Yes, No or Not sure.")
    if "No" in answers:
        return "The selected provision's listed elements are not all supported by your answers. Another provision or a non-criminal remedy may be relevant."
    if "Not sure" in answers:
        return "More facts are needed before this provision can be suggested for your incident."
    return "Your answers support considering this provision for professional review; they do not establish an offence or a final charge."


def report(offence_id, answers, region, incident, facts):
    item = OFFENCES[offence_id]
    parts = ["Offence and FIR preparation guide — not an FIR", "Region: " + region,
             "Incident date: " + (str(incident) if incident else "Not supplied"), item["label"],
             "Possible provision: " + item["citation"], "Source: " + item["source"],
             "Reference checked: " + CHECKED, LIMITATION,
             "Territorial application needs verification before suggesting this provision for your incident." if region in ("Azad Jammu and Kashmir", "Gilgit-Baltistan") else assess(offence_id, answers)]
    parts += [q + " Answer: " + a for q, a in zip(item["questions"], answers)]
    parts += ["Important distinction: " + item["caution"], "Records to preserve: " + item["evidence"],
              "Your factual account (not independently verified):\n" + (facts.strip() or "Not supplied")]
    parts += [title + ": " + text + " Source: " + source for title, text, source in PROCEDURE]
    parts += ["Next step: " + ("Open " + NCCIA + " and submit yourself." if item["cyber"] else
              "Take your factual account to the police station with territorial jurisdiction. Obtain acknowledgment. If registration is refused, retain the written request and refusal/reference and seek local legal assistance on the appropriate police-supervisory or judicial remedy."),
              "No complaint has been transmitted or registered by this app."]
    return "\n\n".join(parts)
