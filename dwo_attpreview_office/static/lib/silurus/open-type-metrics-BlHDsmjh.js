var e = (e) => (e.charCodeAt(0) << 24 >>> 0 | e.charCodeAt(1) << 16 | e.charCodeAt(2) << 8 | e.charCodeAt(3)) >>> 0, t = e("ttcf"), n = e("OTTO"), r = e("true"), i = e("typ1"), a = e("head"), o = e("hhea"), s = e("OS/2"), c = e("cmap"), l = e("fvar"), u = [
	[4352, 4607],
	[11904, 12287],
	[12352, 12543],
	[12544, 12591],
	[12592, 12687],
	[12704, 12735],
	[12784, 12799],
	[13312, 19903],
	[19968, 40959],
	[40960, 42191],
	[43360, 43391],
	[44032, 55203],
	[63744, 64255],
	[131072, 205743]
];
function d(e, t, n) {
	return Number.isSafeInteger(t) && Number.isSafeInteger(n) && t >= 0 && n >= 0 && t <= e - n;
}
function f(e, t, n) {
	if (n < 16) return !1;
	let r = e.getUint16(t + 2);
	if (r < 16 || r > n) return !1;
	let i = e.getUint16(t + 6);
	if (i === 0 || i % 2 != 0) return !1;
	let a = i / 2, o = t + 14, s = o + a * 2 + 2, c = s + a * 2, l = c + a * 2;
	if (l + a * 2 > t + r) return !1;
	let d = -1;
	for (let t = 0; t < a; t++) {
		let n = e.getUint16(s + t * 2), r = e.getUint16(o + t * 2);
		if (n > r || n <= d) return !1;
		d = r;
	}
	for (let n = 0; n < a; n++) {
		let i = e.getUint16(s + n * 2), a = e.getUint16(o + n * 2), d = e.getInt16(c + n * 2), f = l + n * 2, p = e.getUint16(f);
		for (let [n, o] of u) {
			let s = Math.max(i, n), c = Math.min(a, o);
			if (!(s > c)) {
				if (p === 0) {
					if (s < c || s + d & 65535) return !0;
					continue;
				}
				for (let n = s; n <= c; n++) {
					let a = f + p + (n - i) * 2;
					if (a + 2 > t + r) break;
					let o = e.getUint16(a);
					if (o !== 0 && o + d & 65535) return !0;
				}
			}
		}
	}
	return !1;
}
function p(e, t, n, r) {
	if (n < 16) return !1;
	let i = e.getUint32(t + 4), a = e.getUint32(t + 12);
	if (i < 16 || i > n || a > (i - 16) / 12) return !1;
	let o = -1;
	for (let n = 0; n < a; n++) {
		let i = t + 16 + n * 12, a = e.getUint32(i), s = e.getUint32(i + 4), c = e.getUint32(i + 8);
		if (a > s || s > 1114111 || a <= o) return !1;
		if (o = s, a > u[u.length - 1][1]) break;
		for (let [e, t] of u) {
			let n = Math.max(a, e), i = Math.min(s, t);
			if (!(n > i)) {
				if (r) {
					if (c !== 0) return !0;
				} else if (n < i || c + (n - a) !== 0) return !0;
			}
		}
	}
	return !1;
}
function m(e, t) {
	if (!t || t.length < 4) return !1;
	let n = e.getUint16(t.offset + 2);
	if (4 + n * 8 > t.length) return !1;
	for (let r = 0; r < n; r++) {
		let n = t.offset + 4 + r * 8, i = e.getUint16(n), a = e.getUint16(n + 2);
		if (i !== 0 && !(i === 3 && (a === 1 || a === 10))) continue;
		let o = e.getUint32(n + 4);
		if (o > t.length - 2) continue;
		let s = t.offset + o, c = t.length - o, l = e.getUint16(s);
		if (l === 4 && f(e, s, c) || l === 12 && p(e, s, c, !1) || l === 13 && p(e, s, c, !0)) return !0;
	}
	return !1;
}
var h = 32768, g = 4096, _ = 8, v = 262144;
function y(e, t, n, r) {
	if (n < 16) return null;
	let i = e.getUint16(t + 2);
	if (i < 16 || i > n) return null;
	let a = e.getUint16(t + 6);
	if (a === 0 || a % 2 != 0) return null;
	let o = a / 2, s = t + 14, c = s + o * 2 + 2, l = c + o * 2, u = l + o * 2;
	if (u + o * 2 > t + i) return null;
	let d = [], f = -1, p = -1, m = (e) => {
		d.length > 0 && p + 1 === e ? (p = e, d[d.length - 1] = [f, p]) : (f = p = e, d.push([e, e]));
	}, g = -1;
	for (let n = 0; n < o; n++) {
		let a = e.getUint16(c + n * 2), o = e.getUint16(s + n * 2);
		if (a > o || a <= g) return null;
		g = o;
		let f = e.getInt16(l + n * 2), p = u + n * 2, _ = e.getUint16(p);
		for (let n = a; n <= o && n < 65535; n++) if (--r.remaining < 0 || ((_ === 0 ? n + f & 65535 : (() => {
			let r = p + _ + (n - a) * 2;
			if (r + 2 > t + i) return 0;
			let o = e.getUint16(r);
			return o === 0 ? 0 : o + f & 65535;
		})()) !== 0 && m(n), d.length > h)) return null;
	}
	return d;
}
function b(e, t, n, r, i) {
	if (n < 16) return null;
	let a = e.getUint32(t + 4), o = e.getUint32(t + 12);
	if (a < 16 || a > n || o > (a - 16) / 12 || o > h) return null;
	let s = [], c = -1;
	for (let n = 0; n < o; n++) {
		if (--i.remaining < 0) return null;
		let a = t + 16 + n * 12, o = e.getUint32(a), l = e.getUint32(a + 4), u = e.getUint32(a + 8);
		if (o > l || l > 1114111 || o <= c) return null;
		if (c = l, r) u !== 0 && s.push([o, l]);
		else {
			let e = u === 0 ? o + 1 : o;
			e <= l && s.push([e, l]);
		}
	}
	return s;
}
function x(e, t) {
	if (!t || t.length < 4) return [];
	let n = e.getUint16(t.offset + 2);
	if (n > g || 4 + n * 8 > t.length) return [];
	let r = /* @__PURE__ */ new Set(), i = [];
	for (let a = 0; a < n; a++) {
		let n = t.offset + 4 + a * 8, o = e.getUint16(n), s = e.getUint16(n + 2);
		if (o !== 0 && !(o === 3 && (s === 1 || s === 10))) continue;
		let c = e.getUint32(n + 4);
		if (c > t.length - 2) return [];
		let l = t.offset + c, u = t.length - c, d = e.getUint16(l);
		if (!(o === 0 && s === 5 && d === 14)) {
			if (d !== 4 && d !== 12 && d !== 13) return [];
			if (!r.has(c)) {
				if (r.add(c), r.size > _) return [];
				i.push({
					subtable: l,
					availableLength: u,
					format: d
				});
			}
		}
	}
	let a = { remaining: v }, o = null;
	for (let t of i) {
		let n = t.format === 4 ? y(e, t.subtable, t.availableLength, a) : b(e, t.subtable, t.availableLength, t.format === 13, a);
		if (!n?.length) return [];
		if (o === null) {
			o = n;
			continue;
		}
		let r = [], i = 0, s = 0;
		for (; i < o.length && s < n.length;) {
			if (--a.remaining < 0) return [];
			let e = o[i], t = n[s], c = Math.max(e[0], t[0]), l = Math.min(e[1], t[1]);
			if (c <= l) {
				let e = r.at(-1);
				if (e && e[1] + 1 === c) r[r.length - 1] = [e[0], l];
				else {
					if (r.length >= h) return [];
					r.push([c, l]);
				}
			}
			e[1] <= t[1] && i++, t[1] <= e[1] && s++;
		}
		if (!r.length) return [];
		o = r;
	}
	return Object.freeze((o ?? []).map((e) => Object.freeze(e)));
}
function S(e) {
	let t = 0, n = 0;
	for (; t < e.length && n < u.length;) {
		let [r, i] = e[t], [a, o] = u[n];
		if (i < a) t++;
		else if (o < r) n++;
		else return !0;
	}
	return !1;
}
function C(e, t, n = {}) {
	return w(e, t, !0, n.variations);
}
function w(u, f, p, h) {
	if (f !== void 0 && (!Number.isSafeInteger(f) || f < 0) || u.byteLength < 12) return null;
	let g = new DataView(u.buffer, u.byteOffset, u.byteLength), _ = 0;
	if (g.getUint32(0) === t) {
		if (f === void 0 || u.byteLength < 12) return null;
		let e = g.getUint32(8);
		if (f >= e || !d(u.byteLength, 12, e * 4)) return null;
		_ = g.getUint32(12 + f * 4);
	} else if (f !== void 0 && f !== 0) return null;
	if (!d(u.byteLength, _, 12)) return null;
	let v = g.getUint32(_);
	if (v !== 65536 && v !== n && v !== r && v !== i) return null;
	let y = g.getUint16(_ + 4);
	if (!d(u.byteLength, _ + 12, y * 16)) return null;
	let b = /* @__PURE__ */ new Map();
	for (let e = 0; e < y; e++) {
		let t = _ + 12 + e * 16, n = g.getUint32(t), r = g.getUint32(t + 8), i = g.getUint32(t + 12);
		if (b.has(n) || !d(u.byteLength, r, i)) return null;
		b.set(n, {
			offset: r,
			length: i
		});
	}
	let C;
	if (b.has(l) && p && (!h || (C = h(g, b, e) ?? void 0, !C))) return null;
	let w = b.get(a), T = b.get(o);
	if (!w || w.length < 20 || !T || T.length < 10) return null;
	let E = g.getUint16(w.offset + 18);
	if (E < 16 || E > 16384) return null;
	let D = b.get(s), O = D !== void 0 && D.length >= 4 ? g.getInt16(D.offset + 2) : 0, k = D !== void 0 && D.length >= 78, A = D !== void 0 && D.length >= 86 && g.getUint16(D.offset) >= 1, j = p ? x(g, b.get(c)) : void 0;
	return Object.freeze({
		unitsPerEm: E,
		...O > 0 ? { averageCharWidthRatio: O / E } : {},
		hheaAscent: g.getInt16(T.offset + 4),
		hheaDescent: g.getInt16(T.offset + 6),
		hheaLineGap: g.getInt16(T.offset + 8),
		farEastCodePage: A ? (g.getUint32(D.offset + 78) & 1966080) != 0 : null,
		hasEastAsianCmap: j ? S(j) : m(g, b.get(c)),
		...j === void 0 ? {} : { unicodeRanges: j },
		...k ? {
			typoAscent: g.getInt16(D.offset + 68),
			typoDescent: g.getInt16(D.offset + 70),
			typoLineGap: g.getInt16(D.offset + 72),
			winAscent: g.getUint16(D.offset + 74),
			winDescent: g.getUint16(D.offset + 76),
			useTypoMetrics: (g.getUint16(D.offset + 62) & 128) != 0
		} : {},
		...C ? { variation: C } : {}
	});
}
export { C as t };
