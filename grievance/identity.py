"""Input format checks only; no identity lookup or external transmission."""
import re
from datetime import date


def validate_identity(cnic, expiry, mobile):
    cnic = cnic.strip()
    if not re.fullmatch(r"(?:[0-9]{13}|[0-9]{5}-[0-9]{7}-[0-9])", cnic):
        raise ValueError("Enter a 13-digit CNIC number, with or without hyphens.")
    if not isinstance(expiry, date):
        raise ValueError("Enter the CNIC expiry date printed on your card.")
    mobile = re.sub(r"[\s-]", "", mobile.strip())
    if re.fullmatch(r"\+923[0-9]{9}", mobile):
        mobile = "0" + mobile[3:]
    if not re.fullmatch(r"03[0-9]{9}", mobile):
        raise ValueError("Enter a mobile number as 03XXXXXXXXX or +923XXXXXXXXX.")
    digits = cnic.replace("-", "")
    return {"cnic": f"{digits[:5]}-{digits[5:12]}-{digits[12]}",
            "cnic_expiry": expiry.isoformat(), "mobile": mobile}
