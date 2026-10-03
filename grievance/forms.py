"""Reviewed public form fields. No portal automation or credential collection."""
from copy import deepcopy

CHECKED = "2026-10-03"


def field(label, help, value_key=None):
    return dict(label=label, help=help, value_key=value_key)


FORMS = {
    "nccia": dict(url="https://complaint.nccia.gov.pk/", fields=[
        field("Full Name *", "Your name as shown on your identity document."),
        field("CNIC *", "Enter your 13-digit CNIC in the portal's requested format."),
        field("Gender *", "Choose the appropriate option yourself."),
        field("Mobile Number *", "Use a reachable number you control."),
        field("Email Address", "A contact email, if supplied."),
        field("Occupation", "Select your occupation if supplied."),
        field("Postal Address", "Your correspondence address."),
        field("City *", "Select the relevant city; clarify incident location in details."),
        field("Crime Category *", "Choose the closest factual category; it is not a final charge."),
        field("Crime Details *", "State what happened, dates, accounts/URLs, loss and evidence available.", "narrative"),
        field("Captcha", "Complete on the official site yourself."),
        field("Truth declaration", "Read and affirm only if accurate; then submit yourself."),
    ], note="An acknowledgment confirms a complaint was received, not that an FIR has been registered."),
    "nepra": dict(url="https://nepra.org.pk/CAD-Database/CMS-CAD/cregister.php", fields=[
        field("Issue pending since *", "Use the actual start date."),
        field("Earlier DISCO complaint", "Answer accurately; approach SDO/XEN first."),
        field("Results *", "Give the earlier reference and response.", "prior_reference"),
        field("Documents", "Published limit: PDF/JPG, 2.5 MB; check current instructions."),
        field("CNIC / Name *", "Use your identity details on the official form."),
        field("Address / City / Province *", "Use the relevant service location and contact address."),
        field("Cell No * / E-mail", "Provide reachable contact details."),
        field("Consumer category *", "Choose Existing, New or KE as appropriate."),
        field("Account/Reference/Consumer No *", "Copy from the relevant bill/application.", "reference"),
        field("DISCO/Licensee *", "Select the supplier being complained about."),
        field("Nearest NEPRA Complaint Office *", "Select the appropriate office from current options."),
        field("Main points *", "Give facts and requested correction.", "complaint"),
        field("Affidavit / CAPTCHA", "Read every declaration; do not affirm an inaccurate statement. Complete CAPTCHA yourself."),
    ], note="The form contains differing messages about older-than-one-year complaints; seek written guidance from DG Consumer Affairs rather than assuming an exception."),
    "kwsc": dict(url="https://complain.kwsc.gos.pk/add/complaint", fields=[
        field("Consumer # on BILL", "Copy the account identifier if available.", "reference"),
        field("Applicant Name *", "Enter the complainant's name."),
        field("Applicant Phone Number *", "Follow the displayed +92 format."),
        field("Applicant Email", "Provide if available."),
        field("Town * / UC or Mohalla *", "Select where the service problem occurs."),
        field("Applicant Person Address", "Provide the address needed to locate the issue."),
        field("Nearest Land Mark *", "Use a recognisable nearby landmark."),
        field("Complaint Type * / Grievance *", "Choose the relevant service issue."),
        field("Description *", "Maximum 350 characters: issue, location and action requested.", "short_description"),
        field("Picture", "Use relevant photo evidence; this is not a verified PDF attachment field."),
    ], note="Keep the full petition separately. Submit the official form yourself and retain acknowledgment."),
}

GENERAL_FIELDS = [
    field("Identity and contact fields", "Use the authority's requested format; mandatory fields can differ from this app."),
    field("Department / service / account", "Confirm the provider and service reference before filing.", "reference"),
    field("Complaint / details", "Review and copy your factual account with the requested action.", "complaint"),
    field("Earlier complaint reference", "Use the actual acknowledgment if escalating.", "prior_reference"),
    field("Attachments", "Attach the petition only if the portal accepts it; follow its current size/type limits."),
    field("Declaration / verification / submit", "Review, complete any OTP or CAPTCHA and submit yourself."),
]


def form_guide(department_id):
    specific = FORMS.get(department_id)
    return deepcopy(dict(specific, verified=True, reviewed=CHECKED) if specific else dict(
        fields=GENERAL_FIELDS, verified=False, reviewed=None, url="",
        note="General preparation help only. This department's exact form fields have not yet been reviewed; follow its live instructions."))


def form_values(case):
    """Only copyable case content, no automatic CNIC/phone/name transmission."""
    from .agents import filing_text
    return dict(narrative=case["intake"]["text"], complaint=filing_text(case),
                reference=case.get("reference", ""), prior_reference=case["route"].get("prior_reference", ""))


def form_text(department_id):
    guide = form_guide(department_id)
    lines = ["Official form assistance", guide["note"], "Form: " + (guide["url"] or "Confirm on the authority website")]
    lines += [f"{f['label']}: {f['help']}" for f in guide["fields"]]
    return "\n\n".join(lines)
