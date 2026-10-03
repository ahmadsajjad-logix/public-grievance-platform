"""Curated Pakistan routing directory. A complaint channel is not an appeal.

Reviewed against linked official sources on 2026-10-01. Local office entries
require the complainant's district; directory links are labelled separately
from online complaint forms. No universal statutory deadline is inferred.
"""
from dataclasses import dataclass

REGIONS = ["Punjab", "Sindh", "Khyber Pakhtunkhwa", "Balochistan", "Islamabad", "Gilgit-Baltistan", "Azad Jammu and Kashmir"]
PROVINCES = REGIONS[:4]
REVIEW_DATE = "2026-10-01"
STAGES = ["First complaint", "Unresolved earlier complaint", "Challenge a formal decision"]


@dataclass(frozen=True)
class Department:
    id: str
    name: str
    category: str
    regions: tuple[str, ...]
    url: str
    aliases: tuple[str, ...] = ()
    escalation: str = ""
    channel: str = "Official website / office directory"
    scope: str = ""
    caveat: str = ""
    locality: str = ""
    review_required: bool = False


DEPARTMENTS: dict[str, Department] = {}


def add(id, name, category, url, *, regions=(), aliases=(), escalation="", channel="Official website / office directory", scope="", caveat="", locality="", review_required=False):
    DEPARTMENTS[id] = Department(id, name, category, tuple(regions), url, tuple(aliases), escalation, channel, scope, caveat, locality, review_required)


add("nepra", "NEPRA", "Electricity", "https://nepra.org.pk/CAD-Database/CMS-CAD/home.php", aliases=("nepra", "نیپرا"), channel="Complaint portal", scope="Electricity billing, connections, metering and supply complaints.", caveat="Keep the supplier's earlier complaint and response. Eligibility and procedural requirements must be checked on the portal.")
add("pta", "PTA", "Telecom", "https://complaint.pta.gov.pk/userlogin.aspx", aliases=("pta", "پی ٹی اے"), channel="Complaint portal", scope="Telecom service, billing, SIM misuse and spam.", caveat="For a service dispute, retain the telecom operator's complaint reference. Online fraud/harassment also needs the cybercrime route; content-removal jurisdiction must be checked separately.")
add("pemra", "PEMRA / Council of Complaints", "Broadcasting", "https://www.pemra.gov.pk/contact/", aliases=("pemra", "پیمرا"), scope="Broadcast content, cable operators and channel-distribution complaints.", caveat="Include channel/operator, programme, date and time. A broadcast complaint is distinct from a social-media complaint.")
add("ogra", "OGRA", "Gas & petroleum", "https://complaint.ogra.org.pk/complaint", aliases=("ogra", "اوگرا"), channel="Complaint portal", scope="Gas billing/supply and regulated oil, LPG/CNG quality or quantity complaints.", caveat="For gas complaints, the portal requires an earlier attempt with the licensee and supporting records. Its filing window is not a promised resolution deadline.")
add("wafaqi", "Wafaqi Mohtasib (Federal Ombudsman)", "Federal administration", "https://complaints.mohtasib.gov.pk/", aliases=("wafaqi mohtasib", "federal ombudsman", "وفاقی محتسب"), channel="Complaint portal", scope="Maladministration by federal agencies within the Ombudsman's jurisdiction.", caveat="Not a universal appellate court. Matters pending in court, service matters and other statutory exclusions need eligibility review.")
add("fto", "Federal Tax Ombudsman (FTO)", "Tax administration", "https://fto.gov.pk/onlineComSys.aspx", aliases=("fto", "tax ombudsman", "ٹیکس محتسب"), channel="Official complaint gateway", scope="Tax-administration delay, harassment and maladministration.", caveat="Disputes over tax assessment, liability or customs valuation may belong in statutory tax appeals; FTO is not a substitute for those appeals.")
add("nccia", "NCCIA (Cybercrime; formerly FIA/NR3C route)", "Cybercrime", "https://www.nccia.gov.pk/", aliases=("nccia", "nr3c", "fia cybercrime", "ایف آئی اے", "سائبر کرائم"), scope="Online fraud, identity theft, hacking and cyber harassment.", caveat="Use the current NCCIA reporting channel linked on its website. Preserve original messages, URLs, dates and transaction references; do not alter evidence.")

for code, area, regions, aliases in [
    ("LESCO", "Lahore", ("Punjab",), ("لیسکو",)),
    ("IESCO", "Islamabad / Rawalpindi", ("Islamabad", "Punjab", "Azad Jammu and Kashmir"), ("آئیسکو", "آئیسکو")),
    ("FESCO", "Faisalabad", ("Punjab",), ("فیسکو",)),
    ("GEPCO", "Gujranwala", ("Punjab",), ("گیپکو",)),
    ("PESCO", "Peshawar", ("Khyber Pakhtunkhwa",), ("پیسکو",)),
    ("HESCO", "Hyderabad", ("Sindh",), ("حیسکو", "ہیسکو")),
    ("SEPCO", "Sukkur", ("Sindh",), ("سیپکو",)),
    ("QESCO", "Quetta", ("Balochistan",), ("کیسکو",)),
]:
    add(code.lower(), f"{code} - {area}", "Electricity", "https://ccms.pitc.com.pk/", regions=regions, aliases=(code.lower(), *aliases), escalation="nepra", channel="PITC complaint portal", scope="Billing, outages, meter and connection issues.", caveat="Confirm the distribution company printed on your bill; city examples are not complete service-area boundaries.")
add("ke", "K-Electric - Karachi", "Electricity", "https://ke.com.pk/contact-us/", regions=("Sindh", "Balochistan"), aliases=("k electric", "kelectric", "کے الیکٹرک"), escalation="nepra", scope="K-Electric customer-service complaints.", caveat="Confirm the supplier on your bill. Do not send K-Electric cases to the PITC DISCO portal.")
add("sngpl", "SNGPL - Sui Northern Gas", "Gas & petroleum", "https://www.sngpl.com.pk/", regions=("Punjab", "Khyber Pakhtunkhwa", "Islamabad", "Azad Jammu and Kashmir"), aliases=("sngpl", "سوئی ناردرن", "sui northern"), escalation="ogra", scope="SNGPL gas billing, supply, connection and leakage complaints.", caveat="Confirm your provider from the bill. Gilgit-Baltistan coverage is not assumed.")
add("ssgc", "SSGC - Sui Southern Gas", "Gas & petroleum", "https://www.ssgc.com.pk/web/?page_id=111824", regions=("Sindh", "Balochistan"), aliases=("ssgc", "ssgcl", "سوئی سدرن", "sui southern"), escalation="ogra", scope="SSGC gas billing, supply, connection and leakage complaints.", caveat="For urgent leakage use the utility's emergency channel; the draft workflow does not dispatch emergency help.")
add("fbr", "FBR / Customs administration", "Tax administration", "https://www.fbr.gov.pk/", aliases=("fbr", "customs", "ایف بی آر", "کسٹمز"), escalation="fto", scope="Identify the relevant tax office and retain refund/application records.")
add("federal-office", "Federal ministry / agency (specify office)", "Federal administration", "https://www.mohtasib.gov.pk/", escalation="wafaqi", scope="Name the federal agency, office and the administrative failure.", review_required=True)

OMBUDSMEN = {
    "Punjab": ("omb-punjab", "Mohtasib Punjab", "https://www.ombudsmanpunjab.gov.pk/"),
    "Sindh": ("omb-sindh", "Ombudsman Sindh", "https://www.mohtasibsindh.gov.pk/"),
    "Khyber Pakhtunkhwa": ("omb-kp", "KP Ombudsman", "https://ombudsmankp.gov.pk/"),
    "Balochistan": ("omb-balochistan", "Balochistan Ombudsman", "https://balochistan.gov.pk/citizen-services/"),
}
for region, (id, name, url) in OMBUDSMEN.items():
    add(id, name, "Provincial maladministration", url, regions=(region,), aliases=(name.lower(),), scope="Maladministration by eligible provincial agencies.", caveat="Check exclusions and whether the matter is already before a court. This is not an automatic appeal from every departmental decision.", review_required=region == "Balochistan")

PROVINCIAL_SOURCES = {
    "Punjab": "https://www.punjab.gov.pk/complaints",
    "Sindh": "https://www.sindh.gov.pk/",
    "Khyber Pakhtunkhwa": "https://kp.gov.pk/",
    "Balochistan": "https://balochistan.gov.pk/citizen-services/",
}
LOCAL_DOMAINS = {
    "Municipal & sanitation": ("Local Government / municipal office", "Garbage, drains, missing manhole covers and street lights."),
    "Water & sewerage": ("WASA / district water and sanitation office", "Water supply, water billing and sewerage."),
    "Police & public safety": ("District Police Office (DPO / CPO)", "FIR refusal, police misconduct or administrative inaction."),
    "Traffic & safe cities": ("Traffic Police / Safe City office", "Traffic signals, parking, traffic administration or camera complaints."),
    "Food safety": ("Food Authority", "Adulteration, expired food or unhygienic premises."),
    "Consumer rights & pricing": ("Consumer Protection Council / district consumer court", "Defective products, service disputes and pricing complaints."),
    "Revenue & land": ("Board of Revenue / Patwari / Tehsildar", "Land records, Fard, mutation and revenue-office delay."),
    "Health": ("Health Department / district health office", "Absent staff, missing medicines and public hospital service."),
    "Education": ("School Education Department / district education office", "School staff absence, public-school service or private-school fee regulation."),
}
POLICE_URLS = {
    "Punjab": "https://www.punjabpolice.gov.pk/igp_complaint_center_8787",
    "Sindh": "https://igpcms.sindhpolice.gov.pk/",
    "Khyber Pakhtunkhwa": "https://www.kppolice.gov.pk/detail.php?pid=45",
    "Balochistan": "https://pkm.balochistanpolice.gov.pk/",
}
FOOD_URLS = {
    "Punjab": "https://pfa.gop.pk/for-consumer/report-a-complaint/",
    "Sindh": "https://sfa.gos.pk/",
    "Khyber Pakhtunkhwa": "https://e.kpfsa.gov.pk/contact",
    "Balochistan": "https://bfa.gob.pk/",
}
for region in PROVINCES:
    prefix = {"Punjab": "punjab", "Sindh": "sindh", "Khyber Pakhtunkhwa": "kp", "Balochistan": "balochistan"}[region]
    for index, (category, (office, scope)) in enumerate(LOCAL_DOMAINS.items()):
        url = PROVINCIAL_SOURCES[region]
        aliases = ()
        if category in ("Police & public safety", "Traffic & safe cities"):
            url = POLICE_URLS[region]
        if category == "Food safety":
            url = FOOD_URLS[region]
            aliases = {"Punjab": ("pfa", "punjab food authority"), "Sindh": ("sfa", "sindh food authority"), "Khyber Pakhtunkhwa": ("kp-pfa", "kpfsa"), "Balochistan": ("bfa", "balochistan food authority")}[region]
            office += " (" + aliases[0].upper() + ")"
        add(f"{prefix}-{index}", f"{region} - {office}", category, url, regions=(region,), aliases=aliases, escalation=OMBUDSMEN[region][0], scope=scope, review_required=True,
            caveat="Specify the district and exact office. The link is a starting point; local territorial jurisdiction must be confirmed. Court claims and formal appeals have separate procedures.")

for id, name, category, region, city, url, aliases in [
    ("lwmc", "LWMC - Lahore Waste Management", "Municipal & sanitation", "Punjab", "Lahore", "https://www.lwmc.com.pk/", ("lwmc", "ایل ڈبلیو ایم سی")),
    ("rwmc", "RWMC - Rawalpindi Waste Management", "Municipal & sanitation", "Punjab", "Rawalpindi", "https://rwmc.org.pk/RWMC-files/Submit-Complaint.php", ("rwmc",)),
    ("sswmb", "SSWMB - Sindh Solid Waste Management Board", "Municipal & sanitation", "Sindh", "", "https://sswmb.gos.pk/portal/", ("sswmb", "sswma")),
    ("kwsc", "KW&SC - Karachi Water (formerly KWSB)", "Water & sewerage", "Sindh", "Karachi", "https://complain.kwsc.gos.pk/add/complaint", ("kwsc", "kwsb", "karachi water", "واٹر بورڈ")),
    ("lda", "LDA - Lahore Development Authority", "Revenue & land", "Punjab", "Lahore", "https://lda.gop.pk/", ("lda", "ایل ڈی اے")),
    ("rda", "RDA - Rawalpindi Development Authority", "Revenue & land", "Punjab", "Rawalpindi", "https://rda.gop.pk/", ("rda", "آر ڈی اے")),
    ("kda", "KDA - Karachi Development Authority", "Revenue & land", "Sindh", "Karachi", "https://www.kda.gos.pk/", ("kda", "کے ڈی اے")),
]:
    add(id, name, category, url, regions=(region,), aliases=aliases, escalation=OMBUDSMEN[region][0], locality=city, scope=LOCAL_DOMAINS[category][1], caveat="Confirm service-area coverage and the local office; a provincial ombudsman complaint remains subject to eligibility review.")
add("cda", "CDA - Capital Development Authority", "Revenue & land", "https://complaints.cda.gov.pk/", regions=("Islamabad",), aliases=("cda", "سی ڈی اے"), escalation="wafaqi", channel="Complaint portal", scope="CDA land, development and municipal service complaints.")
add("cda-municipal", "CDA - Municipal / water services", "Municipal & sanitation", "https://complaints.cda.gov.pk/", regions=("Islamabad",), escalation="wafaqi", channel="Complaint portal", scope="CDA sanitation, water, sewerage and street-light services.")
add("kp-rts", "KP Right to Public Services Commission", "Public service delays", "https://www.kprts.gov.pk/online-complaints/", regions=("Khyber Pakhtunkhwa",), aliases=("kp rts", "kprts", "کے پی آر ٹی ایس"), channel="Complaint gateway", scope="Delay, refusal or deficient delivery of notified public services.", caveat="Only notified services qualify. Confirm the designated officer, complete application date and applicable notification; there is no single deadline for all services.")
add("punjab-rts", "Punjab Right to Public Services - verification required", "Public service delays", "https://regulationswing.punjab.gov.pk/acts", regions=("Punjab",), aliases=("punjab rts",), scope="The Punjab Right to Public Services Act 2019 is listed in the official Acts directory.", caveat="A current operational Commission complaint portal and service notifications were not verified. Confirm these with the department before treating this as a statutory escalation route.", review_required=True)

CATEGORIES = list(dict.fromkeys(d.category for d in DEPARTMENTS.values()))


def available_departments(category, region):
    return [d for d in DEPARTMENTS.values() if d.category == category and (not d.regions or region in d.regions)]


def starter_documents():
    """Curated factual summaries are searchable alongside uploaded manuals."""
    return [{"name": d.name, "category": d.category, "department_id": d.id,
             "region": d.regions, "source": d.url, "reviewed": REVIEW_DATE,
             "text": f"{d.name}. {d.scope} {d.caveat}", "trusted": True}
            for d in DEPARTMENTS.values()]
