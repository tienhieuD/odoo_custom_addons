import { MODEL_SOURCE_MODULE_PROTOCOL as e, assertCompanionRuntime as t } from "./internal-companion.mjs";
//#region ../core/src/internal/bundled-asset-url.ts
function n(e, t) {
	if (e.startsWith("/") && globalThis.location?.href) {
		let n;
		try {
			n = new URL("/", t);
		} catch {}
		if (!n || n.protocol === "file:") try {
			return new URL(e, globalThis.location.href).href;
		} catch {}
	}
	return new URL(e, t).href;
}
//#endregion
//#region ../../src/companion-version.ts
var r = "0.90.0", i = {
	wasmUrl: /* @__PURE__ */ new Set([
		"http:",
		"https:",
		"file:",
		"blob:",
		"data:"
	]),
	moduleUrl: /* @__PURE__ */ new Set([
		"http:",
		"https:",
		"file:",
		"blob:"
	])
}, a = {
	odt: "docx",
	odp: "pptx",
	ods: "xlsx"
}, o = {
	odt: ["application/vnd.oasis.opendocument.text", "application/vnd.oasis.opendocument.text-template"],
	odp: ["application/vnd.oasis.opendocument.presentation", "application/vnd.oasis.opendocument.presentation-template"],
	ods: ["application/vnd.oasis.opendocument.spreadsheet", "application/vnd.oasis.opendocument.spreadsheet-template"]
}, s = new TextEncoder().encode("mimetype"), c = 128;
function l(e) {
	if (e.byteLength < 30) return;
	let t = new DataView(e.buffer, e.byteOffset, e.byteLength);
	if (t.getUint32(0, !0) !== 67324752) return;
	let n = t.getUint16(6, !0), r = t.getUint16(8, !0), i = t.getUint32(18, !0), a = t.getUint32(22, !0);
	if (!d(e, 30, t.getUint16(26, !0)) || n & 9 || r !== 0 || i !== a || a === 0 || a > c) return;
	let o = 30 + s.length + t.getUint16(28, !0);
	if (e.byteLength < o + a) return;
	let l = "";
	for (let t = o; t < o + a; t++) {
		let n = e[t];
		if (n < 33 || n > 126) return;
		l += String.fromCharCode(n);
	}
	return l;
}
function u(e, t) {
	let n = l(e);
	if (n !== void 0) return t.has(n);
	let r = m(e);
	if (r === void 0) return !1;
	for (let e of t) if (e.length === r.size && _(e) === r.crc) return !0;
	return !1;
}
function d(e, t, n) {
	if (n !== s.length || e.byteLength < t + n) return !1;
	for (let r = 0; r < n; r++) if (e[t + r] !== s[r]) return !1;
	return !0;
}
var f = 1 << 18, p = Symbol("claim work exhausted");
function m(e) {
	let t = new DataView(e.buffer, e.byteOffset, e.byteLength), n = e.byteLength, r = (e) => e >= 0 && e + 4 <= n ? t.getUint32(e, !0) : -1, i = (e) => e >= 0 && e + 8 <= n ? Number(t.getBigUint64(e, !0)) : -1, a = [], o = /* @__PURE__ */ new Set();
	for (let e = n - 22; e >= Math.max(0, n - 22 - 65535); e--) {
		if (r(e) !== 101010256 || e + 22 + t.getUint16(e + 20, !0) !== n || t.getUint32(e + 4, !0) !== 0) continue;
		a.push(e);
		let i = e - 20;
		r(i) === 117853008 && r(i + 4) === 0 && r(i + 16) === 1 && o.add(i);
	}
	let s = { steps: f }, c = /* @__PURE__ */ new Map(), l = /* @__PURE__ */ new Set(), u = (e) => {
		let t = i(e + 4);
		if (r(e) !== 101075792 || t < 44 || !o.has(e + 12 + t) || r(e + 16) !== 0 || r(e + 20) !== 0) return !1;
		if (l.has(e)) return !0;
		l.add(e);
		let n = c.get(e + 12 + t);
		return n === void 0 ? c.set(e + 12 + t, [e]) : n.push(e), !0;
	}, d = !1;
	for (let e of o) {
		let t = u(i(e + 8)), n = u(e - 56);
		d ||= !t && !n;
	}
	if (d) {
		for (let e = n - 56; e >= 0; e--) if (!(e & 15) && --s.steps < 0 || t.getUint32(e, !0) === 101075792 && u(e) && --s.steps < 0) return;
	}
	try {
		for (let e of a) {
			let n = t.getUint16(e + 8, !0), r = t.getUint16(e + 10, !0), a = t.getUint32(e + 12, !0), l = t.getUint32(e + 16, !0), u = e - 20;
			if (o.has(u)) {
				let e = i(u + 8);
				for (let o of c.get(u) ?? []) {
					let c = r === 65535 ? i(o + 32) : r;
					if ((n === 65535 ? i(o + 24) : n) !== c) continue;
					let u = h(t, s, o, o - e, c, a === 4294967295 ? i(o + 40) : a, l === 4294967295 ? i(o + 48) : l);
					if (u !== !1) return u;
				}
				if (r === 65535 || a === 4294967295 || l === 4294967295) continue;
			}
			if (n !== r) continue;
			let d = h(t, s, e, e - l - a, r, a, l);
			if (d !== !1) return d;
		}
	} catch (e) {
		if (e === p) return;
		throw e;
	}
}
function h(e, t, n, r, i, a, o) {
	return r < 0 || i < 0 || a < 0 || o < 0 || r + o + a !== n ? !1 : g(e, t, r, r + o, n, i);
}
function g(e, t, n, r, i, a) {
	let o = new Uint8Array(e.buffer, e.byteOffset, e.byteLength), s = r, c;
	for (let r = 0; r < a; r++) {
		if (--t.steps < 0) throw p;
		if (s + 46 > i || e.getUint32(s, !0) !== 33639248) return !1;
		let r = e.getUint16(s + 28, !0), a = e.getUint16(s + 30, !0), l = s + 46 + r + a + e.getUint16(s + 32, !0);
		if (l > i) return !1;
		let u = e.getUint32(s + 42, !0);
		if (u !== 4294967295 && (n + u + 30 > e.byteLength || e.getUint32(n + u, !0) !== 67324752)) return !1;
		if (c === void 0 && d(o, s + 46, r)) {
			let n = e.getUint32(s + 24, !0);
			if (n === 4294967295) {
				n = -1;
				let i = s + 46 + r + a;
				for (let a = s + 46 + r; a + 4 <= i;) {
					if (--t.steps < 0) throw p;
					let r = e.getUint16(a + 2, !0);
					if (a + 4 + r > i) break;
					if (e.getUint16(a, !0) === 1 && r >= 8) {
						n = Number(e.getBigUint64(a + 4, !0));
						break;
					}
					a += 4 + r;
				}
			}
			c = {
				crc: e.getUint32(s + 16, !0),
				size: n
			};
		}
		s = l;
	}
	return s + 6 <= i && e.getUint32(s, !0) === 84233040 && (s += 6 + e.getUint16(s + 4, !0)), s === i && c;
}
function _(e) {
	let t = 4294967295;
	for (let n = 0; n < e.length; n++) {
		t ^= e.charCodeAt(n);
		for (let e = 0; e < 8; e++) t = t >>> 1 ^ 3988292384 & -(t & 1);
	}
	return (t ^ 4294967295) >>> 0;
}
function v(n, i, s) {
	t(r, "ooxml-model-source-module/v2");
	let c = `OpenDocument ${n.toUpperCase()} source`;
	if (typeof i != "object" || !i || Array.isArray(i)) throw TypeError(`${c} options must be an object`);
	for (let e of Object.keys(i)) if (e !== "wasmUrl" && e !== "moduleUrl") throw TypeError(`${c} option ${e} is unknown`);
	let l = b(i.wasmUrl ?? s.wasmUrl, "wasmUrl", c), d = b(i.moduleUrl ?? s.moduleUrl, "moduleUrl", c), f = a[n], p = new Set(o[n]), m = Object.freeze({
		protocol: e,
		target: f,
		moduleUrl: d,
		config: Object.freeze({ wasmUrl: l })
	});
	return Object.freeze({
		target: f,
		claim(e) {
			return u(e, p);
		},
		beginLoad() {
			return {
				module: m,
				release() {}
			};
		}
	});
}
function y(e, t) {
	let n, r = () => n ??= t();
	return Object.freeze({
		target: e,
		claim: (e) => r().claim(e),
		beginLoad: () => r().beginLoad()
	});
}
function b(e, t, n) {
	if (typeof e != "string" || e.length === 0 || e.trim() !== e) throw TypeError(`${n} ${t} must be a nonempty absolute URL`);
	let r;
	try {
		r = new URL(e);
	} catch {
		throw TypeError(`${n} ${t} must be a nonempty absolute URL`);
	}
	if (!i[t].has(r.protocol)) throw TypeError(`${n} ${t} protocol is unsupported`);
	return e;
}
//#endregion
export { y as n, n as r, v as t };
