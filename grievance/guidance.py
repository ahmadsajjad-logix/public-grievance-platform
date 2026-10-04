"""Reviewed source summaries for Agent 02 and the citizen's filing guide.

An accessible website is not proof of jurisdiction. Unreviewed crawl results
are kept separate from these approved summaries and from petition clauses.
"""
from copy import deepcopy
from urllib.parse import quote
from .catalog import DEPARTMENTS

CHECKED = "2026-10-03"
from .offences import PECA, NCCIA
WFAQ = "https://www.mohtasib.gov.pk/Detail/YmZhYzY4ODktNjNkMC00ZWNlLWI4YjAtYjViYzJmZjlkYjc2"
WLAW = "https://mohtasib.gov.pk/SiteImage/Downloads/presidential_order_1983.pdf"
NLAW = "https://nepra.org.pk/Legal.php"
NFORM = "https://nepra.org.pk/CAD-Database/CMS-CAD/cregister.php"
PTA_MANUAL = "https://complaint.pta.gov.pk/Usermanual/User_Manual_CMS_Web.pdf"
OGRA = "https://complaint.ogra.org.pk/complaint"
KPFORM = "https://erts.kprts.gov.pk/complaint/public_complaint"


def channel(kind, value, source, instructions=""):
    return dict(kind=kind, value=value, source=source, instructions=instructions, checked=CHECKED)


PROFILES = {
    "nccia": dict(
        can="Receive and investigate alleged electronic offences within PECA jurisdiction.",
        cannot="An online complaint is not an FIR, finding of guilt or guaranteed recovery of money. Ordinary service complaints may belong to the provider or regulator.",
        procedure=["Preserve original communications, URLs, dates and transaction references.", "Open NCCIA's complaint form and complete the identity, location, category and factual details. Use the field guidance below.", "Complete the declaration and verification yourself, submit and retain acknowledgment. Follow NCCIA's requests for evidence."],
        requirements=["The official form marks name, CNIC, gender, mobile, city, crime category and details as required", "Preserve supporting digital evidence for investigators; do not share passwords or OTPs"],
        limits="An acknowledgment is not FIR registration. Applicable PECA provisions, cognizability and investigation procedure depend on the facts and current law.",
        sources=[NCCIA, PECA], channels=[channel("portal", NCCIA, NCCIA)],
        laws=[dict(citation="Prevention of Electronic Crimes Act, 2016, as amended; section 29", source=PECA, purpose="NCCIA investigation framework. Select a cyber offence in the FIR guide to examine possible substantive sections.")]),
    "nepra": dict(
        can="Examine electricity supply, connection, metering and billing complaints against regulated licensees.",
        cannot="A regulator complaint is not automatically a statutory appeal or a finding that every disputed charge is unlawful. Identify the supplier and earlier complaint.",
        procedure=["Complain to the distribution company's SDO/XEN first and keep the reference and response.", "Use the NEPRA form, identify the licensee, explain the disputed action and attach the relevant record. The form screens complaint age and prior approach.", "Retain the official acknowledgment; respond to requests for evidence or hearing."],
        requirements=["Earlier complaint to the supplier and response, if received", "Bill / consumer reference and supporting record", "The form currently lists PDF/JPG attachments up to 2.5 MB; check again when filing"],
        limits="The form screens issues older than one year. Applicability, exceptions and any appeal limit require individual review.",
        sources=[NFORM, NLAW, "https://nepra.org.pk/CAD-Database/CMS-CAD/home.php"],
        channels=[channel("portal", NFORM, NFORM, "Complete the form; paste the complaint and requested relief, then attach permitted supporting files.")],
        laws=[dict(citation="NEPRA Complaint Handling and Dispute Resolution (Procedure) Rules, 2015", source=NLAW, purpose="Governs complaint handling; applicable rule and substantive breach require issue-specific review.")],
        address="Director General, Consumer Affairs Division, NEPRA Tower, Attaturk Avenue (East), G-5/1, Islamabad",
        address_source="https://nepra.org.pk/CAD-Database/CMS-CAD/home.php"),
    "pta": dict(
        can="Handle telecom consumer complaints through its Complaint Management System and the relevant service operator.",
        cannot="A telecom service complaint does not by itself establish the correct criminal-investigation or digital-content-removal route.",
        procedure=["Retain your operator complaint reference and response.", "Use PTA CMS and its official user manual to select the complaint type, complete the required fields and keep the acknowledgment.", "The manual describes operator investigation followed by PTA verification of the action taken."],
        requirements=["Operator and affected service/account", "Complaint facts, earlier reference and relevant evidence; verify mandatory CMS fields"],
        limits="Exact applicable consumer regulations, complaint-specific time limits and regional recipient are pending document review.",
        sources=[PTA_MANUAL],
        channels=[channel("portal", "https://complaint.pta.gov.pk/userlogin.aspx", PTA_MANUAL, "Sign in/register and use the complaint registration workflow in the manual.")], laws=[dict(citation="Pakistan Telecommunication (Re-organization) Act, 1996, sections 3–6", source="https://pakistancode.gov.pk/pdffiles/administratorcf6de2451af9e9d016e5fef2ac7e1562.pdf", purpose="Establishes PTA and its regulatory functions and responsibilities; a specific consumer breach needs the relevant regulation and facts.")]),
    "pemra": dict(
        can="Receive complaints concerning licensed broadcast/distributed programmes; regional Councils examine content complaints.",
        cannot="A broadcaster-content complaint is different from a social-media complaint, employee-wage claim or cable billing dispute. The same provisions cannot be reused indiscriminately.",
        procedure=["Identify the programme, channel, episode, broadcast date/time and where it was viewed.", "Describe the specific scenes/dialogue and the remedy sought. Address the relevant Regional Director / Council Secretary; confirm territorial jurisdiction.", "Keep proof of delivery and respond to requests for material or a hearing."],
        requirements=["Programme/channel and exact dates", "Specific scenes, timestamps and supporting recording or transcript where available"],
        limits="Select the complaint type. Do not infer a breach from a broad objection to cultural or religious themes.",
        sources=["https://www.pemra.gov.pk/coc/", "https://www.pemra.gov.pk/assets/uploads/legal/coc_rules_2010.pdf"],
        channels=[channel("website", "https://www.pemra.gov.pk/coc/", "https://www.pemra.gov.pk/coc/", "Council filing information; this link is not a submitted complaint or a verified online form.")], laws=[]),
    "wafaqi": dict(
        can="Investigate maladministration by eligible federal agencies, including administrative delay and inaction.",
        cannot="Generally excludes pending court matters, defence, foreign relations and an employee's own service grievance against their agency; eligibility and exceptions need review.",
        procedure=["State the facts, agency, dates and relief sought. Approaching the agency first is advisable under the FAQ.", "File through the official online service, email, post or a regional/head office; retain acknowledgment.", "The office screens jurisdiction before investigation and requests the agency's response."],
        requirements=["CNIC copy, complete address and phone number", "Relevant correspondence and agency response"],
        limits="FAQ: ordinarily file within three months of the grievance; justified delay may be considered. It describes a general 60-day disposal limit and 30-day review/representation routes. Verify the governing trigger and exceptions before calculating dates.",
        sources=[WFAQ, WLAW, "https://www.mohtasib.gov.pk/"],
        channels=[channel("portal", "https://complaints.mohtasib.gov.pk/", "https://www.mohtasib.gov.pk/"), channel("email", "registrar.isb@mohtasib.gov.pk", "https://www.mohtasib.gov.pk/", "Review the petition and required supporting documents before sending yourself.")],
        laws=[dict(citation="Establishment of the Office of Wafaqi Mohtasib (Ombudsman) Order, 1983, Article 9", source=WLAW, purpose="Investigation of alleged agency maladministration, subject to jurisdictional exclusions.")],
        address="Office of the Wafaqi Mohtasib, 36 Constitution Avenue, G-5/2, Islamabad", address_source="https://www.mohtasib.gov.pk/"),
    "ogra": dict(
        can="Examine eligible complaints against gas licensees after the consumer fails to obtain relief from the licensee.",
        cannot="The gas complaint checklist must not be assumed to cover every petroleum-quality or other licensing dispute.",
        procedure=["First seek redress from the licensee, for example SNGPL or SSGC; retain its decision and your application.", "Submit the required particulars and records through OGRA's complaint form.", "Registrar routes the case to a designated officer, who obtains the licensee's response and considers evidence and a hearing."],
        requirements=["NIC, gas bill and supply application as applicable", "Licensee Review Committee decision and details of proceedings before another body"],
        limits="The official form requires filing within 90 days of the complaint to the licensee. This is a filing window, not a promised resolution time.",
        sources=[OGRA, "https://ogra.org.pk/index.php/complaints-section", "https://ogra.org.pk/download/330"],
        channels=[channel("portal", OGRA, OGRA, "Complete Points 1–8 and the applicable supporting-document requirements.")],
        laws=[dict(citation="Complaint Resolution Procedure Regulations, 2003, regulations 4 and 5", source="https://ogra.org.pk/download/330", purpose="OGRA's published gas-complaint checklist cites these provisions for application particulars and supporting records.")]),
    "ke": dict(
        can="Handle K-Electric customer billing and technical service complaints.",
        cannot="This channel is for K-Electric accounts; do not send another distributor's complaint here.",
        procedure=["Keep your KE account number and explain the billing or technical issue.", "Use KE Live, WhatsApp or the helpline and save the complaint reference.", "If unresolved, assess eligibility for a NEPRA complaint with the prior record."],
        requirements=["KE account number and relevant bill / incident details"],
        limits="WhatsApp availability is not a guaranteed complaint-resolution time. Issue-specific legal provisions remain to be verified.",
        sources=["https://ke.com.pk/contact-us/"],
        channels=[channel("whatsapp", "+923480000118", "https://ke.com.pk/contact-us/", "Send Hi yourself and follow the billing/technical complaint menu."), channel("phone", "118 / (021) 99000", "https://ke.com.pk/contact-us/"), channel("website", "https://ke.com.pk/contact-us/", "https://ke.com.pk/contact-us/", "Official links to KE Live and customer centres.")], laws=[]),
    "kp-rts": dict(
        can="Address refusal, delay or deficient delivery of notified public services in Khyber Pakhtunkhwa.",
        cannot="Not every government service is notified. The designated officer, first appeal and service-specific notification must be checked.",
        procedure=["Identify the notified service, designated officer and original application date.", "Check the applicable first-appeal route. The form has fields for its date and copy.", "Complete the online complaint/appeal description and required identity, district and address fields."],
        requirements=["The form requests identity images (CNIC front/back or applicable passport identity)", "Department, notified service, address and supporting/first appeal record"],
        limits="No universal RTS deadline: use the notification for the specific service and the applicable appeal procedure.",
        sources=["https://www.kprts.gov.pk/", KPFORM],
        channels=[channel("portal", KPFORM, KPFORM, "Paste the prepared complaint in Complaint or Appeal Description; complete the service and identity fields.")],
        laws=[dict(citation="Khyber Pakhtunkhwa Right to Public Services Act, 2014", source="https://www.kprts.gov.pk/", purpose="Framework for notified public services; exact entitlement and appeal provision require the service notification.")]),
    "fto": dict(
        can="Consider tax-administration maladministration within the Federal Tax Ombudsman's jurisdiction.",
        cannot="A dispute about assessment or tax/duty liability may belong to the statutory tax appeal process rather than an FTO complaint.",
        procedure=["Use Form A and identify the tax office and administrative failure.", "Check the territorial schedule and current complaint mechanism on the official website."],
        requirements=["Form A particulars, tax references and relevant administrative record"],
        limits="Recipient, exclusions and specific limitation periods need case-specific verification.",
        sources=["https://fto.gov.pk/faq.aspx"], channels=[channel("website", "https://fto.gov.pk/faq.aspx", "https://fto.gov.pk/faq.aspx")], laws=[]),
}


def service_profile(can, cannot, source, steps, requirements, channels, **extra):
    return dict(can=can, cannot=cannot, sources=[source], procedure=steps,
                requirements=requirements, channels=channels, laws=[],
                limits="Issue-specific legal grounds, appeal routes and resolution deadlines are not yet verified.", **extra)


for distributor in ("lesco", "iesco", "fesco", "gepco", "pesco", "hesco", "sepco", "qesco", "mepco", "tesco", "hazeco"):
    PROFILES[distributor] = service_profile(
        "Register the selected electricity distributor's billing and service complaints through PITC CCMS.",
        "Verify the distributor on your bill. This is the supplier complaint stage, not a NEPRA decision or appeal.",
        "https://ccms.pitc.com.pk/complaint",
        ["Look up the account using its reference or mobile number; confirm the account shown.", "Select the complaint category/type, enter the facts and complete the portal's verification steps yourself.", "Keep the ticket and use the official tracking facility; retain it for any later NEPRA complaint."],
        ["Bill reference / account and contact details", "Issue location, category and description"],
        [channel("portal", "https://ccms.pitc.com.pk/complaint", "https://ccms.pitc.com.pk/complaint", "Paste the facts into Complaint Details; complete account lookup and verification.")])

PROFILES["kwsc"] = service_profile(
    "Receive Karachi water and sewerage complaints through its complaint redressal form.",
    "Confirm the town, UC and service coverage. The form is not a land-title or other municipal dispute forum.",
    "https://complain.kwsc.gos.pk/add/complaint",
    ["Select the town, UC/mohalla, complaint type and grievance.", "Enter a short description (the form displays a 350-character limit), landmark and contact information.", "The form has a picture upload; PDF acceptance was not established. Keep the complete petition for your record."],
    ["Name, phone, town, UC/mohalla and landmark", "Consumer number where available; relevant picture"],
    [channel("portal", "https://complain.kwsc.gos.pk/add/complaint", "https://complain.kwsc.gos.pk/add/complaint")], character_limit=350)
for id in ("cda", "cda-municipal"):
    PROFILES[id] = service_profile(
        "Route Islamabad civic issues to the relevant CDA formation through its complaint system.",
        "Confirm CDA responsibility for the location and service. A civic complaint is not a statutory property appeal.",
        "https://complaints.cda.gov.pk/",
        ["Create/sign into your account using the portal's identity and contact requirements.", "Describe the issue, select its category and attach relevant photos.", "Track the case on the CDA portal; its published workflow allows reopening if dissatisfied."],
        ["CNIC and contact details for portal registration", "Complaint category, facts and relevant photos"],
        [channel("portal", "https://complaints.cda.gov.pk/", "https://complaints.cda.gov.pk/")])
PROFILES["sswmb"] = service_profile(
    "Garbage collection and disposal within the Board's operating areas.",
    "Do not assume responsibility for water supply, street lighting or every municipal service.",
    "https://sswmb.gos.pk/portal/",
    ["Describe the waste problem and exact location; confirm the responsible district office.", "Use the published complaint phone/WhatsApp and retain any reference returned."],
    ["Location, landmark, incident dates and relevant photos"],
    [channel("whatsapp", "+923181030851", "https://sswmb.gos.pk/portal/"), channel("phone", "+92-21-99333702", "https://sswmb.gos.pk/portal/")])
PROFILES["lwmc"] = service_profile(
    "Receive waste collection, sweeping and related sanitation complaints in its service area.",
    "The form lists some WASA-related categories; responsibility for sewerage or large drains must be confirmed rather than assumed.",
    "https://www.lwmc.com.pk/complaint.php",
    ["Enter the complete address, contact details, category and message in the online complaint form.", "Alternatively call the published 1139 helpline. Retain any complaint reference."],
    ["Location, contact details and description of the waste problem"],
    [channel("portal", "https://www.lwmc.com.pk/complaint.php", "https://www.lwmc.com.pk/complaint.php"), channel("phone", "1139", "https://www.lwmc.com.pk/complaint.php")])
PROFILES["punjab-4"] = service_profile(
    "Receive Punjab food-safety complaints about food businesses and products.",
    "Food-safety enforcement does not automatically settle a private compensation or general price dispute.",
    "https://pfa.gop.pk/for-consumer/report-a-complaint/",
    ["Describe the food/product, business location, dates and observed issue.", "Use the published helpline, WhatsApp, official app or contact page; retain acknowledgment."],
    ["Business address, product/batch details and supporting photos/receipt where available"],
    [channel("whatsapp", "+923331017300", "https://pfa.gop.pk/for-consumer/report-a-complaint/"), channel("phone", "1223", "https://pfa.gop.pk/for-consumer/report-a-complaint/"), channel("website", "https://pfa.gop.pk/for-consumer/report-a-complaint/", "https://pfa.gop.pk/for-consumer/report-a-complaint/")])
PROFILES["kp-4"] = service_profile(
    "Receive food-safety complaints or feedback in Khyber Pakhtunkhwa.",
    "Confirm the district and issue; a contact message is not a verified appeal or compensation claim.",
    "https://e.kpfsa.gov.pk/contact",
    ["Use the contact form with name, email, subject and message, or contact the published office.", "Ask for an acknowledgment and instructions for supporting evidence."],
    ["Food business/product, location, dates and facts"],
    [channel("website", "https://e.kpfsa.gov.pk/contact", "https://e.kpfsa.gov.pk/contact", "Contact form for inquiries, complaints and feedback."), channel("phone", "+92-919212959", "https://e.kpfsa.gov.pk/contact")],
    address="New C&W Building, Ground Floor, Khyber Road, Peshawar", address_source="https://e.kpfsa.gov.pk/contact",
    hours="Published contact hours: Monday–Friday, 9:00 AM–5:00 PM. Confirm holiday changes before travelling.")
PROFILES["punjab-2"] = service_profile(
    "Receive complaints about FIR refusal, faulty investigation, illegal detention, false FIRs, neglect and demands for illegal gratification.",
    "An administrative complaint is not a court appeal or an emergency response request.",
    "https://www.punjabpolice.gov.pk/igp_complaint_center_8787",
    ["Identify the station, officers where known, incident dates and previous application.", "Use the official page's online registration link or the published 1787 call/SMS channel.", "The centre forwards complaints to senior officers and checks responses with complainants."],
    ["Station, incident details, application/FIR reference and supporting record"],
    [channel("website", "https://www.punjabpolice.gov.pk/igp_complaint_center_8787", "https://www.punjabpolice.gov.pk/igp_complaint_center_8787"), channel("phone / SMS", "1787", "https://www.punjabpolice.gov.pk/igp_complaint_center_8787")])
PROFILES["sindh-2"] = service_profile(
    "Receive police complaints through the Sindh IGP Complaint Management System.",
    "Select the correct station and complaint type; this does not replace criminal procedure or a judicial appeal.",
    "https://igpcms.sindhpolice.gov.pk/assets/guide/IGP_CMS_Guide.pdf",
    ["Read the portal guide and register the complaint under the correct type.", "Describe the facts and disclose any earlier forum approached; attach that record if applicable.", "Save the tracking number and use the official tracking page."],
    ["Complainant/contact information, complaint type and description", "Prior forum record when applicable; guide lists JPG, PNG, PDF, MPG and MP3 up to 30 MB — recheck on filing"],
    [channel("portal", "https://igpcms.sindhpolice.gov.pk/", "https://igpcms.sindhpolice.gov.pk/assets/guide/IGP_CMS_Guide.pdf")])
PROFILES["omb-kp"] = service_profile(
    "Investigate maladministration by eligible KP provincial agencies.",
    "The mandate excludes pending court/tribunal matters and bodies outside its statutory definition; anonymous complaints are not entertained.",
    "https://ombudsmankp.gov.pk/jurisdiction/mandate",
    ["Identify the provincial agency and administrative failure.", "Use the official E-Complaint instructions, checking admissibility before submission."],
    ["Identity/contact particulars and relevant agency correspondence"],
    [channel("website", "https://ombudsmankp.gov.pk/", "https://ombudsmankp.gov.pk/jurisdiction/mandate")])
PROFILES["omb-kp"]["laws"] = [dict(citation="Khyber Pakhtunkhwa Provincial Ombudsman Act, 2010, section 9", purpose="Maladministration investigation subject to statutory jurisdiction and exclusions.", source="https://ombudsmankp.gov.pk/jurisdiction/What_We_Can_Do")]

# Supplied documents are identified by title and PDF page, with official
# publication gateways where available. They do not prove current staff details.
PROFILES["pta"]["procedure"][0] = "First complain to the operator by its helpline or written channel. If unresolved or the response is unsatisfactory, approach PTA and retain the operator reference."
PROFILES["pta"]["sources"].append("https://www.pta.gov.pk/category/public-complaints-resolution-mechanism-407381753-2023-05-30")
PROFILES["pta"]["channels"].append(channel("phone", "0800-55055", PROFILES["pta"]["sources"][-1], "PTA helpline. Hours and named staff on the supplied older poster have not been verified as current."))
PROFILES["ogra"]["limits"] = "Source conflict: the supplied Complaint Resolution Procedure Regulations 2003, regulation 4(c), PDF page 3, measures 90 days from failure to obtain redress (or another Registrar-approved period); the online checklist measures from lodging with the licensee. Confirm the applicable trigger with OGRA. No automatic deadline is generated."
PROFILES["ogra"]["cannot"] = "Check the precise licensed activity and eligibility. The supplied regulation 4(d) excludes anonymous complaints and matters pending or already decided by a court/tribunal. A gas-form checklist may not suit a refined-oil complaint."
PROFILES["ogra"]["procedure"].append("The supplied regulation 8 describes a written decision, ordinarily within 90 days of admission, with reasons recorded for delay; regulation 9 describes an appeal. Confirm amendments and triggering dates before relying on either period.")
PROFILES["nepra"]["laws"].append(dict(citation="Consumer Service Manual, revised 26 November 2025, clauses 10.1 and 15.1.1–15.1.4 (supplied PDF pages 65 and 81)", source=NLAW, purpose="Supplier complaint handling and routes for unresolved disputes; Provincial Office of Inspection, section 39 and section 35-A have distinct scopes."))
PROFILES["punjab-rts"] = service_profile(
    "The supplied Punjab Right to Public Services Act 2019 provides a framework for notified public services and designated officers.",
    "The Act alone does not establish that a particular service is currently notified or identify its operational filing office.",
    "https://regulationswing.punjab.gov.pk/acts",
    ["Verify the commencement notification under section 1(3) and the service/officer/time limit notification under section 4.", "Identify the designated officer and applicable appellate authority before using section 6. An operational complaint portal has not been confirmed."],
    ["Service application and acknowledgment date", "Relevant service notification and refusal/delay record"],
    [channel("website", "https://regulationswing.punjab.gov.pk/acts", "https://regulationswing.punjab.gov.pk/acts", "Official Acts directory, not a verified filing portal.")])
PROFILES["punjab-rts"]["laws"] = [dict(citation="Punjab Right to Public Services Act 2019, sections 1(3), 4 and 6 (supplied PDF pages 3–6)", source="https://regulationswing.punjab.gov.pk/acts", purpose="Commencement, notified service conditions and appeals must be established before claiming a particular entitlement or deadline.")]


from .department_research import extend
extend(PROFILES)
from .sector_research import extend as extend_sectors
extend_sectors(PROFILES)

from .pemra import COUNCILS, SOURCE as PEMRA_SOURCE, REVIEWED as PEMRA_REVIEWED, is_pemra
for id, council in COUNCILS.items():
    PROFILES[id] = deepcopy(PROFILES["pemra"])
    PROFILES[id].update(reviewed=PEMRA_REVIEWED, address=council["address"], address_source=PEMRA_SOURCE)
    if council["phone"]:
        PROFILES[id]["channels"].append(channel("phone", council["phone"], PEMRA_SOURCE, "Council office contact; retain proof of any formal complaint filing."))


def department_guide(department_id, region="", legal_profile=None):
    d = DEPARTMENTS[department_id]
    known = PROFILES.get(department_id)
    guide = deepcopy(known) if known else dict(
        can=d.scope, cannot="Detailed statutory powers and exclusions have not yet been reviewed for this entry.",
        procedure=["Confirm the exact service provider, district and receiving office.", "Use the listed official starting page to locate its current complaint instructions; do not assume it is an online filing form."],
        requirements=["Confirm the receiving authority's own checklist before filing"],
        limits=d.caveat or "Complaint and appeal procedures require verification.", sources=[d.url],
        channels=[dict(kind="directory", value=d.url, source=d.url, instructions="Directory starting point; filing channel not verified.", checked=None)], laws=[])
    guide.update(department_id=d.id, name=d.name, region=region,
                 reviewed=known.get("reviewed", CHECKED) if known else None,
                 status="Reviewed guidance; check provision-specific limitations" if known else "Directory only — research incomplete")
    profile = legal_profile
    if profile is None and is_pemra(department_id):
        from .legal import filing_profile
        profile = filing_profile(department_id, region or (d.regions[0] if d.regions else ""), "")
    profile = profile or {}
    guide["recipient"] = profile.get("recipient") or "Exact receiving officer requires verification"
    guide["address"] = profile.get("address") or guide.get("address", "")
    guide["address_source"] = profile.get("endpoint_source") or guide.get("address_source", "")
    guide["hours"] = guide.get("hours", "Opening hours not verified; confirm before travelling.")
    guide["map"] = ("https://www.google.com/maps/search/?api=1&query=" + quote(guide["address"])) if guide["address"] else ""
    guide["provisions"] = profile.get("legal_provisions", [])
    from .reference_library import library
    guide["local_documents"] = [dict(file=item["file"], pages=item["pages"],
                                     note=item["version_note"], missing_ocr=len(item["pages_needing_ocr"]))
                                for item in library()["documents"] if ("pemra" if is_pemra(d.id) else d.id) in item["department_ids"]]
    return guide


def research_documents():
    """The indexed corpus contains reviewed summaries with source provenance."""
    documents = []
    for id, p in PROFILES.items():
        d = DEPARTMENTS[id]
        for title, text, source in [
            ("Ambit and limits", p["can"] + " " + p["cannot"], p["sources"][0]),
            ("Filing procedure", " ".join(p["procedure"] + p["requirements"]) + " " + p["limits"], p["sources"][0]),
            *[(law["citation"], law["purpose"], law["source"]) for law in p["laws"]],
        ]:
            documents.append(dict(name=d.name + " — " + title, text=text, source=source,
                                  department_id=id, category=d.category, region=d.regions,
                                  trusted=True, reviewed=p.get("reviewed", CHECKED), evidence_type="reviewed source summary"))
    return documents


def guide_sections(guide):
    from .rights import rights_for
    from .forms import form_text
    sections = [("Title", "Department and filing guidance"), ("Heading2", guide["name"]),
                ("Normal", guide["status"]), ("Normal", "Source review: " + (guide["reviewed"] or "Not completed")),
                ("Heading2", "Legal framework")]
    sections += [("Normal", p["citation"] + ": " + p["purpose"] + " Source: " + p["source"]) for p in guide["laws"] + guide["provisions"]]
    if not guide["laws"] and not guide["provisions"]:
        sections.append(("Normal", "Governing law and complaint-specific provisions have not yet been verified."))
    rights = rights_for(guide["department_id"], guide["provisions"])
    sections.append(("Heading2", "Your rights and available remedies"))
    sections += [("Normal", r["text"] + " " + r["citation"] + " Source: " + r["source"]) for r in rights]
    if not rights:
        sections.append(("Normal", "Complaint-specific entitlements are pending review; filing information does not establish a breach or promise a remedy."))
    sections += [
                ("Heading2", "What this authority can help with"), ("Normal", guide["can"]),
                ("Heading2", "Limits and exclusions"), ("Normal", guide["cannot"]),
                ("Heading2", "How to file")]
    sections += [("Normal", f"{i}. {step}") for i, step in enumerate(guide["procedure"], 1)]
    sections += [("Normal", f"{c['kind'].title()}: {c['value']}. {c['instructions']} Source: {c['source']}") for c in guide["channels"]]
    sections += [("Heading2", "Documents and preparation")]
    sections += [("Normal", r) for r in guide["requirements"]]
    sections += [("Normal", "Uploads are optional in this app; the authority can require documents when you file."),
                 ("Normal", "Paste the prepared text into the authority's form. Attach the petition PDF only where accepted; otherwise retain it or use a confirmed paper route."),
                 ("Heading2", "Time limits and procedure"), ("Normal", guide["limits"])]
    sections += [("Heading2", "Office and follow-up"), ("Normal", guide["recipient"]),
                 ("Normal", guide["address"] or "Office address not verified"), ("Normal", guide["hours"])]
    if guide["map"]:
        sections.append(("Normal", "Map search (confirm the result): " + guide["map"]))
    sections += [("Normal", "Keep the authority's acknowledgment. The app does not submit, confirm receipt, calculate an unverified statutory deadline or monitor the authority's case status."),
                 ("Heading2", "Official sources")]
    sections += [("Normal", s) for s in dict.fromkeys(guide["sources"] + ([guide["address_source"]] if guide["address_source"] else []))]
    sections.append(("Heading2", "Official form assistance"))
    sections += [("Normal", paragraph) for paragraph in form_text(guide["department_id"]).split("\n\n")]
    if guide.get("local_documents"):
        sections.append(("Heading2", "Departmental documents consulted / indexed as references"))
        sections += [("Normal", f"{d['file']} ({d['pages']} PDF pages). {d['note']} Pages still requiring OCR: {d['missing_ocr']}.") for d in guide["local_documents"]]
    return sections


def guide_text(guide):
    return "\n\n".join(text for _, text in guide_sections(guide))
