import { n as e } from "./substitutions-_KDT_mVq.js";
import { i as t } from "./substitute-script-COw3MRyd.js";
import { o as n, r } from "./scripts-DxEAUeVI.js";
import { t as i } from "./symbol-font-Cf7Xu0_f.js";
import { n as a, t as o } from "./metafile-font-demand-CmEiy4lu.js";
import { i as s } from "./face-download-BGnp7NTs.js";
import { t as c } from "./installed-families-ChA8CUiK.js";
import { t as l } from "./chart-font-sources-B96UtO2E.js";
import { c as u, f as d, o as f, s as p } from "./number-format-CKqKnRTi.js";
import { t as m } from "./scalar-demand-bzQ71V_C.js";
import { n as h, t as g } from "./chart-paint-texts-C9chlISz.js";
function _(e) {
	return Object.freeze(e.flatMap((e) => e.substitutions ?? []));
}
var v = `${String.fromCharCode(...Array.from({ length: 95 }, (e, t) => 32 + t))}…`, y = new Set([
	"horz",
	"vert",
	"vert270",
	"mongolianVert",
	"eaVert",
	"wordArtVert",
	"wordArtVertRtl"
]), b = new Set([
	"eaVert",
	"wordArtVert",
	"wordArtVertRtl"
]), x = /^[\x20-\x7e]*$/;
function S(e) {
	return (e.styles?.cellXfs ?? []).some((e) => e.textRotation === 255);
}
var C = class {
	workbook;
	cjkLang;
	scopedScripts = /* @__PURE__ */ new Map();
	scripts;
	families = /* @__PURE__ */ new Map();
	fallbacks = /* @__PURE__ */ new Set();
	proven = /* @__PURE__ */ new Map();
	committed = /* @__PURE__ */ new Set();
	all = !1;
	collector;
	freshFamilies = /* @__PURE__ */ new Map();
	scannedRows = /* @__PURE__ */ new WeakMap();
	scannedParts = /* @__PURE__ */ new WeakSet();
	symbolStyleFamilies;
	constructor(t, a, o) {
		this.workbook = t;
		for (let t of o) {
			if (!t.script) continue;
			let n = e(t.for);
			this.scopedScripts.set(n, (this.scopedScripts.get(n) ?? /* @__PURE__ */ new Set()).add(t.script));
		}
		let s = null;
		for (let e of t.styles?.fonts ?? []) s ??= n(e.name);
		this.cjkLang = s ?? a, this.scripts = new r(this.cjkLang), this.collector = this.newCollector(), this.symbolStyleFamilies = [...new Set((t.styles?.fonts ?? []).map((e) => e.name?.trim() ?? "").filter(i))], S(t) && this.collector.add(g), this.collector.addSymbolText(v, this.symbolStyleFamilies);
		for (let e of t.styles?.fonts ?? []) this.addCellFont(e);
		for (let e of t.sharedStrings ?? []) {
			e.runs?.length || this.addText(e.text, void 0, /[\uF020-\uF0FF]/u.test(e.text) ? this.symbolStyleFamilies : void 0);
			for (let t of e.runs ?? []) t.font?.name && this.addFamily(t.font.name), this.addText(t.text, t.font?.name, /[\uF020-\uF0FF]/u.test(t.text) ? this.symbolStyleFamilies : void 0);
			for (let t of e.phoneticRuns ?? []) this.addText(t.text, this.phoneticFamily(e.phoneticPr));
		}
		let c = f(t.styles);
		c.complete || this.collector.decline();
		let l = (e) => t.styles?.fonts?.[e ?? 0]?.name?.trim() || "Calibri", u = /* @__PURE__ */ new Map();
		(t.styles?.cellXfs ?? []).forEach((e, t) => {
			let n = c.cellXfs[t];
			if (!n?.length) return;
			let r = l(e.fontId), i = u.get(r) ?? /* @__PURE__ */ new Set();
			if (!i.has(n)) {
				i.add(n), u.set(r, i);
				for (let e of n) this.addText(e, r);
			}
		});
		let d = [...new Set((t.styles?.fonts ?? []).map((e) => e.name?.trim() || "Calibri"))];
		for (let e of c.dxfs) {
			this.addText(e, void 0, this.symbolStyleFamilies);
			for (let t of d) this.prove(t, e);
		}
	}
	newCollector() {
		return new m({
			budget: Infinity,
			committed: this.committed
		});
	}
	addText(e, t, n = [], r = !1) {
		e && ((r || !t) && n.length === 0 && x.test(e) || (this.collector.addSymbolText(e, [t, ...n]), this.scripts.addText([e])), t && this.prove(t, e));
	}
	prove(n, r) {
		let i = e(n), a = this.scopedScripts.get(i);
		if (a) for (let e of a) {
			if (this.proven.get(i)?.has(e) || !t({ script: e }, r, "any")) continue;
			this.proven.set(i, (this.proven.get(i) ?? /* @__PURE__ */ new Set()).add(e));
			let n = this.families.get(i);
			n && this.freshFamilies.set(i, n);
		}
	}
	addFamily(t) {
		let n = t?.trim();
		if (!n || n.startsWith("+")) return;
		let r = e(n);
		r && (this.families.has(r) || (this.families.set(r, n), this.freshFamilies.set(r, n)));
	}
	addCellFont(e) {
		let t = e.name?.trim() || "Calibri";
		this.addFamily(t);
		let n = /^(.*?)\s+Regular$/i.exec(t);
		n?.[1]?.trim() && this.addFamily(n[1].trim());
	}
	phoneticFamily(e) {
		let t = this.workbook.styles?.fonts ?? [];
		return (t[e?.fontId ?? 0] ?? t[0])?.name?.trim() || "Calibri";
	}
	fontOfCell(e, t) {
		let n = e ? u(e, t, t.col) : t.styleIndex ?? 0, r = this.workbook.styles ? p(this.workbook.styles, n) : void 0;
		return r ? this.workbook.styles.fonts?.[r.fontId] : void 0;
	}
	rows(e, t) {
		let n = t ? d(t) : !1;
		for (let r of e) for (let e of r.cells) {
			let r = e.value;
			if (r.type !== "text" && r.type !== "error") continue;
			let i = this.fontOfCell(t, e), a = i?.name?.trim() || "Calibri";
			if (r.type === "error") {
				this.collector.addSymbolText(r.error, [a]);
				continue;
			}
			if (r.runs?.length) for (let e of r.runs) e.font?.name && this.addFamily(e.font.name), this.addText(e.text, e.font?.name?.trim() || a);
			else this.addText(r.text, a, [], !0);
			if (n && i?.scheme) {
				let e = i.scheme === "major" ? t?.themeJapaneseMajorFont : t?.themeJapaneseMinorFont;
				e && this.prove(e, r.text);
			}
			for (let e of r.phoneticRuns ?? []) this.addText(e.text, this.phoneticFamily(r.phoneticPr));
		}
	}
	newRowsOf(e) {
		let t = e.rows ?? [], n = this.scannedRows.get(t) ?? 0;
		t.length > n && this.rows(t.slice(n), e), this.scannedRows.set(t, t.length);
	}
	worksheetParts(e) {
		if (!this.scannedParts.has(e)) {
			this.scannedParts.add(e), d(e) && (this.addFamily(e.themeJapaneseMajorFont), this.addFamily(e.themeJapaneseMinorFont));
			for (let t of e.charts ?? []) {
				for (let e of l(t.chart)) this.addFamily(e);
				let e = h(t.chart);
				if (e === "all") this.collector.decline();
				else for (let t of e) this.collector.add(t);
			}
			for (let t of e.shapeGroups ?? []) for (let e of t.shapes) this.shape(e);
			for (let t of e.slicers ?? []) {
				let e = t.style?.header, n = [t.style?.selectedItemWithData, t.style?.unselectedItemWithData];
				for (let r of [
					e,
					...n,
					t.style?.whole
				]) r?.fontFamily && this.addFamily(r.fontFamily);
				this.addText(t.caption, e?.fontFamily);
				for (let e of t.items) {
					this.addText(e.name, void 0, n.map((e) => e?.fontFamily));
					for (let t of n) t?.fontFamily && this.prove(t.fontFamily, e.name);
				}
			}
		}
	}
	shape(e) {
		let t = e.text;
		if (t) {
			t.vert !== void 0 && !y.has(t.vert) && this.collector.decline(), t.vert !== void 0 && b.has(t.vert) && this.collector.add(g);
			for (let e of t.paragraphs) for (let t of e.runs) {
				if (t.type === "math" || t.type !== "text") continue;
				let e = t.fontFace?.trim() || "Calibri", n = t.fontFaceEa?.trim(), r = t.fontFaceSym?.trim();
				this.addFamily(e), n && this.addFamily(n), r && this.addFamily(r), this.addText(t.text, e, [r]), n && this.prove(n, t.text);
			}
		}
	}
	take() {
		let e = this.collector.result(), t = e === "all" && !this.all, n = e === "all" ? [] : e, r = this.scripts.names().filter((e) => !this.fallbacks.has(e)), i = [...this.freshFamilies.values()];
		if (!t && n.length === 0 && i.length === 0 && r.length === 0) return null;
		let a = Object.create(null);
		for (let e of this.freshFamilies.keys()) a[e] = Object.freeze([...this.proven.get(e) ?? []].sort());
		let o = Object.freeze({
			families: Object.freeze(i),
			fallbackFamilies: Object.freeze(r),
			scalars: this.all || t ? "all" : Object.freeze(n),
			substituteScripts: Object.freeze(a)
		});
		for (let e of r) this.fallbacks.add(e);
		if (e === "all") this.all = !0;
		else for (let e of n) this.committed.add(e);
		return this.freshFamilies = /* @__PURE__ */ new Map(), this.all || (this.collector = this.newCollector()), o;
	}
};
export { a as FontSourceSession, c as InstalledFamilyExclusion, C as XlsxFontDemand, _ as declaredFontSubstitutions, s as inRealmResolverFaceAcquirer, o as metafileFontDemand };
