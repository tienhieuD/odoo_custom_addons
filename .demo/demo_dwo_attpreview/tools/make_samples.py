# /// script
# requires-python = ">=3.10"
# dependencies = ["python-docx", "python-pptx", "openpyxl", "py7zr"]
# ///
"""Builds the English sample files shipped in static/samples (run with: uv run tools/make_samples.py).

The Office, archive and e-mail samples are generated here so that every demo file is English. The 3D, DXF, IFC and
OpenDocument samples are copied from the tests/files folders of the dwo_attpreview_* modules by the same script.
"""
import csv
import io
import shutil
import tarfile
import zipfile
from pathlib import Path

import py7zr
from docx import Document
from docx.shared import Pt
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from pptx import Presentation
from pptx.util import Inches, Pt as PPt

HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "static" / "samples"
REPO = HERE.parent.parent  # odoo_custom_addons19
OUT.mkdir(parents=True, exist_ok=True)

REGIONS = [("North", 18200, 21450, 19800, 24100), ("South", 15400, 16900, 18350, 20200),
           ("East", 12100, 13900, 14250, 16800), ("West", 20300, 22100, 23950, 26400)]
PRODUCTS = [("Garden chair", "Furniture", 120, 340), ("Garden table", "Furniture", 450, 120), ("Watering can", "Tools", 15, 900),
            ("Pruning shears", "Tools", 24, 610), ("Plant pot set", "Decor", 32, 450), ("Solar lantern", "Decor", 18, 780)]
FILLER = ("The team reviewed the plan for the new online catalogue and agreed on the main milestones. "
          "Product search, checkout and delivery tracking will be released in three stages, starting in April. "
          "Customer feedback from the pilot shops was positive, and the remaining open points are listed below.")


def make_docx():
    doc = Document()
    doc.styles["Normal"].font.size = Pt(11)
    doc.add_heading("Spring Catalogue Launch", 0)
    doc.add_paragraph("Project kickoff notes, Northwind Garden Supplies. Internal meeting, March 3.")
    doc.add_heading("1. Regional sales", 1)
    table = doc.add_table(rows=1, cols=5)
    table.style = "Light Grid Accent 1"
    for cell, text in zip(table.rows[0].cells, ("Region", "Q1", "Q2", "Q3", "Q4")):
        cell.text = text
    for row in REGIONS:
        cells = table.add_row().cells
        for cell, value in zip(cells, row):
            cell.text = "{:,}".format(value) if isinstance(value, int) else value
    doc.add_heading("2. Next steps", 1)
    for item in ("Finish the product photos", "Open the pilot shops in April", "Train the support team", "Publish the catalogue"):
        doc.add_paragraph(item, style="List Bullet")
    p = doc.add_paragraph()
    p.add_run("Bold text, ").bold = True
    p.add_run("italic text and ").italic = True
    p.add_run("normal text in one paragraph.")
    for index in range(6):
        doc.add_paragraph("Paragraph %d. %s" % (index + 1, FILLER))
    doc.save(OUT / "sample.docx")
    long = Document()
    long.add_heading("Quarterly Operations Report", 0)
    for section in range(1, 13):
        long.add_heading("Section %d: %s" % (section, ("Overview", "Sales", "Stock", "Suppliers", "Delivery", "Support")[section % 6]), 1)
        for _ in range(5):
            long.add_paragraph(FILLER)
    long.save(OUT / "long.docx")


def make_xlsx():
    wb = Workbook()
    ws = wb.active
    ws.title = "Sales"
    ws.append(["Region", "Q1", "Q2", "Q3", "Q4", "Total"])
    for region, *quarters in REGIONS:
        ws.append([region] + quarters + [sum(quarters)])
    ws.append(["All regions"] + [sum(r[i] for r in REGIONS) for i in range(1, 5)] + [sum(sum(r[1:]) for r in REGIONS)])
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="1F4E79")
    for cell in ws[ws.max_row]:
        cell.font = Font(bold=True)
    ws.column_dimensions["A"].width = 16
    inv = wb.create_sheet("Inventory")
    inv.append(["Product", "Category", "Unit price", "In stock"])
    for row in PRODUCTS:
        inv.append(list(row))
    for cell in inv[1]:
        cell.font = Font(bold=True)
    inv.column_dimensions["A"].width = 18
    wb.save(OUT / "sample.xlsx")


def make_pptx():
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = "Spring Catalogue Launch"
    slide.placeholders[1].text = "Northwind Garden Supplies - team update, March"
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Milestones"
    body = slide.placeholders[1].text_frame
    body.text = "Online catalogue and product search"
    for line in ("Checkout and payment: April 10", "Delivery tracking: May 2", "Pilot shops: all regions"):
        body.add_paragraph().text = line
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = "Sales by region"
    rows, cols = len(REGIONS) + 1, 5
    table = slide.shapes.add_table(rows, cols, Inches(0.7), Inches(1.8), Inches(8.6), Inches(3)).table
    for c, head in enumerate(("Region", "Q1", "Q2", "Q3", "Q4")):
        table.cell(0, c).text = head
    for r, row in enumerate(REGIONS, 1):
        for c, value in enumerate(row):
            table.cell(r, c).text = "{:,}".format(value) if isinstance(value, int) else value
    prs.save(OUT / "sample.pptx")


def make_tables():
    header = ["Order", "Customer", "Product", "Quantity", "Amount"]
    rows = [("SO-1001", "Northwind Traders", "Garden chair", 4, 480), ("SO-1002", "Contoso Ltd", "Watering can", 20, 300),
            ("SO-1003", "Globex Corporation", "Solar lantern", 12, 216), ("SO-1004", "Initech", "Plant pot set", 6, 192),
            ("SO-1005", "Umbrella Supplies", "Pruning shears", 9, 216)]
    for name, delimiter in (("sample.csv", ","), ("sample_semicolon.csv", ";"), ("sample.tsv", "\t")):
        with open(OUT / name, "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle, delimiter=delimiter)
            writer.writerow(header)
            writer.writerows(rows)


def make_archives():
    files = {
        "project/README.md": "# Spring Catalogue\n\nOpen the files inside the archive.\n",
        "project/src/main.py": "print('hello from the archive')\n",
        "project/src/data.json": '{"inside": "archive", "items": [1, 2, 3]}\n',
        "project/docs/notes.txt": "Meeting notes inside a nested folder.\n",
        "project/docs/plan/milestones.md": "## Milestones\n\n- April 10: checkout\n- May 2: delivery tracking\n",
    }
    with zipfile.ZipFile(OUT / "project.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for name, text in files.items():
            archive.writestr(name, text)
    with tarfile.open(OUT / "project.tar.gz", "w:gz") as archive:
        for name, text in files.items():
            data = text.encode()
            info = tarfile.TarInfo(name)
            info.size = len(data)
            archive.addfile(info, io.BytesIO(data))
    with py7zr.SevenZipFile(OUT / "project.7z", "w") as archive:
        for name, text in files.items():
            archive.writestr(text, name)


def make_emails():
    from email.message import EmailMessage
    inner = EmailMessage()
    inner["Subject"] = "Draft of the price list"
    inner["From"] = "Carol Evans <carol@example.com>"
    inner["To"] = "Alice Martin <alice@example.com>"
    inner["Date"] = "Thu, 20 Nov 2026 16:05:00 +0000"
    inner.set_content("Hi Alice,\n\nHere is the first draft of the price list. Please check the garden range.\n\nCarol")
    inner.add_attachment((OUT / "sample.csv").read_bytes(), maintype="text", subtype="csv", filename="price-list.csv")
    msg = EmailMessage()
    msg["Subject"] = "Quarterly report and price list"
    msg["From"] = "Alice Martin <alice@example.com>"
    msg["To"] = "Bob Carter <bob@example.com>"
    msg["Cc"] = "Carol Evans <carol@example.com>"
    msg["Date"] = "Fri, 21 Nov 2026 09:30:00 +0000"
    msg.set_content("Hi Bob,\n\nThe quarterly report is attached, with Carol's draft of the price list (forwarded).\n\nBest regards,\nAlice")
    msg.add_alternative("<p>Hi Bob,</p><p>The <b>quarterly report</b> is attached, with Carol's draft of the price list (forwarded).</p>"
                        "<p>Best regards,<br/>Alice</p>", subtype="html")
    msg.add_attachment((OUT / "sample.docx").read_bytes(), maintype="application",
                       subtype="vnd.openxmlformats-officedocument.wordprocessingml.document", filename="quarterly-report.docx")
    msg.add_attachment(inner)
    (OUT / "quarterly-report.eml").write_bytes(msg.as_bytes())
    simple = EmailMessage()
    simple["Subject"] = "Meeting on Tuesday"
    simple["From"] = "Bob Carter <bob@example.com>"
    simple["To"] = "Alice Martin <alice@example.com>"
    simple["Date"] = "Mon, 17 Nov 2026 08:10:00 +0000"
    simple.set_content("Hi Alice,\n\nCan we meet on Tuesday at 10:00 to go through the catalogue plan?\n\nBob")
    (OUT / "meeting.eml").write_bytes(simple.as_bytes())


def copy_neutral_samples():
    """3D models, DXF, IFC and OpenDocument files: geometry or English text already."""
    pairs = {"dwo_attpreview_office": ["sample.odt", "sample.ods", "sample.odp"],
             "dwo_attpreview_cad": ["floor-plan.dxf"], "dwo_attpreview_bim": ["office-building.ifc"],
             "dwo_attpreview_3d": ["spur-gear.stl", "spur-gear.glb", "spur-gear.obj", "spur-gear.3mf", "spur-gear.ply",
                                   "spur-gear.fbx", "spur-gear.dae", "rounded-cube.step", "cube-10x10.igs"]}
    for module, names in pairs.items():
        for name in names:
            shutil.copy(REPO / module / "tests" / "files" / name, OUT / name)


if __name__ == "__main__":
    make_docx(); make_xlsx(); make_pptx(); make_tables(); make_archives(); make_emails(); copy_neutral_samples()
    for path in sorted(OUT.iterdir()):
        print("%-28s %6d KB" % (path.name, path.stat().st_size // 1024 or 1))
