"""Optional visual QA helper; requires pypdfium2 in the development environment."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from grievance import agents
from grievance.knowledge import route
import pypdfium2

case = agents.new_case("احمد", "Punjab", "بل درست کیا جائے اور تحریری جواب دیا جائے۔", "12345678", 14)
case["city"] = "راولپنڈی"
case["intake"] = agents.intake("میرے گھر کا بجلی کا بل غلط ہے۔ میٹر کی ریڈنگ درست نہیں ہے۔ IESCO reference 12345678. براہ کرم اس مسئلے کو حل کیا جائے۔", {})
case["route"] = route("IESCO bill", "Electricity", [], department_id="iesco")
case["attachments"] = []
output = Path(__file__).resolve().parents[1] / "data" / "uploads"
output.mkdir(parents=True, exist_ok=True)
pdf = agents.petition(case)
(output / "urdu-layout.pdf").write_bytes(pdf)
document = pypdfium2.PdfDocument(pdf)
for index, page in enumerate(document):
    page.render(scale=1.5).to_pil().save(output / f"urdu-layout-{index + 1}.png")
print(f"Rendered {len(document)} pages into {output}")
