import { r as e } from "./wmf-HY7sNn5s.js";
import { a as t, n } from "./substitutions-_KDT_mVq.js";
import { s as r } from "./resource-policy.generated-D_HlV2Rm.js";
import { i } from "./substitute-script-COw3MRyd.js";
import { o as a, r as o, u as s } from "./scripts-DxEAUeVI.js";
import { r as c } from "./office-fallback-O-L6rrDh.js";
import { Dr as l, Or as u, Ti as d, _i as f, ai as p, ci as m, fi as h, ii as g, li as ee, mi as te, n as _, oi as v, ri as ne, ui as re, wi as ie, xr as y, y as b } from "./document-content-DXDaB_ij.js";
import { t as x } from "./open-type-metrics-BlHDsmjh.js";
import { t as S } from "./cjk-fallback-CxqXJu32.js";
import { t as ae } from "./symbol-font-Cf7Xu0_f.js";
import { t as oe } from "./unicode-range-CD3UJT9S.js";
import { n as se, t as ce } from "./metafile-font-demand-CmEiy4lu.js";
import { t as le } from "./chart-font-sources-B96UtO2E.js";
import { t as ue } from "./scalar-demand-bzQ71V_C.js";
import { t as de } from "./chart-paint-texts-C9chlISz.js";
var C = [
	"hasc",
	"hdsc",
	"hlgp",
	"hcla",
	"hcld"
], w = (e, t) => String.fromCharCode(e.getUint8(t), e.getUint8(t + 1), e.getUint8(t + 2), e.getUint8(t + 3)), T = (e, t) => e.getInt32(t) / 65536, E = (e, t) => e.getInt16(t) / 16384;
function D(e, t, n) {
	return t >= 0 && n >= 0 && t + n <= e.length;
}
function fe(e, t) {
	if (!D(t, 0, 16)) return null;
	let n = e.getUint16(t.offset + 4), r = e.getUint16(t.offset + 8), i = e.getUint16(t.offset + 10);
	if (i < 20 || r === 0 || !D(t, n, r * i)) return null;
	let a = [];
	for (let o = 0; o < r; o++) {
		let r = t.offset + n + o * i, s = {
			tag: w(e, r),
			min: T(e, r + 4),
			default: T(e, r + 8),
			max: T(e, r + 12)
		};
		if (!(s.min <= s.default && s.default <= s.max)) return null;
		a.push(Object.freeze(s));
	}
	return a;
}
function pe(e, t, n) {
	let r = Array.from({ length: n }, () => null);
	if (!t) return r;
	if (!D(t, 0, 8) || e.getUint16(t.offset) !== 1 || e.getUint16(t.offset + 6) !== n) return null;
	let i = [], a = 8;
	for (let r = 0; r < n; r++) {
		if (!D(t, a, 2)) return null;
		let n = e.getUint16(t.offset + a);
		if (!D(t, a + 2, n * 4)) return null;
		let r = [];
		for (let i = 0; i < n; i++) {
			let n = t.offset + a + 2 + i * 4;
			r.push([E(e, n), E(e, n + 2)]);
		}
		a += 2 + n * 4, i.push(r.length >= 3 ? Object.freeze(r) : null);
	}
	return i;
}
function me(e, t, n, r) {
	if (t + 4 > n) return null;
	let i = e.getUint16(t), a = e.getUint16(t + 2);
	if (i !== r || t + 4 + a * r * 6 > n) return null;
	let o = [];
	for (let n = 0; n < a; n++) {
		let i = [];
		for (let a = 0; a < r; a++) {
			let o = t + 4 + (n * r + a) * 6;
			i.push([
				E(e, o),
				E(e, o + 2),
				E(e, o + 4)
			]);
		}
		o.push(Object.freeze({ axes: Object.freeze(i) }));
	}
	return o;
}
function O(e, t, n, r) {
	if (t + 6 > n) return null;
	let i = e.getUint16(t), a = e.getUint16(t + 2), o = (a & 32768) != 0, s = a & 32767, c = e.getUint16(t + 4);
	if (s > c || r >= i) return null;
	let l = t + 6, u = o ? s * 4 + (c - s) * 2 : s * 2 + (c - s), d = l + c * 2;
	if (d + i * u > n) return null;
	let f = [], p = [], m = d + r * u;
	for (let t = 0; t < c; t++) f.push(e.getUint16(l + t * 2)), t < s ? (p.push(o ? e.getInt32(m) : e.getInt16(m)), m += o ? 4 : 2) : (p.push(o ? e.getInt16(m) : e.getInt8(m)), m += o ? 2 : 1);
	return {
		regions: Object.freeze(f),
		deltas: Object.freeze(p)
	};
}
function k(e, t, n) {
	let r = t.get(n("fvar"));
	if (!r) return null;
	let i = fe(e, r);
	if (!i) return null;
	let a = pe(e, t.get(n("avar")), i.length);
	if (!a) return null;
	let o = t.get(n("MVAR")), s = /* @__PURE__ */ new Map(), c = [];
	if (o) {
		if (!D(o, 0, 12) || e.getUint16(o.offset) !== 1) return null;
		let t = e.getUint16(o.offset + 6), n = e.getUint16(o.offset + 8), r = e.getUint16(o.offset + 10);
		if (n > 0) {
			if (t < 8 || !D(o, 12, n * t) || !r) return null;
			let a = o.offset + o.length, l = o.offset + r;
			if (l + 8 > a || e.getUint16(l) !== 1) return null;
			let u = l + e.getUint32(l + 2), d = e.getUint16(l + 6);
			if (l + 8 + d * 4 > a) return null;
			let f = me(e, u, a, i.length);
			if (!f) return null;
			c = f;
			for (let r = 0; r < n; r++) {
				let n = o.offset + 12 + r * t, i = w(e, n);
				if (!C.includes(i)) continue;
				let u = e.getUint16(n + 4), f = e.getUint16(n + 6);
				if (u === 65535 && f === 65535) continue;
				if (u >= d) return null;
				let p = O(e, l + e.getUint32(l + 8 + u * 4), a, f);
				if (!p || p.regions.some((e) => e >= c.length)) return null;
				s.set(i, p);
			}
		}
	}
	return Object.freeze({
		axes: Object.freeze(i),
		avar: Object.freeze(a),
		regions: Object.freeze(c),
		metrics: s
	});
}
function A(e, t, n) {
	let r = Math.min(e.max, Math.max(e.min, n)), i = r < e.default ? e.default === e.min ? 0 : (r - e.default) / (e.default - e.min) : r > e.default ? e.max === e.default ? 0 : (r - e.default) / (e.max - e.default) : 0;
	if (t) for (let e = 1; e < t.length; e++) {
		let [n, r] = t[e - 1], [a, o] = t[e];
		if (i <= a) {
			i = a === n ? r : r + (o - r) * (i - n) / (a - n);
			break;
		}
	}
	return i;
}
function j(e, t) {
	let n = 1;
	return e.axes.forEach(([e, r, i], a) => {
		let o = t[a] ?? 0;
		if (!(e > r || r > i || e < 0 && i > 0 && r !== 0 || r === 0 || o === r)) {
			if (o <= e || o >= i) {
				n = 0;
				return;
			}
			n *= o < r ? (o - e) / (r - e) : (i - o) / (i - r);
		}
	}), n;
}
function M(e, t) {
	return e.axes.map((n, r) => {
		let i = Object.prototype.hasOwnProperty.call(t, n.tag) ? t[n.tag] : n.default;
		return A(n, e.avar[r] ?? null, i);
	});
}
function N(e, t, n = C) {
	let r = e.axes.findIndex((e) => e.tag === t);
	if (r < 0) return !1;
	for (let t of n) {
		let n = e.metrics.get(t);
		if (!n) continue;
		let { regions: i, deltas: a } = n;
		if (i.some((t, n) => a[n] !== 0 && e.regions[t].axes[r][1] !== 0)) return !0;
	}
	return !1;
}
function P(e, t, n) {
	let r = e.metrics.get(t);
	if (!r) return 0;
	let i = 0;
	return r.regions.forEach((t, a) => {
		i += r.deltas[a] * j(e.regions[t], n);
	}), i;
}
function F(e, t) {
	return x(e, t, { variations: k });
}
function I(e, t, n) {
	let r = e.variation;
	if (!r) return e;
	if (N(r, "opsz", n)) return null;
	let i = M(r, t), a = (e) => P(r, e, i), { variation: o, ...s } = e;
	return Object.freeze({
		...s,
		...e.winAscent === void 0 ? {} : {
			winAscent: e.winAscent + a("hcla"),
			winDescent: (e.winDescent ?? 0) + a("hcld")
		},
		...e.typoAscent === void 0 ? {} : {
			typoAscent: e.typoAscent + a("hasc"),
			typoDescent: (e.typoDescent ?? 0) + a("hdsc"),
			typoLineGap: (e.typoLineGap ?? 0) + a("hlgp")
		}
	});
}
var L = r * 4, R = [
	"head",
	"hhea",
	"OS/2",
	"cmap",
	"fvar",
	"avar",
	"MVAR"
], z = 2001684038, he = 2001684018, ge = new Set([
	65536,
	1330926671,
	1953658213
]), _e = /* @__PURE__ */ "cmap.head.hhea.hmtx.maxp.name.OS/2.post.cvt .fpgm.glyf.loca.prep.CFF .VORG.EBDT.EBLC.gasp.hdmx.kern.LTSH.PCLT.VDMX.vhea.vmtx.BASE.GDEF.GPOS.GSUB.EBSC.JSTF.MATH.CBDT.CBLC.COLR.CPAL.SVG .sbix.acnt.avar.bdat.bloc.bsln.cvar.fdsc.feat.fmtx.fvar.gvar.hsty.just.lcar.mort.morx.opbd.prop.trak.Zapf.Silf.Glat.Gloc.Feat.Sill".split("."), B = (e, t) => String.fromCharCode(e.getUint8(t), e.getUint8(t + 1), e.getUint8(t + 2), e.getUint8(t + 3));
function ve() {
	try {
		return typeof DecompressionStream == "function" ? (new DecompressionStream("brotli"), !0) : !1;
	} catch {
		return !1;
	}
}
async function V(e, t, n, r, i = Infinity) {
	let a;
	try {
		let n = new DecompressionStream(e);
		a = new Blob([t]).stream().pipeThrough(n);
	} catch {
		return null;
	}
	let o = a.getReader(), s = 0;
	try {
		for (;;) {
			let { done: e, value: t } = await o.read();
			if (e) break;
			if (t) {
				if (s + t.byteLength > r) return await o.cancel().catch(() => void 0), null;
				if (n(s, t), s += t.byteLength, s >= i) {
					await o.cancel().catch(() => void 0);
					break;
				}
			}
		}
	} catch {
		return null;
	}
	return s;
}
function H(e, t, n) {
	let r = Math.max(e.start, t), i = Math.min(e.start + e.bytes.byteLength, t + n.byteLength);
	r < i && e.bytes.set(n.subarray(r - t, i - t), r - e.start);
}
function U(e, t, n) {
	let r = [...t].sort((e, t) => e.tag < t.tag ? -1 : +(e.tag > t.tag)), i = 12 + r.length * 16, a = [];
	for (let { length: e } of r) a.push(i), i += e + 3 & -4;
	if (i > n) return null;
	let o = new Uint8Array(i), s = new DataView(o.buffer);
	s.setUint32(0, e), s.setUint16(4, r.length);
	let c = /* @__PURE__ */ new Map();
	return r.forEach(({ tag: e, length: t }, n) => {
		let r = 12 + n * 16;
		for (let t = 0; t < 4; t++) s.setUint8(r + t, e.charCodeAt(t));
		s.setUint32(r + 8, a[n]), s.setUint32(r + 12, t), c.set(e, o.subarray(a[n], a[n] + t));
	}), {
		out: o,
		slices: c
	};
}
async function ye(e, t) {
	if (t.byteLength < 44) return null;
	let n = e.getUint32(4), r = e.getUint16(12);
	if (44 + r * 20 > t.byteLength) return null;
	let i = [], a = /* @__PURE__ */ new Set();
	for (let n = 0; n < r; n++) {
		let r = 44 + n * 20, o = B(e, r);
		if (a.has(o)) return null;
		if (a.add(o), !R.includes(o)) continue;
		let s = e.getUint32(r + 4), c = e.getUint32(r + 8), l = e.getUint32(r + 12);
		if (s + c > t.byteLength || c > l) return null;
		i.push({
			tag: o,
			stored: t.subarray(s, s + c),
			length: l
		});
	}
	let o = U(n, i, L);
	if (!o) return null;
	for (let { tag: e, stored: t, length: n } of i) {
		let r = o.slices.get(e);
		if (t.byteLength === n) {
			r.set(t);
			continue;
		}
		let i = {
			start: 0,
			bytes: r
		};
		if (await V("deflate", t, (e, t) => H(i, e, t), n) !== n) return null;
	}
	return o.out;
}
function W(e, t, n) {
	let r = 0;
	for (let i = 0; i < 5; i++) {
		if (t.offset >= n) return null;
		let a = e.getUint8(t.offset++);
		if (i === 0 && a === 128 || r & 4261412864) return null;
		if (r = r << 7 | a & 127, !(a & 128)) return r >>> 0;
	}
	return null;
}
async function be(e, t) {
	if (t.byteLength < 48) return null;
	let n = e.getUint32(4);
	if (n === 1953784678) return null;
	let r = e.getUint16(12), i = e.getUint32(20), a = { offset: 48 }, o = [], s = /* @__PURE__ */ new Set(), c = 0;
	for (let n = 0; n < r; n++) {
		if (a.offset >= t.byteLength) return null;
		let n = e.getUint8(a.offset++), r;
		if ((n & 63) == 63) {
			if (a.offset + 4 > t.byteLength) return null;
			r = B(e, a.offset), a.offset += 4;
		} else if (r = _e[n & 63] ?? "", !r) return null;
		if (s.has(r)) return null;
		s.add(r);
		let i = n >> 6, l = W(e, a, t.byteLength);
		if (l === null) return null;
		let u = r === "glyf" || r === "loca" ? i !== 3 : i !== 0, d = u ? W(e, a, t.byteLength) : l;
		if (d === null) return null;
		if (R.includes(r)) {
			if (u) return null;
			o.push({
				tag: r,
				start: c,
				length: l
			});
		}
		if (c += d, c > 2 ** 53 - 1) return null;
	}
	if (a.offset + i > t.byteLength) return null;
	if (!ve()) return "unsupported";
	if (o.length === 0) return null;
	let l = o.reduce((e, t) => Math.max(e, t.start + t.length), 0), u = U(n, o, L - l);
	if (!u) return null;
	let d = o.map((e) => ({
		start: e.start,
		bytes: u.slices.get(e.tag)
	})), f = await V("brotli", t.subarray(a.offset, a.offset + i), (e, t) => {
		for (let n of d) H(n, e, t);
	}, L - u.out.byteLength, l);
	return f === null || f < l ? null : u.out;
}
async function xe(e) {
	let t = new Uint8Array(e);
	if (t.byteLength < 12) return null;
	let n = new DataView(e), r = n.getUint32(0);
	return ge.has(r) || r === 1953784678 ? t : r === z ? ye(n, t) : r === he ? be(n, t) : null;
}
async function Se(e) {
	try {
		let t = await xe(e);
		return t instanceof Uint8Array ? F(t) : null;
	} catch {
		return null;
	}
}
function Ce(e) {
	return e.useTypoMetrics ? [
		"hasc",
		"hdsc",
		"hlgp"
	] : e.hheaAscent === 0 && e.hheaDescent === 0 ? ["hcla", "hcld"] : [];
}
function G(e, t) {
	let n = [], r = 0, i = 0;
	for (; r < e.length && i < t.length;) {
		let a = Math.max(e[r][0], t[i][0]), o = Math.min(e[r][1], t[i][1]);
		a <= o && n.push(Object.freeze([a, o])), e[r][1] < t[i][1] ? r++ : i++;
	}
	return n;
}
function we(e) {
	let t = e.trim().toLowerCase().split(/\s+/), n = t.map((e) => e === "normal" ? 400 : e === "bold" ? 700 : /^\d+(?:\.\d+)?$/.test(e) && Number(e) >= 1 && Number(e) <= 1e3 ? Number(e) : void 0);
	if (t.length > 2 || n.some((e) => e === void 0)) return;
	let r = n[0], i = n[1] ?? r;
	return r <= i ? [r, i] : [i, r];
}
function Te(e) {
	let t = e.trim().toLowerCase();
	return t === "normal" || t === "italic" ? t : void 0;
}
var K = (e, [t, n]) => Math.min(n, Math.max(t, e));
function Ee(e, t, n) {
	let r = e.map((e) => ({
		face: e,
		weight: K(t, e.range),
		style: e.style
	})), i = l(r, t, n);
	return i ? r.filter((e) => e.weight === i.weight && e.style === i.style && e.face.range[0] <= i.weight && i.weight <= e.face.range[1]).map(({ face: e }) => e) : [];
}
var q = /* @__PURE__ */ new WeakMap();
function De(e, t) {
	if (q.has(e)) return q.get(e);
	let n = t.get(e.unicodeRange);
	return n === void 0 && t.set(e.unicodeRange, n = oe(e.unicodeRange)), q.set(e, n), n;
}
var J = /* @__PURE__ */ new WeakMap();
function Oe(e) {
	let t = J.get(e);
	return t || J.set(e, t = g(e)), t;
}
function ke(e, t, r = !1) {
	let i = Object.create(null), a = /* @__PURE__ */ new Map(), o = /* @__PURE__ */ new Map();
	e.faces.forEach((e, t) => {
		let r = n(e.family);
		if (!r) return;
		let i = a.get(r);
		i ? i.faces.push({
			face: e,
			index: t
		}) : a.set(r, {
			display: ne(e.family),
			faces: [{
				face: e,
				index: t
			}]
		});
	});
	for (let { display: e, faces: n } of a.values()) {
		let a = [], s = !0;
		for (let { face: e, index: t } of n) {
			let n = we(e.weight), r = Te(e.style);
			if (!n || !r || e.stretch.trim().toLowerCase() !== "normal") {
				s = !1;
				break;
			}
			a.push({
				face: e,
				index: t,
				range: n,
				style: r,
				declared: De(e, o)
			});
		}
		if (!s) continue;
		let c = m(e);
		for (let { weight: n, style: o } of te) {
			let s = Ee(a, n, o).map(({ face: i, index: a, range: s, style: c, declared: l }) => {
				if (!l) return;
				if (i.resourceMetrics && r) {
					let e = i.resourceMetrics.farEastCodePage === !0, t = I(i.resourceMetrics, {
						wght: K(n, s),
						ital: +(c === "italic")
					}, [...Ce(i.resourceMetrics), ...e ? ["hcla", "hcld"] : []]);
					return t?.unicodeRanges ? re(t, Object.freeze(G(v(l), v(t.unicodeRanges)))) : void 0;
				}
				if (i.resourceMetrics) {
					let e = I(i.resourceMetrics, {
						wght: K(n, s),
						ital: +(c === "italic")
					}, i.resourceMetrics.farEastCodePage ? ["hcla", "hcld"] : []), t = e && ee(e);
					return !e?.unicodeRanges || !t || e.farEastCodePage == null ? void 0 : {
						farEastCodePage: e.farEastCodePage,
						lineHeightRatio: t.lineHeightRatio,
						designAscentRatio: t.designAscentRatio,
						designDescentRatio: t.designDescentRatio,
						unicodeRanges: Object.freeze(G(v(l), v(e.unicodeRanges))),
						...e.hasEastAsianCmap ? { eastAsianLineHeightRatio: t.lineHeightRatio } : {}
					};
				}
				let u = t.faceLines.get(a), d = u && p(e, u.lines[f(n, o)], u);
				return d && {
					...d,
					unicodeRanges: Oe(l)
				};
			});
			s.length === 0 || s.some((e) => e === void 0) || s.forEach((t, r) => {
				i[`${c}\u0000${n}\u0000${o}\u0000${r}`] = Object.freeze({
					family: e,
					weight: n,
					style: o,
					sourceIdentity: c,
					synthesized: !1,
					...t
				});
			});
		}
	}
	return i;
}
function* Ae(e) {
	let t = [e], n = /* @__PURE__ */ new Set();
	for (; t.length > 0;) {
		let e = t.pop();
		if (typeof e != "object" || !e || n.has(e) || ArrayBuffer.isView(e)) continue;
		n.add(e);
		let r = e;
		if (r.type === "chart" && r.chart && typeof r.chart == "object") {
			yield r.chart;
			continue;
		}
		for (let e of Object.values(r)) typeof e == "object" && e && t.push(e);
	}
}
function Y(e, t, r) {
	let c = new o(a(e.majorFont) ?? a(e.minorFont) ?? r ?? null), l = /* @__PURE__ */ new Set(), u = /* @__PURE__ */ new Map(), d = /* @__PURE__ */ new Map(), f = (e) => {
		let t = d.get(e);
		return t === void 0 && d.set(e, t = n(e)), t;
	}, p = (e) => {
		let t = e?.trim(), n = t ? f(t) : "";
		t && n && !u.has(n) && u.set(n, t);
	}, m = /* @__PURE__ */ new Map();
	for (let e of t) {
		if (!e.script) continue;
		let t = n(e.for);
		m.set(t, (m.get(t) ?? /* @__PURE__ */ new Set()).add(e.script));
	}
	let h = /* @__PURE__ */ new Map(), g = (e, t) => h.set(e, (h.get(e) ?? /* @__PURE__ */ new Set()).add(t));
	for (let t of [e.majorFont, e.minorFont]) {
		let e = t?.trim();
		if (e) {
			p(e);
			for (let t of m.get(n(e)) ?? []) g(n(e), t);
		}
	}
	for (let t of _(e, "font-demand")) {
		for (let e of t.fontFamilies) {
			let n = e?.trim();
			if (!n) continue;
			p(n);
			let r = f(n);
			for (let e of m.get(r) ?? []) !h.get(r)?.has(e) && i({ script: e }, t.text, "any") && g(r, e);
		}
		let e = S(t.eastAsiaLanguage);
		if (e) for (let n of s([t.text], e, !0)) l.add(n);
		else c.addText([t.text]);
	}
	for (let t of Ae(e)) for (let e of le(t)) p(e);
	return {
		authored: [...u.values()],
		fallback: [...new Set([...c.names(), ...l])],
		substituteScripts: Object.freeze(Object.fromEntries([...u.keys()].map((e) => [e, Object.freeze([...h.get(e) ?? []].sort())])))
	};
}
function X(e, r, i, a) {
	let o = h(r), s = Y(e, o, i), c = new Set(a.installed ?? []), l = a.presenceChecked === void 0 ? void 0 : new Set(a.presenceChecked), u = new Set(Object.keys(a.routes).map((e) => e.split(":")[0])), d = (e) => {
		let t = e.trim().toLowerCase();
		return u.has(t) || c.has(t);
	}, f = s.authored.filter((e) => !d(e) && (l === void 0 || l.has(e.trim().toLowerCase()))), p = (e) => {
		let t = n(e);
		return Object.prototype.hasOwnProperty.call(s.substituteScripts, t) ? s.substituteScripts[t] : [];
	}, m = (e) => t(o, e, p(e)).length > 0, g = [...new Set(s.authored.filter((e) => d(e) && m(e)).map((e) => e.trim().toLowerCase()))].sort();
	return Object.freeze({
		families: Object.freeze(f),
		fallbackFamilies: Object.freeze([...s.fallback]),
		installedSubstituteFamilies: Object.freeze(g),
		substituteScripts: s.substituteScripts
	});
}
async function je(e, t, n, r, i = (e) => c(e)) {
	let a = new Set(Object.keys(r.routes).map((e) => e.split(":")[0])), o = new Set(r.installed ?? []), s = new Set(r.presenceChecked ?? []), l = Y(e, h(t), n).authored.filter((e) => {
		let t = e.trim().toLowerCase();
		return !a.has(t) && !o.has(t) && !s.has(t);
	});
	if (l.length > 0) {
		let e = await i(l);
		for (let t of e.installed) o.add(t);
		for (let t of e.checked) s.add(t);
	}
	return {
		...r,
		...o.size > 0 ? { installed: [...o].sort() } : {},
		presenceChecked: [...s].sort()
	};
}
var Z = new Set([
	"decimal",
	"decimalHalfWidth",
	"decimalZero",
	"upperRoman",
	"lowerRoman",
	"upperLetter",
	"lowerLetter",
	"hex",
	"numberInDash",
	"none",
	"cardinalText",
	"ordinalText",
	"ordinal"
]), Me = new Set([
	"lrTb",
	"tbRl",
	"btLr",
	"lrTbV",
	"tbRlV",
	"tbLrV",
	"tb",
	"rl",
	"lr",
	"tbV",
	"rlV",
	"lrV"
]), Ne = /\.(?:wmf|emf|wmz|emz)$/i, Pe = Object.freeze([400, 700]);
function Fe(e) {
	let t = [], n = [], r = !1, i = !1, a = e.__noteLayoutSettings;
	for (let e of [a?.footnoteNumberFormat, a?.endnoteNumberFormat]) if (e !== void 0 && !Z.has(e)) return "all";
	let o = [e], s = /* @__PURE__ */ new Set();
	for (; o.length > 0;) {
		let e = o.pop();
		if (!(typeof e != "object" || !e || s.has(e)) && (s.add(e), !(ArrayBuffer.isView(e) || e instanceof ArrayBuffer))) {
			if (!Array.isArray(e)) {
				let a = e;
				if (typeof a.textDirection == "string") {
					if (!Me.has(a.textDirection)) return "all";
					a.textDirection !== "lrTb" && !r && (r = !0, t.push(de));
				}
				if (typeof a.textVert == "string" && a.textVert !== "horz" || a.eastAsianVert === !0 || a.eastAsianCombine === !0 || (typeof a.alignment == "string" && a.alignment.endsWith("Kashida") && !i && (i = !0, t.push("ـ")), a.type === "chart")) return "all";
				if (a.type === "math") {
					n.push(typeof a.fallbackText == "string" ? a.fallbackText : u(a.nodes));
					continue;
				}
				if (a.pageNumType && typeof a.pageNumType == "object") {
					let e = a.pageNumType.fmt;
					if (typeof e == "string" && !Z.has(e)) return "all";
				}
				let o = [];
				if (typeof a.fieldType == "string" && typeof a.instruction == "string") {
					let e = d(a.instruction);
					if (e !== null && !Z.has(e)) return "all";
					if (a.fieldType === "date" || a.fieldType === "time") {
						let e = ie(a.instruction);
						e && o.push(e);
					}
				}
				let s = a.ruby;
				if (s && typeof s == "object" && typeof s.text == "string" && o.push(s.text), t.push(...o), a.allCaps === !0 || a.smallCaps === !0) for (let e of [
					a.text,
					a.fallbackText,
					...o
				]) typeof e == "string" && t.push(e.toUpperCase());
				typeof a.emphasisMark == "string" && t.push(b(a.emphasisMark));
			}
			for (let t of Object.values(e)) typeof t == "object" && t && o.push(t);
		}
	}
	return {
		texts: t,
		literal: n
	};
}
function Q(e) {
	let t = Fe(e);
	if (t === "all") return "all";
	let n = new ue({ budget: Infinity });
	if (!n.add(String.fromCodePoint(...y))) return "all";
	let r = /* @__PURE__ */ new Set();
	for (let t of _(e, "font-demand")) {
		for (let e of t.fontFamilies) ae(e) && r.add(e);
		if (!n.addSymbolText(t.text, t.fontFamilies, !0)) return "all";
	}
	if (!n.addSymbolText(String.fromCodePoint(...y), r)) return "all";
	for (let e of t.texts) if (!n.addSymbolText(e, r)) return "all";
	for (let e of t.literal) if (!n.addSymbolText(e, [], !0)) return "all";
	return n.result();
}
function $(t) {
	let n = [t], r = /* @__PURE__ */ new Set();
	for (; n.length > 0;) {
		let t = n.pop();
		if (typeof t != "object" || !t || r.has(t) || ArrayBuffer.isView(t)) continue;
		r.add(t);
		let i = t;
		if (i.type === "math" || typeof i.mimeType == "string" && e(i.mimeType) || typeof i.imagePath == "string" && Ne.test(i.imagePath)) return !0;
		for (let e of Object.values(i)) typeof e == "object" && e && n.push(e);
	}
	return !1;
}
async function Ie(e, t, n, r = {}) {
	let i = new se({
		...r,
		sources: n,
		readMetricTables: Se,
		...$(e) ? {} : { requestedWeights: Pe }
	});
	try {
		let n = await i.ensureWithScalars({
			families: t.families,
			fallbackFamilies: t.fallbackFamilies,
			substituteScripts: t.substituteScripts
		}, () => Q(e));
		return {
			session: i,
			names: Object.freeze([...t.families, ...t.fallbackFamilies]),
			loaded: n,
			lineMetrics: ke
		};
	} catch (e) {
		throw i.release(), e;
	}
}
export { Z as ASCII_NUMBER_FORMATS, je as completeDocxFontPresence, Q as docxFontDemandScalars, X as docxFontFamilyPlan, $ as docxRegistersEveryDeclaration, Ie as loadDocxFontSources, ce as metafileFontDemand };
