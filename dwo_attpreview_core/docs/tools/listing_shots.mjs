// Copyright 2026 Duotek. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
// Listing screenshots (1600x900, English UI) of the Attachment Preview modules in Odoo 19.
// usage: node listing_shots.mjs PORT DB SAMPLES_DIR OUT_DIR [scene,scene,...]
//   needs: playwright (npm), Chrome for Testing / chromium (CHROME env or the Playwright default), a database with
//   dwo_attpreview_core + dwo_attpreview_office + dwo_attpreview_mail installed (no demo data needed), login admin/admin.
//   SAMPLES_DIR holds japan-labour-market-2024.{xlsx,docx,pptx} (sample files #63), bao-cao.pdf, anh-mau.png and legacy-export.bin.
import { chromium } from "playwright";
import fs from "fs"; import path from "path"; import os from "os";
const [port, db, samples, out, only] = process.argv.slice(2);
const scenes = only ? only.split(",") : ["01", "02", "03", "04", "05", "06", "07", "08"];
const CHROME = process.env.CHROME || path.join(os.homedir(), "Library/Caches/ms-playwright/chromium-1255/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing");
const base = `http://localhost:${port}`;
fs.mkdirSync(out, { recursive: true });
const b = await chromium.launch({ executablePath: CHROME, headless: true });
const ctx = await b.newContext({ viewport: { width: 1600, height: 900 }, locale: "en-US", deviceScaleFactor: 1 });
const page = await ctx.newPage();
const shot = (name) => page.screenshot({ path: path.join(out, name + ".png") });
await page.goto(`${base}/web/login?db=${db}`);
await page.fill("input[name=login]", "admin"); await page.fill("input[name=password]", "admin"); await page.press("input[name=password]", "Enter");
await page.waitForSelector(".o_main_navbar", { timeout: 60000 });
const rpc = (model, method, args, kwargs = {}) => page.evaluate(async ([m, me, a, k]) => {
  const r = await fetch(`/web/dataset/call_kw/${m}/${me}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ jsonrpc: "2.0", method: "call", params: { model: m, method: me, args: a, kwargs: k } }) }).then((r) => r.json());
  if (r.error) throw new Error(JSON.stringify(r.error).slice(0, 400)); return r.result; }, [model, method, args, kwargs]);
// demo data: a company with a chatter and attachments of several kinds (fictional names)
await rpc("res.company", "write", [[1], { name: "Northwind Staffing" }]);
const partner = await rpc("res.partner", "create", [{ name: "Sakura Manufacturing Ltd.", is_company: true, email: "hr@sakura-manufacturing.example", phone: "+81 3 5550 0142", website: "https://sakura-manufacturing.example", street: "2-10-1 Marunouchi", city: "Chiyoda-ku, Tokyo", zip: "100-0005" }]);
for (const [f, kind] of [["bao-cao.pdf", "pdf"], ["anh-mau.png", "png"]]) {
  if (fs.existsSync(path.join(samples, "en-" + f))) continue;
  const p2 = await ctx.newPage();
  if (kind === "pdf") {
    await p2.setContent("<h1 style='font-family:sans-serif'>Service agreement</h1>" + "<p style='font-family:sans-serif'>1. The supplier provides recruitment and onboarding services to the client under the terms below.</p>".repeat(30));
    fs.writeFileSync(path.join(samples, "en-" + f), await p2.pdf({ format: "A4" }));
  } else {
    await p2.setViewportSize({ width: 800, height: 500 });
    await p2.setContent("<body style='margin:0;background:linear-gradient(135deg,#2f6fd0,#2aa198);height:500px;display:flex;align-items:flex-end;font:32px sans-serif;color:#fff'><div style='padding:24px'>Factory floor, Tokyo</div></body>");
    fs.writeFileSync(path.join(samples, "en-" + f), await p2.screenshot());
  }
  await p2.close();
}
const files = [["japan-labour-market-2024.xlsx", "Labour market indicators 2024.xlsx"], ["japan-labour-market-2024.docx", "Labour market report 2024.docx"],
  ["japan-labour-market-2024.pptx", "Board presentation Q4.pptx"], ["en-bao-cao.pdf", "Service agreement.pdf"], ["en-anh-mau.png", "Site photo.png"], ["legacy-export.bin", "Legacy export.bin"]];
const ids = {};
for (const [src, name] of files) {
  const r = await rpc("ir.attachment", "create", [{ name, datas: fs.readFileSync(path.join(samples, src)).toString("base64"), res_model: "res.partner", res_id: partner }]);
  ids[name] = Array.isArray(r) ? r[0] : r;
}
await rpc("res.partner", "message_post", [[partner]], { body: "Hi team, the labour market report and the deck for the board are attached, plus the signed agreement.", attachment_ids: Object.values(ids).slice(0, 4), message_type: "comment", subtype_xmlid: "mail.mt_comment" });
await rpc("res.partner", "message_post", [[partner]], { body: "Site photo and the legacy export from their old system.", attachment_ids: Object.values(ids).slice(4), message_type: "comment", subtype_xmlid: "mail.mt_comment" });
const openRecord = async () => {
  await page.goto(`${base}/odoo/res.partner/${partner}`);
  await page.waitForSelector(".o-mail-AttachmentContainer", { timeout: 30000 });
  await page.waitForTimeout(1200);
};
const openFile = async (name) => {
  await page.locator(".o-mail-AttachmentContainer", { hasText: name }).first().click({ force: true });
  await page.waitForSelector(".o_dwo_ap_dialog", { timeout: 30000 });
  await page.waitForSelector(".o_dwo_office[data-state=ready]", { timeout: 90000 });
  await page.waitForTimeout(2500);
};
const viewerFrame = () => page.frames().find((f) => f.url().includes("viewer.html"));
const close = async () => { await page.keyboard.press("Escape"); await page.waitForTimeout(500); };
if (scenes.includes("01")) {
  await openRecord(); await page.mouse.move(5, 5); await shot("01-chatter-attachments");
}
if (scenes.some((s) => ["02", "03"].includes(s))) {
  await openRecord(); await openFile("Labour market indicators 2024.xlsx");
  // the sheet tabs are drawn on a canvas at the bottom of the viewer: click at their x position
  const box = await page.locator(".o_dwo_office iframe").boundingBox();
  const tabs = { "Unemployment 2024": 246, "By Nationality": 360, "Status & Industry": 468, "Minimum Wage": 580, "Shortage Sectors": 690, "Wages & Shunto": 805, "Hiring Flow": 905 };
  const y = box.y + box.height - 14;
  if (scenes.includes("02")) { await page.mouse.click(tabs[process.env.SHEET || "Status & Industry"], y); await page.waitForTimeout(2500); await page.mouse.move(5, 5); await shot("02-xlsx-sheet-with-charts"); }
  if (scenes.includes("03")) { await page.mouse.click(tabs["Hiring Flow"], y); await page.waitForTimeout(2500); await page.mouse.move(5, 5); await shot("03-xlsx-hiring-flow-arrows"); }
  await close();
}
if (scenes.includes("04")) {
  await openRecord(); await openFile("Labour market report 2024.docx");
  const fr = viewerFrame();
  await fr.evaluate((y) => { const els = [...document.querySelectorAll("*")].filter((e) => e.scrollHeight > e.clientHeight + 200 && getComputedStyle(e).overflowY !== "visible"); if (els[0]) els[0].scrollTop = y; }, Number(process.env.DOCX_SCROLL || 2600));
  await page.waitForTimeout(3000); await page.mouse.move(5, 5); await shot("04-docx-continuous-scroll");
  await close();
}
if (scenes.includes("05")) {
  await openRecord(); await openFile("Board presentation Q4.pptx");
  const fr = viewerFrame();
  for (let i = 0; i < Number(process.env.SLIDE || 3); i++) await fr.click("#next");
  await page.waitForTimeout(2500); await page.mouse.move(5, 5); await shot("05-pptx-slide-with-chart");
  await close();
}
if (scenes.includes("06")) {
  await openRecord();
  await page.locator(".o-mail-AttachmentContainer", { hasText: "Legacy export" }).first().click({ force: true });
  await page.waitForSelector(".o_notification", { timeout: 10000 });
  await page.waitForTimeout(700); await page.mouse.move(5, 5); await shot("06-toast-unsupported-file");
}
// 07 and 08: Settings of the core. To show an engine that is not in the addons, the caller marks its module as
// not installable in the database first (UPDATE ir_module_module SET state='uninstallable' WHERE name='dwo_attpreview_office';
// the Settings read the state on every load, no restart needed); 08 opens the popup of that engine (ENGINE_POPUP, default office).
const openSettings = async () => {
  await page.goto(`${base}/odoo/action-base_setup.action_general_configuration`);
  await page.waitForSelector(".settings_tab .tab[data-key=dwo_attpreview_core]", { timeout: 60000 });
  await page.click(".settings_tab .tab[data-key=dwo_attpreview_core]");
  await page.waitForSelector(".o_dwo_ap_engine", { timeout: 30000 });
  await page.waitForTimeout(1200);
};
if (scenes.includes("07")) {
  await openSettings(); await page.mouse.move(5, 5); await shot("07-preview-engines");
}
if (scenes.includes("08")) {
  await openSettings();
  await page.click(`.o_dwo_ap_engine[data-module=${process.env.ENGINE_POPUP || "dwo_attpreview_office"}] input`);
  await page.waitForSelector(".modal .o_dwo_ap_store_desc", { timeout: 30000 });
  await page.waitForTimeout(2000); await page.mouse.move(5, 5); await shot("08-engine-popup");
}
await b.close();
