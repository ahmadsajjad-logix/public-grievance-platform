"""Public-record request preparation; separate from service complaints."""
CHECKED = "2026-10-04"
PROFILES = {
    "Federal public body": dict(
        law="Right of Access to Information Act, 2017",
        source="https://rti.gov.pk/SiteImage/Misc/files/The-Right-of-Access-to-Information-Act-2017-Gazette.pdf",
        forum="Pakistan Information Commission",
        link="https://rti.gov.pk/Detail/Nzk3ZDQ1NzgtODE3Mi00YzliLWJkNjgtMWQyZWI3NzhiMDkx",
        label="Open federal RTI appeal instructions",
        procedure="Apply to the designated official of the federal public body first. For an appeal, retain the request and delivery receipt and follow PIC's post/email instructions, including its declaration about other forums.",
        limits="The ordinary response period is 10 working days, with a possible further 10-working-day extension. Appeal timing depends on the response or expiry of the applicable period; check the Act and current instructions. No automatic deadline is calculated."),
    "Punjab public body": dict(
        law="Punjab Transparency and Right to Information Act, 2013",
        source="https://pshealthpunjab.gov.pk/Upload/RTI/RTIINFO.pdf",
        forum="Punjab Information Commission",
        link="https://rti.punjab.gov.pk/",
        label="Open Punjab Information Commission website",
        procedure="Request the records from the public information officer of the relevant Punjab body. If dissatisfied, check the Act's internal-review and Commission complaint routes and preserve proof of your request.",
        limits="The commission website is listed by the Punjab government; its current online complaint form was not verified. Confirm filing instructions and applicable time limits before submission."),
    "Sindh public body": dict(
        law="Sindh Transparency and Right to Information Act, 2016",
        source="https://www.bbshrrdb.gos.pk/downloads/STRIACT.pdf",
        forum="Sindh Information Commission",
        link="https://rti.sindh.gov.pk/application-procedure",
        label="Open Sindh RTI application procedure",
        procedure="Send the information request to the designated official of the Sindh public body. Consult the Act and official application procedure for review and Commission complaints; retain the response and proof of delivery.",
        limits="The application-procedure page was indexed but unavailable during direct review. Live form fields and current receiving-office details require confirmation."),
    "Khyber Pakhtunkhwa public body": dict(
        law="Khyber Pakhtunkhwa Right to Information Act, 2013, as amended",
        source="https://www.kprti.gov.pk/downloads/",
        forum="KP Information Commission",
        link="https://www.kprti.gov.pk/online-complaints/",
        label="Open KP RTI online complaint",
        procedure="Request information from the public body first. KPIC's online instructions allow a complaint where information has not been provided within 10 working days; upload the information request, receipt and CNIC as the official portal requires.",
        limits="Check applicable extensions, exemptions and amendments in the Act. This app's optional uploads do not waive the Commission's own filing requirements."),
    "Balochistan public body": dict(
        law="Balochistan Right to Information framework and Right of Information Rules, 2022",
        source="https://balochistan.gov.pk/information-department-downloads/information-department-rules/",
        forum="Competent Balochistan RTI authority — receiving office requires verification",
        link="https://balochistan.gov.pk/information-department-downloads/information-department-rules/",
        label="Open Balochistan RTI rules directory",
        procedure="Identify the designated information official in the public body and request the records. Confirm the current Commission/complaint receiving office and prescribed process before seeking review.",
        limits="A functioning official online RTI complaint endpoint was not verified. The rules directory is a reference page, not a complaint form."),
    "AJK / Gilgit-Baltistan / unsure": dict(
        law="Applicable territorial information-access law requires verification",
        source="https://rti.gov.pk/",
        forum="Determine the public body's legal jurisdiction first",
        link="https://rti.gov.pk/",
        label="Open federal information commission reference",
        procedure="Identify whether the record holder is a federal body or a territorial institution. Your residential location alone does not determine the applicable RTI law. Confirm the local law and receiving official for a territorial body.",
        limits="Do not assume the federal or a provincial RTI Act applies to a territorial institution. A jurisdiction-specific draft cannot be generated until the law is confirmed."),
}


def request_draft(jurisdiction, body, records, period, delivery):
    if jurisdiction == "AJK / Gilgit-Baltistan / unsure":
        raise ValueError("Confirm the public body's legal jurisdiction before preparing a statutory RTI request.")
    if not body.strip() or not records.strip():
        raise ValueError("Enter the public body and the records you want.")
    profile = PROFILES[jurisdiction]
    return (f"To: The designated Public Information Officer / Designated Official\n{body.strip()}\n\n"
            f"Subject: Request for records under {profile['law']}\n\n"
            f"Please provide access to the following records held by your public body:\n{records.strip()}\n\n"
            f"Period covered: {period.strip() or '[specify relevant dates]'}\n"
            f"Preferred access: {delivery}\n\n"
            "Please inform me of any applicable reproduction charges before incurring them. If access is refused in whole or part, please communicate the decision, the applicable legal basis and the available review procedure.\n\n"
            "Applicant: [complete as required by the receiving body]\nContact / correspondence address: [complete before filing]\nDate and signature: [complete before filing]\n\n"
            f"Reference: {profile['source']}\nDraft for review; not submitted.")


def render(st):
    st.subheader("Right to Information (RTI)")
    st.write("Request public records such as rules, expenditure, application status records, inspection reports or recorded reasons for a decision. RTI obtains information; a service remedy or FIR follows a separate process.")
    st.caption("Choose the government responsible for the record-holding body, not simply your home province. Access is subject to the applicable law and its exemptions.")
    jurisdiction = st.selectbox("Who holds the records?", list(PROFILES))
    profile = PROFILES[jurisdiction]
    st.markdown("**Legal framework:** " + profile["law"])
    st.markdown(f"[Official framework source]({profile['source']})")
    st.write(profile["procedure"])
    st.write("Review / complaint forum: " + profile["forum"])
    st.link_button(profile["label"], profile["link"])
    st.info(profile["limits"])
    st.caption(f"Sources reviewed {CHECKED}. Keep your request, delivery receipt, refusal and earlier correspondence.")
    st.subheader("Prepare an information request")
    body = st.text_input("Public body / office holding the records", key="rti_body")
    records = st.text_area("Records requested — list each item precisely", key="rti_records", help="For example: copies of the inspection report and action-taken record for complaint ABC. Specify existing records rather than asking the official to create an opinion.")
    period = st.text_input("Dates or period covered", key="rti_period")
    delivery = st.selectbox("Preferred access", ["Electronic copies", "Paper copies", "Inspection of records"], key="rti_delivery")
    if body.strip() and records.strip():
        try:
            draft = request_draft(jurisdiction, body, records, period, delivery)
        except ValueError as exc:
            st.warning(str(exc))
        else:
            st.text_area("Request draft — review before filing", value=draft, height=300)
            st.download_button("Download RTI request draft", draft, "rti-request.txt", "text/plain")
    st.caption("Complete the official body's identity/contact requirements when filing. No request is sent automatically.")
