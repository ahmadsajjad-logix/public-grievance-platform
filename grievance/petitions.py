"""Embedded, licensed fonts and per-line RTL shaping for portable Urdu PDFs."""
import io
import re
from html import escape
from pathlib import Path
from threading import Lock

_FONT_LOCK = Lock()
_RENDER_LOCK = Lock()
ARABIC = re.compile(r"[\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff\ufb50-\ufeff]")


def preview_pages(pdf):
    """PDFium is not thread-safe; serialize rendering across visitor sessions."""
    import pypdfium2
    images = []
    with _RENDER_LOCK, pypdfium2.PdfDocument(pdf) as document:
        for index in range(len(document)):
            page = document[index]
            bitmap = page.render(scale=1.3)
            try:
                output = io.BytesIO()
                bitmap.to_pil().save(output, format="PNG")
                images.append(output.getvalue())
            finally:
                bitmap.close()
                page.close()
    return images


def register_fonts():
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    with _FONT_LOCK:
        if "CivicLatin" not in pdfmetrics.getRegisteredFontNames():
            root = Path(__file__).resolve().parents[1] / "assets" / "fonts"
            pdfmetrics.registerFont(TTFont("CivicLatin", str(root / "NotoSans-Regular.ttf")))
            pdfmetrics.registerFont(TTFont("CivicUrdu", str(root / "NotoNaskhArabic-Regular.ttf")))


def visual_runs(text):
    import arabic_reshaper
    from bidi.algorithm import get_display
    visual = get_display(arabic_reshaper.reshape(text), base_dir="R")
    runs = []
    for char in visual:
        font = "CivicUrdu" if ARABIC.match(char) else "CivicLatin"
        if runs and runs[-1][0] == font:
            runs[-1] = (font, runs[-1][1] + char)
        else:
            runs.append((font, char))
    return runs


def rtl_lines(text, width, size=12):
    from reportlab.pdfbase.pdfmetrics import stringWidth
    def measured(value):
        return sum(stringWidth(run, font, size) for font, run in visual_runs(value))
    lines = []
    for paragraph in text.splitlines() or [text]:
        line = ""
        for word in paragraph.split():
            candidate = f"{line} {word}".strip()
            if line and measured(candidate) > width:
                lines.append(line)
                line = ""
            # Also bound long unbroken identifiers/URLs.
            if measured(word) > width:
                for char in word:
                    if line and measured(line + char) > width:
                        lines.append(line)
                        line = ""
                    line += char
            else:
                line = f"{line} {word}".strip()
        lines.append(line)
    return lines


def build_petition(case):
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Flowable
    from reportlab.pdfbase.pdfmetrics import stringWidth
    register_fonts()

    class UrduLine(Flowable):
        def __init__(self, value):
            super().__init__()
            self.runs = visual_runs(value)
            self.height = 23
        def wrap(self, availWidth, availHeight):
            self.width = availWidth
            return self.width, self.height
        def draw(self):
            x = self.width - sum(stringWidth(run, font, 12) for font, run in self.runs)
            self.canv.setFillColor(HexColor("#172b3a"))
            for font, run in self.runs:
                self.canv.setFont(font, 12)
                self.canv.drawString(x, 6, run)
                x += stringWidth(run, font, 12)

    styles = getSampleStyleSheet()
    for style in styles.byName.values():
        style.fontName = "CivicLatin"
        if hasattr(style, "leading"):
            style.leading = max(style.leading, 15)
    route = case["route"]
    sections = [
        ("Title", "DRAFT - Public service grievance"),
        ("Normal", f"To: {route['body']}"),
        ("Normal", f"Concerning: {route.get('department', route['body'])}"),
        ("Normal", f"Date: {case['created'].date()} | Stage: {route.get('stage', 'First complaint')}"),
        ("Normal", f"Applicant: {case['name'] or 'To be supplied'}"),
        *[("Normal", f"{label}: {case['identity'][key]}")
          for key, label in (("cnic", "CNIC"), ("cnic_expiry", "CNIC expiry date"), ("mobile", "Mobile"))
          if case.get("identity")],
        ("Normal", f"Location: {case.get('city', '')}, {case['region']}"),
        ("Heading2", "Statement of grievance / شکایت کی تفصیل"),
        ("Normal", case["intake"]["text"]),
        ("Heading2", "Requested remedy / مطلوبہ حل"), ("Normal", case["remedy"]),
        ("Heading2", "Service and earlier complaint references"),
        ("Normal", case["reference"] or ", ".join(case["intake"]["references"]) or "Service reference to be supplied"),
        ("Normal", "Earlier complaint: " + (route.get("prior_reference") or "None provided")),
        ("Heading2", "Routing basis and review notes"),
        ("Normal", route["guidance"]),
        ("Normal", "Official source: " + route["source"]),
        *[("Normal", note) for note in route.get("notes", [])],
        ("Normal", "No binding deadline is asserted in this draft. The calendar date is a personal follow-up reminder, not a statutory appeal or limitation deadline."),
        ("Heading2", "Attachments and declaration"),
        ("Normal", "Supporting files supplied: " + (", ".join(case["attachments"]) or "None")),
        ("Normal", "I confirm that the facts and supporting documents are accurate to the best of my knowledge. Signature: ____________________"),
    ]
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, title="Draft grievance petition", leftMargin=48, rightMargin=48, topMargin=48, bottomMargin=48)
    flow = []
    for style, value in sections:
        if ARABIC.search(value):
            for line in rtl_lines(value, doc.width):
                flow.append(UrduLine(line))
        else:
            flow.append(Paragraph(escape(value).replace("\n", "<br/>"), styles[style]))
        flow.append(Spacer(1, 8))
    def footer(canvas, document):
        canvas.setFont("CivicLatin", 8)
        canvas.setFillColor(HexColor("#64748b"))
        canvas.drawString(48, 28, "Prepared draft - review and sign before official submission")
        canvas.drawRightString(document.pagesize[0] - 48, 28, str(document.page))
    doc.build(flow, onFirstPage=footer, onLaterPages=footer)
    return buffer.getvalue()
