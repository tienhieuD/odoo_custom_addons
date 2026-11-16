import { r as e } from "./own-key-CzMRhMxt.js";
import { H as t, I as n, L as r, M as i, S as a, V as o, _ as s, g as c, w as l } from "./wmf-HY7sNn5s.js";
import { n as u } from "./substitutions-_KDT_mVq.js";
import { n as d } from "./ooxml-error-DbICW35n.js";
import { n as f } from "./font-registry-CA7E7o7P.js";
import { h as p } from "./resource-policy.generated-D_HlV2Rm.js";
import { a as m, c as h, h as g, i as _, m as v, o as y, p as b, u as x } from "./substitute-script-COw3MRyd.js";
import { c as S, d as C, i as w, n as T, o as E, s as D, t as O } from "./scripts-DxEAUeVI.js";
import { t as k } from "./symbol-font-Cf7Xu0_f.js";
import { A, D as j, E as M, R as N, S as ee, b as te, f as ne, g as P, h as F, l as I, o as L, r as R, u as z } from "./segment-line-BR56kM-V.js";
import { T as B, a as re, c as ie, d as ae, f as V, l as H, m as U, n as oe, o as se, p as ce, r as le, s as W, w as G, x as ue, y as de } from "./vertical-vert-feature-ru96Mg5B.js";
import { $n as fe, nr as pe, qn as me, u as he } from "./plot-area-frame-BSqoSYxZ.js";
import { a as K, i as ge, o as q } from "./units-BBDOirYi.js";
import { l as _e, m as ve, n as ye, o as J, p as be, s as xe } from "./paint-s8gGHFU5.js";
import { g as Se, m as Ce } from "./chart-number-format-BTQAc_0Z.js";
import { H as we, r as Te } from "./renderer-D3GIB31w.js";
import { r as Ee } from "./drawingml-shape-CzD75ylB.js";
import { n as De, r as Oe } from "./chart-font-sources-B96UtO2E.js";
import { n as ke } from "./office-auto-line-D6xJtpwV.js";
import { a as Ae, c as je, d as Me, f as Ne, g as Pe, h as Fe, i as Ie, m as Le, n as Re, o as ze, p as Be, r as Ve, s as He, t as Ue, u as We } from "./stacked-glyphs-B5TfEXN9.js";
import { a as Ge, c as Ke, f as qe, i as Je, n as Ye, s as Xe, u as Ze } from "./number-format-CKqKnRTi.js";
import { n as Qe, r as $e } from "./worksheet-policy-context-CntId_kd.js";
import { c as et, m as tt, p as nt, s as rt, t as it } from "./grid-geometry-yvWZvfnR.js";
function at(e, t, n) {
	let { values: r } = n;
	if (r.length === 0 || t.w <= 0 || t.h <= 0) return;
	let i = n.colorSeries ?? "#5B9BD5", a = Math.min(2, t.w * .08), o = Math.max(2, t.h * .2), s = t.x + a, c = t.y + o, l = Math.max(1, t.w - a * 2), u = Math.max(1, t.h - o * 2), d = r.filter((e) => typeof e == "number");
	if (d.length === 0) return;
	let f = Math.min(...d), p = Math.max(...d), m = n.min ?? f, h = n.max ?? p;
	m === h && (h = m + 1, --m);
	let g = h - m, _ = (e) => c + u - (e - m) / g * u;
	if (n.kind === "stem") {
		ct(e, n, s, c, l, u);
		return;
	}
	if (n.kind === "column") {
		st(e, n, r, s, c, l, u, m, h);
		return;
	}
	if (n.displayXAxis && m < 0 && h > 0) {
		e.save(), e.strokeStyle = n.colorAxis ?? "#000000", e.lineWidth = 1, e.beginPath();
		let t = _(0);
		e.moveTo(s, t), e.lineTo(s + l, t), e.stroke(), e.restore();
	}
	let v = r.length, y = (e) => v === 1 ? s + l / 2 : s + e / (v - 1) * l;
	e.save(), e.strokeStyle = i, e.lineCap = "round", e.lineJoin = "round", e.lineWidth = (n.lineWeight ?? .75) * q, e.beginPath();
	let b = !1, x = n.displayEmptyCellsAs ?? "gap";
	for (let t = 0; t < v; t++) {
		let n = r[t];
		if (n == null) {
			if (x === "zero") {
				let n = y(t), r = _(0);
				b ? e.lineTo(n, r) : (e.moveTo(n, r), b = !0);
			} else x === "gap" && (b = !1);
			continue;
		}
		let i = y(t), a = _(n);
		b ? e.lineTo(i, a) : (e.moveTo(i, a), b = !0);
	}
	e.stroke(), e.restore();
	let S = Math.max(1, Math.min(2.5, u * .12)), C = ot(r, n);
	for (let t = 0; t < v; t++) {
		let a = r[t];
		if (a == null) continue;
		let o = C[t];
		(n.markers || o != null) && (e.save(), e.fillStyle = o ?? n.colorMarkers ?? i, e.beginPath(), e.arc(y(t), _(a), S, 0, Math.PI * 2), e.fill(), e.restore());
	}
}
function ot(e, t) {
	let n = e.map(() => null), r = e.map((e) => typeof e == "number" ? e : null), i = r.findIndex((e) => e != null), a = -1;
	for (let e = r.length - 1; e >= 0; e--) if (r[e] != null) {
		a = e;
		break;
	}
	let o = r.filter((e) => e != null), s = NaN, c = NaN;
	if (o.length > 0 && (s = Math.max(...o), c = Math.min(...o)), t.negative && t.colorNegative) for (let e = 0; e < r.length; e++) {
		let i = r[e];
		i != null && i < 0 && (n[e] = t.colorNegative);
	}
	if (t.first && t.colorFirst && i >= 0 && (n[i] = t.colorFirst), t.last && t.colorLast && a >= 0 && (n[a] = t.colorLast), t.high && t.colorHigh && !Number.isNaN(s)) for (let e = 0; e < r.length; e++) r[e] === s && (n[e] = t.colorHigh);
	if (t.low && t.colorLow && !Number.isNaN(c)) for (let e = 0; e < r.length; e++) r[e] === c && (n[e] = t.colorLow);
	return n;
}
function st(e, t, n, r, i, a, o, s, c) {
	let l = n.length;
	if (l === 0) return;
	let u = s < 0 && c > 0 ? 0 : s, d = c - s, f = (e) => i + o - (e - s) / d * o, p = f(u), m = a / l, h = Math.min(1.5, m * .15), g = ot(n, t);
	for (let i = 0; i < l; i++) {
		let a = n[i];
		if (a == null) continue;
		let o = g[i] ?? (a < 0 && t.colorNegative ? t.colorNegative : t.colorSeries ?? "#5B9BD5"), s = f(a), c = r + m * i + h / 2, l = Math.max(1, m - h);
		e.save(), e.fillStyle = o, e.fillRect(c, Math.min(p, s), l, Math.abs(p - s)), e.restore();
	}
}
function ct(e, t, n, r, i, a) {
	let o = t.values.length;
	if (o === 0) return;
	let s = r + a / 2, c = a / 2, l = i / o, u = Math.min(1.5, l * .15), d = ot(t.values, t);
	for (let r = 0; r < o; r++) {
		let i = t.values[r];
		if (i == null || i === 0) continue;
		let a = i < 0, o = d[r] ?? (a && t.colorNegative ? t.colorNegative : t.colorSeries ?? "#5B9BD5"), f = n + l * r + u / 2, p = Math.max(1, l - u);
		e.save(), e.fillStyle = o, a ? e.fillRect(f, s, p, c) : e.fillRect(f, s - c, p, c), e.restore();
	}
}
function lt(e, t) {
	return e === !0 ? "rtl" : e === !1 ? "ltr" : l().computeLevels(t, "auto").paragraphLevel === 1 ? "rtl" : "ltr";
}
function ut(e, t, n, r) {
	let i = t;
	for (let t of e) r(t, i, n), i += t.width;
	return i;
}
function dt(e) {
	let t = e.fontFace?.trim();
	if (!t) return;
	let n = (e) => !e?.trim() || e.trim().toLocaleLowerCase("en-US") === t.toLocaleLowerCase("en-US");
	return n(e.fontFaceEa) && n(e.fontFaceCs) ? t : void 0;
}
function ft(e) {
	let t = [];
	for (let n of e.paragraphs) for (let e of n.runs) e.type === "text" && dt(e) && t.push(e);
	return t;
}
function pt(e) {
	return e && (e.type === "pts" ? {
		type: "pts",
		val: Math.floor(e.val + .5)
	} : {
		type: "pct",
		val: Math.floor(e.val / 1e3 + .5) * 1e3
	});
}
function mt(e) {
	let t = e.family.trim().toLowerCase(), n = e.weight ?? 400, r = e.style ?? "normal";
	return n === 400 && r === "normal" ? t : `${t}:${n}:${r}`;
}
function ht(e) {
	return mt({
		family: e.fontFace,
		weight: e.bold ? 700 : 400,
		style: e.italic ? "italic" : "normal"
	});
}
var gt = 1e3, _t = 2 / gt, vt = /* @__PURE__ */ new WeakMap();
function yt(e) {
	return (t) => {
		let n = vt.get(t);
		if (n !== void 0) return n ?? void 0;
		let r = e.font, i = null;
		try {
			e.font = `${t.style} ${t.weight} ${gt}px "${t.family}"`;
			let n = e.measureText("H"), r = n.fontBoundingBoxAscent, a = n.fontBoundingBoxDescent;
			Number.isFinite(r) && Number.isFinite(a) && r + a > 0 && (i = {
				ascent: r / gt,
				descent: a / gt
			});
		} finally {
			e.font = r;
		}
		return vt.set(t, i), i ?? void 0;
	};
}
var bt = (e) => e.source === "macos-system" || e.source === "macos-supplemental";
function xt(e) {
	if (e.source !== "published-open-font" && !(e.farEastCodePage == null || !e.win)) return ke({
		faceSource: bt(e) ? "system" : "office-bundle",
		unitsPerEm: e.unitsPerEm,
		hhea: e.hhea,
		win: e.win,
		typoMetrics: e.typoMetrics,
		farEastCodePage: e.farEastCodePage
	}) ?? void 0;
}
function St(e) {
	let t;
	for (let n of e) {
		let e = xt(n);
		if (!e || t && (e.ascentRatio !== t.ascentRatio || e.descentRatio !== t.descentRatio)) return;
		t = e;
	}
	return t;
}
function Ct(e, t) {
	let n = t.unitsPerEm, r = [[t.hhea[0], -t.hhea[1]]];
	return t.win && r.push(t.win), t.typoMetrics && r.push([t.typoMetrics[0], -t.typoMetrics[1]]), r.some(([t, r]) => Math.abs(e.ascent - t / n) <= _t && Math.abs(e.descent - r / n) <= _t);
}
function wt(e, t, n) {
	let r = dt(e);
	if (!r || !t || t.source !== "local" || t.metric.synthesized || !t.resourceIdentity.startsWith("office-local:") || t.requestedFamily.toLocaleLowerCase("en-US") !== r.toLocaleLowerCase("en-US") || t.weight !== (e.bold ? 700 : 400) || t.style !== (e.italic ? "italic" : "normal")) return;
	let i = C(r, {
		weight: t.weight,
		style: t.style
	});
	if (i.length === 0) return;
	let a = St(i);
	if (a || i.length === 1) return a;
	let o = n?.(t);
	if (!o) return;
	let s = i.filter((e) => Ct(o, e));
	if (s.length !== 0 && !(i.some(bt) && !s.every(bt))) return St(s);
}
function Tt(e, t) {
	if (e.length === 0 || t.length === 0) return 0;
	let n = [...e, ...t], r = e.length;
	return r - I(n, r, z, 1);
}
function Et(e, t) {
	let n = t;
	for (; n < e.length;) {
		let t = e[e.length - n - 1], r = e[e.length - n], i = t?.codePointAt(0), a = r?.codePointAt(0);
		if (i !== void 0 && a !== void 0 && g(i) && g(a)) n++;
		else break;
	}
	return n >= e.length ? t : n;
}
function Dt(e, t) {
	if (e.length === 0 || t.length === 0) return 0;
	let n = t[0].codePointAt(0), r = e.length - 1, i = e[r].codePointAt(0);
	if (i === void 0 || n === void 0 || i === 8203 || n === 8203 || !L(i, n)) return 0;
	for (; r > 0;) {
		let t = e[r - 1].codePointAt(0), n = e[r].codePointAt(0);
		if (t === void 0 || n === void 0 || !L(t, n)) break;
		r--;
	}
	return r === 0 ? 0 : e.length - r;
}
function Ot(e, t, n) {
	let r = [], i = [], a = 0;
	for (; a < e.length;) {
		let t = e[a], n = t.codePointAt(0) ?? 0;
		if (v(n)) i.push(t), a += n > 65535 ? 2 : 1;
		else if (t === " ") {
			let t = a;
			for (; t < e.length && e[t] === " ";) t++;
			i.push(e.slice(a, t)), a = t;
		} else {
			let t = a;
			for (; t < e.length;) {
				let n = e[t], r = n.codePointAt(0) ?? 0;
				if (n === " " || v(r)) break;
				t += r > 65535 ? 2 : 1;
			}
			let n = e.slice(a, t), r = m(n) ? b(n) : null;
			if (r && r.length > 0) {
				let e = 0;
				for (let t of r) i.push(n.slice(e, t)), e = t;
				i.push(n.slice(e));
			} else i.push(n);
			a = t;
		}
	}
	let o = "";
	for (let e of i) {
		if (o === "") {
			o = e;
			continue;
		}
		let i = o + e;
		if (n(i) <= t) o = i;
		else {
			let t = e.replace(/^ +/, "");
			t === "" && (t = e);
			let n = [...o], i = Tt(n, [...t]);
			if (i > 0) {
				let e = n.length - i;
				r.push(n.slice(0, e).join("")), o = n.slice(e).join("") + t;
			} else r.push(o), o = t;
		}
	}
	return r.push(o), r;
}
function kt(e, t, n, r, i, a, o) {
	let s = [], c = [], l = 0, u = 0, d = n.size, f = 0, p = () => {
		c.length !== 0 && (s.push({
			segments: c,
			maxFontSize: u,
			para: f
		}), c = [], l = 0, u = 0);
	}, g = () => {
		if (c.length === 0) {
			s.push({
				segments: [],
				maxFontSize: d || o,
				para: f
			});
			return;
		}
		p();
	}, _ = (t, n) => {
		if (!t) return;
		d = n.size, a(n, t);
		let i = e.measureText(t).width;
		if (c.length > 0 && l + i > r) {
			let r = c.flatMap((e) => [...e.text]), i = Tt(r, [...t]);
			i > 0 ? i = Et(r, i) : !m(t) && !m(c[c.length - 1]?.text ?? "") && !/^\s/u.test(t) && !/\s$/u.test(r.at(-1) ?? "") && (i = Dt(r, [...t]));
			let o = c[c.length - 1], s = [...o.text];
			i > s.length && (i = s.length);
			let d = null;
			if (i > 0) {
				let t = s.slice(0, s.length - i), n = s.slice(s.length - i);
				if (t.length === 0) c.pop();
				else {
					let n = t.join("");
					a(o.font, n), o.text = n, o.width = e.measureText(n).width;
				}
				let r = n.join("");
				a(o.font, r), d = {
					text: r,
					font: o.font,
					width: e.measureText(r).width
				};
			}
			p(), d && (c.push(d), l += d.width, d.font.size > u && (u = d.font.size)), a(n, t);
		}
		c.push({
			text: t,
			font: n,
			width: i
		}), l += i, n.size > u && (u = n.size);
	}, S = (t, n) => {
		let i = b(t);
		if (i.length === 0) {
			_(t, n);
			return;
		}
		a(n, t);
		let o = (t) => e.measureText(t).width, s = x(t), c = t.length, u = 0;
		for (; u < c;) {
			let e = r - l, a = y(t, i, u, e, o, s);
			if (a <= u) {
				if (l > 0) {
					p();
					continue;
				}
				let n = i.find((e) => e > u) ?? c, r = t.slice(u, n), d = h(r), f = y(r, d, 0, e, o, s);
				f <= 0 && (f = d.length > 0 ? d[0] : r.length), a = u + f;
			}
			_(t.slice(u, a), n), u = a, u < c && p();
		}
	};
	for (let e of t) {
		let t = i(n, e), r = [], a = 0;
		for (; a < e.text.length;) {
			let t = e.text[a], n = t.codePointAt(0) ?? 0;
			if (n === 10) r.push("\n"), a += 1;
			else if (v(n)) r.push(t), a += n > 65535 ? 2 : 1;
			else if (t === " ") {
				let t = a;
				for (; t < e.text.length && e.text[t] === " ";) t++;
				r.push(e.text.slice(a, t)), a = t;
			} else {
				let t = a;
				for (; t < e.text.length;) {
					let n = e.text[t], r = n.codePointAt(0) ?? 0;
					if (n === " " || n === "\n" || v(r)) break;
					t += r > 65535 ? 2 : 1;
				}
				r.push(e.text.slice(a, t)), a = t;
			}
		}
		for (let e of r) e === "\n" ? (g(), f++) : m(e) ? S(e, t) : _(e, t);
	}
	return (c.length > 0 || s.length > 0) && g(), s;
}
function At(e, t, n, r, i, a, o) {
	let s = (t, n) => {
		e.font = n.font;
		let r = He(n.face ?? "", n.bold, n.italic), i = r ? void 0 : e.measureText("M"), a = r ? r.ascent * n.px : i?.fontBoundingBoxAscent ?? n.px, o = r ? r.descent * n.px : i?.fontBoundingBoxDescent ?? 0, s = ze * (a + o);
		return Ve(t, {
			family: n.face ?? "",
			bold: n.bold,
			italic: n.italic
		}, {
			upright: s,
			verticalGlyph: n.px,
			rotated: (t) => e.measureText(t).width
		}).map(({ text: e, kind: t, advance: r, nominal: i }) => ({
			text: e,
			style: n,
			kind: t,
			advance: r + n.spacing,
			thickness: s,
			space: e === " ",
			cell: s,
			ascent: a,
			descent: o,
			...i ? { nominal: i } : {}
		}));
	}, c = (e, t) => !e.equation && !t.equation && e.font === t.font && e.color === t.color && e.spacing === t.spacing, l = je(t.paragraphs.map((e) => {
		let t = [], n, r = "", l = 11;
		for (let s of e.runs) {
			if (s.type === "break") {
				t.push({ type: "break" });
				continue;
			}
			if (s.type === "math") {
				let e = o(s, l);
				if (!e) continue;
				let n = {
					font: "",
					px: 0,
					color: s.color ?? "#000000",
					spacing: 0,
					bold: !1,
					italic: !1,
					equation: e
				};
				t.push({
					type: "object",
					width: e.height,
					style: n,
					display: s.display
				}), r = "";
				continue;
			}
			l = s.size > 0 ? s.size : 11;
			let e = "", u, d = () => {
				u && e && t.push({
					type: "text",
					text: e,
					style: u
				});
			};
			for (let t of s.text) {
				let n = /^[\p{M}\p{Cf}]$/u.test(t) && r ? r : t, o = a(s, n);
				r = n;
				let l = {
					...o,
					color: s.color ?? "#000000",
					spacing: (s.spacing ?? 0) * i,
					bold: s.bold,
					italic: s.italic
				};
				u && !c(u, l) && (d(), e = ""), u = l, e += t;
			}
			u ??= {
				...a(s, "M"),
				color: s.color ?? "#000000",
				spacing: (s.spacing ?? 0) * i,
				bold: s.bold,
				italic: s.italic
			}, n = u, d(), s.text === "" && t.push({
				type: "text",
				text: "",
				style: u
			});
		}
		let u = {
			font: `${11 * i}px sans-serif`,
			px: 11 * i,
			color: "#000000",
			spacing: 0,
			bold: !1,
			italic: !1
		};
		return {
			runs: t,
			alignment: e.align,
			lineSpacing: pt(e.spaceLine),
			spaceBefore: pt(e.spaceBefore),
			spaceAfter: pt(e.spaceAfter),
			emptyThickness: s("M", n ?? u)[0].thickness
		};
	}), {
		direction: n,
		rect: r,
		anchor: t.anchor,
		anchorCtr: t.anchorCtr,
		wrap: t.wrap !== "none",
		spcFirstLastPara: t.spcFirstLastPara,
		lnSpcReduction: t.autoFit === "norm" ? t.lnSpcReduction ?? 0 : 0,
		pxPerPt: i,
		glyphs: s,
		sameStyle: c,
		objectGlyph: ({ style: e }) => {
			let t = e.equation;
			return {
				text: "",
				style: e,
				kind: "upright",
				advance: t.height,
				thickness: t.width,
				space: !1,
				cell: t.height,
				ascent: 0,
				descent: 0
			};
		}
	});
	e.save();
	for (let t of l.glyphs) {
		if (t.style.equation) {
			t.style.equation.draw(t.axisX - t.thickness / 2, t.cellTop);
			continue;
		}
		if (!t.space) if (e.font = t.style.font, e.fillStyle = t.style.color, e.textAlign = "center", e.textBaseline = "alphabetic", t.kind === "upright") e.fillText(t.text, t.axisX, Ie(t.cellTop, t.cell, t, 1));
		else {
			let n = t.kind === "verticalGlyph" ? Ae(t) : null;
			n === null ? Ue(e, t.text, t.axisX, t.cellTop, t, 1) : Re(e, n, t.axisX, t.cellTop, t, 1);
		}
	}
	e.restore();
}
var jt = [
	"bold",
	"italic",
	"underline",
	"strike"
];
function Mt(e, t) {
	if (e.font) return e.fontToggles ? e.fontToggles[t] : e.font[t] || void 0;
}
var Nt = p, Pt = 2 ** 53 - 1 - 1;
function Ft(e) {
	let t = e.limit;
	if (t === void 0) return Nt;
	if (typeof t != "number") throw TypeError("coordinate index limit must be a number");
	if (!Number.isSafeInteger(t) || t <= 0 || t > Pt) throw RangeError(`coordinate index limit must be a positive safe integer no greater than ${Pt}`);
	return t;
}
function It(e, t, n, r) {
	return new d(`XLSX renderer ${e.resource} exceeded its limit of ${t} entries`, {
		stage: "rendering",
		violation: {
			format: "xlsx",
			operation: e.operation,
			resource: e.resource,
			metric: "entry-count",
			limit: t,
			observed: Math.min(n, t + 1),
			configurable: r,
			usage: {
				archiveEntryCount: 0,
				declaredInflatedBytes: 0,
				distinctInflatedBytes: 0,
				operationInflatedBytes: 0
			}
		}
	});
}
function Lt(e, t, n = 0) {
	let r = Ft(t), { top: i, bottom: a, left: o, right: s } = e;
	if (!Number.isSafeInteger(i) || !Number.isSafeInteger(a) || !Number.isSafeInteger(o) || !Number.isSafeInteger(s) || !Number.isSafeInteger(n) || n < 0) throw It(t, r, r + 1, !1);
	if (a < i || s < o) return 0;
	let c = a - i + 1, l = s - o + 1;
	if (!Number.isSafeInteger(c) || !Number.isSafeInteger(l)) throw It(t, r, r + 1, !1);
	let u;
	if (l <= Math.floor((2 ** 53 - 1) / c)) {
		let e = c * l;
		if (n > e) throw It(t, r, r + 1, !1);
		u = e - n;
	} else {
		let e = BigInt(c) * BigInt(l), i = BigInt(n);
		if (i > e) throw It(t, r, r + 1, !1);
		let a = e - i;
		if (a > BigInt(2 ** 53 - 1)) throw It(t, r, r + 1, !1);
		u = Number(a);
	}
	if (u > r) throw It(t, r, u, !0);
	return u;
}
function Rt(e, t, n, r) {
	let i = Ft(r);
	if (!e.has(t) && e.size >= i) throw It(r, i, e.size + 1, !0);
	e.set(t, n);
}
function zt(e, t) {
	let n = /* @__PURE__ */ new Map();
	for (let r of e) for (let e of r.cells) Rt(n, `${e.row}:${e.col}`, e, t);
	return n;
}
function Bt(e, t, n) {
	let r = Ft(n);
	if (!e.has(t) && e.size >= r) throw It(n, r, e.size + 1, !0);
	e.add(t);
}
var Vt = [
	"wholeTable",
	"pageFieldLabels",
	"pageFieldValues",
	"firstColumnStripe",
	"secondColumnStripe",
	"firstRowStripe",
	"secondRowStripe",
	"firstColumn",
	"headerRow",
	"firstHeaderCell",
	"firstSubtotalColumn",
	"secondSubtotalColumn",
	"thirdSubtotalColumn",
	"blankRow",
	"firstSubtotalRow",
	"secondSubtotalRow",
	"thirdSubtotalRow",
	"firstColumnSubheading",
	"secondColumnSubheading",
	"thirdColumnSubheading",
	"firstRowSubheading",
	"secondRowSubheading",
	"thirdRowSubheading",
	"lastColumn",
	"totalRow"
], Ht = new Set([
	"default",
	"sum",
	"countA",
	"avg",
	"max",
	"min",
	"product",
	"count",
	"stdDev",
	"stdDevP",
	"var",
	"varP"
]);
function Ut(e) {
	return e === 0 ? "first" : e % 2 == 1 ? "second" : "third";
}
function Wt(e, t, n, r) {
	let i = {
		first: [],
		second: []
	}, a = e, o = !0;
	for (; a <= t;) {
		let e = Math.min(t, a + Math.max(1, o ? n : r) - 1);
		(o ? i.first : i.second).push({
			top: a,
			bottom: e,
			left: 0,
			right: 0
		}), a = e + 1, o = !o;
	}
	return i;
}
function Gt(e, t) {
	let n = e.style, { top: r, bottom: i, left: a, right: o, firstDataRow: s, firstDataCol: c } = e.location, l = r + s, u = a + c, d = /* @__PURE__ */ new Map(), f = (e, t) => {
		if (t.top > t.bottom || t.left > t.right) return;
		let n = d.get(e);
		n ? n.push(t) : d.set(e, [t]);
	};
	if (f("wholeTable", {
		top: r,
		bottom: i,
		left: a,
		right: o
	}), n.showColumnStripes) {
		let e = Wt(u, o, t.get("firstColumnStripe") ?? 1, t.get("secondColumnStripe") ?? 1);
		for (let t of e.first) f("firstColumnStripe", {
			top: l,
			bottom: i,
			left: t.top,
			right: t.bottom
		});
		for (let t of e.second) f("secondColumnStripe", {
			top: l,
			bottom: i,
			left: t.top,
			right: t.bottom
		});
	}
	if (n.showRowStripes) {
		let e = Wt(l, i, t.get("firstRowStripe") ?? 1, t.get("secondRowStripe") ?? 1);
		for (let t of e.first) f("firstRowStripe", {
			...t,
			left: a,
			right: o
		});
		for (let t of e.second) f("secondRowStripe", {
			...t,
			left: a,
			right: o
		});
	}
	n.showRowHeaders && f("firstColumn", {
		top: r,
		bottom: i,
		left: a,
		right: u - 1
	}), n.showColumnHeaders && f("headerRow", {
		top: r,
		bottom: l - 1,
		left: a,
		right: o
	}), f("firstHeaderCell", {
		top: r,
		bottom: l - 2,
		left: a,
		right: u - 1
	});
	let p = Math.max(0, e.rowFields.length - 1);
	return (e.rowItems ?? []).forEach((e, t) => {
		let r = l + t;
		if (r > i) return;
		let s = {
			top: r,
			bottom: r,
			left: a,
			right: o
		}, c = Ut(e.depth);
		e.kind === "blank" ? f("blankRow", s) : e.kind === "grand" ? f("totalRow", s) : Ht.has(e.kind) ? f(`${c}SubtotalRow`, s) : e.kind === "data" && e.depth < p && n.showRowHeaders && f(`${c}RowSubheading`, s);
	}), (e.columnItems ?? []).forEach((e, t) => {
		let a = u + t;
		if (a > o) return;
		let s = {
			top: r,
			bottom: i,
			left: a,
			right: a
		}, c = Ut(e.depth);
		e.kind === "grand" ? n.showLastColumn && f("lastColumn", s) : Ht.has(e.kind) && f(`${c}SubtotalColumn`, s);
	}), d;
}
function Kt(e) {
	return e.patternType === "solid" && e.bgColor && e.bgColor !== e.fgColor ? {
		...e,
		fgColor: e.bgColor
	} : e;
}
function qt(e, t, n, r, i, a) {
	t.fill && (e.fill = Kt(t.fill));
	let o = t.font;
	if (o) {
		o.color ? (e.fontColor = o.color, delete e.fontColorAuto, a ? e.fontColorFromTable = !0 : delete e.fontColorFromTable) : t.fontToggles?.automaticColor && (delete e.fontColor, e.fontColorAuto = !0, a ? e.fontColorFromTable = !0 : delete e.fontColorFromTable);
		for (let n of jt) {
			let r = Mt(t, n);
			r !== void 0 && (e[n] = r);
		}
	}
	let s = t.border;
	if (!s) return;
	let c = (e, t, n) => n ? e : t, l = c(s.top, s.horizontal, r === n.top), u = c(s.bottom, s.horizontal, r === n.bottom), d = c(s.left, s.vertical, i === n.left), f = c(s.right, s.vertical, i === n.right);
	l && (e.top = l), u && (e.bottom = u), d && (e.left = d), f && (e.right = f);
}
var Jt = [
	"wholeTable",
	"firstColumnStripe",
	"secondColumnStripe",
	"firstRowStripe",
	"secondRowStripe",
	"lastColumn",
	"firstColumn",
	"headerRow",
	"totalRow",
	"firstHeaderCell",
	"lastHeaderCell",
	"firstTotalCell",
	"lastTotalCell"
];
function Yt(e, t, n, r, i) {
	let a = {
		first: [],
		second: []
	}, o = !0, s = Math.max(1, n), c = null;
	for (let l = e; l <= t; l++) i(l) || (c || (c = {
		top: l,
		bottom: l,
		left: 0,
		right: 0
	}, (o ? a.first : a.second).push(c)), c.bottom = l, --s, s === 0 && (o = !o, s = Math.max(1, o ? n : r), c = null));
	return a;
}
function Xt(e, t, n) {
	let { top: r, bottom: i, left: a, right: o } = e.range, s = Math.max(0, e.headerRowCount ?? 1), c = Math.max(0, e.totalsRowCount ?? 0), l = r + s, u = i - c, d = /* @__PURE__ */ new Map(), f = (e, t) => {
		if (t.top > t.bottom || t.left > t.right) return;
		let n = d.get(e);
		n ? n.push(t) : d.set(e, [t]);
	};
	if (f("wholeTable", {
		top: r,
		bottom: i,
		left: a,
		right: o
	}), e.showColumnStripes) {
		let e = Wt(a, o, t.get("firstColumnStripe") ?? 1, t.get("secondColumnStripe") ?? 1);
		for (let t of e.first) f("firstColumnStripe", {
			top: l,
			bottom: u,
			left: t.top,
			right: t.bottom
		});
		for (let t of e.second) f("secondColumnStripe", {
			top: l,
			bottom: u,
			left: t.top,
			right: t.bottom
		});
	}
	if (e.showRowStripes) {
		let e = Yt(l, u, t.get("firstRowStripe") ?? 1, t.get("secondRowStripe") ?? 1, n);
		for (let t of e.first) f("firstRowStripe", {
			...t,
			left: a,
			right: o
		});
		for (let t of e.second) f("secondRowStripe", {
			...t,
			left: a,
			right: o
		});
	}
	return e.showLastColumn && f("lastColumn", {
		top: r,
		bottom: i,
		left: o,
		right: o
	}), e.showFirstColumn && f("firstColumn", {
		top: r,
		bottom: i,
		left: a,
		right: a
	}), s > 0 && (f("headerRow", {
		top: r,
		bottom: l - 1,
		left: a,
		right: o
	}), f("firstHeaderCell", {
		top: r,
		bottom: l - 1,
		left: a,
		right: a
	}), f("lastHeaderCell", {
		top: r,
		bottom: l - 1,
		left: o,
		right: o
	})), c > 0 && (f("totalRow", {
		top: u + 1,
		bottom: i,
		left: a,
		right: o
	}), f("firstTotalCell", {
		top: u + 1,
		bottom: i,
		left: a,
		right: a
	}), f("lastTotalCell", {
		top: u + 1,
		bottom: i,
		left: o,
		right: o
	})), d;
}
function Zt(e, t, n, r, i, a) {
	let o = new Map(r.map((e) => [e.kind, e]));
	for (let r of n) {
		let n = o.get(r), s = i.get(r);
		if (!(!n || !s)) for (let r of s) for (let i = r.top; i <= r.bottom; i++) for (let o = r.left; o <= r.right; o++) {
			let s = `${i}:${o}`, c = e.get(s);
			c || (c = {}, Rt(e, s, c, t)), qt(c, n.dxf, r, i, o, a);
		}
	}
}
function Qt(e, t) {
	return !t || e.styleError ? [] : [
		["wholeTable", e.wholeTableDxf],
		["headerRow", e.headerRowDxf],
		["totalRow", e.totalRowDxf],
		["firstColumn", e.firstColumnDxf],
		["lastColumn", e.lastColumnDxf],
		["firstRowStripe", e.band1HorizontalDxf],
		["secondRowStripe", e.band2HorizontalDxf]
	].flatMap(([e, n]) => {
		let r = n === void 0 ? void 0 : t[n];
		return r ? [{
			kind: e,
			size: 1,
			dxf: r
		}] : [];
	});
}
function $t(e, t) {
	let n = /* @__PURE__ */ new Map(), r = {
		resource: "worksheet-structured-style-index",
		operation: "expand-structured-style-coordinates",
		limit: Qe(e).maxCoordinateIndexEntries
	}, i = new Set((e.rows ?? []).filter((e) => e.hidden).map((e) => e.index)), a = (e) => i.has(e);
	for (let i of e.tables ?? []) {
		let e = i.styleElements ?? Qt(i, t);
		e.length !== 0 && (Lt(i.range, r), Zt(n, r, Jt, e, Xt(i, new Map(e.map((e) => [e.kind, e.size])), a), !0));
	}
	for (let t of e.pivotTables ?? []) {
		let e = t.style;
		if (!e || e.elements.length === 0) continue;
		let i = new Map(e.elements.map((e) => [e.kind, e.size]));
		Lt(t.location, r), Zt(n, r, Vt, e.elements, Gt(t, i), !1);
	}
	return n;
}
function en(e, t, n) {
	let r = /* @__PURE__ */ new Set(), i = /* @__PURE__ */ new Set(), a = [];
	for (let i of e) Bt(r, `${i.top}:${i.left}`, t), Lt(i, n, 1), i.bottom >= i.top && i.right >= i.left && a.push(i);
	if (a.length === 0) return {
		anchors: r,
		continuations: i
	};
	let o = [...new Set(a.flatMap((e) => [e.left, e.right + 1]))].sort((e, t) => e - t), s = /* @__PURE__ */ new Map();
	o.forEach((e, t) => s.set(e, t));
	let c = o.length - 1, l = new Int32Array(c * 4), u = new Uint8Array(c * 4), d = (e, t, n, r, i, a) => {
		if (!(i < t || n < r)) {
			if (r <= t && n <= i) l[e] += a;
			else {
				let o = t + n >> 1;
				d(e * 2, t, o, r, i, a), d(e * 2 + 1, o + 1, n, r, i, a);
			}
			u[e] = l[e] > 0 || t < n && (u[e * 2] || u[e * 2 + 1]) ? 1 : 0;
		}
	}, f = (e) => {
		let t = 1, n = 0, r = c - 1, i = 0;
		for (;;) {
			if (i += l[t], n === r) return i;
			let a = n + r >> 1;
			e <= a ? (t *= 2, r = a) : (t = t * 2 + 1, n = a + 1);
		}
	}, p = (e, t, n, r) => {
		if (!u[e]) return;
		if (l[e] > 0) {
			let e = r.at(-1);
			e && e[1] === o[t] - 1 ? e[1] = o[n + 1] - 1 : r.push([o[t], o[n + 1] - 1]);
			return;
		}
		let i = t + n >> 1;
		p(e * 2, t, i, r), p(e * 2 + 1, i + 1, n, r);
	}, m = [], h = /* @__PURE__ */ new Map(), g = /* @__PURE__ */ new Map();
	for (let e of a) {
		let t = s.get(e.left), n = s.get(e.right + 1) - 1;
		m.push({
			row: e.top,
			l: t,
			r: n,
			delta: 1
		}, {
			row: e.bottom + 1,
			l: t,
			r: n,
			delta: -1
		});
		let r = `${e.top}:${e.left}`, i = h.get(r);
		if (h.set(r, (i ?? 0) + 1), i === void 0) {
			let t = g.get(e.top);
			t ? t.push(e.left) : g.set(e.top, [e.left]);
		}
	}
	m.sort((e, t) => e.row - t.row);
	let _ = 0;
	for (; _ < m.length;) {
		let e = m[_].row;
		for (; _ < m.length && m[_].row === e;) {
			let { l: e, r: t, delta: n } = m[_++];
			d(1, 0, c - 1, e, t, n);
		}
		if (!u[1] || _ >= m.length) continue;
		let t = m[_].row - 1, r = /* @__PURE__ */ new Set();
		for (let t of g.get(e) ?? []) {
			let n = `${e}:${t}`;
			f(s.get(t)) === h.get(n) && r.add(n);
		}
		let a = [];
		p(1, 0, c - 1, a);
		for (let o = e; o <= t; o++) for (let [t, s] of a) for (let a = t; a <= s; a++) {
			let t = `${o}:${a}`;
			o === e && r.has(t) || Bt(i, t, n);
		}
	}
	return {
		anchors: r,
		continuations: i
	};
}
function tn(e) {
	return Array.from(e);
}
function nn(e, t, n, r, i) {
	let a = tn(t), o = a.length, s = [];
	for (let t of e) {
		let e = t.sb, c = t.eb;
		if (!(e < c) || e >= o) continue;
		let l = Math.min(c, o), u = n + i(a.slice(0, e).join(""), 0), d = i(a.slice(e, l).join(""), e), f = r === "center" ? "center" : r === "distributed" ? "distribute" : "start";
		s.push({
			text: t.text,
			x: u,
			width: d,
			spread: f
		});
	}
	return s;
}
var rn = (e) => e, an = /^[\p{M}\u200C\u200D]$/u;
function on(e) {
	return {
		segments: [{
			authored: e,
			unicode: !1
		}],
		paint: rn
	};
}
function sn(e, t, n, r, i) {
	if (!t || !k(n)) return on(t);
	let a = /* @__PURE__ */ new Map(), o = /* @__PURE__ */ new Set();
	for (let s of new Set(t)) {
		let t = s.codePointAt(0) ?? 0, c = t >= 61472 && t <= 61695;
		if (!c && (t < 32 || t > 255) || !c && e.draws(s, r) === void 0) continue;
		let l = e.segments(s, n, r, i)[0];
		l?.mapped && o.add(s), l && l.text !== s && a.set(s, l.text);
	}
	if (a.size === 0) return on(t);
	let s = [];
	for (let e of t) {
		let t = s.length > 0 && an.test(e) ? s[s.length - 1].unicode : o.has(e), n = s[s.length - 1];
		n && n.unicode === t ? s[s.length - 1] = {
			authored: n.authored + e,
			unicode: t
		} : s.push({
			authored: e,
			unicode: t
		});
	}
	return Object.freeze({
		segments: s,
		paint: (e) => {
			let t = "";
			for (let n of e) t += a.get(n) ?? n;
			return t;
		}
	});
}
var cn = Object.freeze({
	kind: "unsupported",
	reason: "syntax"
}), ln = Object.freeze({
	kind: "unsupported",
	reason: "outOfGrid"
}), un = Object.freeze({
	kind: "unsupported",
	reason: "unresolvedValue"
}), dn = Object.freeze({ kind: "error" }), fn = Object.freeze({
	kind: "value",
	value: null
}), pn = /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/, mn = /^"(?:[^"]|"")*"$/, hn = /^(\$?)([A-Za-z]{1,3})(\$?)(\d{1,7})$/, gn = 1048576, _n = 16384;
function vn(e) {
	let t = e.trim();
	if (mn.test(t)) return t.slice(1, -1).replace(/""/g, "\"");
	if (pn.test(t)) {
		let e = Number(t);
		return Number.isFinite(e) ? e : void 0;
	}
}
function yn(e, t) {
	let n = vn(e);
	if (n !== void 0) return {
		kind: "value",
		value: n
	};
	let r = hn.exec(e.trim());
	if (!r) return cn;
	let i = 0;
	for (let e of r[2].toUpperCase()) i = i * 26 + (e.charCodeAt(0) - 64);
	let a = Number(r[4]);
	if (a < 1 || a > gn || i > _n) return cn;
	let o = r[3] === "$" ? a : a + (t.row - t.anchorRow), s = r[1] === "$" ? i : i + (t.col - t.anchorCol);
	if (o < 1 || o > gn || s < 1 || s > _n) return ln;
	let c = t.cellIndex.get(`${o}:${s}`)?.value;
	if (!c) return fn;
	switch (c.type) {
		case "empty": return fn;
		case "number": return {
			kind: "value",
			value: c.number
		};
		case "text": return {
			kind: "value",
			value: c.text
		};
		case "bool": return {
			kind: "value",
			value: c.bool
		};
		case "error": return dn;
		default: return un;
	}
}
var bn = 1048576, xn = 16384, Sn = class {
	code;
	constructor(e) {
		this.code = e;
	}
}, Y = class extends Error {
	kind;
	code;
	constructor(e, t) {
		super(`CF formula ${e}`), this.kind = e, this.code = t;
	}
};
function Cn(e) {
	return Array.isArray(e) ? e : [e];
}
function wn(e) {
	return Array.isArray(e) ? e[0] ?? 0 : e;
}
function Tn(e) {
	let t = wn(e);
	if (t instanceof Sn) throw new Y("error", t.code);
	return t;
}
function En(e) {
	return e.flatMap(Cn).map((e) => Tn(e));
}
var Dn = 8, On = 128, kn = 64 * 1024;
function An(e) {
	if (e.kind !== "value") return !1;
	try {
		return Mn(e.value);
	} catch (e) {
		if (e instanceof Y) return !1;
		throw e;
	}
}
function jn(e, t) {
	try {
		let n = Un(e, t);
		return n instanceof Sn ? { kind: "error" } : {
			kind: "value",
			value: n
		};
	} catch (e) {
		if (e instanceof Y) return { kind: e.kind };
		throw e;
	}
}
function Mn(e) {
	let t = Tn(e);
	return typeof t == "boolean" ? t : typeof t == "number" ? t !== 0 : typeof t == "string" ? t.length > 0 && t.toUpperCase() !== "FALSE" : !1;
}
function X(e) {
	let t = Tn(e);
	if (typeof t == "number") {
		if (!Number.isFinite(t)) throw new Y("error", "#NUM!");
		return t;
	}
	if (typeof t == "boolean") return +!!t;
	if (t == null) return 0;
	let n = Nn(t);
	if (n === null) throw new Y("error", "#VALUE!");
	return n;
}
function Nn(e) {
	if (!/^ *[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)? *$/u.test(e)) return null;
	let t = Number(e);
	return Number.isFinite(t) ? t : null;
}
function Pn(e) {
	let t = Tn(e);
	return t == null ? "" : typeof t == "boolean" ? t ? "TRUE" : "FALSE" : String(t);
}
function Z(e) {
	return new Sn(e);
}
var Fn = new Set([
	"<",
	">",
	"=",
	"+",
	"-",
	"*",
	"/",
	"&",
	"^",
	"%"
]);
function In(e) {
	let t = [], n = 0, r = e;
	for (; n < r.length;) {
		let e = r[n];
		if (e === " " || e === "	" || e === "\n" || e === "\r") {
			n++;
			continue;
		}
		if (e === "(") {
			t.push({
				kind: "lparen",
				text: e
			}), n++;
			continue;
		}
		if (e === ")") {
			t.push({
				kind: "rparen",
				text: e
			}), n++;
			continue;
		}
		if (e === ",") {
			t.push({
				kind: "comma",
				text: e
			}), n++;
			continue;
		}
		if (e === ":") {
			t.push({
				kind: "colon",
				text: e
			}), n++;
			continue;
		}
		if (e === "\"") {
			let e = n + 1, i = "";
			for (; e < r.length;) {
				if (r[e] === "\"" && r[e + 1] === "\"") {
					i += "\"", e += 2;
					continue;
				}
				if (r[e] === "\"") break;
				i += r[e], e++;
			}
			if (e === r.length) throw new Y("invalid");
			t.push({
				kind: "str",
				text: i
			}), n = e + 1;
			continue;
		}
		if (e === "#") {
			let e = /^#(?:NULL!|DIV\/0!|VALUE!|REF!|NAME\?|NUM!|N\/A|GETTING_DATA)/u.exec(r.slice(n));
			if (!e) throw new Y("unsupported");
			t.push({
				kind: "error",
				text: e[0]
			}), n += e[0].length;
			continue;
		}
		if (e >= "0" && e <= "9" || e === "." && /[0-9]/u.test(r[n + 1] ?? "")) {
			let e = /^(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?/u.exec(r.slice(n));
			if (!e || !Number.isFinite(Number(e[0]))) throw new Y("invalid");
			t.push({
				kind: "num",
				text: e[0]
			}), n += e[0].length;
			continue;
		}
		if (Fn.has(e)) {
			(e === "<" || e === ">") && (r[n + 1] === "=" || e === "<" && r[n + 1] === ">") ? (t.push({
				kind: "op",
				text: r.slice(n, n + 2)
			}), n += 2) : (t.push({
				kind: "op",
				text: e
			}), n++);
			continue;
		}
		if (e === "$" || Ln(e)) {
			let e = n;
			for (; e < r.length && (r[e] === "$" || Rn(r[e]));) e++;
			let i = r.slice(n, e);
			n = e;
			let a = r[n] === "(" ? null : zn(i);
			if (a) t.push({
				kind: "ref",
				text: i,
				ref: a
			});
			else {
				let e = i.toUpperCase();
				(e === "TRUE" || e === "FALSE") && r[n] !== "(" ? t.push({
					kind: "bool",
					text: e
				}) : t.push({
					kind: "name",
					text: i
				});
			}
			continue;
		}
		throw new Y("unsupported");
	}
	return t;
}
function Ln(e) {
	return e >= "A" && e <= "Z" || e >= "a" && e <= "z" || e === "_";
}
function Rn(e) {
	return Ln(e) || e >= "0" && e <= "9" || e === ".";
}
function zn(e) {
	let t = 0, n = !1, r = !1;
	e[t] === "$" && (n = !0, t++);
	let i = t;
	for (; t < e.length && e[t] >= "A" && e[t].toUpperCase() <= "Z" && !(!(e[t] >= "A" && e[t] <= "Z") && !(e[t] >= "a" && e[t] <= "z"));) t++;
	if (t === i) return null;
	let a = e.slice(i, t).toUpperCase();
	e[t] === "$" && (r = !0, t++);
	let o = t;
	for (; t < e.length && e[t] >= "0" && e[t] <= "9";) t++;
	if (t === o || t !== e.length) return null;
	let s = parseInt(e.slice(o, t), 10), c = 0;
	for (let e = 0; e < a.length; e++) c = c * 26 + (a.charCodeAt(e) - 64);
	return s < 1 || s > bn || c > xn ? null : {
		colAbs: n,
		col: c,
		rowAbs: r,
		row: s
	};
}
var Bn = /* @__PURE__ */ new WeakMap();
function Vn(e) {
	return e.replace(/[A-Z]+/gu, (e) => e.toLowerCase());
}
function Hn(e, t) {
	let n = Bn.get(e);
	if (!n || n.size !== e.size) {
		let t = /* @__PURE__ */ new Map();
		for (let n of e.keys()) t.set(Vn(n), n);
		n = {
			size: e.size,
			keys: t
		}, Bn.set(e, n);
	}
	let r = n.keys.get(Vn(t));
	return r === void 0 ? void 0 : e.get(r);
}
function Un(e, t) {
	return ar(Wn(e, t.definedNames, t.depth, {
		depth: 0,
		remainingNameSourceUnits: kn
	}), t);
}
function Wn(e, t, n, r) {
	let i = e.trim(), a = In(i.startsWith("=") ? i.slice(1) : i), o = {
		toks: a,
		pos: 0,
		budget: r,
		names: t,
		nameDepth: n
	}, s = qn(o);
	if (o.pos !== a.length) throw new Y("unsupported");
	return s;
}
function Gn(e) {
	return e.toks[e.pos];
}
function Kn(e) {
	return e.toks[e.pos++];
}
function qn(e) {
	if (e.budget.depth >= On) throw new Y("unsupported");
	e.budget.depth++;
	try {
		return Jn(e);
	} finally {
		e.budget.depth--;
	}
}
function Jn(e) {
	let t = Xn(e), n = Gn(e);
	return n && n.kind === "op" && (n.text === "<" || n.text === ">" || n.text === "<=" || n.text === ">=" || n.text === "=" || n.text === "<>") ? (Kn(e), {
		t: "bin",
		op: n.text,
		l: t,
		r: Xn(e)
	}) : t;
}
function Yn(e, t, n) {
	let r = n(e), i = [];
	for (;;) {
		let r = Gn(e);
		if (!r || r.kind !== "op" || !t.includes(r.text)) break;
		Kn(e), i.push({
			op: r.text,
			r: n(e)
		});
	}
	return i.length ? {
		t: "chain",
		first: r,
		rest: i
	} : r;
}
function Xn(e) {
	return Yn(e, ["&"], Zn);
}
function Zn(e) {
	return Yn(e, ["+", "-"], Qn);
}
function Qn(e) {
	return Yn(e, ["*", "/"], rr);
}
function $n(e) {
	return Number.isFinite(e) ? e : Z("#NUM!");
}
function er(e, t, n) {
	switch (e) {
		case "&": return Pn(t) + Pn(n);
		case "+": return $n(X(t) + X(n));
		case "-": return $n(X(t) - X(n));
		case "*": return $n(X(t) * X(n));
		case "/": {
			let e = X(t), r = X(n);
			return r === 0 ? Z("#DIV/0!") : $n(e / r);
		}
		default: return tr(e, Tn(t), Tn(n));
	}
}
function tr(e, t, n) {
	let r = typeof t == "string" && isNaN(parseFloat(t)) ? null : nr(t), i = typeof n == "string" && isNaN(parseFloat(n)) ? null : nr(n);
	if (r !== null && i !== null) switch (e) {
		case "<": return r < i;
		case ">": return r > i;
		case "<=": return r <= i;
		case ">=": return r >= i;
		case "=": return r === i;
		case "<>": return r !== i;
	}
	let a = String(t ?? ""), o = String(n ?? "");
	switch (e) {
		case "<": return a < o;
		case ">": return a > o;
		case "<=": return a <= o;
		case ">=": return a >= o;
		case "=": return a === o;
		case "<>": return a !== o;
	}
	return !1;
}
function nr(e) {
	let t = Tn(e);
	if (typeof t == "number") return t;
	if (typeof t == "boolean") return +!!t;
	if (t == null) return 0;
	let n = parseFloat(t);
	return isNaN(n) ? 0 : n;
}
function rr(e) {
	if (e.budget.depth >= On) throw new Y("unsupported");
	e.budget.depth++;
	try {
		let t = Gn(e);
		return t && t.kind === "op" && t.text === "-" ? (Kn(e), {
			t: "neg",
			e: rr(e)
		}) : t && t.kind === "op" && t.text === "+" ? (Kn(e), {
			t: "pos",
			e: rr(e)
		}) : ir(e);
	} finally {
		e.budget.depth--;
	}
}
function ir(e) {
	let t = Kn(e);
	if (!t) throw new Y("invalid");
	if (t.kind === "num") return {
		t: "lit",
		v: parseFloat(t.text)
	};
	if (t.kind === "str") return {
		t: "lit",
		v: t.text
	};
	if (t.kind === "bool") return {
		t: "lit",
		v: t.text === "TRUE"
	};
	if (t.kind === "error") return {
		t: "lit",
		v: Z(t.text)
	};
	if (t.kind === "lparen") {
		let t = qn(e), n = Kn(e);
		if (!n || n.kind !== "rparen") throw new Y("invalid");
		return t;
	}
	if (t.kind === "ref") {
		if (Gn(e)?.kind === "colon") {
			Kn(e);
			let n = Kn(e);
			if (n?.kind !== "ref" || !n.ref) throw new Y("invalid");
			return {
				t: "range",
				a: t.ref,
				b: n.ref
			};
		}
		return {
			t: "ref",
			ref: t.ref
		};
	}
	if (t.kind === "name") {
		if (Gn(e)?.kind === "lparen") {
			Kn(e);
			let n = [];
			if (Gn(e)?.kind !== "rparen") for (n.push(qn(e)); Gn(e)?.kind === "comma";) Kn(e), n.push(qn(e));
			let r = Kn(e);
			if (!r || r.kind !== "rparen") throw new Y("invalid");
			let i = t.text.toUpperCase();
			return cr(i, n.length), {
				t: "call",
				name: i,
				args: n
			};
		}
		let n = Hn(e.names, t.text);
		if (!n || e.nameDepth >= Dn || n.formula.length > e.budget.remainingNameSourceUnits) throw new Y("unsupported");
		return e.budget.remainingNameSourceUnits -= n.formula.length, {
			t: "name",
			body: Wn(lr(n.formula), e.names, e.nameDepth + 1, e.budget)
		};
	}
	throw new Y("invalid");
}
function ar(e, t) {
	try {
		return or(e, t);
	} catch (e) {
		if (e instanceof Y && e.kind === "error") return Z(e.code ?? "#VALUE!");
		throw e;
	}
}
function or(e, t) {
	switch (e.t) {
		case "lit": return e.v;
		case "ref": return dr(e.ref, t);
		case "range": return hr(e.a, e.b, t);
		case "neg": return -X(ar(e.e, t));
		case "pos": return X(ar(e.e, t));
		case "bin": return er(e.op, ar(e.l, t), ar(e.r, t));
		case "chain": {
			let n = ar(e.first, t);
			for (let { op: r, r: i } of e.rest) n = er(r, n, ar(i, t));
			return n;
		}
		case "call": return yr(e.name, e.args, t);
		case "name": return ar(e.body, {
			...t,
			anchorRow: 1,
			anchorCol: 1
		});
	}
}
var sr = {
	AND: [1, 255],
	OR: [1, 255],
	NOT: [1, 1],
	IF: [2, 3],
	IFERROR: [2, 2],
	IFS: [2, 254],
	TRUE: [0, 0],
	FALSE: [0, 0],
	ISBLANK: [1, 1],
	ISNUMBER: [1, 1],
	ISTEXT: [1, 1],
	ISNONTEXT: [1, 1],
	ISERROR: [1, 1],
	ISERR: [1, 1],
	ISNA: [1, 1],
	ISLOGICAL: [1, 1],
	ROUNDDOWN: [2, 2],
	ROUNDUP: [2, 2],
	ROUND: [2, 2],
	INT: [1, 1],
	TRUNC: [1, 2],
	CEILING: [2, 2],
	FLOOR: [2, 2],
	MOD: [2, 2],
	POWER: [2, 2],
	SQRT: [1, 1],
	ABS: [1, 1],
	SIGN: [1, 1],
	EXP: [1, 1],
	LN: [1, 1],
	LOG10: [1, 1],
	MIN: [1, 255],
	MAX: [1, 255],
	SUM: [1, 255],
	AVERAGE: [1, 255],
	COUNT: [1, 255],
	COUNTA: [1, 255],
	COUNTBLANK: [1, 1],
	COUNTIF: [2, 2],
	SUMIF: [2, 3],
	AVERAGEIF: [2, 3],
	LEN: [1, 1],
	LEFT: [1, 2],
	RIGHT: [1, 2],
	MID: [3, 3],
	UPPER: [1, 1],
	LOWER: [1, 1],
	TRIM: [1, 1],
	EXACT: [2, 2],
	FIND: [2, 3],
	SEARCH: [2, 3],
	CONCATENATE: [1, 255],
	CONCAT: [1, 253],
	T: [1, 1],
	N: [1, 1],
	VALUE: [1, 1],
	ROW: [0, 1],
	COLUMN: [0, 1],
	TODAY: [0, 0],
	NOW: [0, 0],
	DATE: [3, 3],
	YEAR: [1, 1],
	MONTH: [1, 1],
	DAY: [1, 1],
	WEEKDAY: [1, 2]
};
function cr(t, n) {
	let r = e(sr, t);
	if (!r) throw new Y("unsupported");
	if (n < r[0] || n > r[1] || t === "IFS" && n % 2 != 0) throw new Y("invalid");
}
function lr(e) {
	let t = e.match(/^(?:'[^']*'|[A-Za-z_][A-Za-z0-9_.]*)!(.*)$/);
	return t ? t[1] : e;
}
function ur(e, t) {
	return {
		col: e.colAbs ? e.col : e.col + (t.col - t.anchorCol),
		row: e.rowAbs ? e.row : e.row + (t.row - t.anchorRow)
	};
}
function dr(e, t) {
	let { row: n, col: r } = ur(e, t);
	return vr(t.cellIndex.get(`${n}:${r}`));
}
var fr = 4096;
function pr(e, t, n) {
	let r = ur(e, n), i = ur(t, n);
	return {
		r1: Math.min(r.row, i.row),
		c1: Math.min(r.col, i.col),
		r2: Math.max(r.row, i.row),
		c2: Math.max(r.col, i.col)
	};
}
function mr({ r1: e, c1: t, r2: n, c2: r }, i) {
	if ((n - e + 1) * (r - t + 1) > fr) throw new Y("unsupported");
	let a = [];
	for (let o = e; o <= n; o++) for (let e = t; e <= r; e++) a.push(vr(i.cellIndex.get(`${o}:${e}`)));
	return a;
}
function hr(e, t, n) {
	return mr(pr(e, t, n), n);
}
function gr(e, t) {
	switch (e.t) {
		case "ref": {
			let { row: n, col: r } = ur(e.ref, t);
			return {
				r1: n,
				c1: r,
				r2: n,
				c2: r
			};
		}
		case "range": return pr(e.a, e.b, t);
		case "name": return gr(e.body, {
			...t,
			anchorRow: 1,
			anchorCol: 1
		});
		default: return null;
	}
}
function _r(e, t, n) {
	let r = gr(e, n), i = gr(t, n);
	if (!r || !i) return null;
	let a = i.r1 + (r.r2 - r.r1), o = i.c1 + (r.c2 - r.c1);
	if (i.r1 < 1 || i.c1 < 1 || a > bn || o > xn) throw new Y("unsupported");
	return mr({
		r1: i.r1,
		c1: i.c1,
		r2: a,
		c2: o
	}, n);
}
function vr(e) {
	if (!e) return null;
	switch (e.value.type) {
		case "number": return e.value.number;
		case "bool": return e.value.bool;
		case "text": return e.value.text;
		case "error": return Z(e.value.error);
		default: return null;
	}
}
function yr(e, t, n) {
	let r = (e) => ar(t[e], n);
	switch (e) {
		case "IF": return Mn(r(0)) ? r(1) : t.length > 2 ? r(2) : !1;
		case "IFERROR": {
			let e = wn(r(0));
			return (e instanceof Sn ? r(1) : e) ?? "";
		}
		case "ISERROR": return wn(r(0)) instanceof Sn;
		case "ISERR": {
			let e = wn(r(0));
			return e instanceof Sn && e.code !== "#N/A";
		}
		case "ISNA": {
			let e = wn(r(0));
			return e instanceof Sn && e.code === "#N/A";
		}
		case "ROW":
		case "COLUMN": {
			let r = t[0], i = r === void 0 ? n : r.t === "ref" ? ur(r.ref, n) : null;
			if (!i) throw new Y("unsupported");
			return e === "ROW" ? i.row : i.col;
		}
		case "SUMIF":
		case "AVERAGEIF": {
			let i = Cn(r(0)), a = r(1), o = t.length > 2 ? _r(t[0], t[2], n) ?? Cn(r(2)) : null;
			return e === "SUMIF" ? Sr(i, a, o) : Cr(i, a, o);
		}
	}
	let i = t.map((e) => ar(e, n));
	switch (e) {
		case "IFS":
			En(i);
			for (let e = 0; e < i.length; e += 2) if (Mn(i[e])) return i[e + 1];
			return Z("#N/A");
		case "AND": return En(i).every((e) => Mn(e));
		case "OR": return En(i).some((e) => Mn(e));
		case "NOT": return !Mn(i[0]);
		case "TRUE": return !0;
		case "FALSE": return !1;
		case "ISBLANK": return wn(i[0]) === null;
		case "ISNUMBER": return typeof wn(i[0]) == "number";
		case "ISTEXT": return typeof wn(i[0]) == "string";
		case "ISNONTEXT": return typeof wn(i[0]) != "string";
		case "ISLOGICAL": return typeof wn(i[0]) == "boolean";
		case "ROUNDDOWN": {
			let e = X(i[0]), t = 10 ** X(i[1]);
			return (e >= 0 ? Math.floor(e * t) : Math.ceil(e * t)) / t;
		}
		case "ROUNDUP": {
			let e = X(i[0]), t = 10 ** X(i[1]);
			return (e >= 0 ? Math.ceil(e * t) : Math.floor(e * t)) / t;
		}
		case "ROUND": return br(X(i[0]), X(i[1]));
		case "INT": return Math.floor(X(i[0]));
		case "TRUNC": {
			let e = X(i[0]), t = 10 ** X(i[1] ?? 0);
			return (e >= 0 ? Math.floor(e * t) : Math.ceil(e * t)) / t;
		}
		case "CEILING": {
			let e = X(i[0]), t = X(i[1]);
			return t === 0 ? 0 : Math.ceil(e / t) * t;
		}
		case "FLOOR": {
			let e = X(i[0]), t = X(i[1]);
			return e > 0 && t < 0 ? Z("#NUM!") : t === 0 ? 0 : Math.floor(e / t) * t;
		}
		case "MOD": {
			let e = X(i[0]), t = X(i[1]);
			return t === 0 ? Z("#DIV/0!") : e - Math.floor(e / t) * t;
		}
		case "POWER": {
			let e = X(i[0]), t = X(i[1]);
			return e === 0 && t <= 0 ? Z("#DIV/0!") : $n(e ** +t);
		}
		case "SQRT": {
			let e = X(i[0]);
			return e < 0 ? Z("#NUM!") : Math.sqrt(e);
		}
		case "ABS": return Math.abs(X(i[0]));
		case "SIGN": {
			let e = X(i[0]);
			return e > 0 ? 1 : e < 0 ? -1 : 0;
		}
		case "EXP": return $n(Math.exp(X(i[0])));
		case "LN": {
			let e = X(i[0]);
			return e <= 0 ? Z("#NUM!") : Math.log(e);
		}
		case "LOG10": {
			let e = X(i[0]);
			return e <= 0 ? Z("#NUM!") : Math.log10(e);
		}
		case "MIN": {
			let e = En(i).filter((e) => typeof e == "number");
			return e.length ? Math.min(...e) : 0;
		}
		case "MAX": {
			let e = En(i).filter((e) => typeof e == "number");
			return e.length ? Math.max(...e) : 0;
		}
		case "SUM": return En(i).reduce((e, t) => e + (typeof t == "number" ? t : 0), 0);
		case "AVERAGE": {
			let e = En(i).filter((e) => typeof e == "number");
			return e.length ? e.reduce((e, t) => e + t, 0) / e.length : Z("#DIV/0!");
		}
		case "COUNT": return i.flatMap(Cn).filter((e) => typeof e == "number").length;
		case "COUNTA": return i.flatMap(Cn).filter((e) => e != null).length;
		case "COUNTBLANK": return i.flatMap(Cn).filter((e) => e == null || e === "").length;
		case "COUNTIF": return xr(Cn(i[0]), i[1]);
		case "LEN": return Pn(i[0]).length;
		case "LEFT": {
			let e = Pn(i[0]), t = X(i[1] ?? 1);
			return t < 0 ? Z("#VALUE!") : e.slice(0, t);
		}
		case "RIGHT": {
			let e = Pn(i[0]), t = X(i[1] ?? 1);
			return t < 0 ? Z("#VALUE!") : t >= e.length ? e : e.slice(e.length - t);
		}
		case "MID": {
			let e = Pn(i[0]), t = X(i[1]), n = X(i[2]);
			return t < 1 || n < 0 ? Z("#VALUE!") : e.slice(t - 1, t - 1 + n);
		}
		case "UPPER": return Pn(i[0]).toUpperCase();
		case "LOWER": return Pn(i[0]).toLowerCase();
		case "TRIM": {
			let e = Pn(i[0]).replace(/ +/g, " ");
			return e.slice(+!!e.startsWith(" "), e.endsWith(" ") ? e.length - 1 : e.length);
		}
		case "EXACT": return Pn(i[0]) === Pn(i[1]);
		case "FIND": {
			let e = Pn(i[0]), t = Pn(i[1]), n = X(i[2] ?? 1);
			if (n < 1) return Z("#VALUE!");
			let r = t.indexOf(e, n - 1);
			return r < 0 ? Z("#VALUE!") : r + 1;
		}
		case "SEARCH": {
			let e = Pn(i[0]).toLowerCase(), t = Pn(i[1]), n = t.toLowerCase(), r = X(i[2] ?? 1);
			if (r < 1 || t.length > 0 && Number.isInteger(r) && r > t.length) return Z("#VALUE!");
			let a = n.indexOf(e, r - 1);
			return a < 0 ? Z("#VALUE!") : a + 1;
		}
		case "CONCATENATE":
		case "CONCAT": return i.flatMap(Cn).map((e) => Pn(e)).join("");
		case "T": {
			let e = Tn(i[0]);
			return typeof e == "string" ? e : "";
		}
		case "N": {
			let e = Tn(i[0]);
			return typeof e == "number" ? e : typeof e == "boolean" ? +!!e : 0;
		}
		case "VALUE": return X(i[0]);
		case "TODAY": return Tr();
		case "NOW": return Er();
		case "DATE": return Dr(X(i[0]), X(i[1]), X(i[2]));
		case "YEAR": return kr(X(i[0])).y;
		case "MONTH": return kr(X(i[0])).m;
		case "DAY": return kr(X(i[0])).d;
		case "WEEKDAY": {
			let e = Or(X(i[0])).getUTCDay(), t = X(i[1] ?? 1);
			return t === 2 ? e === 0 ? 7 : e : t === 3 ? e === 0 ? 6 : e - 1 : e + 1;
		}
		default: throw new Y("unsupported");
	}
}
function br(e, t) {
	if (!Number.isInteger(t)) throw new Y("unsupported");
	if (e === 0) return 0;
	let n = Math.max(-400, Math.min(400, t)), [r, i = "0"] = String(Math.abs(e)).split("e"), a = r.indexOf("."), o = r.replace(".", ""), s = (a === -1 ? r.length : a) + Number(i) + n;
	if (s >= o.length) return e;
	if (s < 0) return 0;
	let c = (s === 0 ? 0n : BigInt(o.slice(0, s))) + (o[s] >= "5" ? 1n : 0n), l = Number(`${c}e${-n}`);
	if (!Number.isFinite(l)) throw new Y("error", "#NUM!");
	return l === 0 ? 0 : Math.sign(e) * l;
}
function xr(e, t) {
	let n = wr(t), r = 0;
	for (let t of e) n(t) && r++;
	return r;
}
function Sr(e, t, n) {
	let r = wr(t), i = n ?? e, a = 0;
	for (let t = 0; t < e.length; t++) if (r(e[t])) {
		let e = i[t];
		typeof e == "number" && (a += e);
	}
	return a;
}
function Cr(e, t, n) {
	let r = wr(t), i = n ?? e, a = 0, o = 0;
	for (let t = 0; t < e.length; t++) if (r(e[t])) {
		let e = i[t];
		if (e === null) continue;
		typeof e == "number" && (a += e), o++;
	}
	return o === 0 ? Z("#DIV/0!") : a / o;
}
function wr(e) {
	let t = wn(e);
	if (t instanceof Sn) throw new Y("unsupported");
	if (typeof t != "string") {
		let e = typeof t == "number" ? t : null;
		return (n) => e !== null && typeof n == "number" ? n === e : n === t;
	}
	let n = t.match(/^(<=|>=|<>|<|>|=)(.*)$/), r = n ? n[1] : "=", i = n ? n[2] : t, a = i.trim() === "" ? NaN : parseFloat(i), o = !isNaN(a) && /^-?\d+(\.\d+)?$/.test(i.trim()), s = Vn(i);
	return (e) => {
		if (o && typeof e == "number") switch (r) {
			case "<": return e < a;
			case ">": return e > a;
			case "<=": return e <= a;
			case ">=": return e >= a;
			case "<>": return e !== a;
			default: return e === a;
		}
		if (typeof e == "string" && (r === "=" || r === "<>")) {
			let t = Vn(e) === s;
			return r === "=" ? t : !t;
		}
		let t = e == null ? "" : typeof e == "boolean" ? e ? "TRUE" : "FALSE" : e instanceof Sn ? e.code : String(e);
		switch (r) {
			case "<>": return t !== i;
			case "<": return t < i;
			case ">": return t > i;
			case "<=": return t <= i;
			case ">=": return t >= i;
			default: return t === i;
		}
	};
}
function Tr() {
	let e = /* @__PURE__ */ new Date();
	return Se(new Date(Date.UTC(e.getFullYear(), e.getMonth(), e.getDate())), !1);
}
function Er() {
	return Se(new Date(Date.now()), !1);
}
function Dr(e, t, n) {
	return Math.floor(Se(new Date(Date.UTC(e, t - 1, n)), !1));
}
function Or(e) {
	return Ce(Math.floor(e), !1);
}
function kr(e) {
	let t = Or(e);
	return {
		y: t.getUTCFullYear(),
		m: t.getUTCMonth() + 1,
		d: t.getUTCDate()
	};
}
function Ar(e, t, n) {
	for (let r of e) if (t >= r.top && t <= r.bottom && n >= r.left && n <= r.right) return !0;
	return !1;
}
function jr(e) {
	return e && e.value.type === "number" ? e.value.number : null;
}
function Mr(e) {
	return e && e.value.type === "text" ? e.value.text : null;
}
function Nr(e, t) {
	let n = [];
	for (let r of e.rows) for (let e of r.cells) e.value.type === "number" && Ar(t, e.row, e.col) && n.push(e.value.number);
	return n;
}
function Pr(e) {
	let t = e.value;
	if (t == null || t.trim() === "") return e.kind === "formula" ? "invalid" : void 0;
	let n = vn(t);
	return typeof n == "number" ? n : "unsupported";
}
function Fr(e, t) {
	let n = t.length ? Infinity : 0, r = t.length ? -Infinity : 0;
	for (let e of t) e < n && (n = e), e > r && (r = e);
	if (e.kind === "min") return n;
	if (e.kind === "max") return r;
	if (![
		"num",
		"formula",
		"percent",
		"percentile"
	].includes(e.kind)) return "unsupported";
	let i = Pr(e);
	if (typeof i == "string") return i;
	switch (e.kind) {
		case "percent": {
			let e = i ?? 50;
			return n + (r - n) * (e / 100);
		}
		case "percentile": {
			if (!t.length) return 0;
			let e = [...t].sort((e, t) => e - t), n = (i ?? 50) / 100;
			return e[Math.max(0, Math.min(e.length - 1, Math.round(n * (e.length - 1))))];
		}
		default: return i ?? 0;
	}
}
function Ir(e, t) {
	let n = !0;
	for (let r of t) r === "unsupported" ? (e.thresholdUnsupported = !0, n = !1) : r === "invalid" && (e.thresholdInvalid = !0, n = !1);
	return n ? t : void 0;
}
function Lr(e, t = Rr(e)) {
	let n = [], r = /* @__PURE__ */ new Map();
	for (let t of e.definedNames ?? []) r.set(t.name, t);
	let i = e.conditionalFormats ?? [];
	for (let [t, r] of i.entries()) {
		let i = r.rules.some((e) => e.type !== "expression" && e.type !== "cellIs" && e.type !== "other" && !(e.type === "dataBar" && e.extThresholdFormula)) ? Nr(e, r.sqref) : [];
		for (let e of r.rules) {
			let a = {
				rule: e,
				sqref: r.sqref
			};
			if (r.firstMatch && e.type !== "colorScale" && e.type !== "dataBar" && e.type !== "iconSet" && (a.firstMatchBlock = t), e.type === "colorScale") a.scaleStops = Ir(a, e.stops.map((e) => Fr(e, i)));
			else if (e.type === "dataBar") if (e.extThresholdFormula) a.thresholdUnsupported = !0;
			else {
				let t = Ir(a, [Fr(e.min, i), Fr(e.max, i)]);
				t && (a.barMin = t[0], a.barMax = t[1]);
			}
			else if (e.type === "top10") {
				let t = [...i].sort((e, t) => e - t), n = t.length;
				if (n > 0) {
					let r = Math.min(e.rank, n);
					if (e.percent) {
						let i = e.top ? 1 - r / 100 : r / 100;
						a.top10Threshold = t[Math.max(0, Math.min(n - 1, Math.round(i * (n - 1))))];
					} else a.top10Threshold = e.top ? t[Math.max(0, n - r)] : t[Math.min(n - 1, r - 1)];
					a.top10IsTop = e.top;
				}
			} else if (e.type === "aboveAverage") {
				if (i.length > 0) {
					let t = i.reduce((e, t) => e + t, 0) / i.length;
					if (a.avgValue = t, a.avgIsAbove = e.aboveAverage, e.stdDev && e.stdDev > 0) {
						let e = i.reduce((e, n) => e + (n - t) * (n - t), 0) / i.length;
						a.avgStdDev = Math.sqrt(e);
					}
				}
			} else e.type === "iconSet" ? a.iconThresholds = Ir(a, e.cfvos.map((e) => Fr(e, i))) : e.type === "cellIs" && (a.cellIsOperands = e.formulas.map(Vr));
			n.push(a);
		}
	}
	return n.sort((e, t) => (e.rule.priority ?? 0) - (t.rule.priority ?? 0)), {
		compiled: n,
		worksheet: e,
		cellIndex: t,
		definedNames: r
	};
}
function Rr(e) {
	return zt(e.rows, {
		resource: "worksheet-cell-index",
		operation: "index-worksheet-cells",
		limit: Qe(e).maxCoordinateIndexEntries
	});
}
var zr = new Set([
	"lessThan",
	"lessThanOrEqual",
	"equal",
	"notEqual",
	"greaterThanOrEqual",
	"greaterThan",
	"between",
	"notBetween",
	"containsText",
	"notContains",
	"beginsWith",
	"endsWith"
]);
function Br(e, t, n) {
	switch (t) {
		case "greaterThan": return e > (n[0] ?? 0);
		case "greaterThanOrEqual": return e >= (n[0] ?? 0);
		case "lessThan": return e < (n[0] ?? 0);
		case "lessThanOrEqual": return e <= (n[0] ?? 0);
		case "equal": return e === (n[0] ?? 0);
		case "notEqual": return e !== (n[0] ?? 0);
		case "between": return e >= (n[0] ?? 0) && e <= (n[1] ?? 0);
		case "notBetween": return e < (n[0] ?? 0) || e > (n[1] ?? 0);
		default: return !1;
	}
}
function Vr(e) {
	let t = vn(e);
	return t === void 0 ? { formula: e } : { literal: t };
}
function Hr(e, t, n) {
	let r = n[0] ?? "", i = n[1] ?? "", a = (e) => e.toLowerCase();
	switch (t) {
		case "equal": return a(e) === a(r);
		case "notEqual": return a(e) !== a(r);
		case "containsText": return a(e).includes(a(r));
		case "notContains": return !a(e).includes(a(r));
		case "beginsWith": return a(e).startsWith(a(r));
		case "endsWith": return a(e).endsWith(a(r));
		case "between": return a(e) >= a(r) && a(e) <= a(i);
		case "notBetween": return a(e) < a(r) || a(e) > a(i);
		default: return !1;
	}
}
function Ur(e, t, n) {
	let r = e.replace("#", ""), i = t.replace("#", ""), a = parseInt(r.slice(0, 2), 16), o = parseInt(r.slice(2, 4), 16), s = parseInt(r.slice(4, 6), 16), c = parseInt(i.slice(0, 2), 16), l = parseInt(i.slice(2, 4), 16), u = parseInt(i.slice(4, 6), 16), d = Math.round(a + (c - a) * n), f = Math.round(o + (l - o) * n), p = Math.round(s + (u - s) * n);
	return `#${d.toString(16).padStart(2, "0").toUpperCase()}${f.toString(16).padStart(2, "0").toUpperCase()}${p.toString(16).padStart(2, "0").toUpperCase()}`;
}
function Wr(e, t, n) {
	if (!t.length) return "#FFFFFF";
	if (e <= n[0]) return t[0].color;
	if (e >= n[n.length - 1]) return t[t.length - 1].color;
	for (let r = 1; r < n.length; r++) if (e <= n[r]) {
		let i = n[r - 1], a = n[r], o = a === i ? 0 : (e - i) / (a - i);
		return Ur(t[r - 1].color, t[r].color, o);
	}
	return t[t.length - 1].color;
}
function Gr(e, t) {
	if (t && (t.fill && !e.fill && (e.fill = t.fill), t.font?.color && e.fontColor == null && (e.fontColor = t.font.color), e.fontBold ??= Mt(t, "bold"), e.fontItalic ??= Mt(t, "italic"), e.fontUnderline ??= Mt(t, "underline"), e.fontStrike ??= Mt(t, "strike"), t.numFmt && e.numFmt == null && (e.numFmt = {
		numFmtId: t.numFmt.numFmtId,
		formatCode: t.numFmt.formatCode || null,
		...t.numFmt.sectionDivisors?.length ? { sectionDivisors: t.numFmt.sectionDivisors } : {}
	}), t.border)) {
		let n = e.border ?? {};
		e.border = {
			left: n.left ?? t.border.left,
			right: n.right ?? t.border.right,
			top: n.top ?? t.border.top,
			bottom: n.bottom ?? t.border.bottom,
			diagonalUp: n.diagonalUp ?? t.border.diagonalUp,
			diagonalDown: n.diagonalDown ?? t.border.diagonalDown
		};
	}
}
function Kr(e, t, n, r, i) {
	if (e == null) return "active";
	let a = t.sqref[0];
	if (!a) return "inactive";
	let o = yn(e, {
		row: n,
		col: r,
		anchorRow: a.top,
		anchorCol: a.left,
		cellIndex: i.cellIndex
	});
	return o.kind === "unsupported" ? "unsupported" : o.kind === "error" ? "inactive" : typeof o.value == "number" && o.value !== 0 ? "active" : "inactive";
}
function qr(e) {
	return e.thresholdUnsupported === !0 || e.thresholdInvalid === !0;
}
function Jr(e, t, n, r, i) {
	let a = Kr(t, e, n, r, i);
	return a === "unsupported" || a === "inactive" ? !1 : !qr(e);
}
function Yr(e, t, n, r, i) {
	let a = {};
	if (!r.compiled.length) return a;
	let o;
	for (let s of r.compiled) {
		if (!Ar(s.sqref, t, n) || s.firstMatchBlock !== void 0 && o?.has(s.firstMatchBlock)) continue;
		let c = s.rule, l = jr(e), u = !1;
		if (c.type === "expression") {
			let e = s.sqref[0];
			if (!e) continue;
			u = An(jn(c.formula, {
				row: t,
				col: n,
				anchorRow: e.top,
				anchorCol: e.left,
				cellIndex: r.cellIndex,
				definedNames: r.definedNames,
				depth: 0
			})), u && Gr(a, c.dxfId == null ? null : i[c.dxfId]);
		} else if (c.type === "cellIs") {
			let o = s.sqref[0];
			if (!o) continue;
			let d = s.cellIsOperands ?? [], f = c.operator === "between" || c.operator === "notBetween" ? 2 : 1;
			if (!(!zr.has(c.operator) || d.length < f)) {
				let i = [], a = !0;
				for (let e of d) {
					if ("literal" in e) {
						i.push(e.literal);
						continue;
					}
					let s = yn(e.formula, {
						row: t,
						col: n,
						anchorRow: o.top,
						anchorCol: o.left,
						cellIndex: r.cellIndex
					});
					if (s.kind === "value") {
						i.push(s.value);
						continue;
					}
					a = !1;
					break;
				}
				let s = Mr(e);
				a && (l != null && i.every((e) => typeof e == "number") ? u = Br(l, c.operator, i) : s != null && i.every((e) => typeof e == "string") && (u = Hr(s, c.operator, i)));
			}
			u && Gr(a, c.dxfId == null ? null : i[c.dxfId]);
		} else if (c.type === "top10") {
			if (l == null || s.top10Threshold == null) continue;
			u = s.top10IsTop ? l >= s.top10Threshold : l <= s.top10Threshold, u && Gr(a, c.dxfId == null ? null : i[c.dxfId]);
		} else if (c.type === "aboveAverage") {
			if (l == null || s.avgValue == null) continue;
			let e = s.avgStdDev == null ? 0 : s.avgStdDev * (c.stdDev ?? 1), t = s.avgIsAbove ? s.avgValue + e : s.avgValue - e, n = c.equalAverage === !0;
			u = s.avgIsAbove ? n ? l >= t : l > t : n ? l <= t : l < t, u && Gr(a, c.dxfId == null ? null : i[c.dxfId]);
		} else if (c.type === "iconSet") {
			if (l == null || !qr(s) && !s.iconThresholds?.length || !Jr(s, c.activeFormula, t, n, r)) continue;
			let e = s.iconThresholds;
			if (!e?.length) continue;
			u = !0;
			let i = e.length, o = 0;
			for (let t = 1; t < i; t++) l >= e[t] && (o = t);
			if (c.reverse && (o = i - 1 - o), c.customIcons && c.customIcons[o]) {
				let e = c.customIcons[o];
				e.iconSet !== "NoIcons" && (a.iconSet = {
					name: e.iconSet,
					index: e.iconId
				});
			} else a.iconSet = {
				name: c.iconSet,
				index: o
			};
		} else if (c.type === "colorScale") {
			if (l == null || !qr(s) && !s.scaleStops || !Jr(s, c.activeFormula, t, n, r)) continue;
			let e = s.scaleStops;
			if (!e) continue;
			if (u = !0, !a.fill) {
				let t = Wr(l, c.stops, e);
				a.fill = {
					patternType: "solid",
					fgColor: t,
					bgColor: t
				};
			}
		} else if (c.type === "dataBar") {
			if (l == null || !qr(s) && (s.barMin == null || s.barMax == null) || !Jr(s, c.activeFormula, t, n, r)) continue;
			let e = s.barMin, i = s.barMax;
			if (e == null || i == null) continue;
			if (u = !0, !a.dataBar) {
				let t = i - e, n = t === 0 ? 0 : Math.max(0, Math.min(1, (l - e) / t));
				a.dataBar = {
					color: c.color,
					ratio: n,
					gradient: c.gradient
				};
			}
		}
		if (u && s.firstMatchBlock !== void 0 && (o ??= /* @__PURE__ */ new Set()).add(s.firstMatchBlock), u && c.stopIfTrue) break;
	}
	return a;
}
function Xr(e, t) {
	return e === 2 ? !0 : e === 1 ? !1 : lt(void 0, t) === "rtl";
}
function Zr(e, t) {
	let n = e === 2 || a(t);
	return {
		needBidi: n,
		baseRtl: n && Xr(e, t)
	};
}
var Qr = (e, t) => R(e, t);
function $r(e) {
	let t = /^\$?([A-Z]+)\$?(\d+)$/.exec(e.trim());
	if (!t) return null;
	let n = t[1], r = 0;
	for (let e = 0; e < n.length; e++) r = r * 26 + (n.charCodeAt(e) - 64);
	let i = parseInt(t[2], 10);
	return i < 1 || i > 1048576 || r > 16384 ? null : {
		row: i,
		col: r
	};
}
function ei(e, t) {
	let n = "", r = t;
	for (; r > 0;) {
		let e = (r - 1) % 26;
		n = String.fromCharCode(65 + e) + n, r = Math.floor((r - 1) / 26);
	}
	return `${n}${e}`;
}
function ti(e, t, n, r, i, a = !1, o = (t, n, r) => e.fillText(t, n, r)) {
	let s = t.codePointAt(0) ?? 0, c = W(s);
	if (a && ie(s)) {
		e.save(), e.translate(n, r + i / 2), e.textAlign = "center", e.textBaseline = "middle", le(e, () => o(t, 0, 0)), e.restore();
		return;
	}
	if (c === "Tr") {
		let a = re(s);
		if (a !== null) {
			o(String.fromCodePoint(a), n, r);
			return;
		}
		if (H(s)) {
			o(t, n, r);
			return;
		}
		e.save(), e.translate(n, r + i / 2), e.rotate(Math.PI / 2), e.textAlign = "center", e.textBaseline = "middle", o(t, 0, 0), e.restore();
		return;
	}
	let l = c === "Tu" ? se(s) : null;
	o(l === null ? t : String.fromCodePoint(l), n, r);
}
function ni(e) {
	return e.editAs === "oneCell" && (e.nativeExtCx ?? 0) > 0 && (e.nativeExtCy ?? 0) > 0;
}
function ri(e, t, n, r, i) {
	let a = t.offsetOf(e.fromCol + 1) + e.fromColOff * r / K, o = n.offsetOf(e.fromRow + 1) + e.fromRowOff * r / K, s = ii(e, i);
	if (s) return {
		x: a,
		y: o,
		width: s.cx * r / K,
		height: s.cy * r / K
	};
	let c = t.offsetOf(e.toCol + 1) + e.toColOff * r / K, l = n.offsetOf(e.toRow + 1) + e.toRowOff * r / K;
	return {
		x: a,
		y: o,
		width: c - a,
		height: l - o
	};
}
function ii(e, t) {
	return e.anchorTag === void 0 ? ni(e) ? {
		cx: e.nativeExtCx,
		cy: e.nativeExtCy
	} : null : e.anchorTag === "oneCellAnchor" ? {
		cx: e.anchorExtCx ?? 0,
		cy: e.anchorExtCy ?? 0
	} : e.anchorTag === "twoCellAnchor" && e.editAs === "oneCell" && t !== void 0 ? {
		cx: t.cx,
		cy: t.cy
	} : null;
}
var ai = [
	"fromCol",
	"fromColOff",
	"fromRow",
	"fromRowOff",
	"toCol",
	"toColOff",
	"toRow",
	"toRowOff"
], oi = Object.freeze([]), si = Object.freeze({
	cx: 0,
	cy: 0
}), ci = /* @__PURE__ */ new WeakMap(), li = /* @__PURE__ */ new WeakSet();
function ui(e) {
	return e.anchorTag === "twoCellAnchor" && e.editAs === "oneCell";
}
function di(e) {
	let t, n = [e.images, e.shapeGroups];
	for (let e of n) for (let n of e ?? []) {
		if (!ui(n)) continue;
		let e = n, r = 0;
		for (let t of [e.fromRow, e.toRow]) typeof t == "number" && Number.isFinite(t) && t >= 0 && (r = Math.max(r, Math.floor(t) + 1));
		t = Math.max(t ?? 0, r);
	}
	return t;
}
function fi(e) {
	let t = e * K;
	return Number.isFinite(t) && t > 0 ? t : 0;
}
function pi(e) {
	throw Error(`XLSX initial anchor size reference does not match this worksheet projection: ${e}`);
}
function mi(e, t, n = 1) {
	if (!Number.isFinite(n) || n <= 0) throw RangeError(`XLSX initial anchor size capture requires a finite positive scale: ${n}`);
	let r = e.images ?? oi, i = e.shapeGroups ?? oi, a, o;
	for (let e = 0; e < 2; e++) {
		let s = e === 0 ? "image" : "shape", c = e === 0 ? r : i;
		for (let e = 0; e < c.length; e++) {
			let r = c[e];
			if (!ui(r)) continue;
			o ??= t.axesAtScale(n);
			let i = ri(r, o.col, o.row, n);
			(a ??= []).push(Object.freeze({
				family: s,
				index: e,
				fromCol: r.fromCol,
				fromColOff: r.fromColOff,
				fromRow: r.fromRow,
				fromRowOff: r.fromRowOff,
				toCol: r.toCol,
				toColOff: r.toColOff,
				toRow: r.toRow,
				toRowOff: r.toRowOff,
				cx: fi(i.width / n),
				cy: fi(i.height / n)
			}));
		}
	}
	if (a) return Object.freeze({
		version: 1,
		imageCount: r.length,
		shapeGroupCount: i.length,
		entries: Object.freeze(a)
	});
}
function hi(e, t) {
	li.has(t) && pi("the reference was released");
	let n = ci.get(e);
	if (n) {
		if (n.reference === t && e.images === n.images && e.shapeGroups === n.shapeGroups) return;
		pi("the projection is already bound to another reference");
	}
	(t.version !== 1 || !Array.isArray(t.entries)) && pi("unsupported reference shape");
	let r = e.images ?? oi, i = e.shapeGroups ?? oi;
	(r.length !== t.imageCount || i.length !== t.shapeGroupCount) && pi("anchor counts differ");
	let a = /* @__PURE__ */ new WeakMap();
	for (let e of t.entries) {
		let t = e.family === "image" ? r : e.family === "shape" ? i : oi, n = Number.isInteger(e.index) ? t[e.index] : void 0;
		(!n || !ui(n) || a.has(n)) && pi(`${e.family}[${e.index}] is not an eligible anchor`);
		for (let t of ai) Object.is(n[t], e[t]) || pi(`${e.family}[${e.index}].${t} differs`);
		(!Number.isFinite(e.cx) || !Number.isFinite(e.cy) || e.cx < 0 || e.cy < 0) && pi(`${e.family}[${e.index}] has an invalid EMU size`), a.set(n, e);
	}
	let o = 0;
	for (let e of r) ui(e) && o++;
	for (let e of i) ui(e) && o++;
	o !== t.entries.length && pi("an eligible anchor has no captured initial size");
	for (let e of t.entries) Object.freeze(e);
	Object.freeze(t.entries), Object.freeze(t), ci.set(e, {
		reference: t,
		images: e.images,
		shapeGroups: e.shapeGroups,
		sizes: a
	});
}
function gi(e, t) {
	if (!ui(t)) return;
	let n = ci.get(e);
	if (n) return li.has(n.reference) || e.images !== n.images || e.shapeGroups !== n.shapeGroups ? si : n.sizes.get(t) ?? si;
}
function _i(e, t, n, r, i) {
	return ri(t, n, r, i, gi(e, t));
}
function vi(e) {
	li.add(e);
}
var yi = /* @__PURE__ */ new WeakMap();
function bi(e) {
	yi.delete(e);
}
function xi(e, t, n) {
	let r = yi.get(e);
	r || (r = /* @__PURE__ */ new Map(), yi.set(e, r)), r.set(t, n);
}
function Si(e, t, n) {
	return e !== void 0 && yi.get(e)?.get(t) === n;
}
function Ci(e) {
	if (!Number.isFinite(e)) return [0, 1];
	let t = (e % 360 + 360) % 360;
	if (t === 0) return [0, 1];
	if (t === 90) return [1, 0];
	if (t === 180) return [0, -1];
	if (t === 270) return [-1, 0];
	let n = e * Math.PI / 180;
	return [Math.sin(n), Math.cos(n)];
}
function wi(e, t = 0) {
	let [n, r] = Ci(t);
	if (n === 0 && Math.abs(r) === 1) return e;
	let i = Math.abs(e.width * r) + Math.abs(e.height * n), a = Math.abs(e.width * n) + Math.abs(e.height * r);
	return {
		x: e.x + (e.width - i) / 2,
		y: e.y + (e.height - a) / 2,
		width: i,
		height: a
	};
}
function Ti(e, t, n = 0, r = !1, i = !1) {
	if (n === 0 && !r && !i) return e;
	let a = t.x + t.width / 2, o = t.y + t.height / 2, [s, c] = Ci(-n), l = e.x - a, u = e.y - o, d = a + l * c - u * s, f = o + l * s + u * c;
	return r && (d = 2 * a - d), i && (f = 2 * o - f), {
		x: d,
		y: f
	};
}
function Ei(e, t, n, r, i) {
	let a = pe(e);
	if (!a || !(a.width > 0) || !(a.height > 0)) return null;
	let o = e, s = r / a.width, c = i / a.height;
	return {
		x: t - a.x * s,
		y: n - a.y * c,
		width: o.width * s,
		height: o.height * c
	};
}
function Di(e, t, n, r, i, a) {
	let o = r * Math.PI / 180, s = Math.cos(o), c = Math.sin(o), l = Infinity, u = Infinity, d = -Infinity, f = -Infinity;
	for (let [r, o] of [
		[e.x, e.y],
		[e.x + e.width, e.y],
		[e.x, e.y + e.height],
		[e.x + e.width, e.y + e.height]
	]) {
		let e = (r - t) * (i ? -1 : 1), p = (o - n) * (a ? -1 : 1), m = t + e * s - p * c, h = n + e * c + p * s;
		l = Math.min(l, m), u = Math.min(u, h), d = Math.max(d, m), f = Math.max(f, h);
	}
	return {
		x: l,
		y: u,
		width: d - l,
		height: f - u
	};
}
function Oi(e, t, n) {
	if (!t) return e;
	if ("effects" in t) {
		let { widthPt: r, heightPt: i } = ki(n);
		return JSON.stringify([
			"blip",
			e,
			ue(t),
			r,
			i
		]);
	}
	return `${e}|duo:${t.clr1}:${t.clr2}`;
}
function ki(e) {
	if (!(e && Number.isFinite(e.cx) && Number.isFinite(e.cy) && e.cx > 0 && e.cy > 0)) return {
		widthPt: 0,
		heightPt: 0
	};
	let t = fe(e.cx / 12700, e.cy / 12700, e.srcRect, null);
	return {
		widthPt: t.width,
		heightPt: t.height
	};
}
function Ai(e) {
	let t = e.nativeExtCx > 0 && e.nativeExtCy > 0;
	return {
		cx: t ? e.nativeExtCx : e.anchorExtCx ?? 0,
		cy: t ? e.nativeExtCy : e.anchorExtCy ?? 0,
		srcRect: e.srcRect ?? null,
		rotation: e.rotation ?? 0,
		flipH: e.flipH ?? !1,
		flipV: e.flipV ?? !1
	};
}
function ji(e, t) {
	return {
		cx: e.nativeExtCx * t.w,
		cy: e.nativeExtCy * t.h,
		srcRect: t.geom.type === "image" ? t.geom.srcRect ?? null : null,
		rotation: t.rot,
		flipH: t.flipH,
		flipV: t.flipV
	};
}
function Mi(e, t) {
	return e.blipEffects?.length ? {
		effects: e.blipEffects,
		duotone: e.duotone ?? null,
		hostRotation: t?.rotation ?? 0,
		hostFlipH: t?.flipH ?? !1,
		hostFlipV: t?.flipV ?? !1
	} : e.duotone ?? null;
}
var Ni = O.map((e) => `"${e}"`).join(", "), Pi = T.map((e) => `"${e}"`).join(", "), Fi = `"Calibri", Arial, ${Ni}, sans-serif`, Ii = `Arial, Helvetica, "Liberation Sans", ${Ni}, sans-serif`, Li = `"Times New Roman", "Liberation Serif", ${Pi}, serif`, Ri = /* @__PURE__ */ new WeakMap(), zi = /* @__PURE__ */ new WeakMap(), Bi = /* @__PURE__ */ new WeakMap(), Vi = /* @__PURE__ */ new Map(), Hi = /* @__PURE__ */ new WeakMap(), Ui = /* @__PURE__ */ new WeakMap(), Wi = /* @__PURE__ */ new WeakMap(), Gi = /* @__PURE__ */ new WeakMap();
function Ki(e) {
	if (!e) return "";
	let t = Wi.get(e);
	return t === void 0 && (t = JSON.stringify([
		[...e.substitutions].map(([e, t]) => [
			e,
			t.family,
			t.script ?? ""
		]).sort(),
		[...e.regularAliases].sort(),
		[...e.families].sort()
	]), Wi.set(e, t)), t;
}
function qi(e, t) {
	let n = Ki(t), r = (Gi.get(e) ?? "") !== n;
	return Gi.set(e, n), t ? Ui.set(e, t) : Ui.delete(e), r;
}
function Ji(e, t) {
	return t ? (e?.regularAliases ?? Vi).get(t.trim().toLocaleLowerCase("en-US")) : void 0;
}
var Yi = /* @__PURE__ */ new WeakMap(), Xi = /* @__PURE__ */ new WeakMap();
function Zi(e, t) {
	let n = qe(t), r = Xi.get(t);
	(!r || r.japanese !== n || r.themeJapaneseMajorFont !== t.themeJapaneseMajorFont || r.themeJapaneseMinorFont !== t.themeJapaneseMinorFont) && (r = {
		themeJapaneseMajorFont: t.themeJapaneseMajorFont,
		themeJapaneseMinorFont: t.themeJapaneseMinorFont,
		japanese: n,
		cache: /* @__PURE__ */ new Map()
	}, Ze(t, r), Xi.set(t, r)), Yi.set(e, r);
}
function Qi(t, n, r, i, a) {
	let o = t.defaultFontFamily ? mt({
		family: t.defaultFontFamily,
		weight: t.defaultFontBold ? 700 : 400,
		style: t.defaultFontItalic ? "italic" : "normal"
	}) : null, s = o === null || !n ? void 0 : e(n, o), c = {
		tupleKey: o,
		route: s,
		hasDeclaredFace: t.defaultFontFamily ? va(t.defaultFontFamily, r) : !1,
		canvasMdw: a && t.defaultFontFamily && t.defaultFontSize ? ga(t.defaultFontFamily, t.defaultFontSize, s, i?.substitutions, t.defaultFontBold ? 700 : 400, t.defaultFontItalic ? "italic" : "normal", a, Ji(i, t.defaultFontFamily), i?.families) : void 0
	}, l = Bi.get(t);
	(!l || l.tupleKey !== c.tupleKey || l.route !== c.route || l.hasDeclaredFace !== c.hasDeclaredFace || l.canvasMdw !== c.canvasMdw) && it.invalidate(t), Bi.set(t, c);
}
function $i(e, t, n, r, i) {
	Zi(e, t), ea.set(e, i ? i.oracleFor(e) : B(e));
	let a = qi(t, r);
	(zi.get(t) !== n || a) && it.invalidate(t), r ? Hi.set(e, r) : Hi.delete(e), Qi(t, n, (ae(e.canvas) ? e.canvas.ownerDocument?.fonts : void 0) ?? f(), r, e), n ? (Ri.set(e, n), zi.set(t, n)) : (Ri.delete(e), zi.delete(t));
}
var ea = /* @__PURE__ */ new WeakMap();
function ta(e) {
	let t = ea.get(e);
	return t || (t = B(e), ea.set(e, t)), t;
}
function na(e, t) {
	return Ji(Hi.get(e), t);
}
function ra(e) {
	return Hi.get(e)?.substitutions;
}
function ia(e, n) {
	return t(n, Hi.get(e)?.families);
}
function aa(e, t, n) {
	let r = qi(e, n);
	(zi.get(e) !== t || r) && it.invalidate(e), t ? zi.set(e, t) : zi.delete(e), Qi(e, t, f(), n);
}
function oa(t, n, r = !1, i = !1) {
	let a = mt({
		family: n?.trim() || "Calibri",
		weight: r ? 700 : 400,
		style: i ? "italic" : "normal"
	}), o = Ri.get(t);
	return o ? e(o, a) : void 0;
}
function sa(e, t) {
	if (t !== void 0) {
		if (!Number.isFinite(t) || t <= 0) throw Error("XLSX maximum digit width must be a finite positive number");
		it.forWorksheet(e, t);
	}
}
var ca = "\"Courier New\", \"Liberation Mono\", monospace";
function la(e, t, n) {
	let r = e?.get(u(t));
	return r && _(r, n, "any") ? `${o(r.family)}, ` : "";
}
function ua(e, t, i, a = "") {
	let s = e?.trim() || null, c = s ? E(s) : null, l = D(s), d = (e, i = !0) => {
		let o = [...i && t ? w(t, l === "serif" ? "serif" : "sans") : [], ...r(a) ? n(l === "serif") : []];
		if (o.length === 0) return e;
		let s = e.lastIndexOf(",");
		return `${e.slice(0, s)}, ${o.map((e) => `"${e}"`).join(", ")}${e.slice(s)}`;
	}, f = i?.get(u(s ?? "Calibri")), p = f && _(f, a, "any") ? f.family : void 0;
	if (!c) {
		let e = l === "serif" ? Li : l === "mono" ? ca : Ii;
		return d(s ? p ? `${o(p)}, ${e}` : e : p ? `"Calibri", ${o(p)}, Arial, ${Ni}, sans-serif` : Fi);
	}
	let m = l === "serif", h = [...p ? [p] : [], ...w(c, m ? "serif" : "sans").filter((e) => e !== p)].map((e) => `"${e}"`).join(", ");
	return d(`${h ? `${h}, ` : ""}${m ? Li : Ii}`, !1);
}
function da(e, t, n = "", r, i, a, s) {
	let c = e?.trim(), l = S(n) ? t : void 0, u = r && (c?.toLocaleLowerCase("en-US") || "calibri") === r.requestedFamily.trim().toLocaleLowerCase("en-US") ? r : void 0, d = a && a.toLocaleLowerCase("en-US") !== c?.toLocaleLowerCase("en-US") ? `${o(a)}, ` : "", f = s && s.toLocaleLowerCase("en-US") !== c?.toLocaleLowerCase("en-US") ? `${o(s)}, ` : "";
	return u ? `${o(u.family)}, ${d}${f}${ua(c, l, i, n)}` : c ? `${o(c)}, ${d}${f}${ua(c, l, i, n)}` : ua(null, l, i, n);
}
var fa = 11;
function pa(e, t, n) {
	return n - e - t;
}
function ma(e, t, n, r) {
	return r ? pa(e, t, n) : e;
}
var ha = "#7a7a7a";
function ga(e, n, r, i, a = 400, o = "normal", s, c, l) {
	let u = n * q, d = s ? null : typeof OffscreenCanvas < "u" ? new OffscreenCanvas(1, 1) : typeof document < "u" ? document.createElement("canvas") : null, f = s ?? d?.getContext("2d");
	if (!f) return 8;
	let p = a !== 400 || o !== "normal" ? `${o} ${a} ` : "";
	s && f.save();
	try {
		f.font = `${p}${u}px ${t(da(e, void 0, "", r, i, void 0, c), l)}`;
		let n = 0;
		for (let e of "0123456789") {
			let t = f.measureText(e).width;
			t > n && (n = t);
		}
		return _a(n);
	} finally {
		s && f.restore();
	}
}
function _a(e) {
	return Math.round(e) || 8;
}
function va(e, t) {
	if (!t || typeof t[Symbol.iterator] != "function") return !1;
	let n = e.trim().toLocaleLowerCase("en-US");
	for (let e of t) if (e.family.trim().replace(/^(['"])(.*)\1$/u, "$2").toLocaleLowerCase("en-US") === n) return !0;
	return !1;
}
function ya(t) {
	if (!t.defaultFontFamily || !t.defaultFontSize) return 8;
	let n = t.defaultFontBold ? 700 : 400, r = t.defaultFontItalic ? "italic" : "normal", i = mt({
		family: t.defaultFontFamily,
		weight: n,
		style: r
	}), a = zi.get(t), o = a ? e(a, i) : void 0;
	return Bi.get(t)?.canvasMdw ?? ga(t.defaultFontFamily, t.defaultFontSize, o, Ui.get(t)?.substitutions, n, r, void 0, Ji(Ui.get(t), t.defaultFontFamily), Ui.get(t)?.families);
}
function ba(e) {
	return it.forWorksheetMeasured(e, () => ya(e));
}
function xa(e, t, n, r, i, a, o) {
	if (!(i <= 0 || a <= 0)) {
		if (o) {
			let a = e.createLinearGradient(n, r, n + i, r);
			a.addColorStop(0, J(t, .85)), a.addColorStop(1, J(t, .15)), e.fillStyle = a;
		} else e.fillStyle = J(t);
		e.fillRect(n, r, i, a);
	}
}
function Sa(e) {
	switch (e) {
		case "solid": return 1;
		case "darkGray": return .75;
		case "mediumGray": return .5;
		case "lightGray": return .25;
		case "gray125": return .125;
		case "gray0625": return .0625;
		case "darkHorizontal":
		case "darkVertical":
		case "darkDown":
		case "darkUp":
		case "darkGrid":
		case "darkTrellis": return .5;
		case "lightHorizontal":
		case "lightVertical":
		case "lightDown":
		case "lightUp":
		case "lightGrid":
		case "lightTrellis": return .25;
		default: return 1;
	}
}
var Ca = /* @__PURE__ */ new Map(), wa = {
	gray0625: [
		128,
		0,
		8,
		0,
		128,
		0,
		8,
		0
	],
	gray125: [
		136,
		0,
		34,
		0,
		136,
		0,
		34,
		0
	],
	lightGray: [
		170,
		0,
		85,
		0,
		170,
		0,
		85,
		0
	],
	mediumGray: [
		170,
		85,
		170,
		85,
		170,
		85,
		170,
		85
	],
	darkGray: [
		119,
		221,
		119,
		221,
		119,
		221,
		119,
		221
	],
	darkHorizontal: [
		4095,
		4095,
		0,
		4095,
		4095,
		0,
		4095,
		4095,
		0,
		4095,
		4095,
		0
	],
	lightHorizontal: [
		4095,
		0,
		0,
		4095,
		0,
		0,
		4095,
		0,
		0,
		4095,
		0,
		0
	],
	darkVertical: Array(12).fill(3510),
	lightVertical: Array(12).fill(2340),
	darkGrid: [
		204,
		204,
		51,
		51,
		204,
		204,
		51,
		51
	],
	lightGrid: [
		255,
		136,
		136,
		136,
		255,
		136,
		136,
		136
	],
	darkDown: [
		204,
		102,
		51,
		153,
		204,
		102,
		51,
		153
	],
	lightDown: [
		136,
		68,
		34,
		17,
		136,
		68,
		34,
		17
	],
	darkUp: [
		51,
		102,
		204,
		153,
		51,
		102,
		204,
		153
	],
	lightUp: [
		17,
		34,
		68,
		136,
		17,
		34,
		68,
		136
	],
	darkTrellis: [
		255,
		102,
		255,
		153,
		255,
		102,
		255,
		153
	],
	lightTrellis: [
		153,
		102,
		102,
		153,
		153,
		102,
		102,
		153
	]
};
function Ta(t, n, r, a) {
	let o = t.getTransform(), s = Math.max(1, Math.round(Math.hypot(o.a, o.b))), c = Math.max(1, Math.round(Math.hypot(o.c, o.d))), l = `${n}|${r}|${a}|${s}|${c}`;
	if (Ca.has(l)) return Ca.get(l);
	let u = e(wa, n);
	if (!u) return Ca.set(l, null), null;
	let d = u.length, f = i(d, d);
	if (!f) return Ca.set(l, null), null;
	let p = f.getContext("2d");
	if (!p) return Ca.set(l, null), null;
	p.fillStyle = J(a), p.fillRect(0, 0, d, d), p.fillStyle = J(r);
	for (let e = 0; e < d; e++) {
		let t = u[e];
		for (let n = 0; n < d; n++) t & 1 << d - 1 - n && p.fillRect(n, e, 1, 1);
	}
	let m = t.createPattern(f, "repeat");
	if (m && typeof DOMMatrix < "u" && (s >= 2 || c >= 2)) {
		let e = new DOMMatrix();
		e.scaleSelf(1 / s, 1 / c), m.setTransform(e);
	}
	return Ca.set(l, m), m;
}
function Ea(e, t, n, r, i, a) {
	if (t.gradient && t.gradient.stops.length > 0) return e.fillStyle = Da(e, t.gradient, n, r, i, a), e.fillRect(n, r, i, a), !0;
	let o = t.patternType;
	if (!o || o === "none") return !1;
	let s = t.fgColor ?? "000000", c = t.bgColor ?? "FFFFFF";
	if (o === "solid") return e.fillStyle = J(s), e.fillRect(n, r, i, a), !0;
	let l = Ta(e, o, s, c);
	if (l) e.fillStyle = l;
	else {
		let t = Sa(o);
		e.fillStyle = t >= 1 ? J(s) : Aa(s, c, t);
	}
	return e.fillRect(n, r, i, a), !0;
}
function Da(e, t, n, r, i, a) {
	let o;
	if (t.gradientType === "path") {
		let s = n + i * (t.left + (1 - t.right - t.left) / 2), c = r + a * (t.top + (1 - t.bottom - t.top) / 2), l = Math.hypot(Math.max(s - n, n + i - s), Math.max(c - r, r + a - c));
		o = e.createRadialGradient(s, c, 0, s, c, l);
	} else {
		let s = t.degree * Math.PI / 180, c = n + i / 2, l = r + a / 2, u = (Math.abs(Math.cos(s)) * i + Math.abs(Math.sin(s)) * a) / 2;
		o = e.createLinearGradient(c - Math.cos(s) * u, l - Math.sin(s) * u, c + Math.cos(s) * u, l + Math.sin(s) * u);
	}
	for (let e of t.stops) {
		let t = Math.min(1, Math.max(0, e.position));
		o.addColorStop(t, J(e.color));
	}
	return o;
}
var Oa = $r;
function ka(e, t, n, r, i) {
	let a = Math.max(4, Math.min(8, Math.min(r, i) * .18));
	e.save(), e.fillStyle = "#D40000", e.beginPath(), e.moveTo(t + r - a, n), e.lineTo(t + r, n), e.lineTo(t + r, n + a), e.closePath(), e.fill(), e.restore();
}
function Aa(e, t, n) {
	let r = e.replace("#", ""), i = t.replace("#", ""), a = parseInt(r.slice(0, 2), 16), o = parseInt(r.slice(2, 4), 16), s = parseInt(r.slice(4, 6), 16), c = parseInt(i.slice(0, 2), 16), l = parseInt(i.slice(2, 4), 16), u = parseInt(i.slice(4, 6), 16), d = Math.min(1, Math.max(0, n));
	return `rgb(${Math.round(a * d + c * (1 - d))},${Math.round(o * d + l * (1 - d))},${Math.round(s * d + u * (1 - d))})`;
}
function Q(e, t, n = 1) {
	return Math.round(e * q * n * t);
}
function ja(e, t) {
	let n = {
		family: e.name,
		weight: e.bold ? 700 : 400
	};
	if (!qe(t)) return n;
	let r = Ma(e, t);
	if (!r) return n;
	let i = C(r, { source: "office-mac" }), a = new Set(i.map((e) => e.weight)), o = a.size === 1 ? i[0].weight : 400, s = !i.length || a.has(n.weight) ? n.weight : o, c = i.filter((e) => e.weight === s), l = c.filter((t) => t.style === (e.italic ? "italic" : "normal")), u = l.length ? l : c, d = new Set(u.flatMap((e) => e.aliases).filter((e) => /-(?:Regular|Bold|Italic|BoldItalic|Light|Medium)$/i.test(e)).map((e) => e.replace(/-(?:Regular|Bold|Italic|BoldItalic|Light|Medium)$/i, ""))), f = new Set(u.map((e) => e.family)), p = d.size === 1 ? [...d][0] : f.size === 1 ? [...f][0] : void 0;
	return {
		family: r,
		weight: s,
		...e.bold && (s === 300 || s === 400) && i.length ? { syntheticBold: !0 } : {},
		...p && p.toLocaleLowerCase("en-US") !== r.toLocaleLowerCase("en-US") ? { fallbackAlias: p } : {}
	};
}
function Ma(e, t) {
	return e.scheme === "major" ? t?.themeJapaneseMajorFont : e.scheme === "minor" ? t?.themeJapaneseMinorFont : void 0;
}
function Na(e, t) {
	let n = t?.japanese && Ma(e, t);
	if (!t || !n) return {
		family: e.name,
		weight: e.bold ? 700 : 400
	};
	let r = `${e.scheme}:${+!!e.bold}:${+!!e.italic}`, i = t.cache.get(r);
	return i || (i = ja(e, t), t.cache.size < 8 && t.cache.set(r, i)), i;
}
function Pa(e, t, n, r, i, a = 1) {
	if (e.fillText(t, n, r), !i.bold) return;
	let o = Yi.get(e);
	!o?.japanese || !Na(i, o).syntheticBold || (e.save(), e.strokeStyle = e.fillStyle, e.lineWidth = Math.max(1, Math.round(i.size * q * a)) / 35, e.setLineDash([]), e.lineJoin = "miter", e.miterLimit = 10, e.strokeText(t, n, r), e.restore());
}
function $(e, t, n = 1, r, i = "") {
	let a = t.italic ? "italic " : "", o = Math.max(1, Math.round(t.size * q * n)), s = Na(t, Yi.get(e)), c = s.weight === 400 ? "" : `${s.weight} `;
	return t.symbolUnicode ? `${a}${c}${o}px ${ia(e, Fa)}` : `${a}${c}${o}px ${ia(e, da(s.family, r, i, oa(e, s.family, t.bold, t.italic), ra(e), s.fallbackAlias, na(e, s.family)))}`;
}
var Fa = Ii;
function Ia(e, t, n, r = 1, i) {
	let a = Na(t, Yi.get(e)).family;
	if (!n || t.symbolUnicode || !k(a)) return {
		text: n,
		font: t,
		paint: (e) => e
	};
	let { segments: o, paint: s } = sn(ta(e), n, a, $(e, t, r, i, n), () => $(e, {
		...t,
		size: 24,
		symbolUnicode: !0
	}, 1));
	return o.length === 1 ? {
		text: s(n),
		font: o[0].unicode ? {
			...t,
			symbolUnicode: !0
		} : t,
		paint: s
	} : {
		text: s(n),
		font: t,
		paint: s,
		runs: o.map((e) => {
			let t = [...e.authored].map(s);
			return e.unicode ? {
				text: t.join(""),
				symbolUnicode: !0,
				slots: t
			} : {
				text: t.join(""),
				slots: t
			};
		})
	};
}
function La(e, t, n, r = 1, i) {
	let a;
	return t.forEach((o, s) => {
		let c = qa(n, o), l = Ia(e, c, o.text, r, i);
		if (!l.runs && l.text === o.text && l.font === c) {
			a?.push(o);
			return;
		}
		if (a ??= t.slice(0, s), l.runs) {
			for (let e of l.runs) a.push({
				...o,
				text: e.text,
				slots: e.slots,
				...e.symbolUnicode ? { symbolUnicode: !0 } : {}
			});
			return;
		}
		let u = [...o.text].map(l.paint), d = l.font === c ? {
			...o,
			text: l.text,
			slots: u
		} : {
			...o,
			text: l.text,
			symbolUnicode: !0,
			slots: u
		};
		a.push(d);
	}), a ?? t;
}
function Ra(e, t, n, r = 1, i, a) {
	if (!t?.length) return a?.runs;
	let o = Yi.get(e);
	return t.some((e) => k(Na(qa(n, e), o).family)) ? La(e, t, n, r, i) : void 0;
}
function za(e, t, n, r, i) {
	let a = e.font, o = t.map((t) => {
		let a = qa(n, t), o = t.text.replace(/\n/gu, " ");
		return e.font = $(e, no(a), r, i, o), {
			text: o,
			font: a,
			width: e.measureText(o).width
		};
	});
	return e.font = a, o;
}
function Ba(e, t) {
	return e.flatMap((e) => {
		let n = qa(t, e);
		return (e.slots ?? [...e.text]).map((e) => ({
			text: e,
			font: n
		}));
	});
}
function Va(e, t, n, r, i, a) {
	let o = e.font, s = 0, c = n, l = Math.min(t.length, n + r);
	for (; c < l;) {
		let n = t[c].font, r = "";
		for (; c < l && t[c].font === n;) r += t[c++].text;
		e.font = $(e, no(n), i, a, r), s += e.measureText(r).width;
	}
	return e.font = o, s;
}
function Ha(e, t, n, r, i) {
	let a = Ba(t, n);
	return (t, n) => Va(e, a, n, [...t].length, r, i);
}
function Ua(e, t, n, r, i) {
	let a = Ia(e, t, n, r, i);
	if (a.runs) return za(e, a.runs, t, r, i).reduce((e, t) => e + t.width, 0);
	let o = e.font;
	e.font = $(e, a.font, r, i, a.text);
	let s = e.measureText(a.text).width;
	return e.font = o, s;
}
function Wa(e, t, n, r, i, a, o, s, c, l, u, d) {
	if (t.length === 0) return;
	let f = n?.fontId ?? 0, p = a.fonts[f] ?? a.fonts[0];
	if (!p) return;
	let m = n?.alignment ?? "left";
	e.save(), e.textBaseline = "top", e.textAlign = "left", e.fillStyle = l;
	let h = (t) => {
		let n = Ia(e, p, t, c, u);
		return n.runs ? n.runs.map((e) => ({
			text: e.text,
			font: qa(n.font, e)
		})) : [{
			text: n.text,
			font: n.font
		}];
	}, g = (t) => t.reduce((t, n) => (e.font = $(e, n.font, c, u, n.text), t + e.measureText(n.text).width), 0), _ = (t, n, r) => {
		let i = n;
		for (let n of t) e.font = $(e, n.font, c, u, n.text), Pa(e, n.text, i, r, n.font, c), i += e.measureText(n.text).width;
		return i;
	}, v = s + Math.round(2 * c);
	if (m === "noControl") {
		let n = o;
		for (let e of t) n = _(h(e.text), n, v);
		e.restore();
		return;
	}
	let y = nn(t, r, o, m, (t, n) => d ? d(t, n) : Ga(e, t, i));
	for (let t of y) {
		let n = [...t.text], r = h(t.text), i = g(r);
		if (t.spread === "distribute" && n.length > 1 && i < t.width) {
			let a = (t.width - i) / (n.length - 1);
			try {
				e.letterSpacing = `${a}px`;
			} catch {}
			_(r, t.x, v);
			try {
				e.letterSpacing = "0px";
			} catch {}
		} else t.spread === "center" ? _(r, t.x + (t.width - i) / 2, v) : _(r, t.x, v);
	}
	e.restore();
}
function Ga(e, t, n) {
	let r = e.font;
	e.font = n;
	let i = e.measureText(t).width;
	return e.font = r, i;
}
function Ka(e, t, n, r, i, a, o = 1) {
	if (e.save(), e.strokeStyle = i, e.lineWidth = .5, e.beginPath(), a) {
		let i = r - 1, a = r + 1, c = i + s(i, .5, o), l = a + s(a, .5, o);
		e.moveTo(t, c), e.lineTo(n, c), e.moveTo(t, l), e.lineTo(n, l);
	} else {
		let i = r + s(r, .5, o);
		e.moveTo(t, i), e.lineTo(n, i);
	}
	e.stroke(), e.restore();
}
function qa(e, t) {
	let n = Ja(e, t);
	return t.symbolUnicode ? {
		...n,
		symbolUnicode: !0
	} : n;
}
function Ja(e, t) {
	let n = t.font;
	return n ? {
		bold: n.bold,
		italic: n.italic,
		underline: n.underline,
		underlineStyle: n.underlineStyle,
		strike: n.strike,
		size: n.size ?? e.size,
		color: n.color ?? null,
		name: n.name ?? e.name,
		vertAlign: n.vertAlign
	} : e;
}
function Ya(e, t) {
	let n = Xe(e, t) ?? {
		fontId: 0,
		fillId: 0,
		borderId: 0,
		numFmtId: 0,
		alignH: null,
		alignV: null,
		wrapText: !1
	};
	return {
		font: e.fonts[n.fontId] ?? {
			bold: !1,
			italic: !1,
			underline: !1,
			strike: !1,
			size: fa,
			color: null,
			name: null
		},
		fill: e.fills[n.fillId] ?? {
			patternType: "none",
			fgColor: null,
			bgColor: null
		},
		border: e.borders[n.borderId] ?? {
			left: null,
			right: null,
			top: null,
			bottom: null
		},
		xf: n
	};
}
function Xa(e, t, n, r) {
	let i = [];
	for (let a of t.split("\n")) i.push(...Za(e, a, n, r));
	return i;
}
function Za(e, t, n, r = (t) => e.measureText(t).width) {
	return Ot(t, n, r);
}
function Qa(e, t, n, r, i, a) {
	return kt(e, t, n, i, qa, (t, n) => {
		e.font = $(e, no(t), r, a, n);
	}, fa);
}
function $a(e) {
	return e === "number" ? "right" : e === "bool" ? "center" : "left";
}
function eo(e, t, n) {
	return e === "middle" ? {
		underline: t + Math.round(n * .55),
		strike: t
	} : e === "bottom" ? {
		underline: t + 1,
		strike: t - Math.round(n * .35)
	} : {
		underline: t + n + 1,
		strike: t + Math.round(n * .5)
	};
}
function to(e) {
	let { alignV: t, cy: n, cellH: r, paddingY: i } = e;
	return t === "top" ? {
		baseline: "top",
		textY: n + i
	} : t === "center" ? {
		baseline: "middle",
		textY: n + r / 2
	} : {
		baseline: "bottom",
		textY: n + r - i
	};
}
function no(e) {
	return e.vertAlign === "superscript" || e.vertAlign === "subscript" ? {
		...e,
		size: e.size * .65
	} : e;
}
function ro(e, t, n, r, i, a, o, c, l) {
	e.textAlign = "left", e.textBaseline = i;
	let u = c.needBidi ? Qr(t, c.baseRtl ?? !1) : null, d = e, f = n;
	for (let n = 0; n < t.length; n++) {
		let p = u ? u.order[n] : n;
		if (u) try {
			d.direction = u.rtl[p] ? "rtl" : "ltr";
		} catch {}
		let m = t[p], h = no(m.font);
		e.font = $(e, h, a, l, m.text);
		let g = c.fontColor ?? m.font.color;
		e.fillStyle = g ? J(g) : "#000000";
		let _ = Q(m.font.size, a), v = 0;
		m.font.vertAlign === "superscript" ? v = -Math.round(_ * .35) : m.font.vertAlign === "subscript" && (v = Math.round(_ * .1)), Pa(e, m.text, f, r + v, h, a);
		let y = Q(h.size, a);
		if (m.font.underline || m.font.strike) {
			let t = eo(i, r, y);
			if (m.font.underline) {
				let n = g ? J(g) : "#000000", r = m.font.underlineStyle === "double" || m.font.underlineStyle === "doubleAccounting";
				Ka(e, f, f + m.width, t.underline + v, n, r, o);
			}
			if (m.font.strike) {
				let n = t.strike + v, r = n + s(n, .5, o);
				e.save(), e.strokeStyle = g ? J(g) : "#000000", e.lineWidth = .5, e.beginPath(), e.moveTo(f, r), e.lineTo(f + m.width, r), e.stroke(), e.restore();
			}
		}
		f += m.width;
	}
	if (u) try {
		d.direction = "ltr";
	} catch {}
}
function io(e, t, n, r, i, a, o, s, c) {
	let { alignH: l, cx: u, cellW: d, leftPad: f, paddingX: p } = n, m = t.reduce((e, t) => e + t.width, 0), h;
	h = l === "right" ? u + d - p - m : l === "center" ? u + d / 2 - m / 2 : u + f;
	let { needBidi: g, baseRtl: _ } = Zr(a.readingOrder, t.map((e) => e.text).join(""));
	ro(e, t, h, o, s, r, i, {
		fontColor: a.fontColor,
		needBidi: g,
		baseRtl: _
	}, c);
}
function ao(e, t, n, r, i, a, o, s, c, l) {
	io(e, t.map((t) => {
		let r = qa(n, t);
		return e.font = $(e, no(r), i, l, t.text), {
			text: t.text,
			font: r,
			width: e.measureText(t.text).width
		};
	}), r, i, a, o, s, c, l);
}
function oo(e, t, n, r, i, a, o = {}, s) {
	let { baseline: c, textY: l } = to(r);
	ao(e, t, n, r, i, a, o, l, c, s);
}
function so(e, t, n, r, i, a, o = {}, s) {
	let { alignV: c, cy: l, cellH: u, paddingY: d } = r, f = Lo(t, n, i), p = f.reduce((e, t) => e + t.heightPx, 0), m;
	m = c === "top" ? l + d : c === "center" ? l + (u - p) / 2 : l + u - p - d;
	for (let t of f) t.runs.length > 0 && ao(e, t.runs, n, r, i, a, o, m, "top", s), m += t.heightPx;
}
var co = 5;
function lo(e, t, n, r, i, a, o = (t) => e.measureText(t).width) {
	if (r.shrinkToFit || r.textRotation || r.wrapText) return n;
	let s = i - a - co;
	return Ye(t, n, (e) => o(e) <= s);
}
function uo(e, t, n, r) {
	return k(Na(t, Yi.get(e)).family) ? (i) => Ua(e, t, i, n, r) : void 0;
}
function fo(e, t, n, r, i, a, o, s, c) {
	let l = Math.max(0, t) + 3, u = Math.min(t + r, e.canvas.width) - 3 - l;
	if (u <= 0) return;
	let d = Ia(e, o, "#", s, c);
	d.font !== o && (e.font = $(e, d.font, s, c, d.text));
	let f = e.measureText(d.text).width, p = f > 0 ? Math.max(1, Math.floor(u / f)) : 1;
	e.textAlign = "left";
	let { baseline: m, textY: h } = to({
		alignH: "left",
		alignV: a,
		cx: t,
		cy: n,
		cellW: r,
		cellH: i,
		leftPad: 3,
		paddingX: 3,
		paddingY: 2
	});
	e.textBaseline = m, Pa(e, d.paint("#".repeat(p)), l, h, d.font, s);
}
function po(e, t, n, r, i, a, o = {}, s) {
	t.some((e) => e.text.includes("\n")) ? so(e, t, n, r, i, a, o, s) : oo(e, t, n, r, i, a, o, s);
}
function mo(e, t, n, r, i, a) {
	let { alignV: o, cy: s, cellH: c, leftPad: l, paddingX: u, paddingY: d } = i, f = Xa(e, t, i.cellW - l - u);
	if (f.length === 1) {
		let { baseline: t, textY: o } = to(i);
		e.textBaseline = t, Pa(e, f[0], n, o, r, a);
		return;
	}
	let p = Q(r.size, a, 1.2), m = f.length * p, h;
	h = o === "top" ? s + d : o === "center" ? s + (c - m) / 2 : s + c - m - d, e.textBaseline = "top";
	for (let t = 0; t < f.length; t++) Pa(e, f[t], n, h + t * p, r, a);
}
function ho(e, t, n, r, i, a, o = {}, s) {
	let { alignH: c, alignV: l, cx: u, cy: d, cellW: f, cellH: p, leftPad: m, paddingX: h, paddingY: g } = r, _ = Qa(e, t, n, i, f - m - h, s);
	if (_.length === 1) {
		let { baseline: t, textY: n } = to(r);
		io(e, _[0].segments, r, i, a, o, n, t, s);
		return;
	}
	let v = _.reduce((e, t) => e + Q(t.maxFontSize, i, 1.2), 0), y;
	y = l === "top" ? d + g : l === "center" ? d + (p - v) / 2 : d + p - v - g;
	let b = t.map((e) => e.text).join("").split("\n").map((e) => Zr(o.readingOrder, e));
	for (let t of _) {
		let n = t.segments.reduce((e, t) => e + t.width, 0), r;
		r = c === "right" ? u + f - h - n : c === "center" ? u + f / 2 - n / 2 : u + m;
		let { needBidi: l, baseRtl: d } = b[t.para];
		ro(e, t.segments, r, y, "top", i, a, {
			fontColor: o.fontColor,
			needBidi: l,
			baseRtl: d
		}, s), y += Q(t.maxFontSize, i, 1.2);
	}
}
function go(e, t, n, r, i, a, o, s, c, l, u) {
	let d = Ba(t, n), f = _o(d, c), p = o === "top" ? i + s : o === "center" ? i + (a - f) / 2 : i + a - f - s;
	e.textAlign = "center", e.textBaseline = "top";
	let m;
	for (let { text: t, font: n } of d) {
		if (n !== m) {
			m = n, e.font = $(e, n, c, u, t);
			let r = l ?? n.color;
			e.fillStyle = r ? J(r) : "#000000";
		}
		let i = Q(n.size, c, 1.1), a = t.codePointAt(0) ?? 0, o = ie(a) && oe(e, a);
		ti(e, t, r, p, i, o, (t, r, i) => Pa(e, t, r, i, n, c)), p += i;
	}
}
function _o(e, t) {
	return e.reduce((e, n) => e + Q(n.font.size, t, 1.1), 0);
}
function vo(e) {
	let t = "";
	for (; e > 0;) {
		let n = (e - 1) % 26;
		t = String.fromCharCode(65 + n) + t, e = Math.floor((e - 1) / 26);
	}
	return t;
}
var yo = [
	"#FF0000",
	"#FFFF00",
	"#00B050"
], bo = [
	"#FF0000",
	"#FF6600",
	"#FFFF00",
	"#00B050"
], xo = [
	"#FF0000",
	"#FF6600",
	"#FFFF00",
	"#92D050",
	"#00B050"
];
function So(e, t, n, r, i, a) {
	if (t === "NoIcons") return;
	let o = t || "3TrafficLights1", s = parseInt(o[0]) || 3, c = s === 5 ? xo : s === 4 ? bo : yo, l = c[Math.max(0, Math.min(n, c.length - 1))];
	if (e.save(), e.fillStyle = l, o.includes("Arrow")) {
		let t = a / 2;
		e.beginPath(), n === s - 1 ? (e.moveTo(r + t, i), e.lineTo(r + a, i + a), e.lineTo(r, i + a)) : n === 0 ? (e.moveTo(r, i), e.lineTo(r + a, i), e.lineTo(r + t, i + a)) : (e.moveTo(r, i + a * .3), e.lineTo(r + a, i + t), e.lineTo(r, i + a * .7)), e.closePath(), e.fill();
	} else o === "3Signs" && n < 2 ? (e.beginPath(), n === 0 ? (e.moveTo(r + a / 2, i), e.lineTo(r + a, i + a / 2), e.lineTo(r + a / 2, i + a), e.lineTo(r, i + a / 2)) : (e.moveTo(r + a / 2, i), e.lineTo(r + a, i + a), e.lineTo(r, i + a)), e.closePath(), e.fill()) : o.includes("Flag") ? (e.beginPath(), e.moveTo(r, i), e.lineTo(r + a, i), e.lineTo(r, i + a), e.closePath(), e.fill()) : (e.beginPath(), e.arc(r + a / 2, i + a / 2, a / 2, 0, Math.PI * 2), e.fill());
	e.restore();
}
function Co(e, t, n, r, i) {
	let a = Math.max(6, Math.round(Math.min(r, i) * .45)), o = t + r - a - 1, s = n + i - a - 1;
	e.save(), e.fillStyle = "#D0D0D0", e.fillRect(o, s, a, a), e.fillStyle = "#444444";
	let c = a * .55, l = o + (a - c) / 2, u = s + (a - c * .5) / 2;
	e.beginPath(), e.moveTo(l, u), e.lineTo(l + c, u), e.lineTo(l + c / 2, u + c * .5), e.closePath(), e.fill(), e.restore();
}
function wo(e) {
	let t = /* @__PURE__ */ new Map(), n = ko(e, "worksheet-sparkline-index", "index-sparkline-coordinates");
	for (let r of e.sparklineGroups ?? []) {
		let e = Infinity, i = -Infinity;
		if (r.minAxisType === "group" || r.maxAxisType === "group") {
			for (let t of r.sparklines) for (let n of t.values) typeof n == "number" && (n < e && (e = n), n > i && (i = n));
			(!isFinite(e) || !isFinite(i)) && (e = 0, i = 1);
		}
		for (let a of r.sparklines) {
			let o = a.values.filter((e) => typeof e == "number"), s = o.length ? Math.min(...o) : 0, c = o.length ? Math.max(...o) : 1, l = r.minAxisType === "custom" && typeof r.manualMin == "number" ? r.manualMin : r.minAxisType === "group" ? e : s, u = r.maxAxisType === "custom" && typeof r.manualMax == "number" ? r.manualMax : r.maxAxisType === "group" ? i : c;
			Rt(t, `${a.row}:${a.col}`, {
				kind: r.kind,
				values: a.values,
				min: l,
				max: u,
				displayEmptyCellsAs: r.displayEmptyCellsAs === "zero" || r.displayEmptyCellsAs === "span" ? r.displayEmptyCellsAs : "gap",
				displayXAxis: r.displayXAxis,
				lineWeight: r.lineWeight,
				markers: r.markers,
				high: r.high,
				low: r.low,
				first: r.first,
				last: r.last,
				negative: r.negative,
				colorSeries: r.colorSeries,
				colorNegative: r.colorNegative,
				colorAxis: r.colorAxis,
				colorMarkers: r.colorMarkers,
				colorFirst: r.colorFirst,
				colorLast: r.colorLast,
				colorHigh: r.colorHigh,
				colorLow: r.colorLow
			}, n);
		}
	}
	return t;
}
function To(e, t, n, r, i, a, o, c, l, u, d, f, p, m, h, g, _) {
	if (h <= 0 || g <= 0) return;
	let { styles: v, cellMap: y, mergeAnchorMap: b, mergeSkipSet: x, cfContext: S, cs: C, dpr: w } = t, T, E = i.length, D = a.length, O = new Set(c), k = new Set(o), A = (e, n) => t.rtl ? pa(e, n, t.canvasW) : e, j = [], M = -l;
	for (let e = 0; e < E; e++) j.push(M), M += i[e];
	let N = [], ee = -u;
	for (let e = 0; e < D; e++) N.push(ee), ee += a[e];
	e.save(), e.beginPath(), e.rect(A(p, h), m, h, g), e.clip();
	let te = [], ne = [], P = [];
	for (let i of t.worksheet.mergeCells ?? []) {
		let a = i.top, s = i.left;
		if (O.has(a) && k.has(s) || !c.some((e) => e >= i.top && e <= i.bottom) || !o.some((e) => e >= i.left && e <= i.right)) continue;
		let y = t.mergeAnchorMap.get(`${a}:${s}`);
		if (!y) continue;
		let b = d - l + t.colAxis.offsetOf(s) - t.colAxis.offsetOf(r), x = f - u + t.rowAxis.offsetOf(a) - t.rowAxis.offsetOf(n), E = y.totalW, D = y.totalH;
		if (b + E <= p || b >= p + h || x + D <= m || x >= m + g) continue;
		b = A(b, E);
		let j = `${a}:${s}`, M = t.cellMap.get(j), { font: N, fill: ee, border: te, xf: P } = Ya(v, Ke(t.worksheet, M, s)), F = Yr(M, a, s, S, v.dxfs ?? []), I = F.fill ?? ee, L = t.structuredStyleMap.get(j);
		if (!Ea(e, I, b, x, E, D) && L?.fill && Ea(e, L.fill, b, x, E, D), F.dataBar && F.dataBar.ratio > 0) {
			let t = Math.max(0, (E - 4) * F.dataBar.ratio);
			xa(e, F.dataBar.color, b + 2, x + 2, t, D - 4, F.dataBar.gradient);
		}
		let R = Ls(Is(te, a, s, y.right, y.bottom, t.cellMap, v), F.border);
		if (ne.push(() => zs(e, R, b, x, E, D, w)), !M) continue;
		let z = Je(M, v, F.numFmt, t.worksheet.date1904, T ??= Ge(v.numFmts));
		if (!z.text || z.text === "0" && t.worksheet.showZeros === !1) continue;
		let B = Io(N, F, L);
		e.font = $(e, B, C, _, z.text);
		let re = t.hyperlinkMap.get(j), ie = Po(L, P), ae = re ? "#0563C1" : F.fontColor ?? z.color ?? ie ?? N.color;
		e.fillStyle = ae ? J(ae) : "#000000";
		let V = P.alignH ?? $a(M.value.type), H = P.alignV ?? "bottom", U = P.indent ? Math.round(P.indent * 3 * t.mdw) : 0, oe = 3 + (V === "left" || !P.alignH ? U : 0), se = F.iconSet ? Math.max(8, Math.round(Math.min(E, D) * .55)) + 4 : 0, ce = lo(e, M, z, P, E, oe - 3 + se, uo(e, B, C, _)), le = ce.text, W = Ia(e, B, le, C, _);
		if (W.font !== B && (e.font = $(e, W.font, C, _, W.text)), e.save(), e.beginPath(), e.rect(b, x, E, D), e.clip(), ce.fill) {
			fo(e, b, x, E, D, H, B, C, _), e.restore();
			continue;
		}
		let G;
		V === "right" ? (G = b + E - 3, e.textAlign = "right") : V === "center" ? (G = b + E / 2, e.textAlign = "center") : (G = b + oe, e.textAlign = "left");
		let ue = Mo(L, P), de = M.value.type === "text" ? M.value.runs : void 0, fe = ue == null ? B : {
			...B,
			color: ue
		}, pe = de && Fo(de, ue), me = Ra(e, pe, fe, C, _, W), he = me && !pe?.length ? {
			...B,
			color: ae,
			underline: B.underline || !!re
		} : fe, K = me ?? pe, ge = K && K.length > 0;
		if (P.wrapText && ge) ho(e, K, he, {
			alignH: V,
			alignV: H,
			cx: b,
			cy: x,
			cellW: E,
			cellH: D,
			leftPad: oe,
			paddingX: 3,
			paddingY: 2
		}, C, w, {
			fontColor: F.fontColor,
			readingOrder: P.readingOrder
		}, _);
		else if (P.wrapText) mo(e, W.text, G, W.font, {
			alignH: V,
			alignV: H,
			cx: b,
			cy: x,
			cellW: E,
			cellH: D,
			leftPad: oe,
			paddingX: 3,
			paddingY: 2
		}, C);
		else if (ge) po(e, K, he, {
			alignH: V,
			alignV: H,
			cx: b,
			cy: x,
			cellW: E,
			cellH: D,
			leftPad: oe,
			paddingX: 3,
			paddingY: 2
		}, C, w, {
			fontColor: F.fontColor,
			readingOrder: P.readingOrder
		}, _);
		else {
			let { baseline: t, textY: n } = to({
				alignH: V,
				alignV: H,
				cx: b,
				cy: x,
				cellW: E,
				cellH: D,
				leftPad: oe,
				paddingX: 3,
				paddingY: 2
			});
			e.textBaseline = t, Pa(e, W.text, G, n, W.font, C);
		}
		e.restore();
	}
	for (let n = 0; n < D; n++) {
		let r = c[n], l = f + N[n], u = a[n];
		if ((l + u <= m || l >= m + g) && !o.some((e) => {
			let t = b.get(`${r}:${e}`);
			return t != null && l + t.totalH > m && l < m + g;
		})) continue;
		let D = /* @__PURE__ */ new Set(), O = /* @__PURE__ */ new Set(), k = -1, M = (e) => {
			if (k >= 0 && e - k >= 2) {
				for (let t = k; t < e - 1; t++) D.add(t);
				for (let t = k + 1; t < e; t++) O.add(t);
			}
			k = -1;
		};
		for (let e = 0; e <= E; e++) {
			let n = !1, i = !1;
			if (e < E && o[e] <= t.selectionLastCol) {
				let a = `${r}:${o[e]}`;
				if (!x.has(a) && !b.has(a)) {
					let r = y.get(a);
					n = Ya(v, Ke(t.worksheet, r, o[e])).xf.alignH === "centerContinuous", i = !!(r && r.value && r.value.type !== "empty");
				}
			}
			n ? i && k >= 0 && e > k ? (M(e), k = e) : k < 0 && (k = e) : M(e);
		}
		let ee = !0;
		for (let a = 0; a < E; a++) {
			let c = o[a], f = d + j[a], k = i[a], M = c === t.firstViewportCol && ee, N = `${r}:${c}`;
			if (x.has(N)) {
				ee = f + k <= p || f >= p + h;
				continue;
			}
			let F = b.get(N), I = F ? F.totalW : k, L = F ? F.totalH : u, R = f + I <= p || f >= p + h;
			if (l + L <= m || l >= m + g || R && !t.overflowTextAnchors.has(N)) {
				ee = !0;
				continue;
			}
			ee = !1;
			let z = A(f, I), B = y.get(N), { font: re, fill: ae, border: V, xf: H } = Ya(v, Ke(t.worksheet, B, c)), U = Yr(B, r, c, S, v.dxfs ?? []), se = Ea(e, U.fill ?? ae, z, l, I, L), ce = t.structuredStyleMap.get(N);
			if (!se && ce?.fill && (se = Ea(e, ce.fill, z, l, I, L)), t.commentCells.has(N) && ka(e, z, l, I, L), U.dataBar && U.dataBar.ratio > 0) {
				let t = Math.max(0, (I - 4) * U.dataBar.ratio);
				xa(e, U.dataBar.color, z + 2, l + 2, t, L - 4, U.dataBar.gradient);
			}
			let le = t.sparklineMap.get(N);
			if (le && at(e, {
				x: z,
				y: l,
				w: I,
				h: L
			}, le), t.worksheet.isChartSheet !== !0 && t.worksheet.showGridlines !== !1 && !se) {
				if (e.strokeStyle = "#d0d0d0", e.lineWidth = .5, e.beginPath(), !D.has(a)) {
					let t = z + I + s(z + I, .5, w);
					e.moveTo(t, l), e.lineTo(t, l + L);
				}
				let t = l + L + s(l + L, .5, w);
				if (e.moveTo(z, t), e.lineTo(z + I, t), n === 0) {
					let t = l + s(l, .5, w);
					e.moveTo(z, t), e.lineTo(z + I, t);
				}
				if (M) {
					let t = z + s(z, .5, w);
					e.moveTo(t, l), e.lineTo(t, l + L);
				}
				e.stroke();
			}
			let W = Ls(F ? Is(V, r, c, F.right, F.bottom, y, v) : V, U.border);
			ce && (W = {
				...W,
				top: W.top?.style ? W.top : ce.top ?? W.top,
				bottom: W.bottom?.style ? W.bottom : ce.bottom ?? W.bottom,
				left: W.left?.style ? W.left : ce.left ?? W.left,
				right: W.right?.style ? W.right : ce.right ?? W.right
			}), (D.has(a) || O.has(a)) && (W = {
				...W,
				left: O.has(a) ? null : W.left,
				right: D.has(a) ? null : W.right
			});
			let G = y.get(`${r - 1}:${c}`), ue = G ? Ya(v, Ke(t.worksheet, G, c)).border.bottom : null;
			if (ue?.style && (n === 0 || W.top?.style) && (W = {
				...W,
				top: Us(W.top, ue)
			}), !O.has(a)) {
				let e = y.get(`${r}:${c - 1}`), n = e ? Ya(v, Ke(t.worksheet, e, c - 1)).border.right : null;
				n?.style && (M || W.left?.style) && (W = {
					...W,
					left: Us(W.left, n)
				});
			}
			let de = t.autoFilterCells.has(N), fe = () => {
				de && Co(e, z, l, k, L);
			};
			if (F) {
				let t = W;
				ne.push(() => zs(e, t, z, l, I, L, w)), fe();
			} else {
				let t = W;
				P.push(() => {
					zs(e, t, z, l, I, L, w), fe();
				});
			}
			if (!B) continue;
			let pe = Je(B, v, U.numFmt, t.worksheet.date1904, T ??= Ge(v.numFmts));
			!pe.text || pe.text === "0" && t.worksheet.showZeros === !1 || te.push(() => {
				let n = Io(re, U, ce);
				e.font = $(e, n, C, _, pe.text);
				let u = t.hyperlinkMap.get(N), d = Po(ce, H), p = u ? "#0563C1" : U.fontColor ?? pe.color ?? d ?? re.color;
				e.fillStyle = p ? J(p) : "#000000";
				let m = B.value.type === "number", h = H.alignH ?? $a(B.value.type), g = H.alignV ?? "bottom", S = H.indent ? Math.round(H.indent * 3 * t.mdw) : 0, T = U.iconSet ? Math.max(8, Math.round(Math.min(I, L) * .55)) : 0, D = T > 0 ? T + 4 : 0, O = 3 + (h === "left" || !H.alignH ? S : 0) + D, k = I, j = a;
				if (h === "centerContinuous" && !F) for (let e = a + 1; e < E && o[e] <= t.selectionLastCol; e++) {
					let n = `${r}:${o[e]}`;
					if (x.has(n) || b.has(n)) break;
					let a = y.get(n);
					if (a && a.value.type !== "empty" || Ya(v, Ke(t.worksheet, a, o[e])).xf.alignH !== "centerContinuous") break;
					k += i[e], j = e;
				}
				let M = t.rtl ? z - (k - I) : z, ee = lo(e, B, pe, H, h === "centerContinuous" ? k : I, O - 3, uo(e, n, C, _)), te = ee.text, ne = Ia(e, n, te, C, _), P = ne.font, R = ne.text;
				P !== n && (e.font = $(e, P, C, _, R));
				let ae = Mo(ce, H), V = B.value.type === "text" ? B.value.runs : void 0, se = ae == null ? n : {
					...n,
					color: ae
				}, le = V && Fo(V, ae), W = {
					...n,
					color: p,
					underline: n.underline || !!u
				}, G = Ra(e, le, se, C, _, ne), ue = G && !le?.length ? W : se, de = G ?? le, fe = G && za(e, G, ue, C, _), me = () => fe ? fe.reduce((e, t) => e + t.width, 0) : e.measureText(R).width, he = h === "centerContinuous" ? M : z, K = h === "centerContinuous" ? k : I, ge = te.includes("\n");
				if (!F && !H.wrapText && !H.textRotation && !m && !ge) {
					let e = me(), n = h === "centerContinuous", s = n ? e + 6 : e + O + 3, c = n ? k : I;
					if (s > c) {
						let e = s - c, l = 0, u = 0;
						h === "right" ? u = e : h === "center" || n ? (u = e / 2, l = e / 2) : l = e;
						let d = t.rtl ? -1 : 1, f = t.rtl ? a - 1 : j + 1, p = t.rtl ? 1 : -1, m = t.rtl ? j + 1 : a - 1;
						if (l > 0) {
							let e = l;
							for (let t = f; t >= 0 && t < E && e > 0; t += d) {
								let n = `${r}:${o[t]}`;
								if (x.has(n) || b.has(n)) break;
								let a = y.get(n);
								if (a && a.value.type !== "empty") break;
								K += i[t], e -= i[t];
							}
						}
						if (u > 0) {
							let e = u;
							for (let t = m; t >= 0 && t < E && e > 0; t += p) {
								let n = `${r}:${o[t]}`;
								if (x.has(n) || b.has(n)) break;
								let a = y.get(n);
								if (a && a.value.type !== "empty") break;
								he -= i[t], K += i[t], e -= i[t];
							}
						}
					}
				}
				let q = te, _e = 0;
				if (h === "fill" && !m && te.length > 0) {
					let e = Math.max(1, I - 6), t = me();
					if (t > 0 && t < e) {
						let n = Math.max(1, Math.floor(e / t));
						q = te.repeat(n), G && (de = Array.from({ length: n }, () => G).flat());
					}
				}
				if (h === "distributed" || h === "justify" && !H.wrapText && !ge) {
					let t = Math.max(1, I - 6), n = fe ? me() : e.measureText(ne.paint(q)).width, r = Math.max(1, [...q].length - 1);
					n < t && (_e = Math.max(0, (t - n) / r));
				}
				let ve, ye;
				h === "right" ? (ve = z + I - 3, ye = "right") : h === "center" ? (ve = z + I / 2, ye = "center") : h === "centerContinuous" ? (ve = M + k / 2, ye = "center") : h === "distributed" || h === "justify" && !H.wrapText && !ge ? (ve = z + 3, ye = "left") : (ve = z + O, ye = "left");
				let be = H.textRotation ?? 0, xe = be === 255, Se = be > 0 && be !== 255;
				if (U.iconSet && T > 0 && (e.save(), e.beginPath(), e.rect(z, l, I, L), e.clip(), So(e, U.iconSet.name, U.iconSet.index, z + 2, l + (L - T) / 2, T), e.restore()), e.save(), e.beginPath(), e.rect(he, l, K, L), e.clip(), ee.fill) {
					fo(e, z, l, I, L, g, n, C, _), e.restore();
					return;
				}
				if (xe) {
					let t = Q(re.size, C, 1.1), n = [...te].length;
					if (G) {
						go(e, G, ue, z + I / 2, l, L, g, 2, C, U.fontColor, _), e.restore();
						return;
					}
					let r = n * t, i = g === "top" ? l + 2 : g === "center" ? l + (L - r) / 2 : l + L - r - 2;
					e.textAlign = "center", e.textBaseline = "top";
					let a = (t, n, r) => Pa(e, t, n, r, P, C);
					for (let n of te) {
						let r = ne.paint(n), o = r.codePointAt(0) ?? 0, s = ie(o) && oe(e, o);
						ti(e, r, z + I / 2, i, t, s, a), i += t;
					}
					e.restore();
					return;
				}
				if (Se) {
					let t = be <= 90 ? -(be * Math.PI / 180) : (be - 90) * Math.PI / 180;
					if (e.translate(z + I / 2, l + L / 2), e.rotate(t), fe) {
						let t = fe.reduce((e, t) => e + t.width, 0), { needBidi: n, baseRtl: r } = Zr(H.readingOrder, fe.map((e) => e.text).join(""));
						ro(e, fe, -t / 2, 0, "middle", C, w, {
							fontColor: U.fontColor,
							needBidi: n,
							baseRtl: r
						}, _), e.restore();
						return;
					}
					e.textAlign = "center", e.textBaseline = "middle", Pa(e, R, 0, 0, P, C), e.restore();
					return;
				}
				if (H.shrinkToFit) {
					let t = me(), n = I - O - 3;
					if (t > n && t > 0) {
						let r = n / t, i = h === "right" ? z + I - 3 : h === "center" ? z + I / 2 : z + O;
						e.transform(r, 0, 0, 1, i * (1 - r), 0);
					}
				}
				if (e.textAlign = ye, _e > 0) try {
					e.letterSpacing = `${_e}px`;
				} catch {}
				try {
					e.direction = Xr(H.readingOrder, R) ? "rtl" : "ltr";
				} catch {}
				let Ce = de?.length ? de : void 0, we = G && h === "centerContinuous" ? {
					alignH: "center",
					alignV: g,
					cx: M,
					cy: l,
					cellW: k,
					cellH: L,
					leftPad: O,
					paddingX: 3,
					paddingY: 2
				} : {
					alignH: h,
					alignV: g,
					cx: z,
					cy: l,
					cellW: I,
					cellH: L,
					leftPad: O,
					paddingX: 3,
					paddingY: 2
				};
				if (H.wrapText && Ce) ho(e, Ce, ue, we, C, w, {
					fontColor: U.fontColor,
					readingOrder: H.readingOrder
				}, _);
				else if (H.wrapText) mo(e, R, ve, P, {
					alignH: h,
					alignV: g,
					cx: z,
					cy: l,
					cellW: I,
					cellH: L,
					leftPad: O,
					paddingX: 3,
					paddingY: 2
				}, C);
				else if (Ce) po(e, Ce, ue, we, C, w, {
					fontColor: U.fontColor,
					readingOrder: H.readingOrder
				}, _);
				else {
					let t = P.vertAlign, r = Q(re.size, C), i = 0;
					t === "superscript" ? i = -Math.round(r * .35) : t === "subscript" && (i = Math.round(r * .1));
					let a = t ? {
						...P,
						size: P.size * .65
					} : P;
					t && (e.font = $(e, a, C, _, R));
					let o = null, c = () => o ??= e.measureText(R), d = () => {
						let e = Math.min(c().width, K - O - 3);
						return {
							x: h === "right" ? z + I - 3 - e : h === "center" ? z + I / 2 - e / 2 : z + O,
							width: e
						};
					}, f = Q(a.size, C);
					if (n.underline || u) {
						let { x: t, width: r } = d(), a = (g === "top" ? l + 2 + f + 1 : g === "center" ? l + L / 2 + Math.round(f * .55) : l + L - 2 + 1) + i, o = u ? "#0563C1" : p ? J(p) : "#000000", s = n.underlineStyle === "double" || n.underlineStyle === "doubleAccounting";
						Ka(e, t, t + r, a, o, s, w);
					}
					if (n.strike) {
						let { x: t, width: n } = d(), r = (g === "top" ? l + 2 + Math.round(f * .5) : g === "center" ? l + L / 2 : l + L - 2 - Math.round(f * .35)) + i, a = r + s(r, .5, w);
						e.save(), e.strokeStyle = p ? J(p) : "#000000", e.lineWidth = .5, e.beginPath(), e.moveTo(t, a), e.lineTo(t + n, a), e.stroke(), e.restore();
					}
					if (R.includes("\n")) {
						let t = R.split("\n"), n = Q(re.size, C, 1.2), r = t.length * n, o;
						g === "top" ? (o = l + 2, e.textBaseline = "top") : g === "center" ? (o = l + (L - r) / 2, e.textBaseline = "top") : (o = l + L - r - 2, e.textBaseline = "top");
						for (let r = 0; r < t.length; r++) Pa(e, t[r], ve, o + r * n + i, a, C);
					} else {
						let { baseline: t, textY: n } = to({
							alignH: h,
							alignV: g,
							cx: z,
							cy: l,
							cellW: I,
							cellH: L,
							leftPad: O,
							paddingX: 3,
							paddingY: 2
						});
						e.textBaseline = t, Pa(e, ne.paint(q), ve, n + i, a, C);
					}
				}
				let Te = B.value.type === "text" ? B.value.phoneticRuns : void 0;
				if (B.showPhonetic && Te && Te.length > 0 && !te.includes("\n")) {
					let t = $(e, P, C, _, R), n = fe ? me() : Ga(e, R, t), r;
					r = h === "right" ? z + I - 3 - n : h === "center" ? z + I / 2 - n / 2 : z + O;
					let i = p ? J(p) : "#000000";
					Wa(e, Te, B.value.type === "text" ? B.value.phoneticPr : void 0, te, t, v, r, l, C, i, _, G ? Ha(e, G, ue, C, _) : (n) => Ga(e, ne.paint(n), t));
				}
				if (e.restore(), te && t.textRuns) {
					let e = c >= t.textRunPane.first && c <= t.textRunPane.last, n = e ? t.textRuns.owned : t.textRuns.foreign;
					n.has(N) || n.set(N, {
						sheetName: t.worksheet.name,
						cellRef: ei(r, c),
						text: te,
						x: e ? z : A(f + t.textRunPane.ownerShiftX, I),
						y: l,
						width: I,
						height: L,
						row: r,
						col: c
					});
				}
			});
		}
	}
	for (let e of P) e();
	for (let e of ne) e();
	for (let e of te) e();
	e.restore();
}
var Eo = /* @__PURE__ */ new WeakMap(), Do = /* @__PURE__ */ new WeakSet();
function Oo(e) {
	Eo.delete(e), Do.delete(e);
}
function ko(e, t, n) {
	return {
		resource: t,
		operation: n,
		limit: Qe(e).maxCoordinateIndexEntries
	};
}
function Ao(e, t) {
	let n = Qe(e).maxCoordinateIndexEntries, r = Eo.get(e);
	if (r && r.rowCount === e.rows.length && r.coordinateIndexLimit === n && (t === void 0 || r.styleDxfs === t.dxfs)) return r;
	r && Eo.delete(e), Do.delete(e);
	let i = ko(e, "worksheet-cell-index", "index-worksheet-cells"), a = zt(e.rows, i), o = /* @__PURE__ */ new Map();
	for (let t of e.rows) {
		let e = t.cells.filter((e) => e.value.type !== "empty").map((e) => e.col).sort((e, t) => e - t);
		e.length > 0 && o.set(t.index, e);
	}
	let s = ko(e, "worksheet-merge-anchor-index", "index-merge-anchor-coordinates"), c = ko(e, "worksheet-merge-skip-index", "expand-merged-cell-coordinates"), { anchors: l, continuations: u } = en(e.mergeCells ?? [], s, c), d = /* @__PURE__ */ new Set();
	if (e.autoFilter) {
		let t = e.autoFilter, n = ko(e, "worksheet-auto-filter-index", "expand-auto-filter-coordinates");
		Lt({
			top: t.top,
			bottom: t.top,
			left: t.left,
			right: t.right
		}, n);
		for (let e = t.left; e <= t.right; e++) Bt(d, `${t.top}:${e}`, n);
	}
	let f = /* @__PURE__ */ new Map(), p = ko(e, "worksheet-hyperlink-index", "index-hyperlink-coordinates");
	for (let t of e.hyperlinks ?? []) t.url && Rt(f, `${t.row}:${t.col}`, t.url, p);
	let m = /* @__PURE__ */ new Set(), h = ko(e, "worksheet-comment-index", "index-comment-coordinates");
	for (let t of e.commentRefs ?? []) {
		let e = Oa(t);
		e && Bt(m, `${e.row}:${e.col}`, h);
	}
	let g = {
		rowCount: e.rows.length,
		coordinateIndexLimit: n,
		cellMap: a,
		nonEmptyColsByRow: o,
		cfContext: Lr(e, a),
		mergeAnchorSet: l,
		mergeSkipSet: u,
		autoFilterCells: d,
		hyperlinkMap: f,
		commentCells: m,
		structuredStyleMap: $t(e, t?.dxfs),
		styleDxfs: t?.dxfs,
		sparklineMap: wo(e)
	};
	return Eo.set(e, g), g;
}
var jo = /* @__PURE__ */ new WeakMap();
function Mo(e, t) {
	return t.ownFontColor || !e?.fontColorFromTable ? null : e.fontColorAuto ? No : e.fontColor ?? null;
}
var No = "#000000";
function Po(e, t) {
	return t.ownFontColor ? null : e?.fontColorAuto ? No : e?.fontColor ?? null;
}
function Fo(e, t) {
	return t == null ? e : e.map((e) => e.font?.normalColor ? {
		...e,
		font: {
			...e.font,
			color: t
		}
	} : e);
}
function Io(e, t, n) {
	let r = t.fontBold ?? (e.bold || !!n?.bold), i = t.fontItalic ?? (e.italic || !!n?.italic), a = t.fontUnderline ?? (e.underline || !!n?.underline), o = t.fontStrike ?? (e.strike || !!n?.strike);
	return r === e.bold && i === e.italic && a === e.underline && o === e.strike ? e : {
		...e,
		bold: r,
		italic: i,
		underline: a,
		strike: o
	};
}
function Lo(e, t, n) {
	let r = [[]];
	for (let t of e) {
		let e = t.text.split("\n");
		for (let n = 0; n < e.length; n++) n > 0 && r.push([]), e[n] !== "" && r[r.length - 1].push({
			...t,
			text: e[n]
		});
	}
	let i = t.size;
	return r.map((e) => {
		if (e.length === 0) return {
			runs: e,
			heightPx: Q(i || fa, n, 1.2)
		};
		let r = 0;
		for (let n of e) {
			let e = qa(t, n);
			e.size > r && (r = e.size), i = e.size;
		}
		return {
			runs: e,
			heightPx: Q(r, n, 1.2)
		};
	});
}
function Ro(e, t, n, r, i, a, o, s, c, l) {
	let u = i.alignH ?? $a(t.value.type), d = i.indent ? Math.round(i.indent * 3 * o) : 0, f = s ? Math.max(8, Math.round(Math.min(a, c) * .55)) : 0, p = f > 0 ? f + 4 : 0, m = 3 + (u === "left" || !i.alignH ? d : 0) + p, h = Math.max(1, a - m - 3), g = t.value.type === "text" ? t.value.runs : void 0, _ = i.textRotation ?? 0, v = Ia(e, r, n, 1, l), y = Ra(e, g, r, 1, l, v), b = y ?? g;
	if (e.font = $(e, v.font, 1, l, v.text), _ === 255) return y ? _o(Ba(y, r), 1) + 4 : [...n].length * Q(r.size, 1, 1.1) + 4;
	if (_ > 0) {
		let t = _ <= 90 ? _ * Math.PI / 180 : (_ - 90) * Math.PI / 180, n = y && za(e, y, r, 1, l), i = n ? Math.max(...n.map((e) => Q(e.font.size, 1, 1.2))) : Q(r.size, 1, 1.2), a = n ? n.reduce((e, t) => e + t.width, 0) : e.measureText(v.text.replace(/\n/g, " ")).width;
		return Math.abs(Math.sin(t)) * a + Math.abs(Math.cos(t)) * i + 4;
	}
	let x;
	if (i.wrapText && b?.length) x = Qa(e, b, r, 1, h, l).map((e) => Q(e.maxFontSize, 1, 1.2));
	else if (i.wrapText) {
		e.font = $(e, v.font, 1, l, v.text);
		let t = Q(r.size, 1, 1.2);
		x = Xa(e, v.text, h).map(() => t);
	} else if (b?.length) x = Lo(b, r, 1).map((e) => e.heightPx);
	else {
		let e = Math.max(1, n.split("\n").length), t = Q(r.size, 1, 1.2);
		x = Array.from({ length: e }, () => t);
	}
	return x.reduce((e, t) => e + t, 0) + (x.length > 1 ? 4 : 2);
}
function zo(e, t, n, r) {
	if (n.wrapText || (n.textRotation ?? 0) > 0) return !0;
	if (e.value.type === "text") {
		if (e.value.text.includes("\n")) return !0;
		for (let n of e.value.runs ?? []) if (Q(qa(t, n).size, 1, 1.2) > r) return !0;
	}
	return Q(t.size, 1, 1.2) > r;
}
function Bo(e, t, n, r) {
	if (jo.has(t) || t.isChartSheet) return !1;
	if (t.defaultRowHeightCustom === !0) return jo.set(t, { derived: /* @__PURE__ */ new Map() }), !1;
	let i, a = ba(t), o = tt(t.defaultRowHeight), s = Q(t.normalFontSize ?? t.defaultFontSize ?? fa, 1, 1.2), { cfContext: c, mergeAnchorSet: l, mergeSkipSet: u, structuredStyleMap: d } = Ao(t, n), f = /* @__PURE__ */ new Map(), p = !1;
	e.save();
	try {
		for (let m of t.rows) {
			if (m.hidden || m.customHeight === !0 || m.height !== null || rt(et(t), m.index) || Object.hasOwn(t.rowHeights, m.index)) continue;
			let h = o, g = [];
			for (let o of m.cells) {
				let f = `${m.index}:${o.col}`;
				if (o.value.type === "empty" || l.has(f) || u.has(f)) continue;
				let { font: p, xf: _ } = Ya(n, o.styleIndex ?? 0);
				if (!zo(o, p, _, s)) continue;
				let v = Yr(o, m.index, o.col, c, n.dxfs ?? []), y = Io(p, v, d.get(f)), b = Je(o, n, v.numFmt, t.date1904, i ??= Ge(n.numFmts)).text;
				if (!b || b === "0" && t.showZeros === !1) continue;
				let x = a.col.sizeOf(o.col);
				h = Math.max(h, Ro(e, o, b, y, _, x, a.maximumDigitWidth, v.iconSet, Math.ceil(h), r)), v.iconSet && g.push({
					cell: o,
					text: b,
					font: y,
					xf: _,
					cellWidthPx: x,
					iconSet: v.iconSet
				});
			}
			let _ = g.length === 0;
			for (let t = 0; !_ && t < 32; t++) {
				let t = Math.ceil(h), n = h;
				for (let i of g) n = Math.max(n, Ro(e, i.cell, i.text, i.font, i.xf, i.cellWidthPx, a.maximumDigitWidth, i.iconSet, t, r));
				h = n, _ = Math.ceil(h) === t;
			}
			if (!_) for (let t of g) h = Math.max(h, Ro(e, t.cell, t.text, t.font, t.xf, t.cellWidthPx, a.maximumDigitWidth, t.iconSet, t.cellWidthPx, r));
			let v = Math.ceil(h);
			if (v > o) {
				let e = nt(v);
				t.rowHeights[m.index] = e, f.set(m.index, e), p = !0;
			}
		}
	} finally {
		e.restore();
	}
	return jo.set(t, { derived: f }), p && it.invalidate(t), p;
}
function Vo(e) {
	return jo.has(e);
}
function Ho(e) {
	return jo.get(e)?.derived ?? /* @__PURE__ */ new Map();
}
function Uo(e, t = []) {
	let n = jo.get(e);
	if (!n) return;
	let r = new Set(t), i = !1;
	for (let [t, a] of n.derived) rt(et(e), t) || r.has(t) || e.rowHeights[t] === a && (delete e.rowHeights[t], i = !0);
	jo.delete(e), i && it.invalidate(e);
}
var Wo = /* @__PURE__ */ new WeakMap();
function Go(e, t) {
	let n = Wo.get(t);
	n || (n = /* @__PURE__ */ new WeakMap(), Wo.set(t, n));
	let r = n.get(e);
	return r || (r = e.filter((e) => t.sizeOf(e) > 0), n.set(e, r)), r;
}
function Ko(e, t) {
	let n = 0, r = e.length;
	for (; n < r;) {
		let i = n + r >> 1;
		e[i] < t ? n = i + 1 : r = i;
	}
	return n - 1;
}
function qo(e, t) {
	let n = 0, r = e.length;
	for (; n < r;) {
		let i = n + r >> 1;
		e[i] <= t ? n = i + 1 : r = i;
	}
	return n;
}
function Jo(e, t, n) {
	let r = e[Ko(e, t)];
	if (r == null || n.sizeOf(r) > 0) return r;
	let i = Go(e, n);
	return i[Ko(i, t)];
}
function Yo(e, t, n) {
	let r = e[qo(e, t)];
	if (r == null || n.sizeOf(r) > 0) return r;
	let i = Go(e, n);
	return i[qo(i, t)];
}
function Xo(e, t, n, r, i) {
	return (e.mergeCells ?? []).some((e) => {
		if (t < e.top || t > e.bottom) return !1;
		let a = Math.max(n, e.left), o = Math.min(r, e.right);
		return a <= o && i.offsetOf(o + 1) > i.offsetOf(a);
	});
}
function Zo(e, t, n, r, i, a, o, s, c, l, u, d, f, p, m, h, g) {
	let _ = d, v = f, y, b = /* @__PURE__ */ new Set(), x = (i, u, d, f) => {
		let _ = `${i}:${u}`, v = r.get(_);
		if (!v || v.value.type === "empty" || s.has(_)) return !1;
		let { font: b, xf: x } = Ya(n, Ke(t, v, u)), S = Yr(v, i, u, a, n.dxfs ?? []), C = Je(v, n, S.numFmt, t.date1904, y ??= Ge(n.numFmts)).text;
		if (!C || C === "0" && t.showZeros === !1 || v.value.type === "number" || x.wrapText || x.textRotation || C.includes("\n")) return !1;
		let w = o.get(_), T = S.fontBold ?? (b.bold || !!w?.bold), E = S.fontItalic ?? (b.italic || !!w?.italic), D = T !== b.bold || E !== b.italic ? {
			...b,
			bold: T,
			italic: E
		} : b, O = Ia(e, D, C, p, g);
		e.font = $(e, O.font, p, g, O.text);
		let k = x.alignH ?? $a(v.value.type), A = x.indent ? Math.round(x.indent * 3 * m) : 0, j = c.sizeOf(u), M = l.sizeOf(i), N = S.iconSet ? Math.max(8, Math.round(Math.min(j, M) * .55)) : 0, ee = N > 0 ? N + 4 : 0, te = 3 + (k === "left" || !x.alignH ? A : 0) + ee, ne = Ra(e, v.value.type === "text" ? v.value.runs : void 0, D, p, g, O), P = (ne ? za(e, ne, D, p, g).reduce((e, t) => e + t.width, 0) : e.measureText(O.text).width) + te + 3, F = Math.max(0, P - j);
		return F <= 0 ? !1 : (k === "center" || k === "centerContinuous" ? F / 2 : ((h ? d === "higher" ? "left" : "right" : d === "higher" ? "right" : "left") == "left" ? k === "right" : k !== "right") ? F : 0) > f;
	};
	for (let e of u) {
		let n = i.get(e);
		if (!n) continue;
		let a = Jo(n, d, c), o = r.get(`${e}:${d}`);
		a != null && (!o || o.value.type === "empty") && !Xo(t, e, a + 1, d, c) && x(e, a, "higher", c.offsetOf(d) - c.offsetOf(a + 1)) && (_ = Math.min(_, a), b.add(`${e}:${a}`));
		let s = Yo(n, f, c), l = r.get(`${e}:${f}`);
		s != null && s <= 16384 && (!l || l.value.type === "empty") && !Xo(t, e, f, s - 1, c) && x(e, s, "lower", c.offsetOf(s) - c.offsetOf(f + 1)) && (v = Math.max(v, s), b.add(`${e}:${s}`));
	}
	return {
		startCol: _,
		endCol: v,
		anchorKeys: b
	};
}
var Qo = new Set([
	"rowHeights",
	"colWidths",
	"colCollapsed"
]);
function $o(e, t) {
	let n = e, r = t;
	for (let e of Object.keys(n)) if (!Qo.has(e) && n[e] !== r[e]) return !1;
	for (let e of Object.keys(r)) if (!Qo.has(e) && !Object.hasOwn(n, e)) return !1;
	return !0;
}
function es(e, t, n) {
	Ze(e, t), $e(e, t), $o(e, t) ? (Eo.set(t, Ao(e, n)), Do.add(t)) : Do.delete(t) && Eo.delete(t);
}
function ts(e, t, n, r, i = {}, a) {
	$i(e, t, i.officeFontRoutes, i.fontSources, i.symbolFaces), sa(t, i.authoritativeMdw);
	let o = i.dpr ?? 1, c = i.cellScale ?? 1, l = t.isChartSheet === !0, u = ba(t), d = u.maximumDigitWidth, f = e.canvas.width / o, p = e.canvas.height / o;
	e.clearRect(0, 0, f, p), e.fillStyle = "#ffffff", e.fillRect(0, 0, f, p);
	let m = (e) => Math.round(e * c), h = l ? 0 : m(50), g = l ? 0 : m(22), { rows: _, cols: v } = r, y = Math.max(1, Math.trunc(r.row) || 1), b = Math.max(1, Math.trunc(r.col) || 1), x = (i.scrollOffsetX ?? 0) * c, S = (i.scrollOffsetY ?? 0) * c, { col: C, row: w } = u.axesAtScale(c), T = C.bandsToCover(1, l ? 0 : i.freezeCols ?? 0, Math.max(0, f - h)), E = w.bandsToCover(1, l ? 0 : i.freezeRows ?? 0, Math.max(0, p - g)), D = E.at(-1)?.index ?? 0, O = T.at(-1)?.index ?? 0, k = T.map(({ index: e }) => e), A = E.map(({ index: e }) => e), j = T.map(({ size: e }) => e), M = E.map(({ size: e }) => e), N = j.reduce((e, t) => e + t, 0), ee = M.reduce((e, t) => e + t, 0), te = C.bandsToCover(b, Math.min(16384, b + v - 1)), ne = w.bandsToCover(y, Math.min(1048576, y + _ - 1)), P = te.map(({ index: e }) => e), F = ne.map(({ index: e }) => e), I = te.map(({ size: e }) => e), L = ne.map(({ size: e }) => e), { cellMap: R, cfContext: z, mergeSkipSet: B, autoFilterCells: re, hyperlinkMap: ie, commentCells: ae, structuredStyleMap: V, sparklineMap: H, nonEmptyColsByRow: U } = Ao(t, n), oe = /* @__PURE__ */ new Map(), se = ko(t, "worksheet-merge-anchor-index", "index-merge-anchor-coordinates");
	for (let e of t.mergeCells ?? []) {
		let t = C.offsetOf(e.right + 1) - C.offsetOf(e.left), n = w.offsetOf(e.bottom + 1) - w.offsetOf(e.top);
		Rt(oe, `${e.top}:${e.left}`, {
			totalW: t,
			totalH: n,
			right: e.right,
			bottom: e.bottom
		}, se);
	}
	let ce = P[0] ?? b, le = P.at(-1) ?? Math.min(16384, b + v - 1), W = [...new Set([...A, ...F])], G = Zo(e, t, n, R, U, z, V, oe, C, w, W, ce, le, c, d, t.rightToLeft === !0, a), ue = O > 0 ? Zo(e, t, n, R, U, z, V, oe, C, w, W, 1, O, c, d, t.rightToLeft === !0, a) : {
		startCol: 1,
		endCol: 0,
		anchorKeys: /* @__PURE__ */ new Set()
	}, de = ue.endCol > O ? C.bandsToCover(1, ue.endCol) : T, fe = de.map(({ index: e }) => e), pe = de.map(({ size: e }) => e), me = C.bandsToCover(G.startCol, G.endCol), he = me.map(({ index: e }) => e), K = me.map(({ size: e }) => e), ge = x + C.offsetOf(ce) - C.offsetOf(G.startCol), q = {
		worksheet: t,
		styles: n,
		cellMap: R,
		mergeAnchorMap: oe,
		mergeSkipSet: B,
		cfContext: z,
		colWidths: K,
		rowHeights: L,
		colAxis: C,
		rowAxis: w,
		frozenColWidths: j,
		frozenRowHeights: M,
		frozenW: N,
		frozenH: ee,
		startRow: y,
		startCol: b,
		cs: c,
		dpr: o,
		autoFilterCells: re,
		hyperlinkMap: ie,
		commentCells: ae,
		structuredStyleMap: V,
		sparklineMap: H,
		overflowTextAnchors: G.anchorKeys,
		textRunPane: {
			first: O + 1,
			last: Infinity,
			ownerShiftX: 0
		},
		firstViewportCol: ce,
		selectionLastCol: Infinity,
		textRuns: i.onTextRun ? {
			owned: /* @__PURE__ */ new Map(),
			foreign: /* @__PURE__ */ new Map()
		} : void 0,
		mdw: d,
		rtl: t.rightToLeft === !0,
		canvasW: f,
		threeD: i.threeD
	}, _e = h, ve = g, ye = _e + N, J = ve + ee, be = Math.max(0, f - ye), xe = Math.max(0, p - J), Se = _e - C.offsetOf(1), Ce = ye - x - C.offsetOf(ce), we = l ? 0 : Math.max(0, Math.trunc(i.freezeCols ?? 0)), Te = {
		...q,
		textRunPane: {
			first: we + 1,
			last: Infinity,
			ownerShiftX: Se - Ce
		}
	}, Ee = {
		...q,
		overflowTextAnchors: ue.anchorKeys,
		textRunPane: {
			first: 1,
			last: we,
			ownerShiftX: Ce - Se
		},
		firstViewportCol: k[0] ?? 1,
		selectionLastCol: O
	};
	if (D > 0 && O > 0 && To(e, Ee, 1, 1, pe, M, fe, A, 0, 0, _e, ve, _e, ve, N, ee, a), D > 0 && To(e, Te, 1, G.startCol, K, M, he, A, ge, 0, ye, ve, ye, ve, be, ee, a), O > 0 && To(e, Ee, y, 1, pe, L, fe, F, 0, S, _e, J, _e, J, N, xe, a), l || To(e, Te, y, G.startCol, K, L, he, F, ge, S, ye, J, ye, J, be, xe, a), q.textRuns && i.onTextRun) {
		for (let e of q.textRuns.owned.values()) i.onTextRun(e);
		for (let [e, t] of q.textRuns.foreign) q.textRuns.owned.has(e) || i.onTextRun(t);
	}
	rs(e, t, C, w, i.loadedImages, c, y, b, x, S, ye, J, be, xe, t.rightToLeft === !0, f, i.threeD, i.regionMap, i.chartEx, a), !l && t.slicers && t.slicers.length > 0 && rc(e, t, C, w, c, y, b, x, S, ye, J, be, xe, t.rightToLeft === !0, f), l || ns(e, f, p, y, b, _, v, I, L, P, F, x, S, j, M, k, A, N, ee, h, g, c, o, i.selectedRowRange ?? null, i.selectedColRange ?? null, t.rightToLeft === !0, i.chromeColors);
	let De = t.rightToLeft === !0;
	if (D > 0) {
		e.save(), e.strokeStyle = ha, e.lineWidth = .5, e.beginPath();
		let t = J + s(J, .5, o);
		e.moveTo(0, t), e.lineTo(f, t), e.stroke(), e.restore();
	}
	if (O > 0) {
		e.save(), e.strokeStyle = ha, e.lineWidth = .5, e.beginPath();
		let t = De ? f - ye : ye, n = t + s(t, .5, o);
		e.moveTo(n, g), e.lineTo(n, p), e.stroke(), e.restore();
	}
}
function ns(e, t, n, r, i, a, o, c, l, u, d, f, p, m, h, g, _, v, y, b, x, S, C, w, T, E, D) {
	let O = D?.surface ?? "#f8f9fa", k = D?.mutedSurface ?? "#e8eaed", A = D?.selectedSurface ?? "#caddf6", j = D?.border ?? "#c8ccd0", M = D?.accent ?? "#5b9bd5", N = D?.text ?? "#444", ee = (e) => !T || e < T.start || e > T.end ? O : T.strong ? A : k, te = (e) => !T || e < T.start || e > T.end ? j : T.strong ? M : j, ne = (e) => !w || e < w.start || e > w.end ? O : w.strong ? A : k, P = (e) => !w || e < w.start || e > w.end ? j : w.strong ? M : j, F = `${Math.max(1, Math.round(11 * S))}px ${ia(e, Fi)}`, I = b + v, L = x + y, R = .5 / C, z = (e, n) => E ? pa(e, n, t) : e, B = E ? t - b : 0;
	e.fillStyle = O, e.fillRect(B, 0, b, x), e.strokeStyle = j, e.lineWidth = .5, e.beginPath();
	let re = E ? B + s(B, .5, C) : B + b - R;
	e.moveTo(re, 0), e.lineTo(re, x), e.moveTo(B, x - R), e.lineTo(B + b, x - R), e.stroke(), e.font = F, e.fillStyle = N;
	let ie = (t, n, r) => {
		let i = z(n, r);
		e.fillStyle = ee(t), e.fillRect(i, 0, r, x), e.strokeStyle = te(t), e.lineWidth = .5, e.beginPath();
		let a = i + s(i, .5, C);
		e.moveTo(a, 0), e.lineTo(a, x), e.moveTo(i, x - R), e.lineTo(i + r, x - R), e.stroke(), e.fillStyle = N, e.textAlign = "center", e.textBaseline = "middle", e.fillText(vo(t), i + r / 2, x / 2);
	}, ae = (t, n, r) => {
		let i = B;
		e.fillStyle = ne(t), e.fillRect(i, n, b, r), e.strokeStyle = P(t), e.lineWidth = .5, e.beginPath();
		let a = n + s(n, .5, C), o = E ? i + s(i, .5, C) : i + b - R;
		e.moveTo(o, n), e.lineTo(o, n + r), e.moveTo(i, a), e.lineTo(i + b, a), e.stroke(), e.fillStyle = N, e.textBaseline = "middle";
		let c = Math.max(2, Math.round(4 * S));
		E ? (e.textAlign = "left", e.fillText(String(t), i + c, n + r / 2)) : (e.textAlign = "right", e.fillText(String(t), i + b - c, n + r / 2));
	};
	if (m.length > 0) {
		e.save(), e.beginPath(), e.rect(z(b, v), 0, v, x), e.clip();
		let t = b;
		for (let e = 0; e < m.length; e++) ie(g[e], t, m[e]), t += m[e];
		e.restore();
	}
	e.save(), e.beginPath(), e.rect(z(I, t - I), 0, t - I, x), e.clip();
	let V = I - f;
	for (let e = 0; e < c.length; e++) {
		let n = c[e];
		V + n > I && V < t && ie(u[e], V, n), V += n;
	}
	if (e.restore(), h.length > 0) {
		e.save(), e.beginPath(), e.rect(B, x, b, y), e.clip();
		let t = x;
		for (let e = 0; e < h.length; e++) ae(_[e], t, h[e]), t += h[e];
		e.restore();
	}
	e.save(), e.beginPath(), e.rect(B, L, b, n - L), e.clip();
	let H = L - p;
	for (let e = 0; e < l.length; e++) {
		let t = l[e];
		H + t > L && H < n && ae(d[e], H, t), H += t;
	}
	e.restore();
}
function rs(e, t, n, r, i, a, o, s, c, l, u, d, f, p, m, h, g, _, v, y) {
	let b = [], x = 0;
	if (i) for (let e of t.images ?? []) b.push({
		kind: "image",
		zOrder: e.zOrder ?? 2 ** 53 - 1,
		fallbackOrder: x++,
		anchor: e
	});
	for (let e of t.shapeGroups ?? []) for (let t of e.shapes) b.push({
		kind: "shape",
		zOrder: t.zOrder ?? 2 ** 53 - 1,
		fallbackOrder: x++,
		anchor: e,
		shape: t
	});
	for (let e of t.charts ?? []) b.push({
		kind: "chart",
		zOrder: e.zOrder ?? 2 ** 53 - 1,
		fallbackOrder: x++,
		anchor: e
	});
	b.sort((e, t) => e.zOrder - t.zOrder || e.fallbackOrder - t.fallbackOrder);
	for (let x of b) x.kind === "image" ? os(e, t, n, r, i, a, o, s, c, l, u, d, f, p, m, h, [x.anchor]) : x.kind === "shape" ? ss(e, t, n, r, a, o, s, c, l, u, d, f, p, i, m, h, [x.anchor], y, x.shape) : Ws(e, t, n, r, a, o, s, c, l, u, d, f, p, m, h, i, [x.anchor], g, _, v);
}
function is(e, t) {
	return e.offsetOf(t);
}
function as(e, t) {
	return e.offsetOf(t);
}
function os(e, t, n, r, i, a, o, s, c, l, u, d, f, p, m, h, g = t.images) {
	if (f <= 0 || p <= 0) return;
	let _ = is(n, s), v = as(r, o);
	e.save(), e.beginPath();
	let y = ma(u, f, h, m);
	e.rect(y, d, f, p), e.clip();
	for (let o of g) {
		let s = Ai(o), g = Oi(o.imagePath, Mi(o, s), s), b = i.get(g), x = Si(i, g, "tiff");
		if (!b && !x) continue;
		let { x: S, y: C, width: w, height: T } = _i(t, o, n, r, a);
		if (w <= 0 || T <= 0) continue;
		let E = ma(u + (S - _) - c, w, h, m), D = d + (C - v) - l, O = b && !o.srcRect ? Ei(b, E, D, w, T) : null, k = O ? Di(O, E + w / 2, D + T / 2, o.rotation ?? 0, o.flipH ?? !1, o.flipV ?? !1) : wi({
			x: E,
			y: D,
			width: w,
			height: T
		}, o.rotation);
		if (k.x + k.width < y || k.x > y + f || k.y + k.height < d || k.y > d + p) continue;
		let A = () => {
			b ? me(e, b, o.srcRect, E, D, w, T) : we(e, "tiff", {
				x: E,
				y: D,
				width: w,
				height: T
			});
		}, j = () => {
			if (o.alpha != null && o.alpha < 1) {
				e.save();
				try {
					e.globalAlpha = o.alpha, A();
				} finally {
					e.restore();
				}
			} else A();
		}, M = o.rotation ?? 0, N = o.flipH ?? !1, ee = o.flipV ?? !1;
		M === 0 && !N && !ee ? j() : Ee(e, {
			rect: {
				x: E,
				y: D,
				w,
				h: T
			},
			geometry: {
				kind: "preset",
				name: "rect",
				adjustments: []
			},
			fill: null,
			stroke: null,
			transform: {
				rotationDeg: M,
				flipH: N,
				flipV: ee
			}
		}, j);
	}
	e.restore();
}
function ss(e, t, n, r, i, a, o, s, c, l, u, d, f, p, m, h, g = t.shapeGroups ?? [], _, v) {
	if (d <= 0 || f <= 0 || g.length === 0) return;
	let y = is(n, o), b = as(r, a);
	e.save(), e.beginPath();
	let x = ma(l, d, h, m);
	e.rect(x, u, d, f), e.clip();
	for (let a of g) {
		let { x: o, y: g, width: S, height: C } = _i(t, a, n, r, i);
		if (!(S >= 0 && C >= 0 && (S > 0 || C > 0))) continue;
		let w = ma(l + (o - y) - s, S, h, m), T = u + (g - b) - c, E = v ? [v] : a.shapes, D = E.some((e) => e.geom?.type === "image" && de(e.geom.blipEffects ?? []));
		if (!(!D && (w + S < x || w > x + d)) && !(!D && (T + C < u || T > u + f))) for (let t of E) {
			let n = w + t.x * S, r = T + t.y * C, o = t.w * S, s = t.h * C;
			o >= 0 && s >= 0 && (o > 0 || s > 0) && ((o === 0 || s === 0) && !((t.geom?.type === "preset" || t.geom?.type === "custom") && t.strokeColor && t.strokeWidth > 0) || ps(e, t, n, r, o, s, i, p, _, a));
		}
	}
	e.restore();
}
function cs(e, t, n, r, i, a) {
	if (t.w <= 0 || t.h <= 0) return;
	let o = i / t.w, s = a / t.h, c = n, l = r, u = n, d = r;
	for (let i of t.commands) switch (i.op) {
		case "moveTo": {
			let t = n + i.x * o, a = r + i.y * s;
			e.moveTo(t, a), c = u = t, l = d = a;
			break;
		}
		case "lineTo": {
			let t = n + i.x * o, a = r + i.y * s;
			e.lineTo(t, a), c = t, l = a;
			break;
		}
		case "cubicBezTo": {
			let t = n + i.x3 * o, a = r + i.y3 * s;
			e.bezierCurveTo(n + i.x1 * o, r + i.y1 * s, n + i.x2 * o, r + i.y2 * s, t, a), c = t, l = a;
			break;
		}
		case "quadBezTo": {
			let t = n + i.x2 * o, a = r + i.y2 * s;
			e.quadraticCurveTo(n + i.x1 * o, r + i.y1 * s, t, a), c = t, l = a;
			break;
		}
		case "arcTo": {
			let t = i.wr * o, n = i.hr * s;
			if (t <= 0 || n <= 0) break;
			let r = i.stAng / 6e4 * (Math.PI / 180), a = i.swAng / 6e4 * (Math.PI / 180), u = c - Math.cos(r) * t, d = l - Math.sin(r) * n, f = r + a;
			e.ellipse(u, d, t, n, 0, r, f, a < 0), c = u + Math.cos(f) * t, l = d + Math.sin(f) * n;
			break;
		}
		case "close":
			e.closePath(), c = u, l = d;
			break;
	}
}
function ls(e, t, n, r, i, a) {
	if (t.geom.type === "custom") for (let o of t.geom.paths) o.fill !== "none" && cs(e, o, n, r, i, a);
	else (t.geom.type !== "preset" || !M(e, t.geom.name, n, r, i, a, t.geom.adj ?? [])) && e.rect(n, r, i, a);
}
function us(e) {
	let t = [];
	for (let n of e) (n.cmd === "moveTo" || t.length === 0) && t.push([]), t[t.length - 1].push(n);
	return t;
}
var ds = (e) => !!e && e.type !== "none";
function fs(e, t, n) {
	if (e.length === 0) return null;
	let r = N(e.flatMap((e) => us(e.commands.map((t) => {
		let n = (t) => t / e.w, r = (t) => t / e.h;
		switch (t.op) {
			case "moveTo":
			case "lineTo": return {
				cmd: t.op,
				x: n(t.x),
				y: r(t.y)
			};
			case "cubicBezTo": return {
				cmd: "cubicBezTo",
				x1: n(t.x1),
				y1: r(t.y1),
				x2: n(t.x2),
				y2: r(t.y2),
				x: n(t.x3),
				y: r(t.y3)
			};
			case "quadBezTo": return {
				cmd: "quadBezTo",
				x1: n(t.x1),
				y1: r(t.y1),
				x: n(t.x2),
				y: r(t.y2)
			};
			case "arcTo": return {
				cmd: "arcTo",
				wr: n(t.wr),
				hr: r(t.hr),
				stAng: t.stAng / 6e4,
				swAng: t.swAng / 6e4
			};
			case "close": return { cmd: "close" };
		}
	})))), i = e[0].stroke === !1 ? null : r.start, a = e[e.length - 1].stroke === !1 ? null : r.end, o = (e) => e && {
		x: e.x * t,
		y: e.y * n,
		angle: Math.atan2(e.dy * n, e.dx * t)
	};
	return i || a ? {
		start: o(i),
		end: o(a)
	} : null;
}
function ps(e, t, n, r, i, a, o, s, c, l) {
	if (_e(t.strokeFill) && (e = ve(e)), e.save(), t.rot !== 0 || t.flipH || t.flipV ? (e.translate(n + i / 2, r + a / 2), e.rotate(t.rot * Math.PI / 180), e.scale(t.flipH ? -1 : 1, t.flipV ? -1 : 1), e.translate(-i / 2, -a / 2)) : e.translate(n, r), t.geom.type === "custom") {
		let n = Ss(e, t, i, a, o, s), r = t.geom.paths.filter((e) => e.w > 0 && e.h > 0), c = Ps(t), l = c && (ds(c.headEnd) || ds(c.tailEnd)) ? fs(r, i, a) : null, u = l?.start && c?.headEnd ? ee(c.headEnd, c, 1 / K, ge) : 0, d = l?.end && c?.tailEnd ? ee(c.tailEnd, c, 1 / K, ge) : 0;
		r.forEach((s, c) => {
			if (e.beginPath(), cs(e, s, 0, 0, i, a), s.fill !== "none" && Ms(e, t, i, a, o, n)) {
				let t = A(s.fill);
				t && (e.fillStyle = t, e.fill());
			}
			if (s.stroke === !1) return;
			let l = c === 0 ? u : 0, f = c === r.length - 1 ? d : 0;
			(l > 0 || f > 0) && (e.beginPath(), te(e, (e) => cs(e, s, 0, 0, i, a), l, f)), Fs(e, t, i, a, o);
		}), l && c && ne(e, l, c, 1 / K, ge, {
			x: 0,
			y: 0,
			w: i,
			h: a
		}, t.rot, q * o, {
			hostFrame: !0,
			patternCoordinateTransform: xs(t, i, a)
		});
	} else if (t.geom.type === "preset") {
		let n = Ss(e, t, i, a, o, s), r = t.strokeColor && t.strokeWidth > 0 ? () => Fs(e, t, i, a, o) : null, c = Ps(t), l = t.geom.name.toLowerCase(), u = F(l, c, 1 / K, ge), d = u?.decorated ? u : null, f = d?.restroke != null, p = t.fill?.fillType === "hatch" || t.fill?.fillType === "image" && (t.fill.shift || t.fill.alpha !== void 0) ? (e) => Ms(e, t, i, a, o, n) : void 0, m = t.geom.adj ?? [], h = G(e, t.geom.name, 0, 0, i, a, m, n, r, () => {}, f || p ? {
			...f ? { skipTrailingStroke: !0 } : {},
			...p ? { paintFill: p } : {}
		} : void 0);
		if (h && d && c) {
			let n = j(l, 0, 0, i, a, m);
			n && (e.beginPath(), P(e, d, l, n, 0, 0, i, a, m) && Fs(e, t, i, a, o), ne(e, n, c, 1 / K, ge, {
				x: 0,
				y: 0,
				w: i,
				h: a
			}, t.rot, q * o, {
				hostFrame: !0,
				patternCoordinateTransform: xs(t, i, a)
			}));
		}
		h || (e.beginPath(), e.rect(0, 0, i, a), Ms(e, t, i, a, o, n), Fs(e, t, i, a, o));
	} else if (t.geom.type === "image") {
		let n = t.geom, r = l ? ji(l, t) : void 0, o = Oi(n.imagePath, Mi(n, r), r), c = s?.get(o), u = Si(s, o, "tiff");
		if (c || u) {
			let t = n.alpha, r = () => {
				c ? me(e, c, n.srcRect, 0, 0, i, a) : we(e, "tiff", {
					x: 0,
					y: 0,
					width: i,
					height: a
				});
			};
			t != null && t < 1 ? (e.save(), e.globalAlpha = t, r(), e.restore()) : r();
		}
	}
	t.text && ((t.text.vert === "wordArtVert" || t.text.vert === "wordArtVertRtl") && (t.flipH || t.flipV) ? (e.save(), e.translate(i / 2, a / 2), e.scale(t.flipH ? -1 : 1, t.flipV ? -1 : 1), t.flipV && e.rotate(Math.PI), e.translate(-i / 2, -a / 2), bs(e, t.text, i, a, o, c), e.restore()) : bs(e, t.text, i, a, o, c)), e.restore();
}
var ms = /* @__PURE__ */ new WeakMap();
function hs(e) {
	let t = [];
	for (let n of e.shapeGroups ?? []) for (let e of n.shapes) for (let n of e.text?.paragraphs ?? []) for (let e of n.runs) e.type === "math" && t.push({
		nodes: e.nodes,
		display: e.display
	});
	return t;
}
function gs(e) {
	for (let t of e.shapeGroups ?? []) for (let e of t.shapes) for (let t of e.text?.paragraphs ?? []) for (let e of t.runs) if (e.type === "math" && !ms.has(e.nodes)) return !0;
	return !1;
}
async function _s(e, t) {
	let n = hs(e).filter((e) => !ms.has(e.nodes));
	if (n.length !== 0) {
		await t.loadMathJax();
		for (let e of n) if (!ms.has(e.nodes)) try {
			let n = await t.mathMLToSvg(U(e.nodes, e.display)), r = await ce(n, "#000000");
			ms.set(e.nodes, {
				raster: r,
				widthEm: n.widthEm,
				ascentEm: n.ascentEm,
				descentEm: n.descentEm,
				tinted: /* @__PURE__ */ new Map()
			});
		} catch {}
	}
}
function vs(e, t, n) {
	let r = !1, i = t.paragraphs.map((t) => {
		let i;
		return t.runs.forEach((r, a) => {
			let o = r.type === "text" ? ys(e, r, n) : void 0;
			if (!o) {
				i?.push(r);
				return;
			}
			i ??= t.runs.slice(0, a), i.push(...o);
		}), i ? (r = !0, {
			...t,
			runs: i
		}) : t;
	});
	return r ? {
		...t,
		paragraphs: i
	} : t;
}
function ys(e, t, n) {
	if (!t.text) return;
	let r = k(t.fontFace), i = t.fontFaceSym?.trim() || void 0;
	if (!r && !(i && /[\uF020-\uF0FF]/u.test(t.text))) return;
	let a = (e) => {
		let n = e.codePointAt(0) ?? 0;
		return n >= 61472 && n <= 61695 && i ? i : t.fontFace;
	}, o = [], s = "", c, l = () => {
		if (!s) return;
		let r = {
			...t,
			text: s,
			fontFace: c,
			symbolSource: t
		}, i = sn(ta(e), s, c, n(r), () => n({
			...r,
			size: 24,
			symbolUnicode: !0
		}));
		for (let e of i.segments) {
			let t = i.paint(e.authored);
			o.push(e.unicode ? {
				...r,
				text: t,
				symbolUnicode: !0
			} : {
				...r,
				text: t
			});
		}
	};
	for (let e of t.text) {
		let t = s && /^[\p{M}\u200C\u200D]$/u.test(e) ? c : a(e);
		s && t !== c && (l(), s = ""), c = t, s += e;
	}
	return l(), o.length === 1 && o[0].text === t.text && !o[0].symbolUnicode && o[0].fontFace === t.fontFace ? void 0 : o;
}
function bs(t, n, r, i, a, o) {
	if (r <= 0 || i <= 0 || n.paragraphs.length === 0) return;
	let s = Fe(r, i, {
		lIns: n.lIns,
		rIns: n.rIns,
		tIns: n.tIns,
		bIns: n.bIns
	}, a / K), c = s.left, l = s.width, u = s.height;
	if (l <= 0 || u <= 0) return;
	let d = (e, n = 1) => {
		let r = (e.size > 0 ? e.size : fa) * q * a * n, i = e.symbolUnicode ? ia(t, Fa) : ia(t, da(e.fontFace, o, e.text, oa(t, e.fontFace, e.bold, e.italic), ra(t), void 0, na(t, e.fontFace)));
		return {
			font: `${e.italic ? "italic " : ""}${e.bold ? "bold " : ""}${r}px ${i}`,
			px: r
		};
	};
	if (n = vs(t, n, (e) => d(e).font), n.vert === "wordArtVert" || n.vert === "wordArtVertRtl") {
		let e = n.autoFit === "norm" ? n.fontScale ?? 1 : 1;
		if (e === 0) return;
		At(t, n, n.vert, s, q * a, (t, n) => {
			let r = v(n.codePointAt(0) ?? 0) ? t.fontFaceEa ?? t.fontFace : t.fontFace;
			return {
				...d({
					...t,
					text: n,
					fontFace: r
				}, e),
				face: r
			};
		}, (n, r) => {
			let i = ms.get(n.nodes);
			if (!i) return;
			let o = (n.fontSize ?? r) * q * a * e, s = i.widthEm * o, c = (i.ascentEm + i.descentEm) * o;
			return {
				width: s,
				height: c,
				draw: (e, r) => {
					s > 0 && c > 0 && t.drawImage(V(i, n.color ?? "#000000"), e, r, s, c);
				}
			};
		});
		return;
	}
	let f = /* @__PURE__ */ new Map(), p = !n.paragraphs.some((e) => e.runs.some((e) => e.type === "math")), m = Ri.get(t), h = yt(t);
	for (let t of n.paragraphs) for (let n of t.runs) {
		if (!p) break;
		if (n.type !== "text") continue;
		let t = n.symbolSource ?? n, r = t.fontFace ? wt(t, m ? e(m, ht(t)) : void 0, h) : void 0;
		r ? f.set(n, r) : p = !1;
	}
	n.paragraphs.some((e) => e.runs.some((e) => e.type === "text")) || (p = !1);
	let g = (e, n) => {
		let r = t.font;
		t.font = e;
		let i = t.measureText("M").actualBoundingBoxAscent;
		return t.font = r, i > 0 ? i : n * .85;
	}, _ = n.wrap !== "none", y = [], b = [], x;
	for (let e of n.paragraphs) {
		let r = e.align || "l", i = (e.marL ?? 0) / K * a, o = (e.marR ?? 0) / K * a, s = Math.max(0, (e.indent ?? 0) / K * a), c = Math.max(0, l - i - o), u = [], m = 0;
		for (let t of e.runs) {
			if (t.type === "break") {
				u.push({ type: "break" });
				continue;
			}
			if (t.type === "math") {
				let e = ms.get(t.nodes);
				if (!e) continue;
				let n = (t.fontSize ?? (m || fa)) * q * a, r = e.ascentEm * n, i = e.descentEm * n, o = {
					kind: "math",
					font: "",
					color: t.color ?? "#000000",
					pxSize: n,
					render: e,
					ascent: r,
					descent: i,
					display: t.display === !0
				};
				u.push({
					type: "object",
					width: e.widthEm * n,
					style: o,
					payload: o,
					display: t.display
				});
				continue;
			}
			m = t.size > 0 ? t.size : fa;
			let { font: e, px: n } = d(t);
			u.push({
				type: "text",
				text: t.text,
				style: {
					kind: "text",
					font: e,
					color: t.color ?? "#000000",
					pxSize: n,
					face: t.fontFace,
					ratios: p ? f.get(t) : void 0
				}
			});
		}
		let h = Pe(u, {
			maxWidth: _ ? c : Infinity,
			firstLineIndent: s,
			measureText(e, n) {
				return t.font = n.font, t.measureText(e).width;
			},
			sameStyle: (e, t) => e.kind === t.kind && e.font === t.font && e.color === t.color && e.pxSize === t.pxSize,
			tabStops: e.tabStops?.map((e) => ({
				pos: e.pos / K * a,
				algn: e.algn
			})),
			defaultTabSize: (e.defTabSz ?? 914400) / K * a,
			tabStartPen: (e) => i + (e === 0 ? s : 0)
		}), v = [], S = !1;
		for (let e of u) {
			if (e.type === "break") {
				S = !1;
				continue;
			}
			if (e.type === "object") {
				e.display ? (v.push(!S), S = !1) : S = !0;
				continue;
			}
			if (e.text === "") {
				S = !0;
				continue;
			}
			e.text.split("\n").forEach((e, t) => {
				t > 0 && (S = !1), e.replace(/\r/gu, "") !== "" && (S = !0);
			});
		}
		let C = 0, w = /* @__PURE__ */ new Map();
		u.forEach((e, t) => {
			e.type === "text" && w.set(e.style, t);
		});
		let T, E = -1, D = (e) => {
			let t = w.get(e) ?? -1;
			t >= E && (T = e, E = t);
		}, O = () => {
			let e = T?.pxSize ?? fa * 1.3333333333333333 * a, n = T?.face;
			return T?.ratios ? {
				height: e * (T.ratios.ascentRatio + T.ratios.descentRatio),
				ascent: e * T.ratios.ascentRatio
			} : {
				height: e * 1.2,
				ascent: g(`${e}px ${ia(t, da(n, void 0, "", oa(t, n), ra(t), void 0, na(t, n)))}`, e)
			};
		}, k = n.autoFit === "norm" ? n.lnSpcReduction ?? 0 : 0, A = pt(e.spaceLine), j = (e) => Ne(e, A, q * a, k), M = (e, t) => {
			let n = Le({
				ascent: e,
				descent: t
			}, A, q * a, k);
			return {
				height: n.ascent + n.descent,
				ascent: n.ascent
			};
		}, N = y.length;
		for (let [e, t] of h.entries()) {
			let n = [], a = 0, o = 0, l = 0, d = 0, f = !1, m = !1;
			for (let e of t.segments) {
				if (e.type === "tab") {
					n.push({
						kind: "tab",
						w: e.width
					});
					continue;
				}
				if (e.type === "object") {
					let t = e.style;
					if (!t.render) continue;
					let r = t.ascent ?? 0, i = t.descent ?? 0;
					n.push({
						kind: "math",
						render: t.render,
						color: t.color,
						w: e.width,
						ascent: r,
						descent: i
					}), a = Math.max(a, r + i), o = Math.max(o, r), f = !0, t.display && (m = !0);
					continue;
				}
				let t = e.style;
				n.push({
					kind: "text",
					text: e.text,
					font: t.font,
					color: t.color,
					w: e.width
				}), a = Math.max(a, t.pxSize * 1.2), o = Math.max(o, g(t.font, t.pxSize)), t.ratios && (l = Math.max(l, t.pxSize * t.ratios.ascentRatio), d = Math.max(d, t.pxSize * t.ratios.descentRatio)), D(t);
			}
			if (m && v[C++]) {
				let e = O();
				y.push({
					segs: [],
					align: r,
					height: j(e.height),
					ascent: e.ascent,
					hasMath: !1,
					leftInset: i,
					availW: c,
					gapBefore: 0
				}), b.push(e.height);
			}
			for (let e of t.hiddenRuns ?? []) {
				let t = u[e];
				t.type === "text" && (a = Math.max(a, t.style.pxSize * 1.2), o = Math.max(o, g(t.style.font, t.style.pxSize)), t.style.ratios && (l = Math.max(l, t.style.pxSize * t.style.ratios.ascentRatio), d = Math.max(d, t.style.pxSize * t.style.ratios.descentRatio)), D(t.style));
			}
			let h;
			if (p) {
				if (l + d === 0) {
					let e = O();
					l = e.ascent, d = e.height - e.ascent;
				}
				a = l + d, {height: h, ascent: o} = M(l, d);
			} else a === 0 && ({height: a, ascent: o} = O()), h = j(a);
			let _ = m;
			y.push({
				segs: n,
				align: r,
				height: h,
				ascent: o,
				hasMath: f,
				leftInset: _ ? i : i + (e === 0 ? s : 0),
				availW: _ ? c : c - (e === 0 ? s : 0),
				gapBefore: 0
			}), b.push(a);
		}
		y.length > N && (x && N > 0 && (y[N].gapBefore = Be(pt(x.spaceAfter), x.lastNaturalHeight, q * a) + Be(pt(e.spaceBefore), b[N], q * a)), x = {
			spaceAfter: e.spaceAfter,
			lastNaturalHeight: b[y.length - 1]
		});
	}
	let S = (e) => Number(/(\d+(?:\.\d+)?)px/u.exec(e)?.[1] ?? 0), C = (e) => {
		let n = t.font, r = t.textBaseline;
		t.font = e.font, t.textBaseline = "alphabetic";
		let i = t.measureText(e.text).actualBoundingBoxAscent;
		t.textBaseline = "middle";
		let a = t.measureText(e.text).actualBoundingBoxAscent;
		t.font = n, t.textBaseline = r;
		let o = i - a;
		return Number.isFinite(o) ? o : 0;
	}, w = y.reduce((e, t) => e + t.gapBefore + t.height, 0), T = Me(n.anchor, s, w);
	for (let e of y) {
		T += e.gapBefore;
		let n = e.segs.reduce((e, t) => e + t.w, 0), r = c + e.leftInset, i = We(e.align, r, e.availW, n), a = e.segs.map((e) => ({
			type: "object",
			style: e,
			width: e.w
		}));
		if (e.hasMath) {
			t.textBaseline = "alphabetic";
			let n = T + e.ascent;
			ut(a, i, n, (e, r) => {
				let i = e.style;
				if (i.kind === "text") t.font = i.font, t.fillStyle = i.color, t.fillText(i.text, r, n);
				else if (i.kind === "math") {
					let e = V(i.render, i.color);
					t.drawImage(e, r, n - i.ascent, i.w, i.ascent + i.descent);
				}
			});
		} else if (p) {
			t.textBaseline = "alphabetic";
			let n = T + e.ascent;
			ut(a, i, n, (e, r) => {
				let i = e.style;
				i.kind === "text" && (t.font = i.font, t.fillStyle = i.color, t.fillText(i.text, r, n));
			});
		} else {
			let n = T + e.height / 2, r = e.segs.filter((e) => e.kind === "text"), o = r.reduce((e, t) => !e || S(t.font) > S(e.font) ? t : e, void 0), s = o && r.some((e) => e.font !== o.font) ? n + C(o) : void 0;
			t.textBaseline = s === void 0 ? "middle" : "alphabetic";
			let c = s ?? n;
			ut(a, i, c, (e, n) => {
				let r = e.style;
				r.kind === "text" && (t.font = r.font, t.fillStyle = r.color, t.fillText(r.text, n, c));
			});
		}
		T += e.height;
	}
}
function xs(e, t, n) {
	if (e.rot === 0 && !e.flipH && !e.flipV) return;
	let r = e.rot * Math.PI / 180, i = Math.cos(r), a = Math.sin(r), o = e.flipH ? -1 : 1, s = e.flipV ? -1 : 1, c = o * i, l = -s * a, u = o * a, d = s * i, f = t / 2, p = n / 2;
	return {
		a: c,
		b: l,
		c: u,
		d,
		e: f - c * f - u * p,
		f: p - l * f - d * p
	};
}
function Ss(e, t, n, r, i, a) {
	return t.fill?.fillType === "hatch" ? null : t.fill?.fillType === "image" ? As(e, t.fill, n, r, i, a) : xe(t.fill ?? (t.fillColor ? {
		fillType: "solid",
		color: t.fillColor
	} : null), e, 0, 0, n, r, t.rot, q * i, xs(t, n, r), (e, n, r, i, a) => ls(e, t, n, r, i, a));
}
var Cs = 2, ws = 16384;
function Ts(e, t, n) {
	let r = [
		Math.min(0, t),
		Math.min(0, n),
		Math.max(0, t),
		Math.max(0, n)
	], i = typeof e.getTransform == "function" ? e.getTransform() : null, a = e.canvas;
	if (!i || !a?.width || !a.height) return {
		box: r,
		unit: 1
	};
	let { a: o, b: s, c, d: l, e: u, f: d } = i, f = o * l - s * c, p = Math.sqrt(Math.abs(f));
	if (!Number.isFinite(p) || p === 0) return {
		box: r,
		unit: 1
	};
	let m = [
		[0, 0],
		[a.width, 0],
		[0, a.height],
		[a.width, a.height]
	].map(([e, t]) => ({
		x: (l * (e - u) - c * (t - d)) / f,
		y: (o * (t - d) - s * (e - u)) / f
	})), h = m.map((e) => e.x), g = m.map((e) => e.y);
	return {
		box: [
			Math.max(r[0], Math.min(...h)),
			Math.max(r[1], Math.min(...g)),
			Math.min(r[2], Math.max(...h)),
			Math.min(r[3], Math.max(...g))
		],
		unit: p
	};
}
function Es(e, t, n, r, i) {
	t.background && (e.fillStyle = t.background, e.fill());
	let { box: [a, o, s, c], unit: l } = Ts(e, n, r);
	if (!(s > a && c > o)) return !0;
	let u = t.distancePt * q * i, d = Math.hypot(s - a, c - o), f = Math.max(Number.isFinite(u) && u > 0 ? u : 0, Cs / l, d / ws), p = -t.angle * Math.PI / 180, m = [p];
	t.lines >= 2 && m.push(p + Math.PI / 2), t.lines >= 3 && m.push(p - Math.PI / 4);
	let h = [
		[a, o],
		[s, o],
		[a, c],
		[s, c]
	], g = Math.max(1, i);
	e.save(), e.clip(), e.fillStyle = t.color;
	for (let t of m) {
		let n = Math.cos(t), r = Math.sin(t), i = h.map(([e, t]) => e * n + t * r), a = h.map(([e, t]) => -e * r + t * n), o = Math.min(...i), s = Math.max(...i), c = Math.ceil(Math.min(...a) / f), l = Math.floor(Math.max(...a) / f);
		e.save(), e.rotate(t);
		for (let t = c; t <= l; t++) e.fillRect(o, t * f - g / 2, s - o, g);
		e.restore();
	}
	return e.restore(), !0;
}
function Ds(e, t, n, r, a, o) {
	let s = typeof e.getTransform == "function" ? e.getTransform() : null;
	if (!s || typeof e.drawImage != "function") return !1;
	let { box: [c, l, u, d] } = Ts(e, n, r);
	if (!(u > c && d > l)) return !0;
	let { a: f, b: p, c: m, d: h, e: g, f: _ } = s, v = [
		[c, l],
		[u, l],
		[c, d],
		[u, d]
	].map(([e, t]) => [f * e + m * t + g, p * e + h * t + _]), y = Math.floor(Math.min(...v.map((e) => e[0]))), b = Math.floor(Math.min(...v.map((e) => e[1]))), x = Math.ceil(Math.max(...v.map((e) => e[0]))) - y, S = Math.ceil(Math.max(...v.map((e) => e[1]))) - b;
	if (![
		y,
		b,
		x,
		S
	].every(Number.isFinite)) return !1;
	if (!(x > 0 && S > 0)) return !0;
	let C = i(x, S), w = C?.getContext("2d");
	return !C || !w ? !1 : (w.setTransform(f, p, m, h, g - y, _ - b), w.beginPath(), w.rect(c, l, u - c, d - l), Es(w, t, n, r, a), e.save(), e.clip(), e.setTransform(1, 0, 0, 1, 0, 0), e.globalAlpha *= o, e.drawImage(C, y, b), e.restore(), !0);
}
var Os = /* @__PURE__ */ new WeakMap();
function ks(e, t, n, r, i, a) {
	if (e.layout === "stretch") return {
		tileW: r,
		tileH: i,
		x: 0,
		y: 0
	};
	let o = (e, t, n) => e === void 0 ? t * a : "pt" in e ? e.pt * q * a : e.fraction * n, s = o(e.width, t, r), c = o(e.height, n, i), l = e.layout === "tile";
	return {
		tileW: s,
		tileH: c,
		x: (r - s) * e.align[0] + (l ? e.offset[0] * s : 0),
		y: (i - c) * e.align[1] + (l ? e.offset[1] * c : 0)
	};
}
function As(e, t, n, r, i, a) {
	let o = a?.get(t.imagePath);
	if (!o) return null;
	let s = o, c = Number(s.width) || 0, l = Number(s.height) || 0;
	if (c <= 0 || l <= 0) return null;
	let { tileW: u, tileH: d, x: f, y: p } = ks(t, c, l, n, r, i);
	if (!(u > 0 && d > 0) || ![
		u,
		d,
		f,
		p
	].every(Number.isFinite)) return null;
	let m = e.createPattern(o, t.layout === "tile" ? "repeat" : "no-repeat");
	return m ? (typeof m.setTransform == "function" && m.setTransform({
		a: u / c,
		b: 0,
		c: 0,
		d: d / l,
		e: f,
		f: p
	}), Os.set(m, {
		iw: c,
		ih: l
	}), m) : null;
}
function js(e, t, n, r, i, a) {
	let o = t.shift, s = Os.get(n);
	if (!o || t.layout !== "tile" || !s || typeof n.setTransform != "function") return !1;
	let { iw: c, ih: l } = s, { tileW: u, tileH: d, x: f, y: p } = ks(t, c, l, r, i, a), { box: [m, h, g, _], unit: v } = Ts(e, r, i);
	if (!(g > m && _ > h)) return !0;
	let y = "rows" in o, b = y ? d : u;
	if (!(b * v >= 1) || !Number.isFinite(u) || !Number.isFinite(d)) return !1;
	let x = y ? p : f, [S, C] = y ? [h, _] : [m, g], w = y ? o.rows * u : o.columns * d, T = Math.floor((S - x) / b), E = Math.ceil((C - x) / b) - T;
	if (!Number.isSafeInteger(T) || !Number.isSafeInteger(E) || !Number.isFinite(w)) return !1;
	e.save(), e.clip(), e.fillStyle = n;
	for (let t = 0; t < E; t++) {
		let r = T + t, i = r % 2 == 0 ? 0 : w;
		n.setTransform({
			a: u / c,
			b: 0,
			c: 0,
			d: d / l,
			e: f + (y ? i : 0),
			f: p + (y ? 0 : i)
		}), y ? e.fillRect(m, x + r * b, g - m, b) : e.fillRect(x + r * b, h, b, _ - h);
	}
	return e.restore(), !0;
}
function Ms(e, t, n, r, i, a = Ss(e, t, n, r, i)) {
	let o = t.fill, s = (o?.fillType === "hatch" || o?.fillType === "image") && o.alpha !== void 0 && Number.isFinite(o.alpha) ? Math.min(1, Math.max(0, o.alpha)) : 1;
	if (s >= 1) return Ns(e, t, n, r, i, a);
	if (o?.fillType === "hatch" && Ds(e, o, n, r, i, s)) return !0;
	let c = e.globalAlpha;
	e.globalAlpha = c * s;
	try {
		return Ns(e, t, n, r, i, a);
	} finally {
		e.globalAlpha = c;
	}
}
function Ns(e, t, n, r, i, a) {
	return t.fill?.fillType === "hatch" ? Es(e, t.fill, n, r, i) : a ? t.fill?.fillType === "image" && t.fill.shift && typeof a == "object" && "setTransform" in a && js(e, t.fill, a, n, r, i) ? !0 : (e.fillStyle = a, e.fill(), !0) : !1;
}
function Ps(e) {
	return !e.strokeColor || e.strokeWidth <= 0 ? null : {
		color: e.strokeColor,
		width: e.strokeWidth,
		...e.strokeFill ? { fill: e.strokeFill } : {},
		...e.strokeDashStyle ? { dashStyle: e.strokeDashStyle } : {},
		...e.strokeCustomDash?.length ? { customDash: e.strokeCustomDash } : {},
		...e.strokeLineCap ? { lineCap: e.strokeLineCap } : {},
		...e.strokeLineJoin ? { lineJoin: e.strokeLineJoin } : {},
		...e.strokeMiterLimit === void 0 ? {} : { miterLimit: e.strokeMiterLimit },
		...e.strokeAlignment ? { alignment: e.strokeAlignment } : {},
		...e.strokeCmpd ? { cmpd: e.strokeCmpd } : {},
		...e.strokeHeadEnd ? { headEnd: e.strokeHeadEnd } : {},
		...e.strokeTailEnd ? { tailEnd: e.strokeTailEnd } : {}
	};
}
function Fs(e, t, n, r, i) {
	let a = Ps(t);
	if (a) {
		if (ye(e, a, 1 / K), a.fill) {
			let o = xe(a.fill, e, 0, 0, n, r, t.rot, q * i, xs(t, n, r), void 0, be(e));
			o && (e.strokeStyle = o);
		}
		e.stroke();
	}
}
function Is(e, t, n, r, i, a, o) {
	if (r === n && i === t) return e;
	let s = (e, r) => {
		if (e === t && r === n) return null;
		let i = a.get(`${e}:${r}`);
		return i ? Ya(o, i.styleIndex ?? 0).border : null;
	}, c = s(t, r), l = s(i, n), u = s(i, r), d = (e, ...t) => {
		if (e?.style) return e;
		for (let e of t) if (e?.style) return e;
		return e ?? null;
	};
	return {
		left: e.left,
		top: e.top,
		right: d(c?.right, u?.right, e.right),
		bottom: d(l?.bottom, u?.bottom, e.bottom),
		diagonalUp: e.diagonalUp ?? null,
		diagonalDown: e.diagonalDown ?? null
	};
}
function Ls(e, t) {
	if (!t) return e;
	let n = (e, t) => t && t.style ? t : e ?? null;
	return {
		left: n(e.left, t.left),
		right: n(e.right, t.right),
		top: n(e.top, t.top),
		bottom: n(e.bottom, t.bottom),
		diagonalUp: n(e.diagonalUp, t.diagonalUp),
		diagonalDown: n(e.diagonalDown, t.diagonalDown)
	};
}
function Rs(e, t, n, r, i = 1) {
	return {
		outerStart: n ? e - i : e,
		outerEnd: r ? t + i : t,
		innerStart: n ? e + i : e,
		innerEnd: r ? t - i : t
	};
}
function zs(e, t, n, r, i, a, o = 1) {
	let c = [
		{
			edge: t.top,
			x1: n,
			y1: r,
			x2: n + i,
			y2: r,
			kind: "h"
		},
		{
			edge: t.bottom,
			x1: n,
			y1: r + a,
			x2: n + i,
			y2: r + a,
			kind: "h"
		},
		{
			edge: t.left,
			x1: n,
			y1: r,
			x2: n,
			y2: r + a,
			kind: "v"
		},
		{
			edge: t.right,
			x1: n + i,
			y1: r,
			x2: n + i,
			y2: r + a,
			kind: "v"
		},
		{
			edge: t.diagonalUp,
			x1: n,
			y1: r + a,
			x2: n + i,
			y2: r,
			kind: "d"
		},
		{
			edge: t.diagonalDown,
			x1: n,
			y1: r,
			x2: n + i,
			y2: r + a,
			kind: "d"
		}
	];
	for (let { edge: l, x1: u, y1: d, x2: f, y2: p, kind: m } of c) {
		if (!l || !l.style || l.style === "none") continue;
		let c = l.color ? J(l.color) : "#000000";
		if (l.style === "double" && m === "d") {
			e.strokeStyle = c, e.lineWidth = 1, e.setLineDash([]);
			let t = f - u, n = p - d, r = Math.hypot(t, n), i = -n / r * 1, a = t / r * 1;
			e.beginPath(), e.moveTo(u + i, d + a), e.lineTo(f + i, p + a), e.moveTo(u - i, d - a), e.lineTo(f - i, p - a), e.stroke();
			continue;
		}
		if (l.style === "double" && m !== "d") {
			if (e.strokeStyle = c, e.lineWidth = 1, e.setLineDash([]), e.beginPath(), m === "h") {
				let o = d === r, s = o ? r - 1 : r + a + 1, c = o ? r + 1 : r + a - 1, l = Rs(n, n + i, !!t.left?.style && t.left.style !== "none", !!t.right?.style && t.right.style !== "none", 1);
				e.moveTo(l.outerStart, s), e.lineTo(l.outerEnd, s), e.moveTo(l.innerStart, c), e.lineTo(l.innerEnd, c);
			} else {
				let o = u === n, s = o ? n - 1 : n + i + 1, c = o ? n + 1 : n + i - 1, l = Rs(r, r + a, !!t.top?.style && t.top.style !== "none", !!t.bottom?.style && t.bottom.style !== "none", 1);
				e.moveTo(s, l.outerStart), e.lineTo(s, l.outerEnd), e.moveTo(c, l.innerStart), e.lineTo(c, l.innerEnd);
			}
			e.stroke();
			continue;
		}
		e.beginPath(), e.strokeStyle = c;
		let h = Bs(l.style);
		e.lineWidth = h;
		let g = Vs(l.style);
		e.setLineDash(g);
		let _ = m === "v" ? s(u, h, o) : 0, v = m === "h" ? s(d, h, o) : 0;
		e.moveTo(u + _, d + v), e.lineTo(f + _, p + v), e.stroke(), e.setLineDash([]);
	}
}
function Bs(e) {
	switch (e) {
		case "thick": return 3;
		case "medium":
		case "mediumDashed":
		case "mediumDashDot":
		case "mediumDashDotDot":
		case "slantDashDot": return 2;
		case "hair": return .5;
		default: return 1;
	}
}
function Vs(e) {
	return c(e);
}
function Hs(e) {
	switch (e) {
		case "double": return 13;
		case "thick": return 12;
		case "medium": return 11;
		case "mediumDashed": return 10;
		case "mediumDashDot": return 9;
		case "slantDashDot": return 8;
		case "mediumDashDotDot": return 7;
		case "thin": return 6;
		case "dashed": return 5;
		case "dashDot": return 4;
		case "dashDotDot": return 3;
		case "dotted": return 2;
		case "hair": return 1;
		default: return 0;
	}
}
function Us(e, t) {
	let n = Hs(e?.style), r = Hs(t?.style);
	return n === 0 && r === 0 ? null : n >= r ? e ?? null : t ?? null;
}
function Ws(e, t, n, r, i, a, o, s, c, l, u, d, f, p, m, h, g = t.charts, _, v, y) {
	if (d <= 0 || f <= 0) return;
	let b = is(n, o), x = as(r, a), S = ma(l, d, m, p);
	for (let t of g) {
		let a = t.fromCol + 1, o = t.fromRow + 1, g = t.toCol + 1, C = t.toRow + 1, w = is(n, a) + t.fromColOff * i / K, T = as(r, o) + t.fromRowOff * i / K, E = is(n, g) + t.toColOff * i / K, D = as(r, C) + t.toRowOff * i / K, O = E - w, k = D - T;
		if (O <= 0 || k <= 0) continue;
		let A = ma(l + (w - b) - s, O, m, p), j = u + (T - x) - c;
		A + O < S || A > S + d || j + k < u || j > u + f || (e.save(), e.beginPath(), e.rect(S, u, d, f), e.clip(), e.save(), i !== 1 && e.scale(i, i), Te(e, Oe(t.chart, De(Hi.get(e))), i === 1 ? {
			x: A,
			y: j,
			w: O,
			h: k
		} : {
			x: A / i,
			y: j / i,
			w: O / i,
			h: k / i
		}, q, 0, _, v, h ? he(h) : void 0, y), e.restore(), e.restore());
	}
}
var Gs = "600 12px \"Meiryo UI\", \"Segoe UI\", sans-serif", Ks = "11px \"Meiryo UI\", \"Segoe UI\", sans-serif", qs = "#FFFFFF", Js = "#BFBFBF", Ys = "#F2F2F2", Xs = "#404040", Zs = "#FFFFFF", Qs = "#000000", $s = "#A5A5A5", ec = "#E7E6E6", tc = "#A6A6A6", nc = "#C6C6C6";
function rc(e, t, n, r, i, a, o, s, c, l, u, d, f, p, m) {
	if (d <= 0 || f <= 0) return;
	let h = t.slicers;
	if (!h) return;
	let g = is(n, o), _ = as(r, a), v = ma(l, d, m, p);
	for (let t of h) {
		let a = t.fromCol + 1, o = t.fromRow + 1, h = t.toCol + 1, y = t.toRow + 1, b = is(n, a) + t.fromColOff * i / K, x = as(r, o) + t.fromRowOff * i / K, S = is(n, h) + t.toColOff * i / K, C = as(r, y) + t.toRowOff * i / K, w = S - b, T = C - x;
		if (w <= 0 || T <= 0) continue;
		let E = ma(l + (b - g) - s, w, m, p), D = u + (x - _) - c;
		E + w < v || E > v + d || D + T < u || D > u + f || (e.save(), e.beginPath(), e.rect(v, u, d, f), e.clip(), ic(e, t.caption, t.items, E, D, w, T, i, t.style), e.restore());
	}
}
function ic(e, t, n, r, i, a, o, s, c) {
	let l = c != null;
	e.fillStyle = c?.whole?.fillColor ?? qs, e.fillRect(r, i, a, o);
	let u = l ? c.whole?.borderColor : Js;
	u && (e.strokeStyle = u, e.lineWidth = 1, e.strokeRect(r + .5, i + .5, a - 1, o - 1));
	let d = Math.max(20 * s, 14), f = l ? c.header?.fillColor : Ys;
	f && (e.fillStyle = f, e.fillRect(r + 1, i + 1, a - 2, d)), e.fillStyle = c?.header?.fontColor ?? Xs, e.font = sc(c?.header, Gs, s, Hi.get(e), t);
	let p = oc(e, c?.header, s, t);
	e.textBaseline = "middle", e.textAlign = "left";
	let m = 6 * s;
	if (lc(e, t, r + m, i + d / 2 + 1, a - 2 * m, p), n.length === 0) return;
	let h = Math.max(1, Math.round(2 * s)), g = 4 * s, _ = r + g, v = i + d + g, y = a - 2 * g, b = o - d - 2 * g;
	if (y <= 0 || b <= 0) return;
	let x = Math.max(18 * s, 16), S = Math.max(1, Math.floor((b + h) / (x + h))), C = Math.min(n.length, S), w = Math.min(x, (b - h * (C - 1)) / C);
	if (w <= 0) return;
	e.font = cc(Ks, s, Hi.get(e)?.families);
	let T = 8 * s;
	for (let t = 0; t < C; t++) {
		let r = n[t], i = v + t * (w + h), a = r.selected, o = a ? c?.selectedItemWithData : c?.unselectedItemWithData, u = o?.fillColor ?? (a ? Zs : ec), d = l ? o?.borderColor : a ? $s : nc;
		e.fillStyle = u, l ? (ac(e, _, i, y, w, Math.min(4 * s, w / 4)), e.fill(), d && (e.strokeStyle = d, e.lineWidth = 1, e.stroke())) : (e.fillRect(_, i, y, w), d && (e.strokeStyle = d, e.lineWidth = 1, e.strokeRect(_ + .5, i + .5, y - 1, w - 1))), e.font = sc(o, Ks, s, Hi.get(e), r.name);
		let f = oc(e, o, s, r.name);
		e.fillStyle = o?.fontColor ?? (a ? Qs : tc), lc(e, r.name, _ + T, i + w / 2 + 1, y - 2 * T, f);
	}
}
function ac(e, t, n, r, i, a) {
	let o = Math.max(0, Math.min(a, r / 2, i / 2));
	e.beginPath(), e.moveTo(t + o, n), e.lineTo(t + r - o, n), e.quadraticCurveTo(t + r, n, t + r, n + o), e.lineTo(t + r, n + i - o), e.quadraticCurveTo(t + r, n + i, t + r - o, n + i), e.lineTo(t + o, n + i), e.quadraticCurveTo(t, n + i, t, n + i - o), e.lineTo(t, n + o), e.quadraticCurveTo(t, n, t + o, n), e.closePath();
}
function oc(e, t, n, r) {
	let i = e.font;
	if (!t?.fontFamily || !k(t.fontFamily)) return {
		paint: (e) => e,
		segments: [{
			authored: r,
			font: i
		}]
	};
	let a = Hi.get(e), o = sn(ta(e), r, t.fontFamily, i, () => sc({
		...t,
		fontSize: 24
	}, "", 1, a, "", !0)), s = sc(t, "", n, a, r, !0);
	return {
		paint: o.paint,
		segments: o.segments.map((e) => ({
			authored: e.authored,
			font: e.unicode ? s : i
		}))
	};
}
function sc(e, n, r, i, a, s = !1) {
	if (!e) return cc(n, r, i?.families);
	let c = Math.round((e.fontSize ?? 11) * r), l = e.fontBold ? "bold " : "";
	return s ? `${l}${c}px ${t(Fa, i?.families)}` : `${l}${c}px ${t(e.fontFamily ? `${o(e.fontFamily)}, ${la(i?.substitutions, e.fontFamily, a)}"Segoe UI", sans-serif` : "\"Meiryo UI\", \"Segoe UI\", sans-serif", i?.families)}`;
}
function cc(e, n, r) {
	return e.replace(/(\d+(?:\.\d+)?)px (.*)$/, (e, i, a) => `${Math.round(Number(i) * n)}px ${t(a, r)}`);
}
function lc(e, t, n, r, i, a = {
	paint: (e) => e,
	segments: [{
		authored: t,
		font: e.font
	}]
}) {
	if (i <= 0) return;
	let o = a.segments.map((e) => ({
		chars: [...e.authored],
		font: e.font
	})), s = (t, n) => (e.font = n, e.measureText(t).width), c = o.map((e) => a.paint(e.chars.join(""))), l = [0], u = (e) => {
		for (let t = l.length; t <= e; t++) l[t] = l[t - 1] + s(c[t - 1], o[t - 1].font);
		return l[e];
	}, d = [];
	o.reduce((e, t) => (d.push(e), e + t.chars.length), 0);
	let f = (e) => {
		let t = 0, n = o.length - 1;
		for (; t < n;) {
			let r = t + n + 1 >> 1;
			d[r] < e ? t = r : n = r - 1;
		}
		return {
			index: t,
			take: e - d[t]
		};
	}, p = (e, t, n) => (t === o[e].chars.length ? c[e] : a.paint(o[e].chars.slice(0, t).join(""))) + n, m = (e, t) => {
		let { index: n, take: r } = f(e);
		return u(n) + s(p(n, r, t), o[n].font);
	}, h = (e, t) => {
		let { index: n, take: r } = f(e);
		return [...o.slice(0, n).map((e, t) => ({
			text: c[t],
			font: e.font
		})), {
			text: p(n, r, t),
			font: o[n].font
		}];
	}, g = o.reduce((e, t) => e + t.chars.length, 0);
	if (o.length === 0 || g === 0) return;
	let _ = h(g, "");
	if (m(g, "") > i) {
		let e = g;
		for (; e > 0 && m(e, "…") > i;) e--;
		_ = e > 0 ? h(e, "…") : [];
	}
	let v = n;
	for (let t of _) e.font = t.font, e.fillText(t.text, v, r), v += e.measureText(t.text).width;
}
export { _i as A, wi as C, mi as D, hi as E, mt as F, ft as I, $r as M, Lr as N, di as O, Yr as P, Ti as S, xi as T, _s as _, ga as a, ma as b, ji as c, Oi as d, Mi as f, sa as g, Oo as h, ki as i, ei as j, vi as k, Vo as l, Uo as m, $i as n, Ho as o, es as p, aa as r, ba as s, Bo as t, Ai as u, ts as v, bi as w, gs as x, pa as y };
