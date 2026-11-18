import { MODEL_SOURCE_MODULE_PROTOCOL as e, assertCompanionRuntime as t } from "./internal-companion.mjs";
//#region ../core/src/internal/bundled-asset-url.ts
function n() {
	let e = globalThis, t = e.document?.baseURI ?? e.location?.href;
	return typeof t == "string" ? t : void 0;
}
function r(e, t) {
	let r = n();
	if (e.startsWith("/") && r) {
		let n;
		try {
			n = new URL("/", t);
		} catch {}
		if (!n || n.protocol === "file:") try {
			return new URL(e, r).href;
		} catch {}
	}
	return new URL(e, t).href;
}
//#endregion
//#region ../core/src/errors/cfb-read.ts
var i = 4294967290, a = 1e6;
function o(e, t) {
	return (e + 1) * t;
}
function s(e) {
	return e >= 0 && e <= i;
}
function c(e, t, n) {
	let { sectorSize: r } = n, i = [], c = /* @__PURE__ */ new Set(), l = Math.max(0, Math.floor(t / r) - 1);
	if (n.numFatSectors > l || n.numDifatSectors > l || n.numDifatSectors > a) return null;
	let u = 0, d = (e) => u++ >= n.numFatSectors ? !s(e) : !s(e) || e >= l || c.has(e) ? !1 : (c.add(e), i.push(e), !0);
	for (let t = 0; t < 109; t++) if (!d(e.getUint32(76 + t * 4, !0))) return null;
	let f = r / 4 - 1, p = n.firstDifatSector, m = /* @__PURE__ */ new Set(), h = 0;
	for (; s(p) && h < n.numDifatSectors && (h++, !m.has(p));) {
		m.add(p);
		let n = o(p, r);
		if (n < 0 || n + r > t) return null;
		for (let t = 0; t < f; t++) if (!d(e.getUint32(n + t * 4, !0))) return null;
		p = e.getUint32(n + f * 4, !0);
	}
	return h !== n.numDifatSectors || s(p) || i.length !== n.numFatSectors ? null : i;
}
function l(e, t, n, r, i) {
	let a = n / 4, c = Math.floor(i / a), l = i % a;
	if (c >= r.length) return null;
	let u = r[c];
	if (!s(u)) return null;
	let d = o(u, n) + l * 4;
	return d < 0 || d + 4 > t ? null : e.getUint32(d, !0);
}
//#endregion
//#region ../core/src/errors/cfb-sniff.ts
var u = 4294967290, d = 128, f = 4096, p = 8192;
function m(e, t, n, r, i) {
	if (!_(r)) return null;
	let a = /* @__PURE__ */ new Set(), o = Math.floor(n / d);
	if (o < 1) return null;
	let s = /* @__PURE__ */ new Set(), c = r, u = 0, m = 0;
	for (; _(c) && !(u++ > p || s.has(c));) {
		s.add(c);
		let r = g(c, n);
		if (r < 0 || r + n > t) return null;
		for (let t = 0; t < o; t++) {
			if (m++ > f) return a;
			let n = h(e, r + t * d);
			n && a.add(n);
		}
		let u = l(e, t, n, i, c);
		if (u === null) break;
		c = u;
	}
	return a;
}
function h(e, t) {
	let n = e.getUint16(t + 64, !0);
	if (n < 2 || n > 64) return "";
	let r = n / 2 - 1, i = "";
	for (let n = 0; n < r; n++) {
		let r = e.getUint16(t + n * 2, !0);
		if (r === 0) break;
		i += String.fromCharCode(r);
	}
	return i;
}
function g(e, t) {
	return (e + 1) * t;
}
function _(e) {
	return e >= 0 && e <= u;
}
//#endregion
//#region ../core/src/source/cfb-directory-names.ts
var v = [
	208,
	207,
	17,
	224,
	161,
	177,
	26,
	225
];
function y(e) {
	if (e.length < 512) return null;
	for (let t = 0; t < v.length; t++) if (e[t] !== v[t]) return null;
	let t = new DataView(e.buffer, e.byteOffset, e.byteLength), n = t.getUint16(30, !0);
	if (n !== 9 && n !== 12) return /* @__PURE__ */ new Set();
	let r = 1 << n, i = c(t, e.length, {
		sectorSize: r,
		numFatSectors: t.getUint32(44, !0),
		firstDifatSector: t.getUint32(68, !0),
		numDifatSectors: t.getUint32(72, !0)
	});
	return i === null ? /* @__PURE__ */ new Set() : m(t, e.length, r, t.getUint32(48, !0), i) ?? /* @__PURE__ */ new Set();
}
//#endregion
//#region ../../src/companion-version.ts
var b = "0.90.1";
//#endregion
//#region src/source-module-config.ts
function x(e, t) {
	if (e !== void 0) {
		if (typeof e != "number" || !Number.isSafeInteger(e) || e <= 0) throw RangeError(`${t} maxInputBytes is invalid`);
		return e;
	}
}
//#endregion
//#region src/legacy-source.ts
var S = {
	wasmUrl: new Set([
		"http:",
		"https:",
		"file:",
		"blob:",
		"data:"
	]),
	moduleUrl: new Set([
		"http:",
		"https:",
		"file:",
		"blob:"
	])
}, C = {
	doc: "docx",
	xls: "xlsx",
	ppt: "pptx"
};
function w(e) {
	let t = [];
	return e.has("WordDocument") && t.push("doc"), (e.has("Workbook") || e.has("Book")) && t.push("xls"), e.has("PowerPoint Document") && t.push("ppt"), t.length === 1 ? t[0] : null;
}
function T(n, r, i) {
	t(b, "ooxml-model-source-module/v2");
	let a = `legacy ${n.toUpperCase()} source`;
	if (typeof r != "object" || !r) throw TypeError(`${a} options must be an object`);
	let o = D(r.wasmUrl ?? i.wasmUrl, "wasmUrl", a), s = D(r.moduleUrl ?? i.moduleUrl, "moduleUrl", a), c = x(r.maxInputBytes, a), l = C[n], u = Object.freeze({
		protocol: e,
		target: l,
		moduleUrl: s,
		config: Object.freeze({
			wasmUrl: o,
			...c === void 0 ? {} : { maxInputBytes: c }
		})
	});
	return Object.freeze({
		target: l,
		claim(e) {
			let t = y(e);
			if (!t || t.has("EncryptionInfo") || w(t) !== n) return !1;
			if (c !== void 0 && e.byteLength > c) throw RangeError(`${a} input exceeds the configured size limit`);
			return !0;
		},
		beginLoad() {
			return {
				module: u,
				release() {}
			};
		}
	});
}
function E(e, t) {
	let n, r = () => n ??= t();
	return Object.freeze({
		target: e,
		claim: (e) => r().claim(e),
		beginLoad: () => r().beginLoad()
	});
}
function D(e, t, n) {
	if (typeof e != "string" || e.length === 0 || e.trim() !== e) throw TypeError(`${n} ${t} must be a nonempty absolute URL`);
	let r;
	try {
		r = new URL(e);
	} catch {
		throw TypeError(`${n} ${t} must be a nonempty absolute URL`);
	}
	if (!S[t].has(r.protocol)) throw TypeError(`${n} ${t} protocol is unsupported`);
	return e;
}
//#endregion
export { E as n, r, T as t };
