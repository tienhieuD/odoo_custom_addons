import { a as e, c as t, d as n, f as r, h as i, i as a, l as o, o as s, p as c, s as l, u } from "./chart-number-format-BTQAc_0Z.js";
var d = /* @__PURE__ */ new WeakMap();
function f() {
	return typeof navigator < "u" && (navigator.language || "").toLowerCase().startsWith("ja");
}
function p(e, t) {
	d.set(e, t === !0);
}
function m(e) {
	if (!e) return !1;
	let t = d.get(e);
	return t === void 0 && (t = f(), d.set(e, t)), t;
}
function h(e, t) {
	p(t, m(e));
}
function g(e, t) {
	let n = e.colStyleRanges ?? [];
	for (let e = n.length - 1; e >= 0; e--) {
		let r = n[e];
		if (t >= r.min && t <= r.max) return r.styleIndex;
	}
	return 0;
}
function _(e, t, n) {
	return t?.styleIndex ?? g(e, n);
}
function v(e, t) {
	return e.cellXfs?.[t] ?? e.cellXfs?.[0];
}
function y(e) {
	switch (e.type) {
		case "empty": return "";
		case "text": return e.text;
		case "number": return String(e.number);
		case "bool": return e.bool ? "TRUE" : "FALSE";
		case "error": return e.error;
		case "shared": return "";
	}
}
function b(e) {
	if (Array.isArray(e)) {
		let t = !0;
		for (let n = 0; n < e.length; n++) {
			let r = e[n];
			if (typeof r != "object" || !r) {
				t = !1;
				break;
			}
		}
		if (t) {
			let t = /* @__PURE__ */ new Map();
			for (let n of e) Number.isNaN(n.numFmtId) || t.has(n.numFmtId) || t.set(n.numFmtId, n);
			return t;
		}
	}
	return { get: (t) => e?.find((e) => e.numFmtId === t) };
}
function x(e, t, n, r = !1) {
	return S(e, t, n, r).text;
}
function S(e, t, n, r = !1, i) {
	let a = t.cellXfs[e.styleIndex ?? 0]?.numFmtId ?? 0, o = i ? i.get(a) : t.numFmts?.find((e) => e.numFmtId === a), s = o?.formatCode ?? null, c = n?.numFmtId ?? a, l = n ? n.formatCode : s, u = n ? n.sectionDivisors : o?.sectionDivisors;
	if (e.value.type !== "number") {
		let t = y(e.value);
		return { text: l ? w(t, l) : t };
	}
	return H(e.value.number, c, l, r, u);
}
function C(e, t) {
	let n = e?.[t];
	return n !== void 0 && Number.isFinite(n) && n > 0 ? n : 1;
}
function w(e, t) {
	let n = r(t), i = c(n);
	if (i < 0) return e;
	let a = n[i];
	if (a === "") return "";
	let o = "", s = 0;
	for (; s < a.length;) {
		let t = a[s];
		if (t === "\"") {
			for (s++; s < a.length && a[s] !== "\"";) o += a[s++];
			s < a.length && s++;
		} else if (t === "\\") s + 1 < a.length && (o += a[s + 1]), s += 2;
		else if (t === "[") {
			for (; s < a.length && a[s] !== "]";) s++;
			s < a.length && s++;
		} else t === "@" ? (o += e, s++) : t === "_" || t === "*" ? s += 2 : (o += t, s++);
	}
	return o;
}
var T = {
	15: "d-mmm-yy",
	16: "d-mmm",
	17: "mmm-yy",
	18: "h:mm AM/PM",
	19: "h:mm:ss AM/PM",
	20: "h:mm",
	21: "h:mm:ss",
	22: "m/d/yyyy h:mm",
	27: "[$-411]ge.m.d",
	28: "[$-411]ggge\"年\"m\"月\"d\"日\"",
	29: "[$-411]ggge\"年\"m\"月\"d\"日\"",
	30: "m/d/yy",
	31: "yyyy\"年\"m\"月\"d\"日\"",
	45: "mm:ss",
	46: "[h]:mm:ss",
	47: "mm:ss.0",
	50: "[$-411]ge.m.d",
	51: "[$-411]ggge\"年\"m\"月\"d\"日\"",
	52: "yyyy\"年\"m\"月\"",
	53: "m\"月\"d\"日\"",
	54: "[$-411]ggge\"年\"m\"月\"d\"日\"",
	55: "yyyy\"年\"m\"月\"",
	56: "m\"月\"d\"日\"",
	57: "[$-411]ge.m.d",
	58: "[$-411]ggge\"年\"m\"月\"d\"日\""
}, E = {
	1: "0",
	2: "0.00",
	3: "#,##0",
	4: "#,##0.00",
	9: "0%",
	10: "0.00%",
	11: "0.00E+00",
	37: "#,##0 ;(#,##0)",
	38: "#,##0 ;[Red](#,##0)",
	39: "#,##0.00;(#,##0.00)",
	40: "#,##0.00;[Red](#,##0.00)",
	48: "##0.0E+0"
}, D = 11, O = 5, k = 15;
function A(e) {
	let [t, n] = e.toExponential(k - 1).split("e");
	return {
		digits: t.replace(".", "").split("").map(Number),
		exp: Number(n)
	};
}
function j(e, t) {
	if (t < 0) return {
		digits: [],
		exp: e.exp
	};
	let n = e.digits.slice(0, t);
	if ((e.digits[t] ?? 0) < 5) return {
		digits: n,
		exp: e.exp
	};
	let r = n.length - 1;
	for (; r >= 0; r--) if (n[r] === 9) n[r] = 0;
	else {
		n[r] += 1;
		break;
	}
	return r < 0 ? {
		digits: [1],
		exp: e.exp + 1
	} : {
		digits: n,
		exp: e.exp
	};
}
function M(e, t) {
	let { digits: n, exp: r } = j(e, e.exp + 1 + t);
	if (!n.some((e) => e !== 0)) return null;
	let i = (e) => {
		let t = r - e;
		return t >= 0 && t < n.length ? n[t] : 0;
	}, a = "";
	for (let e = Math.max(r, 0); e >= 0; e--) a += i(e);
	let o = "";
	for (let e = -1; e >= -t; e--) o += i(e);
	return o = o.replace(/0+$/, ""), o ? `${a}.${o}` : a;
}
function N(e) {
	return `E${e >= 0 ? "+" : "-"}${Math.abs(e).toString().padStart(2, "0")}`;
}
function P(e, t) {
	if (e.exp >= 0) {
		let n = e.exp + 1;
		if (n > t) return null;
		for (let r = Math.max(0, t - n - 1); r >= 0; r--) {
			let n = M(e, r);
			if (n !== null && n.length <= t) return n;
		}
		return null;
	}
	let n = M(e, Math.max(0, t - 2));
	return n !== null && n.length <= t ? n : null;
}
function F(e, t) {
	for (let n = O; n >= 0; n--) {
		let { digits: r, exp: i } = j(e, n + 1), a = r.slice(1).join("").replace(/0+$/, ""), o = `${r[0]}${a ? `.${a}` : ""}${N(i)}`;
		if (o.length <= t) return o;
	}
	return null;
}
function I(e) {
	return e.split("E")[0].replace(".", "").replace(/^0+/, "").length;
}
function L(e, t) {
	let n = P(e, t), r = F(e, t);
	if (n === null || r === null) return n ?? r;
	if (e.exp >= 0) return n;
	let i = e.digits.join("").replace(/0+$/, "").length, a = I(n);
	return a >= i ? n : I(r) > a ? r : n;
}
function R(e, t) {
	if (!Number.isFinite(e)) return String(e);
	if (e === 0) return !t || t("0") ? "0" : null;
	let n = e < 0 ? "-" : "", r = A(Math.abs(e)), i = null;
	for (let e = D; e >= 1; e--) {
		let a = L(r, e);
		if (a === null || a === i) continue;
		i = a;
		let o = n + a;
		if (!t || t(o)) return o;
	}
	return null;
}
function z(e) {
	return R(e) ?? "";
}
function B(e, t, n) {
	if (e.value.type !== "number" || !t.general || n(t.text)) return t;
	let r = null, i = R(e.value.number, (e) => (r = e, n(e))) ?? r;
	return i === null ? t : t.color === void 0 ? {
		text: i,
		general: !0
	} : {
		text: i,
		color: t.color,
		general: !0
	};
}
function V(e, t, n, r = !1) {
	let i = S(e, t, n, r);
	if (e.value.type !== "number" || !i.general) return [i.text];
	let a = [];
	return R(e.value.number, (e) => (a.push(e), !1)), a.length > 0 ? a : [i.text];
}
function H(e, n, r, i = !1, o) {
	if (n === 14 && !r) return W(a(e, i), e, i);
	if (r && r.trim().toLowerCase() === "general") {
		let t = C(o, 0);
		return t === 1 ? {
			text: z(e),
			general: !0
		} : { text: z(e / t) };
	}
	if (r) return Q(e, r, i, o);
	let s = T[n];
	if (s) return W(t(e, s, i), e, i);
	let c = E[n];
	return c ? Q(e, c) : n === 49 ? { text: String(e) } : {
		text: z(e),
		general: !0
	};
}
function U(t) {
	let n = /* @__PURE__ */ new Map();
	for (let e of t.numFmts ?? []) e.formatCode !== null && e.formatCode !== void 0 && !n.has(e.numFmtId) && n.set(e.numFmtId, e.formatCode);
	let i = !0, a = /* @__PURE__ */ new Map(), o = (e) => {
		let t = a.get(e);
		if (!t) {
			let n = [e];
			for (let t of r(e)) u(t) && n.push(...l(t));
			t = Object.freeze(n), a.set(e, t);
		}
		return t;
	}, s = /* @__PURE__ */ new Map(), c = (t) => {
		let n = s.get(t);
		if (!n) {
			if (t === 14) {
				let t = e();
				t.complete || (i = !1), n = t.texts;
			} else {
				let e = T[t] ?? E[t];
				n = e ? o(e) : Object.freeze([]);
			}
			s.set(t, n);
		}
		return n;
	}, d = (t.cellXfs ?? []).map((e) => {
		let t = e.numFmtId ?? 0, r = n.get(t);
		return r ? o(r) : c(t);
	}), f = [];
	for (let e of t.dxfs ?? []) e.numFmt && f.push(...e.numFmt.formatCode ? o(e.numFmt.formatCode) : c(e.numFmt.numFmtId));
	return Object.freeze({
		cellXfs: Object.freeze(d),
		dxfs: Object.freeze(f),
		complete: i
	});
}
function W(e, t, n) {
	return e === "#" && !i(t, n) ? {
		text: e,
		fill: !0
	} : { text: e };
}
function G(e) {
	let t = [], n = "", r = "", i = !1, a = !1, o, s = !1, c = 0, l = 0, u = (e) => {
		if (!e) return;
		!a && !s && (c = n.replace(/,/g, "").length);
		let r = t[t.length - 1];
		r && r.kind === "lit" ? r.text += e : t.push({
			kind: "lit",
			text: e
		});
	}, d = 0;
	for (; d < e.length;) {
		let c = e[d];
		if (c === "\"") {
			d++;
			let t = "";
			for (; d < e.length && e[d] !== "\"";) t += e[d++];
			d < e.length && d++, u(t);
		} else if (c === "\\") d + 1 < e.length && u(e[d + 1]), d += 2;
		else if (c === "[") {
			let t = e.indexOf("]", d), n = t > d ? e.slice(d + 1, t) : "";
			if (n.startsWith("$")) {
				let e = n.slice(1), t = e.indexOf("-");
				u(t >= 0 ? e.slice(0, t) : e);
			}
			d = t < 0 ? e.length : t + 1;
		} else if (c === "_") u(" "), d += 2;
		else if (c === "*") u(e[d + 1] ?? ""), d += 2;
		else if (c === "#" || c === "0" || c === "?") a ? (r += c, t.push({
			kind: "fracph",
			ph: c
		})) : (n += c, t.push({
			kind: "intph",
			ph: c
		})), l = 0, d++;
		else if (c === ".") a = !0, t.push({ kind: "dot" }), d++;
		else if (c === ",") a || (n += ","), l++, d++;
		else if (c === "/" && n.replace(/,/g, "").length > 0) {
			s = !0, t.push({ kind: "fraction" }), d++;
			let n = "";
			for (; d < e.length && /[0-9#?]/.test(e[d]);) n += e[d++];
			t[t.length - 1].den = n;
		} else if (c === "%") i = !0, t.push({ kind: "percent" }), d++;
		else if ((c === "E" || c === "e") && (e[d + 1] === "+" || e[d + 1] === "-")) {
			let n = e[d + 1] === "+";
			d += 2;
			let r = 0;
			for (; d < e.length && (e[d] === "0" || e[d] === "#" || e[d] === "?");) r++, d++;
			o = {
				plus: n,
				width: Math.max(r, 1)
			}, t.push({ kind: "exp" });
		} else u(c), d++;
	}
	let f = l, p = /,(?=[#0?])/.test(n), m = n.replace(/,/g, ""), h;
	if (s) {
		let e = t.find((e) => e.kind === "fraction")?.den ?? "?", n = e.match(/[0-9]+/);
		h = {
			wholeSpec: m.slice(0, c),
			numSpec: m.slice(c) || "?",
			denSpec: e.replace(/[^0#?]/g, ""),
			fixedDen: n ? parseInt(n[0], 10) : null
		};
	}
	return {
		parts: t,
		intSpec: m,
		fracSpec: r,
		hasPercent: i,
		commaScale: f,
		grouping: p,
		exp: o,
		fraction: h
	};
}
function K(e) {
	return e.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}
function q(e, t, n) {
	let r = t.split(""), i = e.split(""), a = [], o = i.length - 1, s = [];
	for (let e = r.length - 1; e >= 0; e--) o >= 0 ? (a.unshift(i[o]), s.unshift(i[o]), o--) : r[e] === "0" ? (a.unshift("0"), s.unshift("0")) : r[e] === "?" && a.unshift(" ");
	for (; o >= 0;) a.unshift(i[o]), s.unshift(i[o]), o--;
	if (n) {
		let e = K(s.join(""));
		return (a.length - s.length > 0 ? a.slice(0, a.length - s.length).join("") : "") + e;
	}
	return a.join("");
}
function J(e, t) {
	let n = t.length;
	if (n === 0) return "";
	let r = e.padEnd(n, "0").slice(0, n).split("");
	for (let e = n - 1; e >= 0; e--) {
		let n = t[e] ?? "#";
		if (r[e] === "0" && n === "#") r[e] = "";
		else if (r[e] === "0" && n === "?") r[e] = " ";
		else break;
	}
	return r.join("");
}
function Y(e, t, n) {
	if (n !== null) return [Math.round(e * n), n];
	let r = 10 ** Math.max(t, 1) - 1, i = 0, a = 1, o = Math.abs(e);
	Math.abs(1 - e) < o && (i = 1, a = 1, o = Math.abs(1 - e));
	let s = [0, 1], c = [1, 1];
	for (let t = 0; t < 100; t++) {
		let t = s[0] + c[0], n = s[1] + c[1];
		if (n > r) break;
		let l = t / n, u = Math.abs(l - e);
		if (u < o && (o = u, i = t, a = n), l < e) s = [t, n];
		else if (l > e) c = [t, n];
		else break;
	}
	return [i, a];
}
function X(e, t, n) {
	let r = G(t), i = n ? Math.abs(e) : e;
	r.hasPercent && (i *= 100), r.commaScale > 0 && (i /= 1e3 ** r.commaScale);
	let a = i < 0 ? "-" : "", o = Math.abs(i);
	if (r.fraction) {
		let e = Math.floor(o), t = o - e, { wholeSpec: n, numSpec: i, denSpec: s, fixedDen: c } = r.fraction, l = n.length > 0, [u, d] = Y(t, s.length, c);
		l && u === d && (e += 1, u = 0);
		let f = (e, t) => {
			let n = String(e), r = t.includes("0") ? "0" : " ";
			for (; n.length < t.length;) n = r + n;
			return n;
		}, p = (e, t) => {
			let n = String(e), r = t.includes("0") ? "0" : " ";
			for (; n.length < t.length;) n += r;
			return n;
		}, m = a;
		if (l) {
			let t = e > 0 ? String(e) : n.includes("0") ? "0" : "";
			if (u === 0) {
				let e = c === null ? s.length || 1 : String(c).length;
				m += t + " ".repeat(1 + i.length + 1 + e);
			} else {
				let e = c === null ? p(d, s) : String(c);
				m += t + " " + f(u, i) + "/" + e;
			}
		} else {
			let t = u + e * d, n = c === null ? p(d, s) : String(c);
			m += f(t, i) + "/" + n;
		}
		return m;
	}
	if (r.exp) {
		let e = Math.max(r.intSpec.length, 1), t = r.fracSpec.length, n = 0, i = 0;
		o !== 0 && (i = Math.floor(Math.log10(o)), i = Math.floor(i / e) * e, n = o / 10 ** i, parseFloat(s(n, t)) >= 10 ** e && (i += e, n = o / 10 ** i));
		let [c, l = ""] = s(n, t).split(".");
		return a + Z(r, q(c, r.intSpec, !1), J(l, r.fracSpec), "E" + (i < 0 ? "-" : r.exp.plus ? "+" : "") + String(Math.abs(i)).padStart(r.exp.width, "0"));
	}
	let c = r.fracSpec.length, [l, u = ""] = s(o, c).split("."), d = l.replace(/^0+/, ""), f = /[0]/.test(r.intSpec) || r.intSpec === "" && !1;
	return d === "" && f && (d = "0"), a + Z(r, q(d, r.intSpec, r.grouping), J(u, r.fracSpec), "");
}
function Z(e, t, n, r) {
	let i = t.split(""), a = [];
	e.parts.forEach((e, t) => {
		e.kind === "intph" && a.push(t);
	});
	let o = n.split(""), s = [];
	e.parts.forEach((e, t) => {
		e.kind === "fracph" && s.push(t);
	});
	let c = /* @__PURE__ */ new Map(), l = i.length - 1;
	for (let e = a.length - 1; e >= 0; e--) if (e === 0) {
		let t = "";
		for (; l >= 0;) t = i[l--] + t;
		c.set(a[e], t);
	} else l >= 0 ? c.set(a[e], i[l--]) : c.set(a[e], "");
	let u = /* @__PURE__ */ new Map();
	for (let e = 0; e < s.length; e++) u.set(s[e], o[e] ?? "");
	let d = e.fracSpec.length > 0 && (n.length > 0 || /[0?]/.test(e.fracSpec)), f = "";
	for (let t = 0; t < e.parts.length; t++) {
		let n = e.parts[t];
		n.kind === "lit" ? f += n.text : n.kind === "intph" ? f += c.get(t) ?? "" : n.kind === "fracph" ? f += u.get(t) ?? "" : n.kind === "dot" ? f += d ? "." : "" : n.kind === "percent" ? f += "%" : n.kind === "exp" && (f += r);
	}
	return f;
}
function Q(e, r, i = !1, a) {
	let s = e, c = n(s, r);
	if (c === null) return {
		text: z(s),
		general: !0
	};
	if (c === "none") return { text: "#" };
	let { section: l, useMagnitude: d } = c;
	s /= C(a, c.index);
	let f = d ? Math.abs(s) : s, p = o(l.body);
	if (p) {
		let e = p.percent ? f * 100 : f, t = (e < 0 ? "-" : "") + p.prefix + z(Math.abs(e)) + p.suffix;
		return l.color ? {
			text: t,
			color: l.color
		} : { text: t };
	}
	let m = u(l.body) ? W(t(f, l.body, i), f, i) : { text: X(s, l.body, d) };
	return l.color ? {
		...m,
		color: l.color
	} : m;
}
export { b as a, _ as c, f as d, m as f, S as i, p as l, B as n, U as o, x as r, v as s, V as t, h as u };
