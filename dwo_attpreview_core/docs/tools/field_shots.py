# Copyright 2026 Duotek. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
"""Screenshots of #75 (Preview buttons on file fields), Odoo 19, English UI.
Usage: python3 field_shots.py PORT OUTDIR SAMPLES_DIR   (Python Playwright; a database with core + office + mail, admin/admin)"""
import base64
import os
import sys

from playwright.sync_api import sync_playwright

PORT, OUT, SAMPLES = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(OUT, exist_ok=True)
BASE = f"http://localhost:{PORT}"
CHROME = os.path.expanduser("~/Library/Caches/ms-playwright/chromium-1255/chrome-mac-arm64/Google Chrome for Testing.app/"
                            "Contents/MacOS/Google Chrome for Testing")


def rpc(page, model, method, args, kwargs=None):
    r = page.evaluate("""([m, me, a, k]) => fetch('/web/dataset/call_kw/' + m + '/' + me, {method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({jsonrpc: '2.0', method: 'call', params: {model: m, method: me, args: a, kwargs: k}})})
        .then(r => r.json())""", [model, method, args, kwargs or {}])
    if "error" in r:
        raise Exception(str(r["error"])[:600])
    return r["result"]


def b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def crop(page, selector, name, pad=14, extra=None):
    """Screenshot of the union of the boxes of ``selector`` (and ``extra``) plus a margin."""
    page.mouse.move(3, 3)
    page.wait_for_timeout(700)
    boxes = [page.locator(selector).first.bounding_box()]
    if extra:
        boxes.append(page.locator(extra).first.bounding_box())
    x0 = min(b["x"] for b in boxes) - pad
    y0 = min(b["y"] for b in boxes) - pad
    x1 = max(b["x"] + b["width"] for b in boxes) + pad
    y1 = max(b["y"] + b["height"] for b in boxes) + pad
    page.screenshot(path=f"{OUT}/{name}.png", clip={"x": max(x0, 0), "y": max(y0, 0), "width": x1 - max(x0, 0),
                                                     "height": y1 - max(y0, 0)})
    print("shot", name, flush=True)


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME, headless=True)
    page = b.new_context(viewport={"width": 1600, "height": 900}, locale="en-US").new_page()
    page.on("pageerror", lambda e: print("PAGEERROR", str(e)[:300]))
    page.goto(f"{BASE}/web/login")
    page.fill("input[name=login]", "admin")
    page.fill("input[name=password]", "admin")
    page.press("input[name=password]", "Enter")
    page.wait_for_selector(".o_main_navbar", timeout=60000)

    # --- data (fictional, English) ---------------------------------------
    rpc(page, "res.company", "write", [[1], {"name": "Northwind Staffing"}])
    model_id = rpc(page, "ir.model", "search", [[["model", "=", "res.partner"]]])[0]
    rpc(page, "ir.model.fields", "create", [[
        {"name": "x_contract", "ttype": "binary", "field_description": "Signed contract", "model_id": model_id},
        {"name": "x_contract_name", "ttype": "char", "field_description": "Contract file name", "model_id": model_id},
        {"name": "x_main_document_id", "ttype": "many2one", "relation": "ir.attachment",
         "field_description": "Main document", "model_id": model_id},
        {"name": "x_document_ids", "ttype": "many2many", "relation": "ir.attachment",
         "relation_table": "x_partner_document_rel", "column1": "partner_id", "column2": "attachment_id",
         "field_description": "Documents", "model_id": model_id},
        {"name": "x_report_ids", "ttype": "many2many", "relation": "ir.attachment",
         "relation_table": "x_partner_report_rel", "column1": "partner_id", "column2": "attachment_id",
         "field_description": "Reports", "model_id": model_id},
    ]])
    form = rpc(page, "ir.model.data", "check_object_reference", ["base", "view_partner_form"])[1]
    rpc(page, "ir.ui.view", "create", [{
        "name": "partner documents (screenshots)", "model": "res.partner", "inherit_id": form,
        "arch": """<xpath expr="//notebook" position="before">
            <group name="x_docs">
                <group>
                    <field name="x_contract_name" invisible="1"/>
                    <field name="x_contract" filename="x_contract_name"/>
                    <field name="x_main_document_id"/>
                </group>
                <group>
                    <field name="x_document_ids" widget="many2many_binary"/>
                </group>
            </group>
            <field name="x_report_ids"><list><field name="name"/><field name="mimetype"/><field name="file_size"/></list></field>
        </xpath>"""}])
    jp = os.path.join(SAMPLES, "jp_labor_2024")
    pdf = os.path.join(OUT, "_agreement.pdf")
    if not os.path.exists(pdf):
        p2 = b.new_page()
        p2.set_content("<h1 style='font-family:sans-serif'>Service agreement</h1>" + "<p style='font-family:sans-serif'>"
                       "1. The supplier provides recruitment and onboarding services to the client.</p>" * 25)
        p2.pdf(path=pdf, format="A4")
        p2.close()
    partner = rpc(page, "res.partner", "create", [{
        "name": "Sakura Manufacturing Ltd.", "is_company": True, "email": "hr@sakura-manufacturing.example",
        "x_contract": b64(pdf), "x_contract_name": "Service agreement 2026.pdf"}])
    partner = partner[0] if isinstance(partner, list) else partner

    def att(name, path):
        r = rpc(page, "ir.attachment", "create", [{"name": name, "datas": b64(path), "res_model": "res.partner",
                                                   "res_id": partner}])
        return r[0] if isinstance(r, list) else r

    docx = att("Labour market report 2024.docx", os.path.join(jp, "japan-labour-market-2024.docx"))
    xlsx = att("Labour market indicators 2024.xlsx", os.path.join(jp, "japan-labour-market-2024.xlsx"))
    pptx = att("Board presentation Q4.pptx", os.path.join(jp, "japan-labour-market-2024.pptx"))
    agreement = att("Service agreement 2026.pdf", pdf)
    rpc(page, "res.partner", "write", [[partner], {
        "x_main_document_id": docx,
        "x_document_ids": [[6, 0, [xlsx, agreement]]],
        "x_report_ids": [[6, 0, [docx, xlsx, pptx]]],
    }])

    # --- 09: binary field "File Content" of an attachment ------------------
    # a narrow window so that the field (full width in this form) gives a small crop
    page.set_viewport_size({"width": 760, "height": 700})
    page.goto(f"{BASE}/odoo/action-base.action_attachment/{docx}")
    page.wait_for_selector(".o_field_widget[name=datas] .o_dwo_ap_field_preview", timeout=30000)
    crop(page, ".o_field_widget[name=datas]", "09-binary-field-preview", pad=14,
         extra="label[for^=datas]")
    page.set_viewport_size({"width": 1600, "height": 900})
    page.reload()
    page.wait_for_selector(".o_field_widget[name=datas] .o_dwo_ap_field_preview", timeout=30000)
    # --- 10: dialog opened from that field ----------------------------------
    page.click(".o_field_widget[name=datas] .o_dwo_ap_field_preview")
    page.wait_for_selector(".o_dwo_ap_dialog", timeout=30000)
    page.wait_for_selector(".o_dwo_office[data-state=ready]", timeout=90000)
    page.wait_for_timeout(2500)
    page.mouse.move(3, 3)
    page.screenshot(path=f"{OUT}/10-binary-field-dialog.png")
    print("shot 10", flush=True)
    page.keyboard.press("Escape")
    page.wait_for_timeout(500)

    # --- partner form: binary on another model, many2one, many2many_binary, list --
    page.goto(f"{BASE}/odoo/res.partner/{partner}")
    page.wait_for_selector(".o_field_widget[name=x_report_ids] .o_dwo_ap_list_preview", timeout=30000)
    crop(page, ".o_inner_group:has(.o_field_widget[name=x_contract])", "11-binary-and-many2one-preview", pad=12)
    crop(page, ".o_inner_group:has(.o_field_widget[name=x_document_ids])", "12-many2many-binary-preview", pad=12)
    crop(page, ".o_field_widget[name=x_report_ids]", "13-attachment-list-preview", pad=12)

    # --- 14: a card of the Attachments menu (kanban) ------------------------
    page.goto(f"{BASE}/odoo/action-base.action_attachment")
    card = ".o_kanban_record:has(.o_dwo_ap_kanban_preview):has-text('Labour market report 2024.docx')"
    page.wait_for_selector(card, timeout=30000)
    crop(page, card, "14-attachment-kanban-preview", pad=12)
    b.close()
