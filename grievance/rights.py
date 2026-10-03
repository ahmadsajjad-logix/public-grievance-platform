"""Issue-specific entitlements are distinct from an authority's general remit."""


def rights_for(department_id, provisions):
    if department_id == "pta":
        return [dict(text="PTA's responsibilities include protection of users' interests. For a particular billing or service entitlement, identify the applicable consumer regulation and licence conditions.", source="https://pakistancode.gov.pk/pdffiles/administratorcf6de2451af9e9d016e5fef2ac7e1562.pdf", citation="Telecommunication Act 1996, section 6")]
    if department_id == "nccia":
        return [dict(text="You can report suspected electronic offences through NCCIA's official complaint channel. Reporting does not guarantee FIR registration or a particular outcome.", source="https://complaint.nccia.gov.pk/", citation="Official complaint mechanism")]
    if department_id == "wafaqi":
        return [dict(text="An eligible complainant may seek investigation of federal-agency maladministration, subject to the Order's exclusions and admissibility rules.", source="https://mohtasib.gov.pk/SiteImage/Downloads/presidential_order_1983.pdf", citation="1983 Order, Article 9")]
    if provisions:
        return [dict(text=p["purpose"], source=p["source"], citation=p["citation"]) for p in provisions]
    from .guidance import PROFILES
    profile = PROFILES.get(department_id)
    if profile:
        return [dict(text="Available complaint mechanism: " + profile["can"] + " Eligibility and any enforceable remedy depend on the framework and exclusions below.", source=profile["sources"][0], citation="Official scope and complaint instructions")]
    return []
