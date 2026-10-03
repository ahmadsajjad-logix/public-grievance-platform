"""Display official filing routes without treating information pages as forms."""
from urllib.parse import urlsplit


def complaint_links(guide):
    links = []
    seen = set()
    for item in guide["channels"]:
        kind, value = item["kind"], item["value"]
        if kind == "whatsapp":
            digits = "".join(c for c in value if c.isdigit())
            if not digits:
                continue
            url, label = "https://wa.me/" + digits, "Open official WhatsApp contact"
        elif kind in ("form", "portal", "website", "directory"):
            url = value
            label = {"form": "Open official complaint form", "portal": "Open official complaint portal", "website": "Open official complaint instructions", "directory": "Find the responsible office"}[kind]
        else:
            continue
        parsed = urlsplit(url)
        if parsed.scheme not in ("https", "http") or not parsed.netloc or url in seen:
            continue
        seen.add(url)
        links.append(dict(url=url, label=item.get("label", label), kind=kind,
                          instructions=item["instructions"], source=item["source"],
                          checked=item.get("checked")))
    priority = {"form": 0, "portal": 1, "whatsapp": 2, "website": 3, "directory": 4}
    return sorted(links, key=lambda item: priority[item["kind"]])
