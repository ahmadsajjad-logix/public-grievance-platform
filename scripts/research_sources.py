"""Bounded official-source discovery for every directory entry.

Run from the project root: python -m scripts.research_sources
Results are research candidates, never automatically approved legal advice.
No complaint or user identity is sent to these websites.
"""
import concurrent.futures
import hashlib
import io
import json
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen

from grievance.catalog import DEPARTMENTS

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 4_000_000
INTEREST = re.compile(r"legal|regulation|ordinance|\bact\b|complaint|contact|jurisdiction|procedure|consumer|whatsapp", re.I)
EXCLUDE = re.compile(r"/uploads/|decision|findings|tender|career|login|logout", re.I)
SEEDS = {
    "nepra": ["https://nepra.org.pk/Legal.php"],
    "pta": ["https://complaint.pta.gov.pk/Usermanual/User_Manual_CMS_Web.pdf", "https://www.pta.gov.pk/"],
    "pemra": ["https://www.pemra.gov.pk/coc/", "https://www.pemra.gov.pk/isb/"],
    "wafaqi": ["https://www.mohtasib.gov.pk/", "https://mohtasib.gov.pk/SiteImage/Downloads/presidential_order_1983.pdf"],
    "kp-rts": ["https://www.kprts.gov.pk/", "https://erts.kprts.gov.pk/complaint/public_complaint"],
}


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text, self.links, self.hidden = [], [], 0
        self.link = None

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.hidden += 1
        if tag == "a":
            self.link = [dict(attrs).get("href", ""), ""]

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.hidden = max(0, self.hidden - 1)
        if tag == "a" and self.link:
            self.links.append(self.link)
            self.link = None

    def handle_data(self, data):
        if not self.hidden:
            self.text.append(data.strip())
            if self.link:
                self.link[1] += data


def fetch(url, allowed_host):
    try:
        # Redirects are checked before any follow-up request to another host.
        from urllib.request import HTTPRedirectHandler, build_opener
        class SameHost(HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                if urlsplit(newurl).hostname != allowed_host:
                    raise ValueError("Cross-host redirect needs source review")
                return super().redirect_request(req, fp, code, msg, headers, newurl)
        req = Request(url, headers={"User-Agent": "CivicAccess-SourceReview/1.0", "Accept": "text/html,application/pdf"})
        with build_opener(SameHost()).open(req, timeout=12) as response:
            raw = response.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                raise ValueError("Document exceeds research download limit")
            content_type = response.headers.get_content_type()
        links = []
        if content_type == "application/pdf" or raw.startswith(b"%PDF"):
            from pypdf import PdfReader
            text = "\n".join(p.extract_text() or "" for p in PdfReader(io.BytesIO(raw)).pages[:100])
        elif content_type in ("text/html", "text/plain"):
            page = Page()
            page.feed(raw.decode("utf-8", errors="replace"))
            text = "\n".join(t for t in page.text if t)
            for href, label in page.links:
                candidate = urljoin(url, href).split("#")[0]
                if (urlsplit(candidate).scheme == "https" and urlsplit(candidate).hostname == allowed_host
                        and INTEREST.search(label + " " + href) and not EXCLUDE.search(candidate)):
                    links.append({"url": candidate, "title": label.strip()})
        else:
            raise ValueError("Unsupported source format")
        return {"url": url, "status": "fetched_unreviewed", "sha256": hashlib.sha256(raw).hexdigest(),
                "text": text[:100000], "links": links[:60]}
    except Exception as exc:
        return {"url": url, "status": "unavailable", "error": type(exc).__name__ + ": " + str(exc)[:180]}


def research(url):
    host = urlsplit(url).hostname
    first = fetch(url, host)
    pages = [first]
    unique = list(dict.fromkeys(link["url"] for link in first.get("links", []) if link["url"] != url))
    for candidate in unique[:3]:
        pages.append(fetch(candidate, host))
    return pages


def main():
    by_url = {}
    for d in DEPARTMENTS.values():
        for url in [d.url, *SEEDS.get(d.id, [])]:
            by_url.setdefault(url, []).append(d.id)
    records = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        tasks = {pool.submit(research, url): url for url in by_url}
        for task in concurrent.futures.as_completed(tasks):
            url = tasks[task]
            for result in task.result():
                result["department_ids"] = by_url[url]
                records.append(result)
            print(f"Reviewed source access {len(records)}: {url}", flush=True)
    stamp = datetime.now(timezone.utc).isoformat()
    corpus = ROOT / "data" / "research_candidates.json"
    corpus.write_text(json.dumps({"checked_at": stamp, "records": records}, ensure_ascii=False, indent=2), encoding="utf-8")
    # Public metadata is safe to commit; downloaded source text stays local until review.
    public = [{k: v for k, v in r.items() if k != "text"} for r in records]
    (ROOT / "data" / "source_access_report.json").write_text(json.dumps({"checked_at": stamp, "records": public}, indent=2), encoding="utf-8")
    print(f"{len(DEPARTMENTS)} directory entries; {len(by_url)} seed URLs; {len(records)} access results")


if __name__ == "__main__":
    main()
