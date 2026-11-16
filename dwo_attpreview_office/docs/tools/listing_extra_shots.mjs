// Copyright 2026 Duotek. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
// More listing screenshots of the office engine (1600x900, English UI): search, legacy formats, csv, a macro-enabled
// file and an Office file held in a binary field of a partner (#72).
// usage: node listing_extra_shots.mjs PORT DB SAMPLES_DIR OUT_DIR [scene,scene,...]
//   needs: playwright (npm), Chrome for Testing (CHROME env or the Playwright default), a database with
//   dwo_attpreview_core + dwo_attpreview_office installed, login admin/admin.
//   SAMPLES_DIR holds japan-labour-market-2024.{xlsx,docx,pptx} (sample files #63) and open_positions.csv (English);
//   the legacy .xls/.doc come from tests/files of the module (Apache POI samples).
import { chromium } from "playwright";
import fs from "fs"; import path from "path"; import os from "os"; import url from "url";
import { execFileSync } from "child_process";
const [port, db, samples, out, only] = process.argv.slice(2);
const scenes = only ? only.split(",") : ["15", "16", "17", "18", "19", "20", "21"];
const CHROME = process.env.CHROME || path.join(os.homedir(), "Library/Caches/ms-playwright/chromium-1255/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing");
const TESTS = path.join(path.dirname(url.fileURLToPath(import.meta.url)), "..", "..", "tests", "files");
const base = `http://localhost:${port}`;
fs.mkdirSync(out, { recursive: true });
const b = await chromium.launch({ executablePath: CHROME, headless: true });
const ctx = await b.newContext({ viewport: { width: 1600, height: 900 }, locale: "en-US", deviceScaleFactor: 1 });
const page = await ctx.newPage();
const shot = async (name) => { await page.mouse.move(5, 5); await page.screenshot({ path: path.join(out, name + ".png") }); console.log(name, "ok"); };
await page.goto(`${base}/web/login?db=${db}`);
await page.fill("input[name=login]", "admin"); await page.fill("input[name=password]", "admin"); await page.press("input[name=password]", "Enter");
await page.waitForSelector(".o_main_navbar", { timeout: 60000 });
const rpc = (model, method, args, kwargs = {}) => page.evaluate(async ([m, me, a, k]) => {
  const r = await fetch(`/web/dataset/call_kw/${m}/${me}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ jsonrpc: "2.0", method: "call", params: { model: m, method: me, args: a, kwargs: k } }) }).then((r) => r.json());
  if (r.error) throw new Error(JSON.stringify(r.error).slice(0, 400)); return r.result; }, [model, method, args, kwargs]);
const one = (r) => (Array.isArray(r) ? r[0] : r);
const b64 = (p) => fs.readFileSync(p).toString("base64");

// a macro-enabled copy of the sample workbook: same parts, macro content type (the viewer never runs macros)
function xlsmFrom(xlsxPath) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "xlsm-"));
  const target = path.join(dir, "indicators.xlsm");
  const py = `import sys,zipfile\nsrc=zipfile.ZipFile(sys.argv[1]);dst=zipfile.ZipFile(sys.argv[2],"w",zipfile.ZIP_DEFLATED)\nfor i in src.infolist():\n  d=src.read(i.filename)\n  if i.filename=="[Content_Types].xml":d=d.replace(b"spreadsheetml.sheet.main+xml",b"sheet.macroEnabled.main+xml")\n  dst.writestr(i.filename,d)\ndst.close()`;
  fs.writeFileSync(path.join(dir, "m.py"), py);
  execFileSync("python3", [path.join(dir, "m.py"), xlsxPath, target]);
  return target;
}

await rpc("res.company", "write", [[1], { name: "Northwind Staffing" }]);
const partner = one(await rpc("res.partner", "create", [{ name: "Sakura Manufacturing Ltd.", is_company: true, email: "hr@sakura-manufacturing.example" }]));
const files = [
  [path.join(samples, "japan-labour-market-2024.docx"), "Labour market report 2024.docx"],
  [path.join(samples, "japan-labour-market-2024.xlsx"), "Labour market indicators 2024.xlsx"],
  [path.join(TESTS, "legacy_sample.xls"), "Stock report 2009.xls"],
  [path.join(TESTS, "legacy_sample.doc"), "Meeting notes 2008.doc"],
  [path.join(samples, "open_positions.csv"), "Open positions.csv"],
  [xlsmFrom(path.join(samples, "japan-labour-market-2024.xlsx")), "Indicators with macros.xlsm"],
];
const ids = [];
for (const [src, name] of files) {
  ids.push(one(await rpc("ir.attachment", "create", [{ name, datas: b64(src), res_model: "res.partner", res_id: partner }])));
}
await rpc("res.partner", "message_post", [[partner]], { body: "Files for the quarterly review: report, indicators, old exports and the open positions.", attachment_ids: ids, message_type: "comment", subtype_xmlid: "mail.mt_comment" });

const frame = () => page.frameLocator(".o_dwo_office iframe");
async function openFile(name, state = "ready") {
  await page.goto(`${base}/odoo/res.partner/${partner}`);
  await page.waitForSelector(".o-mail-AttachmentContainer", { timeout: 30000 });
  await page.waitForTimeout(800);
  await page.locator(".o-mail-AttachmentContainer", { hasText: name }).first().click({ force: true });
  await page.waitForSelector(`.o_dwo_ap_dialog .o_dwo_office[data-state=${state}]`, { timeout: 90000 });
  await page.waitForTimeout(2500);
}
async function find(query, { enters = 0 } = {}) {
  await frame().locator("#find-open").click();
  const input = frame().locator("#find-input");
  await input.waitFor({ state: "visible", timeout: 10000 });
  await input.fill(query);
  await page.waitForSelector(".o_dwo_office:not([data-find-where='pending']):not([data-find-where=''])", { timeout: 90000 });
  for (let i = 0; i < enters; i++) { await input.press("Enter"); await page.waitForTimeout(500); }
  await page.waitForTimeout(1500);
  console.log("find", query, await page.locator(".o_dwo_office").getAttribute("data-find-total"));
}
if (scenes.includes("15")) { await openFile("Labour market report 2024.docx"); await find(process.env.DOCX_QUERY || "foreign workers", { enters: Number(process.env.DOCX_ENTERS || 0) }); await shot("15-docx-search"); }
if (scenes.includes("16")) { await openFile("Labour market indicators 2024.xlsx"); await find(process.env.XLSX_QUERY || "Vietnam"); await shot("16-xlsx-search"); }
if (scenes.includes("17")) { await openFile("Stock report 2009.xls"); await shot("17-legacy-xls-warning"); }
if (scenes.includes("18")) { await openFile("Meeting notes 2008.doc"); await shot("18-legacy-doc-warning"); }
if (scenes.includes("19")) { await openFile("Open positions.csv"); await shot("19-csv-as-sheet"); }
if (scenes.includes("20")) { await openFile("Indicators with macros.xlsm"); await shot("20-xlsm-macros-not-run"); }
if (scenes.includes("21")) {
  // an Office file held in a binary field of the partner (not an attachment of the chatter)
  const modelId = (await rpc("ir.model", "search", [[["model", "=", "res.partner"]]]))[0];
  await rpc("ir.model.fields", "create", [[
    { name: "x_budget_file", ttype: "binary", field_description: "Budget file", model_id: modelId },
    { name: "x_budget_file_name", ttype: "char", field_description: "Budget file name", model_id: modelId },
  ]]);
  const form = (await rpc("ir.model.data", "check_object_reference", ["base", "view_partner_form"]))[1];
  await rpc("ir.ui.view", "create", [{ name: "partner budget file (screenshots)", model: "res.partner", inherit_id: form,
    arch: `<xpath expr="//notebook" position="before"><group><group><field name="x_budget_file_name" invisible="1"/><field name="x_budget_file" filename="x_budget_file_name"/></group></group></xpath>` }]);
  await rpc("res.partner", "write", [[partner], { x_budget_file: b64(path.join(samples, "japan-labour-market-2024.xlsx")), x_budget_file_name: "Hiring budget 2025.xlsx" }]);
  await page.goto(`${base}/odoo/res.partner/${partner}`);
  await page.waitForSelector(".o_field_widget[name=x_budget_file] .o_dwo_ap_field_preview", { timeout: 30000 });
  await page.click(".o_field_widget[name=x_budget_file] .o_dwo_ap_field_preview");
  await page.waitForSelector(".o_dwo_ap_dialog .o_dwo_office[data-state=ready]", { timeout: 90000 });
  await page.waitForTimeout(2500);
  await shot("21-xlsx-from-binary-field");
}
await b.close();
