"""Official-source research additions, reviewed 3 October 2026.

Framework references are not automatically pleading grounds. Broad directory
entries still require the actual provider, district and disputed decision.
"""
from copy import deepcopy

CHECKED = "2026-10-03"
PCP = "https://web.citizenportal.gov.pk/"
BAL = "https://balochistan.gov.pk/citizen-services/"
CM = "https://cm.balochistan.gob.pk/register-complaint"


def route(kind, url, source=None, instructions="", label=None):
    result = dict(kind=kind, value=url, source=source or url, instructions=instructions, checked=CHECKED)
    if label:
        result["label"] = label
    return result


def law(title, source, purpose):
    return dict(citation=title, source=source, purpose=purpose)


def add(profiles, id, scope, exclusion, framework, channels, steps, requirements, limits="A service complaint does not suspend a statutory appeal or limitation period. Identify the decision and applicable procedure before calculating dates."):
    profiles[id] = dict(can=scope, cannot=exclusion, laws=framework,
                        channels=channels, procedure=steps, requirements=requirements,
                        limits=limits, sources=list(dict.fromkeys([c["source"] for c in channels] + [p["source"] for p in framework])))


def extend(profiles):
    gaslaw = law("Complaint Resolution Procedure Regulations, 2003, regulations 4–5", "https://ogra.org.pk/download/330", "Seek redress from the gas licensee first; an eligible unresolved complaint can go to OGRA with supporting records.")
    for id, url in [("sngpl", "https://www.sngpl.com.pk/complaints.jsp?mdids=89"), ("ssgc", "https://www.ssgc.com.pk/web/?page_id=5058")]:
        add(profiles, id, "Gas billing, metering, connection and supply complaints for this company's customers.",
            "Check the supplier on the bill. A consumer complaint does not decide a criminal case or automatically cancel charges.", [gaslaw],
            [route("form" if id == "sngpl" else "website", url, instructions="Use the customer complaint route and keep the reference. For a leak, use the company's emergency channel immediately.")],
            ["Identify the consumer number, bill period, address and exact issue.", "Lodge the complaint with the utility and keep its acknowledgment and response.", "If unresolved, consult the OGRA guide and its admissibility rules before escalation."],
            ["Gas bill / consumer number", "Earlier application, payment or meter records relevant to the issue"], profiles["ogra"]["limits"])
    profiles["sngpl"]["channels"].append(route("phone", "1199", "https://www.sngpl.com.pk/sitemap.jsp"))
    add(profiles, "fbr", "Taxpayer-service complaints, refund delay and administrative problems in the relevant FBR formation.",
        "Assessment, tax liability and customs valuation appeals use their own statutory process; an FBR helpdesk ticket or FTO complaint is not a substitute.",
        [law("FTO jurisdiction: tax maladministration versus assessment appeals", "https://fto.gov.pk/faq.aspx", "Administrative delay can be considered separately from the correctness of a tax assessment; select the applicable tax statute for an appeal.")],
        [route("website", "https://fbr.gov.pk/ask-fbr/173354", instructions="Open the Customer Relationship Management (CRM) link for assistance or complaints."), route("email", "helpline@fbr.gov.pk", "https://fbr.gov.pk/ask-fbr/173354")],
        ["Identify the RTO/LTO/customs office, tax type, period and reference.", "Use FBR's helpline or linked CRM service and retain the case number.", "For unresolved maladministration, check FTO eligibility; for an order, check the appeal provision in that order."], ["NTN/registration reference where applicable", "Refund/application/order reference, dates and prior correspondence"])
    add(profiles, "federal-office", "Help identify an unnamed federal agency and its administrative complaint route.",
        "An unnamed agency has no single governing statute or recipient. Pakistan Citizen Portal is administrative routing, not a universal statutory appeal.",
        deepcopy(profiles["wafaqi"]["laws"]), [route("portal", PCP, BAL, "Select the actual ministry/agency and office. This is a general government grievance route.", "Open Pakistan Citizen Portal")],
        ["Name the agency and service before choosing substantive legal provisions.", "Complain through the agency's own channel or the general government portal and retain acknowledgment.", "Check Wafaqi Mohtasib eligibility for unresolved federal maladministration."], ["Agency and office, application/reference, dates and response"])

    for id, title, src, page, kind in [
        ("omb-punjab", "Punjab Office of the Ombudsman Act, 1997, section 9", "https://ombudsmanpunjab.gov.pk/mandate", "https://ombudsmanpunjab.gov.pk/", "website"),
        ("omb-sindh", "Establishment of the Office of Ombudsman for the Province of Sindh Act, 1991", "https://mohtasibsindh.gov.pk/FolderFlyer.pdf", "https://complaints.mohtasibsindh.gov.pk/", "portal"),
        ("omb-balochistan", "Balochistan Ombudsman Ordinance, 2001; Investigation and Disposal of Complaints Regulations, 2005, regulation 3", "https://balochistan.gov.pk/wp-content/uploads/2024/09/The-Ombudsman-for-the-Province-of-Baln-Reg-Inv-and-Disposal-of-Complaints-Reg-2005-2005.pdf", "https://balochistan.gov.pk/wp-content/uploads/2024/09/The-Ombudsman-for-the-Province-of-Baln-Reg-Inv-and-Disposal-of-Complaints-Reg-2005-2005.pdf", "website"),
    ]:
        add(profiles, id, "Investigation of maladministration by eligible agencies of this province.",
            "Check statutory exclusions, pending court proceedings and personal service matters. This is not a general appeal court or a federal-agency forum.",
            [law(title, src, "An eligible person may seek investigation of provincial agency maladministration, subject to admissibility and exclusions.")],
            [route(kind, page, instructions="Use E-Complaint on the official page." if id == "omb-punjab" else "Check the complaint requirements before filing; retain acknowledgment.")],
            ["Identify the provincial agency, action or delay and desired remedy.", "Provide a signed factual complaint and the declarations and identity documents required by the Ombudsman.", "For paper filing, confirm the appropriate regional registry before delivery; keep a stamped copy or postal proof."],
            ["Identity/contact details, agency correspondence and signed complaint", "Required affidavit/declaration; disclose other proceedings"],
            "Check the applicable complaint limitation and admissibility rules. No automatic disposal or appeal deadline is inferred.")
    profiles["omb-balochistan"]["procedure"].append("The 2005 Regulations allow registry submission personally, through an authorized representative or by post; a current public electronic filing endpoint has not been verified.")

    municipal = {
        "punjab": ("Punjab Local Government Act, 2025", "https://lgcd.punjab.gov.pk/system/files/PLGA_2025.pdf"),
        "sindh": ("Sindh Local Government Act, 2013, as amended", "https://www.sindhlaws.gov.pk/setup/publications_SindhCode/PUB-NEW-18-000156.pdf"),
        "kp": ("Khyber Pakhtunkhwa Local Government Act, 2013, as amended", "https://www.kpcode.kp.gov.pk/uploads/THE_KHYBER_PAKHTUNKHWA_LOCAL_GOVERNMENT_ACT_2013.pdf"),
        "balochistan": ("Balochistan Local Government Act, 2010", "https://balochistancode.gob.pk/lawdir/69b034f7-9fe6-45d3-a6cb-1fff3c94f9b6.pdf"),
    }
    for province, (title, src) in municipal.items():
        channels = [route("portal", CM, BAL, "General administrative complaint; choose your local government department and district.", "Open provincial government complaint portal")] if province == "balochistan" else [route("portal", PCP, BAL, "General government route: identify the municipality and service; this is not a statutory appeal.", "Open Pakistan Citizen Portal")]
        add(profiles, province + "-0", "Municipal sanitation, drains, street lighting and local services within the responsible council's service area.", "Cantonment, development-authority, water-company and waste-company areas can have different providers. Identify the location and asset owner.",
            [law(title, src, "Sets the provincial local-government framework; the actual council and assigned service determine responsibility.")], channels,
            ["Identify the town/tehsil, ward/UC, street and landmark.", "Report to the responsible municipal office or the indicated general government route.", "Keep the complaint reference and any response; eligible unresolved maladministration may go to the provincial Ombudsman."], ["Precise service location, dates and photographs where available"])
    waste = law("Suthra Punjab Authority Act, 2026", "https://lgcd.punjab.gov.pk/system/files/Suthra_Punjab_Authority_Act_2026.pdf", "Provincial solid-waste and sanitation framework; water-authority functions remain distinct.")
    for id in ("punjab-0", "lwmc", "rwmc"):
        if id == "rwmc":
            add(profiles, id, "Rawalpindi waste collection and sanitation within the company's service area.", "Water billing, water supply and sewer networks require the responsible water provider.", [waste], [], ["Report the exact waste location, type and dates.", "Use Suthra Punjab's form or 1139 and keep the complaint ID."], ["District, tehsil, service location and contact number"])
        else:
            profiles[id]["laws"].append(deepcopy(waste))
        profiles[id]["channels"].insert(0, route("form", "https://suthra.punjab.gov.pk/complaint.php", instructions="For solid waste/sanitation only. Select district and tehsil, describe the location and problem, review, then submit.", label="Open Suthra Punjab sanitation complaint form"))
        profiles[id]["sources"].extend([waste["source"], "https://suthra.punjab.gov.pk/complaint.php"])

    water = {
        "punjab": ("Punjab Water and Sanitation Authority Act, 2025", "https://wasa.punjab.gov.pk/regulations", "https://wasa.punjab.gov.pk/complaints", "Use the WASA complaint instructions or 1334; confirm that your address is in the relevant agency's service area."),
        "sindh": ("Sindh Local Government Act, 2013; provider-specific water corporation legislation", municipal["sindh"][1], "https://complain.kwsc.gos.pk/add/complaint", "This form is for Karachi KWSC only. Elsewhere identify the local corporation/municipality; do not submit another city's case to KWSC."),
        "kp": ("Khyber Pakhtunkhwa Local Government Act, 2013", municipal["kp"][1], "https://www.wsspeshawar.org.pk/", "WSSP publishes 1334 for its Peshawar service area; other districts require their own WSSC/municipality."),
        "balochistan": ("Balochistan Local Government Act, 2010; provider-specific water legislation", municipal["balochistan"][1], CM, "Choose the actual water provider/PHE/local government and district. Quetta's water authority has separate legislation; local responsibility must be confirmed."),
    }
    for province, (title, src, page, instructions) in water.items():
        add(profiles, province + "-1", "Water supply, sewerage and water-billing complaints to the actual service provider.", "A province-wide directory category is not one water utility. Confirm the provider before using a city-specific form.",
            [law(title, src, "Responsibility depends on the designated water agency and its territorial service area.")],
            [route("form" if province == "sindh" else "portal" if province == "balochistan" else "website", page, BAL if province == "balochistan" else page, instructions, "Open Karachi KWSC complaint form" if province == "sindh" else None)],
            ["Identify provider, consumer number if available, town/UC and precise location.", instructions, "Retain the reference, photographs and disputed bills; request the appropriate remedial work or billing review."], ["Service address and landmark", "Relevant bill/reference and incident details"])

    for province, title, src, page in [
        ("kp", "Khyber Pakhtunkhwa Police Act, 2017", "https://kpcode.kp.gov.pk/homepage/lawDetails/1322", "https://apipsm.kppolice.gov.pk/psm/VideoTutorial"),
        ("balochistan", "Balochistan Police Act, 2011", "https://balochistancode.gob.pk/pdfviewer.aspx?pdffile=4ecf3da1-c43d-4e9a-a5c5-b7439115a086.pdf", "https://pkm.balochistanpolice.gov.pk/public/home/services"),
    ]:
        add(profiles, province + "-2", "Police service complaints and requests to record a reported offence in the competent police jurisdiction.", "A service-centre report or administrative complaint is not itself an FIR. Confirm territorial police/other law-enforcement jurisdiction.",
            [law(title, src, "Police organization and duties; FIR recording and criminal investigation additionally follow applicable criminal procedure.")],
            [route("website", page, instructions="KP provides IGP Complaint / Complaint for FIR through its Police Sahulat Markaz app." if province == "kp" else "The Police Khidmat Markaz page describes in-person Crime Report services and required documents.")],
            ["Identify incident location, station, dates and the action or refusal complained of.", "Keep the original written application and delivery evidence; use the official service instructions.", "Use the FIR guide for CrPC 154/155 distinctions. A report acknowledgment is not confirmation of FIR registration."], ["CNIC, written account and prior application/FIR reference where available"])
    for province in municipal:
        base = deepcopy(profiles[province + "-2"])
        base["can"] = "Traffic-police administrative complaints, officer conduct, signals and parking issues within the responsible unit's area."
        base["cannot"] = "The police complaint channel is for administrative redress. Challenging a traffic challan requires the procedure and forum stated on that notice; it is not cancelled by opening a complaint ticket."
        base["procedure"] = ["Identify the traffic unit, road/junction, date/time and any challan number.", "For misconduct or inaction use the province's police complaint instructions; ask which traffic/Safe City unit controls the equipment.", "For a challan dispute, follow the notice's review/court procedure and retain payment and vehicle records."]
        base["requirements"] = ["Location, vehicle/challan reference if relevant, dates and supporting evidence"]
        profiles[province + "-3"] = base

    for province, title, src, page, phone in [
        ("sindh", "Sindh Food Authority Act, 2016 (Act XIV of 2017)", "https://sfa.gos.pk/documents/Sindh%20Act%20No.XIV%20of%202017.pdf", "https://sfa.gos.pk/", "+923300116553"),
        ("balochistan", "Balochistan Food Authority Act, 2014", "https://bfa.gob.pk/wp-content/uploads/2024/12/BFA-Act-2014.pdf", "https://bfa.gob.pk/contact_us/", ""),
    ]:
        add(profiles, province + "-4", "Food safety, adulteration, expired food and unhygienic food-business complaints.", "Food enforcement does not automatically award private compensation or decide every pricing dispute.",
            [law(title, src, "Food-business regulation and enforcement within the Act's applicable area and powers.")], [route("website", page, instructions="Use the authority's current complaint/contact instructions.")],
            ["Identify the food business, address, product/batch, date and observed problem.", "Report through the official contact route; preserve receipts, packaging and photographs.", "Keep the response and complaint reference; distinguish enforcement from any separate compensation claim."], ["Business location, product details, receipt/photos if available"])
        if phone:
            profiles[province + "-4"]["channels"].insert(0, route("whatsapp", phone, page))

    consumer = [
        ("punjab", "Punjab Consumer Protection Act, 2005, as amended in 2025, sections 26–28", "https://pccmdpunjab.gov.pk/static/acts/acts.pdf", "Written notice to the provider precedes a claim; section 28 addresses a 15-day response and limitation. The 2025 changes designate consumer-court judges; confirm the current district filing registry."),
        ("sindh", "Sindh Consumer Protection Act, 2014 (Act XVII of 2015), section 29", "https://www.sindhlaws.gov.pk/setup/publications_SindhCode/PUB-15-000096.pdf", "Section 29 requires prior written notice, addresses a 15-day response and claim limitation with qualified extensions. Keep proof of delivery and check the applicable dates promptly."),
        ("kp", "Khyber Pakhtunkhwa Consumers Protection Act, 1997, as amended", "https://kpcode.kp.gov.pk/homepage/lawDetails/1196", "Check the district Consumer Court's filing procedure and territorial jurisdiction under the Act; a general grievance portal is not a court filing."),
        ("balochistan", "Balochistan Consumers Protection Act, 2003, sections 12–16; Rules 2007", "https://balochistancode.gob.pk/lawdir/3e165a1b-2b36-49b5-a0fc-cd49af9e79f3.pdf", "The Act provides consumer courts and complaint procedure. The 2007 Rules provide a written plain-paper complaint on oath with particulars and supporting documents."),
    ]
    for province, title, src, step in consumer:
        add(profiles, province + "-5", "Consumer remedies for qualifying defective goods or deficient services under the provincial Act.", "An administrative price-control report is different from a judicial compensation claim. Eligibility, notice and limitation must be checked.", [law(title, src, "Provides consumer complaint and remedial mechanisms subject to the Act's conditions.")],
            [route("website", src, instructions="Read the statutory filing requirements. A working public e-filing endpoint for this court claim has not been verified.", label="Read consumer complaint filing requirements")],
            ["Preserve the invoice, contract, defect/service evidence and provider correspondence.", step, "Confirm the district consumer registry; submit the signed claim and required copies, and keep the filing receipt."], ["Invoice/contract, supplier identity/address and evidence", "Required prior notice and delivery proof, where applicable"], step)

    revenue = [
        ("punjab", "Punjab Land Records Authority Act, 2017; Land Revenue Act, 1967", "https://www.punjab-zameen.gov.pk/guidanceAndRegulation", "https://www.punjab-zameen.gov.pk/complaints", "website"),
        ("sindh", "Sindh land-record administration: Board of Revenue service instructions", "https://sindhzameen.gos.pk/FAQs.aspx", "https://sindhzameen.gos.pk/demo_registries/complaint.aspx", "form"),
        ("kp", "West Pakistan Land Revenue Act, 1967, as applicable in KP", "https://www.revenue.kp.gov.pk/wp-content/uploads/2020/08/The-W.P-Land-Revenue-Act-1967.pdf", "https://www.revenue.kp.gov.pk/", "website"),
        ("balochistan", "Balochistan Land Revenue Act, 1967", "https://balochistan.gov.pk/wp-content/uploads/2024/10/The-Baln-Land-Revenue-Act-1967-1967.pdf", CM, "portal"),
    ]
    for province, title, src, page, kind in revenue:
        add(profiles, province + "-6", "Land-record service delay, record errors and revenue-office administration.", "A complaint does not establish ownership, reverse a revenue order or replace a title suit/statutory appeal. Development-authority and other land agencies may keep separate records.", [law(title, src, "Identify the record custodian and applicable correction or appeal procedure; online information alone is not certified title evidence.")],
            [route(kind, page, BAL if province == "balochistan" else page, "Identify the district, tehsil/taluka, mouza/deh and service office.")],
            ["Give the land identifiers and service/application reference without guessing ownership.", "Report service delay or the specific discrepancy to the record custodian through its complaint route.", "Obtain certified records; for an adverse order, identify the proper statutory appeal separately."], ["District, mouza/deh, parcel/record identifiers, application receipt and relevant order"])

    healthcare = [
        ("punjab", "Punjab Healthcare Commission Act, 2010; Complaint Management Regulations, 2014", "https://os.phc.org.pk/downloads/PHC-Complaint-Management-Regulations-Gazette-Notification-2014.pdf", "https://os.phc.org.pk/complaintFAQs.aspx", "website"),
        ("sindh", "Sindh Healthcare Commission Act, 2013", "https://shcc.org.pk/wp-content/uploads/2022/12/SHCC-ACT-2013.pdf", "https://shcc.org.pk/", "website"),
        ("kp", "Khyber Pakhtunkhwa Health Care Commission Act, 2015, section 13", "https://hcc.kp.gov.pk/wp-content/uploads/2022/02/2015_5_THE_KHYBER_PAKHTUNKHWA_HEALTH_CARE_COMMISSION_ACT_2015.pdf", "https://complaintshcc.kp.gov.pk/", "portal"),
        ("balochistan", "Balochistan Healthcare Commission Act, 2019", "https://health.balochistan.gov.pk/wp-content/uploads/2025/02/BHCC-Act-2019.pdf", "https://health.balochistan.gov.pk/", "website"),
    ]
    for province, title, src, page, kind in healthcare:
        add(profiles, province + "-7", "Healthcare service complaints, including quality failures and relevant public-facility administration.", "A health-department staffing complaint differs from a negligence complaint to a healthcare commission. Neither route automatically awards damages or replaces emergency treatment.", [law(title, src, "Healthcare regulation and complaint framework; identify the facility, conduct and competent forum.")],
            [route(kind, page, "https://hcc.kp.gov.pk/directorate-of-legal-affairs/" if province == "kp" else page, "Follow the Commission's complaint instructions." if province != "balochistan" else "Health Department publishes its complaint contacts; the Commission's own filing endpoint is not verified.")],
            ["First complain to the facility's management and keep the dated record.", "For quality/negligence, check the relevant Commission's admissibility, affidavit and time-limit requirements; for staffing/medicines, identify the district health administration.", "Provide the treatment chronology and relevant records; retain the authority's acknowledgment."], ["Facility and practitioner details, dates, medical records and earlier complaint", "Identity, authorization and affidavit required by the receiving forum"])
    profiles["kp-7"]["procedure"][1] = "KP HCC instructions permit approaching the Commission when the facility has not addressed the complaint within 30 days. Submit the required attested affidavit; separately check the Act's complaint limitation and exclusions."
    profiles["kp-7"]["sources"].append("https://hcc.kp.gov.pk/directorate-of-legal-affairs/")

    education = [
        ("punjab", "Punjab Private Educational Institutions Rules, 1984", "https://schools.punjab.gov.pk/system/files/1984.pdf", "https://pepris.pesrp.edu.pk/complaints", "form", "PEPRIS is for private-school complaints. For public-school staff/service issues contact the district education authority."),
        ("sindh", "Sindh Right of Children to Free and Compulsory Education Act, 2013; private-school regulatory instructions", "https://drips.gos.pk/Downloads/11112025freeship10percent.pdf", "https://drips.gos.pk/", "website", "DRIPS handles private institutions. For public-school monitoring use the School Education Department's monitoring office."),
        ("kp", "KP Private Schools Regulatory Authority: official complaint instructions", "https://psra.gkp.pk/public/", "https://psra.gkp.pk/public/", "website", "PSRA directs private-school complaints to Pakistan Citizen Portal or Ekhtyar Awam Ka; public schools require the district education administration."),
        ("balochistan", "Balochistan education-sector statutory and policy framework", "https://newemis.emis.gob.pk/Uploads/BESP2020-25.pdf", CM, "portal", "Use the provincial government portal for a School Education Department complaint, selecting the district and school. This is an administrative route."),
    ]
    for province, title, src, page, kind, step in education:
        add(profiles, province + "-8", "School-service, staff-absence and appropriate private-school regulatory complaints.", "Private-school regulation and public-school administration use different offices. A fee objection is not automatically a proven statutory breach.", [law(title, src, "Determine school type and applicable law before claiming a fee, admission or education entitlement.")],
            [route(kind, page, BAL if province == "balochistan" else page, step, "Open Punjab private-school complaint form" if province == "punjab" else None)],
            ["Identify school name, district, public/private status and the disputed conduct.", step, "Keep the school response, fee demand/receipt or attendance evidence and request a specific remedy."], ["School identity/location, dates and relevant fee/communication records"])

    for id, title, src, page, kind in [
        ("lda", "Lahore Development Authority Act, 1975, as amended", "https://lda.gop.pk/website/images/stories/lda_act_1975_as_amended_by_2013.pdf", "https://lda.gop.pk/", "website"),
        ("rda", "Punjab Development of Cities Act, 1976", "https://rda.gop.pk/", "https://cms.rda.gop.pk/", "portal"),
        ("kda", "Karachi Development Authority Order, 1957", "https://www.kda.gos.pk/Docs/CMS/file/KDA%20Rules/President%205%20of%2057-.pdf", "https://www.kda.gos.pk/contents/", "website"),
    ]:
        add(profiles, id, "Development-authority scheme, planning, allotment and relevant property-service administration within its jurisdiction.", "This is not the general Patwari/land-record office. A service complaint cannot determine disputed title or replace a statutory planning/property appeal.", [law(title, src, "Establishes the development-authority framework; the scheme, decision and applicable rules determine the remedy.")],
            [route(kind, page, instructions="Use the complaint link or contact/one-window instructions. Application-status lookup is for tracking, not a new complaint.")],
            ["Identify the scheme, plot/application number and authority office.", "Complain through the authority's published route and retain acknowledgment.", "For a formal adverse order, check the law and appeal instructions specific to that decision."], ["Scheme/plot reference, application/order, receipts and prior correspondence"])

    # Upgrade proven direct forms; keep login portals and information pages distinct.
    for id in ("nccia", "nepra", "ogra", "kwsc", "lwmc", "kp-rts"):
        for item in profiles[id]["channels"]:
            if item["kind"] == "portal":
                item["kind"] = "form"
    profiles["pemra"]["channels"].insert(0, route("website", "https://pemra.gov.pk/complaints/", instructions="Official complaint app, call-centre and PCP options; the Council information page is not an online filing form.", label="Open PEMRA complaint options"))
    profiles["pemra"]["channels"].append(route("phone", "0800-73672", "https://pemra.gov.pk/complaints/"))
    profiles["pemra"]["sources"].append("https://pemra.gov.pk/complaints/")
    profiles["sswmb"]["laws"].append(law("Sindh Solid Waste Management Act, 2021", "https://www.sindhlaws.gov.pk/setup/publications_SindhCode/PUB-NEW-23-000070.pdf", "Framework for solid-waste collection, disposal and boards; confirm the operating area."))
    for id in ("lesco", "iesco", "fesco", "gepco", "pesco", "hesco", "sepco", "qesco", "mepco", "tesco", "hazeco", "ke"):
        profiles[id]["laws"] = deepcopy(profiles["nepra"]["laws"])
    additions = {
        "punjab-4": ("Punjab Food Authority Act, 2011", "https://pfa.gop.pk/wp-content/uploads/2023/02/The-Punjab-Food-Authority-Act-2011.pdf", "Food-safety regulation and enforcement; identify the product, conduct and applicable provision before alleging an offence."),
        "pemra": ("PEMRA Ordinance, 2002, section 26; Council of Complaints Rules, 2010", "https://www.pemra.gov.pk/assets/uploads/legal/coc_rules_2010.pdf", "Council complaint procedure; programme-content grounds and cable-service issues require different legal analysis."),
        "fto": ("Establishment of the Office of Federal Tax Ombudsman Ordinance, 2000", "https://fto.gov.pk/assets/img/fto_Ordinance_2000-_4th_draft_a.pdf", "Tax maladministration jurisdiction subject to statutory exclusions; not a substitute for assessment appeals."),
        "kwsc": ("Karachi Water and Sewerage Corporation Act, 2023", "https://www.sindhlaws.gov.pk/setup/Publications/PUB-23-000081.pdf", "Water and sewerage corporation framework for Karachi Division and additionally notified areas."),
        "cda": ("Capital Development Authority Ordinance, 1960", "https://cda.gov.pk/Assets/pdf/cdaordinance1960.pdf", "Planning, development and assigned municipal functions; identify the responsible formation and applicable rules."),
        "kp-4": ("Khyber Pakhtunkhwa Food Safety Authority Act, 2014, as amended", "https://kpcode.kp.gov.pk/uploads/2014_10_THE_KHYBER_PAKHTUNKHWA_FOOD_SAFETY_AUTHORITY_ACT_2014.pdf", "Food-safety authority framework; select the applicable offence/enforcement provision from the actual facts."),
        "punjab-2": ("Police Order, 2002, as applicable in Punjab", "https://punjabpolice.gov.pk/RulesandRegs", "Police duties and administration; FIR recording and judicial remedies also depend on the CrPC."),
        "sindh-2": ("Sindh (Repeal of Police Act, 1861 and Revival of Police Order, 2002) (Amendment) Act, 2019", "https://sindhlaws.gov.pk/SindhGazetteDetail.aspx?X=ACT&Year=2019", "Provincial police framework; apply subsequent amendments and the relevant criminal procedure to the facts."),
        "kp-8": ("Khyber Pakhtunkhwa Private Schools Regulatory Authority Act, 2017", "https://www.kpcode.kp.gov.pk/homepage/RuleDetails/1359", "Registration, regulation and supervision of private schools; public schools use a different administrative route."),
        "balochistan-8": ("Balochistan Compulsory Education Act, 2014", "https://balochistancode.gob.pk/lawdir/3a78cfa3-fce8-4e76-9d3c-00992080db78.pdf", "Compulsory education framework; check territorial application and the child's eligibility before asserting a specific entitlement."),
        "sindh-6": ("Sindh Land Revenue Act, 1967, section 52, substituted by Act X of 2022", "https://sindhlaws.gov.pk/setup/publications_SindhCode/PUB-NEW-23-000078.pdf", "Lawful record-of-rights entries carry a rebuttable presumption; a web complaint does not itself correct a record or determine title."),
        "fbr": ("Federal Board of Revenue Act, 2007", "https://www.fbr.gov.pk/Categ/Federal-Board-of-Revenue-Act-2007/659", "FBR institutional framework; the relevant income-tax, sales-tax or customs law governs substantive decisions and appeals."),
    }
    for id, args in additions.items():
        profiles[id]["laws"].append(law(*args))
    profiles["cda-municipal"]["laws"] = deepcopy(profiles["cda"]["laws"])
    for province in ("punjab", "sindh"):
        profiles[province + "-3"]["laws"] = deepcopy(profiles[province + "-2"]["laws"])
    profiles["kda"]["channels"].insert(0, route("portal", "https://cc.kda.gos.pk/", "https://www.kda.gos.pk/contents/", "KDA's official site links this Complaint Centre. Its current public form fields have not been verified."))
    profiles["kp-7"]["channels"][0]["value"] = "https://complaintshcc.kp.gov.pk/login"
    for profile in profiles.values():
        profile["sources"] = list(dict.fromkeys(profile["sources"] + [c["source"] for c in profile["channels"]] + [p["source"] for p in profile["laws"]]))
    return profiles
