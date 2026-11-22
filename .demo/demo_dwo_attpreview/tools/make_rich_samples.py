# /// script
# requires-python = ">=3.10"
# dependencies = ["reportlab", "pillow", "py7zr"]
# ///
"""Builds the realistic part of the samples (run with: uv run tools/make_rich_samples.py, after make_samples.py).

PDF report (3 pages, table, chart), a photo-like PNG, video and audio (ffmpeg), long text/code/log files, a 240-row
CSV, and project archives with a real folder tree. Everything is English and made up (Northwind Garden Supplies)."""
import csv
import io
import json
import math
import random
import subprocess
import tarfile
import zipfile
from pathlib import Path

import py7zr
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "static" / "samples"
TEXT = OUT / "text"
TEXT.mkdir(parents=True, exist_ok=True)
rnd = random.Random(7)
REGIONS = [("North", 18200, 21450, 19800, 24100), ("South", 15400, 16900, 18350, 20200),
           ("East", 12100, 13900, 14250, 16800), ("West", 20300, 22100, 23950, 26400)]
FILLER = ("Sales grew in every region during the year. The online catalogue was the main driver, with the pilot shops "
          "reporting faster order entry and fewer returns. Delivery times fell from six days to four after the new "
          "carrier contract started in June. The remaining risks are stock of seasonal items and support capacity.")


def make_pdf():
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(OUT / "sample.pdf"), pagesize=A4, leftMargin=2.2 * cm, rightMargin=2.2 * cm,
                            topMargin=2 * cm, bottomMargin=2 * cm, title="Annual Report 2026", author="Northwind Garden Supplies")
    flow = [Paragraph("Northwind Garden Supplies", styles["Title"]), Paragraph("Annual Report 2026", styles["Heading2"]),
            Spacer(1, 12)]
    for head in ("1. Summary", "2. Sales by region"):
        flow += [Paragraph(head, styles["Heading1"])] + [Paragraph(FILLER, styles["BodyText"]) for _ in range(2)]
        if head.startswith("2"):
            data = [["Region", "Q1", "Q2", "Q3", "Q4", "Total"]] + [
                [r[0]] + ["{:,}".format(v) for v in r[1:]] + ["{:,}".format(sum(r[1:]))] for r in REGIONS]
            table = Table(data, hAlign="LEFT")
            table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E79")),
                                       ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                                       ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EEF3F8")]),
                                       ("ALIGN", (1, 0), (-1, -1), "RIGHT")]))
            flow += [Spacer(1, 8), table, Spacer(1, 14)]
    drawing = Drawing(440, 200)
    chart = VerticalBarChart()
    chart.x, chart.y, chart.width, chart.height = 40, 30, 380, 150
    chart.data = [[sum(r[1:3]) for r in REGIONS], [sum(r[3:]) for r in REGIONS]]
    chart.categoryAxis.categoryNames = [r[0] for r in REGIONS]
    chart.bars[0].fillColor, chart.bars[1].fillColor = colors.HexColor("#5B9BD5"), colors.HexColor("#1F4E79")
    drawing.add(chart)
    flow += [Paragraph("First half (light) and second half (dark), in EUR", styles["Italic"]), drawing, PageBreak()]
    flow += [Paragraph("3. Operations", styles["Heading1"])] + [Paragraph(FILLER, styles["BodyText"]) for _ in range(6)]
    flow += [Paragraph("4. Outlook", styles["Heading1"])] + [Paragraph(FILLER, styles["BodyText"]) for _ in range(5)]
    doc.build(flow, onFirstPage=_footer, onLaterPages=_footer)


def _footer(canvas, doc):
    canvas.setFont("Helvetica", 8)
    canvas.drawString(2.2 * cm, 1.2 * cm, "Northwind Garden Supplies - Annual Report 2026")
    canvas.drawRightString(A4[0] - 2.2 * cm, 1.2 * cm, "Page %d" % doc.page)


def make_png():
    """A landscape picture: sky gradient, sun, layered hills, a small cottage, soft grain (looks like a photo)."""
    w, h = 1600, 1000
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        t = y / h
        for x in range(w):
            px[x, y] = (int(255 - 90 * t), int(190 - 20 * t + 20 * (x / w)), int(120 + 110 * t))
    draw = ImageDraw.Draw(img, "RGBA")
    draw.ellipse((1100, 120, 1300, 320), fill=(255, 240, 190, 255))
    for r in range(8, 0, -1):
        draw.ellipse((1200 - 100 - r * 22, 220 - 100 - r * 22, 1200 + 100 + r * 22, 220 + 100 + r * 22), fill=(255, 236, 170, 12))
    for layer, (base, amp, colr) in enumerate([(560, 70, (96, 128, 150)), (640, 60, (70, 120, 96)),
                                               (740, 50, (52, 104, 62)), (850, 40, (36, 82, 44))]):
        pts = [(0, h)] + [(x, base + amp * math.sin(x / 190 + layer * 1.7) + 25 * math.sin(x / 61 + layer)) for x in range(0, w + 8, 8)] + [(w, h)]
        draw.polygon(pts, fill=colr + (255,))
    draw.rectangle((300, 720, 460, 810), fill=(236, 226, 205, 255))
    draw.polygon([(285, 722), (380, 650), (475, 722)], fill=(150, 62, 48, 255))
    draw.rectangle((365, 755, 400, 810), fill=(94, 64, 40, 255))
    draw.rectangle((320, 745, 345, 770), fill=(120, 170, 210, 255))
    for _ in range(60):
        x, y = rnd.randint(0, w), rnd.randint(870, h)
        draw.line((x, y, x + rnd.randint(-6, 6), y - rnd.randint(25, 60)), fill=(60, 120, 50, 200), width=3)
    img = img.filter(ImageFilter.GaussianBlur(1.2))
    px = img.load()
    for _ in range(w * h // 14):
        x, y = rnd.randrange(w), rnd.randrange(h)
        d = rnd.randint(-5, 5)
        r, g, b = px[x, y]
        px[x, y] = (max(0, min(255, r + d)), max(0, min(255, g + d)), max(0, min(255, b + d)))
    img.save(OUT / "sample.png", optimize=True)


def make_media():
    ff = ["ffmpeg", "-y", "-loglevel", "error"]
    subprocess.run(ff + ["-f", "lavfi", "-i", "testsrc2=size=640x360:rate=24:duration=6", "-f", "lavfi", "-i",
                         "sine=frequency=440:duration=6", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "30", "-c:a", "aac",
                         "-b:a", "64k", "-shortest", str(OUT / "sample.mp4")], check=True)
    notes = "+".join("sin(2*PI*%d*t)*between(t\\,%s\\,%s)" % (f, i * 0.5, i * 0.5 + 0.45)
                     for i, f in enumerate((262, 294, 330, 349, 392, 440, 494, 523)))
    subprocess.run(ff + ["-f", "lavfi", "-i", "aevalsrc='0.4*(%s)':s=44100:d=4" % notes, "-b:a", "96k", str(OUT / "sample.mp3")], check=True)


def make_text():
    (TEXT / "README.md").write_text("""# Northwind Catalogue API

A small service that publishes the **Northwind Garden Supplies** catalogue to the shops.

## Quick start

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python -m catalogue.server --port 8080
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/products` | List products, paged |
| GET | `/products/<id>` | One product with its stock |
| POST | `/orders` | Create an order |

## Configuration

Settings live in `settings.yaml`. Environment variables override them:

- `CATALOGUE_DB`: database URL
- `CATALOGUE_CACHE`: cache time in seconds (default `60`)

> **Note**
> Prices are in EUR and include tax.

### Release checklist

1. Run the tests
2. Update `CHANGELOG.md`
3. Tag the release

See also [the plan](docs/plan/milestones.md).
""")
    products = [{"id": 1000 + i, "sku": "NW-%04d" % i, "name": n, "category": c, "price": round(p, 2),
                 "stock": rnd.randint(0, 900), "tags": t, "dimensions": {"w": rnd.randint(10, 90), "h": rnd.randint(10, 120)},
                 "active": i % 7 != 0}
                for i, (n, c, p, t) in enumerate([
                    ("Garden chair", "Furniture", 120, ["outdoor", "wood"]), ("Garden table", "Furniture", 450, ["outdoor"]),
                    ("Watering can", "Tools", 15.5, ["metal"]), ("Pruning shears", "Tools", 24, ["steel", "grip"]),
                    ("Plant pot set", "Decor", 32, ["clay"]), ("Solar lantern", "Decor", 18.9, ["solar", "led"]),
                    ("Hose 25 m", "Tools", 39, []), ("Raised bed", "Furniture", 89, ["wood", "diy"]),
                    ("Compost bin", "Tools", 54, ["eco"]), ("Bird feeder", "Decor", 14.2, ["wood", "birds"]),
                    ("Wheelbarrow", "Tools", 79, ["steel"]), ("Hammock", "Furniture", 65, ["outdoor", "cotton"])] * 3, 1)]
    (TEXT / "data.json").write_text(json.dumps({"generated": "2026-11-21T08:00:00Z", "currency": "EUR", "count": len(products),
                                                "products": products}, indent=2))
    rows = "".join("      <product sku='NW-%04d' price='%s' stock='%d'>%s</product>\n" % (i, round(rnd.uniform(5, 300), 2), rnd.randint(0, 500), n)
                   for i, n in enumerate(["Garden chair", "Garden table", "Watering can", "Pruning shears", "Plant pot set", "Solar lantern"], 1))
    (TEXT / "config.xml").write_text("""<?xml version="1.0" encoding="UTF-8"?>
<!-- Catalogue service configuration -->
<config version="2.4">
  <server host="0.0.0.0" port="8080" workers="4">
    <tls enabled="true" cert="/etc/ssl/catalogue.pem"/>
  </server>
  <database url="postgresql://catalogue@db/catalogue" pool="10"/>
  <cache ttl="60" backend="redis"><node host="cache1"/><node host="cache2"/></cache>
  <modules>
    <module name="base"/>
    <module name="mail"/>
    <module name="sale" optional="true"/>
  </modules>
  <catalogue>
""" + rows + """  </catalogue>
</config>
""")
    (TEXT / "settings.yaml").write_text("""# Catalogue service settings
server:
  host: 0.0.0.0
  port: 8080
  workers: 4
  tls:
    enabled: true
    cert: /etc/ssl/catalogue.pem
database:
  url: postgresql://catalogue@db/catalogue
  pool: 10
cache:
  ttl: 60
  nodes:
    - host: cache1
      port: 6379
    - host: cache2
      port: 6379
logging:
  level: INFO
  handlers: [console, file]
  file: /var/log/catalogue/server.log
modules:
  - base
  - mail
  - sale
features:
  search: true
  recommendations: false
  tax_included: true
""")
    (TEXT / "script.py").write_text('''"""Stock report: reads the catalogue export and prints the items that need to be reordered."""
import argparse
import csv
import json
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class Item:
    sku: str
    name: str
    category: str
    price: float
    stock: int

    @property
    def value(self):
        return self.price * self.stock


def load(path):
    """Read the JSON export and return the active items."""
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    return [Item(p["sku"], p["name"], p["category"], p["price"], p["stock"]) for p in data["products"] if p["active"]]


def by_category(items):
    totals = defaultdict(float)
    for item in items:
        totals[item.category] += item.value
    return dict(sorted(totals.items(), key=lambda pair: -pair[1]))


def to_reorder(items, threshold=50):
    return [item for item in items if item.stock < threshold]


def write_csv(items, path):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["SKU", "Name", "Stock"])
        for item in items:
            writer.writerow([item.sku, item.name, item.stock])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export")
    parser.add_argument("--threshold", type=int, default=50)
    parser.add_argument("--out", default="reorder.csv")
    args = parser.parse_args()
    items = load(args.export)
    print("Stock value by category:")
    for category, total in by_category(items).items():
        print("  %-10s %10.2f EUR" % (category, total))
    low = to_reorder(items, args.threshold)
    write_csv(low, args.out)
    print("%d of %d items below %d units, written to %s" % (len(low), len(items), args.threshold, args.out))


if __name__ == "__main__":
    main()
''')
    (TEXT / "page.html").write_text("""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Spring catalogue</title>
<style>body{font-family:sans-serif;max-width:720px;margin:2em auto;color:#222}h1{color:#1F4E79}
table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccc;padding:6px 10px;text-align:left}th{background:#eef3f8}</style></head>
<body><h1>Spring catalogue</h1>
<p>Everything for the garden, <b>delivered in four days</b>. See the <a href="#range">range</a> below.</p>
<h2 id="range">Our range</h2>
<table><tr><th>Product</th><th>Category</th><th>Price</th></tr>
<tr><td>Garden chair</td><td>Furniture</td><td>120.00 EUR</td></tr>
<tr><td>Watering can</td><td>Tools</td><td>15.50 EUR</td></tr>
<tr><td>Solar lantern</td><td>Decor</td><td>18.90 EUR</td></tr></table>
<ul><li>Free delivery over 100 EUR</li><li>30 days to return</li></ul></body></html>
""")
    levels = ["INFO"] * 14 + ["DEBUG"] * 4 + ["WARN"] * 2 + ["ERROR"]
    msgs = {"INFO": ["request GET /products 200 %dms", "order SO-%d created", "cache refreshed (%d keys)", "user login ok (id %d)"],
            "DEBUG": ["query returned %d rows", "cache miss for key %d"],
            "WARN": ["slow query (%d ms)", "retrying connection (attempt %d)"],
            "ERROR": ["connection reset by peer (code %d)", "payment gateway timeout (order %d)"]}
    lines, minute = [], 0
    for n in range(320):
        minute += rnd.randint(0, 2) if n % 3 else 0
        lvl = rnd.choice(levels)
        lines.append("2026-11-21 %02d:%02d:%02d %-5s %s" % (8 + minute // 60, minute % 60, rnd.randint(0, 59), lvl,
                                                            rnd.choice(msgs[lvl]) % rnd.randint(2, 4000)))
    (TEXT / "server.log").write_text("\n".join(lines) + "\n")
    (TEXT / "change.diff").write_text("""diff --git a/catalogue/server.py b/catalogue/server.py
index 3f2a1c4..9be07d2 100644
--- a/catalogue/server.py
+++ b/catalogue/server.py
@@ -12,9 +12,12 @@ from .cache import Cache
 
 
 def list_products(page=1, size=50):
-    rows = db.query("SELECT * FROM product")
-    return [dict(r) for r in rows]
+    offset = (page - 1) * size
+    rows = db.query("SELECT * FROM product WHERE active ORDER BY name LIMIT %s OFFSET %s", (size, offset))
+    return {"page": page, "size": size, "items": [dict(r) for r in rows]}
 
 
 def get_product(product_id):
@@ -40,7 +43,8 @@ def create_order(payload):
     if not payload.get("lines"):
         raise ValueError("an order needs at least one line")
-    order = Order(**payload)
+    order = Order(**payload, currency="EUR")
+    order.validate_stock()
     db.save(order)
     return order.id
 
diff --git a/settings.yaml b/settings.yaml
index 71d0aa1..a8c33e9 100644
--- a/settings.yaml
+++ b/settings.yaml
@@ -1,6 +1,6 @@
 server:
   host: 0.0.0.0
-  port: 8000
+  port: 8080
   workers: 4
 cache:
-  ttl: 30
+  ttl: 60
diff --git a/CHANGELOG.md b/CHANGELOG.md
index e69de29..4c1d9ab 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -0,0 +1,5 @@
+## 2.4.0
+
+- Paged product list
+- Orders check the stock before they are saved
+- Default port is now 8080
""")


def make_tables():
    first = ["Northwind Traders", "Contoso Ltd", "Globex Corporation", "Initech", "Umbrella Supplies", "Hooli", "Stark Garden", "Wayne Outdoor"]
    products = [("Garden chair", 120), ("Watering can", 15.5), ("Solar lantern", 18.9), ("Plant pot set", 32), ("Pruning shears", 24),
                ("Hose 25 m", 39), ("Raised bed", 89), ("Compost bin", 54)]
    rows = []
    for i in range(240):
        p, price = rnd.choice(products)
        qty = rnd.randint(1, 30)
        rows.append(("SO-%d" % (1001 + i), "2026-%02d-%02d" % (rnd.randint(1, 11), rnd.randint(1, 28)), rnd.choice(first), p, qty,
                     "%.2f" % (qty * price), rnd.choice(["Paid", "Paid", "Open", "Late"])))
    for name, delim in (("sample.csv", ","), ("sample_semicolon.csv", ";"), ("sample.tsv", "\t")):
        with open(OUT / name, "w", newline="", encoding="utf-8") as handle:
            wr = csv.writer(handle, delimiter=delim)
            wr.writerow(["Order", "Date", "Customer", "Product", "Quantity", "Amount", "Status"])
            wr.writerows(rows)


def make_archives():
    files = {"project/README.md": (TEXT / "README.md").read_text(), "project/settings.yaml": (TEXT / "settings.yaml").read_text(),
             "project/requirements.txt": "flask==3.0.3\npsycopg2-binary==2.9.9\nredis==5.0.4\npytest==8.2.0\n",
             "project/src/catalogue/__init__.py": '"""Catalogue service."""\n__version__ = "2.4.0"\n',
             "project/src/catalogue/server.py": (TEXT / "script.py").read_text(),
             "project/src/catalogue/data.json": (TEXT / "data.json").read_text(),
             "project/tests/test_server.py": "from catalogue.server import to_reorder, Item\n\n\ndef test_reorder():\n    items = [Item('A', 'a', 'x', 1.0, 3), Item('B', 'b', 'x', 1.0, 99)]\n    assert [i.sku for i in to_reorder(items)] == ['A']\n",
             "project/docs/notes.txt": "Meeting notes\n=============\n- Checkout ready for April 10\n- Delivery tracking May 2\n- Pilot shops: all regions\n",
             "project/docs/plan/milestones.md": "## Milestones\n\n| Date | Goal |\n|------|------|\n| April 10 | Checkout |\n| May 2 | Delivery tracking |\n",
             "project/docs/server.log": (TEXT / "server.log").read_text(),
             "project/assets/sample.png": None, "project/data/orders.csv": (OUT / "sample.csv").read_text()}
    files["project/assets/sample.png"] = (OUT / "sample.png").read_bytes()
    enc = lambda v: v if isinstance(v, bytes) else v.encode()
    with zipfile.ZipFile(OUT / "project.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for n, v in files.items():
            z.writestr(n, enc(v))
    with tarfile.open(OUT / "project.tar.gz", "w:gz") as t:
        for n, v in files.items():
            info = tarfile.TarInfo(n)
            info.size = len(enc(v))
            t.addfile(info, io.BytesIO(enc(v)))
    with py7zr.SevenZipFile(OUT / "project.7z", "w") as s:
        for n, v in files.items():
            s.writestr(enc(v), n)


if __name__ == "__main__":
    make_pdf(); make_png(); make_media(); make_text(); make_tables(); make_archives()
    for p in sorted(OUT.rglob("*")):
        if p.is_file() and p.stat().st_mtime > __import__("time").time() - 300:
            print("%-30s %6d KB" % (p.relative_to(OUT), p.stat().st_size // 1024 or 1))
