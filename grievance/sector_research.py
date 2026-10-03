"""Operator-first telecom and banking guidance, checked 4 October 2026.

Official channels and framework references are not findings of a legal breach.
Banking Mohtasib and SBP are separate forums, not an automatic appeal ladder.
"""
from copy import deepcopy
from .department_research import add, law, route

CHECKED = "2026-10-04"
SUNWAI = "https://sunwai.sbp.org.pk/"
BMP = "https://www.bankingmohtasib.gov.pk/Website/preComplaintForm.aspx"
BMP_LAW = "https://www.bankingmohtasib.gov.pk/website/WebPages.aspx?enc_+=wYtMASFXrZxCFcRk3IiEVu4CzVkNTnGAD3IcvjbKIujQLrHxvntjzbjmNkFYvoO3"
BMP_CHANGE = "https://www.bankingmohtasib.gov.pk/Documents/PressRelease12-Nov-2024-EN.pdf"
SBP = "https://www.sbp.org.pk/our-operations/consumer-protection"
TELECOM_ACT = "https://pakistancode.gov.pk/pdffiles/administratorcf6de2451af9e9d016e5fef2ac7e1562.pdf"
PTA_PROCEDURE = "https://www.pta.gov.pk/category/public-complaints-resolution-mechanism-407381753-2023-05-30"

# id, public service brand, official support gateway, aliases, channel type
OPERATORS = [
    ("jazz", "Jazz", "https://jazz.com.pk/help/help/contact-us", ("jazz", "mobilink", "warid", "جاز", "موبی لنک"), "form"),
    ("zong", "Zong / CMPak", "https://complaint.zong.com.pk/CustomerComplaint", ("zong", "cmpak", "زونگ"), "portal"),
    ("ufone", "Ufone / PTML", "https://www.ufone.com/selfcare/app/complaints/log-complaint.php", ("ufone", "یوفون", "یو فون"), "portal"),
    ("telenor", "Telenor Pakistan", "https://www.telenor.com.pk/faqs/offers/", ("telenor", "ٹیلی نار", "ٹیلینور"), "website"),
    ("onic", "Onic — PTML digital brand", "https://onic.pk/help-center", ("onic", "اونک"), "website"),
    ("ptcl", "PTCL / Flash Fiber", "https://ptcl.com.pk/Home/PageDetail?ItemId=285", ("ptcl", "flash fiber", "flashfiber", "پی ٹی سی ایل"), "website"),
    ("scom", "SCOM / SCO — AJK and Gilgit-Baltistan", "https://apps.sco.gov.pk/dgportal", ("scom", "sco", "ایس کام", "ایس سی او"), "portal"),
]


def register_departments(register):
    for id, name, url, aliases, kind in OPERATORS:
        register(id, name, "Telecom", url, aliases=aliases,
                 regions=("Azad Jammu and Kashmir", "Gilgit-Baltistan") if id == "scom" else (),
                 escalation="" if id == "scom" else "pta",
                 channel={"form": "Complaint form", "portal": "Complaint portal", "website": "Official support page"}[kind],
                 scope="Provider complaints about connectivity, billing, activation and customer service.",
                 caveat="Complain to the provider first and keep the ticket. Mobile-wallet transactions require the financial provider's complaint route. " +
                 ("Confirm territorial jurisdiction before escalation from AJK/GB; SCO's DG portal is a supervisory channel." if id == "scom" else "PTA escalation is subject to eligibility and the earlier operator response."))
    register("banking-mohtasib", "Banking Mohtasib (Ombudsman) Pakistan", "Banking", BMP,
             aliases=("banking mohtasib", "banking ombudsman", "bmp", "بینکنگ محتسب"), channel="Complaint form",
             scope="Eligible complaints against commercial banks after approaching the bank.",
             caveat="Microfinance banks and other excluded institutions are outside BMP's complaint jurisdiction. SBP is not a general appeal from BMP decisions.")
    register("sbp", "State Bank of Pakistan (SBP)", "Banking", SUNWAI,
             aliases=("sbp", "state bank", "اسٹیٹ بینک", "سٹیٹ بینک"), channel="Sunwai complaint portal",
             scope="Banking regulator; Sunwai routes complaints to the financial institution, BMP or SBP as appropriate.",
             caveat="Start with the financial institution. SBP handles specified cases, including microfinance complaints; check eligibility rather than escalating every BMP case to SBP.")


def extend(profiles):
    framework = [law("Pakistan Telecommunication (Re-organization) Act, 1996, sections 3–6", TELECOM_ACT,
                     "PTA's regulatory responsibilities include users' interests; establish the applicable licence, regulation and facts for a specific breach."),
                 law("PTA public complaints resolution mechanism", PTA_PROCEDURE,
                     "Seek operator redress first and retain the complaint reference for an eligible unresolved complaint to PTA.")]
    contracts = {
        "jazz": ("Jazz subscriber terms and conditions", "https://jazz.com.pk/assets/documents/Terms-Conditions.pdf"),
        "zong": ("Zong subscriber terms and conditions", "https://www.zong.com.pk/terms-and-conditions"),
        "ufone": ("Ufone Code of Commercial Practice; Telecom Consumer Protection Regulations 2009, regulations 10 and 11", "https://www.ufone.com/code-of-commercial-practice/"),
    }
    for id, name, url, aliases, kind in OPERATORS:
        laws = deepcopy(framework)
        if id in contracts:
            title, source = contracts[id]
            laws.append(law(title, source, "Consult the published consumer terms, billing disclosures and complaint provisions alongside the terms of the subscribed package; establish the relevant version."))
        if id == "scom":
            laws = [law("SCO customer support policy; territorial applicability requires confirmation", "https://www.sco.gov.pk/sco-policy", "Use SCO support for its AJK/GB services. Confirm the applicable regional law and licence before relying on federal telecom provisions or choosing an external forum.")]
        channels = [route(kind, url)]
        if id == "jazz":
            channels.append(route("phone", "111 (Jazz prepaid); 042-111-300-300 (other networks)", url))
        elif id == "zong":
            channels.append(route("phone", "310", "https://www.zong.com.pk/about-zong/zong-complaints"))
        elif id == "ufone":
            channels += [route("phone", "0331-1333100", "https://www.ufone.com/support/"),
                         route("whatsapp", "https://wa.me/923311333100", "https://www.ufone.com/support/"),
                         route("email", "customercare@ufone.com", "https://www.ufone.com/support/")]
        elif id == "telenor":
            channels.append(route("phone", "345 / 042-111-345-100", url, "You can also register a complaint in My Telenor App."))
        elif id == "onic":
            channels.append(route("email", "happiness@onic.pk", url, "Use Onic web/app chat for PTML's Onic brand."))
        elif id == "ptcl":
            channels.append(route("phone", "1218", "https://charji.ptcl.com.pk/coverage", "PTCL support. The main contact-directory page timed out during review; unverified WhatsApp/email details are not listed."))
        elif id == "scom":
            channels.insert(0, route("phone", "355 (from SCOM)", "https://www.sco.gov.pk/sco-policy", "Start with customer support; retain its reference before using the DG portal."))
        add(profiles, id, f"{name}: service activation, network faults, billing and account-service complaints.",
            "This route concerns telecom services. Wallet transfers, deposits and banking disputes belong with the financial institution; criminal fraud may also need NCCIA. Refunds and compensation are not guaranteed.",
            laws, channels,
            ["Identify the provider, affected number/account, issue location, dates and requested remedy.",
             "Use the provider's complaint channel. Record the ticket, date and response; complete any verification yourself.",
             "For an unresolved operator complaint, consult PTA eligibility and provide the operator ticket and response." if id != "scom" else "Use SCO's DG complaint portal for supervisory redress. Verify the competent external forum for the AJK/GB service before escalation."],
            ["Affected service number, contact details and service location", "Disputed package/bill, fault dates and earlier ticket if available"],
            "No universal disposal deadline is asserted. Applicable package terms, licence, consumer regulations and territorial jurisdiction must be checked. " +
            ("An operator-specific contract was not verified in this review." if id not in contracts else "Read the linked provider terms for your service."))
    banking_laws = [law("Banking Companies Ordinance 1962, Part IVA, sections 82A–82E", BMP_LAW,
                        "Defines BMP jurisdiction, eligible banking-service grievances, procedure and remedies. A complaint is not an automatic finding of bank liability."),
                    law("Banking Companies (Amendment) Act 2024: section 82D(2), BMP notice of 12 November 2024", BMP_CHANGE,
                        "The notice replaces the former 45-day periods with 30 days for bank response and a further 30-day filing period, subject to the statutory conditions and condonation provision.")]
    add(profiles, "banking-mohtasib", "Consider eligible commercial-bank service complaints, including unauthorized debits, transfer delays and failure to follow banking requirements.",
        "Excluded categories include microfinance banks, DFIs and investment/insurance companies. Pending or decided court matters and bank pricing/risk policy challenges face exclusions. BMP cannot compel a new loan.",
        banking_laws, [route("form", BMP), route("portal", SUNWAI, "https://sunwai.sbp.org.pk/about-us.html", "Use guided routing; first complaints go to the bank."),
                      route("website", "https://www.bankingmohtasib.gov.pk/website/WebPages.aspx?lang=E&pageid=17", instructions="Official English/Urdu paper forms and filing instructions.")],
        ["Write to the bank first, describe the transaction and requested remedy, and retain its acknowledgment and response.",
         "Check BMP's admissibility questions truthfully before continuing to its online complaint form.",
         "Provide the relevant bank correspondence, transaction record and required declarations. Save the BMP reference.",
         "For a BMP decision, consult its Review and Representation guidance; do not treat SBP as an automatic appellate forum."],
        ["Bank/branch, transaction details, dates and relief sought", "Identity/contact details, bank complaint and response, relevant records and portal declarations"],
        "BMP's November 2024 notice specifies 30 days plus a further 30-day filing period under amended section 82D(2). Some official pages still reproduce 45 days. Confirm the trigger and current requirements with BMP; the app does not calculate a statutory deadline.")
    review_url = "https://www.bankingmohtasib.gov.pk/website/WebPages.aspx?lang=E&pageid=21"
    profiles["banking-mohtasib"]["channels"].append(route("website", review_url, instructions="Review/representation of a BMP decision uses the applicable FOIRA procedure."))
    profiles["banking-mohtasib"]["sources"].append(review_url)
    add(profiles, "sbp", "Regulatory consumer protection and complaints assigned to SBP, including microfinance-bank matters; Sunwai provides institution-aware routing.",
        "SBP is not a universal appeal from BMP. Commercial-bank complaints normally start at the bank and may qualify for BMP. Institutions outside banking regulation require their own regulator.",
        [law("SBP CPD Circular No. 01 of 2023 — Sunwai complaint management service", "https://www.sbp.org.pk/circulars/cpd-circular-no-01-of-2023", "Provides the official channel for complaints against banks, MFBs and DFIs; routing depends on the institution and complaint."),
         law("SBP consumer grievance handling and complaint jurisdiction guidance", SBP, "Financial institutions must maintain complaint handling arrangements. Check which unresolved cases fall to BMP or SBP.")],
        [route("portal", SUNWAI, "https://sunwai.sbp.org.pk/about-us.html"), route("website", SBP)],
        ["Register with Sunwai and select the actual financial institution and complaint type in that official portal.",
         "File with the institution first; retain the reference and response. Follow Sunwai's questions to determine BMP or SBP eligibility.",
         "Describe disputed transactions and the remedy sought. Review the form and submit it yourself; save the acknowledgment."],
        ["Institution/branch, complaint narrative, transaction dates and references", "Portal registration identity/contact details and earlier complaint record when applicable"],
        "Time limits depend on the complaint and forum. Do not apply the commercial-bank BMP waiting period to every institution or treat a service target as an appeal deadline.")
    # All newly researched entries carry their own date, preserving older dates.
    for id in [*(row[0] for row in OPERATORS), "banking-mohtasib", "sbp", "mepco", "tesco", "hazeco"]:
        profiles[id]["reviewed"] = CHECKED
        for channel in profiles[id]["channels"]:
            channel["checked"] = CHECKED
    profiles["hazeco"]["channels"].append(route("website", "https://hazeco.com.pk/contact", instructions="Official HAZECO contact page; confirm your supplier from the bill."))
    profiles["hazeco"]["sources"].append("https://hazeco.com.pk/contact")
