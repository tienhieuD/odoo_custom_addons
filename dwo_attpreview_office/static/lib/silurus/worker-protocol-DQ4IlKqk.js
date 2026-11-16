import { u as e } from "./number-format-CKqKnRTi.js";
import { r as t } from "./worksheet-policy-context-CntId_kd.js";
import { l as n, o as r, t as i, u as a } from "./grid-geometry-yvWZvfnR.js";
function o(e, t) {
	let n = !1;
	for (let [r, i] of Object.entries(t)) {
		let t = Number(r);
		i === null ? Object.hasOwn(e, t) && (delete e[t], n = !0) : e[t] !== i && (e[t] = i, n = !0);
	}
	return n;
}
function s(e, t) {
	if (!t) return;
	let r = !1;
	if (t.rowHeightRanges && (a(e, t.rowHeightRanges), r = !0), t.rows && (r = o(e.rowHeights, t.rows) || r), t.cols && (r = o(e.colWidths, t.cols) || r), t.columnCssWidths) for (let [i, a] of Object.entries(t.columnCssWidths)) n(e, Number(i), a) && (r = !0);
	r && i.invalidate(e);
}
function c(e, t) {
	return t ? l(e, t) : e;
}
function l(n, i) {
	let a = { ...n };
	return i && (a.rowHeights = { ...n.rowHeights }, a.colWidths = { ...n.colWidths }), e(n, a), t(n, a), r(n, a), s(a, i), a;
}
var u = Symbol("xlsx-viewer-render-context");
function d(e, t, n) {
	if (!Number.isFinite(t) || t <= 0) throw Error("XLSX maximum digit width must be a finite positive number");
	return {
		...e,
		[u]: {
			maximumDigitWidth: t,
			worksheet: n?.worksheet,
			projection: n?.projection
		}
	};
}
function f(e) {
	let t = e[u], n = { ...e };
	return delete n[u], t ? {
		opts: n,
		layoutMetrics: { maximumDigitWidth: t.maximumDigitWidth },
		worksheet: t.worksheet,
		projection: t.projection
	} : { opts: n };
}
export { f as n, d as r, c as t };
