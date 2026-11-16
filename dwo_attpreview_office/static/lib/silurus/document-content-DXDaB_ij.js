import { r as e } from "./own-key-CzMRhMxt.js";
import { B as t, C as n, E as r, F as i, O as a, P as o, S as s, V as c, b as l, f as u, v as d, w as f, y as p, z as m } from "./wmf-HY7sNn5s.js";
import { n as h } from "./substitutions-_KDT_mVq.js";
import { a as g, i as _, r as v } from "./font-registry-CA7E7o7P.js";
import { a as y, c as b, d as x, l as S, m as C, n as w, o as T, p as E, r as D, s as O, u as k } from "./substitute-script-COw3MRyd.js";
import { c as A, d as j, i as M, l as N, n as P, o as F, s as I, t as L } from "./scripts-DxEAUeVI.js";
import { i as R } from "./office-fallback-O-L6rrDh.js";
import { a as z, t as ee } from "./symbol-font-Cf7Xu0_f.js";
import { G as B, H as V, K as te, P as H, U, V as ne, W as re, a as ie, c as ae, d as oe, i as se, l as W, n as ce, o as le, r as ue, s as de, t as fe, u as pe, z as me } from "./segment-line-BR56kM-V.js";
import { r as he } from "./paint-s8gGHFU5.js";
import { n as ge, t as _e } from "./synthetic-em-box-ls5vK0gE.js";
import { r as ve, t as ye } from "./drawingml-geometry-CIvPRuDI.js";
import { n as be, o as xe, t as Se } from "./line-distribute-DcBhkyOb.js";
import { t as Ce } from "./unicode-range-CD3UJT9S.js";
import { r as we, t as Te } from "./office-auto-line-D6xJtpwV.js";
import { a as Ee, d as De, f as Oe, i as ke, l as Ae, o as je, s as Me, t as Ne, u as Pe } from "./source-key-D06ZqbTD.js";
function Fe(e, t) {
	let n = e.trim();
	if (!n) throw TypeError("Canvas font route requires a family list");
	return Object.freeze({
		familyList: n,
		scope: t,
		fingerprint: `canvas-font-route-v1:${encodeURIComponent(t)}:${encodeURIComponent(n)}`
	});
}
function Ie(e, t, n, r) {
	if (!Number.isFinite(t) || t < 0) throw RangeError("Canvas font size must be finite and non-negative");
	if (!Number.isFinite(n) || n < 1 || n > 1e3) throw RangeError("Canvas font weight must be finite and between 1 and 1000");
	if (!e.familyList.trim()) throw TypeError("Canvas font route requires a family list");
	return `${r} ${n} ${t}px ${e.familyList}`;
}
var Le = "__ooxml_missing_font_control_6f33c9b4__";
function Re(e, t, n, r) {
	return `${r} ${n} ${t}px ${c(e)}, ${c(Le)}, serif`;
}
function ze(e) {
	return [
		e.width,
		e.actualBoundingBoxAscent,
		e.actualBoundingBoxDescent
	];
}
function Be(e, t, n) {
	let r = t.trim(), i = n.text, a = n.emPx ?? 100, o = n.weight ?? 400, s = n.style ?? "normal";
	if (!r || r === Le || !i || !Number.isFinite(a) || a <= 0 || !Number.isInteger(o) || o < 1 || o > 1e3) return null;
	let c = e.font;
	try {
		e.font = Re(r, a, o, s);
		let t = e.measureText(i);
		e.font = Re(Le, a, o, s);
		let n = e.measureText(i), c = ze(t), l = ze(n);
		if (c.every((e, t) => Object.is(e, l[t]))) return null;
		let u = t.fontBoundingBoxAscent, d = t.fontBoundingBoxDescent;
		return Number.isFinite(u) && Number.isFinite(d) && u + d > 0 ? (u + d) / a : null;
	} finally {
		e.font = c;
	}
}
var Ve = [
	[1e3, "M"],
	[900, "CM"],
	[500, "D"],
	[400, "CD"],
	[100, "C"],
	[90, "XC"],
	[50, "L"],
	[40, "XL"],
	[10, "X"],
	[9, "IX"],
	[5, "V"],
	[4, "IV"],
	[1, "I"]
], He = 4096;
function Ue(e) {
	if (e > He) throw RangeError("Number-format output budget exceeded");
}
function We(e) {
	let t = "", n = e;
	for (let [e, r] of Ve) {
		let i = Math.floor(n / e);
		Ue(t.length + i * r.length), t += r.repeat(i), n %= e;
	}
	return t;
}
function Ge(e, t) {
	let n = t.length, r = Math.floor((e - 1) / n) + 1, i = t[(e - 1) % n];
	return Ue(r * i.length), i.repeat(r);
}
var Ke = Array.from({ length: 26 }, (e, t) => String.fromCharCode(65 + t)), qe = /* @__PURE__ */ "أ.ب.ت.ث.ج.ح.خ.د.ذ.ر.ز.س.ش.ص.ض.ط.ظ.ع.غ.ف.ق.ك.ل.م.ن.ه.و.ي".split("."), Je = /* @__PURE__ */ "أ.ب.ج.د.ه.و.ز.ح.ط.ي.ك.ل.م.ن.س.ع.ف.ص.ق.ر.ش.ت.ث.خ.ذ.ض.غ.ظ".split("."), Ye = [
	"א",
	"ב",
	"ג",
	"ד",
	"ה",
	"ו",
	"ז",
	"ח",
	"ט",
	"י",
	"כ",
	"ל",
	"מ",
	"נ",
	"ס",
	"ע",
	"פ",
	"צ",
	"ק",
	"ר",
	"ש",
	"ת"
], Xe = [
	...rt(1072, 1080),
	...rt(1082, 1087),
	...rt(1088, 1097),
	"ы",
	"э",
	"ю",
	"я"
], Ze = [
	...rt(1040, 1048),
	...rt(1050, 1055),
	...rt(1056, 1065),
	"Ы",
	"Э",
	"Ю",
	"Я"
], Qe = [
	"ก",
	"ข",
	"ค",
	...rt(3591, 3619),
	"ล",
	...rt(3623, 3630)
], $e = [
	"ㄱ",
	"ㄴ",
	"ㄷ",
	"ㄹ",
	"ㅁ",
	"ㅂ",
	"ㅅ",
	"ㅇ",
	"ㅈ",
	"ㅊ",
	"ㅋ",
	"ㅌ",
	"ㅍ",
	"ㅎ"
], et = [
	"가",
	"나",
	"다",
	"라",
	"마",
	"바",
	"사",
	"아",
	"자",
	"차",
	"카",
	"타",
	"파",
	"하"
], tt = rt(2325, 2361), nt = [
	...rt(2309, 2324),
	"अं",
	"अः"
];
function rt(e, t) {
	let n = [];
	for (let r = e; r <= t; r++) n.push(String.fromCodePoint(r));
	return n;
}
var it = /* @__PURE__ */ "ア.イ.ウ.エ.オ.カ.キ.ク.ケ.コ.サ.シ.ス.セ.ソ.タ.チ.ツ.テ.ト.ナ.ニ.ヌ.ネ.ノ.ハ.ヒ.フ.ヘ.ホ.マ.ミ.ム.メ.モ.ヤ.ユ.ヨ.ラ.リ.ル.レ.ロ.ワ.ヰ.ヱ.ヲ.ン".split("."), at = [
	...rt(65393, 65436),
	"ｦ",
	"ﾝ"
];
function ot(e) {
	return e <= 20 ? String.fromCodePoint(9312 + (e - 1)) : String(e);
}
function st(e, t) {
	return String(e).split("").map((e) => t[e.charCodeAt(0) - 48]).join("");
}
var ct = rt(65296, 65305), lt = rt(3664, 3673), ut = rt(2406, 2415), dt = [
	"〇",
	"一",
	"二",
	"三",
	"四",
	"五",
	"六",
	"七",
	"八",
	"九"
], ft = [
	"영",
	"일",
	"이",
	"삼",
	"사",
	"오",
	"육",
	"칠",
	"팔",
	"구"
], pt = [
	"零",
	"一",
	"二",
	"三",
	"四",
	"五",
	"六",
	"七",
	"八",
	"九"
], mt = [
	"○",
	"一",
	"二",
	"三",
	"四",
	"五",
	"六",
	"七",
	"八",
	"九"
];
function ht(e, t) {
	if (e < 10) return t[e];
	if (e < 100) {
		let n = Math.floor(e / 10), r = e % 10, i = n === 1 ? "十" : t[n] + "十";
		return r === 0 ? i : i + t[r];
	}
	return st(e, t);
}
function gt(e, t) {
	if (t === "none") return "";
	if (!Number.isSafeInteger(e)) return String(e);
	switch (t) {
		case "upperRoman": return e >= 1 ? We(e) : String(e);
		case "lowerRoman": return e >= 1 ? We(e).toLowerCase() : String(e);
		case "upperLetter": return e >= 1 ? Ge(e, Ke) : String(e);
		case "lowerLetter": return e >= 1 ? Ge(e, Ke).toLowerCase() : String(e);
		case "arabicAlpha": return e >= 1 ? Ge(e, qe) : String(e);
		case "arabicAbjad": return e >= 1 ? Ge(e, Je) : String(e);
		case "russianLower": return e >= 1 ? Ge(e, Xe) : String(e);
		case "russianUpper": return e >= 1 ? Ge(e, Ze) : String(e);
		case "thaiLetters": return e >= 1 ? Ge(e, Qe) : String(e);
		case "chosung": return e >= 1 ? Ge(e, $e) : String(e);
		case "ganada": return e >= 1 ? Ge(e, et) : String(e);
		case "hindiVowels": return e >= 1 ? Ge(e, tt) : String(e);
		case "hindiConsonants": return e >= 1 ? Ge(e, nt) : String(e);
		case "aiueoFullWidth": return e >= 1 ? Ge(e, it) : String(e);
		case "aiueo": return e >= 1 ? Ge(e, at) : String(e);
		case "decimalEnclosedCircle": return e >= 1 ? ot(e) : String(e);
		case "hebrew1": return e >= 1 ? bt(e) : String(e);
		case "hebrew2": return e >= 1 ? xt(e) : String(e);
		case "hex": return e >= 1 ? e.toString(16).toUpperCase() : String(e);
		case "numberInDash": return e >= 1 ? `- ${e} -` : String(e);
		case "decimalZero": return e >= 1 && e <= 9 ? `0${e}` : String(e);
		case "decimalFullWidth": return e >= 1 ? st(e, ct) : String(e);
		case "decimalHalfWidth": return String(e);
		case "thaiNumbers": return e >= 1 ? st(e, lt) : String(e);
		case "hindiNumbers": return e >= 1 ? st(e, ut) : String(e);
		case "ideographDigital":
		case "japaneseDigitalTenThousand": return e >= 1 ? st(e, dt) : String(e);
		case "koreanDigital": return e >= 1 ? st(e, ft) : String(e);
		case "koreanDigital2": return e >= 1 ? st(e, pt) : String(e);
		case "taiwaneseDigital": return e >= 1 ? st(e, mt) : String(e);
		case "chineseCounting": return e >= 1 ? ht(e, dt) : String(e);
		case "taiwaneseCounting": return e >= 1 ? ht(e, mt) : String(e);
		case "chineseCountingThousand": return e >= 1 ? At(e, Ct) : String(e);
		case "taiwaneseCountingThousand": return e >= 1 ? At(e, wt) : String(e);
		case "chineseLegalSimplified": return e >= 1 ? At(e, Et) : String(e);
		case "ideographLegalTraditional": return e >= 1 ? At(e, Ot) : String(e);
		case "japaneseCounting": return e >= 1 ? At(e, St) : String(e);
		case "japaneseLegal": return e >= 1 ? At(e, Dt) : String(e);
		case "koreanCounting": return e >= 1 ? At(e, Tt) : String(e);
		case "koreanLegal": return e >= 1 ? Nt(e) : String(e);
		default: return String(e);
	}
}
var _t = [
	"",
	"א",
	"ב",
	"ג",
	"ד",
	"ה",
	"ו",
	"ז",
	"ח",
	"ט"
], vt = [
	"",
	"י",
	"כ",
	"ל",
	"מ",
	"נ",
	"ס",
	"ע",
	"פ",
	"צ"
], yt = [
	"",
	"ק",
	"ר",
	"ש",
	"ת",
	"ך",
	"ם",
	"ן",
	"ף",
	"ץ"
];
function bt(e) {
	let t = "", n = e, r = Math.floor(n / 1e3);
	n %= 1e3;
	let i = Math.floor(n / 100);
	if (n %= 100, r > 0 && (t += _t[r % 10]), t += yt[i], n === 15) return t + "טו";
	if (n === 16) return t + "טז";
	let a = Math.floor(n / 10), o = n % 10;
	return t += vt[a], t += _t[o], t;
}
function xt(e) {
	let t = Ye.length, n = Math.floor((e - 1) / t), r = e - t * n;
	return Ue(1 + n), Ye[r - 1] + "ת".repeat(n);
}
var St = {
	digits: pt,
	ten: "十",
	hundred: "百",
	thousand: "千",
	myriad: "万",
	elideOne: !0,
	insertZero: !1
}, Ct = {
	...St,
	elideOne: !1,
	insertZero: !0
}, wt = { ...Ct }, Tt = {
	digits: [
		"영",
		"일",
		"이",
		"삼",
		"사",
		"오",
		"육",
		"칠",
		"팔",
		"구"
	],
	ten: "십",
	hundred: "백",
	thousand: "천",
	myriad: "만",
	elideOne: !0,
	insertZero: !1
}, Et = {
	digits: [
		"零",
		"壹",
		"贰",
		"叁",
		"肆",
		"伍",
		"陆",
		"柒",
		"捌",
		"玖"
	],
	ten: "拾",
	hundred: "佰",
	thousand: "仟",
	myriad: "万",
	elideOne: !1,
	insertZero: !0
}, Dt = {
	digits: [
		"零",
		"壱",
		"弐",
		"参",
		"四",
		"伍",
		"六",
		"七",
		"八",
		"九"
	],
	ten: "拾",
	hundred: "百",
	thousand: "阡",
	myriad: "萬",
	elideOne: !1,
	insertZero: !1
}, Ot = {
	digits: [
		"零",
		"壹",
		"貳",
		"參",
		"肆",
		"伍",
		"陸",
		"柒",
		"捌",
		"玖"
	],
	ten: "拾",
	hundred: "佰",
	thousand: "仟",
	myriad: "萬",
	elideOne: !1,
	insertZero: !1
};
function kt(e, t, n) {
	let r = Math.floor(e / 1e3) % 10, i = Math.floor(e / 100) % 10, a = Math.floor(e / 10) % 10, o = e % 10, s = [
		{
			digit: r,
			unit: t.thousand
		},
		{
			digit: i,
			unit: t.hundred
		},
		{
			digit: a,
			unit: t.ten
		},
		{
			digit: o,
			unit: ""
		}
	], c = "", l = !1, u = !1;
	for (let { digit: e, unit: r } of s) {
		if (e === 0) {
			l && (u = !0);
			continue;
		}
		u &&= (t.insertZero && (c += t.digits[0]), !1), n && e === 1 && r ? c += r : c += t.digits[e] + r, l = !0;
	}
	return c;
}
function At(e, t) {
	if (e >= 1e8) {
		let n = Math.floor(e / 1e8), r = e % 1e8, i = At(n, t) + "億";
		return r === 0 ? i : i + (t.insertZero && r < 1e7 ? t.digits[0] : "") + At(r, t);
	}
	let n = Math.floor(e / 1e4), r = e % 1e4, i = "";
	return n > 0 && (i += kt(n, t, t.elideOne) + t.myriad), r > 0 && (t.insertZero && n > 0 && r < 1e3 && (i += t.digits[0]), i += kt(r, t, t.elideOne)), i;
}
var jt = [
	"",
	"하나",
	"둘",
	"셋",
	"넷",
	"다섯",
	"여섯",
	"일곱",
	"여덟",
	"아홉"
], Mt = [
	"",
	"열",
	"스물",
	"서른",
	"마흔",
	"쉰",
	"예순",
	"일흔",
	"여든",
	"아흔"
];
function Nt(e) {
	if (e >= 100) return String(e);
	let t = Math.floor(e / 10), n = e % 10;
	return Mt[t] + jt[n];
}
var Pt = {
	Arabic: "decimal",
	ArabicDash: "numberInDash",
	Hex: "hex",
	Roman: "upperRoman",
	roman: "lowerRoman",
	ALPHABETIC: "upperLetter",
	alphabetic: "lowerLetter",
	ARABICABJAD: "arabicAbjad",
	ARABICALPHA: "arabicAlpha",
	HEBREW1: "hebrew1",
	HEBREW2: "hebrew2",
	HINDIARABIC: "hindiNumbers",
	HINDILETTER1: "hindiVowels",
	HINDILETTER2: "hindiConsonants",
	THAIARABIC: "thaiNumbers",
	THAILETTER: "thaiLetters",
	CHOSUNG: "chosung",
	GANADA: "ganada",
	DBCHAR: "decimalFullWidth",
	SBCHAR: "decimalHalfWidth"
};
function Ft(t) {
	let n = /\\\*\s+(\S+)/g, r;
	for (; (r = n.exec(t)) !== null;) {
		let t = e(Pt, r[1]);
		if (t) return t;
	}
	return null;
}
var It = [
	"January",
	"February",
	"March",
	"April",
	"May",
	"June",
	"July",
	"August",
	"September",
	"October",
	"November",
	"December"
], Lt = [
	"Jan",
	"Feb",
	"Mar",
	"Apr",
	"May",
	"Jun",
	"Jul",
	"Aug",
	"Sep",
	"Oct",
	"Nov",
	"Dec"
], Rt = [
	"Sunday",
	"Monday",
	"Tuesday",
	"Wednesday",
	"Thursday",
	"Friday",
	"Saturday"
], zt = [
	"Sun",
	"Mon",
	"Tue",
	"Wed",
	"Thu",
	"Fri",
	"Sat"
], Bt = (e) => e < 10 ? `0${e}` : `${e}`;
function Vt(e) {
	let t = /\\@\s*"([^"]*)"/.exec(e);
	if (t) return t[1];
	let n = /\\@\s*(\S+)/.exec(e);
	return n ? n[1] : null;
}
function Ht(e, t) {
	let n = t.getFullYear(), r = t.getMonth(), i = t.getDate(), a = t.getDay(), o = t.getHours(), s = o % 12 == 0 ? 12 : o % 12, c = t.getMinutes(), l = t.getSeconds(), u = o >= 12, d = "", f = 0, p = e.length;
	for (; f < p;) {
		let t = e[f];
		if (t === "'") {
			f++;
			let t = "";
			for (; f < p;) {
				if (e[f] === "'") {
					if (e[f + 1] === "'") {
						t += "'", f += 2;
						continue;
					}
					f++;
					break;
				}
				t += e[f++];
			}
			d += t;
			continue;
		}
		if (/[A-Za-z]/.test(t)) {
			let u = f;
			for (; u < p && e[u] === t;) u++;
			let m = e.slice(f, u).length, h = t.toLowerCase(), g = null;
			if (t === "y" || t === "Y" ? g = m >= 4 ? String(n).padStart(4, "0") : Bt(n % 100) : t === "M" ? g = m >= 4 ? It[r] : m === 3 ? Lt[r] : m === 2 ? Bt(r + 1) : String(r + 1) : h === "d" ? g = m >= 4 ? Rt[a] : m === 3 ? zt[a] : m === 2 ? Bt(i) : String(i) : t === "H" ? g = m >= 2 ? Bt(o) : String(o) : t === "h" ? g = m >= 2 ? Bt(s) : String(s) : t === "m" ? g = m >= 2 ? Bt(c) : String(c) : t === "s" ? g = m >= 2 ? Bt(l) : String(l) : (h === "a" || h === "p") && (g = null), g !== null) {
				d += g, f = u;
				continue;
			}
			if (!(h === "a" || h === "p")) return null;
		}
		let m = /^([AaPp])([Mm])?\/([AaPp])([Mm])?/.exec(e.slice(f));
		if (m) {
			let e = m[2] !== void 0;
			d += e ? u ? "PM" : "AM" : u ? "P" : "A", f += m[0].length;
			continue;
		}
		d += t, f++;
	}
	return d;
}
function Ut(e) {
	return e.trim().toLowerCase();
}
var Wt = 2 * ne;
function Gt(e) {
	return e ? e.createElement("canvas").getContext("2d") : typeof OffscreenCanvas < "u" ? new OffscreenCanvas(1, 1).getContext("2d") : typeof document < "u" ? document.createElement("canvas").getContext("2d") : null;
}
function Kt(e, t) {
	return e.length === t.length && e.every((e, n) => e.name === t[n].name && e.generic === t[n].generic);
}
function qt(e) {
	let n = /* @__PURE__ */ new Set();
	if (!e || typeof e[Symbol.iterator] != "function") return n;
	for (let r of e) {
		let e = t(r.family)?.[0]?.name ?? r.family;
		n.add(e.trim().toLowerCase());
	}
	return n;
}
function Jt(e, t, n) {
	for (let r = 0; r < t.length; r += 1) {
		let i = t[r];
		if (i.generic) return r;
		let a = i.text, o = n.get(a);
		if (o === void 0) {
			let t = U.map((t) => {
				e.font = `${ne}px ${i.text}, ${c(t)}`;
				let n = e.measureText("");
				return [n.fontBoundingBoxAscent, n.fontBoundingBoxDescent];
			});
			o = t[0][0] === t[1][0] && t[0][1] === t[1][1], n.set(a, o);
		}
		if (o) return r;
	}
}
function Yt(e, t, n, r) {
	let i = Jt(e, t, r);
	if (!(i === void 0 || t[i].generic)) {
		for (let e = 0; e <= i; e += 1) if (n.has(t[e].name.toLowerCase())) return;
		return i;
	}
}
function Xt(e, t) {
	return Math.abs(e.height - 2 * t.height) <= 3 && Math.abs(e.ascent - 2 * t.ascent) <= 1 && Math.abs(e.descent - 2 * t.descent) <= 1;
}
var Zt = 4;
function Qt(e, n, r) {
	let i = e.map(() => null), a = n.body ? Gt(n) : null, o = n.defaultView;
	if (!a || !o || !te(a)) return i;
	let s = qt(n.fonts), c = /* @__PURE__ */ new Map(), l = /* @__PURE__ */ new Map(), u = /* @__PURE__ */ new Map();
	e.forEach((e, n) => {
		let i = t(e.familyList);
		if (!i) return;
		let o = Yt(a, i, s, c);
		if (o === void 0 || !r(i[o].name, e.weight, e.style)) return;
		u.set(n, o);
		let d = JSON.stringify([
			i[o].text,
			e.weight,
			e.style
		]), f = l.get(d);
		f ? f.requests.push(n) : l.set(d, {
			requests: [n],
			primary: i[o],
			weight: e.weight,
			style: e.style,
			em: Wt
		});
	});
	let d = [...l.values()];
	for (let r = 0; r < Zt && d.length > 0; r += 1) {
		let r = n.createElement("div");
		if (r.style.cssText = "all:initial;position:fixed;visibility:hidden;contain:strict;", typeof r.attachShadow != "function") return i;
		let s = r.attachShadow({ mode: "closed" }), c = d.map((e) => [e.em, e.em / 2].map((t) => {
			let r = n.createElement("span");
			return r.style.cssText = `all:initial;display:block;white-space:pre;font:${e.style} ${e.weight} ${t}px ${e.primary.text};line-height:normal;`, r.textContent = "​", s.append(r), r;
		})), l = [];
		n.body.append(r);
		try {
			d.forEach((n, r) => {
				let [s, d] = c[r].map((e, r) => {
					let i = t(o.getComputedStyle(e).fontFamily);
					if (!i || !Kt(i, [n.primary])) return null;
					let s = r ? n.em / 2 : n.em;
					a.font = `${n.style} ${n.weight} ${s}px ${n.primary.text}`;
					let c = a.measureText(""), l = e.offsetHeight;
					return Number.isFinite(l) && l > 0 && Number.isFinite(c.fontBoundingBoxAscent) && c.fontBoundingBoxAscent >= 0 && Number.isFinite(c.fontBoundingBoxDescent) && c.fontBoundingBoxDescent >= 0 ? {
						height: l,
						ascent: c.fontBoundingBoxAscent,
						descent: c.fontBoundingBoxDescent
					} : null;
				});
				if (!(!s || !d)) {
					if (!Xt(s, d)) {
						n.em /= 2, l.push(n);
						return;
					}
					for (let t of n.requests) {
						let r = e[t];
						i[t] = Object.freeze({
							familyList: r.familyList,
							weight: r.weight,
							style: r.style,
							primaryIndex: u.get(t),
							primaryFamily: n.primary.name,
							primaryFamilyText: n.primary.text,
							emPx: n.em,
							ascentRatio: s.ascent / n.em,
							descentRatio: s.descent / n.em,
							lineGapRatio: (s.height - s.ascent - s.descent) / n.em
						});
					}
				}
			});
		} catch {
			l.length = 0;
		} finally {
			r.remove();
		}
		d = l;
	}
	return i;
}
function $t(e, n) {
	let r = Gt();
	if (!r || !te(r)) return e.map(() => !1);
	let i = qt(n), a = /* @__PURE__ */ new Map();
	return e.map((e) => {
		let n = t(e.familyList);
		if (!n || n[e.primaryIndex]?.name !== e.primaryFamily || n[e.primaryIndex].text !== e.primaryFamilyText || Yt(r, n, i, a) !== e.primaryIndex) return !1;
		r.font = `${e.style} ${e.weight} ${e.emPx}px ${e.primaryFamilyText}`;
		let o = r.measureText("");
		return Math.abs(o.fontBoundingBoxAscent - e.ascentRatio * e.emPx) < .001 && Math.abs(o.fontBoundingBoxDescent - e.descentRatio * e.emPx) < .001;
	});
}
function en(e, t, n) {
	return [`${n} ${t} ${ne}px ${e}, ${c(U[0])}`, `${n} ${t} ${ne}px ${e}, ${c(U[1])}`];
}
var tn = (V[0].inkUp + V[0].inkDown) * ne / re, nn = [`${ne}px ${c(U[0])}`, `${ne}px ${c(U[1])}`], rn = [], an = [], on = /* @__PURE__ */ new Map();
function sn(e, t) {
	let n = e.measureText(t);
	return [
		n.width,
		n.actualBoundingBoxLeft,
		n.actualBoundingBoxRight,
		n.actualBoundingBoxAscent,
		n.actualBoundingBoxDescent
	];
}
function cn(e, t) {
	let n = [];
	for (let r = 0; r < 2; r += 1) {
		rn[r] ??= Gt();
		let i = rn[r];
		if (!i) return;
		an[r] !== e[r] && (i.font = e[r], an[r] = e[r]), n.push(sn(i, t));
	}
	return n;
}
var ln = (e, t) => e.every((e, n) => Number.isFinite(e) && Object.is(e, t[n])), un = /[\p{Extended_Pictographic}\p{Emoji_Modifier}\p{Regional_Indicator}\u200d\u20e3\ufe00-\ufe0f\u{e0020}-\u{e007f}\u{e0100}-\u{e01ef}]/u;
function dn(e, t) {
	if (un.test(t)) return !1;
	let n = on.get(t);
	if (n === void 0) {
		let e = cn(nn, t);
		if (!e) return;
		n = !ln(e[0], e[1]), on.size >= 4096 && on.delete(on.keys().next().value), on.set(t, n);
	}
	if (!n) return !1;
	let r = cn(e, t);
	if (!r) return;
	let [, , , i, a] = r[0];
	return ln(r[0], r[1]) && i + a < tn;
}
function fn() {
	let e = Gt();
	return e !== null && te(e);
}
var pn = /* @__PURE__ */ new WeakMap();
function mn(e, t, n, r, i) {
	if (e.status !== "loaded") return null;
	let a = pn.get(e);
	if (a?.emPx === r) return a.metric;
	let o = hn(e, e.weight, e.style, t, n, r, i);
	return pn.set(e, {
		emPx: r,
		metric: o
	}), o;
}
function hn(e, t, n, r, i, a, o) {
	return gn([{
		face: e,
		weight: t,
		style: n
	}], r, i, a, o)[0];
}
function gn(e, t, n, r, i) {
	let a = e.map(() => null);
	if (!Number.isFinite(r) || r <= 0 || !i?.body || i.fonts !== t) return a;
	let o = e.flatMap((e, t) => e.face.status === "loaded" ? [{
		index: t,
		request: e,
		em: r
	}] : []);
	for (let e = 0; e < _n && o.length > 0; e++) {
		let e = vn(o.flatMap(({ request: e, em: t }) => [{
			family: e.face.family,
			weight: e.weight,
			style: e.style,
			em: t
		}, {
			family: e.face.family,
			weight: e.weight,
			style: e.style,
			em: t / 2
		}]), n, i), t = [];
		o.forEach((n, r) => {
			let i = e[r * 2], o = e[r * 2 + 1];
			if (!(!i || !o)) {
				if (bn(i, o)) {
					a[n.index] = Object.freeze({
						ascentRatio: i.ascent / n.em,
						descentRatio: i.descent / n.em,
						lineGapRatio: (i.height - i.ascent - i.descent) / n.em
					});
					return;
				}
				n.em /= 2, t.push(n);
			}
		}), o = t;
	}
	return a;
}
var _n = 4;
function vn(e, t, n) {
	let r = e.map(() => null), i = n.createElement("div");
	if (i.style.cssText = "all:initial;position:fixed;visibility:hidden;contain:strict;", typeof i.attachShadow != "function") return r;
	let a = t.font;
	try {
		let a = i.attachShadow({ mode: "closed" }), o = e.map(({ family: e, weight: t, style: r, em: i }) => {
			let o = `${r} ${t} ${i}px ${c(e)}`, s = n.createElement("span");
			return s.style.cssText = `all:initial;display:block;white-space:pre;font:${o};line-height:normal;`, s.textContent = "​", a.append(s), {
				probe: s,
				font: o,
				family: e
			};
		});
		n.body.append(i);
		let s = n.defaultView;
		return s && o.forEach(({ probe: e, font: n, family: i }, a) => {
			try {
				if (yn(s.getComputedStyle(e).fontFamily) !== yn(c(i))) return;
				t.font = n;
				let o = t.measureText(""), l = e.offsetHeight, u = o.fontBoundingBoxAscent, d = o.fontBoundingBoxDescent;
				r[a] = Number.isFinite(l) && l > 0 && Number.isFinite(u) && u >= 0 && Number.isFinite(d) && d >= 0 ? {
					height: l,
					ascent: u,
					descent: d
				} : null;
			} catch {}
		}), r;
	} catch {
		return e.map(() => null);
	} finally {
		i.remove(), t.font = a;
	}
}
function yn(e) {
	return e.trim().replace(/^(["'])(.*)\1$/, "$2");
}
function bn(e, t) {
	return Math.abs(e.height - 2 * t.height) <= 3 && Math.abs(e.ascent - 2 * t.ascent) <= 1 && Math.abs(e.descent - 2 * t.descent) <= 1;
}
async function xn(e, t, n) {
	let r = `${e.family}_coverage`, { face: i } = _(`local-coverage:${t}:${e.weight}:${e.style}`, n, () => {
		let i = new FontFace(r, t, {
			weight: e.weight,
			style: e.style,
			sizeAdjust: "0%"
		});
		return n.add(i), i;
	});
	try {
		if (await g(i.load()) && i.status === "loaded" && i.sizeAdjust === "0%" && Cn(i, e)) return i;
	} catch {}
	return v([i]), null;
}
var Sn = "A";
function Cn(e, t) {
	let n = wn();
	if (!n) return !1;
	try {
		n.font = `${e.style} ${e.weight} 100px ${c(e.family)}`;
		let r = n.measureText(Sn);
		n.font = `${t.style} ${t.weight} 100px ${c(t.family)}`;
		let i = n.measureText(Sn);
		return r.width === 0 && r.actualBoundingBoxAscent === 0 && r.actualBoundingBoxDescent === 0 && i.width > 0;
	} catch {
		return !1;
	}
}
function wn() {
	return typeof OffscreenCanvas < "u" ? new OffscreenCanvas(1, 1).getContext("2d") : typeof document < "u" ? document.createElement("canvas").getContext("2d") : null;
}
var Tn, En = /^[\x20-\x7e]*$/;
function Dn(e) {
	if (En.test(e)) return e;
	let t = O();
	return t ? Array.from(t.segment(e), (e) => e.segment) : [e];
}
var On = /* @__PURE__ */ new WeakMap();
function kn(e, t, n) {
	let r = e.glyphCoverageProbeFamily, i = e.nativeRoutePrimaryFamily;
	if (!r && !i || !t) return !e.requiresGlyphCoverage || t.length === 0;
	if (!n) return !1;
	let a = On.get(e);
	a || (a = /* @__PURE__ */ new WeakMap(), On.set(e, a));
	let o = a.get(n);
	if (!o) {
		if (i) {
			if (!fn()) return !1;
			let t = en(i, e.weight ?? 400, e.style ?? "normal");
			o = {
				measure: (e) => dn(t, e),
				results: /* @__PURE__ */ new Map(),
				clusters: /* @__PURE__ */ new Map()
			};
		} else {
			let t = c(e.family);
			if (n.familyList !== t && !n.familyList.startsWith(`${t},`)) return !1;
			let i = c(r) + n.familyList.slice(t.length), a = `${e.style ?? "normal"} ${e.weight ?? 400} 100px ${i}`;
			o = {
				measure: (e) => Mn(a, e),
				results: /* @__PURE__ */ new Map(),
				clusters: /* @__PURE__ */ new Map()
			};
		}
		a.set(n, o);
	}
	let s = o.results, l = s.get(t);
	if (l !== void 0) return l;
	let u = !0;
	for (let e of Dn(t)) {
		let t = o.clusters.get(e);
		if (t === void 0) {
			let n = o.measure(e);
			if (n === void 0) return !1;
			t = n, An(o, e, t);
		}
		if (!t) {
			u = !1;
			break;
		}
	}
	return s.size >= 1024 && s.delete(s.keys().next().value), s.set(t, u), u;
}
function An(e, t, n) {
	e.clusters.size >= 4096 && e.clusters.delete(e.clusters.keys().next().value), e.clusters.set(t, n);
}
var jn;
function Mn(e, t) {
	if (Tn ??= wn(), !Tn) return;
	jn !== e && (Tn.font = e, jn = e);
	let n = Tn.measureText(t);
	return n.width === 0 && n.actualBoundingBoxAscent === 0 && n.actualBoundingBoxDescent === 0;
}
async function Nn(e, t, n, r, i, a) {
	let { face: o } = _(`local-normal:${e}:${n}:${r}`, a.fonts, () => {
		let i = new FontFace(`${t}_normal`, e, {
			weight: String(n),
			style: r
		});
		return a.fonts.add(i), i;
	});
	try {
		let e = await g(o.load()), t = a.createElement("canvas").getContext("2d");
		return e && t ? mn(o, a.fonts, t, i, a) : null;
	} catch {
		return null;
	} finally {
		v([o]);
	}
}
var Pn = 15e3, Fn = 1024, In = [
	{
		weight: 400,
		style: "normal"
	},
	{
		weight: 700,
		style: "normal"
	},
	{
		weight: 400,
		style: "italic"
	},
	{
		weight: 700,
		style: "italic"
	}
], Ln = (e, t) => `${e}:${t}`, Rn = (e) => (Ce(e) ?? [[0, 1114111]]).some(([e, t]) => e <= 32 && 32 <= t);
function zn(e) {
	let t = [], n = /* @__PURE__ */ new Map(), r = (t, n) => {
		let r = e.faces[t];
		return {
			index: t,
			source: r.probeSource,
			weight: r.weight,
			style: r.style,
			stretch: r.stretch,
			...n ? { members: n } : {}
		};
	}, i = /* @__PURE__ */ new Map();
	for (let t of e.faces) {
		let e = h(t.family), n = t.sharedSubsetMetrics ? t.sourceIndex : null;
		i.set(e, i.has(e) && i.get(e) !== n ? null : n);
	}
	e.faces.forEach((e, a) => {
		if (e.resourceMetrics || e.probeSource === void 0) return;
		if (!e.sharedSubsetMetrics || i.get(h(e.family)) == null) {
			t.push(r(a));
			return;
		}
		let o = [
			e.sourceIndex,
			h(e.family),
			e.weight,
			e.style,
			e.stretch
		].join("\0"), s = n.get(o);
		s ? s.push(a) : n.set(o, [a]);
	});
	for (let i of n.values()) {
		let n = [...i].reverse().find((t) => Rn(e.faces[t].unicodeRange));
		n === void 0 ? t.push(...i.map((e) => r(e))) : t.push(r(n, Object.freeze(i)));
	}
	return t.sort((e, t) => e.index - t.index);
}
var Bn = 0, Vn = /* @__PURE__ */ new WeakMap(), Hn = 0;
function Un(e) {
	let { source: t } = e;
	if (typeof t == "string") return;
	let n = Vn.get(t);
	return n === void 0 && (n = ++Hn, Vn.set(t, n)), `served-face:bytes:${n}\u0000${e.weight}\u0000${e.style}\u0000${e.stretch}`;
}
function Wn(e, t) {
	return _(Un(e) ?? `served-face:${++Bn}`, t, () => {
		let n = new FontFace(`__ooxml_served_face_${++Bn}`, e.source, {
			weight: e.weight,
			style: e.style,
			stretch: e.stretch
		});
		return t.add(n), n;
	}).face;
}
function Gn(e, t) {
	let n = /* @__PURE__ */ new Map();
	return e.map((e) => {
		let r = Un(e), i = r === void 0 ? void 0 : n.get(r);
		if (i) return i;
		let a = Wn(e, t);
		return r !== void 0 && n.set(r, a), a;
	});
}
async function Kn(e, t) {
	if (t?.aborted) return !1;
	let n, r, i = new Promise((e) => {
		n = setTimeout(() => e(!1), Pn), r = () => e(!1), t?.addEventListener("abort", r, { once: !0 });
	});
	try {
		return await Promise.race([e.load().then(() => e.status === "loaded", () => !1), i]);
	} finally {
		clearTimeout(n), r && t?.removeEventListener("abort", r);
	}
}
function qn(e, t) {
	let n = [...new Set(e)], r = n.length ? t.createElement("canvas").getContext("2d") : null, i = r ? gn(n.flatMap((e) => In.map(({ weight: t, style: n }) => ({
		face: e,
		weight: t,
		style: n
	}))), t.fonts, r, Fn, t) : [], a = /* @__PURE__ */ new Map();
	return n.forEach((e, t) => {
		let n = Object.create(null);
		In.forEach(({ weight: e, style: r }, a) => {
			n[Ln(e, r)] = i[t * In.length + a] ?? null;
		}), a.set(e, n);
	}), e.map((e) => a.get(e));
}
async function Jn(e, t) {
	let n = typeof document > "u" ? null : document;
	if (!n?.body) return e.map(({ index: e }) => ({
		index: e,
		lines: {}
	}));
	let r = Gn(e, n.fonts);
	try {
		let i = await Promise.all(r.map((e) => Kn(e, t))), a = qn(r.filter((e, t) => i[t]), n), o = 0;
		return e.map((e, t) => ({
			index: e.index,
			lines: i[t] ? a[o++] : {}
		}));
	} finally {
		setTimeout(() => v(new Set(r)), 0);
	}
}
var Yn = Object.freeze({
	faceLines: /* @__PURE__ */ new Map(),
	familyLines: /* @__PURE__ */ new Map()
});
async function Xn(e, t, n, r, i) {
	let a = e ? zn(e) : [], o = typeof document < "u" && document.body && document.fonts === t ? document : null, s = o ? Qn(t, n) : [];
	if (!t || a.length === 0 && s.length === 0 || i?.aborted) return {
		...Yn,
		faces: []
	};
	let c = await B(t);
	if (!c) return {
		...Yn,
		faces: []
	};
	let l = [...c];
	if (i?.aborted) return R(l), {
		...Yn,
		faces: []
	};
	let u = /* @__PURE__ */ new Map(), d = /* @__PURE__ */ new Map(), f = a.filter((e) => o || !e.members), p = Gn(f, t), m = await Promise.all(p.map((e) => Kn(e, i))), g = /* @__PURE__ */ new Map();
	f.forEach((e, t) => {
		m[t] && g.set(e, p[t]);
	});
	let _ = new Set(f.flatMap((e) => !e.members && g.has(e) ? [g.get(e)] : []));
	l.push(..._);
	let y = a.filter((e) => g.has(e) || !o && e.members), b = o || i?.aborted ? void 0 : await r, x = new Map(b?.map((e) => [e.index, e.lines])), S = o && !i?.aborted ? qn(y.map((e) => g.get(e)), o) : y.map((e) => x.get(e.index));
	if (v(new Set(p.filter((e) => !_.has(e)))), y.forEach((t, n) => {
		let r = S[n];
		if (!r) return;
		if (!t.members) {
			u.set(t.index, {
				ownershipFamily: g.get(t).family,
				lines: r
			});
			return;
		}
		let i = e?.families.get(h(e.faces[t.index].family));
		if (i) for (let e of t.members) u.set(e, {
			ownershipFamily: i,
			lines: r
		});
	}), i?.aborted) return R(l), {
		...Yn,
		faces: []
	};
	let C = s.length ? qn(s, o) : [];
	return s.forEach((e, t) => {
		d.set(h(Zn(e.family)), {
			ownershipFamily: Zn(e.family),
			lines: C[t]
		});
	}), u.size === 0 && d.size === 0 ? (R(l), {
		...Yn,
		faces: []
	}) : {
		faceLines: u,
		familyLines: d,
		faces: l
	};
}
var Zn = (e) => e.trim().replace(/^(['"])(.*)\1$/, "$2");
function Qn(e, t) {
	if (!e || typeof e[Symbol.iterator] != "function") return [];
	let n = new Set(t.map(h)), r = /* @__PURE__ */ new Map();
	for (let t of e) {
		if (t.status !== "loaded") continue;
		let e = h(Zn(t.family));
		n.has(e) && r.set(e, [...r.get(e) ?? [], t]);
	}
	let i = [];
	for (let e of r.values()) {
		let [t] = e;
		e.length !== 1 || !t || (Ce(t.unicodeRange) ?? [[0, 1114111]]).some(([e, t]) => e <= 32 && 32 <= t) && i.push(t);
	}
	return i;
}
function $n(e) {
	return Object.freeze((e ?? []).flatMap((e) => e.substitutions ?? []));
}
function er(e) {
	let t = /* @__PURE__ */ new Map();
	for (let n of e) {
		let e = h(n.for), r = n.script ?? null, i = t.get(e);
		t.set(e, i === void 0 || i === r ? r : null);
	}
	let n = /* @__PURE__ */ new Map();
	for (let [e, r] of t) r !== null && n.set(e, r);
	return n;
}
function tr(e, t, n) {
	return t ? e + Math.max(0, n) : e;
}
function nr(e, t, n, r, i) {
	return i ? {
		start: Math.max(e, n),
		end: Math.min(t, r)
	} : {
		start: e,
		end: t
	};
}
function rr(e) {
	let { unitsPerEm: t, hhea: n, win: r, typo: i } = e;
	if (!(Number.isFinite(t) && t > 0)) return;
	let [a, o, s] = n[0] >= 0 && n[1] <= 0 ? [
		n[0],
		-n[1],
		n[2]
	] : [
		0,
		0,
		0
	];
	if (a === 0 && o === 0 && r && ([a, o, s] = [
		r[0],
		r[1],
		0
	]), i && i[0] >= 0 && i[1] <= 0 && ([a, o, s] = [
		i[0],
		-i[1],
		i[2]
	]), !(![
		a,
		o,
		s
	].every(Number.isFinite) || !(a + o > 0))) return Object.freeze({
		normalAscentRatio: a / t,
		normalDescentRatio: o / t,
		normalLineGapRatio: s / t
	});
}
function ir(e) {
	return rr({
		unitsPerEm: e.unitsPerEm,
		hhea: [
			e.hheaAscent,
			e.hheaDescent,
			e.hheaLineGap
		],
		...e.winAscent !== void 0 && e.winDescent !== void 0 ? { win: [e.winAscent, e.winDescent] } : {},
		...e.useTypoMetrics && e.typoAscent !== void 0 && e.typoDescent !== void 0 ? { typo: [
			e.typoAscent,
			e.typoDescent,
			e.typoLineGap ?? 0
		] } : {}
	});
}
function ar(e, t) {
	let n = ir(e);
	if (!n) return;
	let r = $r({
		...e,
		farEastCodePage: !1
	}) ?? sr(n), i = e.farEastCodePage === !0 ? $r({
		...e,
		farEastCodePage: !0
	}) : null;
	return {
		...e.farEastCodePage == null ? {} : { farEastCodePage: e.farEastCodePage },
		lineHeightRatio: r.lineHeightRatio,
		designAscentRatio: r.designAscentRatio,
		designDescentRatio: r.designDescentRatio,
		...n,
		...i ? {
			wordLineHeightRatio: i.lineHeightRatio,
			wordAscentRatio: i.designAscentRatio,
			wordDescentRatio: i.designDescentRatio
		} : {},
		...t === void 0 ? {} : { unicodeRanges: t },
		...e.hasEastAsianCmap ? { eastAsianLineHeightRatio: r.lineHeightRatio } : {}
	};
}
var or = .27;
function sr(e, t = {
	externalLeading: !0,
	msWordGridMetrics: !1
}, n = !1) {
	let r = e.normalDescentRatio + (t.externalLeading ? Math.max(0, e.normalLineGapRatio) : 0), i = e.normalAscentRatio + r, a = t.msWordGridMetrics && n ? i * or : 0;
	return Object.freeze({
		lineHeightRatio: i + a,
		designAscentRatio: e.normalAscentRatio + a,
		designDescentRatio: r
	});
}
function cr(e, t, n = "disables") {
	return t != null && e >= t && (t > 0 || n === "size-comparison");
}
function lr(e) {
	return /\p{Script=Arabic}/u.test(e) && !/[^\p{Script=Arabic}\p{Script=Common}\p{Script=Inherited}]/u.test(e);
}
function ur(e, t) {
	return !(t > 0) || !Number.isFinite(e) ? 1 : Math.max(1, Math.ceil(Math.max(0, e) / t - 1e-9));
}
function dr(e) {
	return !e;
}
function fr(e, t) {
	if (!(t > 0) || !Number.isFinite(e) || e <= 0) return 0;
	let n = (e % t + t) % t, r = 1e-9;
	return n <= r || t - n <= r ? 0 : n;
}
function pr(e) {
	return e !== "bar" && e !== "clear";
}
function mr(e) {
	let { ordinaryAdvancePx: t, allocatedGridAdvancePx: n, atLeastZeroAdvancePx: r, lineSpacing: i, gridAllocationActive: a, scale: o } = e;
	return a ? i?.rule === "atLeast" && i.value < 0 ? Math.abs(i.value) * o : i?.rule === "atLeast" && i.value === 0 ? r : i?.rule === "exact" ? t : Math.max(t, n) : t;
}
function hr(e, t, n, r, i = 0) {
	let a = !t.kashidaLineFitMode15 && i < 0 ? 0 : e === "mediumKashida" ? .1 : e === "highKashida" ? .2 : 0, o = _r(n, r);
	if (!(a === 0 && !o)) return t.kashidaLineFitMode15 ? {
		fraction: 1 - a,
		reserveShare: 0,
		rtlVisiblePrefix: o
	} : {
		fraction: 1,
		reserveShare: a,
		rtlVisiblePrefix: o
	};
}
function gr(e, t, n, r, i) {
	if (!t.kashidaLineFitMode15 || !n || !r || e.alignment !== "mediumKashida" && e.alignment !== "highKashida" || !i || e.numbering !== null && e.numbering !== void 0 || e.runs.length !== 1 || e.complexFieldBoundaries !== void 0) return !1;
	let a = e.runs[0];
	return a.type !== "text" || a.rtl === !0 || a.cs === !0 || a.ruby || a.noteRef || a.fitTextVal !== void 0 || "optionalHyphen" in a && a.optionalHyphen || "noteSeparatorCharacter" in a && a.noteSeparatorCharacter || /[\t\r\n\u00ad\ufffc]/u.test(a.text) ? !1 : /(?=\p{Script=Arabic})\p{Letter}/u.test(a.text);
}
function _r(e, t) {
	return e && t;
}
function vr(e) {
	return e === "lowKashida" || e === "mediumKashida" || e === "highKashida" || e === "thaiDistribute";
}
function yr(e, t) {
	return !e && t;
}
function br(e, t, n) {
	return e - (n ? 0 : t);
}
function xr(e, t) {
	return (e === "both" || e === "justify" || e === "distribute" || e === "lowKashida") && t.justifiedInterwordCompression;
}
function Sr(e, t) {
	return e > t / 4;
}
function Cr(e) {
	let { overflow: t, naturalGapSum: n, previousOpportunitySum: r, expansionWithoutCandidate: i, candidateLineEndSeparator: a } = e;
	if (!(!(t > 0) || !(n > 0) || !(r > 0) || Sr(t, n))) return t / (n + a) <= .5 * i / r ? t / n : void 0;
}
function wr(e) {
	return Number.isInteger(e) && e >= 2;
}
function Tr(e) {
	return e !== "snapToChars";
}
function Er(e, t) {
	return e.latinInterwordXavgFloor === "always" || e.latinInterwordXavgFloor === "without-explicit-kerning" && !t;
}
function Dr(e) {
	return e / 4;
}
function Or(e) {
	return e / 2;
}
function kr(e) {
	return e * 2;
}
function Ar(e, t) {
	return e.compressedSpaceLineFitMode && (t === "compressPunctuation" || t === "compressPunctuationAndJapaneseKana");
}
function jr(e, t) {
	return Math.min(e * t / 2, e / 4);
}
function Mr(e, t) {
	return e ? t / 2 : void 0;
}
function Nr(e, t) {
	return e && t === 1 ? 1 : 0;
}
function Pr(e, t) {
	if (t !== "complexScript") return e.length > 0 && [...e].every((e) => e === " " || e === "　") ? .5 : t === "eastAsia" ? 1 : [...e].every((e) => (e.codePointAt(0) ?? 128) <= 127) ? .5 : void 0;
}
function Fr(e) {
	let t = Math.max(0, e.punctuationAdvancePt), n = Math.max(0, e.ideographicCellAdvancePt);
	return t < n ? t : Math.min(t, Math.max(0, e.punctuationInkEndPt, n / 2));
}
function Ir(e) {
	return e === void 0 || e <= 0;
}
function Lr(e, t) {
	return e.endsWith(" ") && t.startsWith(" ");
}
var Rr = {
	ja: new Set([...",.’”、。」』】），．］｝｡､"]),
	zhHans: new Set([..."!%),.:;>?]}¢°·ˇ’”‰′″℃∶、。〃〉》」』】〗〕〞﹚﹜﹞！＂％＇），．：；？］｝￠"]),
	zhHant: new Set([..."!),.:;?]}’”′、。〉》」』】〕〞﹚﹜﹞！），．：；？］｝"]),
	ko: new Set([..."!%),.:;?]}¢°’”′″℃〉》」』】〕！％），．：；？］｝￠"])
}, zr = new Set([
	...Rr.ja,
	...Rr.zhHans,
	...Rr.zhHant,
	...Rr.ko
]), Br = new Set([".", ","]);
function Vr(e, t, n = !1, r = !1, i = "earlier", a = !0, o = !1) {
	if (t) {
		if (o && r && a) {
			if (i === "mode15") return "none";
			if (i === "earlier" && (e === "left" || e === "both" || e === "justify" || e === "distribute")) return "one-from-fitting-prefix";
		}
		if (a && !r && i !== "unmeasured" && (e === "left" || e === "start" || e === "center" || e === "right" || e === "end")) return n || i === "mode15" ? "none" : "one";
		switch (e) {
			case "lowKashida":
			case "mediumKashida":
			case "highKashida":
			case "thaiDistribute": return "none";
			case "left":
			case "start":
			case "both":
			case "justify":
			case "distribute": return n ? "none" : "one";
			default: return;
		}
	}
}
function Hr(e, t, n, r, i) {
	if (e === void 0 || i || !C(t.codePointAt(0))) return !1;
	if (e === "none") return !0;
	if (!r.enabled) return !1;
	let a = n();
	return a !== void 0 && r.lineStartForbidden.has(a.codePointAt(0));
}
var Ur = new Set([
	"ar",
	"fa",
	"ur",
	"he",
	"iw",
	"yi",
	"ji",
	"ps",
	"sd",
	"ug",
	"dv",
	"syr",
	"ckb"
]);
function Wr(e, t, n = !1, r = !1, i = !1, a) {
	let o = t?.toLowerCase();
	if (o?.startsWith("ja")) return Rr.ja.has(e);
	if (o?.startsWith("ko")) return Rr.ko.has(e);
	if (o?.startsWith("zh")) return (/(?:^|-)(?:tw|hk|mo)(?:-|$)|hant/u.test(o) ? Rr.zhHant : Rr.zhHans).has(e);
	let s = a?.split("-")[0].toLowerCase(), c = s != null && Ur.has(s);
	return n || i && !c ? zr.has(e) : r && Br.has(e);
}
function Gr(e) {
	return e.compat.numberingSpaceSuffixArialMode && e.leftToRight && e.markerWeight <= 400 && e.markerStyle === "normal" && !e.complexScriptMarker && !e.symbolMarker;
}
function Kr(e, t) {
	return t.alignment === "num" && Math.abs(t.pos - e) <= 1e-6;
}
function qr(e, t, n) {
	let r = /^[A-Za-z][A-Za-z0-9+.-]*:\/\//u.exec(e);
	if (!r) return [];
	let i = r[0].length, a = e.slice(i).search(/[/?#]/u), o = a < 0 ? e.length : i + a, s = [];
	for (let r = o; r < e.length; r += 1) {
		let i = e[r], a = r + 1;
		(i === "/" && r > o || i === "-" || i === "?" || i === "&") && t.has(a) && !n.has(a) && s.push(a);
	}
	return s;
}
function Jr(e, t) {
	return t === 0 ? e : e - t / 2;
}
function Yr(e, t) {
	return e === "super" ? t * .35 : e === "sub" ? -t * .15 : 0;
}
var Xr = Te;
function Zr(e, t) {
	return e.inlinePictureAutoLeading && !t.numbering && !t.framePr && t.lineSpacing?.rule === "auto" && t.lineSpacing.value > 1 && t.runs.length > 0 && t.runs.every((e) => e.type === "image" && e.anchor !== !0 || e.type === "shape" && e.inline === !0);
}
function Qr(e, t, n) {
	return e + t * (n - 1);
}
function $r(e) {
	return we(e);
}
function ei(e, t) {
	return t > 0 ? Math.max(1, Math.ceil(e / t)) : 1;
}
function ti(e, t) {
	return e > 0 ? e : t * Xr;
}
function ni(e, t, n) {
	return Math.max(e, t * n);
}
function ri(e, t, n) {
	return Math.max(e, t, n);
}
function ii(e, t) {
	return (e === "exact" || e === "auto") && t <= 0;
}
function ai(e, t, n) {
	return Math.max(e, n > 0 ? Math.max(1, Math.ceil(n / t)) * t : t);
}
function oi(e) {
	if (e.rule === "exact") return {
		advancePt: e.value,
		baselineOffsetPt: e.value * 4 / 5
	};
	let t = e.pitchPt !== null && e.pitchPt > 0 ? Math.ceil(e.singlePt / e.pitchPt) * e.pitchPt : e.singlePt, n = e.rule === "atLeast" ? Math.max(e.value, t) : t;
	return {
		advancePt: n,
		baselineOffsetPt: n - (t - e.singlePt) / 2 - e.descentPt
	};
}
function si(e, t) {
	return !t && !e.isLastLine ? "word" : !t && e.endsAtHardBreak === !0 && e.alignment !== "distribute" ? e.lineEndJustificationBeforeMode15 === !0 ? "word" : null : e.alignment === "distribute" || e.alignment === void 0 && e.stretchLastLine ? e.lineEndJustificationBeforeMode15 === !0 ? "character" : "word-or-centre" : !t || e.doNotExpandShiftReturn === !0 ? null : e.alignment === "thaiDistribute" && e.lineEndJustificationBeforeMode15 !== !0 ? "character" : "word";
}
function ci(e) {
	return `font-source:${h(e)}`;
}
function li(e) {
	return `app-face:${h(e)}`;
}
function ui(e) {
	if (e.farEastCodePage != null) return $r({
		...e,
		farEastCodePage: e.farEastCodePage
	}) ?? void 0;
}
function di(e) {
	let t = [];
	for (let [n, r] of [...e].sort((e, t) => e[0] - t[0])) {
		let e = t[t.length - 1];
		e && n <= e[1] + 1 ? e[1] = Math.max(e[1], r) : t.push([n, r]);
	}
	return t;
}
var fi = (e) => Object.freeze(di(e).map((e) => Object.freeze(e))), pi = (e) => e.trim().replace(/^(['"])(.*)\1$/, "$2");
function mi(e, t, n) {
	if (!t || j(e).some((e) => e.farEastCodePage !== !1)) return;
	let r = t.ascentRatio + t.lineGapRatio, i = t.descentRatio;
	if (Number.isFinite(r) && Number.isFinite(i) && r >= 0 && i >= 0 && r + i > 0) return {
		requiresGlyphCoverage: !0,
		nativeRoutePrimaryFamily: c(n.ownershipFamily),
		lineHeightRatio: r + i,
		designAscentRatio: r,
		designDescentRatio: i,
		lineGapRatio: t.lineGapRatio,
		normalAscentRatio: t.ascentRatio,
		normalDescentRatio: t.descentRatio,
		normalLineGapRatio: t.lineGapRatio
	};
}
function hi(e, t, n = Yn, r = !1) {
	let i = e?.loaded.faces.length ? e.lineMetrics(e.loaded, n, r) : Object.create(null), a = /* @__PURE__ */ new Set();
	for (let t of e?.loaded.faces ?? []) {
		let e = h(t.family);
		e && a.add(e);
	}
	for (let [e, r] of n.familyLines) {
		if (a.has(e)) continue;
		let n = r.ownershipFamily, o = li(n), s = Ce((t && typeof t[Symbol.iterator] == "function" ? [...t].find((t) => h(pi(t.family)) === e) : void 0)?.unicodeRange) ?? [[0, 1114111]];
		for (let { weight: e, style: t } of In) {
			let a = mi(n, r.lines[Ln(e, t)], r);
			a && (i[`${o}\u0000${e}\u0000${t}`] = Object.freeze({
				family: n,
				weight: e,
				style: t,
				sourceIdentity: o,
				synthesized: !1,
				...a,
				unicodeRanges: fi(s)
			}));
		}
	}
	return i;
}
function gi(e) {
	let { text: t, rtl: n } = e;
	return typeof t == "string" ? n === !0 ? "rtl" : "ltr" : void 0;
}
var _i = a;
function vi(e, t) {
	return e === t;
}
function yi(e) {
	return e !== null;
}
var bi = Object.freeze({
	isTab: (e) => "isTab" in e,
	isRtlMarked: (e) => e.rtl === !0,
	digitsAsAN: (e) => e.digitsAsAN === !0,
	isRtlAmbiguous: _i,
	preserveRtlNumericCS: !0,
	directionFromAnyOdd: !0
});
function xi(e) {
	return e.characterSpreadBidi || e.alignment === "distribute" || !e.baseRtl || e.runDirectionUnauthored ? "line-level" : "word";
}
var Si = (e) => ie(e, bi), Ci = Object.freeze({
	...bi,
	isolateDirection: gi,
	isolateRequiresUniformSlices: !0
}), wi = (e, t) => se(e, t, Ci), Ti = (e) => e === "word" ? Ci : bi, Ei = (e, t, n = "line-level") => ue(e, t, Ti(n)), Di = (e, t, n, r) => ce(e, t, n, n ? Ci : bi, r === "word" ? Ci : bi), Oi = (e) => {
	let t = e.text;
	return typeof t == "string" ? t : void 0;
}, ki = () => {
	let e = f();
	return {
		engine: e,
		compute: e.computeLevels,
		reorder: e.reorderVisual,
		token: n()
	};
}, Ai = (e, t) => e.engine === t.engine && e.token === t.token && e.compute === t.compute && e.reorder === t.reorder;
function ji() {
	let e;
	return (t, n, r = "line-level") => {
		let i = ki(), a = Ti(r);
		if (e && e.baseRtl === n && e.model === r && Ai(e.engine, i) && e.facts.length === t.length && e.facts.every((e, n) => {
			let r = t[n];
			return e.text === Oi(r) && e.tab === (a.isTab?.(r) === !0) && e.rtl === (a.isRtlMarked?.(r) === !0) && e.digits === (a.digitsAsAN?.(r) === !0) && e.isolate === a.isolateDirection?.(r);
		})) return e.visual;
		e = void 0;
		let o = t.map((e) => ({
			text: Oi(e),
			tab: a.isTab?.(e) === !0,
			rtl: a.isRtlMarked?.(e) === !0,
			digits: a.digitsAsAN?.(e) === !0,
			isolate: a.isolateDirection?.(e)
		})), s = fe(t, n, a) ?? Ei(t, n, r), c = Object.freeze({
			order: Object.freeze([...s.order]),
			rtl: Object.freeze([...s.rtl])
		});
		return e = Ai(i, ki()) ? Object.freeze({
			baseRtl: n,
			model: r,
			engine: i,
			facts: o,
			visual: c
		}) : void 0, c;
	};
}
function Mi(e, t) {
	switch (e) {
		case "center": return "center";
		case "both":
		case "justify":
		case "distribute":
		case "lowKashida":
		case "mediumKashida":
		case "highKashida":
		case "thaiDistribute": return "justify";
		case "end":
		case "right": return t ? "left" : "right";
		case "start":
		case "left":
		case void 0:
		default: return t ? "right" : "left";
	}
}
function Ni(e) {
	switch (e) {
		case "both":
		case "justify":
		case "distribute":
		case "lowKashida":
		case "mediumKashida":
		case "highKashida":
		case "thaiDistribute": return !0;
		default: return !1;
	}
}
function Pi(e) {
	return e === "distribute";
}
function Fi(e) {
	return e < 0n ? -e : e;
}
function Ii(e, t) {
	let n = Fi(e), r = Fi(t);
	for (; r !== 0n;) {
		let e = n % r;
		n = r, r = e;
	}
	return n;
}
function Li(e, t) {
	if (t === 0n) throw Error("Exact rational denominator must be nonzero");
	if (e === 0n) return Object.freeze({
		numerator: 0n,
		denominator: 1n
	});
	let n = t < 0n ? -1n : 1n, r = Ii(e, t);
	return Object.freeze({
		numerator: n * e / r,
		denominator: n * t / r
	});
}
function G(e, t) {
	let n = e.numerator * t.denominator - t.numerator * e.denominator;
	return n < 0n ? -1 : +(n > 0n);
}
function Ri(e, t) {
	return Li(e.numerator * t.denominator + t.numerator * e.denominator, e.denominator * t.denominator);
}
function zi(e, t) {
	return Li(e.numerator * t.denominator - t.numerator * e.denominator, e.denominator * t.denominator);
}
function Bi(e, t) {
	return Li(e.numerator * t.denominator + t.numerator * e.denominator, 2n * e.denominator * t.denominator);
}
function Vi(e) {
	return `${e.numerator}/${e.denominator}`;
}
var Hi = /* @__PURE__ */ new DataView(/* @__PURE__ */ new ArrayBuffer(8));
function Ui(e) {
	if (!Number.isFinite(e)) throw Error("Exact geometry requires a finite binary64 value");
	if (e === 0) return Object.freeze({
		coefficient: 0n,
		exponent: 0
	});
	Hi.setFloat64(0, e, !1);
	let t = Hi.getBigUint64(0, !1), n = t >> 63n != 0n, r = Number(t >> 52n & 2047n), i = t & (1n << 52n) - 1n, a = r === 0 ? i : 1n << 52n | i, o = r === 0 ? -1074 : r - 1023 - 52;
	for (; (a & 1n) == 0n;) a >>= 1n, o += 1;
	return Object.freeze({
		coefficient: n ? -a : a,
		exponent: o
	});
}
function Wi(e) {
	let t = Ui(e);
	return t.exponent >= 0 ? Li(t.coefficient << BigInt(t.exponent), 1n) : Li(t.coefficient, 1n << BigInt(-t.exponent));
}
function Gi(e) {
	return e === 0n ? 0 : e.toString(2).length;
}
function Ki(e, t, n) {
	let r = n >= 0 ? e : e << BigInt(-n), i = n >= 0 ? t << BigInt(n) : t;
	return r < i ? -1 : +(r > i);
}
function qi(e, t, n) {
	let r = n >= 0 ? e << BigInt(n) : e, i = n >= 0 ? t : t << BigInt(-n), a = r / i, o = r % i * 2n;
	return (o > i || o === i && (a & 1n) != 0n) && (a += 1n), a;
}
function Ji(e) {
	return Hi.setBigUint64(0, e, !1), Hi.getFloat64(0, !1);
}
function Yi(e) {
	if (e.numerator === 0n) return 0;
	let t = e.numerator < 0n, n = Fi(e.numerator), r = e.denominator, i = Gi(n) - Gi(r);
	Ki(n, r, i) < 0 && --i;
	let a = t ? 1n << 63n : 0n;
	if (i < -1022) {
		let e = qi(n, r, 1074);
		return Ji(e === 0n ? a : e >= 1n << 52n ? a | 1n << 52n : a | e);
	}
	let o = qi(n, r, 52 - i);
	if (o === 1n << 53n && (o >>= 1n, i += 1), i > 1023) return t ? -Infinity : Infinity;
	let s = BigInt(i + 1023) << 52n, c = o - (1n << 52n);
	return Ji(a | s | c);
}
function Xi(e) {
	if (e === Infinity) return e;
	if (Object.is(e, -0) || e === 0) return Number.MIN_VALUE;
	Hi.setFloat64(0, e, !1);
	let t = Hi.getBigUint64(0, !1);
	return Ji(e > 0 ? t + 1n : t - 1n);
}
function Zi(e) {
	let t = Yi(e);
	if (t === Infinity) return t;
	if (t === -Infinity) return -Number.MAX_VALUE;
	let n = Ui(t);
	return G(n.exponent >= 0 ? {
		numerator: n.coefficient << BigInt(n.exponent),
		denominator: 1n
	} : {
		numerator: n.coefficient,
		denominator: 1n << BigInt(-n.exponent)
	}, e) >= 0 ? t : Xi(t);
}
function Qi(e) {
	return -Zi({
		numerator: -e.numerator,
		denominator: e.denominator
	});
}
function $i(e) {
	if (!e.points || e.points.length < 3 || e.points.some((e) => !Number.isFinite(e.xPt) || !Number.isFinite(e.yPt))) throw Error(`Invalid ${e.kind} wrapPolygon for ${e.imageKey}`);
	if (![
		e.xLeftPt,
		e.xRightPt,
		e.yTopPt,
		e.yBottomPt
	].every(Number.isFinite) || e.xRightPt < e.xLeftPt || e.yBottomPt < e.yTopPt) throw Error(`Invalid finite wrap bounds for ${e.imageKey}`);
}
var ea = /* @__PURE__ */ new WeakMap();
function ta(e, t) {
	return e.x === t.x && e.y === t.y;
}
function na(e, t, n, r) {
	return e * r - t * n;
}
function ra(e, t) {
	return t > 0n ? e >= 0n && e <= t : e <= 0n && e >= t;
}
function ia(e, t) {
	let n = ta(e.from, t.from) || ta(e.from, t.to) ? e.from : ta(e.to, t.from) || ta(e.to, t.to) ? e.to : null;
	if (n) return Object.freeze({
		y: Li(n.y, 1n),
		contact: "shared-endpoint"
	});
	let r = e.to.x - e.from.x, i = e.to.y - e.from.y, a = t.to.x - t.from.x, o = t.to.y - t.from.y, s = na(r, i, a, o);
	if (s === 0n) return null;
	let c = t.from.x - e.from.x, l = t.from.y - e.from.y, u = na(c, l, a, o), d = na(c, l, r, i);
	return !ra(u, s) || !ra(d, s) ? null : Object.freeze({
		y: Li(e.from.y * s + i * u, s),
		contact: i === 0n || o === 0n ? "horizontal" : "active-crossing"
	});
}
function aa(e, t) {
	return `${e}:${t}`;
}
function oa(e, t, n) {
	let r = /* @__PURE__ */ new Set();
	for (let i of t) {
		if (i < 0 || i >= Math.floor(e.length / 2)) continue;
		n();
		let t = e[i * 2], a = e[i * 2 + 1];
		r.add(aa(t, a));
	}
	return r;
}
function sa(e) {
	let t = (e) => {
		if (e.length === 0) return null;
		let n = e[Math.floor(e.length / 2)].yTopPt, r = [], i = [], a = [];
		for (let t of e) t.yBottomPt <= n ? r.push(t) : t.yTopPt > n ? i.push(t) : a.push(t);
		return Object.freeze({
			centerYPt: n,
			crossingByTop: Object.freeze(a),
			crossingByBottom: Object.freeze(a.slice().sort((e, t) => t.yBottomPt - e.yBottomPt)),
			below: t(r),
			above: t(i)
		});
	};
	return t(e.slice().sort((e, t) => e.yTopPt - t.yTopPt || e.yBottomPt - t.yBottomPt));
}
function ca(e, t) {
	return Yi(t >= 0 ? {
		numerator: e.numerator << BigInt(t),
		denominator: e.denominator
	} : {
		numerator: e.numerator,
		denominator: e.denominator << BigInt(-t)
	});
}
function la(e, t) {
	return Zi(t >= 0 ? {
		numerator: e.numerator << BigInt(t),
		denominator: e.denominator
	} : {
		numerator: e.numerator,
		denominator: e.denominator << BigInt(-t)
	});
}
function ua(e, t) {
	let n = Ui(e), r = n.exponent - t;
	return r >= 0 ? {
		numerator: n.coefficient << BigInt(r),
		denominator: 1n
	} : {
		numerator: n.coefficient,
		denominator: 1n << BigInt(-r)
	};
}
function da(e, t, n) {
	let r = e.dx * n.numerator - e.c * n.denominator, i = t.dx * n.numerator - t.c * n.denominator, a = r * t.dy - i * e.dy;
	return a < 0n ? -1 : +(a > 0n);
}
function fa(e) {
	let t = (e) => {
		if (e.length === 0) return null;
		let n = e[Math.floor(e.length / 2)].yTop, r = [], i = [], a = [];
		for (let t of e) G(t.yBottom, n) <= 0 ? r.push(t) : G(t.yTop, n) > 0 ? i.push(t) : a.push(t);
		return Object.freeze({
			centerY: n,
			crossingByTop: Object.freeze(a),
			crossingByBottom: Object.freeze(a.slice().sort((e, t) => G(t.yBottom, e.yBottom))),
			below: t(r),
			above: t(i)
		});
	};
	return t(e.slice().sort((e, t) => G(e.yTop, t.yTop) || G(e.yBottom, t.yBottom)));
}
function pa(e, t, n, r) {
	if (!(!e || G(n, t) <= 0)) {
		if (G(n, e.centerY) <= 0) {
			for (let t of e.crossingByTop) {
				if (G(t.yTop, n) >= 0) break;
				r.push(t);
			}
			pa(e.below, t, n, r);
			return;
		}
		if (G(t, e.centerY) >= 0) {
			for (let n of e.crossingByBottom) {
				if (G(n.yBottom, t) <= 0) break;
				r.push(n);
			}
			pa(e.above, t, n, r);
			return;
		}
		r.push(...e.crossingByTop), pa(e.below, t, n, r), pa(e.above, t, n, r);
	}
}
function ma(e, t, n, r, i) {
	let a = /* @__PURE__ */ new Map(), o = /* @__PURE__ */ new Map();
	t.forEach((e, t) => {
		if (e.minY === e.maxY) return;
		let n = Vi(Li(e.minY, 1n)), r = Vi(Li(e.maxY, 1n)), i = a.get(n);
		i ? i.push(t) : a.set(n, [t]);
		let s = o.get(r);
		s ? s.push(t) : o.set(r, [t]);
	});
	let s = /* @__PURE__ */ new Map();
	for (let e of i) {
		if (e.contact !== "active-crossing") continue;
		let t = Vi(e.y), n = s.get(t);
		n || s.set(t, n = /* @__PURE__ */ new Set()), n.add(e.leftEdge), n.add(e.rightEdge);
	}
	let c = [], l = /* @__PURE__ */ new Set(), u = /* @__PURE__ */ new Map(), d = [], f = [], p = 0, m = 0, h = (t, n, i) => {
		for (let a of t) {
			if (n.has(a)) continue;
			let t = u.get(a);
			if (t && G(i, t.yTop) > 0) {
				let n = Object.freeze({
					yTop: t.yTop,
					yBottom: i,
					leftEdge: t.leftEdge,
					rightEdge: t.rightEdge
				});
				d.push(n);
				let a = ca(t.yTop, r), o = ca(i, r);
				o > a && f.push(Object.freeze({
					yTopPt: a,
					yBottomPt: o,
					left: e[t.leftEdge],
					right: e[t.rightEdge]
				}));
			}
			u.delete(a);
		}
		for (let e of n) {
			if (t.has(e)) continue;
			let n = e.indexOf(":");
			u.set(e, {
				leftEdge: Number(e.slice(0, n)),
				rightEdge: Number(e.slice(n + 1)),
				yTop: i
			});
		}
	}, g = /* @__PURE__ */ new Map(), _ = (e, t) => {
		e.add(Math.floor((t - 1) / 2)), e.add(Math.floor(t / 2)), e.add(Math.floor((t + 1) / 2));
	}, v = (e) => oa(c, e, () => {
		m += 2;
	}), y = () => {
		let e = /* @__PURE__ */ new Set();
		for (let t = 0; t + 1 < c.length; t += 2) m += 2, e.add(aa(c[t], c[t + 1]));
		return e;
	};
	for (let e = 0; e < n.length; e += 1) {
		let r = n[e], i = n[e + 1], u = i ? Bi(r, i) : r, d = (e, n) => (p += 1, da(t[e], t[n], u) || e - n), f = (e) => {
			let t = 0, n = c.length;
			for (; t < n;) {
				let r = t + n >>> 1;
				d(c[r], e) <= 0 ? t = r + 1 : n = r;
			}
			c.splice(t, 0, e);
			for (let e = t; e < c.length; e += 1) g.set(c[e], e);
		}, m = (e) => {
			let t = g.get(e);
			if (t !== void 0) {
				c.splice(t, 1), g.delete(e);
				for (let e = t; e < c.length; e += 1) g.set(c[e], e);
			}
		}, b = (e) => {
			let n = [...e].filter((e) => g.has(e) && G(Li(t[e].minY, 1n), r) <= 0 && G(r, Li(t[e].maxY, 1n)) < 0), i = n.map((e) => g.get(e)).sort((e, t) => e - t);
			n.sort(d);
			for (let e = 0; e < i.length; e += 1) {
				let t = i[e], r = n[e];
				c[t] = r, g.set(r, t);
			}
		}, x = Vi(r), S = o.get(x) ?? [], C = a.get(x) ?? [], w = s.get(x) ?? l;
		if (S.length === 0 && C.length === 0 && (w.size === 0 || i === void 0)) continue;
		let T = S.length > 0 || C.length > 0, E = /* @__PURE__ */ new Set();
		if (!T) for (let e of w) {
			let t = g.get(e);
			t !== void 0 && _(E, t);
		}
		let D = T ? y() : v(E);
		for (let e of S) m(e);
		for (let e of C) f(e);
		if (w.size > 0 && i !== void 0 && b(w), c.length % 2 != 0) throw Error("Compiled wrapPolygon produced an odd open-slab crossing count");
		if (T) h(D, y(), r);
		else {
			let e = /* @__PURE__ */ new Set();
			for (let t of w) {
				let n = g.get(t);
				n !== void 0 && _(e, n);
			}
			h(D, v(e), r);
		}
	}
	return Object.freeze({
		spans: Object.freeze(f),
		exactSpans: Object.freeze(d),
		orderComparisonCount: p,
		pairMembershipVisitCount: m
	});
}
function ha(e) {
	$i(e);
	let t = e.points, n = Object.freeze(t.map((e) => Object.freeze({ ...e }))), r = [
		...n.flatMap((e) => [e.xPt, e.yPt]),
		e.xLeftPt,
		e.xRightPt,
		e.yTopPt,
		e.yBottomPt
	].map(Ui).filter(({ coefficient: e }) => e !== 0n), i = r.length === 0 ? 0 : Math.min(...r.map(({ exponent: e }) => e)), a = (e) => {
		let t = Ui(e);
		return t.coefficient === 0n ? 0n : t.coefficient << BigInt(t.exponent - i);
	}, o = n.map((e) => Object.freeze({
		x: a(e.xPt),
		y: a(e.yPt)
	})), s = n.map((e, t) => {
		let r = n[(t + 1) % n.length], i = r.yPt - e.yPt, a = i === 0 ? 0 : (r.xPt - e.xPt) / i;
		return Object.freeze({
			from: e,
			to: r,
			minYPt: Math.min(e.yPt, r.yPt),
			maxYPt: Math.max(e.yPt, r.yPt),
			slopeXPerY: a,
			interceptX: i === 0 ? e.xPt : e.xPt - a * e.yPt
		});
	}), c = o.map((e, t) => {
		let n = o[(t + 1) % o.length], r = e.y <= n.y ? e : n, i = e.y <= n.y ? n : e, a = i.x - r.x, s = i.y - r.y;
		return Object.freeze({
			index: t,
			from: e,
			to: n,
			minY: r.y,
			maxY: i.y,
			dx: a,
			dy: s,
			c: a * r.y - s * r.x
		});
	}), l = [];
	for (let e = 0; e < c.length; e += 1) for (let t = e + 1; t < c.length; t += 1) {
		let n = ia(c[e], c[t]);
		n && l.push(Object.freeze({
			y: n.y,
			contact: n.contact,
			leftEdge: e,
			rightEdge: t
		}));
	}
	let u = Infinity, d = -Infinity, f = Infinity, p = -Infinity;
	for (let e of n) u = Math.min(u, e.xPt), d = Math.max(d, e.xPt), f = Math.min(f, e.yPt), p = Math.max(p, e.yPt);
	let m = /* @__PURE__ */ new Map();
	for (let e of o) {
		let t = Li(e.y, 1n);
		m.set(Vi(t), t);
	}
	for (let e of l) m.set(Vi(e.y), e.y);
	let h = Object.freeze([...m.values()].sort(G)), g = Object.freeze([...new Set(h.map((e) => ca(e, i)))].sort((e, t) => e - t)), _ = ma(s, c, h, i, l), v = Li(o.reduce((e, t) => t.x < e ? t.x : e, o[0].x), 1n), y = Li(o.reduce((e, t) => t.x > e ? t.x : e, o[0].x), 1n), b = Li(o.reduce((e, t) => t.y < e ? t.y : e, o[0].y), 1n), x = Li(o.reduce((e, t) => t.y > e ? t.y : e, o[0].y), 1n), S = Li(0n, 1n), C = (e, t) => {
		let n = zi(e, t);
		return G(n, S) > 0 ? n : S;
	}, w = Object.freeze({
		scaleExponent: i,
		edges: Object.freeze(c),
		eventYs: h,
		spans: _.exactSpans,
		spanIndex: fa(_.exactSpans),
		polygonLeft: v,
		polygonRight: y,
		polygonTop: b,
		polygonBottom: x,
		padLeft: C(v, Li(a(e.xLeftPt), 1n)),
		padRight: C(Li(a(e.xRightPt), 1n), y),
		padTop: C(b, Li(a(e.yTopPt), 1n)),
		padBottom: C(Li(a(e.yBottomPt), 1n), x)
	}), T = Object.freeze({
		kind: e.kind,
		edges: Object.freeze(s),
		eventYPts: g,
		contourSpans: _.spans,
		contourSpanIndex: sa(_.spans),
		intersectionCount: l.length,
		compileOrderComparisonCount: _.orderComparisonCount,
		compilePairMembershipVisitCount: _.pairMembershipVisitCount,
		polygonLeftPt: u,
		polygonRightPt: d,
		polygonTopPt: f,
		polygonBottomPt: p,
		padLeftPt: Math.max(0, u - e.xLeftPt),
		padRightPt: Math.max(0, e.xRightPt - d),
		padTopPt: Math.max(0, f - e.yTopPt),
		padBottomPt: Math.max(0, e.yBottomPt - p)
	});
	return ea.set(T, w), T;
}
function ga(e, t) {
	return {
		numerator: e.dx * t.numerator - e.c * t.denominator,
		denominator: e.dy * t.denominator
	};
}
function _a(e, t) {
	return e.dx * t.dy === t.dx * e.dy && e.c * t.dy === t.c * e.dy;
}
function va(e) {
	let t = e.filter((e) => G(e.r, e.l) > 0).slice().sort((e, t) => G(e.l, t.l) || G(e.r, t.r)), n = [];
	for (let e of t) {
		let t = n.at(-1);
		!t || G(e.l, t.r) > 0 ? n.push({ ...e }) : G(e.r, t.r) > 0 && (n[n.length - 1] = {
			l: t.l,
			r: e.r
		});
	}
	return n;
}
function ya(e, t) {
	return {
		numerator: e.numerator * t.denominator + t.numerator * e.denominator,
		denominator: e.denominator * t.denominator
	};
}
function ba(e, t) {
	return {
		numerator: e.numerator * t.denominator - t.numerator * e.denominator,
		denominator: e.denominator * t.denominator
	};
}
function xa(e, t, n) {
	let r = ea.get(e);
	if (!r) throw Error("Compiled polygon omitted its exact geometry authority");
	let i = ba(t, r.padBottom), a = ya(n, r.padTop), o = G(r.polygonTop, i) >= 0 ? r.polygonTop : i, s = G(r.polygonBottom, a) <= 0 ? r.polygonBottom : a;
	if (G(s, o) <= 0) return [];
	let c = [], l = [];
	pa(r.spanIndex, o, s, l);
	for (let e of l) {
		let t = G(o, e.yTop) >= 0 ? o : e.yTop, n = G(s, e.yBottom) <= 0 ? s : e.yBottom;
		if (G(n, t) <= 0) continue;
		let i = r.edges[e.leftEdge], a = r.edges[e.rightEdge];
		if (_a(i, a)) continue;
		let l = ga(i, t), u = ga(i, n), d = ga(a, t), f = ga(a, n);
		c.push({
			l: ba(G(l, u) <= 0 ? l : u, r.padLeft),
			r: ya(G(d, f) >= 0 ? d : f, r.padRight)
		});
	}
	let u = va(c);
	return e.kind === "through" || u.length === 0 ? u : [{
		l: u[0].l,
		r: u.at(-1).r
	}];
}
function Sa(e, t, n) {
	let r = ea.get(e);
	if (!r) throw Error("Compiled polygon omitted its exact geometry authority");
	let i = ua(t, r.scaleExponent), a = ya(i, ua(n, r.scaleExponent)), o = (e) => r.scaleExponent >= 0 ? {
		numerator: e.numerator << BigInt(r.scaleExponent),
		denominator: e.denominator
	} : {
		numerator: e.numerator,
		denominator: e.denominator << BigInt(-r.scaleExponent)
	};
	return Object.freeze(xa(e, i, a).map((e) => Object.freeze({
		l: o(e.l),
		r: o(e.r)
	})));
}
function Ca(e, t) {
	let n = ea.get(e);
	if (!n) throw Error("Compiled polygon omitted its exact geometry authority");
	let r = ua(t, n.scaleExponent), i = /* @__PURE__ */ new Set();
	for (let e of n.eventYs) i.add(la(ya(e, n.padBottom), n.scaleExponent)), i.add(la(ba(ba(e, r), n.padTop), n.scaleExponent));
	return Object.freeze([...i].filter(Number.isFinite).sort((e, t) => e - t));
}
function wa(e, t, n, r) {
	let i = ea.get(e);
	if (!i) throw Error("Compiled polygon omitted its exact geometry authority");
	let a = Bi(ua(n, i.scaleExponent), ua(r, i.scaleExponent)), o = ua(t, i.scaleExponent), s = ba(a, i.padBottom), c = ya(o, i.padTop), l = ya(a, c), u = G(i.polygonTop, s) >= 0 ? i.polygonTop : s, d = G(i.polygonBottom, l) <= 0 ? i.polygonBottom : l, f = [], p = [];
	pa(i.spanIndex, u, d, p);
	for (let e of p) {
		let t = G(u, e.yTop) >= 0 ? u : e.yTop;
		if (G(G(d, e.yBottom) <= 0 ? d : e.yBottom, t) <= 0) continue;
		let n = i.edges[e.leftEdge], r = i.edges[e.rightEdge];
		if (_a(n, r)) continue;
		let a = G(s, e.yTop) > 0, o = G(l, e.yBottom) < 0, p = (e, t, n, r) => {
			let a = t ? n : r, o = {
				numerator: e.dx * a.numerator - e.c * a.denominator,
				denominator: e.dy * a.denominator
			};
			return {
				slope: t ? {
					numerator: e.dx,
					denominator: e.dy
				} : {
					numerator: 0n,
					denominator: 1n
				},
				intercept: i.scaleExponent >= 0 ? {
					numerator: o.numerator << BigInt(i.scaleExponent),
					denominator: o.denominator
				} : {
					numerator: o.numerator,
					denominator: o.denominator << BigInt(-i.scaleExponent)
				}
			};
		}, m = p(n, a, {
			numerator: -i.padBottom.numerator,
			denominator: i.padBottom.denominator
		}, e.yTop), h = p(n, o, c, e.yBottom), g = p(r, a, {
			numerator: -i.padBottom.numerator,
			denominator: i.padBottom.denominator
		}, e.yTop), _ = p(r, o, c, e.yBottom), v = n.dx >= 0n ? m : h, y = r.dx >= 0n ? _ : g, b = Object.freeze({
			left: Object.freeze({
				slope: v.slope,
				intercept: ba(v.intercept, i.scaleExponent >= 0 ? {
					numerator: i.padLeft.numerator << BigInt(i.scaleExponent),
					denominator: i.padLeft.denominator
				} : {
					numerator: i.padLeft.numerator,
					denominator: i.padLeft.denominator << BigInt(-i.scaleExponent)
				})
			}),
			right: Object.freeze({
				slope: y.slope,
				intercept: ya(y.intercept, i.scaleExponent >= 0 ? {
					numerator: i.padRight.numerator << BigInt(i.scaleExponent),
					denominator: i.padRight.denominator
				} : {
					numerator: i.padRight.numerator,
					denominator: i.padRight.denominator << BigInt(-i.scaleExponent)
				})
			})
		});
		f.push(b);
	}
	return Object.freeze(f);
}
function Ta(e, t, n) {
	return e.left < t.right - n && e.right > t.left + n && e.top < t.bottom - n && e.bottom > t.top + n;
}
function Ea(e, t, n) {
	let r = e.right - e.left, i = e.bottom - e.top;
	if (r < 0 || i < 0) throw RangeError("Overlap rectangle has negative extent");
	let a = e.left, o = e.top;
	for (let e = 0; e <= t.length; e += 1) {
		let s = {
			left: a,
			right: a + r,
			top: o,
			bottom: o + i
		}, c = t.map((e) => ({
			left: e.left,
			right: e.right,
			top: e.top,
			bottom: e.bottom
		})).filter((e) => Ta(s, e, n.overlapEpsilon));
		if (c.length === 0) return Object.freeze({
			left: a,
			top: o
		});
		if (e === t.length) throw Error("Axis-aligned overlap resolution did not converge");
		let l = Math.max(...c.map((e) => e.right));
		if (l + r <= n.rightBoundary + n.rightBoundarySlack) {
			a = l;
			continue;
		}
		o = Math.max(...c.map((e) => e.bottom));
	}
	throw Error("Axis-aligned overlap resolution did not converge");
}
var Da = .01, Oa = .5;
function ka() {
	return Object.freeze({ kind: "none" });
}
function Aa(e) {
	return Object.freeze(e ? { kind: "none" } : { kind: "drawingml-normative" });
}
function ja() {
	return Object.freeze({ kind: "none" });
}
function Ma(e) {
	let t = {
		occurrenceId: e.occurrenceId,
		paragraphId: e.paragraphId,
		bounds: e.bounds,
		exclusionBounds: e.exclusionBounds
	};
	return e.kind === "table" ? {
		...t,
		kind: "table",
		tableOverlap: e.overlap
	} : e.kind === "frame" ? {
		...t,
		kind: "frame",
		...e.exclusionMode ? { exclusionMode: e.exclusionMode } : {}
	} : {
		...t,
		kind: "drawingml"
	};
}
function Na(e, t) {
	let n = e.imageX, r = e.imageY, i = e.imageW, a = e.imageH, o = e.xLeft, s = e.xRight, c = e.yTop, l = e.yBottom, u = {
		occurrenceId: e.anchorOccurrenceId ?? e.acquisitionOccurrenceId ?? `display-float:${t}`,
		paragraphId: e.paraId,
		bounds: {
			xPt: n,
			yPt: r,
			widthPt: i,
			heightPt: a
		},
		exclusionBounds: {
			xPt: o,
			yPt: c,
			widthPt: s - o,
			heightPt: l - c
		}
	};
	return e.kind === "table" ? {
		...u,
		kind: "table",
		tableOverlap: e.tableOverlap
	} : e.kind === "frame" ? {
		...u,
		kind: "frame",
		exclusionMode: e.mode
	} : {
		...u,
		kind: "drawingml"
	};
}
function Pa(e) {
	let t = e.xPt, n = e.yPt, r = e.widthPt, i = e.heightPt;
	return {
		left: t,
		right: t + r,
		top: n,
		bottom: n + i
	};
}
function Fa(e, t, n) {
	return t === 0 && n === 0 ? e : Object.freeze({
		xPt: e.xPt + t,
		yPt: e.yPt + n,
		widthPt: e.widthPt,
		heightPt: e.heightPt
	});
}
function Ia(e, t, n, r) {
	return Object.freeze({
		bounds: Fa(e.bounds, t, n),
		exclusionBounds: Fa(e.exclusionBounds, t, n),
		displacement: Object.freeze({
			xPt: t,
			yPt: n
		}),
		appliedCompatibilityRuleIds: Object.freeze([...r])
	});
}
function La(e, t, n = e.rightBoundaryPt) {
	let r = Pa(e.moving.bounds);
	return t.length === 0 ? Object.freeze({
		left: r.left,
		top: r.top
	}) : Ea(r, t, {
		overlapEpsilon: e.overlapEpsilonPt ?? 0,
		rightBoundary: n,
		rightBoundarySlack: e.rightBoundarySlackPt ?? 0
	});
}
function Ra(e) {
	let { moving: t, avoidance: n } = e, r = e.blockers.flatMap((e) => t.kind === "table" && e.kind === "table" && (t.tableOverlap === "never" || e.tableOverlap === "never") || n.kind === "drawingml-normative" && e.kind === "drawingml" ? [Pa(e.bounds)] : []), i = La(e, r), a = e.pageVerticalBoundsPt;
	if (t.kind === "table" && a && r.length > 0 && i.top + t.bounds.heightPt > a.bottomPt + (e.overlapEpsilonPt ?? 0)) {
		let n = za(Pa(t.bounds), r, e.overlapEpsilonPt ?? 0);
		return Ia(t, 0, (n !== null && n >= a.topPt - (e.overlapEpsilonPt ?? 0) ? n : t.bounds.yPt) - t.bounds.yPt, []);
	}
	return Ia(t, i.left - t.bounds.xPt, i.top - t.bounds.yPt, []);
}
function za(e, t, n) {
	let r = e.bottom - e.top, i = e.top;
	for (let a = 0; a <= t.length; a += 1) {
		let a = {
			...e,
			top: i,
			bottom: i + r
		}, o = t.filter((e) => Ta(a, e, n));
		if (o.length === 0) return i;
		i = Math.min(...o.map((e) => e.top)) - r;
	}
	return null;
}
function Ba(e, t) {
	let n = {
		startPt: t.inlineStartPt,
		endPt: t.inlineEndPt
	};
	switch (e.kind) {
		case "table": return n;
		case "frame": return (e.exclusionMode ?? "square") === "topAndBottom" ? {
			startPt: Math.min(t.flowBandStartPt, n.startPt),
			endPt: Math.max(t.flowBandEndPt, n.endPt)
		} : n;
		case "drawingml": return null;
	}
}
function Va(e) {
	if (e.inlineEndPt < e.inlineStartPt || e.flowBandEndPt < e.flowBandStartPt || e.blockExtentPt < 0) throw RangeError("Block-flow admission received a negative extent");
	let t = e.blockers.filter((t) => {
		let n = Ba(t, e);
		if (!n) return !1;
		let r = t.exclusionBounds;
		return n.endPt - r.xPt > e.overlapEpsilonPt && r.xPt + r.widthPt - n.startPt > e.overlapEpsilonPt;
	}), n = e.blockStartPt;
	for (let r = 0; r <= t.length; r += 1) {
		let i = t.filter((t) => {
			let r = t.exclusionBounds;
			return n + e.blockExtentPt - r.yPt > e.overlapEpsilonPt && r.yPt + r.heightPt - n > e.overlapEpsilonPt;
		});
		if (i.length === 0) return Object.freeze({ blockStartPt: n });
		if (r === t.length) throw Error("Block-flow float admission did not converge");
		n = Math.max(...i.map((e) => e.exclusionBounds.yPt + e.exclusionBounds.heightPt));
	}
	throw Error("Block-flow float admission did not converge");
}
function K(e) {
	let t = Ui(e);
	return t.exponent >= 0 ? {
		numerator: t.coefficient << BigInt(t.exponent),
		denominator: 1n
	} : {
		numerator: t.coefficient,
		denominator: 1n << BigInt(-t.exponent)
	};
}
function Ha(e, t) {
	return {
		numerator: e.numerator * t.denominator + t.numerator * e.denominator,
		denominator: e.denominator * t.denominator
	};
}
function Ua(e, t) {
	return {
		numerator: e.numerator * t.denominator - t.numerator * e.denominator,
		denominator: e.denominator * t.denominator
	};
}
function Wa(e, t) {
	return {
		numerator: e.numerator * t.numerator,
		denominator: e.denominator * t.denominator
	};
}
function Ga(e, t) {
	let n = t.numerator < 0n;
	return {
		numerator: (n ? -e.numerator : e.numerator) * t.denominator,
		denominator: e.denominator * (n ? -t.numerator : t.numerator)
	};
}
function Ka(e, t) {
	let n = K(e), r = K(t);
	return Yi({
		numerator: n.numerator * r.denominator + r.numerator * n.denominator,
		denominator: 2n * n.denominator * r.denominator
	});
}
function qa(e) {
	switch (e) {
		case "left":
		case "right":
		case "largest":
		case "bothSides": return e;
		default: return "bothSides";
	}
}
function Ja(e) {
	return e === "square" || e === "topAndBottom" || e === "tight" || e === "through";
}
function Ya(e, t, n) {
	return e.xRight > t + .01 && e.xLeft < n - .01;
}
var Xa = /* @__PURE__ */ new WeakMap(), Za = 4, Qa = /* @__PURE__ */ new WeakMap();
function $a(e) {
	return Object.isFrozen(e) && e.every((e) => Object.isFrozen(e));
}
function eo(e, t, n, r, i, a) {
	return e.kind === t && Object.is(e.xLeftPt, n) && Object.is(e.xRightPt, r) && Object.is(e.yTopPt, i) && Object.is(e.yBottomPt, a);
}
function to(e, t, n) {
	let r = e.authoredWrap;
	if (r !== "tight" && r !== "through") throw Error("Polygon compilation requires tight or through wrap");
	let i = {
		kind: r,
		imageKey: e.imageKey,
		points: e.wrapPolygon,
		xLeftPt: e.xLeft,
		xRightPt: e.xRight,
		yTopPt: e.yTop,
		yBottomPt: e.yBottom
	};
	$i(i);
	let a = $a(t);
	if (a) {
		let i = Qa.get(t)?.find((t) => eo(t, r, e.xLeft, e.xRight, e.yTop, e.yBottom));
		if (i) return n && (n.polygonCacheHitCount += 1), i.compiled;
	}
	n && (n.polygonCompileCount += 1);
	let o = ha(i);
	if (a) {
		let n = Object.freeze({
			kind: r,
			xLeftPt: e.xLeft,
			xRightPt: e.xRight,
			yTopPt: e.yTop,
			yBottomPt: e.yBottom,
			compiled: o
		});
		Qa.set(t, Object.freeze([n, ...(Qa.get(t) ?? []).slice(0, Za - 1)]));
	}
	return o;
}
function no(e, t) {
	let n = e.map((e) => {
		let n = e.wrapPolygon;
		t && n && (t.polygonSnapshotPointCount += n.length);
		let r = Object.freeze({
			...e,
			...n ? { wrapPolygon: Object.freeze(n.map((e) => Object.freeze({ ...e }))) } : {}
		}), i = r.authoredWrap === "tight" || r.authoredWrap === "through" ? to(r, n ?? [], t) : null;
		return Object.freeze({
			rect: r,
			polygon: i,
			wrapMaximumLeftPt: i ? Math.min(r.xLeft, i.polygonLeftPt) : r.xLeft,
			wrapMaximumRightPt: i ? Math.max(r.xRight, i.polygonRightPt) : r.xRight
		});
	}), r = Object.freeze({ floats: Object.freeze(n) });
	return Xa.set(r, /* @__PURE__ */ new Map()), r;
}
function ro(e, t) {
	let n = qa(e.rect.side);
	if (n !== "largest") return n;
	let r = G(Ua(K(e.wrapMaximumLeftPt), K(t.xLeftPt)), Ua(K(t.xRightPt), K(e.wrapMaximumRightPt)));
	return r === 0 ? t.readingDirection === "ltr" ? "left" : "right" : r > 0 ? "left" : "right";
}
function io(e, t, n, r, i, a) {
	let { rect: o, polygon: s } = e, c = s ? Sa(s, t, n) : [{
		l: K(o.xLeft),
		r: K(o.xRight)
	}];
	if (c.length === 0) return [];
	let l = s === null, u = c.reduce((e, t) => G(t.l, e) < 0 ? t.l : e, c[0].l), d = c.reduce((e, t) => G(t.r, e) > 0 ? t.r : e, c[0].r);
	switch (ro(e, a)) {
		case "left": return [{
			l: u,
			r: K(i),
			leftSquareBoundary: l,
			rightSquareBoundary: !1
		}];
		case "right": return [{
			l: K(r),
			r: d,
			leftSquareBoundary: !1,
			rightSquareBoundary: l
		}];
		case "bothSides": return c.map((e) => ({
			...e,
			leftSquareBoundary: l,
			rightSquareBoundary: l
		}));
	}
}
function ao(e, t) {
	let n = Xa.get(t);
	if (!n) throw Error("Prepared float geometry omitted its sweep cache");
	let r = n.get(e);
	if (r) return r;
	let i = /* @__PURE__ */ new Set(), a = (e) => {
		Number.isFinite(e) && i.add(e);
	};
	for (let { rect: n, polygon: r } of t.floats) if (a(Zi(Ua(K(n.yTop), K(e)))), a(n.yBottom), n.exemptLineTopPt !== void 0 && a(n.exemptLineTopPt), n.topEdgeInclusiveFromYPt !== void 0 && a(n.topEdgeInclusiveFromYPt), r) for (let t of Ca(r, e)) a(t);
	let o = Object.freeze([...i].sort((e, t) => e - t));
	return n.set(e, o), o;
}
function oo(e) {
	let t = e.filter((e) => G(e.r, e.l) > 0).slice().sort((e, t) => G(e.l, t.l) || G(e.r, t.r)), n = [];
	for (let e of t) {
		let t = n.at(-1);
		if (!t || G(e.l, t.r) > 0) {
			n.push({ ...e });
			continue;
		}
		G(e.l, t.l) === 0 && (t.leftSquareBoundary = t.leftSquareBoundary && e.leftSquareBoundary);
		let r = G(e.r, t.r);
		r > 0 ? (t.r = e.r, t.rightSquareBoundary = e.rightSquareBoundary) : r === 0 && (t.rightSquareBoundary = t.rightSquareBoundary && e.rightSquareBoundary);
	}
	return n;
}
function so(e, t, n, r, i, a, o) {
	let s = oo(e), c = K(t), l = K(n), u = [], d = (e, t, n) => {
		let r = G(c, e) >= 0 ? c : e, i = G(l, t) <= 0 ? l : t;
		G(i, r) > 0 && u.push({
			l: r,
			r: i,
			squareConstrained: n
		});
	}, f = c, p = !1;
	for (let e of s) {
		if (G(e.r, c) <= 0) {
			p = e.rightSquareBoundary;
			continue;
		}
		if (G(e.l, l) >= 0) {
			d(f, l, p), f = l;
			break;
		}
		G(e.l, f) > 0 && d(f, e.l, p || e.leftSquareBoundary);
		let t = G(e.r, f);
		if (t > 0 ? (f = e.r, p = e.rightSquareBoundary) : t === 0 && (p &&= e.rightSquareBoundary), G(f, l) >= 0) break;
	}
	G(f, l) < 0 && d(f, l, p);
	for (let e of a === "rtl" ? u.reverse() : u) if (G(Ua(e.r, e.l), K(Math.max(1, e.squareConstrained ? i : r))) >= 0 && (o === void 0 || o(e))) return {
		l: e.l,
		r: e.r,
		squareConstrained: e.squareConstrained
	};
	return null;
}
function co(e, t, n, r, i) {
	if (e.length < 3 || !(n > 0) || !(i > r)) return !1;
	let a = e.map((e) => e.xPt), o = e.map((e) => e.yPt), s = ha({
		kind: "tight",
		imageKey: "anchor-line-rewrap-probe",
		points: e,
		xLeftPt: Math.min(...a),
		xRightPt: Math.max(...a),
		yTopPt: Math.min(...o),
		yBottomPt: Math.max(...o)
	}), c = K(r), l = K(i);
	return Sa(s, t, n).some((e) => G(e.l, l) < 0 && G(e.r, c) > 0);
}
var lo = 2 ** -10;
function uo(e, t, n) {
	if (e.polygon?.kind !== "tight") return null;
	let { rect: r } = e;
	return G(t, K(r.yBottom)) === 0 ? r.yBottom - lo : r.topEdgeInclusiveFromYPt !== void 0 && G(t, K(r.topEdgeInclusiveFromYPt)) >= 0 && G(n, K(r.yTop)) === 0 ? r.yTop : null;
}
function fo(e) {
	let t = no([e]).floats[0], { rect: n } = t;
	return (e, r) => {
		let i = K(e), a = Ha(i, K(r)), o = G(a, K(n.yTop)) > 0 && G(i, K(n.yBottom)) < 0;
		return n.mode === "topAndBottom" ? o : n.exemptLineTopPt === e ? !1 : o || uo(t, i, a) !== null;
	};
}
function po(e, t, n, r, i, a) {
	return mo(e, t, n, r, i, a) !== null;
}
function mo(e, t, n, r, i, a) {
	let o = K(t), s = Ha(o, K(n)), c = null;
	for (let t of e.floats) {
		let { rect: e } = t;
		!t.polygon || e.mode !== "square" || t.polygon.kind !== "tight" && !a || Ya(e, r, i) && (uo(t, o, s) !== null || G(s, K(e.yTop)) > 0 && G(o, K(e.yBottom)) < 0) && (c = Math.max(c ?? -Infinity, e.yBottom));
	}
	return c;
}
function ho(e, t, n, r, i, a, o, s, c, l, u, d) {
	let f = K(e), p = Ha(f, K(t)), m = (e) => K(e);
	if (a.floats.some(({ rect: e }) => e.mode === "topAndBottom" && Ya(e, o, s) && G(p, m(e.yTop)) > 0 && G(f, m(e.yBottom)) < 0)) return null;
	let h = [];
	for (let i of a.floats) {
		let { rect: a } = i;
		if (a.mode !== "square" || a.exemptLineTopPt === e) continue;
		let o = uo(i, f, p);
		if (o === null && (G(p, m(a.yTop)) <= 0 || G(f, m(a.yBottom)) >= 0) || !Ya(a, n, r)) continue;
		let s = o === null ? io(i, e, t, n, r, c) : io(i, o, lo, n, r, c);
		s.length !== 0 && h.push(...s);
	}
	if (h.length === 0) return {
		topY: e,
		xOffset: 0,
		maxWidth: i
	};
	let g = so(h, n, r, l, u, c.readingDirection, d === void 0 ? void 0 : (t) => d(go(t, e, n, r)));
	return g ? go(g, e, n, r) : null;
}
function go(e, t, n, r) {
	let i = {
		numerator: 0n,
		denominator: 1n
	}, a = Ua(e.l, K(n)), o = G(a, i) > 0 ? a : i, s = K(n), c = Zi(o), l = n + c, u = K(l);
	if (G(u, e.l) < 0 && (c = Zi(Ua(K(Zi(e.l)), s)), l = n + c, u = K(l)), G(u, e.l) < 0) throw Error("Exact float window could not represent a contained start");
	let d = K(r), f = G(e.r, d) <= 0 ? e.r : d, p = Ua(K(Qi(f)), u), m = Qi(G(p, i) > 0 ? p : i);
	if (G(K(l + m), f) > 0) throw Error("Exact float window could not represent a contained end");
	return {
		topY: t,
		xOffset: c,
		maxWidth: m
	};
}
function _o(e, t, n, r, i) {
	let a = no(e), o = K(t), s = Ha(o, K(n)), c = {
		xLeftPt: r,
		xRightPt: i,
		readingDirection: "ltr"
	}, l = [];
	for (let e of a.floats) {
		let { rect: a } = e;
		if (!(G(s, K(a.yTop)) <= 0 || G(o, K(a.yBottom)) >= 0) && Ya(a, r, i)) {
			if (a.mode === "topAndBottom") return null;
			l.push(...io(e, t, n, r, i, c));
		}
	}
	let u = K(r), d = K(i), f = K(1);
	for (let e of oo(l)) if (!(G(e.r, u) <= 0)) {
		if (G(Ua(G(e.l, d) < 0 ? e.l : d, u), f) >= 0) return Zi(u);
		if (u = e.r, G(u, d) >= 0) return null;
	}
	return G(Ua(d, u), f) >= 0 ? Zi(u) : null;
}
function vo(e, t) {
	return Ha(Wa(e.exact.slope, K(t)), e.exact.intercept);
}
function yo(e, t) {
	return G(e.exact.slope, t.exact.slope) === 0 && G(e.exact.intercept, t.exact.intercept) === 0;
}
function bo(e, t, n) {
	return G(vo(e, n), vo(t, n)) || G(e.exact.slope, t.exact.slope);
}
function xo(e, t, n) {
	let r = Ua(e.slope, t.slope);
	if (r.numerator === 0n) return null;
	let i = Ua(e.intercept, t.intercept);
	return Ga(Ua(K(n), i), r);
}
function So(e, t, n, r, i) {
	t === null || G(t, K(n)) <= 0 || G(t, K(r)) >= 0 || (e.push(Zi(t)), i && (i.localRootCandidateCount += 1));
}
function Co(e, t, n, r, i, a) {
	let o = e[0];
	for (let r of e.slice(1)) {
		let e = bo(r, o, n);
		(t === "min" && e < 0 || t === "max" && e > 0) && (o = r);
	}
	let s = o.square;
	for (let c of e) if (c !== o) {
		if (yo(c, o)) {
			s &&= c.square;
			continue;
		}
		(t === "min" ? G(c.exact.slope, o.exact.slope) < 0 : G(c.exact.slope, o.exact.slope) > 0) && So(i, xo(c.exact, o.exact, 0), n, r, a);
	}
	return {
		exact: o.exact,
		square: s
	};
}
function wo(e, t = !1) {
	return {
		exact: {
			slope: {
				numerator: 0n,
				denominator: 1n
			},
			intercept: K(e)
		},
		square: t
	};
}
function To(e, t, n, r, i, a, o, s, c) {
	let { rect: l, polygon: u } = e, d = K(Ka(n, r));
	if (G(Ha(d, K(t)), K(l.yTop)) <= 0 || G(d, K(l.yBottom)) >= 0) return [];
	let f = u ? wa(u, t, n, r).map((e) => ({
		left: {
			exact: e.left,
			square: !1
		},
		right: {
			exact: e.right,
			square: !1
		}
	})) : [{
		left: wo(l.xLeft, !0),
		right: wo(l.xRight, !0)
	}];
	if (f.length === 0) return [];
	let p = Co(f.map((e) => e.left), "min", n, r, s, c), m = Co(f.map((e) => e.right), "max", n, r, s, c);
	switch (u?.kind === "tight" && (f = [{
		left: p,
		right: m
	}]), ro(e, o)) {
		case "left": return [{
			left: p,
			right: wo(a)
		}];
		case "right": return [{
			left: wo(i),
			right: m
		}];
		case "bothSides": return f;
	}
}
function Eo(e, t, n, r, i) {
	let a = e.slice().sort((e, n) => bo(e.left, n.left, t) || bo(e.right, n.right, t));
	for (let e = 0; e + 1 < a.length; e += 1) So(r, xo(a[e].left.exact, a[e + 1].left.exact, 0), t, n, i);
	let o = [];
	for (let e of a) {
		let a = o.at(-1);
		if (!a) {
			o.push(e);
			continue;
		}
		if (So(r, xo(e.left.exact, a.right.exact, 0), t, n, i), bo(e.left, a.right, t) > 0) {
			o.push(e);
			continue;
		}
		let s = Co([a.right, e.right], "max", t, n, r, i), c = yo(a.left, e.left) ? {
			exact: a.left.exact,
			square: a.left.square && e.left.square
		} : a.left;
		o[o.length - 1] = {
			left: c,
			right: s
		};
	}
	return o;
}
function Do(e, t, n, r, i, a, o, s, c, l, u, d) {
	let f = K(Ka(e, t)), p = Ha(f, K(n));
	if (a.floats.some(({ rect: e }) => e.mode === "topAndBottom" && Ya(e, o, s) && G(p, K(e.yTop)) > 0 && G(f, K(e.yBottom)) < 0)) return null;
	let m = [], h = [];
	for (let o of a.floats) {
		let { rect: a } = o;
		a.mode === "square" && Ya(a, r, i) && h.push(...To(o, n, e, t, r, i, c, m, d));
	}
	if (h.length === 0) return null;
	let g = Eo(h, e, t, m, d), _ = wo(r), v = wo(i), y = [], b = (n, r, i) => {
		let a = {
			slope: Ua(r.exact.slope, n.exact.slope),
			intercept: Ua(r.exact.intercept, n.exact.intercept)
		};
		y.push({ exactWidth: a });
		let o = Math.max(1, i ? u : l);
		G(Ha(Wa(a.slope, K(e)), a.intercept), K(o)) < 0 && a.slope.numerator > 0n && So(m, xo(r.exact, n.exact, o), e, t, d);
	}, x = _;
	for (let e of g) b(x, e.left, x.square || e.left.square), x = e.right;
	b(x, v, x.square);
	let S = y[0];
	for (let t of y.slice(1)) (G(Ha(Wa(t.exactWidth.slope, K(e)), t.exactWidth.intercept), Ha(Wa(S.exactWidth.slope, K(e)), S.exactWidth.intercept)) || G(t.exactWidth.slope, S.exactWidth.slope)) > 0 && (S = t);
	if (S) for (let n of y) n === S || G(n.exactWidth.slope, S.exactWidth.slope) <= 0 || So(m, xo(n.exactWidth, S.exactWidth, 0), e, t, d);
	return m.length === 0 ? null : Math.min(...m);
}
var Oo = 2e4, ko = 2 ** 33, Ao = .05, jo = 1584;
function Mo(e) {
	return !(e > 0) || !Number.isFinite(e) ? null : Math.min(Math.max(e, Ao), jo);
}
function No(e, t, n) {
	if (!(Math.abs(e) <= ko && Math.abs(n) <= ko && t >= .05 && t <= 1584)) throw RangeError("Line grid query outside the float line-search domain");
	let r = (n) => e + n * t, i = Math.max(1, Math.floor((n - e) / t) + 1), a = 0;
	for (; r(i) <= n;) i += 1, a += 1;
	for (; i > 1 && r(i - 1) > n;) --i, a += 1;
	if (a > 2) throw Error("Line grid estimate violated its one-step error bound");
	return r(i);
}
function Po(e, t, n, r, i, a, o = r, s = r + i, c = {
	xLeftPt: r,
	xRightPt: r + i,
	readingDirection: "ltr"
}, l = t, u = null, d) {
	let f = r, p = r + i, m = ao(n, a);
	if (u) {
		u.structuralEventCount = m.length;
		for (let { polygon: e } of a.floats) e && (u.compiledIntersectionCount += e.intersectionCount, u.compiledContourSpanCount += e.contourSpans.length, u.compileOrderComparisonCount += e.compileOrderComparisonCount, u.compilePairMembershipVisitCount += e.compilePairMembershipVisitCount);
	}
	let h = (e) => (u && (u.evaluatedYCount += 1), ho(e, n, f, p, i, a, o, s, c, t, l, d)), g = h(e);
	if (g) return g;
	let _ = Math.abs(e) <= ko ? Mo(n) : null, v = (e) => _ !== null && Math.abs(e) <= ko && po(a, e, n, f, p, c.stepThroughPolygons === !0), y = (t) => No(e, _, Math.min(t, ko)), b = Oo, x = (e) => {
		if (b > 0) return --b, y(e);
		let t = mo(a, e, n, f, p, c.stepThroughPolygons === !0);
		return y(t === null ? e : Math.max(t, e));
	}, S = e, C = !0, w = 0;
	for (;;) {
		for (; w < m.length && m[w] <= S;) w += 1;
		let e, r;
		if (C && v(S)) e = x(S), r = !0;
		else if (w < m.length) {
			let i = m[w], d = Ka(S, i);
			if (d > S && d < i && v(d)) e = x(S), r = !0;
			else {
				let d = Do(S, i, n, f, p, a, o, s, c, t, l, u);
				d !== null && u && (u.localRootEventCount += 1), e = d ?? i, r = !1;
			}
		} else {
			let e = Math.max(S, ...a.floats.map(({ rect: e }) => e.yBottom)), t = _ !== null && e <= ko ? y(e) : e + 2 ** -52 * Math.max(1, Math.abs(e));
			return Number.isFinite(t) || (t = e), h(t) ?? {
				topY: t,
				xOffset: 0,
				maxWidth: i
			};
		}
		if (!(e > S)) throw Error("Float line-window search violated strictly increasing candidate progress");
		let d = h(e);
		if (d) return d;
		S = e, C = r;
	}
}
function Fo(e, t, n, r, i, a, o = r, s = r + i, c = {
	xLeftPt: r,
	xRightPt: r + i,
	readingDirection: "ltr"
}, l = t, u) {
	return Po(e, t, n, r, i, a, o, s, c, l, null, u);
}
function Io(e, t, n, r) {
	let i = /* @__PURE__ */ new Set();
	for (;;) {
		let a = e;
		for (let i of t) i.mode === "topAndBottom" && Ya(i, n, r) && e >= i.yTop && e < i.yBottom && (a = Math.max(a, i.yBottom));
		if (a === e) return e;
		if (!Number.isFinite(a) || a < e || i.has(a)) throw Error("Top-and-bottom solver violated strictly increasing finite-bottom progress");
		i.add(a), e = a;
	}
}
var Lo = "word/document.xml", Ro = Object.freeze({
	REF_BOOKMARK_RESOURCE_LIMIT: Object.freeze({
		severity: "warning",
		part: Lo,
		layoutCode: "UNSUPPORTED_FEATURE",
		message: "REF bookmark acquisition exceeded its resource limits; cached field results were retained"
	}),
	UNSUPPORTED_VML_CONTENT: Object.freeze({
		severity: "warning",
		part: Lo,
		layoutCode: "UNSUPPORTED_FEATURE",
		message: "Some VML content could not be rendered"
	}),
	UNSUPPORTED_TEXT_EFFECT: Object.freeze({
		severity: "warning",
		part: Lo,
		layoutCode: "UNSUPPORTED_FEATURE",
		message: "WordprocessingML text effects are not rendered"
	}),
	INVALID_TEXT_EFFECT_VALUE: Object.freeze({
		severity: "warning",
		part: Lo,
		layoutCode: "INVALID_VALUE",
		message: "An invalid WordprocessingML text-effect value was ignored"
	}),
	MISSING_DRAWING_EXTENT: Object.freeze({
		severity: "error",
		part: Lo,
		layoutCode: "INVALID_GEOMETRY",
		message: "A drawing with a missing required extent was omitted"
	}),
	INVALID_DRAWING_EXTENT: Object.freeze({
		severity: "error",
		part: Lo,
		layoutCode: "INVALID_GEOMETRY",
		message: "A drawing with an invalid extent was omitted"
	}),
	DEGENERATE_DRAWING_EXTENT: Object.freeze({
		severity: "warning",
		part: Lo,
		layoutCode: "INVALID_GEOMETRY",
		message: "A drawing has a schema-valid zero-area extent"
	}),
	NESTED_CELL_FRAME_FLOW: Object.freeze({
		severity: "warning",
		part: "document",
		layoutCode: "UNSUPPORTED_FEATURE",
		message: "Nested-cell paragraph frames are retained but laid out in ordinary cell flow; their frame positioning is not implemented for this source"
	})
}), zo = Object.freeze({
	code: "INVALID_VALUE",
	severity: "warning",
	message: "The parser diagnostic contract did not match this renderer build"
});
function Bo(e) {
	return typeof e == "object" && !!e && !Array.isArray(e);
}
function Vo(e, t) {
	if (!Array.isArray(e) || !e.every((e) => Number.isSafeInteger(e) && e >= 0)) return !1;
	let [n] = e;
	return n === void 0 || n < t;
}
function Ho(e) {
	return Object.freeze({
		story: "body",
		storyInstance: "body",
		path: Object.freeze([...e])
	});
}
function Uo(e, t) {
	if (e === void 0) return Object.freeze([]);
	if (!Array.isArray(e)) return Object.freeze([zo]);
	let n = [], r = !1;
	for (let i of e) {
		if (!Bo(i) || typeof i.code != "string" || !Object.hasOwn(Ro, i.code) || !Vo(i.path, t)) {
			r = !0;
			continue;
		}
		let e = Ro[i.code];
		if (i.part !== e.part || i.severity !== e.severity) {
			r = !0;
			continue;
		}
		n.push(Object.freeze({
			code: e.layoutCode,
			severity: e.severity,
			source: Ho(i.path),
			message: e.message
		}));
	}
	return r && n.push(zo), Object.freeze(n);
}
var Wo = class extends Error {
	code;
	constructor(e, t) {
		super(`${e}: ${t}`), this.name = "LayoutInvariantError", this.code = e;
	}
}, Go = class extends Wo {
	reason;
	states;
	passes;
	constructor(e, t, n) {
		super("NON_CONVERGENCE", e === "cycle" ? `repeated exact-state cycle at ${t.at(-1) ?? "<missing>"}` : `hard exact-state pass limit ${n} reached`), this.name = "ExactConvergenceError", this.reason = e, this.states = Object.freeze([...t]), this.passes = n;
	}
};
function Ko(e) {
	let t = qo({
		...e,
		step: function* (t, n) {
			return e.step(t, n);
		}
	}), n = t.next();
	for (; !n.done;) n = t.next();
	return n.value;
}
function* qo(e) {
	let { seedState: t, step: n, stateOf: r, limit: i, carry: a } = e, o = t === void 0 ? 2 : 1;
	if (!Number.isInteger(i) || i < o) throw RangeError(`Exact convergence limit must be an integer >= ${o}`);
	let s = t === void 0 ? [] : [t], c = new Set(s), l = null, u = null;
	for (let e = 1; e <= i; e += 1) {
		u = yield* n(l, e);
		let t = r(u), o = s.at(-1);
		if (s.push(t), o === t) return Object.freeze({
			value: u,
			passes: e
		});
		if (c.has(t)) throw new Go("cycle", s, e);
		if (c.add(t), e === i) throw new Go("limit", s, e);
		l = a ? a(u) : u, u = null;
	}
	throw new Go("limit", s, i);
}
function* Jo(e, t, n, r) {
	if (!Number.isInteger(n) || n < 1) throw new Wo("NON_CONVERGENCE", "limit must be a positive integer");
	let i = e.fingerprint, a = r ? r(e) : e;
	e = void 0;
	try {
		return (yield* qo({
			seedState: i,
			step: function* (e) {
				return yield* t(e ?? a);
			},
			stateOf: (e) => e.fingerprint,
			...r ? { carry: r } : {},
			limit: n
		})).value;
	} catch (e) {
		throw e instanceof Go ? new Wo("NON_CONVERGENCE", e.reason === "cycle" ? `repeated geometry fingerprint cycle at ${e.states.at(-1) ?? "<missing>"}` : `hard iteration limit ${n} reached`) : e;
	}
}
var Yo = class extends Wo {
	reason;
	states;
	constructor(e, t) {
		super("NON_CONVERGENCE", e === "cycle" ? `line wrap measure/resolve cycle did not converge (${t.length} states)` : `line wrap measure/resolve pass limit did not converge (${t.length} states)`), this.name = "LineWrapNonConvergenceError", this.reason = e, this.states = Object.freeze([...t]);
	}
};
function Xo(e) {
	return e.map((e) => ({ ...e }));
}
function Zo(e, t) {
	return !e || !t ? !1 : e.physicalLineIndex !== void 0 || t.physicalLineIndex !== void 0 ? e.physicalLineIndex === t.physicalLineIndex : e.topY !== void 0 && e.topY === t.topY;
}
function Qo(e, t, n) {
	let r = -1;
	return JSON.stringify(e.map((i, a) => (Zo(e[a - 1], i) || (r += 1), {
		physicalLineIndex: i.physicalLineIndex,
		end: i.consumedEnd,
		topY: i.topY,
		xOffset: i.xOffset,
		availableWidth: i.availWidth,
		probeHeight: t[r],
		probeFloor: n[r],
		segments: i.segments.map((e) => ({
			source: e.src,
			...e.text === void 0 ? {} : { text: e.text }
		}))
	})));
}
var $o = 16;
function es(e, t, n) {
	let r = (e) => {
		let r = n?.(e);
		return Object.freeze(e.flatMap((n, i) => Zo(n, e[i + 1]) ? [] : [r?.[i] ?? t(n)]));
	}, i = (e, t) => Object.freeze(Array.from({ length: Math.max(e.length, t.length) }, (n, r) => Math.max(e[r] ?? -Infinity, t[r] ?? -Infinity))), a = [], o = 0;
	try {
		try {
			return Ko({
				step: (t) => {
					o += 1;
					let n = e(t?.probeHeights ?? null, t?.probeFloors ?? null), s = r(n);
					a = i(a, s);
					let c = t ? i(s, t.probeFloors).slice(0, s.length) : s;
					return Object.freeze({
						lines: n,
						probeHeights: s,
						probeFloors: Object.freeze(c),
						state: Qo(n, s, c)
					});
				},
				stateOf: (e) => e.state,
				limit: $o
			}).value.lines;
		} catch (e) {
			if (!(e instanceof Go) || e.reason !== "cycle" || $o - o < 2) throw e;
		}
		let t = a;
		return Ko({
			step: (n) => {
				let a = n ? i(t, n.probeHeights) : t;
				t = a;
				let o = e(a, a);
				return Object.freeze({
					lines: o,
					probeHeights: r(o),
					probeFloors: a,
					state: Qo(o, a, a)
				});
			},
			stateOf: (e) => e.state,
			limit: $o - o
		}).value.lines;
	} catch (e) {
		throw e instanceof Go ? new Yo(e.reason, e.states) : e;
	}
}
function ts(e, t, n, r) {
	return rs(ns(e), t, n, r);
}
function ns(e) {
	let t = 0, n = 0;
	for (let r of e) t += 1, r !== "­" && !os.test(r) && (n += 1);
	return {
		scalars: t,
		pitchBearing: n
	};
}
function rs({ scalars: e, pitchBearing: t }, n, r, i) {
	return e === t ? e * i : e * n + t * r;
}
function is(e, t, n, r) {
	let i = t + rs(ns(e), n, r, n + r);
	return i < 0 ? -i : 0;
}
function as(e) {
	for (let t of e) {
		let e = d(t.codePointAt(0));
		if (e === "D" || e === "R" || e === "L") return !0;
	}
	return !1;
}
var os = /^\p{M}$/u, ss = 255;
function cs(e, t) {
	let { levels: n, paragraphLevel: r } = f().computeLevels(e, t), i = Uint8Array.from(n), a = -1, o = -1;
	for (let e = 0; e < i.length; e += 1) {
		if (i[e] === ss) {
			a >= 0 ? i[e] = a : o < 0 && (o = e);
			continue;
		}
		o >= 0 && (i.fill(i[e], o, e), o = -1), a = i[e];
	}
	return o >= 0 && i.fill(r, o), i;
}
function ls(e) {
	let t = cs(e, "ltr"), n = cs(e, "rtl"), r = e.replace(/\u202D/gu, "‪").replace(/\u202E/gu, "‫"), i = r === e ? t : cs(r, "ltr"), a = r === e ? n : cs(r, "rtl"), o = (e) => t[e] !== i[e] || n[e] !== a[e];
	return (r) => r > 0 && r < e.length && (t[r] !== t[r - 1] || n[r] !== n[r - 1] || o(r) || o(r - 1));
}
function us(e) {
	let { segments: t, point: n, advances: r } = e, i = t[n.segmentIndex];
	if (!i || !("text" in i) || i.text[n.charOffset] !== ".") return;
	let a = (e.resolveOrder ?? Ei)(t, !0, e.model), o = a.rtl[n.segmentIndex] ? "rtl" : "ltr";
	if (cs(i.text, o).some((e) => (e & 1) != 0)) return;
	let s = 0;
	for (let t of a.order) if (!(t < e.cellStart || t >= e.cellEnd)) {
		if (t === n.segmentIndex) return s + e.selectedPrefixAdvance;
		s += r[t];
	}
}
var ds = 16 * 1024 * 1024;
function fs(e, t, n = ds) {
	let r = e + t;
	return Number.isSafeInteger(e) && e >= 0 && Number.isSafeInteger(t) && t >= 0 && Number.isSafeInteger(r) && r <= n ? r : void 0;
}
function ps(e = ds) {
	let t = 0;
	return (n) => {
		let r = fs(t, n, e);
		if (r === void 0) throw RangeError("DOCX line-break prefix search exceeded its UTF-16 work quota");
		t = r;
	};
}
function ms(e) {
	if (e === void 0) return 0;
	if (e === null) return 4;
	if (typeof e == "string") return fs(2, e.length * 6);
	if (typeof e == "number" || typeof e == "boolean") return JSON.stringify(e).length;
	if (typeof e != "object") return;
	let t = 2;
	for (let [n, r] of Object.entries(e)) {
		if (r === void 0) continue;
		let e = ms(n), i = ms(r), a = e === void 0 || i === void 0 ? void 0 : fs(t, e + i + 2);
		if (a === void 0) return;
		t = a;
	}
	return t;
}
function hs(e, t) {
	return e * t;
}
function gs(e) {
	return e === "wordArtVert" || e === "wordArtVertRtl" ? "mongolianVert" : e === "vert" || e === "vert270" || e === "eaVert" || e === "mongolianVert" ? e : void 0;
}
function q(e, t) {
	let n = (e.smallCaps ? Math.max(e.fontSize - 2, 1) : e.fontSize) * t;
	return e.vertAlign && (n *= .65), n;
}
var _s = .5, vs = /[ᄀ-ᇿ⺀-⿟　-〿぀-ヿ㄰-㆏㐀-䶿一-鿿ꥠ-꥿가-퟿豈-﫿＀-￯]/u;
function ys(e, t, n) {
	let r = null, i = 0;
	for (let n of t) n.alignment !== "bar" && Number.isFinite(n.pos) && (n.pos > i && (i = n.pos), n.pos > e && (r === null || n.pos < r.pos) && (r = n));
	let a = null;
	if (n > 0) {
		let t = 1e-6, r = Math.max(e, i), o = Math.ceil((r + t) / n), s = Number.isFinite(o) ? o * n : r + t;
		s <= e && (s += n), Number.isFinite(s) && (a = {
			pos: s,
			alignment: "left"
		});
	}
	return r && a ? r.pos <= a.pos ? r : a : r ?? a;
}
function bs(e, t, n) {
	return ys(e, t, n);
}
function xs(e, t) {
	let n = gs(t) !== void 0;
	return {
		type: "text",
		text: e.text,
		bold: e.bold ?? !1,
		italic: e.italic ?? !1,
		rtl: e.rtl,
		cs: e.cs,
		...e.rtl || e.cs ? {
			fontFamilyCs: e.fontFamilyCs ?? e.fontFamily ?? void 0,
			fontSizeCs: e.fontSizeCsPt ?? e.fontSizePt,
			boldCs: e.boldCs ?? e.bold ?? !1,
			italicCs: e.italicCs ?? e.italic ?? !1
		} : {
			...e.fontFamilyCs == null ? {} : { fontFamilyCs: e.fontFamilyCs },
			...e.fontSizeCsPt === void 0 ? {} : { fontSizeCs: e.fontSizeCsPt },
			...e.boldCs === void 0 ? {} : { boldCs: e.boldCs },
			...e.italicCs === void 0 ? {} : { italicCs: e.italicCs }
		},
		underline: !1,
		strikethrough: !1,
		fontSize: e.fontSizePt,
		color: e.color ?? null,
		fontFamily: e.fontFamily ?? null,
		fontFamilyEastAsia: e.fontFamilyEastAsia ?? null,
		isLink: !1,
		background: null,
		vertAlign: null,
		hyperlink: null,
		ruby: e.ruby ?? void 0,
		textBoxLineFloor: !0,
		textBoxVertical: n
	};
}
function Ss(e) {
	return /^[A-Za-z]\p{M}+$/u.test(e) && b(e).length === 0;
}
var Cs = /^(?:[\p{Script=Latin}\u0020-\u0040\u005B-\u0060\u007B-\u007E\u00A0-\u00AC\u00AE-\u00BF\u00D7\u00F7\u0300-\u036F])+$/u;
function ws(e) {
	return /\p{Script=Latin}/u.test(e) && Cs.test(e);
}
function Ts(e) {
	if (e.length < 2 || e.length > 3) return !1;
	let t = /^ +$/u.test(e[e.length - 1].text);
	return e.length - +!!t == 2;
}
function Es(e, t) {
	let n = 0, r = e.length;
	for (; n < r;) {
		let i = n + r >>> 1;
		e[i].end <= t ? n = i + 1 : r = i;
	}
	return n;
}
function Ds(e, t, n) {
	if (!e) return;
	let r = [];
	for (let i = Es(e, t); i < e.length; i++) {
		let a = e[i];
		if (a.start >= n) break;
		let o = Math.max(t, a.start), s = Math.min(n, a.end);
		o < s && r.push(Object.freeze({
			...a,
			start: o - t,
			end: s - t
		}));
	}
	return Object.freeze(r);
}
function Os(e, t) {
	let n = e.substituteContext;
	if (!n || n.text !== t || !Number.isInteger(n.offset) || n.offset < 0 || n.offset + e.text.length > t.length || t.slice(n.offset, n.offset + e.text.length) !== e.text) throw Error("Text shape request does not match its full run context; project the range explicitly");
}
function ks(e, t, n) {
	let r = e.substituteContext ?? {
		text: e.text,
		offset: 0
	}, i = e.text.slice(t, n);
	return {
		...e,
		text: i,
		registeredLatinPieceText: e.joinRegisteredLatinSlots === !0 && e.registeredLatinPieceText === e.text ? i : void 0,
		joinRegisteredGrapheme: t === 0 && n === e.text.length ? e.joinRegisteredGrapheme : void 0,
		substituteContext: {
			text: r.text,
			offset: r.offset + t
		}
	};
}
function As(e, t) {
	return {
		...e,
		text: t,
		baseDirection: void 0,
		joinRegisteredGrapheme: void 0,
		joinRegisteredLatinSlots: void 0,
		registeredLatinPieceText: void 0,
		substituteContext: {
			text: t,
			offset: 0
		}
	};
}
function js(e, t) {
	let n = e.substituteContext ?? {
		text: e.text,
		offset: 0
	};
	return {
		...e,
		text: t,
		baseDirection: void 0,
		joinRegisteredGrapheme: void 0,
		joinRegisteredLatinSlots: void 0,
		registeredLatinPieceText: void 0,
		substituteContext: {
			text: n.text.slice(0, n.offset) + t + n.text.slice(n.offset + e.text.length),
			offset: n.offset
		}
	};
}
function Ms(e, t, n) {
	if (!n || e.baseDirection !== "rtl" || !e.text.endsWith(" ") || t.spans.length !== 1) return !1;
	let r = t.spans[0];
	if (n.measurement.nativeBaseDirection !== "rtl" || n.request.baseDirection !== "rtl") throw TypeError("Visible native prefix receipt mismatch");
	let i = n.request, a = n.measurement.inkBounds;
	return n.endUTF16 === e.text.replace(/ +$/u, "").length && i.text === e.text.slice(0, n.endUTF16) && i.fontRoute.fingerprint === r.fontRoute.fingerprint && i.fontRoute.familyList === r.fontRoute.familyList && i.fontRoute.scope === r.fontRoute.scope && i.fontSizePt === e.fontSizePt && i.weight === r.font.weight && i.style === r.font.style && i.letterSpacingPt === (e.letterSpacingPt ?? 0) && i.kerning === (lr(r.text) ? !0 : e.kerning) && n.measurement.horizontalInkBoundsAreTight === !0 && !!a && Object.values(a).every(Number.isFinite) && Number.isFinite(n.measurement.advancePt) && n.measurement.advancePt >= 0 && n.measurement.advancePt <= t.advancePt && Number.isFinite(n.measurement.ascentPt) && Number.isFinite(n.measurement.descentPt);
}
function Ns(t, n = {}, r = {}) {
	if (!t) return "sans-serif";
	let i = e(n, t);
	if (i === "roman") return "serif";
	if (i === "swiss") return "sans-serif";
	if (i === "modern" && e(r, t) === "fixed") return "monospace";
	let a = I(t);
	return a === "mono" ? "monospace" : a === "serif" ? "serif" : "sans-serif";
}
function Ps(e) {
	return e === "eastAsia" ? "sans-serif" : "serif";
}
var Fs = Symbol("docx.fontMetricSnapshot");
function Is(e) {
	if (e.length > 32768) throw RangeError("Font cmap coverage has too many ranges");
	let t = e.map(([e, t]) => {
		if (!Number.isInteger(e) || !Number.isInteger(t) || e < 0 || t > 1114111 || e > t) throw RangeError("Font cmap coverage contains an invalid range");
		return [e, t];
	}).sort((e, t) => e[0] - t[0] || e[1] - t[1]), n = [];
	for (let [e, r] of t) {
		let t = n[n.length - 1];
		t && e <= t[1] + 1 ? n[n.length - 1] = [t[0], Math.max(t[1], r)] : n.push([e, r]);
	}
	return Object.freeze(n.map((e) => Object.freeze(e)));
}
function Ls(e = {}) {
	if (e[Fs]) return e;
	let t = Object.entries(e).map(([e, t]) => {
		if (!t.family?.trim()) throw TypeError(`Font metric ${e} requires a family`);
		if (t.lineHeightRatio !== void 0 && (!Number.isFinite(t.lineHeightRatio) || t.lineHeightRatio < 0)) throw RangeError(`Font metric ${e} lineHeightRatio must be finite and non-negative`);
		if (t.designAscentRatio !== void 0 && (!Number.isFinite(t.designAscentRatio) || t.designAscentRatio < 0)) throw RangeError(`Font metric ${e} designAscentRatio must be finite and non-negative`);
		if (t.designDescentRatio !== void 0 && (!Number.isFinite(t.designDescentRatio) || t.designDescentRatio < 0)) throw RangeError(`Font metric ${e} designDescentRatio must be finite and non-negative`);
		let n = [
			t.normalAscentRatio,
			t.normalDescentRatio,
			t.normalLineGapRatio
		].every((e) => e !== void 0 && Number.isFinite(e)) && t.normalAscentRatio >= 0 && t.normalDescentRatio >= 0 && t.normalAscentRatio + t.normalDescentRatio > 0;
		if (t.eastAsianLineHeightRatio !== void 0 && (!Number.isFinite(t.eastAsianLineHeightRatio) || t.eastAsianLineHeightRatio < 0)) throw RangeError(`Font metric ${e} eastAsianLineHeightRatio must be finite and non-negative`);
		if (t.fontBoxRatio !== void 0 && (!Number.isFinite(t.fontBoxRatio) || t.fontBoxRatio <= 0)) throw RangeError(`Font metric ${e} fontBoxRatio must be finite and positive`);
		if (t.averageCharWidthRatio !== void 0 && (!Number.isFinite(t.averageCharWidthRatio) || t.averageCharWidthRatio <= 0)) throw RangeError(`Font metric ${e} averageCharWidthRatio must be finite and positive`);
		if (t.weight !== void 0 && (!Number.isFinite(t.weight) || t.weight < 1 || t.weight > 1e3)) throw RangeError(`Font metric ${e} weight must be finite and between 1 and 1000`);
		let r = {
			family: t.family,
			...t.requiresGlyphCoverage === void 0 ? {} : { requiresGlyphCoverage: t.requiresGlyphCoverage },
			...t.glyphCoverageProbeFamily === void 0 ? {} : { glyphCoverageProbeFamily: t.glyphCoverageProbeFamily },
			...t.nativeRoutePrimaryFamily === void 0 ? {} : { nativeRoutePrimaryFamily: t.nativeRoutePrimaryFamily },
			...t.farEastCodePage === void 0 ? {} : { farEastCodePage: t.farEastCodePage },
			...t.lineHeightRatio === void 0 ? {} : { lineHeightRatio: t.lineHeightRatio },
			...t.designAscentRatio === void 0 ? {} : { designAscentRatio: t.designAscentRatio },
			...t.designDescentRatio === void 0 ? {} : { designDescentRatio: t.designDescentRatio },
			...t.wordLineHeightRatio !== void 0 && t.wordAscentRatio !== void 0 && t.wordDescentRatio !== void 0 && [
				t.wordLineHeightRatio,
				t.wordAscentRatio,
				t.wordDescentRatio
			].every((e) => Number.isFinite(e) && e >= 0) ? {
				wordLineHeightRatio: t.wordLineHeightRatio,
				wordAscentRatio: t.wordAscentRatio,
				wordDescentRatio: t.wordDescentRatio
			} : {},
			...n ? {
				normalAscentRatio: t.normalAscentRatio,
				normalDescentRatio: t.normalDescentRatio,
				normalLineGapRatio: t.normalLineGapRatio
			} : {},
			...t.eastAsianLineHeightRatio === void 0 ? {} : { eastAsianLineHeightRatio: t.eastAsianLineHeightRatio },
			...t.fontBoxRatio === void 0 ? {} : { fontBoxRatio: t.fontBoxRatio },
			...t.averageCharWidthRatio === void 0 ? {} : { averageCharWidthRatio: t.averageCharWidthRatio },
			...t.unicodeRanges === void 0 ? {} : { unicodeRanges: Is(t.unicodeRanges) },
			...t.requestedFamily === void 0 ? {} : { requestedFamily: t.requestedFamily },
			...t.weight === void 0 ? {} : { weight: t.weight },
			...t.style === void 0 ? {} : { style: t.style },
			...t.sourceIdentity === void 0 ? {} : { sourceIdentity: t.sourceIdentity },
			...t.synthesized === void 0 ? {} : { synthesized: t.synthesized }
		};
		return [Ut(e), Object.freeze(r)];
	}).sort(([e], [t]) => e.localeCompare(t)), n = Object.fromEntries(t);
	return Object.defineProperty(n, Fs, { value: !0 }), Object.freeze(n);
}
var Rs = new Set([
	161,
	164,
	167,
	168,
	170,
	173,
	175,
	176,
	177,
	178,
	179,
	180,
	182,
	183,
	184,
	185,
	186,
	188,
	189,
	190,
	191,
	215,
	247
]), zs = new Set([
	224,
	225,
	232,
	233,
	234,
	236,
	237,
	242,
	243,
	249,
	250,
	252
]), Bs = /^[\s\p{Cf}\p{M}]$/u, Vs = 64, Hs = 8, Us = [
	"ascii",
	"highAnsi",
	"eastAsia",
	"complexScript"
];
function Ws(e, t) {
	return e === t ? !0 : e.source === "native" || e.source === "generic" ? !1 : e.source === t.source && e.resolvedFamily === t.resolvedFamily && e.resourceIdentity === t.resourceIdentity && e.weight === t.weight && e.style === t.style;
}
function Gs(e, t, n, r, i) {
	let a = n === "eastAsia", o = r?.split(/[-_]/, 1)[0]?.toLowerCase() === "zh", s = /^(?:86|88)$/i.test(i?.trim() ?? ""), c = "highAnsi";
	return e <= 127 ? c = "ascii" : e <= 255 ? c = a && (Rs.has(e) || o && zs.has(e)) ? "eastAsia" : "highAnsi" : e >= 256 && e <= 687 ? c = a && (o || s) ? "eastAsia" : "highAnsi" : e >= 688 && e <= 767 || e >= 768 && e <= 879 || e >= 880 && e <= 975 || e >= 1024 && e <= 1279 ? c = a ? "eastAsia" : "highAnsi" : e >= 1424 && e <= 1983 || e >= 64285 && e <= 65023 || e >= 65136 && e <= 65278 ? c = "ascii" : e >= 4352 && e <= 4607 || e >= 11904 && e <= 12031 || e >= 12032 && e <= 12255 || e >= 12272 && e <= 12687 || e >= 12688 && e <= 12703 || e >= 12800 && e <= 19903 || e >= 19968 && e <= 40879 || e >= 40960 && e <= 42127 || e >= 42128 && e <= 42191 || e >= 44032 && e <= 55215 || e >= 63744 && e <= 64255 || e >= 65072 && e <= 65103 || e >= 65104 && e <= 65135 || e >= 65280 && e <= 65519 || e >= 65536 && e <= 1114111 ? c = "eastAsia" : e >= 7680 && e <= 7935 ? c = a && o ? "eastAsia" : "highAnsi" : (e >= 8192 && e <= 10175 || e >= 57344 && e <= 63743 || e >= 64256 && e <= 64284) && (c = a ? "eastAsia" : "highAnsi"), c === "eastAsia" && a ? c : t ? "complexScript" : c;
}
function Ks(e, t) {
	return e.themeFontPresence?.[t] ?? e.themeFonts?.[t] != null ? e.themeFonts?.[t] : e.fonts[t] ?? (e.themeFontPresence?.ascii ?? e.themeFonts?.ascii != null ? e.themeFonts?.ascii : e.fonts.ascii);
}
var qs = /* @__PURE__ */ new WeakMap(), Js = /* @__PURE__ */ new WeakMap();
function Ys(e, t, n, r, i) {
	let a = new Map([[0, 0], [e.text.length, n]]);
	return (n) => {
		if (e.measure === !1 || n <= 0) return 0;
		let o = a.get(n);
		if (o !== void 0) return o;
		let s = 0;
		for (let a of t) {
			if (n >= a.end) {
				s += a.advancePt;
				continue;
			}
			if (n <= a.start) break;
			let t = {
				text: a.text.slice(0, n - a.start),
				fontRoute: a.fontRoute,
				fontSizePt: e.fontSizePt,
				weight: a.font.weight,
				style: a.font.style,
				letterSpacingPt: e.letterSpacingPt ?? 0,
				kerning: lr(a.text) ? !0 : e.kerning,
				...e.baseDirection === void 0 ? {} : { baseDirection: e.baseDirection }
			}, o = r(t);
			s += o.advancePt, i?.(n, a, t, o);
			break;
		}
		return a.set(n, s), s;
	};
}
function Xs(t) {
	let n = Ls({
		...t.localMetrics,
		...t.fontMetrics
	}), r = (e, t, n, r) => JSON.stringify([
		e,
		t,
		n,
		r
	]), i = /* @__PURE__ */ new Map();
	for (let e of Object.values(n)) e.sourceIdentity && e.weight !== void 0 && e.style !== void 0 && i.set(r(e.sourceIdentity, e.family, e.weight, e.style), e);
	let a = (e, t, n) => JSON.stringify([
		Ut(e),
		t,
		n
	]), o = /* @__PURE__ */ new Map();
	for (let e of Object.values(n)) {
		let t = a(e.family, e.weight ?? 400, e.style ?? "normal"), n = o.get(t);
		n ? n.push(e) : o.set(t, [e]);
	}
	let s = Object.freeze(Object.fromEntries(Object.entries(t.genericFamilies ?? {}).map(([e, t]) => [e.trim().toLowerCase(), t]).sort(([e], [t]) => e.localeCompare(t)))), c = Object.freeze(Object.fromEntries(Object.entries(t.eastAsiaFontCharsets ?? {}).map(([e, t]) => [e.trim().toLowerCase(), t.trim()]).sort(([e], [t]) => e.localeCompare(t))));
	if (t.glyphContours && !t.glyphContourFingerprint?.trim()) throw TypeError("Native glyph contour acquisition requires an authority fingerprint");
	let l = typeof t.measurer.measureDirected == "function" && (!t.glyphContours || t.glyphContoursSupportDirection === !0) && (!(t.measurer.sameGlyphRaster || t.measurer.ownsGlyphs) || t.measurer.supportsDirectedAuxiliaries === !0), u = (t, n) => Gs(n.codePointAt(0) ?? 0, t.complexScript ?? !1, t.fontHint, t.eastAsiaLanguage, t.eastAsiaFontCharset ?? (() => {
		let n = Ks(t, "eastAsia");
		return n ? e(c, n.trim().toLowerCase()) : void 0;
	})()), d = Oe("text", {
		contextualAdvanceBatch: !0,
		glyphContours: t.glyphContourFingerprint ?? "unavailable",
		...l ? { directedMeasurement: !0 } : {},
		...l && t.acquireProjectableNativeUnits ? { projectableNativeUnits: !0 } : {},
		fonts: t.fonts.fingerprint,
		measurer: t.measurer.fingerprint,
		cjkFallback: t.cjkFallback ?? null,
		fontMetrics: n,
		eastAsiaFontCharsets: c,
		genericFamilies: s,
		...t.plainLineBoxes ? { plainLineBoxes: !0 } : {},
		...t.libreOfficeLineBoxes ? { libreOfficeLineBoxes: !0 } : {},
		...t.libreOfficeMsWordGridMetrics ? { libreOfficeMsWordGridMetrics: !0 } : {},
		...t.libreOfficeNoExternalLeading ? { libreOfficeNoExternalLeading: !0 } : {}
	}), f = (n) => {
		let r = Ks(n, n.slot), i = r ? e(s, r.trim().toLowerCase()) ?? n.genericFamily ?? "sans-serif" : n.genericFamily ?? Ps(n.slot), a = A(n.text ?? ""), o = t.fonts.scopedSubstituteScript?.(r, n.weight, n.style), c = n.substituteScope ?? (o !== void 0 && w(o, n.text ?? "", n.slot === "complexScript" ? "any" : "exclusive")), l = o && c ? o : void 0;
		return t.fonts.resolve({
			requestedFamily: r,
			...l ? { script: l } : {},
			cjkFallback: a ? t.cjkFallback : void 0,
			language: n.slot === "eastAsia" && a ? n.eastAsiaLanguage : void 0,
			genericFamily: i,
			weight: n.weight,
			style: n.style
		});
	}, p = /* @__PURE__ */ new Map(), m = (e, t) => {
		let n = e.get(t);
		return n !== void 0 && (e.delete(t), e.set(t, n)), n;
	}, h = (e, t, n, r) => {
		e.set(t, n), e.size > r && e.delete(e.keys().next().value);
	}, g = /* @__PURE__ */ new Map(), _ = /* @__PURE__ */ new WeakMap(), v = (e) => {
		let t = _.get(e);
		if (t !== void 0) return t;
		let n = JSON.stringify([
			e.familyList,
			e.scope,
			e.fingerprint
		]), r = g.get(n);
		return r === void 0 && (g.size >= 4096 && (g = /* @__PURE__ */ new Map(), _ = /* @__PURE__ */ new WeakMap(), p.clear()), r = g.size, g.set(n, r)), Object.isFrozen(e) && _.set(e, r), r;
	}, y = (e) => {
		if (e.baseDirection === void 0) return t.measurer.measure(e);
		if (!l) throw TypeError("Directed text acquisition is unsupported");
		let n = t.measurer.measureDirected({
			...e,
			baseDirection: e.baseDirection
		});
		if (n.nativeBaseDirection !== e.baseDirection) throw TypeError("Directed measurement receipt does not match its request");
		return n;
	}, x = (e) => {
		let t = [
			e.text,
			v(e.fontRoute),
			e.fontSizePt,
			e.weight,
			e.style,
			e.letterSpacingPt,
			e.kerning ?? null
		];
		e.baseDirection !== void 0 && t.push(e.baseDirection);
		let n = JSON.stringify(t), r = m(p, n);
		if (r) return r;
		let i = y(e), a = Object.freeze({
			...i,
			...i.inkBounds ? { inkBounds: Object.freeze({ ...i.inkBounds }) } : {}
		});
		return h(p, n, a, 40960), a;
	}, S = (e) => y(e), C = /* @__PURE__ */ new Map(), T = /* @__PURE__ */ new Map(), E = 0, O = 0, k = /* @__PURE__ */ new Map(), j = t.measurer.sameGlyphRaster ? (e) => {
		if (e.baseDirection !== void 0 && !l) throw TypeError("Directed raster proof is unsupported");
		let n = [
			e.route.fingerprint,
			e.faceFamily,
			e.weight,
			e.style,
			e.text
		];
		e.baseDirection !== void 0 && n.push(e.baseDirection);
		let r = JSON.stringify(n), i = k.get(r);
		if (i !== void 0) return i;
		let a = t.measurer.sameGlyphRaster(e);
		return k.size >= 256 && k.clear(), k.set(r, a), a;
	} : void 0, M = Object.freeze({
		acquireContextualAdvances(e) {
			let t = 0;
			for (let { request: n, ranges: r, additionalWorkUtf16: i = 0 } of e) {
				let e = fs(t, i);
				if (e === void 0) return;
				t = e;
				let { text: a, substituteContext: o, ...s } = n, c = ms(s), l = c === void 0 ? void 0 : fs(t, c);
				if (l === void 0) return;
				t = l;
				let u = fs(n.text.length, n.text.length), d = u === void 0 ? void 0 : fs(u, n.substituteContext?.text.length ?? n.text.length), f = d === void 0 ? void 0 : fs(t, d);
				if (f === void 0) return;
				t = f;
				let p = 0;
				for (let { start: e, end: i } of r) {
					if (!Number.isSafeInteger(e) || !Number.isSafeInteger(i) || e < p || i <= e || i > n.text.length) return;
					p = i;
					let r = fs(t, e), a = r === void 0 ? void 0 : fs(r, i);
					if (a === void 0) return;
					t = a;
				}
			}
			let n = [];
			for (let { request: t, ranges: r } of e) {
				let e = M.shape({
					...t,
					measure: !0,
					clusterGeometry: !1
				}), i = 0;
				for (let t of r) for (let n of [t.start, t.end]) {
					for (; i < e.graphemeBoundaries.length && e.graphemeBoundaries[i] < n;) i++;
					if (e.graphemeBoundaries[i] !== n) return;
				}
				let a = Ys({
					...t,
					measure: !0
				}, e.spans, e.advancePt, S), o = r.map((e) => {
					let t = a(e.start);
					return Object.freeze({
						range: Object.freeze({ ...e }),
						offsetPt: t,
						advancePt: a(e.end) - t
					});
				});
				if (o.some((e) => !Number.isFinite(e.offsetPt) || !Number.isFinite(e.advancePt))) return;
				n.push(Object.freeze({
					shape: e,
					clusters: Object.freeze(o)
				}));
			}
			return Object.freeze(n);
		},
		...l && t.acquireProjectableNativeUnits ? { acquireProjectableNativeUnits: (e) => t.acquireProjectableNativeUnits(e, (e) => {
			let t = N(e);
			return "shape" in t ? t : { shape: t };
		}) } : {},
		...t.glyphContours ? { glyphContours: (e) => {
			if (e.baseDirection !== void 0 && !l) throw TypeError("Directed contour acquisition is unsupported");
			return t.glyphContours(e);
		} } : {},
		...l ? { shapeDirected: (e) => M.shape(e) } : {},
		...j ? { sameGlyphRaster: j } : {},
		...t.measurer.ownsGlyphs ? { ownsGlyphs: (e) => {
			if (e.baseDirection !== void 0 && !l) throw TypeError("Directed glyph ownership is unsupported");
			return t.measurer.ownsGlyphs(e);
		} } : {},
		...t.fonts.exactLocalFaces ? { exactLocalFaces: (e) => t.fonts.exactLocalFaces(e) } : {},
		scalarFamily(e, t) {
			return Ks(e, u(e, t));
		},
		symbolDraws(e, n) {
			let r = u(e, n);
			return ee(Ks(e, r)) ? t.symbolDraws?.(n, f({
				...e,
				text: n,
				slot: r
			})) : !1;
		},
		symbolMonochrome(e, n) {
			let r = !0;
			for (let i of n) {
				let n = t.symbolMonochrome?.(i, f({
					...e,
					text: i,
					slot: u(e, i)
				}));
				if (n === !1) return !1;
				n === void 0 && (r = void 0);
			}
			return r;
		},
		symbolText(e) {
			let n = [], r = (e) => {
				let t = n.at(-1);
				t && t.mapped === e.mapped ? n[n.length - 1] = {
					...e,
					text: t.text + e.text
				} : e.text && n.push(e);
			};
			for (let n of e.text) {
				let i = u(e, n), a = Ks(e, i);
				if (!a || !ee(a)) {
					r({
						text: n,
						mapped: !1
					});
					continue;
				}
				let o = t.symbolText ? t.symbolText(n, a, f({
					...e,
					text: n,
					slot: i
				}), (t) => {
					let n = {
						...e,
						fonts: {
							ascii: null,
							highAnsi: null,
							eastAsia: null,
							complexScript: null
						},
						themeFonts: void 0,
						themeFontPresence: void 0
					};
					return f({
						...n,
						text: t,
						slot: u(n, t)
					});
				}, (t) => Ks(e, u(e, t))?.trim().toLowerCase() === a.trim().toLowerCase()) : z(n, a);
				for (let e of o) r(e);
			}
			return n;
		},
		fingerprint: d,
		fontMetrics: n,
		localMetrics: n,
		...t.plainLineBoxes ? { plainLineBoxes: !0 } : {},
		...t.libreOfficeLineBoxes ? { libreOfficeLineBoxes: !0 } : {},
		...t.libreOfficeMsWordGridMetrics ? { libreOfficeMsWordGridMetrics: !0 } : {},
		...t.libreOfficeNoExternalLeading ? { libreOfficeNoExternalLeading: !0 } : {},
		resolve: f,
		sourceScopeKey(e) {
			if (!Us.some((n) => t.fonts.scopedSubstituteScript?.(Ks(e, n), e.weight, e.style))) return;
			let n = M.shape({
				...e,
				measure: !1,
				clusterGeometry: !1
			}).spans, r = [...new Set(n.map((e) => JSON.stringify([e.fontRoute.fingerprint, e.substituteScope])))];
			return r.length === 1 ? r[0] : "mixed";
		},
		shape(e) {
			let t = N(e);
			return "shape" in t ? t.shape : t;
		}
	});
	function N(n) {
		if (n.baseDirection !== void 0 && !l) throw TypeError("Directed text acquisition is unsupported");
		if (!Number.isFinite(n.fontSizePt) || n.fontSizePt < 0) throw RangeError("fontSizePt must be a finite non-negative number");
		let s = n.substituteContext ?? {
			text: n.text,
			offset: 0
		};
		n.substituteContext && Os(n, s.text);
		let u = /* @__PURE__ */ new Map(), d = /* @__PURE__ */ new Map();
		for (let e of Us) {
			let r = Ks(n, e), i = t.fonts.configuredSubstituteScript?.(r);
			i && u.set(e, i);
			let a = t.fonts.scopedSubstituteScript?.(r, n.weight, n.style);
			a && d.set(e, a);
		}
		let p = Ks(n, "eastAsia"), g = n.eastAsiaFontCharset ?? (p ? e(c, p.trim().toLowerCase()) : void 0), _ = (e) => {
			let t = [], r = 0;
			for (let i of e) {
				let e = r + i.length;
				t.push({
					text: i,
					start: r,
					end: e,
					slot: Gs(i.codePointAt(0) ?? 0, n.complexScript ?? !1, n.fontHint, n.eastAsiaLanguage, g),
					inScope: !1
				}), r = e;
			}
			return t;
		}, v;
		if (d.size > 0) {
			let e = JSON.stringify([
				[...d],
				[...u],
				n.complexScript ?? !1,
				n.fontHint ?? null,
				n.eastAsiaLanguage ?? null,
				g ?? null
			]), t = m(T, s.text);
			t || (t = /* @__PURE__ */ new Map(), h(T, s.text, t, Vs));
			let r = m(t, e);
			if (!r) {
				E += 1, O += s.text.length;
				let n = _(s.text), i = new Map(n.map((e, t) => [e.start, t]));
				r = new Uint8Array(s.text.length);
				for (let e of new Set(d.values())) {
					let t = (e, t) => {
						let r;
						for (let a = i.get(e) ?? n.length; a < n.length && n[a].start < t; a += 1) if (r ??= n[a].slot, !Bs.test(n[a].text)) return n[a].slot;
						return r;
					}, a = D(e, s.text, (n, r) => {
						let i = t(n, r);
						return i !== void 0 && (u.get(i) ?? d.get(i)) === e;
					}), o;
					for (let n of a) {
						if (!n.inScope) {
							o = void 0;
							continue;
						}
						n.cls !== "neutral" && (o = t(n.start, n.end)), o !== void 0 && d.get(o) === e && r.fill(Us.indexOf(o) + 1, n.start, n.end);
					}
				}
				h(t, e, r, Hs);
			}
			v = Array.from(r.subarray(s.offset, s.offset + n.text.length), (e) => String.fromCharCode(48 + e)).join("");
		}
		let y = [
			n.text,
			n.fontSizePt,
			[
				n.fonts.ascii ?? null,
				n.fonts.highAnsi ?? null,
				n.fonts.eastAsia ?? null,
				n.fonts.complexScript ?? null
			],
			[
				n.themeFonts?.ascii ?? null,
				n.themeFonts?.highAnsi ?? null,
				n.themeFonts?.eastAsia ?? null,
				n.themeFonts?.complexScript ?? null
			],
			[
				n.themeFontPresence?.ascii ?? null,
				n.themeFontPresence?.highAnsi ?? null,
				n.themeFontPresence?.eastAsia ?? null,
				n.themeFontPresence?.complexScript ?? null
			],
			n.weight ?? null,
			n.style ?? null,
			n.complexScript ?? null,
			n.fontHint ?? null,
			n.eastAsiaLanguage ?? null,
			n.eastAsiaFontCharset ?? null,
			n.genericFamily ?? null,
			n.letterSpacingPt ?? null,
			n.kerning ?? null,
			n.joinRegisteredGrapheme ?? null,
			n.joinRegisteredLatinSlots ?? null,
			n.registeredLatinPieceText !== void 0 && n.registeredLatinPieceText === n.text,
			n.measure ?? null,
			n.clusterGeometry ?? null,
			...v === void 0 ? [] : [v]
		];
		n.baseDirection !== void 0 && y.push(["baseDirection", n.baseDirection]);
		let w = JSON.stringify(y), k = m(C, w);
		if (k) return k;
		let A = [], j = Object.freeze([...new Set([
			0,
			...b(n.text),
			n.text.length
		])].sort((e, t) => e - t)), M = new Set(j), N = _(n.text);
		N.forEach((e) => {
			let t = Number(v?.[e.start] ?? 0);
			t > 0 && (e.inScope = !0, e.slot = Us[t - 1]);
		});
		for (let e of N) {
			let t = A.at(-1);
			t?.script === e.slot && t.substituteScript === e.inScope ? (t.text += e.text, t.end = e.end) : A.push({
				text: e.text,
				start: e.start,
				end: e.end,
				script: e.slot,
				breakBefore: M.has(e.start),
				substituteScript: e.inScope
			});
		}
		let P = A.map((e) => ({
			...e,
			font: f({
				fonts: n.fonts,
				themeFonts: n.themeFonts,
				themeFontPresence: n.themeFontPresence,
				slot: e.script,
				text: e.text,
				eastAsiaLanguage: n.eastAsiaLanguage,
				weight: n.weight,
				style: n.style,
				genericFamily: n.genericFamily,
				...d.has(e.script) ? { substituteScope: e.substituteScript } : {}
			})
		})), F = [];
		for (let e of P) {
			let t = F.at(-1);
			t && t.substituteScript && e.substituteScript && Ws(t.font, e.font) ? F[F.length - 1] = {
				...t,
				text: t.text + e.text,
				end: e.end
			} : F.push(e);
		}
		let I = n.joinRegisteredGrapheme === !0 && Ss(n.text) && j.length === 2, L = n.registeredLatinPieceText === n.text && F.length === 2 && F[0].script === "highAnsi" && F[0].text.length > 0 && /^ +$/u.test(F[1].text), R = n.joinRegisteredLatinSlots === !0 && n.kerning === !0 && (Ts(F) && ws(n.text) || L && Cs.test(n.text));
		if ((I || R) && F.length > 1 && v === void 0) {
			let e = F[0], t = e.font, s = t.resourceIdentity ? i.get(r(t.resourceIdentity, t.resolvedFamily, t.weight, t.style)) : void 0, c = [...new Set(Array.from(n.text, (e) => e.codePointAt(0)))], l = (e) => {
				let t = 0;
				for (let n of c) {
					let r = 0, i = e.length;
					for (; r < i;) {
						let t = r + i >>> 1;
						e[t][1] < n ? r = t + 1 : i = t;
					}
					r < e.length && e[r][0] <= n && (t += 1);
				}
				return t;
			}, u = s?.unicodeRanges, d = u !== void 0 && l(u) === c.length && (o.get(a(t.resolvedFamily, t.weight, t.style)) ?? []).every((e) => e === s || e.unicodeRanges !== void 0 && [0, c.length].includes(l(e.unicodeRanges)));
			if ((t.source === "embedded" || t.source === "local") && t.resourceIdentity && d && F.every((e) => !e.substituteScript && (e.script === "ascii" || e.script === "highAnsi") && e.font.source === t.source && e.font.resourceIdentity === t.resourceIdentity && e.font.resolvedFamily === t.resolvedFamily && e.font.weight === t.weight && e.font.style === t.style && e.font.route.fingerprint === t.route.fingerprint)) {
				let t = Object.freeze(F.map((e) => Object.freeze({
					start: e.start,
					end: e.end,
					script: e.script,
					font: e.font
				})));
				F.splice(0, F.length, {
					...e,
					text: n.text,
					end: n.text.length,
					semanticSlotSpans: t
				});
			}
		}
		let z = F.map(({ substituteScript: e, font: t, ...r }) => {
			let i = n.measure === !1 ? {
				advancePt: 0,
				ascentPt: 0,
				descentPt: 0
			} : x({
				text: r.text,
				fontRoute: t.route,
				fontSizePt: n.fontSizePt,
				weight: t.weight,
				style: t.style,
				letterSpacingPt: n.letterSpacingPt ?? 0,
				kerning: lr(r.text) ? !0 : n.kerning,
				...n.baseDirection === void 0 ? {} : { baseDirection: n.baseDirection }
			});
			return Object.freeze({
				...r,
				...i,
				font: t,
				fontRoute: t.route,
				...v === void 0 ? {} : { substituteScope: e }
			});
		}), ee = z.flatMap((e) => e.semanticSlotSpans ? e.semanticSlotSpans.flatMap((e) => e.font.diagnostics) : e.font.diagnostics), B = z.length > 0 && z.every((e) => e.inkBounds !== void 0) ? (() => {
			let e = 0, t = Infinity, n = -Infinity, r = 0, i = 0;
			for (let a of z) {
				let o = a.inkBounds;
				t = Math.min(t, e + o.xMinPt), n = Math.max(n, e + o.xMaxPt), r = Math.max(r, o.ascentPt), i = Math.max(i, o.descentPt), e += a.advancePt;
			}
			return Object.freeze({
				xMinPt: t,
				xMaxPt: n,
				ascentPt: r,
				descentPt: i
			});
		})() : void 0, V = 0, te = 0, H = 0;
		for (let e of z) V += e.advancePt, te = Math.max(te, e.ascentPt), H = Math.max(H, e.descentPt);
		let U, ne;
		if (n.baseDirection === "rtl" && n.measure !== !1 && n.clusterGeometry !== !1 && z.length === 1 && n.text.endsWith(" ")) {
			let e = n.text.length;
			for (; e > 0 && n.text.charCodeAt(e - 1) === 32;) e--;
			e > 0 && (ne = e);
		}
		let re = n.clusterGeometry === !1 ? void 0 : (() => {
			let e = Ys(n, z, V, S, ne === void 0 ? void 0 : (e, t, n, r) => {
				e === ne && t.start === 0 && r.nativeBaseDirection === "rtl" && r.horizontalInkBoundsAreTight === !0 && r.inkBounds && Number.isFinite(r.advancePt) && r.advancePt >= 0 && Number.isFinite(r.ascentPt) && Number.isFinite(r.descentPt) && Object.values(r.inkBounds).every(Number.isFinite) && (U = Object.freeze({
					endUTF16: e,
					request: Object.freeze(n),
					measurement: Object.freeze({
						advancePt: r.advancePt,
						ascentPt: r.ascentPt,
						descentPt: r.descentPt,
						nativeBaseDirection: r.nativeBaseDirection,
						horizontalInkBoundsAreTight: !0,
						inkBounds: Object.freeze({
							xMinPt: r.inkBounds.xMinPt,
							xMaxPt: r.inkBounds.xMaxPt,
							ascentPt: r.inkBounds.ascentPt,
							descentPt: r.inkBounds.descentPt
						})
					})
				}));
			}), t = [];
			if (n.clusterGeometry === "spaces") for (let e = n.text.indexOf(" "); e >= 0; e = n.text.indexOf(" ", e + 1)) t.push({
				start: e,
				end: e + 1
			});
			else for (let e = 0; e < j.length - 1; e += 1) t.push({
				start: j[e],
				end: j[e + 1]
			});
			return Object.freeze(t.map(({ start: t, end: n }) => {
				let r = e(t);
				return Object.freeze({
					range: Object.freeze({
						start: t,
						end: n
					}),
					offsetPt: r,
					advancePt: e(n) - r
				});
			}));
		})(), ie = Object.freeze({
			advancePt: V,
			...n.baseDirection !== void 0 && (n.text.length === 0 || z.length > 0 && z.every((e) => e.nativeBaseDirection === n.baseDirection)) ? { nativeBaseDirection: n.baseDirection } : {},
			ascentPt: te,
			descentPt: H,
			...B ? { inkBounds: B } : {},
			...B && z.every((e) => e.horizontalInkBoundsAreTight === !0) ? { horizontalInkBoundsAreTight: !0 } : {},
			spans: Object.freeze(z),
			graphemeBoundaries: j,
			...re ? { clusters: re } : {},
			diagnostics: Object.freeze(ee)
		}), ae = U ? Object.freeze({
			shape: ie,
			visiblePrefix: U
		}) : ie;
		return h(C, w, ae, 81920), ae;
	}
	return qs.set(M, () => g.size), Js.set(M, () => Object.freeze({
		scans: E,
		utf16Units: O
	})), M;
}
function Zs(e) {
	let t = [];
	for (let n of e) {
		let e = n.toLowerCase() === n && n.toUpperCase() !== n, r = /\s/.test(n) ? t[t.length - 1]?.reduced ?? !1 : e, i = t[t.length - 1];
		i && i.reduced === r ? i.text += n : t.push({
			text: n,
			reduced: r
		});
	}
	return t.length ? t : [{
		text: e,
		reduced: !1
	}];
}
function Qs(e, t) {
	return t ? gt(t.start + e - 1, t.format) : String(e);
}
function $s(e, t) {
	for (let n = t - 1; n >= 0; n--) {
		let t = e[n];
		if (t.type === "text" || t.type === "field") return t.fontSize;
	}
	for (let n = t + 1; n < e.length; n++) {
		let t = e[n];
		if (t.type === "text" || t.type === "field") return t.fontSize;
	}
	return 10;
}
function ec(e, t) {
	if (e.fieldType === "page") return gt(t.displayPageNumber ?? t.pageIndex + 1, Ft(e.instruction) ?? t.pageNumberFormat ?? "decimal");
	if (e.fieldType === "numPages") {
		let n = Ft(e.instruction) ?? "decimal";
		return gt(t.totalPages, n);
	}
	if (e.fieldType === "date" || e.fieldType === "time") {
		let n = Vt(e.instruction);
		if (n) {
			let e = Ht(n, new Date(t.currentDateMs ?? Date.now()));
			if (e !== null) return e;
		}
		return e.fallbackText;
	}
	return e.fallbackText;
}
function tc(e) {
	for (let t = 0; t < e.length;) {
		let n = e.codePointAt(t);
		if (C(n)) return !0;
		t += n > 65535 ? 2 : 1;
	}
	return !1;
}
var nc = new Set([
	"、",
	"。",
	"，",
	"．",
	"」",
	"』",
	"】",
	"）",
	"］",
	"｝"
]);
function rc(e) {
	let t = e.codePointAt(0);
	return t === void 0 ? !1 : t >= 12353 && t <= 12438 || t >= 12445 && t <= 12447 || t >= 12449 && t <= 12538 || t === 12540 || t >= 12541 && t <= 12543 || t >= 12784 && t <= 12799 || t >= 110576 && t <= 110591 || t >= 110592 && t <= 110959;
}
function ic(e, t) {
	switch (t) {
		case "compressPunctuation": return nc.has(e);
		case "compressPunctuationAndJapaneseKana": return nc.has(e) || rc(e);
		default: return !1;
	}
}
function ac(e, t) {
	if (e === void 0) return;
	let n = [];
	for (let r of e) r > t && n.push(r - t);
	return n;
}
function oc(e, t, n = Infinity) {
	if (t <= 0 || n <= 0 || Number.isFinite(n) && e[t - 1] === "　") return t;
	let r = t, i = n;
	for (; r < e.length && e[r] === "　" && i > 0;) r++, i--;
	return r;
}
function sc(e, t) {
	if (e) {
		let t = e.split("-")[0].toLowerCase();
		if (Ur.has(t)) return !0;
	}
	return t;
}
function cc(e) {
	let t = [], n = null, r = "";
	for (let i of e) {
		let e = C(i.codePointAt(0));
		n === null || e === n ? (n = e, r += i) : (t.push({
			text: r,
			ea: n
		}), n = e, r = i);
	}
	return r.length > 0 && t.push({
		text: r,
		ea: n ?? !1
	}), t;
}
function lc(e) {
	let t = (e) => e >= 48 && e <= 57, n = (e) => e === "." || e === "," || e === ":" || e === "/" || e === "\xA0", r = [], i = "", a = null;
	for (let o = 0; o < e.length; o++) {
		let s = e[o], c = t(s.charCodeAt(0));
		!c && a === !0 && n(s) && t(e.charCodeAt(o + 1)) && (c = !0), a === null || c === a ? i += s : (r.push(i), i = s), a = c;
	}
	return i.length > 0 && r.push(i), r.length ? r : [e];
}
function uc(e) {
	let t = [], n = 0;
	for (; n < e.length;) {
		let r = n;
		for (; r < e.length && e[r] !== " ";) r++;
		for (; r < e.length && e[r] === " ";) r++;
		r > n && t.push(e.slice(n, r)), n = r;
	}
	return t.length ? t : [e];
}
function dc(e) {
	return e.length ? {
		offsets: e,
		start: 0,
		end: e.length,
		origin: 0
	} : void 0;
}
function fc(e, t) {
	return e.offsets[e.start + t] - e.origin;
}
function* pc(e) {
	if (e) for (let t = 0; t < e.end - e.start; t++) yield fc(e, t);
}
function mc(e, t, n) {
	if (!e) return;
	let r = (t, n) => {
		let r = e.start, i = e.end;
		for (; r < i;) {
			let a = Math.floor((r + i) / 2);
			e.offsets[a] < t || n && e.offsets[a] === t ? r = a + 1 : i = a;
		}
		return r;
	}, i = r(e.origin + t, !0), a = r(e.origin + n, !1);
	return i < a ? {
		offsets: e.offsets,
		start: i,
		end: a,
		origin: e.origin + t
	} : void 0;
}
function hc(e) {
	let t = e?.defaultTabStop;
	return t != null && t > 0 && Number.isFinite(1 / t) ? t : 36;
}
function gc(e, t, n, r) {
	if (n || !e || !("text" in e) || e.rtl === !0 !== r) return !1;
	let i = e.text;
	if (i.length === 0 || /^\s/u.test(i) || t && "text" in t && t.joinPrev === !0 || e.fitTextRegionIndex !== void 0 || e.ruby || e.tateChuYoko || e.hardJoinPrev || e.noBreakRanges?.length || e.seaBreaks !== void 0 || e.optionalHyphen || e.optionalHyphenBreaks?.length || tc(i)) return !1;
	let a = i.replace(/\s+$/u, "").length;
	for (let t of pc(e.explicitBreaks)) if (t > 0 && t < a) return !1;
	return !0;
}
function _c(e, t, n, r, i) {
	let a = ys(e, t, n);
	if (!a || r <= 0 || !i) return a;
	let o = t.some((e) => e.alignment !== "bar" && e.pos === a.pos);
	return {
		...a,
		pos: tr(a.pos, o, r)
	};
}
function vc(e, t, n, r) {
	return e === "left" ? t : e === "right" ? n - r : (t + n - r) / 2;
}
function yc(e) {
	return e === "center" ? "center" : e === "decimal" ? "decimal" : e === "right" || e === "end" ? "trailing" : "leading";
}
function bc(e, t, n, r, i, a) {
	let o = e.length, s = e.map((e) => e.width), c = Array(o).fill(void 0), l = Array(o).fill(void 0), u = (t, n) => {
		let r = 0, i;
		for (let n = t; n < o && !e[n].isTab; n++) i === void 0 && e[n].decimalOffset !== void 0 && (i = r + e[n].decimalOffset), r += s[n];
		let a = n === "decimal" ? e[t - 1]?.resolvePhysicalDecimal?.() : void 0;
		return {
			total: r,
			decimal: i,
			alignment: n === "center" ? r / 2 : n === "trailing" ? r : n === "decimal" ? a === void 0 ? i === void 0 ? 0 : r - i : r - a : 0
		};
	}, d = n;
	for (let n = 0; n < o; n++) {
		let o = e[n];
		if (!o.isTab) {
			d += s[n];
			continue;
		}
		if (o.readingGap !== void 0) {
			s[n] = o.readingGap, c[n] = o.leader, d += s[n];
			continue;
		}
		if (o.ptab && a) {
			let e = u(n + 1, "leading").total, t = nr(o.ptab.relativeTo === "indent" ? a.indentStart : 0, o.ptab.relativeTo === "indent" ? a.indentEnd : r, a.bandStart, a.bandEnd, a.narrowed), i = vc(o.ptab.alignment, t.start, t.end, e);
			s[n] = Math.max(0, Math.min(i, (o.ptab.alignment === "left" ? a.fitEnd ?? a.bandEnd : a.bandEnd) - e) - d), d += s[n];
			continue;
		}
		let f = a ? _c(d, t, i, a.leadingShift, o.displacedFrame === !0) : bs(d, t, i);
		if (!f) {
			s[n] = 0;
			continue;
		}
		let p = yc(f.alignment), m = u(n + 1, p), h = m.total, g;
		g = p === "leading" ? f.pos : f.pos - m.alignment;
		let _ = a?.narrowed ? o.windowOverflow === !0 ? Infinity : a.bandEnd : Math.min(r, a?.bandEnd ?? r), v = a?.fitEnd === void 0 || p !== "leading" ? _ : Math.min(_, a.fitEnd);
		if (c[n] = f.leader, p !== "leading" && o.alignedFitBack === !0) {
			let e = o.cellWidth ?? h, t = o.cellWidth === void 0 ? m.decimal : o.cellDecimal, r = p === "center" ? e / 2 : p === "trailing" ? e : o.cellPhysicalDecimal === void 0 ? t === void 0 ? 0 : e - t : e - o.cellPhysicalDecimal, i = f.pos - r;
			if ((p !== "decimal" || t !== void 0) && Math.max(i, d) + e > v) {
				s[n] = 0, i > d && (l[n] = i - d);
				continue;
			}
		}
		g + h > v && (g = v - h), g < d && (g = d), s[n] = g - d, d = g;
	}
	return {
		results: e.map((e, t) => l[t] === void 0 ? {
			width: s[t],
			leader: c[t]
		} : {
			width: s[t],
			leader: c[t],
			alignedGapLimit: l[t]
		}),
		endPen: d
	};
}
function xc(e, t) {
	return e && t.some((e) => e.alignment === "decimal");
}
function Sc(e) {
	if (!e.bidiOrdering) return "line-level";
	let t = e.bidiOrdering;
	return xi({
		...t,
		baseRtl: e.baseRtl,
		characterSpreadBidi: e.isJustified === !0 && si({
			...t,
			isLastLine: !1,
			stretchLastLine: e.stretchLastLine
		}, e.endsWithBreak === !0) === "character"
	});
}
function Cc(e) {
	let { marginRightPx: t, maxWidth: n, lineXOffset: r, lineMaxWidth: i, isFirst: a, firstIndent: o, tabOriginPx: s } = e, c = t - (r + i) + (a ? o : 0), l = t - r;
	return {
		startPen: c,
		leftLimit: t + s,
		frame: {
			leadingShift: n - (r + i),
			indentStart: t - n,
			indentEnd: t,
			bandStart: t - (r + i) + (a ? Math.min(0, o) : 0),
			bandEnd: l,
			fitEnd: e.fitWidth === void 0 ? l : Math.min(l, c + e.fitWidth),
			narrowed: r !== 0 || i !== n
		}
	};
}
function wc(e) {
	return !e.baseRtl || !e.currentLine.some((e) => "isTab" in e) ? 0 : Ec(e, 0, Cc(e).startPen, !0).delta;
}
function Tc() {
	let e, t = 0, n = 0;
	return (r) => {
		e !== r.currentLine && (e = r.currentLine, t = 0, n = Cc(r).startPen);
		let i = Ec(r, t, n);
		return t = r.currentLine.length, n = i.endPen, i.delta;
	};
}
function Ec(e, t, n, r = !1) {
	let { baseRtl: i, bidiCustomStopsPx: a, bidiIntervalPx: o, decimalAlignmentPoint: s, strAdvance: c } = e;
	if (!i) return {
		delta: 0,
		endPen: n
	};
	let l = e.currentLine.slice(t), u = l.map((e) => ({
		isTab: "isTab" in e,
		width: e.measuredWidth,
		ptab: "isTab" in e ? e.ptab : void 0,
		readingGap: "isTab" in e ? e.readingGap : void 0,
		leader: "isTab" in e ? e.leader : void 0,
		displacedFrame: "isTab" in e ? e.displacedFloatTabFrame : void 0,
		windowOverflow: "isTab" in e ? e.windowOverflow : void 0,
		alignedFitBack: "isTab" in e ? e.alignedFitBack : void 0,
		cellWidth: "isTab" in e ? e.alignedCellWidth : void 0,
		cellDecimal: "isTab" in e ? e.alignedCellDecimal : void 0,
		cellPhysicalDecimal: "isTab" in e ? e.alignedCellPhysicalDecimal : void 0
	}));
	for (let n = 0; n < l.length; n += 1) {
		if (!("isTab" in l[n])) continue;
		let i = n + 1;
		for (; i < l.length && !("isTab" in l[i]);) i += 1;
		let a = s(l.slice(n + 1, i));
		if (!a) continue;
		let o = n + 1 + a.segmentIndex, d = l[o];
		if ("text" in d) {
			let s = c(d, d.text.slice(0, a.charOffset));
			u[o].decimalOffset = s;
			let f = l[n];
			r && "isTab" in f && f.alignedFitBack && d.text[a.charOffset] === "." && (u[n].resolvePhysicalDecimal = () => us({
				segments: e.currentLine,
				point: {
					...a,
					segmentIndex: t + o
				},
				cellStart: t + n + 1,
				cellEnd: t + i,
				advances: e.currentLine.map((e) => e.measuredWidth),
				selectedPrefixAdvance: s + (d.leadingWordBoundaryPx ?? 0),
				model: Sc(e),
				resolveOrder: e.decimalOrder
			}));
		}
	}
	let { leftLimit: d, frame: f } = Cc(e), { results: p, endPen: m } = bc(u, a, n, d, o, f), h = 0;
	for (let e = 0; e < l.length; e++) {
		let t = l[e];
		"isTab" in t && (h += p[e].width - t.measuredWidth, t.measuredWidth = p[e].width, t.leader = p[e].leader, t.alignedGapLimit = p[e].alignedGapLimit);
	}
	return {
		delta: h,
		endPen: m
	};
}
function Dc(e, t) {
	if (t === void 0) return e;
	let n = 0;
	for (let r of e) {
		if (!("text" in r) || r.metricOnly || r.sourceRunIndex !== 0 || r.text.length === 0 || r.sourceTextOffset !== void 0 && r.sourceTextOffset !== n || r.textShapeRequest?.substituteContext?.text !== t || r.textShapeRequest.substituteContext.offset !== n || t.slice(n, n + r.text.length) !== r.text) return e;
		n += r.text.length;
	}
	if (n !== t.length || e.length === 0) return e;
	n = 0;
	for (let t of e) t.sourceCursorStart = n, n += "text" in t ? t.text.length : 0;
	return e;
}
function Oc(e, t) {
	return {
		segIndex: e.segIndex,
		charOffset: e.charOffset + t,
		...e.sourceTextStart === void 0 ? {} : { sourceTextStart: e.sourceTextStart }
	};
}
function kc(e) {
	if (e[0]?.sourceCursorStart === void 0) return;
	let t = 0;
	for (let n of e) {
		if (!("text" in n) || n.sourceCursorStart !== t || !n.text.length) throw Error("Invalid authoritative source cursor partition");
		t += n.text.length;
	}
	return t;
}
function Ac(e, t) {
	if (t.sourceTextStart === void 0) return t;
	let n = kc(e), r = t.sourceTextStart + t.charOffset;
	if (n === void 0 || !Number.isSafeInteger(t.sourceTextStart) || t.sourceTextStart < 0 || !Number.isSafeInteger(t.charOffset) || t.charOffset < 0 || !Number.isSafeInteger(r) || r > n) throw Error("Invalid authoritative source resume boundary");
	if (r === n) return {
		...t,
		segIndex: e.length,
		charOffset: 0,
		sourceTextStart: n
	};
	for (let n = 0; n < e.length; n++) {
		let i = e[n], a = i.sourceCursorStart;
		if ("text" in i && r < a + i.text.length) return {
			...t,
			segIndex: n,
			charOffset: r - a,
			sourceTextStart: a
		};
	}
	throw Error("Unowned authoritative source resume boundary");
}
function jc(e) {
	let t = e.nativeLevelUnit, n = e.textShapeRequest, r = n?.substituteContext;
	return !!t && n?.baseDirection === t.baseDirection && r?.text === t.sourceText && r.offset >= t.start && r.offset + e.text.length <= t.end && r.text.slice(r.offset, r.offset + e.text.length) === e.text;
}
function Mc(e, t) {
	let n = e.nativeLevelUnit, r = t.nativeLevelUnit;
	return !n && !r || !!n && !!r && jc(e) && jc(t) && n.sourceText === r.sourceText && n.start === r.start && n.end === r.end && n.baseDirection === r.baseDirection;
}
function Nc(e) {
	let t = e.nativeVisiblePrefix, n = e.textShapeRequest;
	if (!t || !n || !jc(e) || n.baseDirection !== "rtl" || !e.text.endsWith(" ")) return !1;
	let r = t.request;
	return t.endUTF16 === e.text.replace(/ +$/u, "").length && r.text === e.text.slice(0, t.endUTF16) && r.baseDirection === "rtl" && t.measurement.nativeBaseDirection === "rtl" && t.measurement.horizontalInkBoundsAreTight === !0 && r.fontRoute.fingerprint === e.fontRoute?.fingerprint && r.fontRoute.familyList === e.fontRoute?.familyList && r.fontRoute.scope === e.fontRoute?.scope && r.fontSizePt === n.fontSizePt && r.weight === (n.weight ?? 400) && r.style === (n.style ?? "normal") && r.letterSpacingPt === (n.letterSpacingPt ?? 0) && r.kerning === (lr(e.text) ? !0 : n.kerning);
}
function Pc(e, t) {
	if (t.baseDirection === void 0) return e.shape(t);
	if (!e.shapeDirected) throw TypeError("Directed source request lost its directed provider");
	let n = e.shapeDirected(t);
	if (n.nativeBaseDirection !== t.baseDirection) throw TypeError("Directed source result receipt does not honor its requested base");
	return n;
}
var Fc = {
	nativeLevelUnit: void 0,
	nativeVisiblePrefix: void 0,
	leadingWordBoundaryPx: void 0,
	shapedClusters: void 0,
	shapedSpaceClusters: void 0,
	selectedFaceInkBounds: void 0,
	selectedFaceFontBox: void 0,
	snapGridClass: void 0,
	snapGridNaturalWidthPx: void 0,
	snapGridLeadingPadPx: void 0,
	snapGridTrailingPadPx: void 0,
	snapGridCellPitchPx: void 0
};
function Ic(e, t) {
	return !e || e.charSpacePt == null || e.type !== "linesAndChars" && e.type !== "snapToChars" ? 0 : e.charSpacePt * t;
}
function Lc(e) {
	let t = 0;
	for (let n of e) vs.test(n) && t++;
	return t;
}
function Rc(e, t, n) {
	let r = Ic(t, n);
	if (r === 0 || e.length === 0) return 0;
	let i = [...e];
	return t?.type === "linesAndChars" || Lc(e) === i.length ? i.length * r : 0;
}
function zc(e, t, n) {
	return e.snapToCharacterGrid === !1 || t?.type === "snapToChars" ? 0 : t?.type === "linesAndChars" && e.widthBalanceGridDeltaFactor !== void 0 ? Ic(t, n) * e.widthBalanceGridDeltaFactor : Rc(e.text, t, n) === 0 ? 0 : Ic(t, n);
}
function Bc(e, t) {
	return e.fitTextPerGapPx === void 0 ? Vc(e) * t : e.fitTextPerGapPx;
}
function Vc(e) {
	return e.charSpacing ?? 0;
}
function Hc(e, t) {
	return e.autoSpaceBeforePt === void 0 ? 0 : e.autoSpaceLeadingPx ?? e.autoSpaceBeforePt * t;
}
function Uc(e, t) {
	return e.characterGrid?.type === "snapToChars" ? 0 : Hc(t, e.scale);
}
function Wc(e) {
	return e.punctuationCompressions?.reduce((e, t) => e + t.adjustmentPt, 0) ?? 0;
}
function Gc(e, t) {
	return Kc(e, e.text, t);
}
function Kc(e, t, n) {
	if (e.fitTextPerGapPx !== void 0 || e.tateChuYoko || !Tr(n?.type) || !e.widthBalanceSpaceSequence || e.widthBalanceSpaceAdjustmentPt === void 0) return 0;
	let r = 0;
	for (let e of t) e === " " && (r += 1);
	return r * e.widthBalanceSpaceAdjustmentPt;
}
function qc(e, t, n) {
	let r = e.punctuationCompressions?.filter((e) => e.end > t && e.end <= n).map((e) => Object.freeze({
		end: e.end - t,
		adjustmentPt: e.adjustmentPt
	}));
	return r && r.length > 0 ? Object.freeze(r) : void 0;
}
function Jc(e, t, n) {
	let r = e.noBreakRanges?.filter((e) => e.start >= t && e.end <= n).map((e) => Object.freeze({
		start: e.start - t,
		end: e.end - t
	}));
	return r && r.length > 0 ? Object.freeze(r) : void 0;
}
function Yc(e) {
	return new Set(e.noBreakRanges?.flatMap((e) => [e.start, e.end]) ?? []);
}
function Xc(e, t, n = 0) {
	let r = Yc(e);
	return [
		0,
		...b(e.text),
		e.text.length
	].filter((e, t, n) => n.indexOf(e) === t).filter((e) => e >= n && e <= t && !r.has(e)).at(-1) ?? 0;
}
function Zc(e) {
	if (e.hardJoinPrev !== !0 || e.text.length === 0) return;
	let t = Yc(e);
	return [...b(e.text), e.text.length].find((e) => e > 0 && !t.has(e)) ?? e.text.length;
}
function J(e, t, n) {
	let r = e.semanticSlotSpans, i = (e.semanticSlotRange?.start ?? 0) + t, a = (e.semanticSlotRange?.start ?? 0) + n;
	return {
		...jc(e) ? {
			nativeLevelUnit: e.nativeLevelUnit,
			...e.nativeVisiblePrefix && t === 0 && n > e.nativeVisiblePrefix.endUTF16 ? { nativeVisiblePrefix: e.nativeVisiblePrefix } : {}
		} : {},
		...r ? {
			semanticSlotSpans: r,
			semanticSlotRange: Object.freeze({
				start: i,
				end: a
			}),
			script: r[Es(r, i)]?.script ?? e.script
		} : {},
		...e.sourceTextOffset === void 0 ? {} : { sourceTextOffset: e.sourceTextOffset + t },
		...e.textShapeRequest ? { textShapeRequest: ks(e.textShapeRequest, t, n) } : {},
		punctuationCompressions: qc(e, t, n),
		autoSpaceBeforePt: t === 0 ? e.autoSpaceBeforePt : void 0,
		autoSpaceLeadingPx: t === 0 ? e.autoSpaceLeadingPx : void 0,
		noBreakRanges: Jc(e, t, n),
		explicitBreaks: mc(e.explicitBreaks, t, n),
		optionalHyphenBreaks: e.optionalHyphenBreaks?.filter((e) => e.offset > t && e.offset <= n).map((e) => Object.freeze({
			...e,
			offset: e.offset - t
		}))
	};
}
function Qc(e, t, n = 0) {
	if (!e.textLayoutService || !e.textShapeRequest || t.length === 0) return;
	let r = e.textLayoutService.shape({
		...ks(e.textShapeRequest, n, n + t.length),
		measure: !0,
		clusterGeometry: !1
	});
	if (r.horizontalInkBoundsAreTight !== !0 || !r.inkBounds || !Number.isFinite(r.advancePt) || !Number.isFinite(r.inkBounds.xMinPt) || !Number.isFinite(r.inkBounds.xMaxPt)) return;
	let i = e.charScale ?? 1;
	return {
		advancePt: r.advancePt * i,
		xMinPt: r.inkBounds.xMinPt * i,
		xMaxPt: r.inkBounds.xMaxPt * i
	};
}
function $c(e) {
	if (!e.textLayoutService || !e.textShapeRequest || e.text.length === 0) return;
	let t = e.textLayoutService.shape({
		...e.textShapeRequest,
		measure: !0,
		clusterGeometry: !0
	});
	if (!t.clusters?.length) return;
	let n = e.charScale ?? 1, r = /* @__PURE__ */ new Map();
	for (let e of t.clusters) {
		if (!Number.isFinite(e.advancePt)) return;
		r.set(e.range.end, e.advancePt * n);
	}
	return r;
}
function el(e) {
	let t, n = /* @__PURE__ */ new Map();
	for (let r of e) {
		if (!("text" in r) || r.verticalRun) {
			t = void 0;
			continue;
		}
		let e = r, i = e.punctuationCompressions ?? [], a = new Map(i.map((e, t) => [e.end, t])), o = i.length > 0 ? $c(e) : void 0, s = [
			0,
			...b(e.text),
			e.text.length
		];
		for (let r = 0; r < s.length - 1; r += 1) {
			let i = s[r], c = s[r + 1];
			if (c <= i) continue;
			let l = a.get(c), u = t || l !== void 0 ? Qc(e, e.text.slice(i, c), i) : void 0;
			if (t && u) {
				let e = n.get(t.segment) ?? t.segment.punctuationCompressions.map((e) => ({ ...e })), r = e[t.compressionIndex], i = Math.max(0, t.ink.advancePt + r.adjustmentPt), a = Math.min(0, i - t.contextualAdvancePt), o = Math.min(0, t.ink.xMaxPt - u.xMinPt - t.contextualAdvancePt), s = Math.max(r.adjustmentPt, a, o);
				s !== r.adjustmentPt && (e[t.compressionIndex] = {
					end: r.end,
					adjustmentPt: s
				}, n.set(t.segment, e));
			}
			t = l !== void 0 && u ? {
				segment: e,
				compressionIndex: l,
				ink: u,
				contextualAdvancePt: o?.get(c) ?? u.advancePt
			} : void 0;
		}
	}
	for (let [e, t] of n) e.punctuationCompressions = Object.freeze(t.map((e) => Object.freeze(e)));
}
function tl(e) {
	return e.charScale ?? 1;
}
function nl(e, t, n, r, i) {
	let { scalars: a, pitchBearing: o } = ns(t);
	return e * r + a * n + o * i;
}
function rl(e, t, n) {
	return e.fitTextPerGapPx === void 0 ? zc(e, t, n) + Bc(e, n) : e.fitTextPerGapPx;
}
function il(e, t, n) {
	if (e.fitTextPerGapPx !== void 0 || e.tateChuYoko) return !1;
	let r = zc(e, t, n);
	return r + Bc(e, n) < 0 || r < 0;
}
function al(e, t, n, r) {
	let i = ol.get(e);
	if (i && i.text === e.text && i.compressions === e.punctuationCompressions && i.grid === t && i.scale === n) return i.adjustmentPx;
	r?.(e.text.length);
	let a = new Float64Array(e.text.length + 2);
	for (let t of e.punctuationCompressions ?? []) t.end >= 0 && t.end <= e.text.length && (a[t.end + 1] += t.adjustmentPt);
	for (let e = 1; e < a.length; e += 1) a[e] += a[e - 1];
	let o = tl(e), s = (r, i) => (a[i + 1] - a[r + 1]) * n + Kc(e, e.text.slice(r, i), t) * n * o;
	return ol.set(e, {
		text: e.text,
		compressions: e.punctuationCompressions,
		grid: t,
		scale: n,
		adjustmentPx: s
	}), s;
}
var ol = /* @__PURE__ */ new WeakMap();
function sl(e, t, n, r) {
	let i = zc(e, t, n), a = Bc(e, n), o = tl(e), s = r.kind === "natural-clusters" ? al(e, t, n) : void 0, c = 0, l = (r.kind === "natural-clusters" ? r.clusters : r.cells).map((e) => {
		let t = c;
		return c += e.text.length, s ? e.advancePx * o + rs(ns(e.text), i, a, i + a) + s(t, c) : e.advancePx;
	});
	if (c !== e.text.length) throw Error("Condensed advance units do not cover their segment");
	return l;
}
function cl(e, t) {
	return e.kind === "vertical-cells" ? e.cells.some((e) => e.floored === !0) : t.some((e) => e < 0);
}
function ll(e, t, n, r) {
	let i = sl(e, t, n, r);
	if (!cl(r, i)) return;
	let a = 0;
	for (let e of i) a += e > 0 ? e : 0;
	return a;
}
function ul(e, t, n, r, i, a) {
	let o = [...new Set([
		t,
		...b(e.text.slice(t, n)).map((e) => t + e),
		n
	])].sort((e, t) => e - t), s = (t, n) => {
		if (n <= t) return 0;
		if (a(n - t), e.textLayoutService && e.textShapeRequest) {
			if (e.textShapeRequest.text !== e.text) throw Error("Cluster measurement does not match its retained text range context");
			return e.textLayoutService.shape({
				...ks(e.textShapeRequest, t, n),
				fontSizePt: r,
				measure: !0,
				clusterGeometry: !1
			}).advancePt;
		}
		return i(e.text.slice(t, n));
	}, c = [];
	for (let t = 0; t < o.length - 1; t += 1) {
		let n = o[t], r = o[t + 1], i = o[Math.max(0, t - 4)];
		c.push({
			text: e.text.slice(n, r),
			advancePx: s(i, r) - s(i, n)
		});
	}
	return c;
}
function dl(e, t, n, r, i) {
	if (e.fitTextPerGapPx !== void 0) {
		let n = [...e.text].length, r = e.fitTextRegionEnd ? Math.max(0, n - 1) : n;
		return t * tl(e) + r * e.fitTextPerGapPx + (e.fitTextTrailingPadPx ?? 0);
	}
	if (e.tateChuYoko) return e.fontSize * r;
	let a = zc(e, n, r), o = nl(t, e.text, a, tl(e), Bc(e, r)) + Gc(e, n) * r * tl(e) + Wc(e) * r;
	return il(e, n, r) ? i ? ll(e, n, r, i) ?? o : o > 0 ? o : 0 : o;
}
function fl(e, t) {
	return t?.type !== "snapToChars" || !t.characterPitchPt || t.characterPitchPt <= 0 || e.snapToCharacterGrid === !1 || e.metricOnly || e.fitTextRegionIndex !== void 0 || e.tateChuYoko ? null : e.script === "eastAsia" ? "eastAsia" : e.script === "complexScript" ? "complexScript" : "latin";
}
function pl(e, t, n, r = 1) {
	return !(n > 0) || !Number.isFinite(e) ? e : t === "eastAsia" ? Math.max(1, r) * n : Math.max(1, Math.ceil(Math.max(0, e) / n - 1e-9)) * n;
}
function ml(e) {
	return !e || !e.linePitchPt || e.linePitchPt <= 0 ? !1 : e.type === "lines" || e.type === "linesAndChars" || e.type === "snapToChars";
}
function hl(e, t, n) {
	if (!t) return 0;
	if (!n) throw Error("Vertical glyph measurement capability is required for vertical text");
	return n.measureRunInkExtra(e);
}
var gl = 19;
function _l(e) {
	let t = e?.semanticSlotSpans;
	if (!e || !t) return !1;
	let n = e.semanticSlotRange?.start ?? 0, r = e.semanticSlotRange?.end ?? e.text.length, i = t[Es(t, n)];
	return i !== void 0 && i.end < r;
}
function vl(e, t, n) {
	let r = e.textShapeRequest, i = t.textShapeRequest;
	return !!r && !!i && r.kerning === !0 && i.kerning === !0 && !!t.textLayoutService && t.textLayoutService === e.textLayoutService && !e.tateChuYoko && !t.tateChuYoko && !e.ruby && !t.ruby && !e.rubyPiece && !t.rubyPiece && !e.metricOnly && !t.metricOnly && e.fitTextRegionIndex === void 0 && t.fitTextRegionIndex === void 0 && !e.verticalRun && !t.verticalRun && !e.rtl && !t.rtl && !r.complexScript && !i.complexScript && (e.script === "ascii" || e.script === "highAnsi") && (t.script === "ascii" || t.script === "highAnsi") && !!e.fontRoute && e.fontRoute.fingerprint === t.fontRoute?.fingerprint && q(e, n) === q(t, n) && e.bold === t.bold && e.italic === t.italic && r.weight === i.weight && r.style === i.style && tl(e) === tl(t) && e.sourceRunIndex !== void 0 && e.sourceRunIndex === t.sourceRunIndex && e.sourceTextSequence === t.sourceTextSequence && Mc(e, t);
}
var yl = class {
	context;
	scale;
	fontForSegment;
	verticalGlyphMeasurement;
	selectedFont = null;
	initialFont;
	selectedKerning;
	kernedSeamPairs = /* @__PURE__ */ new Map();
	letterSpacing;
	constructor(e, t, n, r) {
		this.context = e, this.scale = t, this.fontForSegment = n, this.verticalGlyphMeasurement = r, this.initialFont = e.font, this.selectedKerning = e.fontKerning, this.letterSpacing = e.letterSpacing;
	}
	setFont(e) {
		e !== this.selectedFont && (this.context.font = e, this.selectedFont = e);
	}
	selectSegmentFont(e) {
		this.setFont(this.fontForSegment(e));
	}
	selectSegmentKerning(e) {
		let t = this.selectedKerning, n = this.segmentKerning(e);
		return this.context.fontKerning = n, this.selectedKerning = n, t;
	}
	segmentKerning(e) {
		return (e.textShapeRequest?.kerning ?? cr(e.fontSize, e.kerning)) || lr(e.text) ? "normal" : "none";
	}
	restoreKerning(e) {
		e != null && (this.context.fontKerning = e, this.selectedKerning = e);
	}
	withSegmentKerning(e, t) {
		let n = this.selectSegmentKerning(e);
		try {
			return t();
		} finally {
			this.restoreKerning(n);
		}
	}
	acquireCompressionSpaceClusters(e) {
		if (!(!e.textLayoutService || !e.textShapeRequest)) {
			if (e.textShapeRequest.text !== e.text) throw Error("Segment measurement does not match its retained text range context");
			return e.textLayoutService.shape({
				...e.textShapeRequest,
				fontSizePt: q(e, this.scale),
				measure: !0,
				clusterGeometry: "spaces"
			}).clusters;
		}
	}
	measureSegment(e, t = !1) {
		if (e.textLayoutService && e.textShapeRequest) {
			if (e.textShapeRequest.text !== e.text) throw Error("Segment measurement does not match its retained text range context");
			let n = Pc(e.textLayoutService, {
				...e.textShapeRequest,
				fontSizePt: q(e, this.scale),
				measure: !0,
				clusterGeometry: t
			});
			return t && (t === "spaces" ? e.shapedSpaceClusters = n.clusters : e.shapedClusters = n.clusters, (t !== "spaces" || e.metricOnly || e.text.length === 0) && (e.selectedFaceFontBox = {
				ascentPt: n.ascentPt,
				descentPt: n.descentPt
			}, e.selectedFaceInkBounds = n.inkBounds ?? {
				xMinPt: 0,
				xMaxPt: n.advancePt,
				ascentPt: n.ascentPt,
				descentPt: n.descentPt
			})), {
				width: n.advancePt,
				actualBoundingBoxAscent: n.ascentPt,
				actualBoundingBoxDescent: n.descentPt,
				fontBoundingBoxAscent: n.ascentPt,
				fontBoundingBoxDescent: n.descentPt
			};
		}
		this.selectSegmentFont(e);
		let n = this.selectSegmentKerning(e);
		try {
			return this.context.measureText(e.text);
		} finally {
			this.restoreKerning(n);
		}
	}
	wordBoundaryAdvance(e, t) {
		let n = e?.textShapeRequest, r = t.textShapeRequest, i = t.textLayoutService;
		if (!e || !n || !r || n.kerning !== !0 || !i || i !== e.textLayoutService || !e.text.endsWith(" ") || t.text.startsWith(" ") || !t.text || e.metricOnly || t.metricOnly || e.ruby || t.ruby || e.fitTextRegionIndex !== void 0 || t.fitTextRegionIndex !== void 0 || e.verticalRun || t.verticalRun || e.rtl || t.rtl || n.complexScript || r.complexScript || e.script !== "ascii" && e.script !== "highAnsi" || t.script !== "ascii" && t.script !== "highAnsi" || e.fontRoute?.fingerprint !== t.fontRoute?.fingerprint || q(e, this.scale) !== q(t, this.scale) || n.weight !== r.weight || n.style !== r.style || n.kerning !== r.kerning || tl(e) !== tl(t) || e.sourceRunIndex === void 0 || e.sourceRunIndex !== t.sourceRunIndex || e.sourceTextSequence !== t.sourceTextSequence) return 0;
		let a = _l(e) || _l(t);
		if (!a && e.script !== t.script || !Mc(e, t)) return 0;
		let o = n.substituteContext, s = r.substituteContext;
		if (!o || !s || o.text !== s.text || o.offset + e.text.length !== s.offset) return 0;
		let c = (e) => Pc(i, {
			...e,
			fontSizePt: q(t, this.scale),
			measure: !0,
			clusterGeometry: !1
		}), l = c({
			...n,
			text: e.text + t.text,
			registeredLatinPieceText: void 0,
			...a ? { joinRegisteredLatinSlots: !0 } : {}
		});
		return a && !(l.spans.length === 1 && l.spans[0]?.semanticSlotSpans) ? 0 : (l.advancePt - c(n).advancePt - c(r).advancePt) * tl(t);
	}
	kernedSpaceSeamAdvance(e, t) {
		if (!e || !e.text || !t.text || e.tateChuYoko || t.tateChuYoko || e.ruby || t.ruby || e.rubyPiece || t.rubyPiece) return 0;
		let n = e.text.endsWith(" ");
		if (n === t.text.startsWith(" ")) return 0;
		if (n && (e.script === t.script || _l(e) || _l(t))) return this.wordBoundaryAdvance(e, t);
		if (!vl(e, t, this.scale)) return 0;
		let r = e.text.slice(b(e.text).at(-1) ?? 0), i = t.text.slice(0, b(t.text)[0] ?? t.text.length), a = this.fontForSegment(e), o = `${a}\u0000${r}\u0000${i}`, s = this.kernedSeamPairs.get(o);
		if (s !== void 0) return s * tl(t);
		let c = this.selectedFont ?? this.initialFont, l = this.context.fontKerning;
		this.setFont(a), this.context.fontKerning = "normal";
		try {
			let e = (e) => this.context.measureText(e).width, n = e(r + i) - e(r) - e(i);
			return this.kernedSeamPairs.set(o, n), n * tl(t);
		} finally {
			this.context.font = c, this.selectedFont = c, this.context.fontKerning = l;
		}
	}
	condensedAdvanceUnits(e, t, n, r, i) {
		if (!il(e, r, this.scale)) return;
		if (e.text.slice(n, n + t.length) !== t) throw Error("Condensed advance units do not match their segment text range");
		let a = al(e, r, this.scale, i);
		if (e.verticalRun && this.verticalGlyphMeasurement) {
			i(gl * t.length);
			let o = zc(e, r, this.scale);
			return {
				kind: "vertical-cells",
				cells: this.verticalGlyphMeasurement.planRun({
					text: t,
					font: this.fontForSegment(e),
					fontKerning: this.segmentKerning(e),
					fontSizePt: q(e, this.scale),
					letterSpacingPt: rl(e, r, this.scale),
					characterGridDeltaPt: o,
					charScale: tl(e),
					growTrRotateInk: !0,
					writingMode: "vertical-rl",
					characterAdjustmentPt: (e, t) => a(n + e, n + t)
				}).map((e) => ({
					text: t.slice(e.range.start, e.range.end),
					advancePx: e.advancePt,
					...e.floored ? { floored: !0 } : {}
				}))
			};
		}
		if (n === 0) {
			let n = this.condensedClusterCache.get(e);
			(!n || n.text !== e.text) && (n = {
				text: e.text,
				clusters: this.contextualClusters(e, 0, e.text.length, i)
			}, this.condensedClusterCache.set(e, n));
			let r = 0, a = [];
			for (let e of n.clusters) {
				if (r + e.text.length > t.length) break;
				a.push(e), r += e.text.length;
			}
			if (r === t.length) return i(a.length), {
				kind: "natural-clusters",
				clusters: a
			};
		}
		return {
			kind: "natural-clusters",
			clusters: this.contextualClusters(e, n, n + t.length, i)
		};
	}
	condensedClusterCache = /* @__PURE__ */ new WeakMap();
	contextualClusters(e, t, n, r) {
		return ul(e, t, n, q(e, this.scale), (t) => this.measureRunText(e, t).width, r);
	}
	measureRunText(e, t) {
		this.selectSegmentFont(e);
		let n = this.selectSegmentKerning(e);
		try {
			return this.context.measureText(t);
		} finally {
			this.restoreKerning(n);
		}
	}
	measureCurrentText(e) {
		return this.context.measureText(e);
	}
	measureWithFont(e, t) {
		let n = this.selectedFont ?? this.initialFont;
		this.setFont(e);
		try {
			return this.context.measureText(t);
		} finally {
			this.context.font = n, this.selectedFont = n;
		}
	}
	verticalInkExtra(e, t) {
		if (!e.verticalRun) return 0;
		if (!this.verticalGlyphMeasurement) throw Error("Vertical glyph measurement capability is required for vertical text");
		this.selectSegmentFont(e);
		let n = this.selectSegmentKerning(e);
		try {
			return hl(t, !0, this.verticalGlyphMeasurement);
		} finally {
			this.restoreKerning(n);
		}
	}
}, bl = {
	tailPx: 0,
	coreLast: void 0
};
function xl(e) {
	let t = e.replace(/ +$/u, "");
	for (; t.length > 0 && nc.has(t.at(-1));) t = t.slice(0, -1);
	return t;
}
function Sl() {
	return {
		compressed: !1,
		contributions: [],
		eastAsianItems: 0,
		invalidItems: 0,
		mismatchedGaps: 0,
		spaceCount: 0,
		firstGap: -1,
		visibleItems: 0,
		autoSpaceCapacity: 0,
		autoSpaceInvalidItems: 0
	};
}
function Cl(e, t, n) {
	if (Bl(t)) return e;
	if (!("text" in t)) return bl;
	let r = xl(t.text);
	return r.length === 0 ? {
		tailPx: e.tailPx + t.measuredWidth,
		coreLast: e.coreLast
	} : r.length === t.text.length ? {
		tailPx: 0,
		coreLast: r.at(-1)
	} : t.mixedNaturalTrailingSpacePx !== void 0 && t.text.replace(/ +$/u, "").length === r.length ? {
		tailPx: t.mixedNaturalTrailingSpacePx,
		coreLast: r.at(-1)
	} : {
		tailPx: t.measuredWidth - n(t, r),
		coreLast: r.at(-1)
	};
}
function wl(e, t, n) {
	if (Bl(t)) return {
		item: t,
		inkless: !0,
		visibleText: "text" in t && /\S/u.test(t.text),
		eastAsian: !1,
		invalid: !1,
		gapCount: 0,
		capacity: 0,
		mismatched: !1,
		autoSpaceCapacity: 0,
		autoSpaceInvalid: !1
	};
	if (!("text" in t)) return {
		item: t,
		inkless: !1,
		visibleText: !1,
		eastAsian: !1,
		invalid: !0,
		gapCount: 0,
		capacity: 0,
		mismatched: !1,
		autoSpaceCapacity: 0,
		autoSpaceInvalid: !0
	};
	let r = vs.test(t.text), i = /\S/u.test(t.text), a = Vl(t.text), o = Fl(t, t.autoSpaceLeadingPx ?? 0, n), s = !Rl(t);
	if (t.mixedNaturalTrailingSpacePx !== void 0 && a > 0 && a === t.mixedNaturalTrailingSpaceCount && !t.text.slice(0, t.text.length - a).includes(" ")) {
		let c = Hl(t, a, n), l = e.firstGap >= 0 ? e.contributions[e.firstGap] : void 0;
		return {
			item: t,
			inkless: !1,
			visibleText: i,
			eastAsian: r,
			invalid: !1,
			gapCount: a,
			capacity: c,
			mismatched: l !== void 0 && (!Ll(t, l.item) || Math.abs(c - l.capacity) > 1e-6),
			autoSpaceCapacity: o,
			autoSpaceInvalid: s
		};
	}
	return {
		item: t,
		inkless: !1,
		visibleText: i,
		eastAsian: r,
		invalid: !zl(t, t.text),
		gapCount: 0,
		capacity: 0,
		mismatched: !1,
		autoSpaceCapacity: o,
		autoSpaceInvalid: s
	};
}
function Tl(e, t) {
	t.gapCount > 0 && e.firstGap < 0 && (e.firstGap = e.contributions.length), e.contributions.push(t), t.visibleText && (e.visibleItems += 1), t.eastAsian && (e.eastAsianItems += 1), t.invalid && (e.invalidItems += 1), t.mismatched && (e.mismatchedGaps += 1), e.spaceCount += t.gapCount, e.autoSpaceCapacity += t.autoSpaceCapacity, t.autoSpaceInvalid && (e.autoSpaceInvalidItems += 1);
}
function El(e) {
	let t = e.contributions.pop();
	t && (t.visibleText && --e.visibleItems, t.eastAsian && --e.eastAsianItems, t.invalid && --e.invalidItems, t.mismatched && --e.mismatchedGaps, e.spaceCount -= t.gapCount, e.autoSpaceCapacity -= t.autoSpaceCapacity, t.autoSpaceInvalid && --e.autoSpaceInvalidItems, e.firstGap === e.contributions.length && (e.firstGap = -1));
}
function Dl(e, t, n) {
	e.currentLine.push(t), e.mixedSpaceEnabled && Tl(e.mixedSpace, wl(e.mixedSpace, t, n));
}
function Ol(e) {
	e.currentLine.pop(), e.mixedSpaceEnabled && El(e.mixedSpace);
}
function kl(e, t, n) {
	Ol(e), Dl(e, t, n);
}
function Al(e, t) {
	let n = e.contributions, r = n.length - 1;
	for (; r >= 0 && n[r].tail === void 0;) --r;
	let i = r >= 0 ? n[r].tail : bl;
	for (let e = r + 1; e < n.length; e += 1) i = Cl(i, n[e].item, t), n[e].tail = i;
	return i;
}
function jl(e) {
	return e.mixedSpace.visibleItems > 0;
}
function Ml(e) {
	let t = e.mixedSpace;
	return e.mixedSpaceEnabled && (t.spaceCount > 0 && t.invalidItems === 0 && t.mismatchedGaps === 0 || t.autoSpaceCapacity > 0 && t.autoSpaceInvalidItems === 0);
}
function Nl(e, t, n) {
	let r = e.mixedSpace, i = e.currentLine.at(-1), a = n?.autoSpaceCompressible === !0 && e.mixedSpaceEnabled && r.autoSpaceInvalidItems === 0 && i !== void 0 && "text" in i;
	return (Ml(e) || a) && (r.eastAsianItems > 0 || vs.test(t));
}
function Pl(e) {
	return e !== "linesAndChars";
}
function Fl(e, t, n) {
	return e.autoSpaceCompressible !== !0 || e.autoSpaceBeforePt === void 0 ? 0 : Math.max(0, t - Or(e.autoSpaceBeforePt) * n);
}
function Il(e) {
	let t = e.firstGap >= 0 ? e.contributions[e.firstGap] : void 0, n = e.invalidItems === 0 && e.mismatchedGaps === 0;
	return {
		valid: n,
		eastAsian: e.eastAsianItems > 0,
		face: n ? t?.item : void 0,
		perSpaceCapacity: n ? t?.capacity ?? 0 : 0,
		count: n ? e.spaceCount : 0
	};
}
function Ll(e, t) {
	return e.mixedSpaceAverageWidthRatio === t.mixedSpaceAverageWidthRatio && e.fontRoute?.fingerprint === t.fontRoute?.fingerprint && e.fontFamily === t.fontFamily && e.fontSize === t.fontSize && e.bold === t.bold && e.italic === t.italic;
}
function Rl(e) {
	return !e.verticalRun && !e.tateChuYoko && !e.rtl && e.fitTextRegionIndex === void 0;
}
function zl(e, t) {
	return !t.includes(" ") && !e.verticalRun && !e.tateChuYoko && !e.rtl && e.fitTextRegionIndex === void 0 && e.widthBalanceGridDeltaFactor === void 0;
}
function Bl(e) {
	return "text" in e && e.metricOnly === !0 || "imagePath" in e && !!e.anchor;
}
function Vl(e) {
	return e.length - e.replace(/ +$/u, "").length;
}
function Hl(e, t, n) {
	return Math.max(0, e.mixedNaturalTrailingSpacePx / t - jr(q(e, n), e.mixedSpaceAverageWidthRatio));
}
function Ul(e, t) {
	let { breakerState: n, availW: r, fitsMeasuredWidth: i, characterGrid: a, baseRtl: o, widthPolicy: s, strNaturalAdvance: c, scale: l } = e, { pieces: u } = t;
	if (u.length === 0 || !Nl(n, u.map((e) => e.text).join(""), u[0].segment) || o || s !== "bounded" || a?.type === "snapToChars" || n.currentLine.length === 0) return;
	let d = Il(n.mixedSpace);
	if (!d.eastAsian && !u.some((e) => vs.test(e.text))) return;
	let f = d.valid && Pl(a?.type), p = n.mixedSpace.autoSpaceInvalidItems === 0, m = 0;
	for (let [t, n] of u.entries()) {
		let r = Vl(n.text), i = n.text.slice(0, n.text.length - r);
		if (!n.segment.fontRoute) return;
		Rl(n.segment) || (p = !1), zl(n.segment, i) || (f = !1), r > 0 && (t !== u.length - 1 || n.segment.mixedSpaceAverageWidthRatio === void 0 || d.face !== void 0 && !Ll(n.segment, d.face)) && (f = !1), m += Fl(n.segment, Uc(e, n.segment), l);
	}
	let h = (f && d.face ? d.perSpaceCapacity * d.count : 0) + (p ? n.mixedSpace.autoSpaceCapacity + m : 0);
	if (!(h > 0)) return;
	let g = n.currentWidth, _ = t.fitWidth, v = Math.max(0, g + _ - r());
	if (v > h || !i(g + _ - v, r())) return;
	let y = u.map((e) => e.text.replace(/ +$/u, "")), b = y.length - 1;
	for (; b >= 0 && (y[b] = xl(y[b]), !(y[b].length > 0));) --b;
	let x = b >= 0 ? bl : Al(n.mixedSpace, c), S = b >= 0 ? y[b].at(-1) : x.coreLast, C = b >= 0 ? u[b].segment : u[0].segment, w = Mr(S !== void 0 && vs.test(S), q(C, l));
	if (w !== void 0) {
		let e = g - (b >= 0 ? 0 : x.tailPx);
		for (let t = 0; t <= b; t += 1) y[t].length > 0 && (e += c(u[t].segment, y[t]));
		if (e - r() > w + 1e-9) return;
	}
	return v;
}
function Wl(e) {
	e.breakerState.mixedSpace.compressed = !0;
}
function Gl(e) {
	let { breakerState: t, availW: n, characterGrid: r } = e;
	if (t.mixedSpace.compressed) {
		let e = Il(t.mixedSpace), i = t.mixedSpace.contributions.flatMap((e) => e.gapCount > 0 ? [{
			segment: e.item,
			count: e.gapCount
		}] : []), a = 0;
		for (let e = t.currentLine.length - 1; e >= 0; --e) {
			let n = t.currentLine[e];
			if (Bl(n)) continue;
			let r = i.at(-1);
			if (r?.segment !== n || (i.pop(), a += r.segment.mixedNaturalTrailingSpacePx, r.segment.text.trim().length > 0)) break;
		}
		let o = i.reduce((e, t) => e + t.count, 0), s = Math.max(0, t.currentWidth - a - n()), c = e.valid && o > 0 && Pl(r?.type) ? e.perSpaceCapacity * o : 0, l = t.mixedSpace.autoSpaceInvalidItems === 0 ? t.mixedSpace.contributions.filter((e) => e.autoSpaceCapacity > 0) : [], u = l.reduce((e, t) => e + t.autoSpaceCapacity, 0), d = Math.min(s, c + u);
		if (d > 0) {
			let e = u > 0 ? d * c / (c + u) : d;
			if (e > 0) {
				let t = e / o;
				for (let e of i) {
					let n = t * e.count;
					e.segment.measuredWidth -= n, e.segment.latinSpaceCompressionPx = n;
				}
			}
			if (u > 0) {
				let t = (d - e) / u;
				for (let e of l) {
					let n = e.item, r = t * e.autoSpaceCapacity;
					n.measuredWidth -= r, n.autoSpaceLeadingPx = (n.autoSpaceLeadingPx ?? 0) - r;
				}
			}
			t.currentWidth -= d;
		}
	}
	t.mixedSpace = Sl();
}
function Kl(e) {
	let t = e?.compatibilityMode, n = t === void 0, r = t === 14, i = t === 15, a = !n && t < 15, o = n || t < 15, s = t === 11 || t === 12 || r || i, c = n || t === 11 || t === 12 || r, l = (e) => e === !0, u = l(e?.enableOpenTypeFeatures), d = l(e?.lineWrapLikeWord6), f = l(e?.doNotSuppressIndentation), p = l(e?.ww11IndentRules), m = l(e?.doNotUseIndentAsNumberingTabStop), h = l(e?.noTabHangInd);
	return Object.freeze({
		pageWideFootnoteArea: i,
		pageWideEndnoteArea: i,
		perColumnFootnoteBands: e?.__footnoteColumnBands === !0 || a,
		continuousSectionKeepsFootnotePage: i,
		footnoteLayoutLikeWW8: l(e?.footnoteLayoutLikeWW8),
		pageBreakBeforeSuppressesTopSpacing: i,
		tableOriginMeasuredMode: s,
		tableOriginPlacementMode: n || s,
		tableMode15Geometry: i,
		autofitLeadingIndentBandMode: n || r || i,
		autofitOuterMarginsHangOutsideBand: n || r,
		numberingSpaceSuffixArialMode: n || r || i,
		textMarkerKeepsBodyDescent: n || t === 12 || r || i,
		textMarkerFirstLineUnionMode15: i,
		numberedWindowFrame: (n || t === 12 || r) && !f && !p && !m && !h,
		specifiedTextLineBoxMode: r || i,
		specifiedTextLineBoxMode15: i,
		inlinePictureAutoLeading: i,
		lineEndJustificationBeforeMode15: !i,
		thaiDistributeProportionalSpread: o,
		kashidaLineFitMode15: i,
		justifiedInterwordCompression: i,
		preservePre15AnchorLine: !i,
		mode14TightAnchor: r,
		mode14ColumnLineStartOrigin: r,
		throughWrapStepsLines: i,
		tabDisplacedReadingFrame: o,
		latinInterwordXavgFloor: a ? r || !u ? "always" : "never" : !d && !u ? "without-explicit-kerning" : "never",
		compressedSpaceLineFitMode: a,
		firstOwnerClosingPairAdvance: n || s,
		gridRightIndentPitchAlignment: o,
		cjkClosingMarkHangProfile: i ? "mode15" : c ? "earlier" : "unmeasured",
		paragraphOffJapaneseLineEdges: n || s,
		paragraphOffThaiLineEdges: c,
		adjustLineHeightInTable: l(e?.adjustLineHeightInTable),
		useFeLayout: l(e?.useFeLayout),
		balanceSingleByteDoubleByteWidth: l(e?.balanceSingleByteDoubleByteWidth),
		lineWrapLikeWord6: d,
		enableOpenTypeFeatures: u,
		ulTrailSpace: l(e?.ulTrailSpace),
		doNotExpandShiftReturn: l(e?.doNotExpandShiftReturn),
		doNotSuppressIndentation: f,
		ww11IndentRules: p,
		doNotUseIndentAsNumberingTabStop: m,
		noTabHangInd: h
	});
}
var ql = Kl(void 0), Jl = /* @__PURE__ */ new WeakMap(), Yl = /* @__PURE__ */ new Map();
function Xl(e) {
	let t = Jl.get(e);
	if (t === void 0) {
		let n = JSON.stringify(Object.values(e));
		t = Yl.get(n), t === void 0 && (t = Yl.size, Yl.set(n, t)), Jl.set(e, t);
	}
	return t;
}
function Zl(e) {
	return e.compat ?? ql;
}
function Ql(e) {
	let t = [...e];
	for (let e = t.length - 1; e >= 0; --e) if (t[e] !== "　") return vs.test(t[e]);
	return !1;
}
var $l = 1e-9;
function eu(e, t) {
	return e <= t + $l;
}
function tu(e, t, n, r = 0, i = 1, a = 0, o = !1, s, c, l = Infinity) {
	let u = [...t], d = (t) => c?.(t) ?? (() => {
		let n = hl(t, o, s);
		return nl(e.measureText(t).width + n, t, r, i, a);
	})(), f = (e) => {
		let t = e, r = l;
		if (r > 0) {
			for (; t > 0 && u[t - 1] === "　";) t--;
			let n = e - t;
			t += Math.max(0, n - r);
		}
		return eu(d(u.slice(0, t).join("")), n);
	}, p = 0, m = u.length;
	for (; p < m;) {
		let e = p + m + 1 >> 1;
		f(e) ? p = e : m = e - 1;
	}
	return u.slice(0, p).join("");
}
var nu = new Set([..."。、．，」』）】〉》〕｝"]), ru = new Set([..."」』）】〉》〕｝、。「『（【〈《〔｛"]), iu = (e) => e.length === 2 && nu.has(e[0]) && ru.has(e[1]);
function au(e, t, n) {
	return (e.alignment === "left" || e.alignment === "justify") && n.closingPairRootSource === !0 && t.hasEastAsianText && !e.framePr && !t.runDirectionUnauthored && !t.baseRtl && !t.hasRuby && (!t.characterGrid.active || t.characterGrid.kind === "linesAndChars" && t.characterGrid.deltaPt === 0) && n.pageWritingMode === "horizontal-tb" && !n.verticalPageFrame;
}
function ou(e, t) {
	if (!e || !("text" in e) || !e.text || !e.textShapeRequest || !e.textLayoutService || e.metricOnly || e.verticalRun || e.ruby || e.rubyPiece || e.tateChuYoko || e.optionalHyphen || e.optionalHyphenGlyph || e.optionalHyphenWord || e.optionalHyphenBreaks?.length || e.noBreakRanges?.length || e.fitTextRegionIndex !== void 0 || e.fitTextPerGapPx !== void 0 || e.charSpacing || e.charScale !== void 0 && e.charScale !== 1 || e.vertAlign || e.position) return !1;
	let n = e.sourceRunIndex === void 0 ? void 0 : t[e.sourceRunIndex];
	return n?.type === "text" && !n.rtl && !n.cs && !n.allCaps && !n.smallCaps;
}
var su = (e, t) => Number.isFinite(e) && Number.isFinite(t) && eu(e, t) && eu(t, e);
function cu(e, t, n) {
	if (!t.closingPairAdvanceAdmitted || !Zl(t).firstOwnerClosingPairAdvance) return;
	let r = t.layoutServices?.text;
	if (!r?.acquireContextualAdvances || !r.exactLocalFaces || !r.ownsGlyphs || !r.sameGlyphRaster || e.some((e) => {
		if (e.type !== "text") return !0;
		let t = e;
		return t.ruby || t.optionalHyphen || t.noteRef || t.fitTextVal != null || t.noBreakRanges?.length || t.noBreakBefore || t.noBreakAfter || t.eastAsianVert || t.allCaps || t.smallCaps || /[\p{Cc}\p{Cf}]/u.test(e.text);
	})) return;
	let i = [];
	for (let t = 0; t < n.length; t++) {
		let a = n[t];
		if (!ou(a, e) || a.textLayoutService !== r) continue;
		let o = a.textShapeRequest.eastAsiaLanguage?.toLowerCase();
		if (o != null && o !== "ja-jp") continue;
		let s = [], c = [], l = 0;
		for (let i = 0; i < a.text.length; i++) {
			let o = a.text[i], u = a.text[i + 1];
			if (u === void 0) {
				let i = n[t + 1];
				if (ou(i, e) && i.textLayoutService === r) {
					let e = a.textShapeRequest.substituteContext, t = i.textShapeRequest.substituteContext;
					e && t && (e.text === t.text && e.offset + a.text.length === t.offset || i.sourceRunIndex === a.sourceRunIndex + 1 && e.offset + a.text.length === e.text.length && t.offset === 0) && (u = i.text[0]);
				}
			}
			let d = o + (u ?? "");
			for (; l < (a.punctuationCompressions?.length ?? 0) && a.punctuationCompressions[l].end < i + 1;) l++;
			!iu(d) || a.punctuationCompressions?.[l]?.end === i + 1 || (s.push({
				start: i,
				end: i + 1
			}), c.push(d));
		}
		s.length && i.push({
			segment: a,
			ranges: s,
			pairs: c
		});
	}
	if (!i.length || Si(n)) return;
	let a = [], o = 0;
	for (let e of i) {
		let { text: t, substituteContext: n, ...r } = e.segment.textShapeRequest, i = ms({
			...r,
			measure: !1,
			clusterGeometry: !1
		}), s = i === void 0 ? void 0 : fs(e.segment.text.length, i * Math.max(1, e.segment.text.length)), c = s === void 0 ? void 0 : fs(s, e.segment.textShapeRequest.substituteContext?.text.length ?? e.segment.text.length), l = c === void 0 ? void 0 : fs(o, c);
		if (l === void 0) return;
		o = l, a.push({ additionalWorkUtf16: c });
	}
	for (let e = 0; e < i.length; e++) {
		let t = i[e], n = t.segment.textShapeRequest, o = a[e];
		o.shape = r.shape({
			...n,
			measure: !1,
			clusterGeometry: !1
		});
		let { text: s, substituteContext: c, ...l } = n, u = ms({
			...l,
			measure: !0,
			clusterGeometry: !1,
			fontHint: "eastAsia"
		}), d = ms(l);
		if (u === void 0 || d === void 0) return;
		let f = 0, p = [];
		for (let e of o.shape.spans) {
			let t = Object.freeze(r.exactLocalFaces(e.font.requestedFamily).map((e) => Object.freeze({
				resolvedFamily: e.resolvedFamily,
				weight: e.weight,
				style: e.style,
				...e.coverageProbeFamily ? { coverageProbeFamily: e.coverageProbeFamily } : {}
			})));
			p.push(t);
			let n = ms({
				route: e.fontRoute,
				faces: t,
				requestedFamily: e.font.requestedFamily,
				resourceIdentity: e.font.resourceIdentity,
				weight: e.font.weight,
				style: e.font.style
			}), i = n === void 0 ? void 0 : fs(f, n);
			if (i === void 0) return;
			f = i;
		}
		o.faces = Object.freeze(p);
		let m = fs(4 * (u + d), 8 * f + 30 + 5), h = m === void 0 ? void 0 : fs(o.additionalWorkUtf16, m * t.ranges.length);
		if (h === void 0) return;
		o.additionalWorkUtf16 = h;
	}
	if (!i.some((e, t) => {
		let n = a[t], r = 0;
		return e.ranges.some((e) => {
			for (; r < n.shape.spans.length && n.shape.spans[r].end <= e.start;) r++;
			let t = n.shape.spans[r];
			return t?.font.source === "local" && t.font.resourceIdentity?.startsWith("office-local:") && n.faces[r].some((e) => e.resolvedFamily === t.font.resolvedFamily && e.weight === t.font.weight && e.style === t.font.style && e.coverageProbeFamily);
		});
	})) return;
	let s = i.map((e, t) => ({
		request: e.segment.textShapeRequest,
		ranges: e.ranges,
		additionalWorkUtf16: a[t].additionalWorkUtf16
	})), c = r.acquireContextualAdvances(s);
	if (!(!c || c.length !== i.length || c.some((e, t) => e.clusters.length !== i[t].ranges.length || !Number.isFinite(e.shape.advancePt) || e.shape.spans.length !== a[t].shape.spans.length || e.shape.spans.some((e, n) => {
		let r = a[t].shape.spans[n];
		return e.start !== r.start || e.end !== r.end || e.text !== r.text || e.fontRoute.fingerprint !== r.fontRoute.fingerprint || e.fontRoute.familyList !== r.fontRoute.familyList || e.fontRoute.scope !== r.fontRoute.scope || e.font.resourceIdentity !== r.font.resourceIdentity || e.font.resolvedFamily !== r.font.resolvedFamily || e.font.requestedFamily !== r.font.requestedFamily || e.font.weight !== r.font.weight || e.font.style !== r.font.style;
	}) || e.clusters.some((e, n) => !Number.isFinite(e.offsetPt) || !Number.isFinite(e.advancePt) || e.range.start !== i[t].ranges[n].start || e.range.end !== i[t].ranges[n].end)))) for (let e = 0; e < i.length; e++) {
		let { segment: t, ranges: n, pairs: o } = i[e], s = c[e], l = t.textShapeRequest, u = [], d = 0;
		for (let t = 0; t < n.length; t++) {
			let i = n[t], c = o[t];
			for (; d < s.shape.spans.length && s.shape.spans[d].end <= i.start;) d++;
			let f = s.shape.spans[d];
			if (!f || f.start > i.start || f.end < i.end || f.font.source !== "local" || !f.font.resourceIdentity?.startsWith("office-local:")) continue;
			let p = a[e].faces[d].find((e) => e.resolvedFamily === f.font.resolvedFamily && e.weight === f.font.weight && e.style === f.font.style);
			if (!p?.coverageProbeFamily || !r.ownsGlyphs({
				text: c + "一",
				weight: f.font.weight,
				style: f.font.style,
				coverageProbeFamily: p.coverageProbeFamily
			}) || !r.sameGlyphRaster({
				text: c + "一",
				route: f.fontRoute,
				faceFamily: p.resolvedFamily,
				weight: f.font.weight,
				style: f.font.style
			})) continue;
			let m = (e) => r.shape({
				...e,
				measure: !0,
				clusterGeometry: !1
			}), h = m(ks(l, i.start, i.end)), g = m({
				...As(l, "一"),
				fontHint: "eastAsia"
			}), _ = m(i.end < l.text.length ? ks(l, i.start, i.end + 1) : As(l, c)), v = m(As(l, c[1]));
			![
				h,
				g,
				_,
				v
			].every((e) => e.spans.length === 1 && e.spans[0].fontRoute.fingerprint === f.fontRoute.fingerprint && e.spans[0].font.resourceIdentity === f.font.resourceIdentity && e.spans[0].font.weight === f.font.weight && e.spans[0].font.style === f.font.style) || !(h.advancePt > 0 && g.advancePt > 0 && v.advancePt > 0) || !su(h.advancePt, g.advancePt) || !su(_.advancePt - v.advancePt, h.advancePt) || !su(s.clusters[t].advancePt, h.advancePt) || u.push({
				end: i.end,
				adjustmentPt: g.advancePt / 2 - h.advancePt
			});
		}
		u.length && (t.punctuationCompressions = Object.freeze([...t.punctuationCompressions ?? [], ...u].sort((e, t) => e.end - t.end).map((e) => Object.freeze(e))));
	}
}
function lu(e) {
	if (e.length !== 1) return;
	let t = e[0];
	if (t.type !== "text" || t.rtl === !0 || t.cs === !0 || !t.text || t.smallCaps || t.allCaps || t.vertAlign != null || t.text.startsWith(" ") || !/\p{Letter}/u.test(t.text)) return;
	let n = !1, i = !1;
	for (let e = 0; e < t.text.length;) {
		let a = t.text.codePointAt(e), o = String.fromCodePoint(a), s = r(a);
		if (o !== " " && !(o === "." && e + 1 === t.text.length)) {
			if (!/\p{Letter}/u.test(o) || s !== "L" && s !== "R" && s !== "AL") return;
			n ||= s === "L", i ||= s === "R" || s === "AL";
		}
		e += o.length;
	}
	if (!(!i || !n && !t.text.endsWith("."))) return t.text;
}
function uu(e, t, n) {
	let r = n.nativeUnitMinimumBandPt, i = n.layoutServices?.text;
	if (r === void 0 || !i?.acquireProjectableNativeUnits || !i.shapeDirected || t === void 0) return e;
	let a = ki(), o = wi([{
		text: t,
		rtl: !1,
		digitsAsAN: !1
	}], !0);
	if (!o) return e;
	let s = [];
	for (let e of o) {
		let n = t.slice(e.startUTF16, e.endUTF16);
		if (/^ +$/u.test(n) && s.length > 0) {
			s[s.length - 1].end = e.endUTF16;
			continue;
		}
		s.push({
			start: e.startUTF16,
			end: e.endUTF16,
			baseDirection: e.level & 1 ? "rtl" : "ltr"
		});
	}
	if (s.length < 2) return e;
	let c = [], l = 0, u = !1, d = 0;
	for (let n of e) {
		if (!("text" in n) || !n.textShapeRequest || n.metricOnly || n.ruby || n.tateChuYoko || n.vertAlign != null || n.script === "eastAsia" || n.latinSpaceCompressionEligible || n.mixedSpaceAverageWidthRatio !== void 0 || n.widthBalanceSpaceSequence || n.fitTextRegionIndex !== void 0 || n.verticalRun || n.optionalHyphen || n.optionalHyphenBreaks || n.emphasisMark || n.semanticSlotSpans || (n.charSpacing ?? 0) !== 0 || (n.charScale ?? 1) !== 1 || n.autoSpaceBeforePt !== void 0 || n.punctuationCompressions?.length) return e;
		let r = n.textShapeRequest;
		if (r.substituteContext?.text !== t || r.substituteContext.offset !== l || t.slice(l, l + n.text.length) !== n.text) return e;
		let i = l + n.text.length;
		for (; s[d] && s[d].end <= l;) d++;
		let a = d, o;
		for (; a < s.length && s[a].start < i; a++) {
			let d = s[a], f = Math.max(l, d.start), p = Math.min(i, d.end);
			if (f >= p) continue;
			/[^ ]/u.test(t.slice(f, p)) && (o === void 0 ? o = d.baseDirection : u ||= o !== d.baseDirection);
			let m = f - l, h = p - l, g = n.text.slice(m, h);
			if (!g.trimEnd() || g.replace(/ +$/u, "").includes(" ")) return e;
			c.push({
				...n,
				...Fc,
				...J(n, m, h),
				text: g,
				measuredWidth: 0,
				joinPrev: m > 0 ? !0 : n.joinPrev,
				textShapeRequest: {
					...ks(r, m, h),
					baseDirection: d.baseDirection
				},
				nativeLevelUnit: Object.freeze({
					sourceText: t,
					...d
				})
			});
		}
		d = Math.max(d, a - 1), l = i;
	}
	if (!u || l !== t.length || typeof Intl > "u" || typeof Intl.Segmenter != "function") return e;
	let f = new Intl.Segmenter(void 0, { granularity: "grapheme" }).segment(t)[Symbol.iterator](), p = 0, m = (e) => {
		for (; p < e;) {
			let e = f.next();
			if (p = e.done ? t.length : e.value.index, e.done) break;
		}
		return p === e;
	}, h = 0;
	for (let n of c) {
		let r = n.textShapeRequest.substituteContext.offset, i = r + n.text.length;
		if (r !== h || t.slice(r, i) !== n.text || !m(r) || !m(i)) return e;
		h = i;
	}
	if (h !== t.length) return e;
	let g = c.map((e) => ({
		...e.textShapeRequest,
		baseDirection: e.nativeLevelUnit.baseDirection,
		measure: !0,
		clusterGeometry: "spaces"
	})), _ = i.acquireProjectableNativeUnits(g);
	if (!_) return e;
	if (_.length !== c.length) throw TypeError("Native unit source bundle cardinality mismatch");
	let v = 0;
	for (let t = 0; t < c.length; t++) {
		let n = c[t], i = _[t], a = i.shape;
		if (n.nativeLevelUnit.baseDirection === "rtl" && n.text.endsWith(" ")) {
			if (!Ms(g[t], a, i.visiblePrefix)) return e;
			n.nativeVisiblePrefix = i.visiblePrefix;
		}
		if (a.nativeBaseDirection !== n.nativeLevelUnit.baseDirection || a.spans.map((e) => e.text).join("") !== n.text) throw TypeError("Native unit source/receipt mismatch");
		if (!Number.isFinite(a.advancePt) || a.advancePt < 0 || a.spans.some((e) => e.fontRoute.fingerprint !== n.fontRoute?.fingerprint) || (n.joinPrev || (v = 0), v += a.advancePt, !eu(v, r))) return e;
	}
	return Ai(a, ki()) ? c : e;
}
function du(e, t) {
	return t !== !0 && (e === "deletion" || e === "moveFrom");
}
function fu(e, t) {
	if (e.type !== "text" && e.type !== "field") return;
	let n = e;
	if (n.optionalHyphen || n.ruby || n.noteRef || n.fitTextVal != null || n.noBreakRanges?.length || n.noBreakBefore || n.noBreakAfter || n.eastAsianVert || n.spaceAdvancePt !== void 0 || n.listLabel !== void 0) return;
	let r = e.type === "text" ? e.text : ec(e, t), { type: i, ...a } = e;
	return {
		...a,
		type: "text",
		text: r,
		isLink: "isLink" in e ? e.isLink : !1,
		hyperlink: "hyperlink" in e ? e.hyperlink : null
	};
}
function pu(e, t) {
	let n = e.typographyInput, r = (e, t) => e?.status === "valid" && e.value !== null ? e.value : t, i = {
		fontSize: e.fontSize,
		fontFamily: e.fontFamily,
		fontFamilyHighAnsi: e.fontFamilyHighAnsi,
		fontFamilyEastAsia: e.fontFamilyEastAsia,
		fontFamilyCs: e.fontFamilyCs,
		fontSlots: e.fontSlots,
		fontHint: e.fontHint,
		fontSizeCs: e.fontSizeCs,
		bold: e.bold,
		italic: e.italic,
		boldCs: e.boldCs,
		italicCs: e.italicCs,
		rtl: e.rtl,
		cs: e.cs,
		langBidi: e.langBidi,
		langEastAsia: e.langEastAsia,
		vertAlign: r(n?.verticalAlign, e.vertAlign ?? void 0),
		position: r(n?.positionPt, e.position),
		charSpacing: n?.characterSpacingPt ?? e.charSpacing,
		charScale: n?.characterScale ?? e.charScale,
		kerning: n?.kerningThresholdPt ?? e.kerning,
		snapToGrid: n?.snapToGrid ?? e.snapToGrid,
		allCaps: e.allCaps,
		smallCaps: e.smallCaps,
		underline: e.underline,
		underlineStyle: e.underlineStyle,
		underlineColor: e.underlineColor,
		strikethrough: e.strikethrough,
		doubleStrikethrough: e.doubleStrikethrough,
		color: e.color,
		colorAuto: e.colorAuto,
		background: e.background,
		highlight: e.highlight,
		emphasisMark: e.emphasisMark,
		border: e.border ? {
			...e.border,
			val: n?.border?.val.value ?? e.border.style,
			themeColor: n?.border?.themeColor.value || void 0,
			themeTint: n?.border?.themeTint.value || void 0,
			themeShade: n?.border?.themeShade.value || void 0,
			shadow: r(n?.border?.shadow, void 0),
			frame: r(n?.border?.frame, void 0)
		} : void 0,
		hyperlink: e.hyperlink,
		hyperlinkAnchor: e.hyperlinkAnchor,
		revision: t.showTrackedChanges === !0 && e.revision ? {
			kind: e.revision.kind,
			color: t.revisionAuthorColor?.(e.revision.author) ?? "#C00000"
		} : void 0,
		textBoxLineFloor: e.textBoxLineFloor,
		textBoxVertical: e.textBoxVertical
	};
	return JSON.stringify(i, (e, t) => t && typeof t == "object" && !Array.isArray(t) ? Object.fromEntries(Object.entries(t).filter(([, e]) => e != null).sort(([e], [t]) => e < t ? -1 : +(e > t))) : t);
}
function mu(e, t, n) {
	let r = /* @__PURE__ */ new Map(), i = -1, a, o, s = [], c = [], l = [], u = 0, d = () => {
		if (o && c.length > 1) {
			let e = s.join("");
			r.set(i, {
				run: Object.freeze({
					...o,
					text: e,
					...o.typographyInput ? { typographyInput: Object.freeze({
						...o.typographyInput,
						sourceText: e
					}) } : {}
				}),
				sources: Object.freeze(c),
				optionalHyphens: Object.freeze(l)
			});
		}
		i = -1, o = void 0, s = [], c = [], l = [], u = 0;
	};
	for (let [r, f] of e.entries()) {
		let e = f.revision?.kind;
		if (du(e, t.showTrackedChanges)) continue;
		if (o && f.type === "text" && "optionalHyphen" in f && f.optionalHyphen) {
			l.push(Object.freeze({
				offset: u,
				runIndex: r,
				run: f
			})), c.push(Object.freeze({
				runIndex: r,
				start: u,
				end: u
			}));
			continue;
		}
		let p = fu(f, t), m = p ? t.layoutServices?.text.sourceScopeKey?.({
			text: n(p.text, p),
			fontSizePt: p.fontSize,
			fonts: p.fontSlots?.direct ?? {
				ascii: p.fontFamily,
				highAnsi: p.fontFamilyHighAnsi ?? p.fontFamily,
				eastAsia: p.fontFamilyEastAsia ?? p.fontFamily,
				complexScript: p.fontFamilyCs ?? p.fontFamily
			},
			themeFonts: p.fontSlots?.theme,
			themeFontPresence: p.fontSlots?.themePresent,
			weight: (p.rtl || p.cs ? p.boldCs : p.bold) ? 700 : 400,
			style: (p.rtl || p.cs ? p.italicCs : p.italic) ? "italic" : "normal",
			complexScript: p.rtl === !0 || p.cs === !0,
			fontHint: p.fontHint,
			eastAsiaLanguage: p.langEastAsia
		}) : void 0, h = p ? JSON.stringify([pu(p, t), m === "mixed" ? r : m ?? null]) : void 0;
		if ((!p || h !== a) && d(), a = h, !p) continue;
		o ||= (i = r, p), s.push(p.text);
		let g = n(p.text, p);
		c.push(Object.freeze({
			runIndex: r,
			start: u,
			end: u + g.length
		})), u += g.length;
	}
	return d(), r;
}
function hu(e) {
	if (e === void 0) return "0";
	let t = String(e).trim();
	return /^[+-]?\d+$/.test(t) ? BigInt(t).toString() : t;
}
function gu(e, t) {
	let n = [];
	for (let r = 0; r < e.length;) {
		let i = e[r];
		if (i.fitTextValTwips === void 0) {
			r += 1;
			continue;
		}
		let a = r + 1, o = hu(i.fitTextId);
		for (; a < e.length && e[a].fitTextValTwips !== void 0 && hu(e[a].fitTextId) === o;) a += 1;
		let s = 0, c = 0;
		for (let t = r; t < a; t += 1) {
			let n = e[t];
			s += n.naturalWidthPx * (n.charScale ?? 1), c += n.charCount;
		}
		let l = i.fitTextValTwips / 20 * t, u = c > 1 ? (l - s) / (c - 1) : 0, d = l - s - Math.max(0, c - 1) * u;
		n.push({
			start: r,
			end: a,
			targetPx: l,
			naturalPx: s,
			charCount: c,
			perGapPx: u,
			trailingPadPx: d
		}), r = a;
	}
	return n;
}
var _u = new Set([
	"+",
	"-",
	"−",
	"=",
	"±",
	"×",
	"÷"
]);
function vu(e) {
	return _u.has(e) ? ` ${e} ` : e;
}
function Y(e) {
	return e.map((e) => {
		switch (e.kind) {
			case "run": return vu(e.text);
			case "fraction": return `${Y(e.num)}/${Y(e.den)}`;
			case "sup": return `${Y(e.base)}^${Y(e.sup ?? [])}`;
			case "sub": return `${Y(e.base)}_${Y(e.sub ?? [])}`;
			case "subSup": return `${Y(e.base)}_${Y(e.sub ?? [])}^${Y(e.sup ?? [])}`;
			case "nary": return `${e.op}${Y(e.sub ?? [])}${Y(e.sup ?? [])}${Y(e.body)}`;
			case "delimiter": return `${e.begChar}${e.items.map(Y).join(",")}${e.endChar}`;
			case "radical": return `${e.index?.length ? Y(e.index) : ""}√${Y(e.radicand)}`;
			case "limit": return `${Y(e.base)}${Y(e.lower ?? [])}${Y(e.upper ?? [])}`;
			case "array": return e.rows.map((e) => e.map(Y).join(" ")).join(" ");
			case "groupChr": return `${e.char}${Y(e.base)}`;
			case "bar":
			case "box":
			case "borderBox": return Y(e.base);
			case "accent": return `${e.char}${Y(e.base)}`;
			case "func": return `${Y(e.name)}(${Y(e.arg)})`;
			case "group": return Y(e.items);
			case "phant": return e.show ? Y(e.base) : "";
			case "sPre": return `${Y(e.sub)}${Y(e.sup)}${Y(e.base)}`;
		}
	}).join("").replace(/[ \t]{2,}/g, " ");
}
function yu(e) {
	if (e.startsWith("libreoffice")) return {
		externalLeading: !e.endsWith("-no-leading"),
		msWordGridMetrics: e.startsWith("libreoffice-ms-word-grid")
	};
}
var bu = {
	word: /* @__PURE__ */ new WeakMap(),
	plain: /* @__PURE__ */ new WeakMap(),
	libreoffice: /* @__PURE__ */ new WeakMap(),
	"libreoffice-no-leading": /* @__PURE__ */ new WeakMap(),
	"libreoffice-ms-word-grid": /* @__PURE__ */ new WeakMap(),
	"libreoffice-ms-word-grid-no-leading": /* @__PURE__ */ new WeakMap()
}, xu = 1024, Su = /* @__PURE__ */ new Map(), Cu = Object.freeze([]);
function wu(e, t, n) {
	if (!e?.trim()) return Cu;
	let r = `${t}|${n}|${e}`, i = Su.get(r);
	if (i !== void 0) return i;
	let a = [
		["office-mac"],
		["macos-system", "macos-supplemental"],
		["published-open-font"]
	], o = Cu;
	for (let r of a) {
		let i = r.flatMap((r) => j(e, {
			source: r,
			weight: t,
			style: n
		}));
		if (i.length > 0) {
			o = Object.freeze(i);
			break;
		}
	}
	return Su.set(r, o), Su.size > xu && Su.delete(Su.keys().next().value), o;
}
function Tu(e, t, n) {
	let r;
	for (let i of wu(e, t, n)) {
		let e = i.decoration;
		if (!e || !(i.unitsPerEm > 0)) return;
		let [t, n, a, o] = e;
		if (!(n > 0) || !(o > 0) || !(a > 0)) return;
		let s = i.unitsPerEm, c = {
			underlineTopEm: -t / s,
			underlineThicknessEm: n / s,
			strikeTopEm: -a / s,
			strikeThicknessEm: o / s
		};
		if (r && Object.keys(c).some((e) => r[e] !== c[e])) return;
		r = Object.freeze(c);
	}
	return r;
}
function Eu(e, t = "word") {
	let n = bu[t], r = n.get(e);
	if (r !== void 0) return r;
	let i = t === "plain", a = yu(t), o = a ? rr({
		unitsPerEm: e.unitsPerEm,
		hhea: e.hhea,
		...e.win ? { win: e.win } : {},
		...e.typoMetrics ? { typo: e.typoMetrics } : {}
	}) : void 0, s = o && a ? sr(o, a, e.farEastCodePage === !0) : e.farEastCodePage == null ? null : $r({
		unitsPerEm: e.unitsPerEm,
		hheaAscent: e.hhea[0],
		hheaDescent: e.hhea[1],
		hheaLineGap: e.hhea[2],
		winAscent: e.win?.[0],
		winDescent: e.win?.[1],
		farEastCodePage: i ? !1 : e.farEastCodePage
	}), c = s?.lineHeightRatio != null && s.designAscentRatio != null && s.designDescentRatio != null ? Object.freeze({
		lineHeightRatio: s.lineHeightRatio,
		farEastCodePage: e.farEastCodePage === !0,
		designAscentRatio: s.designAscentRatio,
		designDescentRatio: s.designDescentRatio
	}) : null;
	return n.set(e, c), c;
}
function Du(e, t = "word") {
	let n = e.map((e) => Eu(e, t)), r = n[0];
	if (!(!r || n.some((e) => !e || e.farEastCodePage !== r.farEastCodePage || e.lineHeightRatio !== r.lineHeightRatio || e.designAscentRatio !== r.designAscentRatio || e.designDescentRatio !== r.designDescentRatio))) return r;
}
function Ou(e, t = 400, n = "normal", r = "word") {
	return Du(wu(e, t, n), r);
}
function ku(e, t = 400, n = "normal") {
	let r = wu(e, t, n).map((e) => e.xAvgCharWidth != null && e.xAvgCharWidth > 0 ? e.xAvgCharWidth / e.unitsPerEm : void 0);
	return r[0] != null && r.every((e) => e === r[0]) ? r[0] : void 0;
}
var Au = /^[\p{Script=Han}\p{Script=Hiragana}\p{Script=Katakana}\p{Script=Hangul}]$/u, ju = /^\p{L}$/u, Mu = /^[\p{Grapheme_Extend}\u200D]+$/u, Nu = /^\p{Script=Latin}$/u;
function Pu(e) {
	if (e >= "0" && e <= "9" && e.length === 1) return "digit";
	if (!ju.test(e)) return;
	if (Au.test(e)) return "eastAsian";
	let t = e.codePointAt(0);
	if (!(t >= 65280 && t <= 65519)) return Nu.test(e) ? "latinLetter" : void 0;
}
function Fu(e, t, n, r) {
	if (e === void 0 || t === void 0) return !1;
	let i = e === "eastAsian" ? t : t === "eastAsian" ? e : void 0;
	return i === void 0 || i === "eastAsian" ? !1 : i === "digit" ? r !== !1 : n !== !1;
}
function Iu(e) {
	return e.fitTextRegionIndex === void 0 && !e.ruby && !e.tateChuYoko && e.script !== "complexScript" && e.optionalHyphen === void 0 && !e.optionalHyphenGlyph;
}
function Lu(e) {
	for (let t of e) return t;
}
function Ru(e) {
	if (e.length === 0) return;
	let t = b(e);
	return String.fromCodePoint(e.codePointAt(t.at(-1) ?? 0));
}
function zu(e, t, n) {
	return {
		...e,
		...Fc,
		text: e.text.slice(t, n),
		measuredWidth: 0,
		...J(e, t, n),
		...t > 0 ? {
			joinPrev: void 0,
			hardJoinPrev: void 0,
			explicitBreakBefore: void 0,
			breakBefore: !0
		} : {}
	};
}
function Bu(e, t) {
	if (t.autoSpaceDE === !1 && t.autoSpaceDN === !1) return;
	let n = Zl(t), r = Ar(n, t.characterSpacingControl) && !n.lineWrapLikeWord6 && t.verticalCJK !== !0, i = (e, n) => e !== void 0 && n !== void 0 && Fu(Pu(e), Pu(n), t.autoSpaceDE, t.autoSpaceDN), a, o;
	for (let t = 0; t < e.length; t += 1) {
		let n = e[t], r = [];
		if (!("text" in n) || !Iu(n)) o = void 0;
		else if (n.text.length > 0) {
			let e = n.seaBreaks !== void 0;
			for (let t of [0, ...b(n.text)]) {
				let a = String.fromCodePoint(n.text.codePointAt(t));
				Mu.test(a) || (!e && t > 0 && i(o, a) && r.push(t), o = a);
			}
		}
		if (r.length === 0) {
			a?.push(n);
			continue;
		}
		a ??= e.slice(0, t);
		let s = n, c = [
			0,
			...r,
			s.text.length
		];
		for (let e = 0; e + 1 < c.length; e += 1) a.push(zu(s, c[e], c[e + 1]));
	}
	if (a) {
		e.length = 0;
		for (let t of a) e.push(t);
	}
	let s;
	for (let t of e) {
		if (!("text" in t) || !Iu(t)) {
			s = void 0;
			continue;
		}
		if (t.autoSpaceBeforePt = void 0, t.autoSpaceCompressible = void 0, t.text.length === 0 || Mu.test(t.text)) continue;
		let e = s ? Ru(s.text) : void 0, n = Lu(t.text);
		s && i(e, n) && (t.autoSpaceBeforePt = Dr((Pu(e) === "eastAsian" ? s : t).fontSize), r && !((s.charSpacing ?? 0) > 0) && !((t.charSpacing ?? 0) > 0) && (t.autoSpaceCompressible = !0)), s = t;
	}
}
function Vu(e, t, n = !1) {
	if (t) return e?.plainLineBoxes === !0 ? "plain" : "word";
	if (e?.libreOfficeLineBoxes !== !0 || n) return "word";
	let r = e.libreOfficeNoExternalLeading === !0 ? "-no-leading" : "";
	return e.libreOfficeMsWordGridMetrics === !0 ? `libreoffice-ms-word-grid${r}` : `libreoffice${r}`;
}
var Hu = /* @__PURE__ */ new Map(), Uu = /* @__PURE__ */ new WeakMap();
function Wu(e) {
	if (e.wordLineHeightRatio === void 0 || e.wordAscentRatio === void 0 || e.wordDescentRatio === void 0) return e;
	let t = Uu.get(e);
	return t || (t = Object.freeze({
		...e,
		lineHeightRatio: e.wordLineHeightRatio,
		designAscentRatio: e.wordAscentRatio,
		designDescentRatio: e.wordDescentRatio,
		...e.eastAsianLineHeightRatio === void 0 ? {} : { eastAsianLineHeightRatio: e.wordLineHeightRatio }
	}), Uu.set(e, t)), t;
}
function Gu(e, t) {
	if (t === "word") return e && Wu(e);
	let n = yu(t);
	if (!n || !e || e.normalLineGapRatio === void 0 || e.normalAscentRatio === void 0 || e.normalDescentRatio === void 0) return e;
	let r = Hu.get(t);
	r || Hu.set(t, r = /* @__PURE__ */ new WeakMap());
	let i = r.get(e);
	if (!i) {
		let t = sr({
			normalAscentRatio: e.normalAscentRatio,
			normalDescentRatio: e.normalDescentRatio,
			normalLineGapRatio: e.normalLineGapRatio
		}, n, e.farEastCodePage === !0);
		i = Object.freeze({
			...e,
			...t,
			...e.eastAsianLineHeightRatio === void 0 ? {} : { eastAsianLineHeightRatio: t.lineHeightRatio }
		}), r.set(e, i);
	}
	return i;
}
var Ku = /[\p{Script=Han}\p{Script=Hiragana}\p{Script=Katakana}\p{Script=Hangul}\p{Script=Bopomofo}]/u;
function qu(e, t, n) {
	for (let r of n === "italic" ? ["italic", "normal"] : ["normal", "italic"]) {
		let n = e.filter((e) => e.style === r);
		if (n.length === 0) continue;
		let i = n.filter((e) => e.weight < t).sort((e, t) => t.weight - e.weight), a = n.filter((e) => e.weight > t).sort((e, t) => e.weight - t.weight), o = n.filter((e) => e.weight === t);
		return (t > 500 ? [
			...o,
			...a,
			...i
		] : t < 400 ? [
			...o,
			...i,
			...a
		] : [
			...o,
			...a.filter((e) => e.weight <= 500),
			...i,
			...a.filter((e) => e.weight > 500)
		])[0];
	}
}
function Ju(e, t, n = "word") {
	let r = Ou(e.requestedFamily, e.weight, e.style, n);
	if (r || !t?.text.sameGlyphRaster || e.source !== "native" || e.installedFamily !== !0) return r;
	let i = qu(t.text.exactLocalFaces?.(e.requestedFamily) ?? [], e.weight, e.style);
	if (!i?.coverageProbeFamily || !t.text.ownsGlyphs) return;
	let a = Ou(e.requestedFamily, i.weight, i.style, n), o = Ku.test(t.probe) ? "国あ" : "Hxg", s = (n) => t.text.ownsGlyphs({
		text: n,
		weight: e.weight,
		style: e.style,
		coverageProbeFamily: i.coverageProbeFamily,
		...t.baseDirection === void 0 ? {} : { baseDirection: t.baseDirection }
	});
	return a && s(o) && s(t.probe) && t.text.sameGlyphRaster({
		text: o,
		weight: e.weight,
		style: e.style,
		route: e.route,
		faceFamily: i.resolvedFamily,
		...t.baseDirection === void 0 ? {} : { baseDirection: t.baseDirection }
	}) ? a : void 0;
}
function Yu(e, t, n, r = !0, i, a = "word") {
	let o = (n || t?.designAscentRatio == null) && (t?.lineHeightRatio != null || t?.designAscentRatio != null || t?.eastAsianLineHeightRatio != null) ? Gu(t, a) : void 0, s = n && r && !o && pd(e) ? Ju(e, i, a) : void 0;
	return {
		resourceMetric: o,
		referenceMetric: s,
		lineMetric: o ?? s
	};
}
function Xu(e, t, n, r = !0) {
	if (r && e.requiresGlyphCoverage && !kn(e, t, n)) return !1;
	let i = e.unicodeRanges;
	if (i === void 0 || t.length === 0) return !0;
	for (let e of t) {
		let t = e.codePointAt(0), n = 0, r = i.length;
		for (; n < r;) {
			let e = n + r >>> 1;
			i[e][1] < t ? n = e + 1 : r = e;
		}
		if (n >= i.length || i[n][0] > t) return !1;
	}
	return !0;
}
function Zu(e, t, n, r = !0) {
	if (nd(e) !== id(t) || !Xu(e, n, t.route, r)) return !1;
	let i = e.sourceIdentity;
	return t.source === "embedded" ? t.resourceIdentity === void 0 ? i?.startsWith("embedded:") === !0 : i === t.resourceIdentity : t.source === "local" || t.source === "substitute" || t.source === "source" || t.source === "css" ? i !== void 0 && i === t.resourceIdentity : !1;
}
function Qu(e, t) {
	return e.farEastCodePage === t.farEastCodePage && e.lineHeightRatio === t.lineHeightRatio && e.designAscentRatio === t.designAscentRatio && e.designDescentRatio === t.designDescentRatio && e.lineGapRatio === t.lineGapRatio && e.eastAsianLineHeightRatio === t.eastAsianLineHeightRatio && e.fontBoxRatio === t.fontBoxRatio;
}
var $u = /* @__PURE__ */ new WeakMap();
function ed(e, t, n) {
	return `${Ut(e)}\0${t}\0${n}`;
}
var td = /* @__PURE__ */ new WeakMap();
function nd(e) {
	let t = td.get(e);
	if (t !== void 0) return t;
	let n = ed(e.family, e.weight ?? 400, e.style ?? "normal");
	return Object.isFrozen(e) && td.set(e, n), n;
}
var rd = /* @__PURE__ */ new WeakMap();
function id(e) {
	let t = rd.get(e);
	if (t !== void 0) return t;
	let n = ed(e.resolvedFamily, e.weight, e.style);
	return Object.isFrozen(e) && rd.set(e, n), n;
}
function ad(e) {
	let t = Object.isFrozen(e);
	if (t) {
		let t = $u.get(e);
		if (t) return t;
	}
	let n = Object.values(e), r = t && n.every((e) => Object.isFrozen(e)), i = /* @__PURE__ */ new Map();
	for (let e of n) {
		let t = nd(e), n = i.get(t);
		n ? n.push(e) : i.set(t, [e]);
	}
	for (let e of i.values()) Object.freeze(e);
	return r && $u.set(e, i), i;
}
function od(e, t, n, r = !0) {
	if (t.source === "native") {
		let e = t.routeLineMetric;
		return e && Xu(e, n, t.route, r) ? e : void 0;
	}
	if (t.source !== "embedded" && t.source !== "local" && t.source !== "substitute" && t.source !== "source" && t.source !== "css") return;
	let i = e.get(id(t)) ?? [], a;
	for (let e of i) Zu(e, t, n, r) && (a ??= e);
	if (!a) return;
	let o = !0, s = !0;
	for (let e of i) if (Xu(e, n, t.route, r)) {
		if (!Qu(a, e)) return;
		o &&= cd(a, e), s &&= sd(a, e);
	}
	return ud(a, !o, !s);
}
function sd(e, t) {
	return e.wordLineHeightRatio === t.wordLineHeightRatio && e.wordAscentRatio === t.wordAscentRatio && e.wordDescentRatio === t.wordDescentRatio;
}
function cd(e, t) {
	return e.normalAscentRatio === t.normalAscentRatio && e.normalDescentRatio === t.normalDescentRatio && e.normalLineGapRatio === t.normalLineGapRatio;
}
var ld = [
	/* @__PURE__ */ new WeakMap(),
	/* @__PURE__ */ new WeakMap(),
	/* @__PURE__ */ new WeakMap()
];
function ud(e, t, n) {
	if (t &&= e.normalAscentRatio !== void 0 || e.normalDescentRatio !== void 0 || e.normalLineGapRatio !== void 0, n &&= e.wordLineHeightRatio !== void 0 || e.wordAscentRatio !== void 0 || e.wordDescentRatio !== void 0, !t && !n) return e;
	let r = ld[+!!t + (n ? 2 : 0) - 1], i = r.get(e);
	if (!i) {
		let { normalAscentRatio: a, normalDescentRatio: o, normalLineGapRatio: s, wordLineHeightRatio: c, wordAscentRatio: l, wordDescentRatio: u, ...d } = e;
		i = Object.freeze({
			...d,
			...t ? {} : {
				normalAscentRatio: a,
				normalDescentRatio: o,
				normalLineGapRatio: s
			},
			...n ? {} : {
				wordLineHeightRatio: c,
				wordAscentRatio: l,
				wordDescentRatio: u
			}
		}), r.set(e, i);
	}
	return i;
}
function dd(e, t, n) {
	if (t.source !== "embedded" && t.source !== "local" && t.source !== "substitute") return;
	let r = e.get(id(t)) ?? [], i = `${n} `, a = r.find((e) => Zu(e, t, i))?.averageCharWidthRatio;
	if (!(a == null || a <= 0)) return r.every((e) => !Xu(e, i, t.route) || e.averageCharWidthRatio === a) ? a : void 0;
}
function fd(e) {
	return e?.source === "local" && e.resourceIdentity?.startsWith("office-local:") === !0;
}
function pd(e) {
	return e?.source === "native" && e.installedFamily === !0 || fd(e);
}
function md(e, t) {
	return !t || !(e.get(id(t)) ?? []).some((e) => e.requiresGlyphCoverage);
}
function hd(e, t, n) {
	let r = /* @__PURE__ */ new Map();
	for (let t of e) {
		if (t.fitTextRegionIndex === void 0) continue;
		let e = r.get(t.fitTextRegionIndex) ?? [];
		e.push(t), r.set(t.fitTextRegionIndex, e);
	}
	for (let e of r.values()) {
		let r = e.find((e) => e.fitTextVal !== void 0);
		if (!r || r.fitTextVal === void 0) continue;
		let i = 0, a = 0;
		for (let t of e) i += n(t) * tl(t), a += [...t.text].length;
		let o = gu([{
			fitTextValTwips: r.fitTextVal,
			charCount: a,
			naturalWidthPx: i
		}], t)[0];
		o && e.forEach((t, n) => {
			t.fitTextPerGapPx = o.perGapPx, t.fitTextTrailingPadPx = n === e.length - 1 ? o.trailingPadPx : void 0, t.fitTextRegionStart = n === 0 ? !0 : void 0, t.fitTextRegionEnd = n === e.length - 1 ? !0 : void 0;
		});
	}
}
function gd(e, t) {
	let n = e.fontFamily ?? null;
	return {
		fonts: e.fontSlots?.direct ?? {
			ascii: n,
			highAnsi: e.fontFamilyHighAnsi ?? n,
			eastAsia: e.fontFamilyEastAsia ?? n,
			complexScript: e.fontFamilyCs ?? n
		},
		themeFonts: e.fontSlots?.theme,
		themeFontPresence: e.fontSlots?.themePresent,
		weight: (t ? e.boldCs ?? !1 : e.bold) ? 700 : 400,
		style: (t ? e.italicCs ?? !1 : e.italic) ? "italic" : "normal",
		complexScript: t,
		fontHint: e.fontHint,
		eastAsiaLanguage: e.langEastAsia
	};
}
function _d(e) {
	return [e.fonts, e.themeFonts].some((e) => e && [
		e.ascii,
		e.highAnsi,
		e.eastAsia,
		e.complexScript
	].some(ee));
}
function vd(e, t, n, r) {
	return e.layoutServices?.text.symbolText?.({
		...r,
		text: t
	}) ?? z(t, n);
}
function yd(e, t, n) {
	let r = t, i = t.allCaps || t.smallCaps ? e.toUpperCase() : e, a = r.rtl === !0 || r.cs === !0, o = gd(r, a), s = n.layoutServices?.text.symbolText ? _d(o) : void 0, c = (e, t) => s ?? ee(t) ? vd(n, e, t, o).map((e) => e.text).join("") : e;
	return a ? c(i, r.fontFamilyCs ?? t.fontFamily) : n.layoutServices?.text ? c(i, t.fontFamily) : cc(i).map((e) => c(e.text, e.ea ? r.fontFamilyEastAsia ?? t.fontFamily : t.fontFamily)).join("");
}
function bd(e, t, n) {
	return {
		text: yd(e, t, n),
		offset: 0
	};
}
function xd(e, t, n, r, i, a, o, s = !1) {
	let { environment: c, segs: l, fitTextFragmentEntryByKey: u, fitTextRegionByEntry: d, selectedMetric: f, selectedAverageWidth: p } = e, m = n, h = vs.test(t) ? !0 : void 0, g = m.typographyInput, _ = (e, t) => e?.status === "valid" && e.value !== null ? e.value : t, v = _(g?.verticalAlign, r ?? void 0) ?? null, y = _(g?.positionPt, m.position), b = g?.characterSpacingPt ?? m.charSpacing, x = Ir(b), S = g?.characterScale ?? m.charScale, C = g?.kerningThresholdPt ?? m.kerning, w = g?.snapToGrid ?? m.snapToGrid, T = m.ruby, E = T ? {
		text: T.text,
		fontSizePt: T.fontSizePt,
		...T.hpsRaisePt == null ? {} : { hpsRaisePt: T.hpsRaisePt }
	} : void 0, D = m.revision, O = m.rtl === !0 ? !0 : void 0, k = o === void 0 ? void 0 : u.get(`${i}:${o}`), A = k === void 0 ? void 0 : d.get(k), j = m.hyperlink ? {
		kind: "external",
		url: m.hyperlink
	} : m.hyperlinkAnchor ? {
		kind: "internal",
		ref: m.hyperlinkAnchor
	} : void 0, M = m.rtl === !0 || m.cs === !0, N = m.fontSizeCs ?? n.fontSize, P = m.fontFamilyCs ?? n.fontFamily, F = m.fontFamilyHighAnsi ?? n.fontFamily, I = m.boldCs ?? !1, L = m.italicCs ?? !1, R = m.fontFamilyEastAsia ?? n.fontFamily, z = (M || !!m.rtl) && sc(m.langBidi, !!m.rtl), B = {
		base: n,
		joinPreviousRun: s,
		environment: c,
		segs: l,
		selectedMetric: f,
		selectedAverageWidth: p,
		r: m,
		effectiveVertAlign: v,
		effectivePosition: y,
		effectiveCharacterSpacing: b,
		documentCharacterCompressionApplies: x,
		effectiveCharacterScale: S,
		effectiveKerningThreshold: C,
		effectiveSnapToGrid: w,
		ruby: E,
		revision: D,
		fitTextFragmentEntryIndex: k,
		fitTextRegionIndex: A,
		csFontSize: N,
		csFontFamily: P,
		highAnsiFontFamily: F,
		csBold: I,
		csItalic: L,
		eaFontFamily: R,
		digitsAsAN: z,
		sourceRunIndex: i,
		sourceFragmentIndex: o,
		hyperlink: j,
		rtl: O,
		overflowPunctuationEastAsianRun: h,
		reduced: !1,
		firstSeg: !0,
		gluePending: !1,
		scopeContext: {
			text: a.text,
			cursor: a.offset
		}
	}, V = (e, t, n, r, i = !1, a = !1) => kd(B, e, t, n, r, i, a), te = (e) => c.layoutServices?.text.symbolText ? _d(gd(m, e)) : void 0, H = (e, t) => {
		let r = t === "cs", i = t === "cs" ? P : t === "ea" ? R : n.fontFamily;
		if (te(r) ?? ee(i)) {
			for (let t of vd(c, e, i, gd(m, r))) V(t.text, r, t.mapped ? null : i, void 0, !1, t.mapped);
			return;
		}
		V(e, r, i);
	}, U = (e) => {
		if (c.layoutServices?.text) {
			if (te(!1) ?? ee(n.fontFamily)) {
				H(e, "latin");
				return;
			}
			V(e, !1, n.fontFamily);
			return;
		}
		for (let t of cc(e)) H(t.text, t.ea ? "ea" : "latin");
	}, ne = n.smallCaps ? Zs(t) : [{
		text: t,
		reduced: !1
	}], re = "";
	for (let e of ne) {
		B.reduced = e.reduced, B.gluePending = re.length > 0 && !/\s$/.test(re), re = e.text;
		let t = n.allCaps || n.smallCaps ? e.text.toUpperCase() : e.text;
		for (let e of uc(t)) if (M) if (z) for (let t of lc(e)) H(t, "cs");
		else H(e, "cs");
		else U(e);
	}
}
function Sd(e, t) {
	let n = 0, r = 0;
	for (let i of e) {
		let e = n + i.text.length;
		t[r] === n && (i.joinPrev = void 0, i.explicitBreakBefore = !0, r++);
		let a = r;
		for (; r < t.length && t[r] < e;) r++;
		r > a && (i.explicitBreaks = {
			offsets: t,
			start: a,
			end: r,
			origin: n
		}), n = e;
	}
}
function Cd(e, t, n) {
	Pd(e, n);
	let r = new Set(n.filter((e) => "text" in e && e.ruby).map((e) => e.sourceRunIndex));
	for (let e = 0; e < n.length;) {
		let t = (e) => "text" in e && e.hyperlink?.kind !== "external" && e.fitTextRegionIndex === void 0 && !e.ruby && !e.tateChuYoko && !r.has(e.sourceRunIndex);
		if (!t(n[e])) {
			e++;
			continue;
		}
		let i = e, a = [];
		for (; i < n.length && t(n[i]);) a.push(n[i++]);
		let o = a.map((e) => e.text).join("");
		if (o.includes("-")) {
			let e = [...b(o), o.length], t = 0, n = /* @__PURE__ */ new Set(), r = 0;
			for (let e of a) {
				for (let t of e.noBreakRanges ?? []) n.add(r + t.start), n.add(r + t.end);
				e.hardJoinPrev && n.add(r), r += e.text.length;
			}
			let i = [], s = /* @__PURE__ */ new Set(), c = 0, l, u = (e) => e === "AL" || e === "HL" || e === "NU";
			for (let r of o) {
				let a = de(r.codePointAt(0)), d = c + r.length;
				for (; e[t] <= c;) t++;
				let f = e[t];
				if (r === "-" && f < o.length) {
					s.add(f);
					let e = de(o.codePointAt(f));
					u(l) && u(e) && !(l === "HL" && e !== "HL") && o.codePointAt(f - 1) !== 8205 && !n.has(d) && !n.has(f) && (i.push(f), s.delete(f));
				}
				a !== "CM" && a !== "ZWJ" && (l = a), c = d;
			}
			Sd(a, Object.freeze(i));
			let d = 0;
			for (let e of a) s.has(d) && (e.joinPrev = !0), d += e.text.length;
		}
		e = i;
	}
	for (let e = 0; e < n.length;) {
		let t = n[e];
		if (!("text" in t) || t.hyperlink?.kind !== "external") {
			e += 1;
			continue;
		}
		let r = t.hyperlink.url, i = e, a = [];
		for (; i < n.length;) {
			let e = n[i];
			if (!("text" in e) || e.hyperlink?.kind !== "external" || e.hyperlink.url !== r) break;
			a.push(e), i += 1;
		}
		let o = a.map((e) => e.text).join(""), s = /* @__PURE__ */ new Set(), c = 0;
		for (let e of a) {
			for (let t of e.noBreakRanges ?? []) {
				let e = [t.start, t.end];
				for (let t of e) s.add(c + t);
			}
			c += e.text.length;
		}
		let l = /* @__PURE__ */ new Set();
		for (let e of o.matchAll(/\S+/gu)) {
			let t = e[0], n = e.index, r = new Set(b(t).map((e) => n + e)), i = new Set([...s].filter((e) => e > n && e <= n + t.length).map((e) => e - n)), a = new Set([...r].map((e) => e - n));
			for (let e of qr(t, a, i)) l.add(n + e);
		}
		if (l.size === 0) {
			e = i;
			continue;
		}
		Sd(a, Object.freeze([...l].sort((e, t) => e - t))), e = i;
	}
	if (Zl(t).balanceSingleByteDoubleByteWidth) {
		let e = /* @__PURE__ */ new Map(), t = (t) => {
			let n = t.textLayoutService, r = t.textShapeRequest;
			if (!n || !r) return;
			let i = q(t, 1), a = [
				n.fingerprint,
				t.fontRoute?.fingerprint ?? "implicit-latin",
				t.eaFloorRoute?.fingerprint ?? "implicit-east-asia",
				i,
				t.bold ? 700 : 400,
				t.italic ? "italic" : "normal",
				t.kerning ?? "none"
			].join("|"), o = e.get(a);
			if (o !== void 0) return o;
			let s = n.shape({
				...As(r, " "),
				fontSizePt: i,
				measure: !0,
				clusterGeometry: !1
			}).advancePt, c = n.shape({
				...As(r, "一"),
				fontSizePt: i,
				fontHint: "eastAsia",
				measure: !0,
				clusterGeometry: !1
			}).advancePt;
			if (!Number.isFinite(s) || !Number.isFinite(c) || s < 0 || c <= 0) return;
			let l = c / 2 - s;
			return e.set(a, l), l;
		}, r = [], i = 0, a = () => {
			if (wr(i)) for (let e of r) {
				e.widthBalanceSpaceSequence = !0;
				let n = t(e);
				n !== void 0 && (e.widthBalanceSpaceAdjustmentPt = n);
			}
			r = [], i = 0;
		};
		for (let e of n) {
			if (!("text" in e) || e.script === "complexScript") {
				a();
				continue;
			}
			let t = e.text.length - e.text.replace(/ +$/u, "").length;
			t > 0 && t === e.text.length || a(), t > 0 ? (r.push(e), i += t) : a();
		}
		a();
	}
	for (let e of n) {
		if (!("text" in e) || e.spaceAdvancePt === void 0) continue;
		let t = e.textLayoutService, n = e.textShapeRequest;
		if (!t || !n) continue;
		let r = t.shape({
			...As(n, " "),
			fontSizePt: q(e, 1),
			measure: !0,
			clusterGeometry: !1
		}).advancePt;
		Number.isFinite(r) && (e.widthBalanceSpaceSequence = !0, e.widthBalanceSpaceAdjustmentPt = e.spaceAdvancePt / tl(e) - r);
	}
	for (let e = 1; e < n.length; e++) {
		let t = n[e];
		if (!("text" in t) || t.joinPrev) continue;
		let r = t.text.codePointAt(0);
		if (r === void 0 || !pe.lineStartForbidden.has(r)) continue;
		let i = n[e - 1];
		!("text" in i) || /\s$/.test(i.text) || (t.joinPrev = !0);
	}
	for (let e = 1; e < n.length; e++) {
		let t = n[e];
		if (!("text" in t) || t.joinPrev || t.text[0] !== " " && t.text[0] !== "　") continue;
		let r = n[e - 1];
		if (!("text" in r)) continue;
		let i = t.sourceRunIndex === r.sourceRunIndex, a = Lr(r.text, t.text);
		!i && !a || (t.joinPrev = !0);
	}
	for (let e = 1; e < n.length; e++) {
		let t = n[e];
		if (!("text" in t) || t.joinPrev || t.explicitBreakBefore || t.text.length === 0) continue;
		let r = n[e - 1];
		if (!("text" in r) || r.text.length === 0 || /\s$/u.test(r.text) || /^\s/u.test(t.text)) continue;
		let i = [...r.text].at(-1), a = [...t.text][0], o = i?.codePointAt(0), s = a?.codePointAt(0);
		o === void 0 || s === void 0 || o === 8203 || s === 8203 || y(r.text) || y(t.text) || tc(r.text) || tc(t.text) || le(o, s) && (t.joinPrev = !0);
	}
	let i = /* @__PURE__ */ new Set();
	for (let e of n) !("text" in e) || e.fitTextRegionIndex === void 0 || (i.has(e.fitTextRegionIndex) ? e.joinPrev = !0 : (e.fitTextRegionStart = !0, i.add(e.fitTextRegionIndex)));
	for (let e = 0; e < n.length; e += 1) {
		let t = n[e];
		if (!("text" in t)) continue;
		let r = t.optionalHyphenBreaks?.at(-1)?.offset === t.text.length;
		if (!t.optionalHyphen && !r) continue;
		let i = n[e - 1], a = n[e + 1];
		t.optionalHyphen && i && "text" in i && !/\s$/u.test(i.text) && (t.joinPrev = !0), a && "text" in a && !/^\s/u.test(a.text) && (a.joinPrev = !0);
	}
	for (let e = 0; e < n.length;) {
		let t = n[e];
		if (!("text" in t)) {
			e++;
			continue;
		}
		let r = e + 1, i = t.optionalHyphen !== void 0 || !!t.optionalHyphenBreaks?.length;
		for (; r < n.length;) {
			let e = n[r];
			if (!("text" in e) || !e.joinPrev) break;
			i ||= e.optionalHyphen !== void 0 || !!e.optionalHyphenBreaks?.length, r++;
		}
		if (i) for (let t = e; t < r; t++) n[t].optionalHyphenWord = !0;
		e = r;
	}
	el(n), cu(e, t, n);
}
function wd(e) {
	return e.some((e) => e.textBoxVertical === !0);
}
function Td(e, t) {
	t.layoutServices?.text.libreOfficeLineBoxes === !0 && t.wordLineBoxes === void 0 && wd(e) && (t = {
		...t,
		wordLineBoxes: !0
	});
	let n = [], r = t.layoutServices?.text.fontMetrics ?? t.layoutServices?.text.localMetrics ?? {}, i, a = () => i ??= ad(r), o = (e, t) => {
		if (e) return od(a(), e, t);
	}, s = /* @__PURE__ */ new Map(), c = (e, t) => {
		if (!e) return;
		if (e.source !== "native") {
			let n = dd(a(), e, t);
			if (n !== void 0) return n;
			if (e.source !== "local" || !e.resourceIdentity?.startsWith("office-local:")) return;
		}
		if (!fd(e)) return;
		let n = `${e.requestedFamily}\0${e.weight}\0${e.style}`;
		if (!s.has(n)) {
			let t = ku(e.requestedFamily, e.weight, e.style);
			t !== void 0 && s.set(n, t);
		}
		return s.get(n);
	}, l = /* @__PURE__ */ new Map(), u = [];
	for (let [t, n] of e.entries()) {
		if (n.type !== "text") {
			u.push({
				charCount: 0,
				naturalWidthPx: 0
			});
			continue;
		}
		let e = n.text.split("	");
		for (let r = 0; r < e.length; r += 1) l.set(`${t}:${r}`, u.length), u.push({
			fitTextValTwips: n.fitTextVal,
			fitTextId: n.fitTextId,
			charCount: [...e[r]].length,
			naturalWidthPx: 0,
			charScale: n.charScale
		}), r < e.length - 1 && u.push({
			charCount: 0,
			naturalWidthPx: 0
		});
	}
	let d = /* @__PURE__ */ new Map();
	gu(u, 1).forEach((e, t) => {
		for (let n = e.start; n < e.end; n += 1) d.set(n, t);
	}), Nd(e, t, n, {
		runs: e,
		environment: t,
		segs: n,
		fitTextFragmentEntryByKey: l,
		fitTextRegionByEntry: d,
		selectedMetric: o,
		selectedAverageWidth: c
	}, o), Cd(e, t, n), Bu(n, t), Od(n);
	let f = t.nativeUnitMinimumBandPt === void 0 ? void 0 : lu(e);
	return Dc(uu(n, f, t), f);
}
var Ed = /[\p{Grapheme_Extend}\u200D]/u;
function Dd(e) {
	let t = (e, t) => nc.has(e) && t === " ", n, r;
	for (let i of e) {
		if (i === void 0) {
			n = void 0, r = void 0;
			continue;
		}
		for (let e of i) {
			if (n !== void 0 && t(n, e)) return !0;
			if (!Ed.test(e)) {
				if (r !== void 0 && r !== n && t(r, e)) return !0;
				r = e;
			}
			n = e;
		}
	}
	return !1;
}
function Od(e) {
	if (e.some((e) => "text" in e && (e.mixedSpaceAverageWidthRatio !== void 0 || e.autoSpaceCompressible)) && Dd(e.map((e) => "text" in e ? e.text : void 0))) for (let t of e) "text" in t && (t.mixedSpaceAverageWidthRatio = void 0, t.autoSpaceCompressible = void 0);
}
function kd(e, t, n, r, i, a = !1, o = !1, s) {
	let { base: c, environment: l, r: u, documentCharacterCompressionApplies: d, effectiveCharacterScale: f, effectiveKerningThreshold: p, fitTextRegionIndex: m, csFontSize: h, csFontFamily: g, highAnsiFontFamily: _, csBold: v, csItalic: y, eaFontFamily: x } = e, S = e.scopeContext, C = s ?? Object.freeze({
		text: S.text,
		offset: S.cursor
	});
	if (Os({
		text: t,
		substituteContext: C
	}, S.text), s || (S.cursor += t.length), Zl(l).balanceSingleByteDoubleByteWidth && !n && t.includes("　") && [...t].some((e) => e !== "　")) {
		let i = 0;
		for (let s of t.split(/(\u3000+)/u).filter(Boolean)) kd(e, s, n, r, void 0, a, o, C ? {
			text: C.text,
			offset: C.offset + i
		} : void 0), i += s.length;
		return;
	}
	if (!a && d && m === void 0) {
		let i = [
			0,
			...b(t),
			t.length
		];
		if (i.slice(0, -1).map((e, n) => t.slice(e, i[n + 1])).some((e) => ic(e, l.characterSpacingControl))) {
			kd(e, t, n, r, void 0, !0, o, C);
			return;
		}
	}
	let w = n ? v : c.bold, T = n ? y : c.italic, E = w ? 700 : 400, D = T ? "italic" : "normal", O = Object.freeze({
		text: t,
		...C ? { substituteContext: C } : {},
		fontSizePt: n ? h : c.fontSize,
		fonts: o ? {
			ascii: null,
			highAnsi: null,
			eastAsia: null,
			complexScript: null
		} : u.fontSlots?.direct ?? {
			ascii: c.fontFamily,
			highAnsi: _,
			eastAsia: x,
			complexScript: g
		},
		themeFonts: o ? void 0 : u.fontSlots?.theme,
		themeFontPresence: o ? void 0 : u.fontSlots?.themePresent,
		weight: E,
		style: D,
		complexScript: n,
		fontHint: u.fontHint,
		eastAsiaLanguage: u.langEastAsia,
		kerning: cr(n ? h : c.fontSize, p),
		measure: !1
	});
	Ad(e, {
		text: t,
		cs: n,
		fontFamily: r,
		authoritativeSpan: i,
		compressCharacterWhitespace: a,
		mappedSymbolUnicode: o,
		bold: w,
		italic: T,
		weight: E,
		style: D,
		textShapeRequest: O,
		shaped: i ? { spans: [i] } : l.layoutServices?.text.shape(O),
		punctuationCompressions: a && d ? (() => {
			let e = [
				0,
				...b(t),
				t.length
			], n = [];
			for (let r = 0; r < e.length - 1; r += 1) {
				let i = e[r], a = e[r + 1], o = t.slice(i, a);
				if (!ic(o, l.characterSpacingControl)) continue;
				let s = l.layoutServices?.text.shape({
					...ks(O, i, a),
					measure: !0,
					clusterGeometry: !1
				}), c = (s?.inkBounds && s.horizontalInkBoundsAreTight === !0 ? (() => {
					let e = Math.max(0, Math.min(s.advancePt, s.advancePt - s.inkBounds.xMaxPt));
					if (!nc.has(o)) return e;
					let t = s.spans[0]?.fontRoute.fingerprint, n = l.layoutServices?.text.shape({
						...As(O, "一"),
						fontHint: "eastAsia",
						measure: !0,
						clusterGeometry: !1
					}), r = n?.spans[0]?.fontRoute.fingerprint, i = n?.advancePt;
					if (!t || r !== t || i === void 0 || !Number.isFinite(i) || i <= 0) return 0;
					let a = Fr({
						punctuationAdvancePt: s.advancePt,
						punctuationInkEndPt: s.inkBounds.xMaxPt,
						ideographicCellAdvancePt: i
					});
					return Math.max(0, Math.min(e, s.advancePt - a));
				})() : 0) * (f ?? 1);
				c > 0 && n.push({
					end: a,
					adjustmentPt: -c
				});
			}
			return n.length === 0 ? void 0 : Object.freeze(n.map((e) => Object.freeze(e)));
		})() : void 0
	});
}
function Ad(e, t) {
	let { base: n, environment: r, segs: i, selectedMetric: a, selectedAverageWidth: o, r: s, effectiveVertAlign: c, effectivePosition: l, effectiveCharacterSpacing: u, documentCharacterCompressionApplies: d, effectiveCharacterScale: f, effectiveKerningThreshold: p, effectiveSnapToGrid: m, ruby: h, revision: g, fitTextFragmentEntryIndex: _, fitTextRegionIndex: v, csFontSize: y, csFontFamily: b, highAnsiFontFamily: x, eaFontFamily: S, digitsAsAN: C, hyperlink: w, rtl: T, overflowPunctuationEastAsianRun: E, joinPreviousRun: D } = e, { text: O, cs: k, fontFamily: A, authoritativeSpan: j, compressCharacterWhitespace: M, mappedSymbolUnicode: N, bold: P, italic: F, weight: I, style: L, textShapeRequest: R, shaped: z, punctuationCompressions: ee } = t, B = R, V = z, te = !j && V !== void 0 && V.spans.length > 1, H = te && Ss(O), U = te && Ts(V.spans) && B.kerning === !0 && ws(O), ne = r.characterGridActive === !1 && r.verticalCJK !== !0 && r.paragraphRtl === !1 && !T && !h && v === void 0 && !n.smallCaps && !n.allCaps && !c && (u == null || u === 0) && (f == null || f === 1) && !N && !M && (s.fontHint == null || s.fontHint === "default");
	if (!j && V && V.spans.length > 1 && (H || U) && ne) {
		let e = Object.freeze({
			...B,
			...H ? { joinRegisteredGrapheme: !0 } : { joinRegisteredLatinSlots: !0 }
		}), t = r.layoutServices?.text.shape(e);
		t?.spans.length === 1 && t.spans[0]?.semanticSlotSpans && (V = t, B = e.joinRegisteredLatinSlots === !0 ? Object.freeze({
			...e,
			registeredLatinPieceText: O
		}) : e);
	}
	let re = !j && ne && !k && V && V.spans.length > 1 ? /^([A-Za-z]\p{M}+)( +)$/u.exec(O) : null, ie = re ? V.spans[V.spans.length - 1] : void 0;
	if (re && ie && Ss(re[1]) && ie.text === re[2] && ie.start === re[1].length && ie.end === O.length && (ie.script === "ascii" || ie.script === "highAnsi")) {
		let i = re[1], a = Object.freeze({
			...ks(B, 0, i.length),
			joinRegisteredGrapheme: !0,
			joinRegisteredLatinSlots: void 0
		}), o = r.layoutServices?.text.shape(a);
		if (o?.spans.length === 1 && o.spans[0]?.semanticSlotSpans) {
			Ad(e, {
				...t,
				text: i,
				textShapeRequest: a,
				shaped: o
			}), kd(e, ie.text, !1, ie.script === "highAnsi" ? x : n.fontFamily, ie, !1, N, ks(B, ie.start, ie.end).substituteContext);
			return;
		}
	}
	let ae = V?.spans.some((e) => e.script === "complexScript" !== k) ?? !1;
	if (V && (V.spans.length > 1 || ae)) {
		for (let t = 0; t < V.spans.length; t += 1) {
			let i = V.spans[t], a = i.script === "complexScript", o = a ? b : i.script === "eastAsia" ? S : i.script === "highAnsi" ? x : n.fontFamily, s = d && M && [...i.text].some((e) => ic(e, r.characterSpacingControl));
			kd(e, i.text, a, o, i, s, N, ks(B, i.start, i.end).substituteContext);
		}
		return;
	}
	let oe = V?.spans[0], se = oe ? a(oe.font, O) : void 0, W = r.layoutServices?.text.resolve({
		fonts: B.fonts,
		themeFonts: B.themeFonts,
		themeFontPresence: B.themeFontPresence,
		slot: "eastAsia",
		weight: I,
		style: L
	}), ce = s.textBoxLineFloor ? "" : O, le = W ? a(W, ce) : void 0, ue = r.lineSpacing?.rule !== "exact", { resourceMetric: de, referenceMetric: fe, lineMetric: pe } = Yu(oe?.font, se, ue, md(ad(r.layoutServices?.text.fontMetrics ?? r.layoutServices?.text.localMetrics ?? {}), oe?.font), r.layoutServices ? {
		text: r.layoutServices.text,
		probe: O,
		...B.baseDirection === void 0 ? {} : { baseDirection: B.baseDirection }
	} : void 0, Vu(r.layoutServices?.text, r.lineGridActive === !0, r.verticalCJK === !0 || r.wordLineBoxes === !0)), { lineMetric: me } = Yu(W, le, ue, md(ad(r.layoutServices?.text.fontMetrics ?? r.layoutServices?.text.localMetrics ?? {}), W), void 0, Vu(r.layoutServices?.text, r.lineGridActive === !0, r.verticalCJK === !0 || r.wordLineBoxes === !0)), he = W?.resolvedFamily ?? le?.family ?? S, ge = Zl(r).useFeLayout && r.lineGridActive && (s.fontHint === "eastAsia" || !!he?.trim()), _e = oe?.script ?? j?.script ?? (k ? "complexScript" : vs.test(O) ? "eastAsia" : "ascii"), ve = r.characterSpacingControl === "compressPunctuation" && Er(Zl(r), p != null) && r.verticalCJK !== !0 && d && (_e === "ascii" || _e === "highAnsi") && !e.reduced && c == null && (u == null || u === 0) && (f == null || f === 1) ? o(oe?.font, O) : void 0, ye = Ar(Zl(r), r.characterSpacingControl) && !Zl(r).lineWrapLikeWord6 && r.verticalCJK !== !0 && d && (_e === "ascii" || _e === "highAnsi") && !e.reduced && c == null && (u == null || u === 0) && (f == null || f === 1) ? ve ?? o(oe?.font, O) : void 0, be = Zl(r).balanceSingleByteDoubleByteWidth ? Pr(O, _e) : void 0;
	i.push({
		text: O,
		script: _e,
		...s.spaceAdvancePt === void 0 ? {} : { spaceAdvancePt: s.spaceAdvancePt },
		...s.listLabel === void 0 ? {} : { listLabel: s.listLabel },
		...oe?.semanticSlotSpans ? { semanticSlotSpans: oe.semanticSlotSpans } : {},
		...be === void 0 ? {} : { widthBalanceGridDeltaFactor: be },
		...ge ? { metricEastAsian: !0 } : {},
		bold: P,
		italic: F,
		underline: n.underline,
		underlineStyle: s.underlineStyle,
		underlineColor: s.underlineColor,
		strikethrough: n.strikethrough,
		fontSize: k ? y : n.fontSize,
		color: n.color,
		fontFamily: oe?.font.resolvedFamily ?? se?.family ?? A,
		authoredFontFamily: oe?.font.requestedFamily ?? A,
		fontSource: oe?.font.source,
		...oe?.font.installedFamily ? { fontInstalledFamily: !0 } : {},
		authoredReferenceMetricAllowed: pd(oe?.font),
		fontRoute: oe?.fontRoute,
		resolvedLineHeightRatio: pe?.lineHeightRatio,
		resolvedLatinGridCellAllocation: (de?.farEastCodePage ?? fe?.farEastCodePage) === !1,
		...de?.lineHeightRatio == null ? {} : {
			resolvedResourceVerticalMetric: !0,
			resolvedDesignAscentRatio: de.designAscentRatio,
			resolvedDesignDescentRatio: de.designDescentRatio
		},
		...fe ? {
			referenceFontVerticalMetric: !0,
			resolvedDesignAscentRatio: fe.designAscentRatio,
			resolvedDesignDescentRatio: fe.designDescentRatio
		} : {},
		...Fd(oe?.font, fe != null),
		resolvedEastAsianLineHeightRatio: pe?.eastAsianLineHeightRatio,
		...ve != null && ve > 0 ? {
			latinSpaceAverageWidthRatio: ve,
			latinSpaceCompressionEligible: !0
		} : {},
		...ye != null && ye > 0 ? { mixedSpaceAverageWidthRatio: ye } : {},
		vertAlign: c,
		measuredWidth: 0,
		textLayoutService: r.layoutServices?.text,
		textShapeRequest: B,
		...oe?.substituteScope === void 0 ? {} : { substituteScope: oe.substituteScope },
		breakBefore: oe?.breakBefore ?? j?.breakBefore ?? !0,
		smallCaps: e.reduced,
		joinPrev: e.firstSeg && (s.noBreakBefore === !0 || D) || e.gluePending || j?.breakBefore === !1 ? !0 : void 0,
		hardJoinPrev: e.firstSeg && (s.noBreakBefore === !0 || D) ? !0 : void 0,
		doubleStrikethrough: n.doubleStrikethrough ?? !1,
		highlight: n.highlight ?? null,
		emphasisMark: n.emphasisMark,
		background: n.background ?? null,
		colorAuto: s.colorAuto ?? !1,
		border: s.border ?? null,
		ruby: e.firstSeg ? h : void 0,
		...h ? { rubyPiece: !0 } : {},
		revision: g,
		...g && r.showTrackedChanges === !0 ? { trackChangesMarkup: {
			kind: g.kind,
			authorColor: r.revisionAuthorColor?.(g.author) ?? "#C00000"
		} } : {},
		rtl: T,
		digitsAsAN: C ? !0 : void 0,
		eaFloorFamily: he,
		eaFloorRoute: W?.route,
		resolvedEaFloorLineHeightRatio: me?.lineHeightRatio,
		resolvedEaFloorEastAsianLineHeightRatio: me?.eastAsianLineHeightRatio,
		textBoxLineFloor: s.textBoxLineFloor,
		textBoxVertical: s.textBoxVertical,
		hyperlink: w,
		snapToCharacterGrid: m !== !1,
		charSpacing: u,
		punctuationCompressions: ee,
		eastAsiaLanguage: s.langEastAsia,
		overflowPunctuationEastAsianRun: E,
		overflowPunctuationBidiLanguage: s.langBidi,
		charScale: f,
		fitTextVal: v === void 0 ? void 0 : s.fitTextVal,
		fitTextId: v === void 0 ? void 0 : s.fitTextId,
		fitTextRegionIndex: v,
		fitTextRunIndex: v === void 0 ? void 0 : _,
		position: l,
		positionExtendsLineBox: r.positionExtendsLineBox !== !1,
		kerning: p,
		tateChuYoko: r.verticalCJK && s.eastAsianVert === !0 ? !0 : void 0,
		tateChuYokoCompress: r.verticalCJK && s.eastAsianVert === !0 && s.eastAsianVertCompress === !0 ? !0 : void 0,
		verticalRun: r.verticalCJK && s.eastAsianVert !== !0 ? !0 : void 0
	}), e.firstSeg = !1, e.gluePending = !1;
}
function jd(e, t, n, r) {
	if (!e || e.length !== 4 || e.every((e) => !Number.isFinite(e) || e === 0)) return {
		widthPt: t,
		heightPt: n
	};
	let [i, a, o, s] = e.map((e) => Number.isFinite(e) ? e : 0), c = r === "upright-physical" ? [
		a,
		o,
		s,
		i
	] : r === "upright-physical-counter-clockwise" ? [
		s,
		i,
		a,
		o
	] : [
		i,
		a,
		o,
		s
	], [l, u, d, f] = c;
	return {
		widthPt: Math.max(0, t + l + d),
		heightPt: Math.max(0, n + u + f),
		effectExtent: c,
		objectSizePt: [t, n]
	};
}
function Md(e, t, n) {
	let r = t.layoutServices?.text, i = e.bold ? 700 : 400, a = e.italic ? "italic" : "normal", o = r?.resolve({
		text: "x",
		fonts: {
			ascii: e.fontFamily,
			highAnsi: e.fontFamily,
			eastAsia: e.fontFamilyEastAsia,
			complexScript: e.fontFamily
		},
		slot: "ascii",
		weight: i,
		style: a
	});
	if (!o) return {};
	let { lineMetric: s } = Yu(o, n(o, "x"), !0, md(ad(r?.fontMetrics ?? r?.localMetrics ?? {}), o), void 0, Vu(r, !1));
	return s?.designAscentRatio != null && s.designDescentRatio != null ? {
		textOwnedLineBox: !0,
		lineBoxAscentRatio: s.designAscentRatio,
		lineBoxDescentRatio: s.designDescentRatio
	} : {};
}
function Nd(e, t, n, r, i) {
	let a = e.some((e) => e.type === "text" && e.noteSeparatorCharacter !== void 0) ? /* @__PURE__ */ new Map() : mu(e, t, (e, n) => yd(e, n, t)), o = -1, s = !1;
	for (let [c, l] of e.entries()) {
		if (c <= o) continue;
		let u = a.get(c), d = u?.run ?? l;
		u && (o = u.sources.at(-1).runIndex);
		let f = d.revision?.kind;
		if (du(f, t.showTrackedChanges)) continue;
		let p = s;
		s = d.type === "text" && d.noBreakAfter === !0;
		let m = n.length;
		if (d.type === "text") {
			let e = d;
			if (d.optionalHyphen === !0) {
				xd(r, "-", e, e.vertAlign ?? null, c, bd("-", e, t));
				for (let e = m; e < n.length; e += 1) {
					let t = n[e];
					if (!("text" in t)) throw Error("An optional hyphen lost its text authority");
					n[e] = {
						...t,
						text: "",
						metricOnly: !0,
						optionalHyphen: Object.freeze({ ...t }),
						measuredWidth: 0,
						sourceRunIndex: c,
						...t.textShapeRequest ? {
							nativeLevelUnit: void 0,
							nativeVisiblePrefix: void 0,
							textShapeRequest: Object.freeze(As(t.textShapeRequest, ""))
						} : {}
					};
				}
				continue;
			}
			if (d.noteSeparatorCharacter !== void 0) {
				let i = bd("x", e, t), a = i.text;
				xd(r, "x", e, e.vertAlign ?? null, c, i);
				for (let e = m; e < n.length; e += 1) {
					let t = n[e];
					if (!("text" in t)) throw Error("A separator metric probe lost its text authority");
					t.text = "", t.metricOnly = !0, t.metricProbeText = a, t.sourceRunIndex = c, t.textShapeRequest &&= (t.nativeLevelUnit = void 0, t.nativeVisiblePrefix = void 0, Object.freeze(As(t.textShapeRequest, "")));
				}
				continue;
			}
			let a = e.noteRef ? e.noteRef.id ? t.noteNumbers?.get(`${e.noteRef.kind}:${e.noteRef.id}`) : t.noteReferenceNumber : void 0;
			if (e.noteRef) {
				if (e.noteRef.customMarkFollows === !0 || a === 0) {
					let i = bd("x", e, t);
					xd(r, "x", e, e.vertAlign ?? null, c, i);
					for (let e = m; e < n.length; e += 1) {
						let t = n[e];
						if (!("text" in t)) throw Error("A note metric probe lost its text authority");
						t.text = "", t.metricOnly = !0, t.fontSource === "native" && t.fontInstalledFamily !== !0 && (t.metricProbeText = i.text), t.sourceRunIndex = c, t.textShapeRequest &&= (t.nativeLevelUnit = void 0, t.nativeVisiblePrefix = void 0, Object.freeze(As(t.textShapeRequest, "")));
					}
					continue;
				}
				let i = a == null ? e.text || "" : Qs(a, e.noteRef.kind === "footnote" ? t.noteNumbering?.footnote : e.noteRef.kind === "endnote" ? t.noteNumbering?.endnote : void 0);
				i.length > 0 && xd(r, i, e, e.vertAlign ?? null, c, bd(i, e, t), 0, p);
				for (let e = m; e < n.length; e += 1) n[e].sourceRunIndex = c;
				continue;
			}
			let o = e.text.split("	"), s = e.listLabel, l = yd(e.text, e, t), f = 0;
			for (let a = 0; a < o.length; a++) o[a].length > 0 && xd(r, o[a], e, e.vertAlign, c, {
				text: l,
				offset: f
			}, a, a === 0 && p), f += yd(o[a], e, t).length + 1, a < o.length - 1 && n.push({
				isTab: !0,
				fontSize: e.fontSize,
				measuredWidth: 0,
				...t.layoutServices?.text.libreOfficeLineBoxes === !0 && t.lineGridActive !== !0 && t.verticalCJK !== !0 && t.wordLineBoxes !== !0 ? Md(e, t, i) : {},
				bold: e.bold,
				italic: e.italic,
				sourceRunIndex: c,
				...u ? { sourceTextOffset: f - 1 } : {},
				...s === void 0 ? {} : { listLabel: s },
				...Zl(t).tabDisplacedReadingFrame ? { displacedFloatTabFrame: !0 } : {}
			});
		} else if (d.type === "image") {
			let e = d;
			n.push({
				imagePath: e.imagePath,
				mimeType: e.mimeType,
				...e.anchor ? {} : { inlinePicture: !0 },
				...jd(e.anchor ? void 0 : e.inlineEffectExtent, e.widthPt, e.heightPt, t.uprightResourceOrientation),
				rotation: e.rotation,
				flipH: e.flipH,
				flipV: e.flipV,
				anchor: e.anchor ?? !1,
				anchorXPt: e.anchorXPt ?? 0,
				anchorYPt: e.anchorYPt ?? 0,
				anchorXFromMargin: e.anchorXFromMargin ?? !1,
				anchorYFromPara: e.anchorYFromPara ?? !1,
				colorReplaceFrom: e.colorReplaceFrom ?? void 0,
				duotone: e.duotone,
				alpha: e.alpha,
				srcRect: e.srcRect ?? void 0,
				measuredWidth: 0,
				...Id(e)
			});
		} else if (d.type === "chart") {
			let e = d;
			n.push({
				imagePath: "",
				mimeType: "",
				widthPt: e.widthPt,
				heightPt: e.heightPt,
				anchor: e.anchor ?? !1,
				anchorXPt: e.anchorXPt ?? 0,
				anchorYPt: e.anchorYPt ?? 0,
				anchorXFromMargin: e.anchorXFromMargin ?? !1,
				anchorYFromPara: e.anchorYFromPara ?? !1,
				chart: !0,
				chartResourceKey: e.resourceKey,
				measuredWidth: 0
			});
		} else if (d.type === "shape" && d.inline === !0) n.push({
			imagePath: "",
			mimeType: "",
			anchor: !1,
			anchorXPt: 0,
			anchorYPt: 0,
			anchorXFromMargin: !1,
			anchorYFromPara: !1,
			inlineShape: !0,
			inlinePicture: !0,
			...jd(d.inlineEffectExtent, d.widthPt, d.heightPt),
			...d.inlineOffsetXPt ? { inlineOffsetXPt: d.inlineOffsetXPt } : {},
			...d.inlineOffsetYPt ? { inlineOffsetYPt: d.inlineOffsetYPt } : {},
			measuredWidth: 0
		});
		else if (d.type === "unavailableDrawing") {
			let e = "anchorAcquisitionInput" in d ? d.anchorAcquisitionInput : void 0;
			n.push({
				imagePath: "",
				mimeType: "",
				...jd(e !== void 0 || d.resourceKind === "chart" ? void 0 : d.inlineEffectExtent, d.widthPt, d.heightPt),
				anchor: e !== void 0,
				anchorXPt: 0,
				anchorYPt: 0,
				anchorXFromMargin: !1,
				anchorYFromPara: !1,
				unavailableResourceKind: d.resourceKind,
				measuredWidth: 0
			});
		} else if (d.type === "break") {
			if (d.breakType === "line") {
				let t = $s(e, e.indexOf(d));
				n.push({
					lineBreak: !0,
					fontSize: t,
					measuredWidth: 0
				});
			}
		} else if (d.type === "field") {
			let e = d, n = ec(e, t);
			n && xd(r, n, e, e.vertAlign, c, bd(n, e, t), void 0, p);
		} else if (d.type === "math") {
			let r = d.fontSize || $s(e, e.indexOf(d)), i = "resourceKey" in d ? d.resourceKey : void 0;
			if (t.layoutServices && !i) throw Error("Service-backed math layout requires a normalized structural resource key");
			let a = i ? t.layoutServices?.math.resolve(i) : void 0;
			n.push({
				math: !0,
				mathResourceKey: i ?? "",
				mathMetadata: a,
				display: d.display,
				fontSize: r,
				color: null,
				fallbackText: "fallbackText" in d ? d.fallbackText : Y(d.nodes),
				measuredWidth: 0,
				mathAscent: 0,
				mathDescent: 0,
				jc: d.jc
			});
		} else if (d.type === "ptab") n.push({
			isTab: !0,
			fontSize: d.fontSize || $s(e, e.indexOf(d)),
			measuredWidth: 0,
			leader: d.leader,
			ptab: {
				alignment: d.alignment,
				relativeTo: d.relativeTo
			}
		});
		else if (d.type === "anchorHost") {
			let e = d.fontFamilyEastAsia != null, r = d.bold ?? !1, a = d.italic ?? !1, o = d.fontFamilyEastAsia ?? d.fontFamily ?? null, s = r ? 700 : 400, c = a ? "italic" : "normal", l = e ? "あ" : "x", u = t.layoutServices?.text.resolve({
				text: l,
				fonts: {
					ascii: d.fontFamily,
					highAnsi: d.fontFamily,
					eastAsia: d.fontFamilyEastAsia,
					complexScript: d.fontFamily
				},
				slot: e ? "eastAsia" : "ascii",
				weight: s,
				style: c
			}), f = i(u, l), p = t.lineSpacing?.rule !== "exact", m = p || f?.designAscentRatio == null ? Gu(f, Vu(t.layoutServices?.text, t.lineGridActive === !0, t.verticalCJK === !0 || t.wordLineBoxes === !0)) : void 0, h = p && !m && pd(u) && md(ad(t.layoutServices?.text.fontMetrics ?? t.layoutServices?.text.localMetrics ?? {}), u) ? Ou(u.requestedFamily, s, c, Vu(t.layoutServices?.text, t.lineGridActive === !0, t.verticalCJK === !0 || t.wordLineBoxes === !0)) : void 0, g = m ?? h;
			n.push({
				text: "",
				metricOnly: !0,
				...e ? { metricEastAsian: !0 } : {},
				bold: r,
				italic: a,
				underline: !1,
				strikethrough: !1,
				fontSize: d.fontSize,
				color: null,
				fontFamily: u?.resolvedFamily ?? o,
				authoredFontFamily: u?.requestedFamily ?? o,
				fontSource: u?.source,
				authoredReferenceMetricAllowed: pd(u),
				fontRoute: u?.route,
				resolvedLineHeightRatio: g?.lineHeightRatio,
				...m?.lineHeightRatio == null ? {} : {
					resolvedResourceVerticalMetric: !0,
					resolvedDesignAscentRatio: m.designAscentRatio,
					resolvedDesignDescentRatio: m.designDescentRatio
				},
				...h ? {
					referenceFontVerticalMetric: !0,
					resolvedDesignAscentRatio: h.designAscentRatio,
					resolvedDesignDescentRatio: h.designDescentRatio
				} : {},
				...Fd(u, h != null),
				resolvedEastAsianLineHeightRatio: g?.eastAsianLineHeightRatio,
				vertAlign: null,
				measuredWidth: 0,
				eaFloorFamily: e ? u?.resolvedFamily ?? o : null,
				resolvedEaFloorLineHeightRatio: e ? g?.lineHeightRatio : void 0,
				resolvedEaFloorEastAsianLineHeightRatio: e ? g?.eastAsianLineHeightRatio : void 0,
				snapToCharacterGrid: !1,
				...Id(d)
			});
		}
		let h = 0, g = 0;
		for (let e = m; e < n.length; e += 1) {
			let i = n[e];
			if (i.sourceRunIndex = c, u) {
				i.sourceTextSequence = u.sources, i.sourceTextOffset = u.optionalHyphens.length > 0 ? h : "text" in i ? i.textShapeRequest?.substituteContext?.offset ?? 0 : i.sourceTextOffset ?? 0;
				let e = h + ("text" in i ? i.text.length : +("isTab" in i));
				if ("text" in i) {
					let n = [];
					for (; g < u.optionalHyphens.length && u.optionalHyphens[g].offset <= e;) {
						let e = u.optionalHyphens[g++], i = [];
						if (xd({
							...r,
							segs: i
						}, "-", e.run, e.run.vertAlign ?? null, e.runIndex, bd("-", e.run, t)), i.length !== 1 || !("text" in i[0])) throw Error("An optional hyphen lost its single conditional glyph");
						let a = i[0];
						a.sourceRunIndex = e.runIndex, n.push(Object.freeze({
							offset: e.offset - h,
							glyph: Object.freeze(a)
						}));
					}
					n.length && (i.optionalHyphenBreaks = Object.freeze(n));
				}
				h = e;
			}
		}
	}
}
function Pd(e, t) {
	for (let [n, r] of e.entries()) {
		if (r.type !== "text") continue;
		let e = r, i = e.noBreakRanges;
		if (!i || i.length === 0) continue;
		let a = i.map((t) => {
			let n = (t) => {
				let n = e.text.slice(0, t);
				return e.allCaps || e.smallCaps ? n.toUpperCase().length : n.length;
			};
			return {
				start: n(t.start),
				end: n(t.end)
			};
		}), o = 0;
		for (let e of t) {
			if (e.sourceRunIndex !== n) continue;
			if (!("text" in e)) {
				"isTab" in e && (o += 1);
				continue;
			}
			let t = o + e.text.length;
			o > 0 && a.some((e) => e.start === o || e.end === o) && (e.joinPrev = !0, e.hardJoinPrev = !0);
			let r = a.filter((e) => e.start >= o && e.end <= t).map((e) => Object.freeze({
				start: e.start - o,
				end: e.end - o
			}));
			r.length > 0 && (e.noBreakRanges = Object.freeze(r)), o = t;
		}
	}
}
function Fd(e, t) {
	if (!e) return {};
	let n = e.source === "local" && e.resourceIdentity?.startsWith("office-local:") === !0, r = e.source === "native" && e.installedFamily === !0;
	if (!n && !r && !t) return {};
	let i = Tu(e.requestedFamily, e.weight, e.style) ?? (t ? Tu(e.requestedFamily, 400, "normal") : void 0);
	return i ? { referenceFontDecoration: i } : {};
}
function Id(e) {
	let t = e.listLabel;
	return t === void 0 ? {} : { listLabel: t };
}
var Ld = class {
	segments;
	cursor = {
		index: 0,
		front: null
	};
	constructor(e = []) {
		this.segments = e;
	}
	get length() {
		return this.segments.length - this.cursor.index + (this.cursor.front?.length ?? 0);
	}
	peek() {
		return this.cursor.front?.segment ?? this.segments[this.cursor.index];
	}
	peekPair() {
		let { index: e, front: t } = this.cursor;
		return t ? [t.segment, t.next?.segment ?? this.segments[e]] : [this.segments[e], this.segments[e + 1]];
	}
	shift() {
		let { index: e, front: t } = this.cursor;
		if (t) return this.cursor = {
			index: e,
			front: t.next
		}, t.segment;
		if (!(e >= this.segments.length)) return this.cursor = {
			index: e + 1,
			front: null
		}, this.segments[e];
	}
	unshift(e) {
		this.cursor = this.snapshot(e);
	}
	snapshot(e) {
		return e ? {
			index: this.cursor.index,
			front: {
				segment: e,
				next: this.cursor.front,
				length: (this.cursor.front?.length ?? 0) + 1
			}
		} : this.cursor;
	}
	restore(e) {
		this.cursor = e;
	}
	*[Symbol.iterator]() {
		let { index: e, front: t } = this.cursor;
		for (let e = t; e; e = e.next) yield e.segment;
		for (let t = e; t < this.segments.length; t += 1) yield this.segments[t];
	}
};
function Rd(e, t, n, r, i) {
	t = t ? Ac(e, t) : void 0;
	let a = e.map((e, t) => {
		if (e.src = {
			segIndex: t,
			charOffset: 0,
			...e.sourceCursorStart === void 0 ? {} : { sourceTextStart: e.sourceCursorStart }
		}, "text" in e && y(e.text)) {
			let t = Yc(e);
			e.seaBreaks = E(e.text, {
				cjk: !0,
				kinsoku: n
			}).filter((e) => !t.has(e));
		}
		return e;
	}), o;
	if (!t) o = a;
	else if (t.segIndex >= a.length) o = [];
	else {
		let e = a[t.segIndex];
		if (t.charOffset > 0) if (!("text" in e) || t.charOffset > e.text.length) o = [];
		else {
			let n = e.text.slice(t.charOffset);
			o = n ? [{
				...e,
				text: n,
				measuredWidth: 0,
				src: { ...t },
				joinPrev: void 0,
				hardJoinPrev: void 0,
				...J(e, t.charOffset, e.text.length),
				seaBreaks: ac(e.seaBreaks, t.charOffset)
			}, ...a.slice(t.segIndex + 1)] : a.slice(t.segIndex + 1);
		}
		else o = a.slice(t.segIndex);
	}
	let s = 0, c = -1, l = [];
	for (let e = o.length - 1; e >= 0; --e) {
		let t = o[e];
		if (!t || !("text" in t) || t.text.length === 0) break;
		if (t.fitTextRegionIndex !== void 0 || t.tateChuYoko === !0 || t.ruby !== void 0) {
			if (t.sourceRunIndex !== void 0) {
				for (let e = l.length - 1; e >= 0; --e) {
					let n = l[e];
					n.segment.sourceRunIndex === t.sourceRunIndex && (n.segment.paragraphFinalIdeographicSpaceTail = void 0, n.segment.paragraphFinalIdeographicSpaceLocalCount = void 0, n.segment.paragraphFinalIdeographicSpaceCount = void 0, n.segment.paragraphFinalIdeographicSpaceTailStart = void 0, l.splice(e, 1));
				}
				c = l.at(-1)?.index ?? -1;
			}
			break;
		}
		let n = /^\u3000+$/u.test(t.text), r = /[^\u3000]\u3000+$/u.test(t.text);
		if (!n && !r) break;
		let i = n ? [...t.text].length : [...t.text].reverse().findIndex((e) => e !== "　");
		if (s += i, t.paragraphFinalIdeographicSpaceTail = !0, t.paragraphFinalIdeographicSpaceLocalCount = i, t.paragraphFinalIdeographicSpaceCount = s, c = e, l.push({
			index: e,
			segment: t
		}), r) break;
	}
	if (c >= 0) {
		let e = o[c];
		e && "text" in e && (e.paragraphFinalIdeographicSpaceTailStart = !0);
	}
	return hd(o.filter((e) => "text" in e), r, (e) => i.measureSegment(e).width + i.verticalInkExtra(e, e.text)), o;
}
function zd(e) {
	return "text" in e && e.metricOnly === !0 || "imagePath" in e && !!e.anchor;
}
function Bd(e, t) {
	return {
		lines: [],
		firstIndentOverride: void 0,
		numberingFirstLine: void 0,
		currentLine: [],
		currentWidth: 0,
		justifiedGapModel: void 0,
		justifiedCompressionPx: 0,
		justifiedUnitEnd: void 0,
		latinLineFace: void 0,
		latinLineHomogeneous: !0,
		latinLineGaps: [],
		mixedSpace: Sl(),
		mixedSpaceEnabled: !1,
		latinUniformGapCapacity: void 0,
		latinAppliedGapCount: 0,
		latinAppliedPerGap: 0,
		snapBlock: null,
		physicalLineIndex: 0,
		positionReferencePt: void 0,
		firstPositioned: void 0,
		uniformPositionEligible: !0,
		fragmentCursor: null,
		gapTransaction: null,
		inHand: void 0,
		lineHeight: 0,
		lineAscent: 0,
		lineDescent: 0,
		lineIntendedSingle: 0,
		lineHasInlinePicture: !1,
		linePictureMarkSingle: 0,
		lineObjectBaselineMinimum: 0,
		lineObjectAdvanceMinimum: 0,
		lineGridCountSingle: 0,
		lineLatinGridCountSingle: 0,
		lineVisibleAscent: 0,
		lineVisibleDescent: 0,
		lineVisibleIntendedSingle: 0,
		lineHasVisibleMetrics: !1,
		lineMarkerHeight: 0,
		lineMarkerAscent: 0,
		isFirst: !0,
		lineLabelShiftPx: 0,
		lineMaxWidth: e,
		lineXOffset: 0,
		lineMarginExtension: 0,
		currentLineTopY: t?.startPageY ?? 0,
		lineHasRuby: !1,
		lineEastAsian: !1,
		queue: new Ld(),
		trailingBreakFontSize: null
	};
}
var Vd = o, Hd = i;
function Ud(e) {
	return Vd.has(e.toLowerCase());
}
var Wd = m, Gd = ["Noto Naskh Arabic", "Noto Sans Arabic"];
function Kd(e, t) {
	let n = (e ?? t) && (e ?? t) !== "jp" ? M(e ?? t, "sans") : [
		"Noto Sans JP",
		"Hiragino Sans",
		"Meiryo",
		...M("jp", "sans").slice(1)
	];
	return e == null ? `${Wd([
		...L,
		"Arial",
		"Helvetica",
		"Liberation Sans",
		...n,
		...Gd
	])}, sans-serif` : `${Wd([
		...n,
		...Gd,
		...L
	])}, sans-serif`;
}
function qd(e, t) {
	let n = (e ?? t) && (e ?? t) !== "jp" ? M(e ?? t, "serif") : [
		"Yu Mincho",
		"YuMincho",
		"Hiragino Mincho ProN",
		"MS Mincho",
		"Noto Serif JP",
		...M("jp", "serif").slice(1)
	];
	return e == null ? `${Wd([
		...P,
		"Times New Roman",
		"Cambria",
		"Liberation Serif",
		...n,
		...Gd
	])}, serif` : `${Wd([
		...n,
		...Gd,
		...P
	])}, serif`;
}
var Jd = /* @__PURE__ */ new WeakMap(), Yd = /* @__PURE__ */ new WeakMap(), Xd = /* @__PURE__ */ new WeakMap();
function Zd(e, t) {
	let n = Xd.get(e);
	if (!n) {
		n = /* @__PURE__ */ new Map();
		for (let [t, r] of Object.entries(e)) {
			let e = Ut(t);
			n.has(e) ? n.get(e) !== r && n.set(e, null) : n.set(e, r);
		}
		Xd.set(e, n);
	}
	return n.get(Ut(t)) ?? void 0;
}
function Qd(e, t) {
	let n = e ?? {};
	return t && Object.keys(t).length > 0 && Yd.set(n, t), n;
}
function $d(e, t = {}) {
	let n = Jd.get(t) ?? (() => {
		let e = /* @__PURE__ */ new Map();
		return Jd.set(t, e), e;
	})(), r = e ?? "\0null", i = n.get(r);
	if (i !== void 0) return i;
	let a = ef(e, t, Yd.get(t));
	return n.set(r, a), a;
}
function ef(e, t, n = {}, r) {
	if (!e || e === "sans-serif") return Kd(null, r);
	if (e === "serif") return qd(null, r);
	let i = r ? `"Courier New", ${Wd(M(r, "sans"))}, monospace` : "\"Courier New\", monospace";
	if (e === "monospace") return i;
	let a = c(e), o = e.toLowerCase(), s = F(e), l = Zd(t, e);
	if (l && l !== "auto") switch (l) {
		case "roman": return `${a}, ${qd(s, r)}`;
		case "swiss": return `${a}, ${Kd(s, r)}`;
		case "modern":
			if (Zd(n, e) === "fixed") return s == null ? `${a}, ${i}` : `${a}, ${Wd([...s === "jp" ? [
				"Yu Gothic",
				"YuGothic",
				"Hiragino Sans",
				"Meiryo",
				"Noto Sans JP"
			] : M(s, "sans"), "Courier New"])}, monospace`;
			break;
		default: break;
	}
	if (Ud(e)) return Hd.has(o) ? r ? `${a}, "Noto Naskh Arabic", "Noto Sans Arabic", "Noto Serif", ${Kd(null, r).replace(/sans-serif$/, "serif")}` : `${a}, "Noto Naskh Arabic", "Noto Sans Arabic", "Noto Serif", "Noto Sans JP", "Hiragino Sans", serif` : r ? `${a}, "Noto Sans Arabic", "Noto Naskh Arabic", ${Kd(null, r)}` : `${a}, "Noto Sans Arabic", "Noto Naskh Arabic", "Noto Sans JP", "Hiragino Sans", sans-serif`;
	let u = I(e);
	if (u === "serif") return `${a}, ${qd(s, r)}`;
	if (u === "mono") return `${a}, ${i}`;
	if (s == null || s === "jp") {
		if (o.includes("meiryo") || e.includes("メイリオ")) return `${a}, "Meiryo UI", "Meiryo", ${Kd(s, r)}`;
		if (e.includes("游ゴシック") || /\byu\s*gothic\b/i.test(e) || o.includes("yugothic")) return `${a}, "Yu Gothic", "YuGothic", ${Kd(s, r)}`;
		if (o.includes("ipa")) return `${a}, "IPAexGothic", ${Kd(s, r)}`;
		if (o.includes("segoe")) return r ? `${a}, "Segoe UI", ${Kd(null, r)}` : `${a}, "Segoe UI", ${Wd([...Gd, ...L])}, sans-serif`;
	}
	return `${a}, ${Kd(s, r)}`;
}
function tf(e, t, n, r, i = {}, a) {
	return a ? Ie(a, n, e ? 700 : 400, t ? "italic" : "normal") : `${t ? "italic" : "normal"} ${e ? "bold" : "normal"} ${n}px ${$d(r, i)}`;
}
function nf(e, t, n = !1) {
	return (n ? e.resolvedEastAsianLineHeightRatio ?? e.resolvedLineHeightRatio ?? 0 : e.resolvedLineHeightRatio ?? 0) * t;
}
function rf(e, t, n = !1) {
	return (n ? e.resolvedEaFloorEastAsianLineHeightRatio ?? e.resolvedEaFloorLineHeightRatio ?? 0 : e.resolvedEaFloorLineHeightRatio ?? 0) * t;
}
function af(e) {
	for (let t of e.runs) if (t.type === "text" || t.type === "field") return t.fontSize;
	return typeof e.defaultFontSize == "number" ? e.defaultFontSize : 10;
}
function of(e, t = !1) {
	for (let t of e.runs) if (t.type === "text" || t.type === "field") return t.fontFamily;
	return t && e.defaultFontFamilyEastAsia ? e.defaultFontFamilyEastAsia : e.defaultFontFamily ?? null;
}
var sf = {
	textCellSpaceGaps: !0,
	atomicSpaceGaps: !0,
	isWhitespace: (e) => e === 32,
	isGapChar: () => !1,
	lastDrawnSi: Infinity
};
function cf(e, t, n = !0) {
	let r = t?.segmentCount ?? 0, i = (e, n) => be(e, {
		...sf,
		segmentOffset: r,
		prefix: t?.scan,
		collect: n,
		gapWidth: (t, n) => e[t - r].spaceWidths?.get(n) ?? e[t - r].spacePx,
		leadingGapWidth: (t) => e[t - r]?.leadingGapPx ?? 0
	}), a = i(e, n), o = t?.naturalWidthPx ?? 0, { latinPx: s, fullPx: c, gapPx: l, rtl: u } = t?.tail ?? {
		latinPx: 0,
		fullPx: 0,
		gapPx: 0,
		rtl: !1
	}, d;
	if (e.forEach((e, t) => {
		if (o += e.widthPx, e.rtl && (u = !0), e.text === "") return;
		if (e.text === void 0) {
			s = 0, c = 0, d = [t, 0];
			return;
		}
		if (/^ +$/u.test(e.text)) {
			s += e.widthPx, c += e.widthPx;
			return;
		}
		let n = [...e.text], r = (t) => e.spaceWidths?.get(t) ?? e.spacePx, i = n.length;
		for (; i > 0 && n[i - 1] === " ";) --i;
		s = 0;
		for (let e = i; e < n.length; e++) s += r(e);
		let a = n.length;
		for (; a > 0 && (n[a - 1] === " " || e.ideographicSpaceWidths?.has(a - 1) === !0);) --a;
		let l = 0;
		for (let t = a; t < n.length; t++) l += n[t] === " " ? r(t) : e.ideographicSpaceWidths.get(t);
		a === 0 ? c += l : (c = l, d = [t, a - 1]);
	}), c === s) l = 0;
	else if (d === void 0) l += a.state.naturalGapSum - (t?.scan.naturalGapSum ?? 0);
	else {
		let [t, n] = d, r = e.slice(0, t + 1), o = r[t];
		o.text !== void 0 && (r[t] = {
			...o,
			text: [...o.text].slice(0, n + 1).join("")
		}), l = a.state.naturalGapSum - i(r, !1).state.naturalGapSum;
	}
	let f = (e) => d === void 0 || e.segIndex - r > d[0] || e.segIndex - r === d[0] && e.cpOffset >= d[1], p = !u, m = p ? c : s;
	return {
		gaps: p && l > 0 ? a.gaps.filter((e) => !f(e)) : a.gaps,
		S: a.state.naturalGapSum - (p ? l : 0),
		naturalWidthPx: o,
		visibleWidthPx: o - m,
		lineEndSeparatorPx: m,
		segmentCount: r + e.length,
		scan: a.state,
		tail: {
			latinPx: s,
			fullPx: c,
			gapPx: l,
			rtl: u
		}
	};
}
function lf(e, t) {
	return !!(!("text" in e) || e.ruby || e.fitTextRegionIndex !== void 0 || t && /[^ ]/u.test(e.text) && !e.joinPrev && !e.hardJoinPrev || e.autoSpaceBeforePt !== void 0 && !e.joinPrev && !e.hardJoinPrev);
}
function uf(e, t) {
	return !("text" in e) || e.ruby || e.fitTextRegionIndex !== void 0 ? !0 : t === void 0 || lf(t, e.text.endsWith(" "));
}
function df(e, t) {
	let n = [e];
	if (!("text" in e) || e.ruby || e.fitTextRegionIndex !== void 0) return n;
	let r = e.text.endsWith(" ");
	for (let e of t) {
		if (lf(e, r)) break;
		n.push(e);
		let t = e.text;
		t.length > 0 && (r = t.endsWith(" "));
	}
	return n;
}
function ff(e) {
	return e.baseRtl && e.lineFit?.rtlVisiblePrefix !== !0;
}
function pf(e, t) {
	let n = e.order;
	return n.length === 0 ? !0 : e.rtl[t] === !0 ? n[0] === t : n.at(-1) === t;
}
function mf(e, t, n = 0, r = 0) {
	let i = 0;
	for (let r = e.length - 1; r >= n; --r) {
		let n = e[r];
		if (!("text" in n)) return i;
		if (n.text === "") continue;
		if (!n.text.endsWith(" ")) return i;
		t.reservePrefixWork(n.text.length);
		let a = n.text.replace(/ +$/u, "");
		if (i += t.segAdvance(n) - t.strAdvance(n, a), a.length > 0) return i;
	}
	return i + r;
}
var hf = /* @__PURE__ */ new WeakMap();
function gf(e, t) {
	let n = hf.get(e), r = n !== void 0 && n.length <= e.length && (n.length === 0 || e[n.length - 1] === n.last) ? mf(e, t, n.length, n.width) : mf(e, t);
	return hf.set(e, {
		length: e.length,
		last: e[e.length - 1],
		width: r
	}), r;
}
function _f(e, t, n, r = 0) {
	let i = n.segAdvance(e), a = 0;
	for (let o of t) if (!(a++ < r)) {
		if (!("text" in o) || o.fitTextRegionIndex !== e.fitTextRegionIndex) break;
		i += n.segAdvance(o);
	}
	return i;
}
function vf(e, t, n, r = n.segAdvance(e), i = 0, a = 0, o = !1, s = "prefix") {
	let { segAdvance: c, strAdvance: l } = n, u = s === "whole-word", d = s === "prefix" && e.explicitBreaks ? fc(e.explicitBreaks, 0) : e.text.length;
	n.reservePrefixWork(d);
	let f = e.text.slice(0, d), p = [{
		segment: e,
		text: f
	}];
	if (d < e.text.length) return {
		width: l(e, f) + (e.leadingWordBoundaryPx ?? 0),
		trailingSpace: 0,
		next: e,
		pieces: p
	};
	let m = r, h = e.fitTextRegionIndex === void 0 ? i : 0, g = 0, _;
	for (let e of t) {
		if (g++ < a) continue;
		if (_ = e, !("text" in e)) break;
		let t = u && e.explicitBreakBefore && e.hyperlink?.kind !== "external";
		if (!e.joinPrev && !t || o && e.fitTextRegionStart) break;
		let r = e.ruby !== void 0 || e.tateChuYoko === !0;
		e.hardJoinPrev && n.reservePrefixWork(e.text.length);
		let i = Zc(e), s = !u && e.explicitBreaks ? fc(e.explicitBreaks, 0) : void 0, d = r ? e.text.length : i ?? s ?? e.text.length;
		if (!r && i === void 0 && s === void 0 && tc(e.text)) {
			d = 0;
			for (let t of e.text) {
				if (!pe.lineStartForbidden.has(t.codePointAt(0))) break;
				d += t.length;
			}
		}
		n.reservePrefixWork(d);
		let f = e.text.slice(0, d);
		p.push({
			segment: e,
			text: f
		});
		let v = d === e.text.length ? c(e) : l(e, f);
		m += v;
		let y = f.replace(/ +$/, ""), b = !r && !ff(n) && f.endsWith(" ") ? v - l(e, y) : 0;
		if (h = y.length === 0 && h > 0 ? h + b : b, d < e.text.length || !r && s !== void 0 && i === void 0) break;
		_ = void 0;
	}
	return {
		width: m,
		trailingSpace: h,
		next: _,
		pieces: p
	};
}
function yf(e, t) {
	return ei(e, t);
}
function bf(e, t) {
	return ti(e, t);
}
function xf(e, t, n, r, i, a, o = 0, s = !1, c, l, u, d = 0, f = 0) {
	let p = t + n, m = Math.max(p, o), h = ml(i), g = h ? i.linePitchPt * r : 0, _ = () => {
		if (!s) return ai(m, g, f);
		let e = c ?? (o > 0 ? o : l === void 0 ? g : bf(0, l));
		return yf(a ? Math.max(p, e) : e, g) * g;
	}, v = e !== null && e.explicit !== !0;
	if (!e || ii(e.rule, e.value)) return h ? _() : m;
	if (e.rule === "auto") {
		if (h) {
			if (v) {
				let t = _();
				return s ? ni(t, g, e.value) : t;
			}
			return e.value === 1 ? _() : Math.max(m, g * e.value);
		}
		return d > 0 && e.value >= 1 ? Qr(m, d, e.value) : u ? u.normalSinglePx * e.value + Math.max(0, u.positionPx - u.designDescentPx) : m * e.value;
	}
	if (e.rule === "exact") return e.value * r;
	if (e.rule === "atLeast") {
		let t = h ? a || v ? _() : g : 0;
		return ri(m, e.value * r, t);
	}
	return m;
}
function Sf(e, t) {
	return {
		asc: e * t * _e,
		desc: e * t * ge
	};
}
function Cf(e, t) {
	return {
		ascent: e.fontBoundingBoxAscent ?? e.actualBoundingBoxAscent ?? t * .8,
		descent: e.fontBoundingBoxDescent ?? e.actualBoundingBoxDescent ?? t * .2
	};
}
var wf = 1e3, Tf = /* @__PURE__ */ new WeakMap();
function Ef(e, t, n, r, i, a, o) {
	if (n?.scope !== "native" || !r) return null;
	let s = "";
	for (let e of o) if (!/\s/u.test(e)) {
		s = e;
		break;
	}
	if (!s) return null;
	let c = Tf.get(e);
	c || (c = /* @__PURE__ */ new WeakMap(), Tf.set(e, c));
	let l = c.get(t);
	l || (l = /* @__PURE__ */ new Map(), c.set(t, l));
	let u = JSON.stringify([
		n.fingerprint,
		r,
		i,
		a,
		s
	]);
	if (l.has(u)) return l.get(u) ?? null;
	let d = Be(e, r, {
		text: s,
		emPx: 200,
		weight: i,
		style: a
	}), f = d === null ? null : Be(e, r, {
		text: s,
		emPx: wf,
		weight: i,
		style: a
	}), p = d !== null && f !== null && Math.abs(d - f) <= .012 ? f : null;
	return l.size >= 128 && l.clear(), l.set(u, p), p;
}
function Df(e, t, n, r, i = !1, a, o = {}, s = e.lineSpacing, c = {}, l, u, d = !1, f = 0) {
	let p = u, m = i && f <= 0 || p?.fontHint === "eastAsia", h = p?.complexScript === !0, g = p?.fontSizePt ?? af(e), _ = of(e, m), v = p?.weight ?? 400, y = p?.style ?? "normal", b = m ? "あ" : "x", x, S = s?.rule !== "exact", C = _, w, T, E, D = null;
	if (l) {
		let r = v >= 600, i = y === "italic", s = p?.fonts.ascii ?? e.defaultFontFamily ?? _, c = l.shape({
			text: b,
			fontSizePt: g * t,
			fonts: p?.fonts ?? {
				ascii: s,
				highAnsi: s,
				eastAsia: e.defaultFontFamilyEastAsia ?? s,
				complexScript: s
			},
			themeFonts: p?.themeFonts,
			themeFontPresence: p?.themeFontPresence,
			weight: r ? 700 : 400,
			style: i ? "italic" : "normal",
			complexScript: h,
			fontHint: p?.fontHint,
			eastAsiaLanguage: p?.eastAsiaLanguage,
			kerning: p?.kerning,
			measure: !0
		}), u = c.spans[0]?.font, d = Vu(l, (n?.linePitchPt ?? 0) > 0 && n?.type != null && n.type !== "default");
		x = u ? Gu(od(ad(l.fontMetrics ?? l.localMetrics), u, b, !1), d) : void 0, !S && x?.designAscentRatio != null && (x = void 0), E = S && !x && pd(u) && md(ad(l.fontMetrics ?? l.localMetrics ?? {}), u) ? Ju(u, {
			text: l,
			probe: b
		}, d) : void 0, S && !x && !E && u?.source === "native" && a && (D = Ef(a, o, u.route, u.resolvedFamily, u.weight, u.style, b));
		let f = {
			width: c.advancePt,
			actualBoundingBoxAscent: c.ascentPt,
			actualBoundingBoxDescent: c.descentPt,
			fontBoundingBoxAscent: c.ascentPt,
			fontBoundingBoxDescent: c.descentPt
		};
		({ascent: w, descent: T} = Cf(f, g * t));
	} else if (a) {
		let e = a.font;
		a.font = tf(!1, !1, g * t, C, o);
		let n = a.measureText(b);
		a.font = e, {ascent: w, descent: T} = Cf(n, g * t);
	} else ({asc: w, desc: T} = Sf(g, t));
	let O = x?.designAscentRatio != null && x?.designDescentRatio != null ? x : E;
	O && (w = O.designAscentRatio * g * t, T = O.designDescentRatio * g * t), w = Math.max(w, f);
	let k = m ? x?.eastAsianLineHeightRatio ?? x?.lineHeightRatio : x?.lineHeightRatio, A = E ? E.lineHeightRatio * g * t : k == null ? 0 : k * g * t, j = Math.max(A, (D ?? 0) * g * t), M = i ? Math.max(bf(A, g * t), f > 0 ? w + T : 0) : void 0, N = xf(s, w, T, t, n, r, j, i, M), P = d && i && ml(n), F = P ? xf(null, w, T, t, n, r, j, i, M) : N, I = P ? xf({
		rule: "atLeast",
		value: 0,
		explicit: !0
	}, w, T, t, n, r, j, i, M) : N, L = d ? mr({
		ordinaryAdvancePx: N,
		allocatedGridAdvancePx: F,
		atLeastZeroAdvancePx: I,
		lineSpacing: s,
		gridAllocationActive: P,
		scale: t
	}) : N, R = xf(s, w, T, t, void 0, r, j, i, M);
	return {
		advancePx: L,
		gridAfterLeadingPx: ml(n) ? Math.max(0, Math.min((L - R) / 2, kf(L, w, T) - T)) : 0,
		ascentPx: w,
		descentPx: T,
		intendedSinglePx: j
	};
}
function Of(e, t, n, r, i = !1, a, o = {}, s = e.lineSpacing, c = {}, l, u, d = !1) {
	return Df(e, t, n, r, i, a, o, s, c, l, u, d).advancePx;
}
function kf(e, t, n) {
	return Math.max(0, (e - t + n) / 2);
}
function Af(e, t, n, r, i, a = {}) {
	if (t != null) return t * n;
	if (!r?.ruby || !i) throw Error(`Ruby at ${e}pt without hpsRaise requires retained base and guide ink`);
	if (r.textLayoutService && r.textShapeRequest) {
		let e = r.textLayoutService.shape({
			...r.textShapeRequest,
			fontSizePt: q(r, n),
			measure: !0,
			clusterGeometry: !1
		}), t = r.textLayoutService.shape({
			...As(r.textShapeRequest, r.ruby.text),
			fontSizePt: r.ruby.fontSizePt * n,
			measure: !0,
			clusterGeometry: !1
		});
		if (e.inkBounds && t.inkBounds) return e.inkBounds.ascentPt + t.inkBounds.descentPt;
	}
	let o = i.font;
	try {
		i.font = tf(r.bold, r.italic, q(r, n), r.fontFamily, a, r.fontRoute);
		let t = i.measureText(r.text);
		i.font = tf(r.bold, r.italic, e * n, r.fontFamily, a, r.fontRoute);
		let o = i.measureText(r.ruby.text);
		if (Number.isFinite(t.actualBoundingBoxAscent) && Number.isFinite(o.actualBoundingBoxDescent)) return t.actualBoundingBoxAscent + o.actualBoundingBoxDescent;
	} finally {
		i.font = o;
	}
	throw Error("Ruby without hpsRaise requires retained base and guide ink");
}
function jf(e, t, n, r, i, a) {
	let o = i.text.codePointAt(0), s = e.currentLine[e.currentLine.length - 1];
	if (o === void 0 || !t.lineStartForbidden.has(o) || s === void 0 || !("text" in s)) return { kind: "none" };
	let c = s, l = [...c.text], u = ae(l, t, e.currentLine.length > 1 ? 0 : 1);
	if (u <= 0) return { kind: "none" };
	let d = l.slice(0, l.length - u).join(""), f = d.length;
	if (f === 0 && c.hardJoinPrev === !0 || Yc(c).has(f)) return { kind: "blocked" };
	n(), e.latinLineHomogeneous = !1;
	let p = c.text.slice(f), m = {
		...c,
		...Fc,
		text: p,
		...J(c, f, c.text.length),
		measuredWidth: r(c, p, !0),
		joinPrev: void 0,
		hardJoinPrev: void 0,
		src: Oc(c.src, f),
		seaBreaks: ac(c.seaBreaks, f)
	};
	if (d) {
		let t = r(c, d), n = Math.max(c.leadingWordBoundaryPx ?? 0, -t), i = t + n;
		e.currentWidth -= c.measuredWidth - i, kl(e, {
			...c,
			...Fc,
			text: d,
			measuredWidth: i,
			...n === 0 ? {} : { leadingWordBoundaryPx: n },
			...J(c, 0, f)
		}, a);
	} else e.currentWidth -= c.measuredWidth, Ol(e);
	return {
		kind: "retracted",
		tail: m
	};
}
function Mf(e, t, n, r, i, a, o, s) {
	let c = b(i.text)[0] ?? i.text.length;
	if (c <= 0) return !1;
	let l = i.text.slice(0, c), u = t(i, l);
	return n({
		...i,
		...Fc,
		text: l,
		measuredWidth: u,
		...J(i, 0, c)
	}, u, a, o, s), c < i.text.length && r(i, c), !0;
}
function Nf(e, t) {
	return e.latinSpaceCompressionEligible === !0 && !e.verticalRun && !t.verticalRun && !e.tateChuYoko && !t.tateChuYoko && e.latinSpaceAverageWidthRatio === t.latinSpaceAverageWidthRatio && e.fontRoute?.fingerprint === t.fontRoute?.fingerprint && e.fontFamily === t.fontFamily && e.fontSize === t.fontSize && e.bold === t.bold && e.italic === t.italic && (e.charScale == null || e.charScale === 1) && (t.charScale == null || t.charScale === 1) && e.kerning === t.kerning && e.widthBalanceGridDeltaFactor === t.widthBalanceGridDeltaFactor && !e.rtl && e.fitTextRegionIndex === void 0;
}
function Pf(e) {
	let { breakerState: t } = e;
	for (let e = 0; e < t.latinAppliedGapCount; e += 1) {
		let n = t.latinLineGaps[e];
		n.measuredWidth -= t.latinAppliedPerGap, n.latinSpaceCompressionPx = t.latinAppliedPerGap;
	}
	t.latinAppliedGapCount = 0, t.latinAppliedPerGap = 0;
}
var Ff = class extends Error {
	requiredWidth;
	stopBefore;
	constructor(e, t) {
		super("A narrowed float gap cannot admit the line-head unit"), this.requiredWidth = e, this.stopBefore = t, this.name = "LineGapRejection";
	}
};
function If(e, t) {
	let { wrapCtx: n, segs: r, breakerState: i, scale: a } = e;
	if (!n) return 0;
	let o = t?.segIndex ?? 0;
	function* s() {
		for (let e = o; e < r.length; e += 1) yield r[e];
	}
	let c = t ? s() : i.queue, l;
	for (let e of c) {
		if ("text" in e && !e.metricOnly && e.text.length > 0 || "imagePath" in e && !e.anchor || "math" in e || "isTab" in e || "lineBreak" in e) return 0;
		"text" in e && e.metricOnly && (l ??= e);
	}
	return (t ? o >= r.length : i.queue.length === 0) ? 0 : n.paragraphMarkLineStartWidth ?? (l ? l.fontSize * a : 0);
}
function Lf(e, t) {
	return e.strAdvance(t, Rf(e, t));
}
function Rf(e, t) {
	let { lineEdgeRules: n } = e, r = t.text, i = r.length;
	if (t.fitTextRegionIndex === void 0 && !t.ruby && !t.tateChuYoko) {
		let e = Yc(t);
		if (t.hardJoinPrev === !0) i = Zc(t) ?? r.length;
		else if (t.seaBreaks !== void 0) i = t.seaBreaks.find((e) => e > 0 && e < r.length) ?? r.length;
		else if (tc(r)) {
			let e = [...r];
			for (let r = 1; r < e.length; r += 1) {
				if (W(e, r, n, 0) !== r) continue;
				let a = e.slice(0, r).join("").length;
				if (Xc(t, a, 1) === a) {
					i = a;
					break;
				}
			}
		} else i = [...pc(t.explicitBreaks)].find((t) => t > 0 && t < r.length && !e.has(t)) ?? r.length;
	}
	let a = r.slice(0, i);
	return ff(e) ? a : a.replace(/ +$/u, "");
}
function zf(e, t) {
	let { breakerState: n, overflowPunct: r } = e;
	if (!r) return t;
	let i = n.queue[Symbol.iterator](), a = i.next(), o = n.currentLine.length > 0;
	for (; !a.done && zd(a.value);) o = !0, a = i.next();
	if (a.done || !("text" in a.value)) return t;
	let s = a.value, c = Rf(e, s), l = 0, u = [...c].length;
	for (let t = i.next(); c === s.text && !t.done && "text" in t.value && t.value.joinPrev === !0; t = i.next()) l += e.strAdvance(s, c), s = t.value, c = Rf(e, s), u += [...c].length;
	if (Math.abs(l + e.strAdvance(s, c) - t) > 1e-6) return t;
	let d = [...c.replace(/ +$/u, "")];
	u -= [...c].length - d.length;
	let f = d.at(-1);
	return u < 2 && !o || f === void 0 || !Wr(f, s.eastAsiaLanguage, s.overflowPunctuationEastAsianRun === !0, s.script === "ascii" || s.script === "highAnsi", s.script === "complexScript", s.overflowPunctuationBidiLanguage) ? t : l + e.strAdvance(s, d.slice(0, -1).join(""));
}
function Bf({ breakerState: e }) {
	e.lineHeight = 0, e.lineAscent = 0, e.lineDescent = 0, e.lineIntendedSingle = 0, e.lineHasInlinePicture = !1, e.linePictureMarkSingle = 0, e.lineObjectBaselineMinimum = 0, e.lineObjectAdvanceMinimum = 0, e.lineGridCountSingle = 0, e.lineLatinGridCountSingle = 0, e.lineVisibleAscent = 0, e.lineVisibleDescent = 0, e.lineVisibleIntendedSingle = 0, e.lineHasVisibleMetrics = !1, e.lineMarkerHeight = 0, e.lineMarkerAscent = 0, e.lineHasRuby = !1, e.lineEastAsian = !1, e.positionReferencePt = void 0, e.firstPositioned = void 0, e.uniformPositionEligible = !0;
}
function Vf(e, t) {
	if (!(!e || e.length === 0)) return e[t] ?? e[e.length - 1];
}
function Hf(e) {
	let { breakerState: t } = e;
	Bf(e), t.lines.length > 0 && (t.physicalLineIndex += 1);
}
function Uf({ marginRightPx: e, maxWidth: t }) {
	return Math.max(0, e - t);
}
function Wf(e, t = 0) {
	let { breakerState: n, maxWidth: r, wrapCtx: i, firstIndent: a, probeFloors: o } = e;
	n.snapBlock = null, n.lineXOffset = 0, n.lineMaxWidth = r, n.lineMarginExtension = Uf(e), n.gapTransaction = null;
	let s = n.fragmentCursor;
	if (n.fragmentCursor = null, !i || Vf(o, n.physicalLineIndex) === void 0) {
		Hf(e);
		return;
	}
	let c = {
		cursor: s,
		requestTopY: n.currentLineTopY,
		requirement: t + (n.isFirst && !i.numberingFirstLine ? Math.max(0, a) : 0),
		window: null,
		narrowed: !1,
		endsAtExclusion: !1,
		snapshot: null,
		stopBefore: null
	};
	n.gapTransaction = c, s || Hf(e), Yf(e, c, null);
}
function Gf(e, t, n) {
	let { breakerState: r, baseRtl: i } = e, a = Kf(e, t, n, r.lineXOffset, r.lineMaxWidth);
	if (!a) {
		r.firstIndentOverride = void 0, r.numberingFirstLine = void 0;
		return;
	}
	let { windowEdge: o, leadingEdge: s, bodyIndent: c } = a;
	i || (r.lineXOffset += n), r.lineMaxWidth -= n, r.firstIndentOverride = c - o, r.numberingFirstLine = {
		leadingEdgePx: s,
		bodyIndentPx: c,
		lineStartOffsetPx: c - o
	};
}
function Kf(e, t, n, r, i) {
	let { maxWidth: a, baseRtl: o } = e, s = (o ? a - (r + i) : r) + n, c = t.authoredFirstIndentPx, l = t.columnOriginInsetPx === void 0 ? Math.max(Math.max(0, s) + c, s) : s + t.columnOriginInsetPx + c;
	return t.columnOriginInsetPx === void 0 && l <= c ? null : {
		windowEdge: s,
		leadingEdge: l,
		bodyIndent: Math.max(l, t.bodyIndentAt(l))
	};
}
function qf(e, t, n, r, i) {
	let a = i + n, o = Kf(e, t, n, r, a);
	return o ? np(e, {
		xOffset: e.baseRtl ? r : r + n,
		maxWidth: i
	}, i - (o.bodyIndent - o.windowEdge)) : np(e, {
		xOffset: r,
		maxWidth: a
	}, a - e.paragraphFirstIndent);
}
function Jf(e, t, n) {
	return e ? t.xOffset > 1e-9 : t.xOffset + t.maxWidth < n - 1e-9;
}
function Yf(e, t, n) {
	let { breakerState: r, maxWidth: i, wrapCtx: a, baseRtl: o, firstIndent: s, probeFloors: c, preparedFloatWrap: l } = e;
	if (!a) return;
	let u = r.isFirst ? a.numberingFirstLine : void 0, d = r.isFirst ? u?.columnOriginInsetPx === void 0 ? Math.min(0, u ? u.authoredFirstIndentPx : s) : -u.columnOriginInsetPx : 0, f = a.paraX + (o ? 0 : d), p = i - d, m = {
		xLeftPt: a.referenceXPt ?? a.paraX,
		xRightPt: (a.referenceXPt ?? a.paraX) + (a.referenceWidthPt ?? i),
		readingDirection: a.readingDirection ?? (o ? "rtl" : "ltr")
	}, h = u ? t.numberingHead : void 0, g = t.numberingHangingHead ?? h, _ = u && h !== void 0 && g !== void 0 ? (t) => e.fitsMeasuredWidth(Jf(o, t, p) ? h : g, qf(e, u, d, t.xOffset, t.maxWidth)) : void 0, v = (e, n, r, i, o = t.requirement, s) => {
		if (a.indentsFromFloats === !0) {
			let t = a.columnXPt + a.columnWidthPt, c = n - a.columnXPt, l = t - (n + r);
			if (c >= 0 && l >= 0 && (c > 0 || l > 0)) {
				let t = (e) => ({
					xOffset: a.columnXPt + e.xOffset + c - n,
					maxWidth: Math.max(0, e.maxWidth - c - l)
				}), r = y(e, a.columnXPt, a.columnWidthPt, i, o + c + l, s ? (e) => s(t(e)) : void 0);
				return {
					topY: r.topY,
					...t(r)
				};
			}
		}
		return y(e, n, r, i, o, s);
	}, y = (e, t, n, r, i, o) => {
		if (a.lineWindow) {
			let s = a.lineWindow({
				topYPt: e,
				minimumStartWidthPt: i,
				squareMinimumStartWidthPt: i,
				probeHeightPt: r,
				paragraphXPt: t,
				maximumWidthPt: n,
				columnXPt: a.columnXPt,
				columnWidthPt: a.columnWidthPt,
				...o ? { admitsWindow: o } : {}
			});
			return {
				topY: s.topYPt,
				xOffset: s.xOffsetPt,
				maxWidth: s.maximumWidthPt
			};
		}
		return Fo(e, i, r, t, n, l ?? no(a.floats), a.columnXPt, a.columnXPt + a.columnWidthPt, m, i, o);
	}, b = o ? f : f + p, x = (e, n) => {
		let r = e + n.xOffset;
		return t.farEdgeRequirement !== void 0 && (o ? r <= b + 1e-9 : r + n.maxWidth >= b - 1e-9) ? t.farEdgeRequirement : t.requirement;
	}, S = 32, C = (e, n, r, i) => {
		let a = t.farEdgeRequirement;
		if (a === void 0 || a === t.requirement) return v(e, n, r, i);
		let o = Math.min(a, t.requirement), s = Math.max(a, t.requirement), c = (e) => e.maxWidth >= x(n, e), l = v(e, n, r, i, o);
		if (c(l)) return l;
		let u = v(e, n, r, i, s), d = Mo(i);
		for (; d !== null && l.topY < u.topY && Math.abs(l.topY) <= ko && Math.abs(e) <= ko && S > 0 && (--S, l = v(No(e, d, l.topY), n, r, i, o), !(l.topY > u.topY));) if (c(l)) return l;
		return u;
	}, w = null, T = t.cursor;
	if (T) {
		let n = Vf(c, r.physicalLineIndex), i = o ? f : T.right, s = o ? T.left : f + p;
		if (n !== void 0 && s > i) {
			let e = C(T.topY, i, s - i, n);
			e.topY === T.topY && e.maxWidth >= x(i, e) && (w = {
				topY: e.topY,
				xOffset: i - a.paraX + e.xOffset,
				maxWidth: e.maxWidth,
				solverWidth: e.maxWidth,
				narrowed: !0,
				solverBandX: i,
				solverXOffset: e.xOffset
			});
		}
		w || (t.cursor = null, Hf(e), r.currentLineTopY = t.requestTopY);
	}
	if (!w) {
		let n = Vf(c, r.physicalLineIndex);
		if (n === void 0) {
			r.lineXOffset = 0, r.lineMaxWidth = i, r.lineMarginExtension = Uf(e), t.window = null, t.narrowed = !1, t.endsAtExclusion = !1, t.snapshot = null;
			return;
		}
		let a = _ ? v(t.requestTopY, f, p, n, t.requirement, _) : C(t.requestTopY, f, p, n);
		w = {
			topY: a.topY,
			xOffset: a.xOffset,
			maxWidth: a.maxWidth + d,
			solverWidth: a.maxWidth,
			narrowed: a.xOffset !== 0 || a.maxWidth !== p,
			solverBandX: f,
			solverXOffset: a.xOffset
		};
	}
	n && w.narrowed && w.solverWidth < x(w.solverBandX, {
		xOffset: w.solverXOffset,
		maxWidth: w.solverWidth
	}) && (w = {
		...w,
		narrowed: !1
	}), n && _ && w.narrowed && w.topY === n.topY && w.xOffset === n.xOffset && w.solverWidth === n.solverWidth && (w = {
		...w,
		narrowed: !1
	}), r.currentLineTopY = w.topY, r.lineXOffset = w.xOffset, r.lineMaxWidth = w.maxWidth, u && Gf(e, u, d);
	let E = Uf(e), D = Vf(c, r.physicalLineIndex);
	if (w.narrowed || E <= 0 || o) r.lineMarginExtension = 0;
	else if (D === void 0) r.lineMarginExtension = E;
	else {
		let e = v(w.topY, a.paraX + i, E, D, E);
		r.lineMarginExtension = e.topY === w.topY && e.xOffset === 0 && e.maxWidth >= E ? E : 0;
	}
	let { solverBandX: O, solverXOffset: k, ...A } = w;
	t.window = A, t.narrowed = w.narrowed;
	let j = a.paraX + w.xOffset, M = j + w.maxWidth;
	t.endsAtExclusion = o ? j > f + 1e-9 : M < f + p - 1e-9, t.snapshot = null, w.narrowed && Xf(e, !0);
}
function Xf(e, t) {
	let { breakerState: n } = e, r = n.gapTransaction;
	if (!r?.narrowed) return;
	let { lines: i, queue: a, currentLine: o, latinLineGaps: s, gapTransaction: c, inHand: l, snapBlock: u, ...d } = n;
	r.snapshot = {
		scalars: { ...d },
		snapBlock: u ? { ...u } : null,
		linesLength: i.length,
		queue: a.snapshot(t ? l : void 0)
	};
}
function Zf(e, t, n = 0) {
	let { breakerState: r } = e, i = r.gapTransaction;
	if (!i?.narrowed || !i.snapshot) return;
	let a = !1;
	for (let e = 0; e < n && e < r.currentLine.length; e += 1) if (!zd(r.currentLine[e])) {
		a = !0;
		break;
	}
	let o = a ? r.currentLine[n] : void 0;
	throw new Ff(t, o?.src ? { ...o.src } : void 0);
}
function Qf(e, t) {
	return t ? "text" in t ? e.minimalLegalTextWidth(t) : "imagePath" in t ? t.anchor ? 0 : t.widthPt * e.scale : "math" in t ? t.measuredWidth : 0 : 0;
}
function $f(e, t) {
	let { breakerState: n, firstIndent: r, maxWidth: i } = e, a = n.gapTransaction, o = a?.snapshot;
	if (!a || !o || !a.window) throw t;
	if (Object.assign(n, o.scalars), n.snapBlock = o.snapBlock ? { ...o.snapBlock } : null, n.lines.length = o.linesLength, n.queue.restore(o.queue), n.currentLine = [], n.latinLineGaps = [], n.mixedSpace = Sl(), n.inHand = void 0, t.stopBefore && !a.stopBefore) {
		a.stopBefore = t.stopBefore;
		return;
	}
	a.stopBefore = null;
	let s = a.window, c = n.isFirst ? e.wrapCtx?.numberingFirstLine : void 0;
	if (c && a.cursor === null) {
		let n = c.columnOriginInsetPx === void 0 ? Math.min(0, c.authoredFirstIndentPx) : -c.columnOriginInsetPx, r = Math.max(a.numberingHead ?? 0, t.requiredWidth), i = Math.max(a.numberingHangingHead ?? 0, zf(e, t.requiredWidth));
		if (!e.fitsMeasuredWidth(a.endsAtExclusion ? r : i, qf(e, c, n, s.xOffset, s.solverWidth))) {
			a.numberingHead = r, a.numberingHangingHead = i, a.farEdgeRequirement = void 0, a.requirement = i / (e.lineFit?.fraction ?? 1), Yf(e, a, s);
			return;
		}
	}
	if (ap(e)) {
		let o = n.isFirst ? Math.min(0, r) : 0, c = ip(e, t.requiredWidth);
		(a.endsAtExclusion ? c.interior : c.farEdge) > s.solverWidth ? (a.farEdgeRequirement = Math.max(a.farEdgeRequirement ?? a.requirement, c.farEdge), a.requirement = Math.max(a.requirement, c.interior)) : (a.farEdgeRequirement = void 0, a.requirement = i - o), Yf(e, a, s);
		return;
	}
	let l = n.isFirst ? Math.min(0, r) : 0, u = t.requiredWidth + (n.isFirst ? Math.max(0, r) : 0);
	a.requirement = u > s.solverWidth ? Math.max(a.requirement, u) : i - l, Yf(e, a, s);
}
function ep(e) {
	let { breakerState: t, firstIndent: n, widthPolicy: r } = e;
	return r === "bounded" ? tp(e, t.lineMaxWidth - (t.isFirst ? n : 0)) : Infinity;
}
function tp(e, t) {
	return np(e, {
		xOffset: e.breakerState.lineXOffset,
		maxWidth: e.breakerState.lineMaxWidth
	}, t);
}
function np(e, t, n) {
	let r = e.lineFit;
	return r === void 0 ? n : r.reserveShare === 0 ? n * r.fraction : n * r.fraction - r.reserveShare * Math.max(0, t.maxWidth + rp(e, t));
}
function rp(e, t) {
	let { maxWidth: n, marginRightPx: r, tabOriginPx: i, baseRtl: a } = e;
	if (a) return t.xOffset > 1e-9 ? 0 : i + t.xOffset;
	let o = t.xOffset + t.maxWidth;
	return o < n - 1e-9 ? 0 : r - o;
}
function ip(e, t) {
	let n = e.lineFit, { breakerState: r, firstIndent: i, maxWidth: a, marginRightPx: o, tabOriginPx: s, baseRtl: c } = e, l = r.isFirst ? i : 0, u = r.isFirst ? Math.min(0, i) : 0, d = (e) => {
		let r = t / n.fraction + l;
		return n.reserveShare === 0 || r + e <= 0 ? r : (t + n.fraction * l + n.reserveShare * e) / (n.fraction - n.reserveShare);
	}, f = c ? s : o - a;
	return {
		interior: d(0) - u,
		farEdge: d(f) - u
	};
}
function ap(e) {
	let t = e.lineFit;
	return t !== void 0 && (t.fraction !== 1 || t.reserveShare !== 0);
}
function op(e, t, n) {
	let { breakerState: r, firstIndent: i, widthPolicy: a } = e;
	if (eu(t, n)) return !0;
	if (a !== "bounded" || !Number.isFinite(t) || !Number.isFinite(r.lineMaxWidth)) return !1;
	let o = e.lineFit;
	return o !== void 0 && (o.fraction !== 1 || o.reserveShare !== 0) ? !1 : t + (r.isFirst ? i : 0) <= r.lineMaxWidth;
}
function sp(e) {
	return "listLabel" in e && e.listLabel !== void 0;
}
function cp(e, t, n = !1, r) {
	let { breakerState: i, materializeLatinSpaceCompression: a, lineHeadRequirement: o, startLine: s, bidiCustomStopsPx: c, bidiIntervalPx: l, endBoundary: u, strAdvance: d, decimalAlignmentPoint: f, firstIndent: p, scale: m, wrapCtx: h, tabOriginPx: g, marginRightPx: _, baseRtl: v } = e, y = Qf(e, i.inHand);
	!n && r !== void 0 && y > 0 && i.currentLine.length > 0 && i.currentLine.every(zd) && e.forcedPlacement(y), a(), Gl(e), i.currentWidth += wc({
		baseRtl: v,
		bidiOrdering: e.bidiOrdering,
		decimalOrder: e.passContext.decimalOrder,
		isJustified: e.isJustified,
		stretchLastLine: e.stretchLastLine,
		endsWithBreak: n,
		...e.lineFit ? { fitWidth: e.availW() } : {},
		currentLine: i.currentLine,
		marginRightPx: _,
		maxWidth: e.maxWidth,
		lineXOffset: i.lineXOffset,
		lineMaxWidth: i.lineMaxWidth,
		isFirst: i.isFirst,
		firstIndent: p,
		tabOriginPx: g,
		bidiCustomStopsPx: c,
		bidiIntervalPx: l,
		decimalAlignmentPoint: f,
		strAdvance: d
	});
	for (let e of i.currentLine) {
		if ("isTab" in e) continue;
		let t = "text" in e && e.positionExtendsLineBox !== !1 ? e.position ?? 0 : 0;
		if (i.positionReferencePt === void 0 ? i.positionReferencePt = t : i.positionReferencePt !== t && (i.positionReferencePt = null), !("text" in e)) {
			i.uniformPositionEligible = !1;
			continue;
		}
		i.firstPositioned ??= e;
		let n = i.firstPositioned;
		i.uniformPositionEligible &&= e.text.length > 0 && !e.metricOnly && !e.ruby && !e.vertAlign && e.positionExtendsLineBox !== !1 && e.position === n.position && e.fontFamily === n.fontFamily && e.fontRoute?.fingerprint === n.fontRoute?.fingerprint && e.bold === n.bold && e.italic === n.italic && e.fontSize === n.fontSize && e.resolvedDesignDescentRatio === n.resolvedDesignDescentRatio && e.referenceFontVerticalMetric === n.referenceFontVerticalMetric && e.resolvedResourceVerticalMetric === n.resolvedResourceVerticalMetric;
	}
	let b = i.positionReferencePt ?? 0, x = t === void 0 ? i.lineHeight || 10 : Math.max(i.lineHeight, t), S = i.lineAscent > 0 || i.lineDescent > 0, C = S ? i.lineAscent : x * m * .8, w = S ? i.lineDescent : x * m * .2, T = Math.max(C, i.lineMarkerAscent), E = Math.max(0, i.lineObjectBaselineMinimum - T - w), D = T + E, O = Math.max(i.lineIntendedSingle, i.lineObjectAdvanceMinimum), k = Math.max(x, i.lineMarkerHeight), A = i.lineHasVisibleMetrics ? Math.max(i.lineVisibleAscent, i.lineMarkerAscent) + E : D, j = i.lineHasVisibleMetrics ? i.lineVisibleDescent : w, M = i.lineHasVisibleMetrics ? i.lineVisibleIntendedSingle : i.lineIntendedSingle, N = Math.max(i.lineGridCountSingle || (i.lineEastAsian ? bf(i.lineIntendedSingle, x * m) : C + w), i.lineMarkerAscent), P = i.lineHasInlinePicture ? Math.max(i.lineIntendedSingle, i.linePictureMarkSingle) : i.lineMarkerAscent > 0 ? Math.max(i.lineIntendedSingle, C + w) : 0, F = i.firstPositioned, I = b !== 0 && i.uniformPositionEligible && F?.resolvedDesignDescentRatio != null && (F.referenceFontVerticalMetric || F.resolvedResourceVerticalMetric) ? {
		normalSinglePx: Math.max(D + w - Math.abs(b * m), i.lineIntendedSingle),
		positionPx: b * m,
		designDescentPx: F.resolvedDesignDescentRatio * F.fontSize * m
	} : void 0, L = Sp(e) && (!e.justifiedCompressionAdmissionOnly || i.justifiedCompressionPx > 0) ? cf(i.currentLine.map((t) => Op(e, t))) : void 0, R = i.currentLine.length > 0 && i.currentLine.every(sp);
	i.lines.push({
		...i.isFirst && i.numberingFirstLine ? { numberingFirstLine: i.numberingFirstLine } : {},
		...i.isFirst && i.lines.length > 0 ? { listLabelFirstIndent: !0 } : {},
		...i.lineLabelShiftPx === 0 ? {} : { listLabelShiftPx: i.lineLabelShiftPx },
		physicalLineIndex: i.physicalLineIndex,
		...L ? {
			justifiedCompressionPx: Math.min(i.justifiedCompressionPx, Math.max(0, L.visibleWidthPx - e.availW())),
			gapPlan: {
				...L,
				expansionGaps: Cp(i.currentLine)
			}
		} : {},
		segments: i.currentLine,
		height: k,
		ascent: D,
		descent: w,
		visibleAscent: A,
		visibleDescent: j,
		visibleIntendedSingle: M,
		intendedSingle: O,
		latinGridCountSingle: i.lineLatinGridCountSingle,
		...P > 0 ? { inlinePictureTextSingle: P } : {},
		uniformPositionAuto: I,
		gridCountSingle: N,
		xOffset: i.lineXOffset,
		availWidth: i.lineMaxWidth,
		...i.currentLine.some((e) => "isTab" in e && e.marginAllocation) ? { marginExtension: i.lineMarginExtension } : {},
		topY: h ? i.currentLineTopY : void 0,
		hasRuby: i.lineHasRuby,
		eastAsian: i.lineEastAsian,
		endsWithBreak: n,
		consumedEnd: r ?? i.queue.peek()?.src ?? (n ? {
			...u,
			trailingEmptyLine: !0
		} : u)
	}), h && (!n && r !== void 0 && (i.fragmentCursor = {
		topY: i.currentLineTopY,
		left: h.paraX + i.lineXOffset + (i.isFirst ? Math.min(0, p) : 0),
		right: h.paraX + i.lineXOffset + i.lineMaxWidth
	}), i.currentLineTopY += e.probeHeights?.[i.physicalLineIndex] ?? h.lineBoxH(D, w, i.lineHasRuby, O, i.lineEastAsian, N, I, P, i.lineLatinGridCountSingle)), i.currentLine = [], i.currentWidth = 0, i.justifiedGapModel = void 0, i.justifiedCompressionPx = 0, i.justifiedUnitEnd = void 0, i.latinLineFace = void 0, i.latinLineHomogeneous = !0, i.latinLineGaps = [], i.latinUniformGapCapacity = void 0, i.lineLabelShiftPx = 0, i.isFirst = i.isFirst && R, s(o(r));
}
function lp(e, t, n) {
	let { breakerState: r, snapPitchPx: i, eastAsianSnapCellCount: a, characterGrid: o } = e, s = fl(t, o);
	return !s || i == null ? n : s === "eastAsia" ? pl(n, s, i, a(t)) : r.snapBlock?.kind === s ? pl(r.snapBlock.naturalWidthPx + n, s, i) - r.snapBlock.allocatedWidthPx : pl(n, s, i);
}
function up(e, t, n, r, i, a) {
	let { breakerState: o, sameLatinSpaceFace: s, materializeLatinSpaceCompression: c, snapPitchPx: l, effectiveFontPx: u, eastAsianSnapCellCount: d, ctx: f, scale: p, fontFamilyClasses: m, characterGrid: h } = e;
	o.justifiedUnitEnd === t && (o.justifiedUnitEnd = void 0);
	let g = n;
	if ("text" in t && t.autoSpaceBeforePt !== void 0) {
		let r = hp(e, t);
		r !== 0 && (n += r, g = n);
	}
	if ("text" in t) {
		let r = t.leadingWordBoundaryPx ?? 0, i = Np(e, t, n - r);
		t.leadingWordBoundaryPx = i === 0 ? void 0 : i, i !== r && (n += i - r, g = n);
	}
	if ("text" in t) {
		let e = fl(t, h), r = t.snapGridNaturalWidthPx ?? n;
		if (e && l != null) if (t.snapGridClass = e, t.snapGridNaturalWidthPx = r, t.snapGridCellPitchPx = l, e === "eastAsia") g = pl(r, e, l, d(t)), t.snapGridLeadingPadPx = 0, t.snapGridTrailingPadPx = g - r, t.measuredWidth = g, o.snapBlock = null;
		else if (o.snapBlock?.kind === e) {
			let n = o.snapBlock.first.snapGridLeadingPadPx ?? 0, i = o.snapBlock.last.snapGridTrailingPadPx ?? 0, a = o.snapBlock.naturalWidthPx + r, s = pl(a, e, l), c = s - a, u = e === "latin" ? c / 2 : 0, d = c - u;
			o.snapBlock.first.measuredWidth -= n, o.snapBlock.first.snapGridLeadingPadPx = u, o.snapBlock.first.measuredWidth += u, o.snapBlock.last.measuredWidth -= i, t.snapGridLeadingPadPx = 0, t.snapGridTrailingPadPx = d, t.measuredWidth = r + d, g = s - o.snapBlock.allocatedWidthPx, o.snapBlock = {
				kind: e,
				first: o.snapBlock.first,
				last: t,
				naturalWidthPx: a,
				allocatedWidthPx: s
			};
		} else {
			let n = pl(r, e, l), i = n - r, a = e === "latin" ? i / 2 : 0, s = i - a;
			t.snapGridLeadingPadPx = a, t.snapGridTrailingPadPx = s, t.measuredWidth = n, g = n, o.snapBlock = {
				kind: e,
				first: t,
				last: t,
				naturalWidthPx: r,
				allocatedWidthPx: n
			};
		}
		else t.snapGridClass = void 0, t.snapGridLeadingPadPx = void 0, t.snapGridTrailingPadPx = void 0, t.snapGridCellPitchPx = void 0, t.measuredWidth = n, o.snapBlock = null;
	} else o.snapBlock = null;
	if (Dl(o, t, p), o.currentWidth += g, ("text" in t || "imagePath" in t) && (t.listLabel === "end" || t.listLabel === "center")) {
		let e = g * (t.listLabel === "end" ? 1 : .5);
		o.currentWidth -= e, o.lineLabelShiftPx += e;
	}
	if (Sp(e) && (!e.justifiedCompressionAdmissionOnly || o.justifiedGapModel !== void 0)) {
		let n = o.justifiedGapModel;
		o.justifiedGapModel = n?.segmentCount === o.currentLine.length - 1 ? cf([Op(e, t)], n, !1) : cf(o.currentLine.map((t) => Op(e, t)), void 0, !1);
	}
	if ("text" in t && t.latinSpaceCompressionEligible === !0 && t.latinSpaceAverageWidthRatio != null && t.fontRoute) {
		if (o.latinLineFace && !s(t, o.latinLineFace) && (c(), o.latinLineHomogeneous = !1), o.latinLineFace ??= t, t.latinNaturalTrailingSpacePx !== void 0) {
			let e = Math.max(0, t.latinNaturalTrailingSpacePx - (q(t, p) * t.latinSpaceAverageWidthRatio / 2 * tl(t) + zc(t, h, p)));
			o.latinUniformGapCapacity !== void 0 && Math.abs(e - o.latinUniformGapCapacity) > 1e-6 && (c(), o.latinLineHomogeneous = !1), o.latinUniformGapCapacity ??= e, o.latinLineGaps.push(t);
		}
	} else e.isJustified && zd(t) || (c(), o.latinLineHomogeneous = !1);
	r > o.lineHeight && (o.lineHeight = r), "imagePath" in t && t.inlinePicture === !0 && (o.lineHasInlinePicture = !0, o.lineObjectBaselineMinimum = Math.max(o.lineObjectBaselineMinimum, (t.objectRunBaselineMinimumPx ?? 0) * p), o.lineObjectAdvanceMinimum = Math.max(o.lineObjectAdvanceMinimum, (t.objectRunAdvanceMinimumPx ?? 0) * p), o.linePictureMarkSingle = Math.max(o.linePictureMarkSingle, (t.paragraphMarkSinglePx ?? 0) * p)), i > o.lineAscent && (o.lineAscent = i), a > o.lineDescent && (o.lineDescent = a);
	let _ = !("text" in t) || t.metricOnly !== !0;
	_ && (o.lineHasVisibleMetrics = !0, i > o.lineVisibleAscent && (o.lineVisibleAscent = i), a > o.lineVisibleDescent && (o.lineVisibleDescent = a));
	let v = 0;
	if (!("isTab" in t) && !("imagePath" in t) && !("math" in t)) {
		let e = t;
		e.ruby && (o.lineHasRuby = !0);
		let n = e.metricEastAsian === !0 || vs.test(e.text);
		!o.lineEastAsian && n && (o.lineEastAsian = !0);
		let r = e.smallCaps && !e.vertAlign ? e.fontSize * p : u(e), i = n && !e.ruby, a = e.resolvedLineHeightRatio == null ? Ef(f, m, e.fontRoute, e.fontFamily, e.bold ? 700 : 400, e.italic ? "italic" : "normal", e.text) : null, s = e.textBoxLineFloor && e.ruby ? 0 : Math.max(nf(e, r, i), e.textBoxLineFloor || e.metricEastAsian === !0 ? rf(e, r, i) : 0);
		_ && !n && !e.ruby && e.resolvedLatinGridCellAllocation === !0 && (o.lineLatinGridCountSingle = Math.max(o.lineLatinGridCountSingle, s));
		let c = Math.max(s, (a ?? 0) * r);
		c > o.lineIntendedSingle && (o.lineIntendedSingle = c), _ && c > o.lineVisibleIntendedSingle && (o.lineVisibleIntendedSingle = c), i && (v = bf(s, r));
	} else "isTab" in t || (v = i + a);
	v > o.lineGridCountSingle && (o.lineGridCountSingle = v);
}
function dp(e, t, n, r) {
	let { breakerState: i, scale: a } = e;
	i.lineMarkerHeight = Math.max(i.lineMarkerHeight, n), i.lineMarkerAscent = Math.max(i.lineMarkerAscent, r), i.linePictureMarkSingle = Math.max(i.linePictureMarkSingle, (t.paragraphMarkSinglePx ?? 0) * a);
}
function fp(e, t) {
	let { measureText: n, verticalInkExtra: r, scale: i, characterGrid: a } = e;
	return dl(t, n(t).width + r(t, t.text), a, i, pp(e, t, t.text)) + Uc(e, t);
}
function pp(e, t, n, r = 0) {
	let { measurement: i, characterGrid: a, reservePrefixWork: o } = e;
	return i.condensedAdvanceUnits(t, n, r, a, o);
}
function mp(e) {
	let t = e.at(-1);
	return t !== void 0 && "text" in t;
}
function hp(e, t) {
	if (t.autoSpaceBeforePt === void 0) return 0;
	let n = Uc(e, t), r = mp(e.breakerState.currentLine) && e.characterGrid?.type !== "snapToChars" ? t.autoSpaceLeadingPx ?? t.autoSpaceBeforePt * e.scale : 0;
	return t.autoSpaceLeadingPx = r, r - n;
}
function gp(e, t, n) {
	let { snapPitchPx: r, eastAsianSnapCellCount: i, characterGrid: a } = e, o = fl(t, a);
	return !o || r == null || t.text.length === 0 ? n : pl(n, o, r, o === "eastAsia" ? i(t) : 1);
}
function _p(e, t) {
	let { segNaturalAdvance: n, standaloneSnapAdvance: r } = e;
	return r(t, n(t));
}
function vp(e, t, n, r = !1) {
	let { measurement: i, effectiveFontPx: a, verticalInkExtra: o, scale: s, characterGrid: c } = e, l = r ? t.text.length - n.length : 0, u = {
		...t,
		text: n,
		punctuationCompressions: qc(t, Math.max(0, l), Math.max(0, l) + n.length)
	}, d = l <= 0 && n.length > 0 ? Uc(e, t) : 0;
	if (t.textLayoutService && t.textShapeRequest) return dl(u, Pc(t.textLayoutService, {
		...ks(t.textShapeRequest, Math.max(0, l), Math.max(0, l) + n.length),
		fontSizePt: a(t),
		measure: !0,
		clusterGeometry: !1
	}).advancePt + o(t, n), c, s, pp(e, t, n, Math.max(0, l))) + d;
	let f = i.measureRunText(t, n).width;
	return dl(u, f + o(t, n), c, s, pp(e, t, n, Math.max(0, l))) + d;
}
function yp(e, t) {
	let { snapPitchPx: n, measurement: r, measureText: i, verticalInkExtra: a, scale: o, characterGrid: s } = e;
	if (n == null) return 1;
	t.textLayoutService && t.textShapeRequest && !t.shapedClusters && i(t, !0);
	let c = t.shapedClusters?.length ? t.shapedClusters : null, l = c == null ? [...new Set([
		0,
		...b(t.text),
		t.text.length
	])].sort((e, t) => e - t) : null, u = c?.map((e) => ({
		start: e.range.start,
		end: e.range.end,
		advancePx: e.advancePt
	})) ?? l.slice(0, -1).map((e, t) => ({
		start: e,
		end: l[t + 1],
		advancePx: void 0
	})), d = 0;
	for (let e of u) {
		let { start: i, end: c } = e;
		if (c <= i) continue;
		let l = t.text.slice(i, c), u = {
			...t,
			text: l,
			textShapeRequest: t.textShapeRequest ? ks(t.textShapeRequest, i, c) : void 0,
			punctuationCompressions: qc(t, i, c)
		}, f;
		if (e.advancePx != null) f = dl(u, e.advancePx + a(t, l), s, o);
		else {
			let e = r.measureRunText(t, l).width;
			f = dl(u, e + a(t, l), s, o);
		}
		d += ur(f, n);
	}
	return Math.max(1, d);
}
function bp(e, t, n, r = !1) {
	let { standaloneSnapAdvance: i, strNaturalAdvance: a } = e, o = r ? t.text.length - n.length : 0;
	return i({
		...t,
		text: n,
		...t.textShapeRequest ? { textShapeRequest: ks(t.textShapeRequest, Math.max(0, o), Math.max(0, o) + n.length) } : {},
		punctuationCompressions: qc(t, Math.max(0, o), Math.max(0, o) + n.length),
		shapedClusters: n === t.text ? t.shapedClusters : void 0
	}, a(t, n, r));
}
function xp(e, t, n) {
	let { breakerState: r, sameLatinSpaceFace: i, availW: a, fitsMeasuredWidth: o, characterGrid: s, baseRtl: c, isJustified: l, widthPolicy: u } = e;
	if (l || c || u !== "bounded" || s?.type === "snapToChars" || s?.type === "linesAndChars" && t.widthBalanceGridDeltaFactor !== .5 || t.latinSpaceCompressionEligible !== !0 || t.latinSpaceAverageWidthRatio == null || !t.fontRoute || t.rtl || t.verticalRun || t.tateChuYoko || t.fitTextRegionIndex !== void 0 || !r.latinLineHomogeneous || !r.latinLineFace || !i(t, r.latinLineFace) || r.latinLineGaps.length === 0) return !1;
	let d = (r.latinUniformGapCapacity ?? 0) * r.latinLineGaps.length;
	if (d <= 0) return !1;
	let f = r.latinAppliedPerGap * r.latinAppliedGapCount, p = Math.max(0, r.currentWidth + f + n - a());
	return p > d || !o(r.currentWidth + f + n - p, a()) ? !1 : (r.currentWidth += f - p, r.latinAppliedGapCount = r.latinLineGaps.length, r.latinAppliedPerGap = p / r.latinAppliedGapCount, !0);
}
function Sp(e) {
	return e.justifiedCompression === !0 && !e.baseRtl && e.widthPolicy === "bounded" && e.characterGrid?.type !== "snapToChars" && e.characterGrid?.type !== "linesAndChars";
}
function Cp(e) {
	let t = e.map((e) => ({ text: "text" in e && !e.metricOnly && e.fitTextRegionIndex === void 0 && e.snapGridClass === void 0 ? e.text : void 0 })), n = be(t, { lastDrawnSi: Infinity }).gaps;
	if (!n.some((e) => e.codePoint === 12288) || Si(e)) return n;
	let r = [], i = /* @__PURE__ */ new Map();
	t.forEach(({ text: t }, n) => {
		if (t === void 0 || "ruby" in e[n] && e[n].ruby) {
			r.push(65532);
			return;
		}
		let a = 0;
		for (let e of t) (!wp.test(e) || r.length === 0) && (i.set(`${n}:${a}`, r.length), r.push(e.codePointAt(0))), a += 1;
	});
	let a = (e) => e === 32 || e === 12288, o = [], s = Array(r.length), c;
	for (let e = 0; e < r.length; e++) o.push(c), a(r[e]) || (c = r[e]);
	c = void 0;
	for (let e = r.length - 1; e >= 0; e--) s[e] = c, a(r[e]) || (c = r[e]);
	return n.filter((e) => {
		if (e.codePoint !== 12288) return !0;
		let t = i.get(`${e.segIndex}:${e.cpOffset}`);
		return t === void 0 ? !0 : Ep(o[t]) || Ep(s[t]);
	});
}
var wp = /^[\p{Grapheme_Extend}\u200d]$/u, Tp = /^[\p{Script=Han}\p{Script=Hiragana}\p{Script=Katakana}\p{Script=Hangul}]$/u;
function Ep(e) {
	return e !== void 0 && e !== 65532 && (C(e) || Tp.test(String.fromCodePoint(e)));
}
function Dp(e, t, n) {
	return n * tl(t) + rl(t, e.characterGrid, e.scale);
}
function Op(e, t) {
	if ("text" in t) {
		if (t.fitTextRegionIndex !== void 0) return {
			widthPx: t.measuredWidth,
			spacePx: 0,
			...Si([t]) ? { rtl: !0 } : {}
		};
		let n, r, i, a = t.text.indexOf(" "), o = a >= 0 && t.text.indexOf(" ", a + 1) < 0, s = t.shapedSpaceClusters ?? t.shapedClusters;
		if (s && !t.ruby) if (o && s.length === 1 && s[0].range.start === a) {
			let n = s[0].advancePt;
			if (n === void 0) throw Error("A text space lacks authoritative cluster geometry");
			i = Dp(e, t, n);
		} else {
			let r = new Map(s.map((e) => [e.range.start, e.advancePt])), a = 0, c = 0;
			for (let s of t.text) {
				if (s === " ") {
					let s = r.get(a);
					if (s === void 0) throw Error("A text space lacks authoritative cluster geometry");
					let l = Dp(e, t, s);
					o ? i = l : (n ??= /* @__PURE__ */ new Map()).set(c, l);
				}
				a += s.length, c += 1;
			}
		}
		if (e.lineEndIdeographicSpaceHangs === !0 && t.text.includes("　") && !t.ruby) {
			let n = [...t.text], i = t.text.length;
			for (let a = n.length - 1; a >= 0 && (n[a] === " " || n[a] === "　"); a--) --i, n[a] === "　" && (r ??= /* @__PURE__ */ new Map()).set(a, e.strAdvance({
				...t,
				text: "　",
				...J(t, i, i + 1)
			}, "　"));
		}
		let c = i ?? n?.values().next().value ?? (a >= 0 && !t.ruby ? e.strAdvance({
			...t,
			text: " ",
			...J(t, a, a + 1)
		}, " ") : 0), l = Uc(e, t);
		return {
			text: t.metricOnly ? "" : t.ruby ? void 0 : t.text,
			widthPx: t.measuredWidth,
			spacePx: c,
			...n ? { spaceWidths: n } : {},
			...r ? { ideographicSpaceWidths: r } : {},
			...l > 0 ? { leadingGapPx: l } : {},
			...Si([t]) ? { rtl: !0 } : {}
		};
	}
	return {
		widthPx: t.measuredWidth,
		spacePx: 0
	};
}
function kp(e, t, n) {
	let { breakerState: r } = e;
	if (!Sp(e) || t.fitTextRegionIndex !== void 0 || r.currentLine.length === 0 || n.length === 0) return;
	(!r.justifiedGapModel || r.justifiedGapModel.segmentCount !== r.currentLine.length) && (r.justifiedGapModel = cf(r.currentLine.map((t) => Op(e, t)), void 0, !1));
	let i = r.justifiedGapModel, a = cf([Op(e, {
		...t,
		...Fc,
		text: n,
		...J(t, 0, n.length),
		measuredWidth: e.strAdvance(t, n)
	})], i, !1), o = a.visibleWidthPx - e.availW();
	if (!(o > 0)) return 0;
	if (e.justifiedCompressionAdmissionOnly !== !0) return Cr({
		overflow: o,
		naturalGapSum: a.S,
		candidateLineEndSeparator: a.lineEndSeparatorPx,
		previousOpportunitySum: i.S + i.lineEndSeparatorPx,
		expansionWithoutCandidate: e.availW() - i.visibleWidthPx
	}) === void 0 ? void 0 : o;
}
function Ap(e, t) {
	let { breakerState: n } = e;
	if (n.currentLine.length === 0 || n.justifiedGapModel !== void 0 || n.justifiedCompressionPx > 0 || n.latinLineGaps.length > 0 || n.mixedSpace.compressed) return;
	let r = 0, i = 0, a = 0;
	for (let o = 0; o <= n.currentLine.length; o += 1) {
		let s = o === n.currentLine.length ? t : n.currentLine[o];
		if (!("text" in s) || s.text.length === 0 || s.text === " " || s.metricOnly || s.ruby || s.verticalRun || s.tateChuYoko || s.fitTextRegionIndex !== void 0 || s.fitTextPerGapPx !== void 0 || s.snapGridClass !== void 0 || s.autoSpaceBeforePt !== void 0 || s.autoSpaceLeadingPx !== void 0 || s.autoSpaceCompressible || s.optionalHyphen || s.optionalHyphenWord || s.optionalHyphenGlyph || s.optionalHyphenBreaks !== void 0 || s.explicitBreaks !== void 0 || s.latinSpaceCompressionEligible || s.latinSpaceCompressionPx !== void 0 || s.latinNaturalTrailingSpacePx !== void 0 || s.mixedSpaceAverageWidthRatio !== void 0 || s.mixedNaturalTrailingSpacePx !== void 0 || s.punctuationCompressions !== void 0 || s.widthBalanceGridDeltaFactor !== void 0 || s.widthBalanceSpaceSequence || s.widthBalanceSpaceAdjustmentPt !== void 0 || il(s, e.characterGrid, e.scale) || s.text.includes("　") || !Number.isFinite(s.measuredWidth) || s.measuredWidth < 0) return;
		let c = s.text.indexOf(" ");
		if (c >= 0 && c !== s.text.length - 1 || (r += s.measuredWidth, !Number.isFinite(r))) return;
		if (c < 0) continue;
		let l = s.shapedSpaceClusters ?? s.shapedClusters, u = l?.[0];
		if (l?.length !== 1 || u?.range.start !== c || u.range.end !== c + 1 || u.advancePt === void 0) return;
		let d = Dp(e, s, u.advancePt);
		if (!Number.isFinite(d) || d < 0 || (i += d, !Number.isFinite(i))) return;
		o === n.currentLine.length && (a += d);
	}
	let o = r - a - e.availW();
	return Number.isFinite(o) && o > 0 && Sr(o, i) ? o : void 0;
}
function jp(e, t, n) {
	if (!Sp(e) || t.fitTextRegionIndex !== void 0) return !1;
	let { breakerState: r } = e;
	if (r.justifiedUnitEnd) return r.justifiedUnitEnd === t && (r.justifiedUnitEnd = void 0), !1;
	let i = df(t, r.queue);
	if (i.some((e) => !("text" in e))) return !1;
	if (e.justifiedCompressionAdmissionOnly === !0 && i.some((e) => "text" in e && tc(e.text))) return i.length > 1 && (r.justifiedUnitEnd = i.at(-1)), !1;
	let a = r.currentLine.at(-1), o = [], s = i.map((t, r) => {
		if (!("text" in t)) throw Error("A text candidate lost its placement unit");
		let i = r === 0 && e.justifiedCompressionAdmissionOnly === !0 && n, s = i || e.textSegmentBox(t);
		i && (t.leadingWordBoundaryPx = void 0, t.snapGridNaturalWidthPx = s.width);
		let c = Mp(e, a && "text" in a ? a : void 0, t, s.width);
		return o.push(c), t.measuredWidth = s.width + c, a = t, s;
	});
	if (e.justifiedCompressionAdmissionOnly === !0) for (let t of [r.currentLine, i]) for (let n of t) "text" in n && n.text.includes(" ") && !n.ruby && !n.metricOnly && n.textLayoutService && n.textShapeRequest && (n.shapedSpaceClusters = e.measurement.acquireCompressionSpaceClusters(n));
	let c = e.justifiedCompressionAdmissionOnly === !0 && i.length === 1 ? Ap(e, t) : void 0, l = c ?? 0, u;
	if (c === void 0) {
		(!r.justifiedGapModel || r.justifiedGapModel.segmentCount !== r.currentLine.length) && (r.justifiedGapModel = cf(r.currentLine.map((t) => Op(e, t)), void 0, !1));
		let t = r.justifiedGapModel, n = cf(i.map((t) => Op(e, t)), t, !1);
		l = n.visibleWidthPx - e.availW(), u = l > 0 ? Cr({
			overflow: l,
			naturalGapSum: n.S,
			candidateLineEndSeparator: n.lineEndSeparatorPx,
			previousOpportunitySum: t.S + t.lineEndSeparatorPx,
			expansionWithoutCandidate: e.availW() - t.visibleWidthPx
		}) : 0;
	}
	if (u === void 0) {
		for (let [e, t] of i.entries()) t.measuredWidth = s[e].width;
		return o.some((e) => e !== 0) && r.currentLine.length > 0 ? (e.flush(void 0, !1, t.src), r.queue.unshift(t), !0) : (i.length > 1 && (r.justifiedUnitEnd = i.at(-1)), !1);
	}
	for (let [n, a] of i.entries()) {
		if (a !== t && r.queue.shift(), !("text" in a)) throw Error("A text candidate lost its placement unit");
		let i = s[n];
		a.leadingWordBoundaryPx = o[n], e.addToLine(a, a.measuredWidth, i.height, i.ascent, i.descent);
	}
	return r.justifiedCompressionPx = Math.max(0, l), !0;
}
function Mp(e, t, n, r) {
	if (!t || !("text" in t)) return 0;
	if (e.widthPolicy === "intrinsic" && (t.semanticSlotSpans || n.semanticSlotSpans)) return e.measurement.wordBoundaryAdvance(t, n);
	if (t.textShapeRequest?.kerning !== !0 || !t.text || !n.text || t.text.endsWith(" ") === n.text.startsWith(" ")) return 0;
	let { characterGrid: i, scale: a } = e;
	if (fl(n, i) || fl(t, i)) return 0;
	let o = e.measurement.kernedSpaceSeamAdvance(t, n);
	if (o === 0) return 0;
	if (il(t, i, a)) {
		let n = e.measurement.condensedAdvanceUnits(t, t.text, 0, i, e.reservePrefixWork), r = n ? sl(t, i, a, n).at(-1) : void 0;
		r !== void 0 && (o = Math.max(0, r + o) - Math.max(0, r));
	}
	return Math.max(o, -Math.max(0, r));
}
function Np(e, t, n) {
	return Mp(e, e.breakerState.currentLine.at(-1), t, n);
}
function Pp(e, t) {
	let { measurement: n, effectiveFontPx: r, measureText: i, verticalInkExtra: a, ctx: o, scale: s, fontFamilyClasses: c, characterGrid: l } = e;
	t.leadingWordBoundaryPx = void 0;
	let u = Sp(e) && t.text.includes(" ") && !t.ruby && (!e.justifiedCompressionAdmissionOnly || t.metricOnly) ? n.measureSegment(t, "spaces") : i(t, fl(t, l) === "eastAsia"), d = dl(t, u.width + a(t, t.text), l, s, pp(e, t, t.text)) + Uc(e, t);
	t.snapGridNaturalWidthPx = d;
	let f = t.fontSize * s, p = u, m = r(t);
	if (t.metricOnly && t.metricProbeText) {
		let e = t.smallCaps && !t.vertAlign ? f : m, r = t.textLayoutService && t.textShapeRequest ? t.textLayoutService.shape({
			...As(t.textShapeRequest, t.metricProbeText),
			fontSizePt: e,
			measure: !0,
			clusterGeometry: !1
		}) : void 0, i = r ? void 0 : n.measureWithFont(tf(t.bold, t.italic, e, t.fontFamily, c, t.fontRoute), t.metricProbeText);
		p = {
			width: u.width,
			actualBoundingBoxAscent: r ? r.ascentPt : i.actualBoundingBoxAscent,
			actualBoundingBoxDescent: r ? r.descentPt : i.actualBoundingBoxDescent,
			fontBoundingBoxAscent: r ? r.ascentPt : i.fontBoundingBoxAscent,
			fontBoundingBoxDescent: r ? r.descentPt : i.fontBoundingBoxDescent
		}, m = e;
	} else if (t.smallCaps && !t.vertAlign && m !== f) {
		if (t.textLayoutService && t.textShapeRequest) {
			let e = t.textLayoutService.shape({
				...t.text ? t.textShapeRequest : As(t.textShapeRequest, "X"),
				fontSizePt: f,
				measure: !0,
				clusterGeometry: !1
			});
			p = {
				width: e.advancePt,
				actualBoundingBoxAscent: e.ascentPt,
				actualBoundingBoxDescent: e.descentPt,
				fontBoundingBoxAscent: e.ascentPt,
				fontBoundingBoxDescent: e.descentPt
			};
		} else p = n.measureWithFont(tf(t.bold, t.italic, f, t.fontFamily, c, t.fontRoute), t.text || "X");
		m = f;
	}
	let h = Cf(p, f), g = (!t.ruby || t.ruby.hpsRaisePt != null) && (t.resolvedResourceVerticalMetric || t.referenceFontVerticalMetric) && (t.position ?? 0) === 0 && t.resolvedDesignAscentRatio != null && t.resolvedDesignDescentRatio != null, _ = g ? t.resolvedDesignAscentRatio * m : h.ascent, v = g ? t.resolvedDesignDescentRatio * m : h.descent;
	if (t.positionExtendsLineBox !== !1) {
		let e = (t.position ?? 0) * s;
		e > 0 ? _ += e : e < 0 && (v -= e);
	}
	if (t.ruby && (!t.textBoxLineFloor || t.textBoxVertical)) {
		let e = Af(t.ruby.fontSizePt, t.ruby.hpsRaisePt, s, t, o, c);
		_ = t.ruby.hpsRaisePt == null ? _ + e : Math.max(_, e + t.ruby.fontSizePt * s);
	}
	return {
		width: d,
		height: t.fontSize,
		ascent: _,
		descent: v
	};
}
function Fp(e, t) {
	let { breakerState: n, addToLine: r, textSegmentBox: i } = e;
	if (/\s$/u.test(t.text) || t.ruby !== void 0 || t.tateChuYoko === !0 || t.fitTextRegionIndex !== void 0) return;
	let a = n.queue.peek();
	if (!a || !("text" in a) || a.joinPrev !== !0 || a.text.length === 0 || [...a.text].some((e) => e !== "　")) return;
	n.queue.shift();
	let o = Nr(Ql(t.text), a.paragraphFinalIdeographicSpaceCount ?? [...a.text].length);
	if (o === 0) {
		n.queue.unshift(a);
		return;
	}
	let s = a.text.slice(0, o), c = {
		...a,
		...Fc,
		text: s,
		measuredWidth: 0,
		...J(a, 0, s.length)
	}, l = i(c);
	c.measuredWidth = l.width, r(c, l.width, l.height, l.ascent, l.descent);
	let u = a.text.slice(s.length);
	u.length > 0 && n.queue.unshift({
		...a,
		...Fc,
		text: u,
		measuredWidth: 0,
		joinPrev: void 0,
		hardJoinPrev: void 0,
		...J(a, s.length, a.text.length),
		src: a.src ? Oc(a.src, s.length) : void 0
	});
}
function Ip(e, t) {
	let { segAdvance: n, scale: r } = e;
	return "isTab" in t ? t.measuredWidth || 0 : "imagePath" in t ? t.widthPt * r : "math" in t ? t.measuredWidth || 0 : "lineBreak" in t ? 0 : n(t);
}
function Lp(e) {
	for (let t = 0; t < e.length; t += 1) {
		let n = e[t];
		if (!("text" in n)) continue;
		let r = n.text.indexOf(".");
		if (r >= 0) return {
			segmentIndex: t,
			charOffset: r
		};
	}
	let t = null, n = !1;
	for (let r = 0; r < e.length; r += 1) {
		let i = e[r];
		if (!("text" in i)) {
			if (n) return t;
			continue;
		}
		let a = 0;
		for (let e of i.text) if (a += e.length, /\p{Decimal_Number}/u.test(e)) n = !0, t = {
			segmentIndex: r,
			charOffset: a
		};
		else if (n) return t;
	}
	return t;
}
function Rp(e, t) {
	let { strAdvance: n, tabFollowWidth: r, decimalAlignmentPoint: i } = e, a = i(t);
	if (!a) return;
	let o = 0;
	for (let n = 0; n < a.segmentIndex; n += 1) o += zp(e, t, n);
	let s = t[a.segmentIndex];
	if (!("text" in s)) return o;
	let c = n(s, s.text.slice(0, a.charOffset));
	return o + c + Mp(e, t[a.segmentIndex - 1], s, r(s));
}
function zp(e, t, n) {
	let r = t[n], i = e.tabFollowWidth(r);
	return "text" in r ? i + Mp(e, t[n - 1], r, i) : i;
}
function Bp(e, t) {
	let { breakerState: n, decimalAlignmentPrefixWidth: r } = e, i = [], a = 0, o = t ? [] : void 0, s = !1;
	for (let t of n.queue) {
		if ("isTab" in t || "lineBreak" in t) {
			s = "lineBreak" in t;
			break;
		}
		i.push(t);
		let n = zp(e, i, i.length - 1);
		a += n, o?.push(n);
	}
	let c = r(i);
	if (c === void 0) return { totalWidth: a };
	if (!o) return {
		totalWidth: a,
		decimalPrefixWidth: c
	};
	let l = e.decimalAlignmentPoint(i);
	if (!l) return {
		totalWidth: a,
		decimalPrefixWidth: c
	};
	let u = i[l.segmentIndex];
	if (!("text" in u) || u.text[l.charOffset] !== ".") return {
		totalWidth: a,
		decimalPrefixWidth: c
	};
	let d = e.strAdvance(u, u.text.slice(0, l.charOffset)) + Mp(e, i[l.segmentIndex - 1], u, e.tabFollowWidth(u)), f = n.currentLine, p = f.length + 1, m = [
		...f,
		t,
		...i
	], h = us({
		segments: m,
		point: {
			...l,
			segmentIndex: p + l.segmentIndex
		},
		cellStart: p,
		cellEnd: m.length,
		resolveOrder: e.passContext.decimalOrder,
		advances: [
			...f.map((e) => e.measuredWidth),
			0,
			...o
		],
		selectedPrefixAdvance: d,
		model: Sc({
			baseRtl: e.baseRtl,
			bidiOrdering: e.bidiOrdering,
			isJustified: e.isJustified,
			stretchLastLine: e.stretchLastLine,
			endsWithBreak: s
		})
	});
	return {
		totalWidth: a,
		decimalPrefixWidth: c,
		...h === void 0 ? {} : { physicalDecimalOffset: h }
	};
}
function Vp(e, t) {
	if (!e || !t(0)) return -1;
	let n = 0, r = 1;
	for (; r < e && t(r);) n = r, r = r * 2 + 1;
	for (r = Math.min(r, e); n + 1 < r;) {
		let e = Math.floor((n + r) / 2);
		t(e) ? n = e : r = e;
	}
	return n;
}
function Hp(e, t, n, r = !0) {
	let { prospectiveSnapAdvance: i, measurement: a, effectiveFontPx: o, setMeasureFont: s, strNaturalAdvance: c, strAdvance: l, ctx: u, scale: d, fontFamilyClasses: f, characterGrid: p, verticalGlyphMeasurement: m } = e;
	e.reservePrefixWork(t.text.length);
	let h = Yc(t), g = [...new Set([
		0,
		...b(t.text),
		t.text.length
	])], _ = 0;
	if (n > 0) if (Bc(t, d) >= 0 && fl(t, p) !== "latin") s(tf(t.bold, t.italic, o(t), t.fontFamily, f, t.fontRoute)), a.withSegmentKerning(t, () => {
		let r = tu(u, t.text, n, zc(t, p, d), tl(t), Bc(t, d), t.verticalRun === !0, m, (n) => (e.reservePrefixWork(n.length), l(t, n))).length;
		_ = g.filter((e) => e <= r && !h.has(e)).at(-1) ?? 0;
	});
	else if (Bc(t, d) >= 0) {
		let r = g.filter((e) => e > 0 && !h.has(e)), a = Vp(r.length, (a) => (e.reservePrefixWork(r[a]), eu(i(t, c(t, t.text.slice(0, r[a]))), n)));
		a >= 0 && (_ = r[a]);
	} else for (let r of g) r <= 0 || h.has(r) || (e.reservePrefixWork(r), eu(i(t, c(t, t.text.slice(0, r))), n) && (_ = r));
	for (_ <= 0 && r && (_ = g.find((e) => e > 0 && !h.has(e)) ?? t.text.length); t.text.startsWith("　", _);) _ += 1;
	return _;
}
function Up(e, t, n) {
	let { prospectiveSnapAdvance: r, strNaturalAdvance: i, scale: a } = e, o = t.explicitBreaks;
	if (!(n > 0) || !o) return 0;
	let s = o.end - o.start, c = (a) => {
		let s = fc(o, a);
		return e.reservePrefixWork(s), eu(r(t, i(t, t.text.slice(0, s))), n);
	};
	if (Bc(t, a) < 0) {
		let e = 0;
		for (let t = 0; t < s; t++) c(t) && (e = fc(o, t));
		return e;
	}
	let l = Vp(s, c);
	return l < 0 ? 0 : fc(o, l);
}
function Wp(e, t, n) {
	let { breakerState: r } = e;
	r.queue.unshift({
		...t,
		...Fc,
		text: t.text.slice(n),
		...J(t, n, t.text.length),
		seaBreaks: ac(t.seaBreaks, n),
		measuredWidth: 0,
		joinPrev: void 0,
		hardJoinPrev: void 0,
		src: Oc(t.src, n)
	});
}
function Gp(e, t) {
	let { breakerState: n, materializeLatinSpaceCompression: r, strAdvance: i, lineEdgeRules: a } = e;
	return jf(n, a, r, i, t, e.scale);
}
function Kp(e, t, n, r, i) {
	let { breakerState: a, addToLine: o, strNaturalAdvance: s, queueEmergencyTail: c } = e;
	return Mf(a, s, o, c, t, n, r, i);
}
function qp(e, t, n, r, i) {
	let a = t < e.text.length, o = a ? e.text.codePointAt(t) : n?.text.codePointAt(0);
	return r && o !== void 0 && !/^\s/u.test(String.fromCodePoint(o)) && !e.hardJoinPrev && (a || !n?.hardJoinPrev) && e.fitTextRegionIndex === void 0 && (!i.enabled || !i.lineStartForbidden.has(o));
}
function Jp(e, t) {
	if (!t.optionalHyphenWord || t.joinPrev && e.breakerState.currentLine.length > 0) return !1;
	e.reservePrefixWork(t.text.length + 1);
	let n = [t];
	for (let t of e.breakerState.queue) {
		if (!("text" in t) || !t.joinPrev) break;
		e.reservePrefixWork(t.text.length + 1), n.push(t);
	}
	let r = e.breakerState.currentWidth, i = e.breakerState.currentLine.at(-1), a, o = !1;
	for (let [t, s] of n.entries()) {
		let c = s.optionalHyphen ? [{
			offset: 0,
			glyph: s.optionalHyphen
		}] : s.optionalHyphenBreaks ?? [];
		s.optionalHyphen || (r += Mp(e, i, s, e.segAdvance(s)), i = s);
		for (let i of c) {
			e.reservePrefixWork(i.offset + 1);
			let c = s.text.slice(0, i.offset), l = n[t + 1];
			if (!qp(s, i.offset, l, o || c.trim().length > 0, e.lineEdgeRules)) continue;
			let u = {
				...i.glyph,
				...Fc,
				src: s.src ? {
					...s.src,
					charOffset: s.src.charOffset + i.offset
				} : void 0,
				optionalHyphenGlyph: !0,
				joinPrev: !0
			}, d = i.offset > 0 ? e.strAdvance(s, c) : 0;
			e.fitsMeasuredWidth(r + d + e.segAdvance(u), e.availW()) && (a = {
				index: t,
				offset: i.offset,
				glyph: u
			});
		}
		s.optionalHyphen || (r += e.segAdvance(s), o ||= s.text.trim().length > 0);
	}
	if (!ff(e)) {
		let t = mf(n.filter((e) => !e.optionalHyphen), e);
		t > 0 && !(e.baseRtl && e.fitsMeasuredWidth(r - t, e.availW()) && !e.fitsMeasuredWidth(r, e.availW()) && Yp(e, n.filter((e) => !e.optionalHyphen))) && (r -= t);
	}
	if (e.fitsMeasuredWidth(r, e.availW()) || n.every((n) => n.optionalHyphen || e.sameLatinSpaceFace(n, t)) && e.fitHomogeneousLatinSpaces(t, r - e.breakerState.currentWidth)) return !1;
	if (!a) return e.breakerState.currentLine.length > 0 && !t.joinPrev ? (e.flush(void 0, !1, t.src), e.breakerState.queue.unshift(t), !0) : !1;
	for (let t = 0; t <= a.index; t += 1) {
		t > 0 && e.breakerState.queue.shift();
		let r = n[t], i = r;
		if (t === a.index) {
			e.reservePrefixWork(r.text.length);
			let t = r.text.slice(a.offset);
			if (t && e.breakerState.queue.unshift({
				...r,
				...Fc,
				text: t,
				measuredWidth: 0,
				joinPrev: void 0,
				hardJoinPrev: void 0,
				...J(r, a.offset, r.text.length),
				src: r.src ? {
					...r.src,
					charOffset: r.src.charOffset + a.offset
				} : void 0
			}), a.offset === 0) continue;
			i = {
				...r,
				...Fc,
				text: r.text.slice(0, a.offset),
				measuredWidth: 0,
				...J(r, 0, a.offset)
			};
		}
		if (i.optionalHyphen) {
			e.addToLine(i, 0, 0, 0, 0);
			continue;
		}
		let o = e.textSegmentBox(i);
		i.measuredWidth = o.width, e.addToLine(i, o.width, o.height, o.ascent, o.descent);
	}
	let s = e.breakerState.queue.peek();
	s && "text" in s && (s.joinPrev || s.hardJoinPrev) && (e.breakerState.queue.shift(), e.breakerState.queue.unshift({
		...s,
		joinPrev: void 0,
		hardJoinPrev: void 0
	}));
	let c = e.textSegmentBox(a.glyph);
	return a.glyph.measuredWidth = c.width, e.addToLine(a.glyph, c.width, c.height, c.ascent, c.descent), e.flush(void 0, !1, e.breakerState.queue.peek()?.src), !0;
}
function Yp(e, t) {
	if (!e.baseRtl || t.length === 0 || e.isJustified || !e.breakerState.currentLine.some((e) => "isTab" in e)) return !1;
	let n = t.at(-1);
	if (!("text" in n) || n.text.trim() === "") return !1;
	let r = [...e.breakerState.currentLine, ...t];
	return !pf(Ei(r, !0, Sc({
		baseRtl: !0,
		bidiOrdering: e.bidiOrdering,
		isJustified: e.isJustified,
		stretchLastLine: e.stretchLastLine
	})), r.length - 1);
}
function Xp(e, t) {
	return e !== void 0 && e.segIndex === t.segIndex && e.charOffset === t.charOffset;
}
function Zp(e) {
	let t = e.length - 1;
	for (; t > 0;) {
		let n = e[t];
		if (!("text" in n) || !n.joinPrev) break;
		--t;
	}
	return Math.max(0, t);
}
function Qp(e, t, n) {
	let { breakerState: r, strAdvance: i, availW: a, fitsMeasuredWidth: o } = e, s = (ff(e) ? n : n.replace(/ +$/u, "")).replace(/\u3000+$/u, "");
	return !o($p(e, s) + i(t, s), a());
}
function $p(e, t) {
	let { breakerState: n } = e;
	return t !== "" || ff(e) ? n.currentWidth : n.currentWidth - gf(n.currentLine, e);
}
function em(e, t) {
	let n = 0;
	for (let r = t; r < e.length; r += 1) n += e[r].measuredWidth ?? 0;
	return n;
}
function tm(e, t) {
	let { breakerState: n, flush: r } = e, i = Tc();
	for (; n.queue.length > 0;) {
		let a = n.gapTransaction;
		if (a?.narrowed) {
			let e = n.queue.peek();
			if (a.stopBefore && n.currentLine.length > 0 && Xp(e.src, a.stopBefore)) {
				r(void 0, !1, e.src);
				continue;
			}
			n.currentLine.length === 0 && t?.captureGapSnapshot();
		}
		let o = n.queue.shift();
		n.inHand = o;
		try {
			nm(e, o, i);
		} catch (e) {
			if (!(e instanceof Ff) || !t) throw e;
			t.rejectGap(e);
		}
		n.inHand = void 0;
	}
}
function nm(e, t, n) {
	let { breakerState: r, flush: i } = e;
	if ("lineBreak" in t) {
		i(t.fontSize, !0), r.trailingBreakFontSize = t.fontSize;
		return;
	}
	if (r.trailingBreakFontSize = null, "isTab" in t) {
		gm(e, t, n);
		return;
	}
	if ("imagePath" in t) {
		am(e, t);
		return;
	}
	if ("math" in t) {
		im(e, t);
		return;
	}
	if ("text" in t) {
		if (t.fitTextRegionIndex !== void 0 && Jp(e, t)) return;
		if (t.optionalHyphen) {
			e.addToLine(t, 0, 0, 0, 0);
			return;
		}
	}
	rm(e, t);
}
function rm(e, t) {
	let { breakerState: n, flush: r, addToLine: i, characterGrid: a, availW: o, textSegmentBox: s, prospectiveSnapAdvance: c, segAdvance: l, strAdvance: u, overflowPunct: d, sameLatinSpaceFace: f } = e, p = t;
	p.autoSpaceBeforePt !== void 0 && (p.autoSpaceLeadingPx = mp(n.currentLine) ? void 0 : 0);
	let m = s(p), h = Np(e, p, m.width);
	p.leadingWordBoundaryPx = h === 0 ? void 0 : h;
	let g = m.width + h, _ = c(p, g), v = m.height, y = m.ascent, b = m.descent, x = p.paragraphFinalIdeographicSpaceTail === !0, C = p.paragraphFinalIdeographicSpaceCount ?? 0, w = p.paragraphFinalIdeographicSpaceLocalCount ?? 0, T = x ? p.text.slice(0, Math.max(0, p.text.length - w)) : p.text;
	if (x && C > 1 && T.length > 0) {
		let e = {
			...p,
			...Fc,
			text: T,
			paragraphFinalIdeographicSpaceTail: void 0,
			paragraphFinalIdeographicSpaceLocalCount: void 0,
			paragraphFinalIdeographicSpaceCount: void 0,
			paragraphFinalIdeographicSpaceTailStart: void 0,
			measuredWidth: 0,
			...J(p, 0, T.length)
		}, t = {
			...p,
			...Fc,
			text: p.text.slice(T.length),
			paragraphFinalIdeographicSpaceLocalCount: w,
			joinPrev: void 0,
			hardJoinPrev: void 0,
			paragraphFinalIdeographicSpaceTailStart: !0,
			measuredWidth: 0,
			...J(p, T.length, p.text.length),
			src: p.src ? Oc(p.src, T.length) : void 0
		};
		n.queue.unshift(t), n.queue.unshift(e);
		return;
	}
	if (x && /^\u3000+$/u.test(p.text) && p.paragraphFinalIdeographicSpaceTailStart === !0 && n.currentLine.some((e) => "text" in e && /[^\u3000]/u.test(e.text))) {
		let e = g;
		for (let t of n.queue) {
			if (!("text" in t) || t.paragraphFinalIdeographicSpaceTail !== !0) break;
			e += l(t);
		}
		if (!eu(n.currentWidth + e, o())) {
			r(void 0, !1, p.src), n.queue.unshift(p);
			return;
		}
	}
	if (p.fitTextRegionIndex !== void 0) {
		if (p.fitTextRegionStart) {
			let t = _f(p, n.queue, e);
			n.currentLine.length > 0 && !eu(n.currentWidth + t, o()) && r(void 0, !1, p.src), n.currentLine.length === 0 && !e.fitsMeasuredWidth(t, o()) && e.forcedPlacement(t);
		}
		p.measuredWidth = g, i(p, g, v, y, b);
		return;
	}
	let E = p.text.replace(/ +$/, ""), D = fl(p, a) ? 0 : p.text.endsWith(" ") ? g - (E ? h : 0) - u(p, E) : 0;
	p.latinNaturalTrailingSpacePx = D > 0 && p.latinSpaceCompressionEligible === !0 && /^[^ ]+ $/u.test(p.text) ? D : void 0, p.latinSpaceCompressionPx = void 0;
	let O = p.mixedSpaceAverageWidthRatio !== void 0 && D > 0 && !E.includes(" ") && (E.length > 0 || jl(n));
	p.mixedNaturalTrailingSpacePx = O ? D : void 0, p.mixedNaturalTrailingSpaceCount = O ? p.text.length - E.length : void 0;
	let k = (t, r, i, a) => {
		let s = br(t, r, ff(e)), c = km(e, a ? a.at(-1).segment : p, i);
		return c === void 0 ? s === t || !e.baseRtl || e.fitsMeasuredWidth(n.currentWidth + t, o()) || !e.fitsMeasuredWidth(n.currentWidth + s, o()) ? s : Yp(e, a ? a.map((e) => e.segment) : [p]) ? t : s : t + c;
	}, A = k(_, D, n.queue.peek()), j = p.seaBreaks !== void 0 && S(p.text);
	p.measuredWidth = g;
	let M = !bm(e, p) || p.autoSpaceBeforePt !== void 0, N = M && e.justifiedCompressionAdmissionOnly === !0 && Sp(e) && n.justifiedUnitEnd === void 0 && !(n.justifiedCompressionPx > 0) && !p.optionalHyphenWord && p.explicitBreaks === void 0 && e.fitsMeasuredWidth(n.currentWidth + A, o()) && uf(p, n.queue.peek());
	if (M && !N && jp(e, p, e.justifiedCompressionAdmissionOnly === !0 ? m : void 0) || (p.leadingWordBoundaryPx = h === 0 ? void 0 : h, p.measuredWidth = g, Jp(e, p))) return;
	let P = n.currentLine.at(-1);
	if (Tm(e, {
		s: p,
		w: g,
		trailingSpaceW: D,
		sDictSea: j,
		fitWidthFor: k
	})) return;
	if (h !== 0 && n.currentLine.at(-1) !== P) {
		p.leadingWordBoundaryPx = void 0, n.queue.unshift(p);
		return;
	}
	let F = [...E], I = F.at(-1), L = F.slice(0, -1).join(""), R = d && n.gapTransaction?.endsAtExclusion !== !0 && I !== void 0 && (n.currentLine.length > 0 || L.length > 0) && Wr(I, p.eastAsiaLanguage, p.overflowPunctuationEastAsianRun === !0, p.script === "ascii" || p.script === "highAnsi", p.script === "complexScript", p.overflowPunctuationBidiLanguage) && !Hr(e.cjkClosingMarkHang, I, () => E.length < p.text.length ? String.fromCodePoint(p.text.codePointAt(E.length)) : _m(e), e.kinsoku, p.verticalRun === !0) && eu(n.currentWidth + h + u(p, L), o());
	if (n.mixedSpace.compressed && Nl(n, p.text, p) && e.mixedSpaceRequirement(vm(e, p, p.text, A)) !== void 0) {
		p.measuredWidth = g, i(p, g, v, y, b), e.appendQueuedIdeographicSpaceSegment(p);
		return;
	}
	if (n.latinAppliedPerGap > 0 && (!n.latinLineHomogeneous || !n.latinLineFace || !f(p, n.latinLineFace))) {
		r(void 0, !1, p.src), n.queue.unshift(p);
		return;
	}
	wm(e, {
		s: p,
		w: g,
		h: v,
		asc: y,
		desc: b,
		wForFit: A,
		paragraphFinalIdeographicSpaceTail: x,
		admitsTrailingOverflowPunctuation: R
	});
}
function im(e, t) {
	let { breakerState: n, flush: r, addToLine: i, scale: a, availW: o, setMeasureFont: s, fontFamilyClasses: c, measurement: l } = e, u = t.mathMetadata;
	if (!u || u.available === !1) {
		let u = t.fontSize * a;
		s(tf(!1, !1, u, null, c));
		let d = l.measureCurrentText(t.fallbackText), f = d.width, p = d.fontBoundingBoxAscent ?? d.actualBoundingBoxAscent ?? u * .8, m = d.fontBoundingBoxDescent ?? d.actualBoundingBoxDescent ?? u * .2;
		t.measuredWidth = f, t.mathAscent = p, t.mathDescent = m, n.currentLine.length > 0 && !eu(n.currentWidth + f, o()) && r(void 0, !1, t.src), n.currentLine.length === 0 && !eu(f, o()) && e.forcedPlacement(f), i(t, f, t.fontSize, Math.max(p, u * _e), Math.max(m, u * ge));
		return;
	}
	let d = t.fontSize * a, f = u.widthEm * d, p = u.ascentEm * d, m = u.descentEm * d;
	t.measuredWidth = f, t.mathAscent = p, t.mathDescent = m;
	let h = Math.max(p, d * _e), g = Math.max(m, d * ge);
	n.currentLine.length > 0 && !eu(n.currentWidth + f, o()) && r(void 0, !1, t.src), n.currentLine.length === 0 && !eu(f, o()) && e.forcedPlacement(f), i(t, f, t.fontSize, h, g);
}
function am(e, t) {
	let { breakerState: n, flush: r, addToLine: i, scale: a, availW: o } = e;
	if (t.anchor) {
		t.measuredWidth = 0;
		return;
	}
	if (t.markerMetric) {
		t.measuredWidth = 0, e.admitLineMetric(t, t.heightPt, t.heightPt * a);
		return;
	}
	if (t.listLabel !== void 0) {
		let e = 2 * _s, r = (t.widthPt + e) * a, o = (t.heightPt + e) * a;
		t.measuredWidth = r, i(t, r, t.heightPt + e, 0, Math.max(0, o - n.lineAscent));
		return;
	}
	let s = t.widthPt * a, c = t.heightPt, l = t.heightPt * a;
	t.measuredWidth = s, n.currentLine.length > 0 && !eu(n.currentWidth + s, o()) && r(void 0, !1, t.src), n.currentLine.length === 0 && !eu(s, o()) && e.forcedPlacement(s), i(t, s, c, l, 0);
}
function om(e) {
	let { breakerState: t, scale: n, addToLine: r, measureText: i, verticalInkExtra: a, characterGrid: o, measurement: s } = e;
	for (; t.queue.length > 0;) {
		let c = t.queue.peek();
		if ("isTab" in c || "lineBreak" in c) break;
		if (t.queue.shift(), "imagePath" in c) {
			let e = c.widthPt * n;
			c.measuredWidth = e, r(c, e, c.heightPt, c.heightPt * n, 0);
		} else if ("math" in c) r(c, c.measuredWidth || 0, c.fontSize, c.mathAscent || 0, c.mathDescent || 0);
		else {
			let t = i(c), l = dl(c, t.width + a(c, c.text), o, n, s.condensedAdvanceUnits(c, c.text, 0, o, e.reservePrefixWork)) + Uc(e, c);
			c.measuredWidth = l;
			let u = t.fontBoundingBoxAscent ?? t.actualBoundingBoxAscent ?? c.fontSize * n * .8, d = t.fontBoundingBoxDescent ?? t.actualBoundingBoxDescent ?? c.fontSize * n * .2;
			r(c, l, c.fontSize, u, d);
		}
	}
}
function sm(e) {
	return lm(e) + e.breakerState.lineMarginExtension;
}
function cm(e, t) {
	if (e.ptab) return e.ptab.alignment !== "left";
	let n = t();
	return n != null && yc(n.alignment) !== "leading";
}
function lm(e) {
	let { breakerState: t, firstIndent: n, widthPolicy: r } = e;
	return r === "bounded" ? t.lineMaxWidth - (t.isFirst ? n : 0) : Infinity;
}
function um(e, t) {
	let { breakerState: n } = e;
	if (n.currentLine.length === 0 || e.widthPolicy !== "bounded" || dm(e)) return !1;
	let [r, i] = n.queue.peekPair();
	return gc(r, i, e.characterGrid?.type === "snapToChars", e.baseRtl) ? !e.fitsMeasuredWidth(n.currentWidth + t + e.minimalLegalTextWidth(r), e.availW()) : !1;
}
function dm(e) {
	let { breakerState: t, maxWidth: n } = e;
	return t.lineXOffset !== 0 || t.lineMaxWidth !== n || t.gapTransaction?.narrowed === !0;
}
function fm(e) {
	for (let t of e.breakerState.queue) {
		if ("isTab" in t || "lineBreak" in t) return !1;
		if ("text" in t && t.text.includes(".")) return !0;
	}
	return !1;
}
function pm(e) {
	for (let t of e.breakerState.queue) {
		if ("isTab" in t) return !0;
		if ("lineBreak" in t) return !1;
	}
	return !1;
}
var mm = /* @__PURE__ */ new WeakMap();
function hm(e) {
	let { breakerState: t, scale: n } = e, r = mm.get(t);
	r || mm.set(t, r = /* @__PURE__ */ new WeakMap());
	let i = [], a = 0;
	for (let o of t.queue) {
		let t = r.get(o);
		if (t !== void 0) {
			a = t;
			break;
		}
		if ("lineBreak" in o) break;
		i.push([o, "text" in o ? e.segAdvance(o) : "math" in o ? o.measuredWidth : "imagePath" in o && !o.anchor ? o.widthPt * n : 0]);
	}
	for (let e = i.length - 1; e >= 0; --e) a += i[e][1], r.set(i[e][0], a);
	return a;
}
function gm(e, t, n) {
	let { breakerState: r, flush: i, baseRtl: a, addToLine: o, scale: s, firstIndent: c, tabOriginPx: l, maxWidth: u, marginRightPx: d, tabFollowWidth: f, tabStops: p, defaultTabPt: m, tabFollowingMetrics: h, availW: g } = e;
	t.marginAllocation = !1, t.alignedGapLimit = void 0, t.alignedFitBack = void 0, t.alignedCellWidth = void 0, t.alignedCellDecimal = void 0, t.alignedCellPhysicalDecimal = void 0, t.windowOverflow = void 0, t.resolvedAlignment = void 0;
	let _ = t.displacedFloatTabFrame === !0, v = () => _ && !r.gapTransaction?.cursor && y(), y = () => hm(e) <= u, b = () => {
		i(void 0, !1, t.src), r.queue.unshift(t);
	}, x = t.fontSize * s * (t.textOwnedLineBox ? t.lineBoxAscentRatio ?? 0 : _e), S = t.fontSize * s * (t.textOwnedLineBox ? t.lineBoxDescentRatio ?? 0 : ge);
	if (a) {
		let i = !1;
		if (t.ptab) {
			let a = {
				...e,
				...r,
				...e.lineFit ? { fitWidth: g() } : {}
			};
			r.currentWidth += n(a);
			let { startPen: o, leftLimit: s, frame: c } = Cc(a), l = h().totalWidth, u = nr(t.ptab.relativeTo === "indent" ? c.indentStart : 0, t.ptab.relativeTo === "indent" ? c.indentEnd : s, c.bandStart, c.bandEnd, c.narrowed);
			if (i = !c.narrowed && t.ptab.alignment === "left" && t.ptab.relativeTo === "margin" && l > u.end - u.start, vc(t.ptab.alignment, u.start, u.end, l) < o + r.currentWidth && r.currentLine.length > 0) {
				b();
				return;
			}
		}
		let a = {
			...e,
			...r,
			...e.lineFit ? { fitWidth: g() } : {}
		}, { startPen: s, frame: c } = Cc(a), u = r.queue.peek(), d = !t.ptab && u !== void 0 && "text" in u && u.rtl === !0;
		if (d || c.narrowed || i || t.ptab?.relativeTo === "indent") {
			r.currentWidth += n(a);
			let u = s + r.currentWidth, d = t.ptab && !i ? void 0 : _c(u, e.bidiCustomStopsPx, e.bidiIntervalPx, c.leadingShift, _);
			if (t.ptab || (t.resolvedAlignment = d?.alignment ?? "left"), t.ptab ? t.ptab.alignment === "left" : !d || yc(d.alignment) === "leading") {
				let n = t.ptab && !i ? nr(t.ptab.relativeTo === "indent" ? c.indentStart : 0, t.ptab.relativeTo === "indent" ? c.indentEnd : a.marginRightPx + l, c.bandStart, c.bandEnd, c.narrowed).start : d?.pos ?? u, s = n > c.fitEnd;
				if (!(s && !c.narrowed && !t.ptab)) {
					let i = s && c.narrowed && !t.ptab && v();
					if (s && !i && r.currentLine.length > 0) {
						b();
						return;
					}
					let a = s && !i ? 0 : Math.max(0, n - u);
					if (!i && !t.ptab && um(e, a)) {
						b();
						return;
					}
					t.readingGap = a, t.measuredWidth = a, t.leader = d?.leader, t.windowOverflow = i || void 0, o(t, a, t.fontSize, x, S), i && om(e);
					return;
				}
			}
		} else t.ptab || (r.currentWidth += n(a), t.resolvedAlignment = _c(s + r.currentWidth, e.bidiCustomStopsPx, e.bidiIntervalPx, c.leadingShift, _)?.alignment ?? "left");
		if (t.readingGap = void 0, t.measuredWidth = 0, !t.ptab && c.narrowed && v()) {
			t.windowOverflow = !0, o(t, 0, t.fontSize, x, S), om(e);
			return;
		}
		let f = ap(e) && cm(t, () => _c(s + r.currentWidth, e.bidiCustomStopsPx, e.bidiIntervalPx, c.leadingShift, _)) && e.fitsMeasuredWidth(r.currentWidth + h().totalWidth, lm(e));
		if (!t.ptab && !f && um(e, 0)) {
			b();
			return;
		}
		if (t.alignedFitBack = d && !pm(e) ? !0 : void 0, t.alignedFitBack) {
			let n = h(t.resolvedAlignment === "decimal" ? t : void 0);
			t.alignedCellWidth = n.totalWidth;
			let r = fm(e);
			t.alignedCellDecimal = r ? n.decimalPrefixWidth : void 0, t.alignedCellPhysicalDecimal = r ? n.physicalDecimalOffset : void 0;
		}
		o(t, 0, t.fontSize, x, S), f && om(e);
		return;
	}
	let C = r.lineXOffset, w = r.lineXOffset !== 0 || r.lineMaxWidth !== u, T = C + r.currentWidth + (r.isFirst ? c : 0);
	if (t.ptab) {
		t.resolvedAlignment = t.ptab.alignment;
		let n = r.lineXOffset + (r.isFirst ? Math.min(0, c) : 0), i = r.lineXOffset + r.lineMaxWidth, a = nr(t.ptab.relativeTo === "indent" ? 0 : -l, t.ptab.relativeTo === "indent" ? u : d, n, i, w), s = h().totalWidth, f = vc(t.ptab.alignment, a.start, a.end, s) - T;
		if (f < 0) {
			if (r.currentLine.length > 0) {
				b();
				return;
			}
			f = 0;
		}
		let p = cm(t, () => null) ? lm(e) : g();
		if (!e.fitsMeasuredWidth(r.currentWidth + f, p)) {
			if (r.currentLine.length > 0) {
				b();
				return;
			}
			f = 0;
		}
		t.measuredWidth = f, o(t, f, t.fontSize, x, S), cm(t, () => null) && e.fitsMeasuredWidth(r.currentWidth + s, p) && om(e);
		return;
	}
	let E = _c(T + l, p.map((e) => ({
		pos: e.pos * s,
		alignment: e.alignment,
		leader: e.leader
	})), m * s, C, _);
	t.resolvedAlignment = E?.alignment ?? "left";
	let D = E ? E.pos - l : T, O = E ? yc(E.alignment) : "leading";
	if (E && cm(t, () => E)) {
		let n = D;
		t.leader = E.leader;
		let i = h(), a = O === "center" ? i.totalWidth / 2 : O === "decimal" ? i.decimalPrefixWidth ?? i.totalWidth : i.totalWidth, s = n - T - a;
		s <= 0 && (s = 0);
		let c = sm(e), l = e.fitsMeasuredWidth(r.currentWidth + s + i.totalWidth, c) ? c : g();
		if (t.marginAllocation = l > lm(e) && r.currentWidth + s + i.totalWidth > lm(e), !e.fitsMeasuredWidth(r.currentWidth + s + i.totalWidth, l)) {
			if (w && s > 0 && v()) {
				t.measuredWidth = s, o(t, s, t.fontSize, x, S), om(e);
				return;
			}
			if (pm(e) || O === "decimal" && !fm(e)) {
				if (r.currentWidth + s > l) {
					if (r.currentLine.length > 0) {
						b();
						return;
					}
					s = 0;
				}
			} else if (s > 0 && (t.alignedGapLimit = s), s = 0, ap(e) && e.fitsMeasuredWidth(r.currentWidth + i.totalWidth, lm(e))) l = lm(e);
			else if (um(e, 0)) {
				b();
				return;
			}
		}
		t.measuredWidth = s, o(t, s, t.fontSize, x, S), e.fitsMeasuredWidth(r.currentWidth + i.totalWidth, l) && om(e);
		return;
	}
	let k = D - T;
	E && (t.leader = E.leader);
	let A = t.listLabel !== void 0;
	if (A && r.currentLine.length === 0) {
		t.measuredWidth = 0, o(t, 0, 0, 0, 0);
		return;
	} else if (!eu(r.currentWidth + k, g()) || A && r.currentWidth + k >= g()) {
		if (w && v()) {
			k = Math.max(0, k), t.measuredWidth = k, o(t, k, t.fontSize, x, S), om(e);
			return;
		}
		if (r.currentLine.length > 0) {
			b();
			return;
		}
		k = 0;
	}
	if (k = Math.max(0, k), !A && um(e, k)) {
		b();
		return;
	}
	t.measuredWidth = k, o(t, k, t.fontSize, x, S);
}
function _m(e) {
	for (let t of e.breakerState.queue) {
		if (!("text" in t)) return;
		if (t.text.length > 0) return String.fromCodePoint(t.text.codePointAt(0));
	}
}
function vm(e, t, n, r) {
	let i = [{
		segment: t,
		text: n
	}];
	if (n !== t.text || n.length === 0 || n.endsWith(" ")) return {
		pieces: i,
		fitWidth: r
	};
	let { kinsoku: a, strAdvance: o } = e, s = (e, t) => a.enabled && (a.lineEndForbidden.has(e.codePointAt(0)) || a.lineStartForbidden.has(t.codePointAt(0))), c = [...n].at(-1), l = r;
	for (let t of e.breakerState.queue) {
		if (!("text" in t) || t.text.length === 0) break;
		let e = [...t.text], n = tc(t.text), r = 0, a = !1;
		for (; r < e.length;) {
			let i = e[r];
			if (i === " ") {
				for (; r < e.length && e[r] === " ";) r += 1;
				a = !0;
				break;
			}
			if (!(r === 0 ? t.joinPrev === !0 || t.hardJoinPrev === !0 || s(c, i) : !n || s(c, i))) {
				a = !0;
				break;
			}
			c = i, r += 1;
		}
		if (r > 0) {
			let n = e.slice(0, r).join("");
			i.push({
				segment: t,
				text: n
			});
			let a = n.replace(/ +$/u, "");
			a.length > 0 && (l += o(t, a));
		}
		if (a || r < e.length) break;
	}
	return {
		pieces: i,
		fitWidth: l
	};
}
function ym(e, t, n) {
	if (!Nl(e.breakerState, t.text, t)) return !1;
	let r = e.mixedSpaceRequirement(vm(e, t, t.text, n));
	return r === void 0 ? !1 : (r > 0 && e.markMixedSpacesCompressed(), !0);
}
function bm(e, t) {
	let n = e.breakerState.currentLine.at(-1), r = n && "text" in n ? [...n.text].at(-1) : void 0;
	return t.hyperlink?.kind !== "external" && r !== void 0 && tc(r) && !tc(t.text);
}
function xm(e, t) {
	let { s: n } = t;
	if (n.autoSpaceBeforePt === void 0 || mp(e.breakerState.currentLine)) return t;
	let r = Uc(e, n);
	return n.autoSpaceLeadingPx = 0, r === 0 ? t : {
		...t,
		w: t.w - r,
		wForFit: t.wForFit - r
	};
}
function Sm(e, t) {
	let n = t.s.leadingWordBoundaryPx ?? 0;
	return n === 0 || mp(e.breakerState.currentLine) ? t : (t.s.leadingWordBoundaryPx = void 0, {
		...t,
		w: t.w - n,
		wForFit: t.wForFit - n
	});
}
function Cm(e, t) {
	if (!e.wrapCtx?.preservePre15AnchorLine || e.fitsMeasuredWidth(t, e.maxWidth)) return !0;
	let { breakerState: n } = e;
	return n.lineXOffset === 0 && n.lineMaxWidth === e.maxWidth && (n.gapTransaction === null || n.currentLineTopY === n.gapTransaction.requestTopY);
}
function wm(e, t) {
	let n = Sm(e, xm(e, t)), { breakerState: r, flush: i, addToLine: a, availW: o, fitsMeasuredWidth: s, fitHomogeneousLatinSpaces: c, appendQueuedIdeographicSpaceSegment: l, emergencyTextSplit: u, strNaturalAdvance: d, explicitTextSplit: f, queueEmergencyTail: p } = e, { s: m, w: h, h: g, asc: _, desc: v, wForFit: y, admitsTrailingOverflowPunctuation: b } = n;
	if (s(r.currentWidth + y, o()) && r.latinAppliedPerGap === 0 || c(m, y) || ym(e, m, y) || s(r.currentWidth + y, o())) m.measuredWidth = h, a(m, h, g, _, v), l(m);
	else if (b) m.measuredWidth = h, a(m, h, g, _, v), l(m);
	else if (tc(m.text) && m.seaBreaks === void 0 && m.hardJoinPrev !== !0) Em(e, n);
	else if (m.seaBreaks !== void 0 && m.hardJoinPrev !== !0) Dm(e, n);
	else if (r.currentLine.length === 0 || m.listLabel === void 0 && r.currentWidth < o() && r.currentLine.every(sp) || r.currentLine.every(zd) && Cm(e, y)) {
		let t = o() - r.currentWidth, n = f(m, t), i = n || u(m, t);
		if ((n === 0 && i < m.text.length || Qp(e, m, m.text.slice(0, i))) && e.forcedPlacement(e.minimalLegalTextWidth(m)), i >= m.text.length) m.measuredWidth = h, a(m, h, g, _, v);
		else {
			let e = m.text.slice(0, i), t = d(m, e);
			a({
				...m,
				...Fc,
				text: e,
				measuredWidth: t,
				...J(m, 0, e.length)
			}, t, g, _, v), p(m, i);
		}
	} else {
		let t = m.leadingWordBoundaryPx ?? 0, n = bm(e, m) ? 0 : f(m, o() - r.currentWidth - t);
		if (n > 0 && n < m.text.length) {
			let e = m.text.slice(0, n), t = d(m, e);
			a({
				...m,
				...Fc,
				text: e,
				measuredWidth: t,
				...J(m, 0, e.length)
			}, t, g, _, v), p(m, n);
			return;
		}
		if (m.joinPrev) {
			let n = o() - r.currentWidth - t, i = u(m, n, !0), s = (n > 0 || m.hardJoinPrev === !0) && i > 0 && i < m.text.length ? m.text.slice(0, i) : m.text;
			if (i < m.text.length || Qp(e, m, s)) {
				let t = Zp(r.currentLine), n = e.minimalLegalTextWidth(m), i = n === 0 && !ff(e) ? Math.min(gf(r.currentLine, e), em(r.currentLine, t)) : 0;
				e.forcedPlacement(em(r.currentLine, t) - i + n, t);
			}
			if ((n > 0 || m.hardJoinPrev === !0) && i > 0 && i < m.text.length) {
				let e = m.text.slice(0, i), t = d(m, e);
				a({
					...m,
					...Fc,
					text: e,
					measuredWidth: t,
					...J(m, 0, e.length)
				}, t, g, _, v), p(m, i);
				return;
			}
			m.measuredWidth = h, a(m, h, g, _, v);
			return;
		}
		let s = r.currentLine.at(-1);
		if (!(s !== void 0 && "isTab" in s && s.resolvedAlignment === "decimal" && !m.text.includes(".") && !fm(e)) && r.currentLine.every((e) => "isTab" in e && !e.ptab) && !dm(e) && gc(m, r.queue.peek(), e.characterGrid?.type === "snapToChars", e.baseRtl)) {
			let t = u(m, o() - r.currentWidth);
			if ((t < m.text.length || Qp(e, m, m.text.slice(0, t))) && e.forcedPlacement(r.currentWidth + e.minimalLegalTextWidth(m), 0), t >= m.text.length) {
				m.measuredWidth = h, a(m, h, g, _, v);
				return;
			}
			let n = m.text.slice(0, t), i = d(m, n);
			a({
				...m,
				...Fc,
				text: n,
				measuredWidth: i,
				...J(m, 0, n.length)
			}, i, g, _, v), p(m, t);
			return;
		}
		i(void 0, !1, m.src), r.queue.unshift(m);
	}
}
function Tm(e, t) {
	let { breakerState: n, flush: r, availW: i, segAdvance: a, strAdvance: o } = e, { s, w: c, trailingSpaceW: l, sDictSea: u, fitWidthFor: d } = t, f = bm(e, s), p = n.queue.peek();
	if (!f && s.explicitBreaks && p?.joinPrev) {
		let t = vf(s, n.queue, e, c, l, 0, !1, "whole-leader");
		if (!eu(n.currentWidth + d(t.width, t.trailingSpace, t.next, t.pieces), i())) {
			let t = e.explicitTextSplit(s, i() - n.currentWidth - (s.leadingWordBoundaryPx ?? 0));
			if (t > 0 && t < s.text.length) return e.queueEmergencyTail(s, t), n.queue.unshift({
				...s,
				...Fc,
				text: s.text.slice(0, t),
				...J(s, 0, t)
			}), !0;
		}
	}
	let m = s.listLabel === void 0 && n.currentWidth < i() && n.currentLine.length > 0 && n.currentLine.every(sp);
	if (!s.joinPrev && !m && n.currentLine.length > 0 && (p?.joinPrev || f && p?.explicitBreakBefore) && (n.queue.peek()?.hardJoinPrev === !0 || !tc(s.text)) && (n.queue.peek()?.hardJoinPrev === !0 || !(s.seaBreaks && s.seaBreaks.length > 0))) {
		let t = vf(s, n.queue, e, c, l, 0, !1, f ? "whole-word" : "prefix"), a = d(t.width, t.trailingSpace, t.next, t.pieces);
		!(n.currentLine.every(zd) && Cm(e, a) && t.pieces.every((e) => e.segment.seaBreaks === void 0)) && !eu(n.currentWidth + a, i()) && !(Nl(n, t.pieces.map((e) => e.text).join(""), t.pieces[0]?.segment) && e.mixedSpaceRequirement({
			pieces: t.pieces,
			fitWidth: a
		}) !== void 0) && r(void 0, !1, s.src);
	}
	if (u && n.currentLine.length > 0 && (() => {
		let e = n.currentLine[n.currentLine.length - 1];
		return !("text" in e) || e.text.endsWith(" ");
	})()) {
		let t = c, u = l, f = [{ segment: s }], p = n.queue.peek();
		if (!s.text.endsWith(" ")) {
			let e = n.queue[Symbol.iterator]();
			for (let n = e.next(); !n.done; n = e.next()) {
				let r = n.value;
				if (p = r, !("text" in r) || r.seaBreaks === void 0 || !S(r.text)) break;
				let i = r, s = a(i), c = i.text.replace(/ +$/, "");
				if (t += s, f.push({ segment: i }), u = i.text.endsWith(" ") ? s - o(i, c) : 0, i.text.endsWith(" ")) {
					p = e.next().value;
					break;
				}
				p = void 0;
			}
		}
		let m = d(t, u, p, f);
		!eu(n.currentWidth + m, i()) && eu(m, tp(e, n.lineMaxWidth)) && r(void 0, !1, s.src);
	}
	return !1;
}
function Em(e, t) {
	let { breakerState: n, flush: r, addToLine: i, scale: a, characterGrid: o, availW: s, setMeasureFont: c, fontFamilyClasses: l, measurement: u, strAdvance: d, overflowPunct: f, appendQueuedIdeographicSpaceSegment: p, emergencyTextSplit: m, effectiveFontPx: h, ctx: g, verticalGlyphMeasurement: _, lineEdgeRules: v, strNaturalAdvance: y, retractCurrentLineForLeadingKinsoku: x, keepLeadingKinsokuWithCurrentLine: S } = e, { s: C, h: w, asc: T, desc: E, paragraphFinalIdeographicSpaceTail: D } = t, O = s() - n.currentWidth, k = "", A = D ? Nr(Ql(C.text), C.paragraphFinalIdeographicSpaceCount ?? 0) : Infinity;
	O > 0 && (Bc(C, a) < 0 || fl(C, o) === "latin" ? k = C.text.slice(0, m(C, O, !1)) : (c(tf(C.bold, C.italic, h(C), C.fontFamily, l, C.fontRoute)), u.withSegmentKerning(C, () => {
		k = tu(g, C.text, O, zc(C, o, a), tl(C), Bc(C, a), C.verticalRun === !0, _, (e) => d(C, e), A);
	})));
	let j = [...C.text], M = n.currentLine.length > 0 ? 0 : 1, N = (t, r) => {
		let i = (r && f && n.gapTransaction?.endsAtExclusion !== !0 && t < j.length && (e.cjkClosingMarkHang !== "one-from-fitting-prefix" || eu(n.currentWidth, s())) && (n.currentLine.length > 0 || t > 0) && !Hr(e.cjkClosingMarkHang, j[t], () => t + 1 < j.length ? j[t + 1] : _m(e), e.kinsoku, C.verticalRun === !0) && Wr(j[t], C.eastAsiaLanguage, C.overflowPunctuationEastAsianRun === !0, C.script === "ascii" || C.script === "highAnsi", C.script === "complexScript", C.overflowPunctuationBidiLanguage) ? t + 1 : null) ?? W(j, t, v, M), a = r ? oc(j, i, D && A === 0 ? 0 : A) : i, o = j.slice(0, a).join("").length;
		return C.text.slice(0, Xc(C, o, +(M > 0)));
	}, P = !1, F = [...k].length;
	if (n.currentLine.length > 0 && Nl(n, C.text, C)) {
		let t = [...C.text], n = (n) => {
			let r = t.slice(0, n).join("");
			return !r.endsWith(" ") && e.mixedSpaceRequirement(vm(e, C, r, d(C, r))) !== void 0;
		}, r = [...N(F, !0)].length, i = Math.max(F, r), a = t.length;
		for (let e = 1; i + e <= t.length; e *= 2) {
			if (!n(i + e)) {
				a = i + e - 1;
				break;
			}
			i += e;
		}
		for (; i < a;) {
			let e = Math.ceil((i + a) / 2);
			n(e) ? i = e : a = e - 1;
		}
		let o = Math.max(F, r), s = (e) => !v.enabled || e >= t.length || !v.lineStartForbidden.has(t[e].codePointAt(0)) && !v.lineEndForbidden.has(t[e - 1].codePointAt(0));
		for (; i > o && !s(i);) --i;
		i > o && (k = t.slice(0, i).join(""), P = !0);
	}
	let I = !1;
	if (!P && n.currentLine.length > 0 && Sp(e) && (Uc(e, C) > 0 || n.currentLine.some((e) => "text" in e && (e.autoSpaceLeadingPx ?? 0) > 0))) {
		let t = [...C.text], n = (n) => {
			let r = t.slice(0, n).join("");
			return !r.endsWith(" ") && kp(e, C, r) !== void 0;
		}, r = Math.max(F, [...N(F, !0)].length), i = r, a = t.length;
		for (let e = 1; i + e <= t.length; e *= 2) {
			if (!n(i + e)) {
				a = i + e - 1;
				break;
			}
			i += e;
		}
		for (; i < a;) {
			let e = Math.ceil((i + a) / 2);
			n(e) ? i = e : a = e - 1;
		}
		i > r && i < t.length && (k = t.slice(0, i).join(""), I = !0);
	}
	let L = [...k].length, R = N(L, !0);
	if (P) {
		let t = (e) => e.length > 0 && !eu(n.currentWidth + d(C, e), s()), r = (e) => {
			if (e.length < C.text.length) return [...C.text.slice(e.length)][0];
			for (let e of n.queue) {
				if (!("text" in e)) return;
				if (e.text.length > 0) return [...e.text][0];
			}
		}, i = (e) => {
			if (!v.enabled || e.length === 0) return !0;
			let t = r(e);
			return t === void 0 || !v.lineStartForbidden.has(t.codePointAt(0)) && !v.lineEndForbidden.has([...e].at(-1).codePointAt(0));
		}, a = (n) => !t(n) || i(n) && e.mixedSpaceRequirement(vm(e, C, n, d(C, n))) !== void 0;
		if (!a(R)) {
			let e = N(L, !1);
			R = a(e) ? e : N(F, !0);
		}
		P = t(R);
	}
	let z = 0;
	if (I) {
		let t = (t) => t.length === 0 ? 0 : kp(e, C, t), n = t(R);
		if (n === void 0) {
			let e = N(L, !1);
			n = t(e), R = n === void 0 ? N(F, !0) : e;
		}
		z = n ?? 0;
	}
	if (n.currentLine.length === 0) {
		let t = W(j, L, v, 0), n = j.slice(0, t).join("").length;
		(Xc(C, n, 1) === 0 || Qp(e, C, R)) && e.forcedPlacement(e.minimalLegalTextWidth(C));
	}
	if (R.length > 0) {
		P && e.markMixedSpacesCompressed(), z > 0 && (n.justifiedCompressionPx = z);
		let t = y(C, R);
		i({
			...C,
			...Fc,
			text: R,
			measuredWidth: t,
			...J(C, 0, R.length)
		}, t, w, T, E);
		let r = C.text.slice(R.length);
		r ? n.queue.unshift({
			...C,
			...Fc,
			text: r,
			...J(C, R.length, C.text.length),
			measuredWidth: 0,
			src: Oc(C.src, R.length)
		}) : p(C);
	} else if (n.currentLine.length > 0) {
		let t = x(C);
		if (t.kind === "blocked") {
			let t = Zp(n.currentLine);
			e.forcedPlacement(em(n.currentLine, t) + d(C, C.text.slice(0, b(C.text).find((e) => e > 0) ?? C.text.length)), t), S(C, w, T, E);
			return;
		}
		r(void 0, !1, t.kind === "retracted" ? t.tail.src : C.src), n.queue.unshift(C), t.kind === "retracted" && n.queue.unshift(t.tail);
	} else {
		let e = [...C.text], t = e.length > 0 ? oc(e, 1, C.paragraphFinalIdeographicSpaceTail === !0 ? Nr(vs.test(e[0] ?? ""), C.paragraphFinalIdeographicSpaceCount ?? 0) : Infinity) : 0, r = e.slice(0, t).join("").length, a = Xc(C, r) || m(C, s(), !0), o = C.text.slice(0, a);
		if (o) {
			let e = y(C, o);
			i({
				...C,
				...Fc,
				text: o,
				measuredWidth: e,
				...J(C, 0, o.length)
			}, e, w, T, E);
			let t = C.text.slice(o.length);
			t ? n.queue.unshift({
				...C,
				...Fc,
				text: t,
				...J(C, o.length, C.text.length),
				measuredWidth: 0,
				src: Oc(C.src, o.length)
			}) : p(C);
		}
	}
}
function Dm(e, t) {
	let { breakerState: n, flush: r, addToLine: i, scale: a, characterGrid: o, availW: s, strAdvance: c, emergencyTextSplit: l, strNaturalAdvance: u, retractCurrentLineForLeadingKinsoku: d, keepLeadingKinsokuWithCurrentLine: f } = e, { s: p, h: m, asc: h, desc: g } = t, _ = p, v = s() - n.currentWidth, y = (e) => c(_, e), x = k(_.text) && Bc(_, a) >= 0 && fl(_, o) !== "latin", S = T(_.text, _.seaBreaks, 0, v, y, x);
	if (S > 0 && n.currentLine.length === 0 && Qp(e, _, _.text.slice(0, S)) && e.forcedPlacement(e.minimalLegalTextWidth(_)), S > 0) {
		let e = _.text.slice(0, S), t = u(_, e);
		i({
			..._,
			...Fc,
			text: e,
			measuredWidth: t,
			...J(_, 0, e.length)
		}, t, m, h, g);
		let r = _.text.slice(S);
		r && n.queue.unshift({
			..._,
			...Fc,
			text: r,
			...J(_, S, _.text.length),
			measuredWidth: 0,
			src: Oc(_.src, S),
			seaBreaks: ac(_.seaBreaks, S)
		});
	} else if (n.currentLine.length > 0) {
		let t = d(_);
		if (t.kind === "blocked") {
			let t = Zp(n.currentLine);
			e.forcedPlacement(em(n.currentLine, t) + c(_, _.text.slice(0, b(_.text).find((e) => e > 0) ?? _.text.length)), t), f(_, m, h, g);
			return;
		}
		r(void 0, !1, t.kind === "retracted" ? t.tail.src : _.src), n.queue.unshift(_), t.kind === "retracted" && n.queue.unshift(t.tail);
	} else {
		e.forcedPlacement(e.minimalLegalTextWidth(_));
		let t = _.seaBreaks[0] ?? _.text.length, r = _.text.slice(0, t), a = b(r), o = T(r, a, 0, v, y, x);
		o <= 0 && (o = a.length > 0 ? a[0] : r.length), o = Xc(_, o) || l(_, v, !0);
		let s = _.text.slice(0, o), c = u(_, s);
		i({
			..._,
			...Fc,
			text: s,
			measuredWidth: c,
			...J(_, 0, s.length)
		}, c, m, h, g);
		let d = _.text.slice(o);
		d && n.queue.unshift({
			..._,
			...Fc,
			text: d,
			...J(_, o, _.text.length),
			measuredWidth: 0,
			src: Oc(_.src, o),
			seaBreaks: ac(_.seaBreaks, o)
		});
	}
}
var Om = new Set([
	"left",
	"start",
	"center",
	"right",
	"end",
	"lowKashida"
]);
function km(e, t, n) {
	let r = e.bidiOrdering;
	if (!r || r.lineEndJustificationBeforeMode15 !== !1 || r.runDirectionUnauthored || !Om.has(r.alignment ?? "left") || !("text" in t) || t.text.trim() === "") return;
	let i = t.text.endsWith(" ") ? t : void 0, a = 0;
	if (n !== void 0) {
		let t = !1;
		for (let r of e.breakerState.queue) {
			if (!t) {
				if (r !== n) continue;
				t = !0;
			}
			if ("text" in r && r.text !== "" && /^ +$/u.test(r.text)) i = r, a += e.segAdvance(r);
			else if (!zd(r)) return;
		}
		if (!t) return;
	}
	if (!(!i || i.rtl === !0 === e.baseRtl)) return a;
}
function Am(e, t, n) {
	if (t !== "intrinsic") for (let t of e) for (let e of t.segments) !("text" in e) || e.metricOnly || e.text.length === 0 || (e.shapedClusters = void 0, e.textLayoutService && e.textShapeRequest && n(e, !0));
}
function jm(e) {
	let { ctx: t, segs: n, maxWidth: r, scale: i, tabStops: a, wrapCtx: o, fontFamilyClasses: s, kinsoku: c, characterGrid: l, defaultTabPt: u, baseRtl: d, startBoundary: f, widthPolicy: p, verticalGlyphMeasurement: m, passContext: h } = e, g = p === "bounded" ? e.lineEdgeRules ?? c : c, { probeHeights: _, preparedFloatWrap: v } = h, y = h.probeFloors ?? _, b = Bd(r, o);
	b.mixedSpaceEnabled = n.some((e) => "text" in e && (e.mixedSpaceAverageWidthRatio !== void 0 || e.autoSpaceCompressible === !0)) && !n.some((e) => "text" in e && e.text.includes("　"));
	let x, S = Nf, C = () => Pf(x), w = l?.type === "snapToChars" && l.characterPitchPt != null && l.characterPitchPt > 0 ? l.characterPitchPt * i : null, T = (e) => If(x, e), E = (e, t) => Zf(x, e, t), D = (e) => Lf(x, e), O = (e = 0) => Wf(x, e), k = () => ep(x), A = (e, t) => op(x, e, t), j = d ? a.map((e) => ({
		pos: e.pos * i,
		alignment: e.alignment,
		leader: e.leader
	})) : [], M = u * i, N = (e, t = !1, n) => cp(x, e, t, n), P = (e, t) => lp(x, e, t), F = (e, t, n, r, i) => up(x, e, t, n, r, i), I = (e, t, n) => dp(x, e, t, n), L = new yl(t, i, (e) => tf(e.bold, e.italic, q(e, i), e.fontFamily, s, e.fontRoute), m), R = (e) => q(e, i), z = (e, t = !1) => L.measureSegment(e, t), ee = (e, t) => L.verticalInkExtra(e, t), B = (e) => L.setFont(e), V = kc(n), te = {
		segIndex: n.length,
		charOffset: 0,
		...V === void 0 ? {} : { sourceTextStart: V }
	};
	b.queue = new Ld(Rd(n, f, g, i, L));
	let H = n.at(-1);
	f?.trailingEmptyLine === !0 && f.segIndex === n.length && f.charOffset === 0 && H && "lineBreak" in H && (b.trailingBreakFontSize = H.fontSize);
	let U = (e) => fp(x, e), ne = (e, t) => gp(x, e, t), re = (e) => _p(x, e), ie = (e, t, n = !1) => vp(x, e, t, n), ae = (e) => yp(x, e), oe = (e, t, n = !1) => bp(x, e, t, n), se = (e, t) => xp(x, e, t), W = (e) => Ul(x, e), ce = () => Wl(x), le = (e) => Pp(x, e), ue = (e) => Fp(x, e), de = (e) => Ip(x, e), fe = Lp, pe = (e) => Rp(x, e), me = (e) => Bp(x, e), he = (e, t, n = !0) => Hp(x, e, t, n), ge = (e, t) => Up(x, e, t), _e = (e, t) => Wp(x, e, t), ve = (e) => Gp(x, e), ye = (e, t, n, r) => Kp(x, e, t, n, r);
	x = {
		...e,
		lineEdgeRules: g,
		paragraphFirstIndent: e.firstIndent,
		reservePrefixWork: ps(),
		probeHeights: _,
		probeFloors: y,
		preparedFloatWrap: v,
		breakerState: b,
		sameLatinSpaceFace: S,
		materializeLatinSpaceCompression: C,
		snapPitchPx: w,
		lineHeadRequirement: T,
		startLine: O,
		forcedPlacement: E,
		minimalLegalTextWidth: D,
		availW: k,
		fitsMeasuredWidth: A,
		bidiCustomStopsPx: j,
		bidiIntervalPx: M,
		flush: N,
		prospectiveSnapAdvance: P,
		addToLine: F,
		admitLineMetric: I,
		measurement: L,
		effectiveFontPx: R,
		measureText: z,
		verticalInkExtra: ee,
		setMeasureFont: B,
		endBoundary: te,
		segNaturalAdvance: U,
		standaloneSnapAdvance: ne,
		segAdvance: re,
		strNaturalAdvance: ie,
		eastAsianSnapCellCount: ae,
		strAdvance: oe,
		fitHomogeneousLatinSpaces: se,
		mixedSpaceRequirement: W,
		markMixedSpacesCompressed: ce,
		textSegmentBox: le,
		appendQueuedIdeographicSpaceSegment: ue,
		tabFollowWidth: de,
		decimalAlignmentPoint: fe,
		decimalAlignmentPrefixWidth: pe,
		tabFollowingMetrics: me,
		emergencyTextSplit: he,
		explicitTextSplit: ge,
		queueEmergencyTail: _e,
		retractCurrentLineForLeadingKinsoku: ve,
		keepLeadingKinsokuWithCurrentLine: ye
	}, Object.defineProperty(x, "firstIndent", {
		get: () => b.firstIndentOverride ?? e.firstIndent,
		enumerable: !0
	}), O(T()), tm(x, {
		captureGapSnapshot: () => Xf(x, !1),
		rejectGap: (e) => $f(x, e)
	}), b.currentLine.length > 0 ? N() : b.trailingBreakFontSize !== null && N(b.trailingBreakFontSize);
	for (let e = 0; e < b.lines.length;) {
		let t = e + 1, n = b.lines[e];
		for (; t < b.lines.length && b.lines[t].physicalLineIndex === n.physicalLineIndex;) t += 1;
		let r = b.lines[t - 1], { segments: i, xOffset: a, availWidth: o, marginExtension: s, consumedEnd: c, endsWithBreak: l, ...u } = r, d;
		for (let n = e; n < t; n += 1) for (let e of b.lines[n].segments) {
			if ("isTab" in e) continue;
			let t = "text" in e && e.positionExtendsLineBox !== !1 ? e.position ?? 0 : 0;
			d = d === void 0 ? t : d === t ? d : 0;
		}
		for (let n = e; n < t; n += 1) {
			let e = b.lines[n];
			Object.assign(e, u), e.endsWithBreak = r.endsWithBreak;
			for (let t of e.segments) "text" in t && (t.lineRelativePosition = Jr(t.position ?? 0, d ?? 0));
		}
		e = t;
	}
	return Am(b.lines, p, z), b.lines;
}
function Mm(e, t, n, r, i, a = [], o, s = {}, c = 0, l = pe, u = void 0, d = 36, f = n, p = !1, m = !1, h = !1, g, _ = "bounded", v, y = !1, b = !1, x, S, C, w, T) {
	if (T === void 0) {
		let T = xc(p, a) ? ji() : void 0, E = (E, D, O = null) => Mm(e, Xo(t), n, r, i, a, o, s, c, l, u, d, f, p, m, h, g, _, v, y, b, x, S, C, w, {
			probeHeights: E,
			probeFloors: O,
			preparedFloatWrap: D,
			decimalOrder: T
		});
		if (!o || _ === "intrinsic") return E(null);
		let D = o.lineWindow ? void 0 : no(o.floats), O = es((e, t) => E(e, D, t), (e) => o.lineBoxH(e.ascent, e.descent, e.hasRuby, e.intendedSingle, e.eastAsian, e.gridCountSingle, e.uniformPositionAuto, e.inlinePictureTextSingle, e.latinGridCountSingle), o.resolveLineAdvances), k = o.resolveLineAdvances?.(O);
		return O.map((e, t) => ({
			...e,
			wrapAllocation: Object.freeze({
				physicalLineIndex: e.physicalLineIndex,
				topYPt: e.topY,
				advancePt: k?.[t] ?? o.lineBoxH(e.ascent, e.descent, e.hasRuby, e.intendedSingle, e.eastAsian, e.gridCountSingle, e.uniformPositionAuto, e.inlinePictureTextSingle, e.latinGridCountSingle)
			})
		}));
	}
	return jm({
		ctx: e,
		segs: t,
		maxWidth: n,
		firstIndent: r,
		scale: i,
		tabStops: a,
		wrapCtx: o,
		fontFamilyClasses: s,
		tabOriginPx: c,
		kinsoku: l,
		lineEdgeRules: w,
		characterGrid: u,
		defaultTabPt: d,
		marginRightPx: f,
		baseRtl: p,
		isJustified: m,
		stretchLastLine: h,
		startBoundary: g,
		bidiOrdering: C,
		widthPolicy: _,
		verticalGlyphMeasurement: v,
		overflowPunct: y,
		justifiedCompression: b !== !1,
		justifiedCompressionAdmissionOnly: typeof b == "object" && b.admissionOnly === !0,
		lineEndIdeographicSpaceHangs: typeof b == "object" ? b.lineEndIdeographicSpaceHangs : b,
		...x ? { lineFit: x } : {},
		...S ? { cjkClosingMarkHang: S } : {},
		passContext: T
	});
}
var Nm = Object.freeze([
	...Array.from({ length: 95 }, (e, t) => 32 + t),
	183,
	12354,
	19968
]);
function Pm(e) {
	return e.__pageObjects ?? [];
}
var Fm = [
	"ascii",
	"highAnsi",
	"eastAsia",
	"complexScript"
];
function Im(e, t) {
	let n = e.fontSlots, r = t.fontSlots;
	return !n || !r ? n === r : Fm.every((e) => n.direct[e] === r.direct[e] && n.theme[e] === r.theme[e] && n.themePresent[e] === r.themePresent[e]);
}
var Lm = /* @__PURE__ */ new WeakMap(), Rm = /* @__PURE__ */ new WeakMap();
function zm(e) {
	if (!e.enabled) return e;
	let t = Lm.get(e);
	return t || (t = Object.freeze({
		...e,
		enabled: !1
	}), Lm.set(e, t)), t;
}
function Bm(e, t, n, r) {
	return r.kinsoku === !1 && e.kinsoku.enabled && e.compat.paragraphOffJapaneseLineEdges && !e.hasCustomKinsokuRules && !((e.characterSpacingControl === "compressPunctuation" || e.characterSpacingControl === "compressPunctuationAndJapaneseKana") && (r.alignment === "lowKashida" || r.alignment === "mediumKashida" || r.alignment === "highKashida")) && (r.alignment === "left" || r.alignment === "both" || r.alignment === "justify" || r.alignment === "distribute" || r.alignment === "lowKashida" || r.alignment === "mediumKashida" || r.alignment === "highKashida" || r.alignment === "thaiDistribute") && n.story === "body" && n.containers.length === 0 && !n.quarterTurned && r.framePr == null && r.bidi !== !0 && r.wordWrap !== !1 && t.columns.length === 1 && t.textDirection === "lrTb" && t.sectionFlow === void 0 && (t.grid.kind === "none" || t.grid.kind === "lines" || t.grid.kind === "linesAndChars" && !t.grid.charSpacePt) && r.numbering == null && r.tabStops.length === 0 && e.paragraphOffBodySource?.(r) === !0;
}
function Vm(e) {
	if (e.runs.length === 0) return !1;
	let t, n = !1, i = !1, a;
	for (let o of e.runs) {
		if (o.type !== "text" || o.rtl === !0 || o.cs === !0 || o.ruby || o.vertAlign != null || o.smallCaps || o.allCaps || o.fitTextVal != null || o.position != null || "optionalHyphen" in o && o.optionalHyphen || o.noteRef !== void 0 || "noteSeparatorCharacter" in o && o.noteSeparatorCharacter !== void 0 || "noBreakBefore" in o && o.noBreakBefore || "noBreakAfter" in o && o.noBreakAfter || "noBreakRanges" in o && o.noBreakRanges?.length || o.charScale !== void 0 && o.charScale !== 1 || o.charSpacing !== void 0 && o.charSpacing !== 0) return !1;
		let e = "langEastAsia" in o ? o.langEastAsia?.toLowerCase() : void 0;
		if (e !== void 0 && e !== "ja-jp" || n && e !== t || (n = !0, t = e, a && (o.fontSize !== a.fontSize || o.fontFamily !== a.fontFamily || o.fontFamilyEastAsia !== a.fontFamilyEastAsia || ("fontFamilyHighAnsi" in o ? o.fontFamilyHighAnsi : void 0) !== a.fontFamilyHighAnsi || ("fontHint" in o ? o.fontHint : void 0) !== a.fontHint || o.kerning !== a.kerning || !Im(a, o) || o.bold !== a.bold || o.italic !== a.italic || o.underline !== a.underline || o.strikethrough !== a.strikethrough))) return !1;
		a = o, i ||= e === "ja-jp" || /[\p{Script=Hiragana}\p{Script=Katakana}]/u.test(o.text);
		for (let e of o.text) {
			let t = e.codePointAt(0), n = r(t);
			if (N(t) || /[\p{Cc}\p{Cf}]/u.test(e) || n === "R" || n === "AL" || n === "AN") return !1;
		}
	}
	return i;
}
function Hm(e, t, n) {
	if (!n || !e.compat.paragraphOffThaiLineEdges || t.alignment !== "thaiDistribute" || e.characterSpacingControl !== "compressPunctuation" && e.characterSpacingControl !== "compressPunctuationAndJapaneseKana") return;
	if (t.overflowPunct === !1) return e.kinsoku;
	let r = Rm.get(e.kinsoku);
	if (!r) {
		let t = new Set(e.kinsoku.lineStartForbidden);
		for (let e of nc) t.delete(e.codePointAt(0));
		r = Object.freeze({
			...e.kinsoku,
			lineStartForbidden: t
		}), Rm.set(e.kinsoku, r);
	}
	return r;
}
function Um(e, t) {
	if (e) return t === "sideways-lr" ? "upright-physical-counter-clockwise" : "upright-physical";
}
function Wm(e) {
	switch (e) {
		case "tb":
		case "tbV":
		case "lrTb":
		case "lrTbV": return "horizontal-tb";
		case "rl":
		case "rlV":
		case "tbRl":
		case "tbRlV": return "vertical-rl";
		case "btLr": return "vertical-rl";
		case "lr":
		case "lrV":
		case "tbLrV": return "vertical-lr";
		default: throw RangeError(`Unsupported Transitional text direction ${JSON.stringify(e)}`);
	}
}
function Gm(e) {
	if (e.sectionFlow == null) return Wm(e.textDirection);
	if (e.sectionFlow !== "bottomToTop" || e.textDirection !== "btLr") throw RangeError(`Section flow ${String(e.sectionFlow)} contradicts text direction ${JSON.stringify(e.textDirection)}`);
	return "sideways-lr";
}
function Km(e) {
	if (!Number.isFinite(e.widthPt) || !Number.isFinite(e.heightPt) || e.widthPt <= 0 || e.heightPt <= 0) throw RangeError("Physical page extents must be positive and finite");
}
function qm(e) {
	if (!Number.isFinite(e.xPt) || !Number.isFinite(e.yPt)) throw RangeError("Point coordinates must be finite");
}
function Jm(e) {
	if (![
		e.a,
		e.b,
		e.c,
		e.d,
		e.e,
		e.f
	].every(Number.isFinite)) throw RangeError("Matrix coefficients must be finite");
}
function Ym(e) {
	if (qm(e), !Number.isFinite(e.widthPt) || !Number.isFinite(e.heightPt) || e.widthPt < 0 || e.heightPt < 0) throw RangeError("Rectangle extents must be finite and non-negative");
}
function Xm(e, t) {
	switch (Km(e), t) {
		case "horizontal-tb": return {
			widthPt: e.widthPt,
			heightPt: e.heightPt
		};
		case "vertical-rl":
		case "vertical-lr":
		case "sideways-lr": return {
			widthPt: e.heightPt,
			heightPt: e.widthPt
		};
		default: throw RangeError(`Unsupported writing mode ${String(t)}`);
	}
}
function Zm(e, t) {
	switch (Km(e), t) {
		case "horizontal-tb": return {
			widthPt: e.widthPt,
			heightPt: e.heightPt
		};
		case "vertical-rl":
		case "vertical-lr":
		case "sideways-lr": return {
			widthPt: e.heightPt,
			heightPt: e.widthPt
		};
		default: throw RangeError(`Unsupported writing mode ${String(t)}`);
	}
}
function Qm(e, t) {
	switch (Km(t), e) {
		case "horizontal-tb": return {
			a: 1,
			b: 0,
			c: 0,
			d: 1,
			e: 0,
			f: 0
		};
		case "vertical-rl": return {
			a: 0,
			b: 1,
			c: -1,
			d: 0,
			e: t.widthPt,
			f: 0
		};
		case "vertical-lr": return {
			a: 0,
			b: 1,
			c: 1,
			d: 0,
			e: 0,
			f: 0
		};
		case "sideways-lr": return {
			a: 0,
			b: -1,
			c: 1,
			d: 0,
			e: 0,
			f: t.heightPt
		};
		default: throw RangeError(`Unsupported writing mode ${String(e)}`);
	}
}
function $m(e, t) {
	switch (Km(t), e) {
		case "horizontal-tb": return {
			a: 1,
			b: 0,
			c: 0,
			d: 1,
			e: 0,
			f: 0
		};
		case "vertical-rl": return {
			a: 0,
			b: -1,
			c: 1,
			d: 0,
			e: 0,
			f: t.widthPt
		};
		case "vertical-lr": return {
			a: 0,
			b: 1,
			c: 1,
			d: 0,
			e: 0,
			f: 0
		};
		case "sideways-lr": return {
			a: 0,
			b: 1,
			c: -1,
			d: 0,
			e: t.heightPt,
			f: 0
		};
		default: throw RangeError(`Unsupported writing mode ${String(e)}`);
	}
}
function eh(e, t) {
	return Jm(e), qm(t), {
		xPt: e.a * t.xPt + e.c * t.yPt + e.e,
		yPt: e.b * t.xPt + e.d * t.yPt + e.f
	};
}
function th(e, t) {
	Ym(t);
	let n = [
		eh(e, t),
		eh(e, {
			xPt: t.xPt + t.widthPt,
			yPt: t.yPt
		}),
		eh(e, {
			xPt: t.xPt,
			yPt: t.yPt + t.heightPt
		}),
		eh(e, {
			xPt: t.xPt + t.widthPt,
			yPt: t.yPt + t.heightPt
		})
	], r = n.map(({ xPt: e }) => e), i = n.map(({ yPt: e }) => e), a = Math.min(...r), o = Math.min(...i);
	return {
		xPt: a,
		yPt: o,
		widthPt: Math.max(...r) - a,
		heightPt: Math.max(...i) - o
	};
}
function nh(e, t) {
	Jm(e);
	let n = eh(e, {
		xPt: 0,
		yPt: 0
	}), r = {
		top: {
			xPt: 0,
			yPt: -1
		},
		right: {
			xPt: 1,
			yPt: 0
		},
		bottom: {
			xPt: 0,
			yPt: 1
		},
		left: {
			xPt: -1,
			yPt: 0
		}
	}, i = {}, a = /* @__PURE__ */ new Set();
	for (let o of [
		"top",
		"right",
		"bottom",
		"left"
	]) {
		let s = eh(e, r[o]), c = s.xPt - n.xPt, l = s.yPt - n.yPt, u = l === 0 && c !== 0 ? c > 0 ? "right" : "left" : c === 0 && l !== 0 ? l > 0 ? "bottom" : "top" : null;
		if (u === null || a.has(u)) throw RangeError("Edge transforms require a non-degenerate axis-aligned matrix");
		i[u] = t[o], a.add(u);
	}
	if (a.size !== 4) throw RangeError("Edge transform must map every physical edge exactly once");
	return i;
}
function rh(e, t) {
	return {
		writingMode: e,
		logicalToPhysical: Qm(e, t),
		physicalToLogical: $m(e, t)
	};
}
function ih(e) {
	return e.fontSource === "native" || e.fontSource === "local" && e.authoredReferenceMetricAllowed === !0 || e.fontSource === void 0 && e.fontRoute?.scope === "native";
}
function ah(e, t = !1) {
	let n = t ? e.defaultFontFamily : e.runs.find((e) => e.type === "text")?.fontFamily ?? e.defaultFontFamily;
	return e.runs.every((r) => {
		if (r.type === "field" || r.type === "math") return !1;
		if (r.type !== "text") return !0;
		if (!/^[\x20-\x7e]*$/u.test(r.text) || r.bold || r.italic || r.underline || r.strikethrough || r.hyperlink || r.vertAlign || r.position || r.smallCaps || r.allCaps || r.ruby || r.charSpacing || r.charScale !== void 0 && r.charScale !== 100 || (r.fontFamily ?? e.defaultFontFamily) !== n || r.fontSize !== e.defaultFontSize) return !1;
		let i = r;
		for (let e of t ? [
			"fontFamilyHighAnsi",
			"fontFamilyEastAsia",
			"fontFamilyCs"
		] : ["fontFamilyHighAnsi", "fontFamilyCs"]) if (i[e] && i[e] !== n) return !1;
		return !0;
	});
}
function oh(e, t, n, r, i = !1, a, o) {
	let s = t.lineSpacing;
	if (!r.specifiedTextLineBoxMode || i || t.hasRuby || s?.explicit !== !0 || s.value <= 0 || s.rule !== "exact" && s.rule !== "atLeast" && !(s.rule === "auto" && s.value === 1) || s.rule === "exact" && (s.value < 12 || s.value > 30) || s.rule === "auto" && !t.lineGrid.active || e.topY !== void 0) return null;
	let c;
	for (let t of e.segments) if (!("text" in t) || !t.metricOnly && t.text && (!/^[\x20-\x7e]+$/u.test(t.text) || t.bold || t.italic || t.underline || t.strikethrough || t.hyperlink || t.ruby || t.vertAlign || t.position || t.smallCaps || t.verticalRun || t.textBoxLineFloor || !ih(t) || (c ??= t, (t.authoredFontFamily ?? t.fontFamily) !== (c.authoredFontFamily ?? c.fontFamily) || t.fontSize !== c.fontSize || t.fontRoute?.fingerprint !== c.fontRoute?.fingerprint))) return null;
	let l = n.paragraphMarkShapeInput ?? a;
	if (l && (l.weight !== 400 || l.style !== "normal" || l.complexScript)) return null;
	let u = c?.authoredFontFamily ?? c?.fontFamily;
	if (!c || n.defaultFontSize !== c.fontSize || c.fontSize <= 0 || !Number.isFinite(c.fontSize) || l && l.fontSizePt !== c.fontSize) return null;
	if (t.lineGrid.active || !r.specifiedTextLineBoxMode15) {
		if ("numbering" in n && n.numbering || n.defaultFontFamily !== u) return null;
		if (l) {
			for (let e of Object.values(l.fonts)) if (e && e !== u) return null;
		}
	}
	for (let t of e.segments) if ("text" in t && t.metricOnly && ((t.authoredFontFamily ?? t.fontFamily) !== u || t.bold || t.italic || !ih(t))) return null;
	let d = c.resolvedLineHeightRatio != null && c.resolvedDesignDescentRatio != null ? {
		lineHeightRatio: c.resolvedLineHeightRatio,
		designDescentRatio: c.resolvedDesignDescentRatio
	} : Ou(u, 400, "normal");
	return d ? oi({
		rule: s.rule,
		value: s.value,
		descentPt: d.designDescentRatio * c.fontSize,
		singlePt: Math.max(d.lineHeightRatio * c.fontSize, o ?? 0),
		pitchPt: t.lineGrid.active ? t.lineGrid.pitchPt : null
	}) : null;
}
function sh(e, t) {
	let n = e.map((e) => Object.freeze({ ...e })), r = no(n);
	return {
		hasExclusions: n.length > 0,
		lineWindow: ({ topYPt: e, minimumStartWidthPt: n, squareMinimumStartWidthPt: i, probeHeightPt: a, paragraphXPt: o, maximumWidthPt: s, columnXPt: c, columnWidthPt: l, admitsWindow: u }) => {
			let d = Fo(e, n, a, o, s, r, c, c + l, t ?? {
				xLeftPt: o,
				xRightPt: o + s,
				readingDirection: "ltr"
			}, i ?? n, u);
			return {
				topYPt: d.topY,
				xOffsetPt: d.xOffset,
				maximumWidthPt: d.maxWidth
			};
		},
		skipTopAndBottomBands: ({ yPt: e, columnXPt: t, columnWidthPt: r }) => Io(e, n, t, t + r)
	};
}
function ch(e) {
	if (e.characterGrid.active) return {
		type: e.characterGrid.kind,
		linePitchPt: null,
		characterPitchPt: e.characterGrid.pitchPt,
		charSpacePt: e.characterGrid.deltaPt
	};
}
function lh(e) {
	let t = ch(e);
	return {
		type: t ? t.type : e.lineGrid.active ? "lines" : null,
		linePitchPt: e.lineGrid.active ? e.lineGrid.pitchPt : null,
		characterPitchPt: e.characterGrid.active ? e.characterGrid.pitchPt : null,
		charSpacePt: e.characterGrid.active ? e.characterGrid.deltaPt : null
	};
}
function uh(e, t) {
	if (!ml(t)) return e;
	let n = t.linePitchPt;
	return n <= 0 ? e : e <= n ? n : Math.ceil(e / n) * n;
}
function dh(e, t, n, r, i, a) {
	let o = lh(t), s = Zl(i), c = H_(t, n.availableWidthPt), l = Math.max(1, n.availableWidthPt - t.physicalIndentLeftPt - t.physicalIndentRightPt - c), u = n.paragraphXPt + t.physicalIndentLeftPt, d = t.spaceBeforePt, f = t.spaceAfterPt, p = Object.freeze({ ...n }), m = r.fontFamilyClasses, h = i.documentHasEastAsianText === !0 || s.useFeLayout && t.lineGrid.active, g = t.lineSpacing?.rule === "exact" && t.lineSpacing.value > 0 ? void 0 : i.firstLinePictureMarkerHeightPt, _ = g !== void 0 && Number.isFinite(g) && g > 0 ? g : void 0, v = a ? void 0 : _, y = n.startYPt + (n.suppressSpaceBefore ? 0 : d);
	n.wrap && (y = n.wrap.skipTopAndBottomBands({
		yPt: y,
		columnXPt: n.paragraphXPt,
		columnWidthPt: n.availableWidthPt
	}));
	let b = t.lineSpacing, x = !a && v === void 0 && s.specifiedTextLineBoxMode15 && !t.lineGrid.active && !t.hasRuby && !(b?.rule === "exact" && (b.value < 12 || b.value > 30)) ? i.markOnlyTextMarkerAscentPt : void 0, S = (e, n, r) => {
		let i = t.lineSpacing;
		return i?.rule === "exact" && i.value > 0 ? e / 5 : i?.rule === "atLeast" ? Math.min(e, r) : Math.max(0, e - n);
	}, C = () => {
		let c = y, g = Df(e, 1, o, t.hasRuby, h, r.context, m, t.lineSpacing, i.resolvedLocalFonts, i.layoutServices?.text, i.paragraphMarkShapeInput, s.useFeLayout, v ?? x ?? 0), _ = g.advancePx, b, C;
		if (n.wrap) {
			let r = n.wrap.lineWindow({
				topYPt: c,
				minimumStartWidthPt: af(e),
				squareMinimumStartWidthPt: hs(af(e), 1),
				probeHeightPt: _,
				paragraphXPt: u,
				maximumWidthPt: l,
				columnXPt: n.paragraphXPt,
				columnWidthPt: n.availableWidthPt,
				...e.__indentsFromFloats === !0 ? { indentsFromFloats: !0 } : {}
			});
			c = r.topYPt;
			let o = i.numberingFirstLine;
			if (o && !a) {
				let e = o.authoredFirstIndentPx, r = Math.min(0, e), i = n.wrap.lineWindow({
					topYPt: c,
					minimumStartWidthPt: 0,
					squareMinimumStartWidthPt: 0,
					probeHeightPt: _,
					paragraphXPt: u + (t.baseRtl ? 0 : r),
					maximumWidthPt: l - r,
					columnXPt: n.paragraphXPt,
					columnWidthPt: n.availableWidthPt
				}), a = t.baseRtl ? l - (i.xOffsetPt + i.maximumWidthPt) : r + i.xOffsetPt, s = Math.max(Math.max(0, a) + e, a);
				i.topYPt === c && s > e && (C = s);
			}
			(r.xOffsetPt !== 0 || r.maximumWidthPt !== l) && (b = {
				xPt: u + r.xOffsetPt,
				yPt: c,
				widthPt: r.maximumWidthPt,
				heightPt: _
			});
		}
		let w = t.lineSpacing, T = v !== void 0 && w?.rule === "auto" && w.value > 1 && !t.hasRuby && !t.lineGrid.active ? (Math.max(g.ascentPx + g.descentPx, g.intendedSinglePx) - g.ascentPx - g.descentPx) / 2 + g.ascentPx : void 0;
		return {
			...b ? { markWrapBounds: b } : {},
			...C === void 0 ? {} : { markNumberingLeadingEdgePt: C },
			...T === void 0 ? {} : { markPictureBaselineOffsetPt: T },
			lines: [],
			markOnly: !0,
			requestedSpaceBeforePt: d,
			requestedSpaceAfterPt: f,
			uniformRubyAdvancePt: 0,
			contentStartYPt: c,
			contentEndYPt: c + _,
			lastLineBelowBaselinePt: x === void 0 ? kf(_, g.ascentPx, g.descentPx) : S(_, g.ascentPx, g.descentPx),
			markGridAfterLeadingPt: g.gridAfterLeadingPx,
			...i.layoutServices?.text.libreOfficeLineBoxes === !0 && !t.lineGrid.active && i.verticalPageFrame !== !0 && !wd(e.runs) && t.lineSpacing?.rule === "auto" && t.lineSpacing.value > 1 ? { markPageEdgeOverhangPt: Math.max(0, _ - Math.max(g.ascentPx + g.descentPx, g.intendedSinglePx)) } : {},
			placement: p
		};
	}, w = Td(e.runs, {
		...i,
		closingPairAdvanceAdmitted: au(e, t, i),
		uprightResourceOrientation: Um(i.verticalPageFrame, i.pageWritingMode),
		lineSpacing: t.lineSpacing,
		lineGridActive: t.lineGrid.active,
		characterGridActive: t.characterGrid.active,
		paragraphRtl: t.baseRtl,
		autoSpaceDE: e.autoSpaceDE,
		autoSpaceDN: e.autoSpaceDN
	});
	if (w.length === 0) return C();
	let T = v;
	if (_ !== void 0 && w.unshift({
		imagePath: "",
		mimeType: "",
		widthPt: 0,
		heightPt: _,
		inlinePicture: !0,
		markerMetric: !0,
		anchor: !1,
		anchorXPt: 0,
		anchorYPt: 0,
		anchorXFromMargin: !1,
		anchorYFromPara: !1
	}), t.lineSpacing?.rule === "auto" && t.lineSpacing.value > 1 && w.some((e) => "imagePath" in e && e.inlinePicture === !0)) {
		let n = i.inlineObjectRunLeadingAdmitted === !0 && Zr(s, e) && i.pageWritingMode === "horizontal-tb" && i.verticalCJK !== !0 && i.verticalPageFrame !== !0 && !t.lineGrid.active && !t.characterGrid.active && !t.baseRtl, a;
		for (let t of w) {
			if (!("imagePath" in t) || t.inlinePicture !== !0) continue;
			let o = t.sourceRunIndex === void 0 ? void 0 : e.runs[t.sourceRunIndex], s = o && (o.type === "shape" || o.type === "image") ? o : void 0, c = n ? s?.inlineObjectShapeInput : void 0, l = () => Df(e, 1, void 0, !1, h, r.context, m, null, i.resolvedLocalFonts, i.layoutServices?.text, c ?? i.paragraphMarkShapeInput).advancePx;
			t.paragraphMarkSinglePx = c ? l() : a ??= l();
		}
	}
	if ((t.lineSpacing == null || t.lineSpacing.rule === "auto" && t.lineSpacing.value === 1) && i.inlineObjectRunLeadingAdmitted === !0 && s.inlinePictureAutoLeading && !e.numbering && !e.framePr && i.pageWritingMode === "horizontal-tb" && i.verticalCJK !== !0 && i.verticalPageFrame !== !0 && !t.lineGrid.active && !t.characterGrid.active && !t.baseRtl && !t.hasRuby) {
		let t = e.runs.every((e) => e.type === "image" && !e.anchor || e.type === "shape" && e.inline === !0);
		for (let n of w) {
			if (!("imagePath" in n) || !n.inlinePicture || n.sourceRunIndex === void 0) continue;
			let a = e.runs[n.sourceRunIndex];
			if (!a || a.type !== "shape" && a.type !== "image" || !a.inlineObjectShapeInput || a.inlineObjectOrigin !== "drawingml" && !(a.inlineObjectOrigin === "vmlStaticTextbox" && t)) continue;
			let o = Df(e, 1, void 0, !1, h, r.context, m, null, i.resolvedLocalFonts, i.layoutServices?.text, a.inlineObjectShapeInput).advancePx;
			a.inlineObjectOrigin === "drawingml" ? n.objectRunBaselineMinimumPx = o : n.objectRunAdvanceMinimumPx = o;
		}
	}
	let E = ah(e, t.lineGrid.active || !s.specifiedTextLineBoxMode15), D = (r) => {
		let c = t.hasRuby ? uh(r.reduce((e, n) => Math.max(e, xf(t.lineSpacing, n.ascent, n.descent, 1, o, !0, n.intendedSingle, t.hasEastAsianText)), 0), o) : 0;
		t.hasRuby && a?.uniformRubyAdvancePt !== void 0 && (c = Math.max(c, a.uniformRubyAdvancePt));
		let l = [], u = T === void 0 ? void 0 : r[0], d = (e, t) => u !== void 0 && (t === 0 || u.physicalLineIndex !== void 0 && e.physicalLineIndex === u.physicalLineIndex);
		for (let [f, p] of r.entries()) {
			let m = d(p, f), h = m && f !== 0 ? {
				...p,
				ascent: Math.max(p.ascent, T),
				visibleAscent: Math.max(p.visibleAscent ?? p.ascent, T),
				...u.inlinePictureTextSingle === void 0 ? {} : { inlinePictureTextSingle: Math.max(p.inlinePictureTextSingle ?? 0, u.inlinePictureTextSingle) }
			} : p, g = s.textMarkerFirstLineUnionMode15, _ = s.textMarkerKeepsBodyDescent, v = (f === 0 || g && r[0]?.physicalLineIndex !== void 0 && p.physicalLineIndex === r[0].physicalLineIndex) && !a && (g || !n.wrap) && !t.lineGrid.active && (t.lineSpacing == null || g && t.lineSpacing.rule === "atLeast" || t.lineSpacing.rule === "auto" && t.lineSpacing.value >= 1) && !t.hasRuby && !h.uniformPositionAuto && !h.inlinePictureTextSingle ? i.firstLineNumberingMarkerBox : void 0, y = v?.ascentPt, b = v?.descentPt, x = _ ? y !== void 0 && Number.isFinite(y) && y > h.ascent ? {
				...h,
				ascent: y,
				visibleAscent: Math.max(h.visibleAscent ?? h.ascent, y)
			} : h : y !== void 0 && b !== void 0 && Number.isFinite(y) && Number.isFinite(b) ? {
				...h,
				ascent: Math.max(h.ascent, y),
				descent: Math.max(h.descent, b),
				visibleAscent: Math.max(h.visibleAscent ?? h.ascent, y),
				visibleDescent: Math.max(h.visibleDescent ?? h.descent, b),
				intendedSingle: Math.max(h.intendedSingle, v?.intendedSinglePt ?? 0),
				visibleIntendedSingle: Math.max(h.visibleIntendedSingle ?? h.intendedSingle, v?.intendedSinglePt ?? 0)
			} : h, S = Math.max(h.ascent + h.descent, h.intendedSingle), C = _ ? x.ascent + x.descent : Math.max(x.ascent + x.descent, v?.intendedSinglePt ?? 0), w = x !== h && C > S, D = E ? oh(x, t, e, s, i.verticalPageFrame === !0, i.paragraphMarkShapeInput, w ? C : void 0) : null, O = m && T >= x.ascent ? Math.max(x.gridCountSingle, x.ascent + x.descent) : void 0, k = D ? D.advancePt : w && t.lineSpacing?.rule !== "atLeast" ? C + S * ((t.lineSpacing?.value ?? 1) - 1) : t.hasRuby ? c : xf(t.lineSpacing, x.ascent, x.descent, 1, o, !1, x.intendedSingle, x.eastAsian ?? !1, O ?? x.gridCountSingle, void 0, x.uniformPositionAuto, x.inlinePictureTextSingle, x.latinGridCountSingle);
			t.lineGrid.active && (t.lineSpacing == null || t.lineSpacing.rule === "auto") && x.ascent + x.descent >= x.intendedSingle && (x.segments.some((e) => "imagePath" in e && !e.anchor && e.heightPt >= x.ascent) || m && T >= x.ascent) && (k = uh(k, o)), l.push({
				layout: x,
				advancePt: k
			});
		}
		return {
			allocations: l,
			uniformRubyAdvancePt: c
		};
	}, O = n.wrap ? {
		startPageY: y,
		preservePre15AnchorLine: s.preservePre15AnchorLine,
		resolveLineAdvances: (e) => D(e).allocations.map((e) => e.advancePt),
		paraX: u,
		columnXPt: n.paragraphXPt,
		columnWidthPt: n.availableWidthPt,
		floats: [],
		paragraphMarkLineStartWidth: hs(af(e), 1),
		hasExclusions: n.wrap.hasExclusions,
		...i.numberingFirstLine && !a ? { numberingFirstLine: i.numberingFirstLine } : {},
		lineWindow: (e) => n.wrap.lineWindow(e),
		lineBoxH: (e, n, r, i, a, s, c, l, u) => xf(t.lineSpacing, e, n, 1, o, t.hasRuby, i ?? 0, t.hasRuby ? t.hasEastAsianText : a ?? !1, s, void 0, c, l, u),
		pageH: n.maximumYPt
	} : void 0, k = hr(e.alignment, s, t.baseRtl, t.wordWrap !== !1, t.baseRtl ? t.physicalIndentLeftPt : t.physicalIndentRightPt + c), A = !t.runDirectionUnauthored && gr(e, s, t.baseRtl, t.wordWrap !== !1, i.verticalCJK !== !0 && (i.pageWritingMode === void 0 || i.pageWritingMode === "horizontal-tb")), j = Mm(r.context, w, l, a ? 0 : t.firstIndentPt, 1, [...t.tabStops], O, m, t.physicalIndentLeftPt, t.kinsoku, o, t.defaultTabPt, l + t.physicalIndentRightPt + c, t.baseRtl, t.isJustified, t.stretchLastLine, a?.boundary, n.noWrap ? "unwrapped" : void 0, i.verticalGlyphMeasurement, t.overflowPunct !== !1, (xr(e.alignment, s) || fh(e)) && i.verticalCJK !== !0 && (e.alignment !== "distribute" && e.alignment !== "lowKashida" || !t.baseRtl && !Si(w)) ? {
		lineEndIdeographicSpaceHangs: e.wordWrap !== !1,
		admissionOnly: e.alignment === "distribute" || e.alignment === "lowKashida"
	} : !1, A && k ? {
		...k,
		rtlVisiblePrefix: !1
	} : k, t.cjkClosingMarkHang, {
		alignment: e.alignment,
		runDirectionUnauthored: t.runDirectionUnauthored,
		lineEndJustificationBeforeMode15: s.lineEndJustificationBeforeMode15,
		doNotExpandShiftReturn: s.doNotExpandShiftReturn,
		endsAtHardBreak: t.endsAtHardBreak
	}, t.lineEdgeRules);
	if (j.length === 0) return C();
	let { allocations: M, uniformRubyAdvancePt: N } = D(j), P = [], F, I = y;
	for (let { layout: e, advancePt: t } of M) {
		let r = e.wrapAllocation;
		if (n.wrap && (!r || r.physicalLineIndex !== e.physicalLineIndex || r.topYPt !== e.topY || r.advancePt !== t)) throw new Wo("INVALID_GEOMETRY", "line origin does not own its allocated advance");
		let i = e.physicalLineIndex !== void 0 && e.physicalLineIndex === F, a = r?.topYPt ?? (i ? I : y);
		F = e.physicalLineIndex, I = a, P.push({
			layout: e,
			topYPt: a,
			advancePt: t
		}), y = a + t;
	}
	let L = P[P.length - 1], R;
	if (i.retainSourceRunBoundaries) {
		let t = /* @__PURE__ */ new Map(), n = w.map((e) => {
			let n = e.sourceRunIndex;
			if (n === void 0 || !("text" in e)) throw Error("Unsupported note source window segment");
			let r = t.get(n) ?? 0;
			return t.set(n, r + e.text.length), r;
		});
		R = P.map(({ layout: r }) => {
			let i = r.consumedEnd;
			if (!i) throw Error("Note source window omitted its consumed boundary");
			let a = w[i.segIndex];
			if (!a) return {
				runIndex: e.runs.length,
				offset: 0
			};
			let o = a.sourceTextSequence;
			if (o) {
				let e = (a.sourceTextOffset ?? 0) + i.charOffset, t = 0, n = o.length;
				for (; t < n;) {
					let r = Math.floor((t + n) / 2);
					o[r].end <= e ? t = r + 1 : n = r;
				}
				let r = o[t];
				return r ? {
					runIndex: r.runIndex,
					offset: e - r.start
				} : {
					runIndex: o.at(-1).runIndex + 1,
					offset: 0
				};
			}
			let s = a.sourceRunIndex, c = n[i.segIndex] + i.charOffset;
			return c >= t.get(s) ? {
				runIndex: s + 1,
				offset: 0
			} : {
				runIndex: s,
				offset: c
			};
		});
	}
	return {
		...R ? { lineEndSourceRuns: R } : {},
		lines: P,
		markOnly: !1,
		requestedSpaceBeforePt: d,
		requestedSpaceAfterPt: f,
		uniformRubyAdvancePt: N,
		contentStartYPt: P[0].topYPt,
		contentEndYPt: y,
		lastLineBelowBaselinePt: kf(L.advancePt, L.layout.ascent, L.layout.descent),
		placement: p
	};
}
function fh(e) {
	let t = e.alignment;
	return e.__justifiedCompression === !0 && (t === "both" || t === "justify" || t === "distribute");
}
function ph(e, t) {
	let n = e < 0n ? -e : e, r = t < 0n ? -t : t;
	for (; r !== 0n;) [n, r] = [r, n % r];
	return n === 0n ? 1n : n;
}
function mh(e, t) {
	if (t === 0n) throw RangeError("Exact length denominator must not be zero");
	let n = t < 0n ? -1n : 1n, r = ph(e, t);
	return Object.freeze({
		numerator: n * e / r,
		denominator: n * t / r
	});
}
var hh = 768, gh = 1100;
function _h(e) {
	let t = /^([+-]?)(?:(\d+)(?:\.(\d*))?|\.(\d+))(?:[eE]([+-]?\d+))?$/.exec(e);
	if (!t) return null;
	let n = t[1] === "-", r = t[2] ?? "", i = t[3] ?? t[4] ?? "", a = Number(t[5] ?? "0");
	if (!Number.isSafeInteger(a)) return null;
	let o = `${r}${i}`, s = 0;
	for (; s < o.length && o.charCodeAt(s) === 48;) s += 1;
	if (s === o.length) return mh(0n, 1n);
	let c = o.length - 1;
	for (; c > s && o.charCodeAt(c) === 48;) --c;
	let l = o.slice(s, c + 1), u = o.length - 1 - c, d = a - i.length + u, f = d + l.length - 1;
	if (l.length > hh || Math.abs(f) > gh) return null;
	let p = BigInt(l), m = 1n;
	return d >= 0 ? p *= 10n ** BigInt(d) : m = 10n ** BigInt(-d), n && (p = -p), mh(p, m);
}
function vh(e) {
	let t = /^(-?\d+)\/([1-9]\d*)$/.exec(e);
	if (!t) throw RangeError(`Invalid exact length key: ${e}`);
	return mh(BigInt(t[1]), BigInt(t[2]));
}
function yh(e) {
	let t = mh(e.numerator, e.denominator);
	return `${t.numerator}/${t.denominator}`;
}
function bh(e) {
	let t = _h(e);
	return t ? yh(t) : null;
}
function xh(e) {
	if (!Number.isFinite(e) || e < 0) return null;
	let t = _h(e.toString());
	return t ? yh(t) : null;
}
function Sh(e, t) {
	let n = e.toString(2).length - t.toString(2).length;
	return (n >= 0 ? e < t << BigInt(n) : e << BigInt(-n) < t) && --n, n;
}
function Ch(e, t, n) {
	let r = n >= 0 ? e << BigInt(n) : e, i = n < 0 ? t << BigInt(-n) : t, a = r / i, o = r % i * 2n - i;
	return o > 0n || o === 0n && a % 2n != 0n ? a + 1n : a;
}
function wh(e) {
	let t = vh(e);
	if (t.numerator === 0n) return 0;
	let n = t.numerator < 0n, r = n ? -t.numerator : t.numerator, i = Sh(r, t.denominator), a;
	if (i < -1022) {
		let e = Ch(r, t.denominator, 1074);
		a = Number(e) * Number.MIN_VALUE;
	} else {
		let e = Ch(r, t.denominator, 52 - i);
		e === 1n << 53n && (e >>= 1n, i += 1), a = i > 1023 ? Infinity : Number(e) * 2 ** (i - 52);
	}
	return n ? -a : a;
}
function Th(e, t) {
	let n = vh(e), r = vh(t);
	return yh(mh(n.numerator * r.denominator + r.numerator * n.denominator, n.denominator * r.denominator));
}
function Eh(e, t) {
	let n = vh(e), r = vh(t);
	return yh(mh(n.numerator * r.numerator, n.denominator * r.denominator));
}
function Dh(e, t) {
	let n = vh(e), r = vh(t);
	return yh(mh(n.numerator * r.denominator - r.numerator * n.denominator, n.denominator * r.denominator));
}
function Oh(e, t) {
	if (t === 0n) throw RangeError("Exact length divisor must not be zero");
	let n = vh(e);
	return yh(mh(n.numerator, n.denominator * t));
}
function kh(e, t) {
	let n = vh(e), r = vh(t), i = n.numerator * r.denominator - r.numerator * n.denominator;
	return i < 0n ? -1 : +(i > 0n);
}
var X = 1e-9;
function Ah(e, t, n, r, i = !1) {
	let a = Number.isFinite(e) ? Math.max(0, e) : 0, o = Math.max(0, t), s = o + Math.max(1, n);
	return {
		startPt: (o === 0 ? a : a / 2) * (i && a > 0 ? 2 : 1),
		endPt: (s >= Math.max(0, r) ? a : a / 2) * (i && a > 0 ? 2 : 1)
	};
}
function jh(e) {
	return typeof e == "number" && Number.isFinite(e) ? Math.max(0, e) : 0;
}
function Mh(e) {
	return e.map((e) => Math.abs(e) <= X ? 0 : e);
}
function Nh(e) {
	let t = e.gridWidthsPt.length;
	for (let n of e.rows) {
		for (let e of n.cells) t = Math.max(t, e.columnStart + Math.max(1, e.columnSpan));
		let e = n.cells.reduce((e, t) => Math.max(e, t.columnStart + Math.max(1, t.columnSpan)), n.before?.columnSpan ?? 0);
		t = Math.max(t, e + (n.after?.columnSpan ?? 0));
	}
	return t;
}
function Ph(e, t, n) {
	let r = 0, i = Math.min(e.length, t + Math.max(1, n));
	for (let n = Math.max(0, t); n < i; n += 1) r += e[n] ?? 0;
	return r;
}
function Fh(e, t) {
	return e ? e.kind === "pct" ? jh(e.value) * t : jh(e.value) : null;
}
function Ih(e, t, n, r) {
	let i = Math.max(0, t), a = Math.max(1, Math.min(n, e.length - i));
	if (a <= 0) return;
	let o = Ph(e, i, a);
	if (o <= X) {
		e[i + a - 1] = r;
		return;
	}
	let s = r / o;
	for (let t = i; t < i + a; t += 1) e[t] = (e[t] ?? 0) * s;
}
function Lh(e, t, n, r) {
	let i = Math.max(0, t), a = Math.max(1, Math.min(n, e.length - i));
	if (a <= 0) return;
	let o = Ph(e, i, a);
	r <= o + X || (e[i + a - 1] += r - o);
}
function Rh(e, t) {
	let n = [];
	e.before && e.before.columnSpan > 0 && n.push({
		start: 0,
		span: e.before.columnSpan,
		preferred: e.before.preferredWidth
	});
	for (let t of e.cells) n.push({
		start: t.columnStart,
		span: t.columnSpan,
		preferred: t.preferredWidth
	});
	return e.after && e.after.columnSpan > 0 && n.push({
		start: Math.max(0, t - e.after.columnSpan),
		span: e.after.columnSpan,
		preferred: e.after.preferredWidth
	}), n;
}
function zh(e, t) {
	let n = Array.from({ length: t }, (t, n) => jh(e.gridWidthsPt[n] ?? 0)), r = n.reduce((e, t) => e + t, 0), i = e.tablePreferredWidthPt ?? (r > 0 ? r : jh(e.availableWidthPt));
	e.rows.forEach((e, r) => {
		for (let a of Rh(e, t)) {
			let e = Fh(a.preferred, i);
			e !== null && (r === 0 ? Ih(n, a.start, a.span, e) : Lh(n, a.start, a.span, e));
		}
	}), e.tablePreferredWidthPt === null && Bh(n, e.rows);
	let a = e.tablePreferredWidthPt, o = n.reduce((e, t) => e + t, 0);
	if (a !== null && a >= 0 && o <= X && n.length > 0) return n.map(() => a / n.length);
	if (a !== null && a >= 0 && o > X) {
		if (e.layout === "autofit" && a < o) {
			let r = e.rows.flatMap((e) => e.cells);
			if (r.some((e) => e.noWrap === !0 && e.preferredWidth?.kind === "dxa")) {
				let { minimums: i } = Vh(e.rows, t, o);
				return Jh(n, i, r, a, 0);
			}
		}
		let r = a / o;
		return n.map((e) => e * r);
	}
	return n;
}
function Bh(e, t) {
	let n = Array(e.length).fill(0);
	for (let r of t) for (let t of r.cells) {
		if (t.columnSpan !== 1 || t.preferredWidth?.kind !== "pct") continue;
		let r = t.columnStart;
		r < 0 || r >= e.length || (n[r] = Math.max(n[r] ?? 0, jh(t.preferredWidth.value)));
	}
	let r = e.reduce((e, t) => e + t, 0), i = n.map((t, n) => t * r > e[n] + X), a = /* @__PURE__ */ new Set();
	for (; i.some(Boolean);) {
		let t = i.map((e) => e ? "1" : "0").join("");
		if (a.has(t)) return;
		a.add(t);
		let o = 0, s = 0;
		for (let t = 0; t < e.length; t += 1) i[t] ? s += n[t] ?? 0 : o += e[t] ?? 0;
		if (s >= 1 - X) return;
		r = o / (1 - s);
		let c = n.map((t, n) => t * r > e[n] + X);
		if (c.every((e, t) => e === i[t])) {
			for (let t = 0; t < e.length; t += 1) i[t] && (e[t] = n[t] * r);
			return;
		}
		i = c;
	}
}
function Vh(e, t, n) {
	let r = Array(t).fill(0), i = Array(t).fill(0);
	for (let n of e) for (let e of n.cells) e.columnSpan !== 1 || e.columnStart < 0 || e.columnStart >= t || (r[e.columnStart] = Math.max(r[e.columnStart] ?? 0, jh(e.minContentWidthPt)), i[e.columnStart] = Math.max(i[e.columnStart] ?? 0, jh(e.maxContentWidthPt)));
	let a = Array(t).fill(!1);
	for (let o of e) for (let e of o.cells) {
		let o = e.columnStart;
		if (e.columnSpan !== 1 || o < 0 || o >= t || a[o] || e.preferredWidth === null) continue;
		let s = Fh(e.preferredWidth, n);
		s !== null && (i[o] = Math.max(r[o] ?? 0, s), a[o] = !0);
	}
	for (let e = 0; e < t; e += 1) i[e] = Math.max(r[e] ?? 0, i[e] ?? 0);
	return {
		minimums: r,
		maximums: i
	};
}
function Hh(e, t, n, r, i) {
	let a = Math.min(e.length, n + r), o = e.map((e, t) => t).filter((e) => e < n || e >= a), s = o.map((n) => Math.max(0, e[n] - (t[n] ?? 0))), c = s.reduce((e, t) => e + t, 0), l = Math.min(i, c);
	return l <= X || c <= X ? 0 : (o.forEach((t, n) => {
		e[t] -= l * ((s[n] ?? 0) / c);
	}), l);
}
function Uh(e, t, n, r) {
	if (r <= X || n <= 0) return;
	let i = Ph(e, t, n);
	for (let a = 0; a < n; a += 1) {
		let o = t + a, s = i > X ? (e[o] ?? 0) / i : 1 / n;
		e[o] += r * s;
	}
}
function Wh(e) {
	let t = Nh(e);
	if (e.layout === "fixed") {
		let n = zh(e, t).reduce((e, t) => e + t, 0);
		return Object.freeze({
			minWidthPt: n,
			maxWidthPt: n
		});
	}
	let n = Array(t).fill(0), r = Array(t).fill(0), i = e.rows.flatMap((e) => e.cells).sort((e, t) => e.columnSpan - t.columnSpan), a = (e, t, n) => {
		let r = Math.max(0, t.columnStart), i = Math.max(1, Math.min(t.columnSpan, e.length - r));
		if (i <= 0) return;
		let a = jh(n) - Ph(e, r, i);
		a > X && Uh(e, r, i, a);
	};
	for (let e of i) a(n, e, e.minContentWidthPt), a(r, e, Math.max(e.minContentWidthPt, e.maxContentWidthPt));
	let o = n.reduce((e, t) => e + t, 0), s = Math.max(o, r.reduce((e, t) => e + t, 0));
	return Object.freeze({
		minWidthPt: o,
		maxWidthPt: s
	});
}
function Gh(e, t, n, r, i) {
	let a = Math.max(0, i.columnStart), o = Math.max(1, Math.min(i.columnSpan, e.length - a));
	if (o <= 0) return;
	let s = jh(i.minContentWidthPt), c = Ph(e, a, o);
	if (s <= c + X) return;
	let l = o === 1 ? r[a] ?? s : Math.max(s, jh(i.maxContentWidthPt));
	Uh(e, a, o, Hh(e, n, a, o, Math.max(0, l - c)));
	let u = Ph(e, a, o);
	if (u < s - X) {
		Uh(e, a, o, Hh(e, t, a, o, s - u));
		let n = Ph(e, a, o);
		n < s - X && Uh(e, a, o, s - n);
	}
}
function Kh(e, t, n) {
	let r = [...t];
	for (let t of n) {
		if (t.noWrap !== !0 || t.preferredWidth?.kind !== "dxa") continue;
		let n = Math.max(0, t.columnStart), i = Math.max(1, Math.min(t.columnSpan, e.length - n)), a = Ph(e, n, i);
		if (a <= X) continue;
		let o = jh(t.preferredWidth.value);
		for (let t = n; t < n + i; t += 1) r[t] = Math.max(r[t] ?? 0, e[t] * o / a);
	}
	return r;
}
function qh(e, t, n, r, i, a) {
	let o = e.map(() => !1);
	for (let t of r) t.preferredWidth === null && t.columnSpan === 1 && t.columnStart >= 0 && t.columnStart < e.length && (o[t.columnStart] = !0);
	for (let t of r) {
		if (t.preferredWidth === null && t.columnSpan === 1) continue;
		let n = Math.max(0, t.columnStart), r = Math.min(e.length, n + Math.max(1, t.columnSpan));
		for (let e = n; e < r; e += 1) o[e] = !1;
	}
	let s = 0, c = 0;
	for (let e of i) s = Math.max(s, e.before?.columnSpan ?? 0), c = Math.max(c, e.after?.columnSpan ?? 0);
	for (let t = 0; t < Math.min(e.length, s); t += 1) o[t] = !1;
	for (let t = Math.max(0, e.length - c); t < e.length; t += 1) o[t] = !1;
	let l = e.length === 2 && o.every(Boolean);
	l && e.forEach((t, r) => {
		e[r] = Math.min(t, n[r] ?? t);
	});
	let u = e.map((e, t) => o[t] ? Math.max(0, (n[t] ?? 0) - e) : 0), d = u.reduce((e, t) => e + t, 0);
	if (d <= X) return;
	if (u.filter((e) => e > X).length > 1) {
		if (!l) return;
		let r = t.reduce((e, t) => e + t, 0);
		if (r > a) return;
		let i = n.map((e, n) => Math.max(0, e - (t[n] ?? 0))), o = i.reduce((e, t) => e + t, 0);
		if (o <= X) return;
		let s = Math.min(1, (a - r) / o);
		e.forEach((n, r) => {
			e[r] = (t[r] ?? 0) + s * i[r];
		});
		return;
	}
	let f = a - e.reduce((e, t) => e + t, 0);
	if (f <= X) return;
	let p = Math.min(f, d);
	u.forEach((t, n) => {
		e[n] = (e[n] ?? 0) + p * t / d;
	});
}
function Jh(e, t, n, r, i) {
	let a = e.reduce((e, t) => e + t, 0);
	if (a <= r + X || a <= X) return e;
	let o = [...e], s = Kh(o, t, n), c = (e, t) => {
		let n = o.map((t, n) => Math.max(0, t - (e[n] ?? 0))), r = n.reduce((e, t) => e + t, 0), i = Math.min(t, r);
		return i <= X || r <= X ? 0 : (o.forEach((e, t) => {
			o[t] -= i * ((n[t] ?? 0) / r);
		}), i);
	}, l = a - r;
	c(t, l - c(s, l));
	for (let e of n) {
		if (e.columnSpan <= 1) continue;
		let n = Math.max(0, e.columnStart), r = Math.max(1, Math.min(e.columnSpan, o.length - n)), i = jh(e.minContentWidthPt) - Ph(o, n, r);
		if (i <= X) continue;
		let a = Hh(o, s, n, r, i), c = a + Hh(o, t, n, r, i - a);
		Uh(o, n, r, c), c < i - X && Uh(o, n, r, i - c);
	}
	let u = o.reduce((e, t) => e + t, 0);
	if (u <= r + X || u <= X) return Mh(o);
	let d = n.find((e) => e.noWrap === !0 && e.preferredWidth === null && e.columnSpan === 1);
	if (i > X && (d?.minContentWidthPt ?? 0) > r - i + X && o.length === 2 && n.length === 2 && n.every((e) => e.columnSpan === 1) && n.some((e) => e.columnStart === 0) && n.some((e) => e.columnStart === 1) && d && n.filter((e) => e.noWrap === !0).length === 1) {
		let e = [0, 0];
		for (let t of n) e[t.columnStart] = jh(t.horizontalMarginsPt);
		let t = o.map((t, n) => Math.max(0, t - (e[n] ?? 0))), a = t.reduce((e, t) => e + t, 0);
		if (a > X) {
			let e = Math.max(0, r - i), n = t.map((t) => t * e / a), o = d.columnStart, s = 1 - o;
			return n[o] += i * (t[s] ?? 0) / a, n[s] += i * (t[o] ?? 0) / a, Mh(n);
		}
	}
	let f = Math.max(0, r) / u;
	return Mh(o.map((e) => e * f));
}
function Yh(e) {
	let t = Nh(e), n = e.separatedCellSpacingPt ?? 0;
	if (e.layout !== "autofit" || n <= 0 || t === 0 || e.growUnpreferredColumns !== "nonbinding" || !e.rows.every((e) => e.before === null && e.after === null && e.cells.length === t && e.cells.every((e, t) => e.columnSpan === 1 && e.columnStart === t && e.preferredWidth === null))) return null;
	let { maximums: r } = Vh(e.rows, t, 0), i = r.reduce((e, t) => e + t, 0), a = (t + 1) * 2 * n;
	return i + a <= (e.availableWidthPt ?? 0) && i + a < (e.contentBandPt ?? 0) ? r : null;
}
function Xh(e) {
	let t = Nh(e);
	if (t === 0) return Object.freeze([]);
	let n = e.separatedCellSpacingPt ?? 0;
	if (n > 0) {
		let r = (t + 1) * 2 * n, i = {
			...e,
			separatedCellSpacingPt: void 0
		}, a;
		if (e.layout === "fixed") {
			let e = Xh(i), t = e.reduce((e, t) => e + t, 0);
			if (t <= r) return e;
			a = e.map((e) => e * (t - r) / t);
		} else {
			let t = Yh(e);
			if (!t) return Xh(i);
			a = t;
		}
		return Object.freeze(a.map((e, r) => {
			let i = Ah(n, r, 1, t, !0);
			return e + i.startPt + i.endPt;
		}));
	}
	let r = zh(e, t);
	if (e.layout === "fixed") {
		if (e.availableWidthPt === null) return Object.freeze(r);
		let t = r.reduce((e, t) => e + t, 0), n = jh(e.availableWidthPt);
		if (t <= n + X || t <= X) return Object.freeze(r);
		let i = n / t;
		return Object.freeze(Mh(r.map((e) => e * i)));
	}
	let i = r.reduce((e, t) => e + t, 0), { minimums: a, maximums: o } = Vh(e.rows, t, i), s = e.rows.flatMap((e) => e.cells);
	s.sort((e, t) => e.columnSpan - t.columnSpan);
	let c = Kh(r, a, s);
	for (let e of s) Gh(r, a, c, o, e);
	let l = o.reduce((e, t) => e + t, 0), u = l <= jh(e.availableWidthPt) + X && e.contentBandPt !== void 0 && l < jh(e.contentBandPt) - X;
	return (e.growUnpreferredColumns === !0 || e.growUnpreferredColumns === "nonbinding" && u) && e.tablePreferredWidthPt === null && qh(r, a, o, s, e.rows, jh(e.availableWidthPt)), Object.freeze(Jh(r, a, s, jh(e.availableWidthPt), jh(e.outerMarginAllowancePt)));
}
function Zh(e) {
	let t = Xh(e), n = t.map((t, n) => {
		let r = t !== e.gridWidthsPt[n];
		return !r && e.gridWidthKeys?.[n] === null ? null : !r && e.gridWidthKeys?.[n] !== void 0 ? e.gridWidthKeys[n] : xh(t) ?? "0/1";
	});
	return Object.freeze({
		widthsPt: Object.freeze([...t]),
		widthKeys: Object.freeze(n)
	});
}
function Qh(e) {
	return Zh(e).widthsPt;
}
function $h(e, t) {
	if (e === null) return null;
	let n = e.trim(), r = t && n.endsWith("%") ? n.slice(0, -1) : n;
	if (r.length === 0) return null;
	let i = Number(r);
	return Number.isFinite(i) ? i : null;
}
function eg(e) {
	return e.value?.trim().endsWith("%") ? "pct" : e.kind ?? "dxa";
}
function tg(e) {
	if (!e) return null;
	let t = e.value?.trim() ?? "", n = eg(e);
	if (n === "dxa") {
		let t = $h(e.value ?? "0", !1);
		return t === null ? null : {
			kind: "dxa",
			value: t / 20
		};
	}
	if (n !== "pct") return null;
	let r = $h(e.value ?? "0", !0);
	return r === null ? null : {
		kind: "pct",
		value: t.endsWith("%") ? r / 100 : r / 5e3
	};
}
function ng(e) {
	let t = tg(e);
	return t?.kind === "dxa" ? t.value : null;
}
function rg(e, t) {
	let n = t ? tg(t) : e.widthPt == null ? e.widthPct == null ? null : {
		kind: "pct",
		value: e.widthPct / 5e3
	} : {
		kind: "dxa",
		value: e.widthPt
	};
	return n?.value === 0 ? null : n;
}
function ig(e, t) {
	let n = e.format.firstRowException?.preferredWidth ?? null;
	if (e.format.firstRowException?.preferredWidthAuthored) return n?.kind === "dxa" ? n.value > 0 ? n.value : null : n?.kind === "pct" && n.value > 0 ? n.value * t : null;
	let r = tg(e.lexical.table?.preferredWidth);
	return r?.kind === "dxa" ? r.value > 0 ? r.value : null : r?.kind === "pct" ? r.value > 0 ? r.value * t : null : e.semantic.widthPt != null && e.semantic.widthPt > 0 ? e.semantic.widthPt : e.semantic.widthPct != null && e.semantic.widthPct > 0 ? e.semantic.widthPct / 5e3 * t : null;
}
function ag(e) {
	if (e.format.firstRowException?.preferredWidthAuthored) {
		let t = e.format.firstRowException.preferredWidth;
		return t?.kind === "dxa" && t.value > 0 ? t.value : null;
	}
	let t = tg(e.lexical.table?.preferredWidth);
	return t ? t.kind === "dxa" && t.value > 0 ? t.value : null : e.semantic.widthPt != null && e.semantic.widthPt > 0 ? e.semantic.widthPt : null;
}
var og = Object.freeze({
	pt: "1/1",
	in: "72/1",
	cm: "3600/127",
	mm: "360/127",
	pc: "12/1",
	pi: "12/1"
}), sg = "18446744073709551615";
function cg(e) {
	let t = e.replace(/[\u0009\u000a\u000d\u0020]+/g, " ").replace(/^ | $/g, ""), n = /^([+-]?)([0-9]+)$/.exec(t);
	if (!n) return null;
	let [, r, i] = n;
	if (r === "-" && /[1-9]/.test(i)) return null;
	let a = i.replace(/^0+/, "") || "0";
	return a.length > 20 || a.length === 20 && a > sg ? null : t;
}
var lg = {
	key: "0/1",
	widthPt: 0
};
function ug(e) {
	let t = wh(e);
	return Number.isFinite(t) ? {
		key: e,
		widthPt: t
	} : lg;
}
function dg(e, t) {
	let n = Number(e);
	if (!Number.isFinite(n)) return lg;
	let r = xh(n), i = r === null ? 0 : wh(Eh(r, t));
	return Number.isFinite(i) ? {
		key: null,
		widthPt: i
	} : lg;
}
function fg(e) {
	if (e == null) return lg;
	let t = cg(e);
	if (t !== null) {
		let e = bh(t);
		return e === null ? lg : ug(Oh(e, 20n));
	}
	let n = /^([0-9]+(?:\.[0-9]+)?)(mm|cm|in|pt|pc|pi)$/.exec(e);
	if (!n) return lg;
	let r = og[n[2]], i = bh(n[1]);
	return i === null ? dg(n[1], r) : ug(Eh(i, r));
}
function pg(e) {
	let t = e.lexical.table?.grid;
	if (!t) {
		let t = e.semantic.colWidths.map((e) => Number.isFinite(e) && e >= 0 ? {
			widthPt: e,
			key: xh(e) ?? "0/1"
		} : lg);
		return {
			widthsPt: t.map((e) => e.widthPt),
			widthKeys: t.map((e) => e.key)
		};
	}
	let n = Math.max(t.requiredColumnCount, t.columns.length), r = Array.from({ length: n }, (e, n) => fg(t.columns[n]?.width ?? null));
	return {
		widthsPt: r.map((e) => e.widthPt),
		widthKeys: r.map((e) => e.key)
	};
}
function mg(e, t) {
	let n = tg(e);
	return n?.kind === "pct" ? {
		kind: "dxa",
		value: Math.max(0, n.value) * Math.max(0, t)
	} : n;
}
function hg(e, t, n, r = t, i) {
	let a = e.semantic, { widthsPt: o, widthKeys: s } = pg(e), c = e.format.firstRowException?.layout === "fixed" ? "fixed" : e.lexical.table?.layout?.kind ?? a.layout, l = e.lexical.table?.grid.authored ? e.lexical.table.grid.columns.length : null, u = a.rows.map((e) => {
		let t = Math.max(0, e.gridBefore ?? 0);
		return l !== null && t > l ? 0 : t;
	}), d = Math.max(l ?? 0, e.lexical.table?.grid.requiredColumnCount ?? 0, ...a.rows.map((e, t) => (u[t] ?? 0) + e.cells.reduce((e, t) => e + Math.max(1, t.colSpan), 0)));
	return {
		layout: c === "fixed" ? "fixed" : "autofit",
		...i ? { separatedCellSpacingPt: i.spacingPt } : {},
		availableWidthPt: r === null ? null : Math.max(0, r),
		gridWidthsPt: o,
		gridWidthKeys: s,
		tablePreferredWidthPt: ig(e, t),
		rows: a.rows.map((r, a) => {
			let s = e.lexical.rows[a], f = u[a] ?? 0, p = Math.max(0, r.gridAfter ?? 0), m = f + r.cells.reduce((e, t) => e + Math.max(1, t.colSpan), 0), h = l !== null && m + p > d ? 0 : p, g = f;
			return {
				before: f > 0 ? {
					columnSpan: f,
					preferredWidth: mg(s?.row?.beforeWidth, t)
				} : null,
				after: h > 0 ? {
					columnSpan: h,
					preferredWidth: mg(s?.row?.afterWidth, t)
				} : null,
				cells: r.cells.map((t, r) => {
					let l = s?.cells[r] ?? null, u = Math.max(1, t.colSpan), d = rg(t, l?.preferredWidth), f = c === "fixed" ? {
						minWidthPt: 0,
						maxWidthPt: 0
					} : n(a, r, d), p = Ah(e.format.rows[a]?.cellSpacingPt ?? 0, g, u, o.length), m = i ? 2 * i.borderPt : p.startPt + p.endPt, h = e.format.rows[a]?.cells[r]?.marginsPt, _ = Math.max(0, h?.left ?? 0) + Math.max(0, h?.right ?? 0), v = {
						columnStart: g,
						columnSpan: u,
						preferredWidth: d,
						...t.noWrap ? { noWrap: !0 } : {},
						..._ > 0 ? { horizontalMarginsPt: _ } : {},
						minContentWidthPt: Math.max(0, f.minWidthPt) + m,
						maxContentWidthPt: Math.max(f.minWidthPt, f.maxWidthPt) + m
					};
					return g += u, v;
				})
			};
		})
	};
}
function gg(e) {
	let t = e.leadingIndentPt + e.authoredFirstIndentPt + e.markerShiftPt;
	return {
		startPt: t,
		endPt: t + e.markerWidthPt
	};
}
function _g(e) {
	let t = e.authoredFirstIndentPt + e.markerShiftPt;
	return e.baseRtl ? e.alignedLeadingEdgePt - t - e.markerWidthPt : e.alignedLeadingEdgePt + t;
}
function vg(e, t) {
	let { numbering: n, markerInput: r, service: i } = t, a = n != null && (n.text !== "" || n.picBulletImagePath != null) && (!e.baseRtl || (n?.suff || "tab") === "tab" && t.authoredFirstIndentPt < 0);
	if (!n || !r || !i || !a) return e;
	let o = xg(n, r, {
		authoredFirstIndentPt: t.authoredFirstIndentPt,
		physicalIndentLeftPt: e.physicalIndentLeftPt,
		tabStops: t.tabStops,
		defaultTabPt: t.defaultTabPt ?? e.defaultTabPt,
		...t.compat ? { compat: t.compat } : {},
		baseRtl: e.baseRtl
	}, i, t.clusterGeometry ?? !0);
	return {
		...e,
		firstIndentPt: o.bodyOffsetPt,
		numberingMarkerGeometry: o
	};
}
function yg(e, t, n, r, i = !0) {
	if (!r) return null;
	let a = r.shape({
		text: t,
		fontSizePt: e.fontSizePt * n,
		fonts: e.fonts,
		themeFonts: e.themeFonts,
		themeFontPresence: e.themeFontPresence,
		weight: e.weight,
		style: e.style,
		complexScript: e.complexScript,
		fontHint: e.fontHint,
		eastAsiaLanguage: e.eastAsiaLanguage,
		kerning: e.kerning ?? !1,
		measure: !0,
		clusterGeometry: i
	}), o = ad(r.fontMetrics ?? r.localMetrics ?? {}), s = 0, c = 0, l = 0;
	for (let t of a.spans) {
		let { resourceMetric: i, referenceMetric: a, lineMetric: u } = Yu(t.font, od(o, t.font, t.text), !0, md(o, t.font), {
			text: r,
			probe: t.text
		}), d = i?.lineHeightRatio == null ? a : i, f = d?.designAscentRatio != null && d.designDescentRatio != null;
		s = Math.max(s, f ? d.designAscentRatio * e.fontSizePt * n : t.ascentPt), c = Math.max(c, f ? d.designDescentRatio * e.fontSizePt * n : t.descentPt);
		let p = t.script === "eastAsia" ? u?.eastAsianLineHeightRatio ?? u?.lineHeightRatio : u?.lineHeightRatio;
		l = Math.max(l, (p ?? 0) * e.fontSizePt * n);
	}
	let u = Object.freeze(a.spans.length > 0 ? {
		ascentPt: s,
		descentPt: c,
		intendedSinglePt: l
	} : {
		ascentPt: a.ascentPt,
		descentPt: a.descentPt,
		intendedSinglePt: 0
	});
	return {
		shape: a,
		fontSizePx: e.fontSizePt * n,
		lineBox: u
	};
}
function bg(e, t, n) {
	return t.find((t) => Kr(e, t)) ?? ys(e, [...t], n);
}
function xg(e, t, n, r, i = !0) {
	let a = e.fontFamily ?? t.fonts.ascii ?? null, o = [t.fonts, t.themeFonts].flatMap((e) => e ? [
		e.ascii,
		e.highAnsi,
		e.eastAsia,
		e.complexScript
	] : []), s = {
		fonts: t.fonts,
		themeFonts: t.themeFonts,
		themeFontPresence: t.themeFontPresence,
		weight: t.weight,
		style: t.style,
		complexScript: t.complexScript,
		fontHint: t.fontHint,
		eastAsiaLanguage: t.eastAsiaLanguage
	}, c = r.scalarFamily ? [...e.text].every((e) => ee(r.scalarFamily(s, e))) : o.some(ee), l = !e.picBulletImagePath && [a, ...o].some(ee), u = c || !l || !ee(a) ? t : {
		...t,
		fonts: {
			ascii: a,
			highAnsi: a,
			eastAsia: a,
			complexScript: a
		},
		themeFonts: void 0,
		themeFontPresence: void 0
	}, d = {
		...s,
		fonts: u.fonts,
		themeFonts: u.themeFonts,
		themeFontPresence: u.themeFontPresence
	}, f = l ? r.symbolText?.({
		...d,
		text: e.text
	}) ?? z(e.text, a) : [{
		text: e.text,
		mapped: !1
	}], p = f.map((e) => e.text).join(""), m = (e, t) => [...t].some((t) => r.symbolDraws?.(e, t) === !0), h = f.some((e) => e.mapped), g = h && !f.some((e) => !e.mapped && m(d, e.text)), _ = e.picBulletImagePath ? "" : g || !h ? p : [...e.text].map((e) => {
		let t = r.symbolText?.({
			...d,
			text: e
		});
		return t?.length === 1 && !t[0].mapped ? t[0].text : e;
	}).join(""), v = _ ? yg(g ? [..._].every((e) => e.codePointAt(0) > 255 && e !== "︎") && r.symbolMonochrome?.(s, _) !== !1 ? t : {
		...t,
		fonts: {
			ascii: null,
			highAnsi: null,
			eastAsia: null,
			complexScript: null
		},
		themeFonts: void 0,
		themeFontPresence: void 0
	} : u, _, 1, r, i) ?? null : null, y = v?.shape ?? null, b = e.picBulletImagePath ? e.picBulletWidthPt ?? t.fontSizePt : y?.advancePt ?? 0, x = e.jc === "right" ? -b : e.jc === "center" ? -b / 2 : 0, S = n.authoredFirstIndentPt + x + b, C = e.suff || "tab", w = S;
	if (C === "space") {
		let a = Gr({
			compat: n.compat ?? ql,
			leftToRight: n.baseRtl === !1,
			markerWeight: t.weight,
			markerStyle: t.style,
			complexScriptMarker: t.complexScript,
			symbolMarker: _ !== e.text || /[\uE000-\uF8FF]/u.test(e.text)
		}) ? {
			...t,
			fonts: {
				ascii: "Arial",
				highAnsi: "Arial",
				eastAsia: "Arial",
				complexScript: "Arial"
			},
			themeFonts: void 0,
			themeFontPresence: void 0
		} : t;
		w += yg(a, " ", 1, r, i)?.shape.advancePt ?? 0;
	} else if (C === "tab" && (w = 0, S > 0)) {
		let e = n.suffixFrameOriginPt, t = e === void 0 ? bg(n.physicalIndentLeftPt + S, n.tabStops, n.defaultTabPt) : bg(n.physicalIndentLeftPt + S - e, [...n.tabStops, {
			pos: Math.max(n.physicalIndentLeftPt, e) - e,
			alignment: "num",
			leader: "none"
		}], n.defaultTabPt);
		w = t ? t.pos + (e ?? 0) - n.physicalIndentLeftPt : S;
	}
	return w = Math.max(0, w), {
		bodyOffsetPt: w,
		markerText: _,
		markerWidthPt: b,
		markerShiftPt: x,
		shape: y,
		...v ? { lineBox: v.lineBox } : {}
	};
}
function Sg(e) {
	return {
		textAnchor: "cell-start",
		widthBasis: "host-cell-content",
		leftFromTextPt: e.hSpace,
		rightFromTextPt: e.hSpace,
		topFromTextPt: e.vSpace,
		bottomFromTextPt: e.vSpace,
		horzAnchor: e.hAnchor,
		horzSpecified: !0,
		vertAnchor: e.vAnchor,
		xPt: e.x ?? 0,
		yPt: e.y ?? 0,
		...e.xAlign == null ? {} : { xAlign: e.xAlign },
		...e.yAlign == null ? {} : { yAlign: e.yAlign }
	};
}
function Cg(e) {
	let t = e.blocks[0]?.layout;
	if (e.columnStart !== 0 || e.vAlign !== "top" || e.verticalMerge !== "none" || e.verticalText || t?.kind !== "paragraph" || t.clipBounds || t.cellContainmentBounds || t.lines.length !== 1 || t.resources.length !== 0 || t.textBoxes.length !== 0 || t.events.length !== 0 || t.exclusions.length !== 0 || t.drawings.length !== 1 || t.anchorFrames?.length !== 1) return !1;
	let n = t.anchorFrames[0];
	return n.status === "resolved" && n.axes.vertical.relativeFrom === "paragraph" && n.geometry.wrap.kind === "none" && t.lines[0].placements.every((e) => e.kind === "anchor-host" && e.anchorOccurrenceId === n.occurrenceId || e.kind === "drawing" && e.advancePt === 0);
}
function wg(e) {
	let t = e.runs.filter((e) => e.type === "shape"), n = t.length === 1 ? t[0]?.anchorAcquisitionInput : void 0;
	return e.numbering == null && n !== void 0 && n.vertical.relativeFrom === "paragraph" && n.wrap.kind === "none" && n.behavior.allowOverlap === !0 && n.behavior.layoutInCell === !0 && e.runs.every((e) => e.type === "shape" || e.type === "anchorHost" && e.anchorOccurrenceId === n.occurrenceId);
}
function Tg(e) {
	return e.runs.length === 0 && e.numbering == null;
}
function Eg(e) {
	let t = e.story, n = t === "body" || t === "header" || t === "footer" || t === "footnote" || t === "textbox", r = e.topLevel || t === "body" && e.tableCellDepth === 1;
	return e.compat.tableOriginPlacementMode && n && r && !e.verticalText && e.commonFrame && e.marginClass && !e.outerEdgeIndent && e.ordinaryFlow && !e.positioned && !e.rowOverrides && !e.gridSkips && !e.unfittedContentSizedAutoFit;
}
function Dg(e) {
	let t = e.rows.length <= 1, n = e.rows.every((e) => e.cells.length <= 1), r = Object.entries(e.borders ?? {}).filter(([e]) => !(e === "insideH" && t) && !(e === "insideV" && n)).map(([, e]) => !e || e.style === "nil" || e.style === "none" ? 0 : e.style === "single" && Number.isFinite(e.width) ? e.width : null);
	return r.some((e) => e === null || e !== r[0]) || e.rows.some((e) => e.cells.some((e) => Object.values(e.borders).some((e) => e != null) || e.vMerge != null || e.textDirection != null && e.textDirection !== "lrTb" || e.content.some((e) => e.type === "table"))) ? null : r[0] ?? 0;
}
function Og(e) {
	let t = e.justification == null || e.justification === "left" || e.justification === "start", n = e.justification === "center", r = t ? e.indentPt : 0;
	if (e.compat.tableMode15Geometry) {
		let i = (n ? 0 : (t === e.bidi ? -1 : 1) * e.borderPt / 2) - (e.bidi ? e.borderPt / 2 : 0);
		return r + (e.bidi ? -i : i);
	}
	if (n || t && !e.indentAuthored) return r;
	let i = t ? e.leadingMarginPt : e.trailingMarginPt, a = (e.bidi ? e.spacingPt : 2 * e.spacingPt) + e.borderPt + i;
	return r + (t ? -a : a);
}
function kg(e) {
	let t = e.story;
	return !e.compat.tableOriginPlacementMode || !e.topLevel || e.verticalText || !e.commonFrame || !e.marginClass || e.spacing || e.outerEdgeIndent || !e.ordinaryFlow || e.positioned || e.rowOverrides || e.gridSkips ? "none" : t === "body" || t === "header" || t === "footer" || t === "footnote" ? "all" : t === "textbox" ? "leading" : "none";
}
function Ag(e) {
	return e.compatibility === "word" && e.availableHeightPt + e.epsilonPt < e.freshPageHeightPt;
}
function jg(e, t) {
	return Math.max(0, e ?? 0) + Math.max(0, ...t);
}
function Mg(e, t, n) {
	return (e ? 0 : Math.max(0, t)) + Math.max(0, n);
}
function Ng(e) {
	return e != null && e !== "none";
}
function Pg(e, t, n) {
	return n ? e - t : e + t;
}
function Fg(e) {
	return e.spacingPt > 0 && !Ng(e.directStyle) && Ng(e.conditionalInsideStyle);
}
function Ig(e, t) {
	let n = Math.min(e.xPt, t.xPt), r = Math.max(e.xPt + e.widthPt, t.xPt + t.widthPt);
	return Object.freeze({
		xPt: n,
		yPt: e.yPt,
		widthPt: r - n,
		heightPt: e.heightPt
	});
}
function Lg(e) {
	return e.compatibility === "word" && e.availableHeightPt + e.epsilonPt >= e.freshPageHeightPt;
}
function Rg(e) {
	return e.compatibility === "word" && !e.repeatedHeader && (e.heightRule === "exact" || e.heightRule === "atLeast") && e.authoredHeightPt !== null && (e.heightRule === "exact" || e.wholeHeightPt <= e.authoredHeightPt + e.epsilonPt) && e.authoredHeightPt > e.availableHeightPt + e.epsilonPt && e.wholeHeightPt <= e.freshAvailableHeightPt + e.epsilonPt;
}
function zg(e) {
	return e.compatibility === "word" && e.hasUnfinishedParagraphWithoutProgress;
}
var Bg = Object.freeze([
	"single",
	"thick",
	"double",
	"dotted",
	"dashed",
	"dotDash",
	"dotDotDash",
	"triple",
	"thinThickSmallGap",
	"thickThinSmallGap",
	"thinThickThinSmallGap",
	"thinThickMediumGap",
	"thickThinMediumGap",
	"thinThickThinMediumGap",
	"thinThickLargeGap",
	"thickThinLargeGap",
	"thinThickThinLargeGap",
	"wave",
	"doubleWave",
	"dashSmallGap",
	"dashDotStroked",
	"threeDEmboss",
	"threeDEngrave",
	"outset",
	"inset"
]), Vg = Object.freeze({
	single: 1,
	thick: 2,
	double: 3,
	dotDash: 8,
	dotDotDash: 9,
	triple: 10,
	thinThickSmallGap: 11,
	thickThinSmallGap: 12,
	thinThickThinSmallGap: 13,
	thinThickMediumGap: 14,
	thickThinMediumGap: 15,
	thinThickThinMediumGap: 16,
	thinThickLargeGap: 17,
	thickThinLargeGap: 18,
	thinThickThinLargeGap: 19,
	wave: 20,
	doubleWave: 21,
	dashSmallGap: 22,
	dashDotStroked: 23,
	threeDEmboss: 24,
	threeDEngrave: 25,
	outset: 26,
	inset: 27
});
function Hg(t, n) {
	return t === "dotted" || t === "dashed" ? 1 : Math.max(0, n) * 8 * (e(Vg, t) ?? 0);
}
function Ug(e, t) {
	return t ? e : "atLeast";
}
function Wg(e, t) {
	return e === "pct" || e === "auto" || e === "nil" ? 0 : t;
}
function Gg(e) {
	return e.kind === "dxa" ? e.dxaValuePt : e.scope === "cell" || e.scope === "exception" ? null : (e.edge === "start" || e.edge === "end") && (e.kind === "pct" || e.kind === "auto" || e.kind === "nil") ? 0 : null;
}
function Kg(e) {
	return e.measured && (e.justification === "center" || e.justification === "right" || e.justification === "end") ? 0 : e.indentPt;
}
function qg(e) {
	let t = Kg({
		...e,
		measured: e.measured || e.nonleadingIndentIgnored === !0
	});
	return !e.measured || e.justification === "center" ? t : e.justification === "right" || e.justification === "end" ? t + (e.compat.tableMode15Geometry ? 0 : e.rowLeftMarginPt) : t - (!e.compat.tableMode15Geometry && e.indentAuthored ? e.firstLeftMarginPt : 0);
}
function Jg(e, t, n) {
	return !t.tableOriginMeasuredMode || !n || e.layout !== "fixed" || e.rows.length === 0 || !e.rows.every((e) => e.cells.length > 0 && e.cells[0]?.columnStart === 1 && e.after === null && e.cells.every((e) => e.columnSpan === 1 && e.preferredWidth?.kind === "dxa" && e.preferredWidth.value > 0)) ? e : {
		...e,
		gridWidthsPt: e.gridWidthsPt.map((e, t) => t === 0 ? 0 : e),
		gridWidthKeys: e.gridWidthKeys?.map((e, t) => t === 0 ? null : e),
		rows: e.rows.map((e) => ({
			...e,
			before: null
		}))
	};
}
function Yg(e) {
	return e === "body" || e === "header" || e === "footer";
}
function Xg(e) {
	let t = e.cells[0]?.content[0];
	return t?.type !== "paragraph" || !t.framePr || t.framePr.dropCap !== "none" ? null : t.framePr;
}
function Zg(e) {
	return Oe("w:framePr:owner-run", [
		e.hAnchor,
		e.vAnchor,
		e.x ?? null,
		e.xAlign ?? null,
		e.y ?? null,
		e.yAlign ?? null,
		e.w ?? null,
		e.h ?? null,
		e.hRule,
		e.wrap,
		e.hSpace,
		e.vSpace
	]);
}
function Qg(e, t, n, r = "autofit", i = rg(e)) {
	let a = 0, o = 0, s = 0;
	for (let t of e.content) {
		let e = t.type === "paragraph" && Tg(t), r = t.type === "paragraph" ? e ? {
			minWidthPt: 0,
			maxWidthPt: 0
		} : n.paragraph(t) : n.nestedTable(t);
		a = Math.max(a, r.minWidthPt), o = Math.max(o, r.maxWidthPt), s = Math.max(s, r.noWrapWidthPt ?? r.maxWidthPt);
	}
	let c = Math.max(0, t.left) + Math.max(0, t.right);
	return {
		minWidthPt: (r === "autofit" && e.noWrap === !0 && i?.kind !== "dxa" ? s : a) + c,
		maxWidthPt: Math.max(a, o) + c
	};
}
function $g(e) {
	let t = e.textShapeRequest, n = (e) => e ? [
		e.ascii ?? null,
		e.highAnsi ?? null,
		e.eastAsia ?? null,
		e.complexScript ?? null
	] : null;
	return JSON.stringify([
		t ? [
			n(t.fonts),
			n(t.themeFonts),
			t.themeFontPresence ? [
				t.themeFontPresence.ascii ?? !1,
				t.themeFontPresence.highAnsi ?? !1,
				t.themeFontPresence.eastAsia ?? !1,
				t.themeFontPresence.complexScript ?? !1
			] : null,
			t.fontHint ?? null,
			t.fontSizePt,
			t.weight ?? null,
			t.style ?? null,
			t.complexScript ?? !1,
			t.eastAsiaLanguage ?? null,
			t.eastAsiaFontCharset ?? null,
			t.genericFamily ?? null,
			t.letterSpacingPt ?? null,
			t.kerning ?? null
		] : null,
		e.bold,
		e.italic,
		q(e, 1),
		e.fontFamily,
		e.fontRoute ? [e.fontRoute.familyList, e.fontRoute.scope] : null,
		e.charScale ?? 1,
		e.charSpacing ?? 0,
		e.fitTextPerGapPx ?? null,
		e.fitTextTrailingPadPx ?? null,
		e.fitTextRegionIndex ?? null,
		e.snapToCharacterGrid !== !1,
		e.widthBalanceGridDeltaFactor ?? null,
		e.widthBalanceSpaceSequence ?? !1,
		e.widthBalanceSpaceAdjustmentPt ?? null,
		e.script ?? null,
		e.tateChuYoko ?? !1,
		e.tateChuYoko ? e.sourceRunIndex ?? null : null,
		e.ruby ? [
			e.sourceRunIndex ?? null,
			e.ruby.text,
			e.ruby.fontSizePt,
			e.ruby.hpsRaisePt ?? null
		] : null,
		e.verticalRun ?? !1
	]);
}
function e_(e, t) {
	return (e.textLayoutService?.fingerprint ?? null) === (t.textLayoutService?.fingerprint ?? null) && $g(e) === $g(t);
}
function t_(e, t) {
	let n = e.textShapeRequest?.substituteContext, r = t.textShapeRequest?.substituteContext;
	return n !== void 0 && r !== void 0 && n.text === r.text && n.offset + e.text.length === r.offset;
}
function n_(e, t) {
	let n = [], r, i;
	for (let a of e) {
		let e = n.at(-1);
		if (e && "text" in e && "text" in a && Mc(e, a) && !e.optionalHyphen && !a.optionalHyphen && !(a.hardJoinPrev && e.optionalHyphenBreaks?.at(-1)?.offset === e.text.length) && !e.semanticSlotSpans && !a.semanticSlotSpans && a.autoSpaceBeforePt === void 0 && !(a.textShapeRequest?.kerning === !0 && e.text.endsWith(" ") !== a.text.startsWith(" ") && (e.script !== a.script || !vl(e, a, 1) || fl(e, t) !== null || fl(a, t) !== null || il(e, t, 1) || il(a, t, 1))) && !(a.textShapeRequest?.kerning === !0 && (e.sourceRunIndex !== a.sourceRunIndex || e.sourceTextSequence !== a.sourceTextSequence)) && e_(e, a) && (e.substituteScope === void 0 && a.substituteScope === void 0 || e.textShapeRequest?.substituteContext?.text === a.textShapeRequest?.substituteContext?.text && e.textShapeRequest?.substituteContext !== void 0 && a.textShapeRequest?.substituteContext?.offset === e.textShapeRequest.substituteContext.offset + e.text.length)) {
			let t = e.text.length, o = e.text + a.text;
			if (a.explicitBreakBefore || a.explicitBreaks) {
				r ??= [], a.explicitBreakBefore && r.push(t);
				for (let e of pc(a.explicitBreaks)) r.push(t + e);
			}
			if (a.optionalHyphenBreaks) {
				i ??= [];
				for (let e of a.optionalHyphenBreaks) i.push({
					...e,
					offset: t + e.offset
				});
			}
			let s = [...e.punctuationCompressions ?? [], ...(a.punctuationCompressions ?? []).map((e) => ({
				end: t + e.end,
				adjustmentPt: e.adjustmentPt
			}))];
			n[n.length - 1] = {
				...e,
				text: o,
				explicitBreaks: r ? dc(r) : void 0,
				optionalHyphenBreaks: i,
				punctuationCompressions: s.length > 0 ? s : void 0,
				textShapeRequest: e.textShapeRequest ? {
					...e.textShapeRequest,
					text: o,
					substituteContext: e.substituteScope !== void 0 || a.substituteScope !== void 0 || e.textShapeRequest.kerning === !0 && t_(e, a) ? e.textShapeRequest.substituteContext : {
						text: o,
						offset: 0
					}
				} : void 0
			};
			continue;
		}
		r && Object.freeze(r), i && Object.freeze(i), i = "text" in a && a.optionalHyphenBreaks ? [...a.optionalHyphenBreaks] : void 0, n.push({
			...a,
			..."text" in a && i ? { optionalHyphenBreaks: i } : {}
		}), r = "text" in a && a.explicitBreaks ? [...pc(a.explicitBreaks)] : void 0;
	}
	return r && Object.freeze(r), i && Object.freeze(i), n;
}
function r_(e, t, n, r, i, a, o) {
	let s = 0, c, l, u, d = null, f = a?.type === "snapToChars" && a.characterPitchPt != null && a.characterPitchPt > 0 ? a.characterPitchPt : null, p = () => {
		!d || f == null || (s += pl(d.naturalWidthPt, d.kind, f), d = null);
	}, m = 0, h = e.length;
	for (; m < h;) {
		let t = Math.floor((m + h) / 2);
		e[t].end <= n ? m = t + 1 : h = t;
	}
	function* g() {
		for (let t = m; t < e.length && e[t].start < r; t++) yield e[t];
		o && (yield {
			segment: o,
			start: r,
			end: r + o.text.length
		});
	}
	for (let e of g()) {
		let m = e.segment === o, h = Math.max(n, e.start), g = m ? e.end : Math.min(r, e.end);
		if (h >= g) continue;
		let _ = m ? o.text : t.slice(h, g), v = h - e.start, y = g - e.start, x = {
			...e.segment,
			text: _,
			...J(e.segment, v, y),
			punctuationCompressions: qc(e.segment, v, y)
		};
		u && (u.semanticSlotSpans || x.semanticSlotSpans) && (c ??= new yl(i.context, 1, (e) => tf(e.bold, e.italic, q(e, 1), e.fontFamily, i.fontFamilyClasses, e.fontRoute)), s += c.wordBoundaryAdvance(u, x)), u = x;
		let S = (e) => {
			l ??= new yl(i.context, 1, (e) => tf(e.bold, e.italic, q(e, 1), e.fontFamily, i.fontFamilyClasses, e.fontRoute));
			let t = l.condensedAdvanceUnits(e, e.text, 0, a, () => {});
			return e.textLayoutService && e.textShapeRequest ? dl(e, e.textLayoutService.shape({
				...e.textShapeRequest,
				fontSizePt: q(e, 1),
				measure: !0,
				clusterGeometry: !1
			}).advancePt, a, 1, t) : (i.context.font = tf(e.bold, e.italic, q(e, 1), e.fontFamily, i.fontFamilyClasses, e.fontRoute), dl(e, i.context.measureText(e.text).width, a, 1, t));
		}, C = fl(x, a);
		if (C === "eastAsia" && f != null) {
			p();
			let e = x.textLayoutService && x.textShapeRequest ? x.textLayoutService.shape({
				...x.textShapeRequest,
				fontSizePt: q(x, 1),
				measure: !0,
				clusterGeometry: !0
			}).clusters : void 0, t = e?.length ? null : [...new Set([
				0,
				...b(_),
				_.length
			])].sort((e, t) => e - t), n = e?.map((e) => ({
				start: e.range.start,
				end: e.range.end,
				naturalWidthPt: dl({
					...x,
					text: _.slice(e.range.start, e.range.end),
					punctuationCompressions: qc(x, e.range.start, e.range.end)
				}, e.advancePt, a, 1)
			})) ?? t.slice(0, -1).map((e, n) => {
				let r = t[n + 1];
				return {
					start: e,
					end: r,
					naturalWidthPt: S({
						...x,
						text: _.slice(e, r),
						...x.textShapeRequest ? { textShapeRequest: ks(x.textShapeRequest, e, r) } : {},
						punctuationCompressions: qc(x, e, r)
					})
				};
			}), r = 0;
			for (let e of n) e.end <= e.start || (r += ur(e.naturalWidthPt, f));
			s += pl(n.reduce((e, t) => e + t.naturalWidthPt, 0), C, f, Math.max(1, r));
		} else {
			let e = S(x);
			if ((C === "latin" || C === "complexScript") && f != null) {
				let t = d;
				t?.kind === C ? d = {
					kind: C,
					naturalWidthPt: t.naturalWidthPt + e
				} : (p(), d = {
					kind: C,
					naturalWidthPt: e
				});
			} else p(), s += e;
		}
	}
	return p(), s;
}
function i_(e, t, n) {
	let r = 0;
	return o_(e, t, n, (e) => (r = Math.max(r, e), !1)), r;
}
function a_(e, t, n, r) {
	let i = ch(n)?.type === "snapToChars", a = [];
	for (let t = 0; t < e.length; t += 1) {
		let o = e[t];
		if (!("isTab" in o)) continue;
		let s;
		!o.ptab && gc(e[t + 1], e[t + 2], i, n.baseRtl) && (s = 0, o_([e[t + 1]], n, r, (e) => (s = e, !0))), a.push(s);
	}
	return a.length === t.filter((e) => "isTab" in e).length ? a : [];
}
function o_(e, t, n, r) {
	let i = ch(t);
	for (let a = 0; a < e.length; a += 1) {
		let o = e[a];
		if (!("text" in o) || o.text.length === 0) continue;
		let s = [], c = "", l = (e) => {
			let t = c.length;
			c += e.text, s.push({
				segment: e,
				start: t,
				end: c.length
			});
		};
		for (l(o); a + 1 < e.length;) {
			let t = e[a + 1];
			if (!("text" in t) || t.joinPrev !== !0) break;
			l(t), a += 1;
		}
		let u = s.flatMap((e) => [...pc(e.segment.explicitBreaks)].map((t) => e.start + t)), d = c.search(/\S/u), f = new Map(s.flatMap((e, n) => (e.segment.optionalHyphen ? [{
			offset: 0,
			glyph: e.segment.optionalHyphen
		}] : e.segment.optionalHyphenBreaks ?? []).filter((r) => qp(e.segment, r.offset, s[n + 1]?.segment, d >= 0 && e.start + r.offset > d, t.kinsoku)).map((t) => [e.start + t.offset, t.glyph]))), p = [...f.keys()].sort((e, t) => e - t), m = 0, h = 0, g = 0;
		for (let e of uc(c)) {
			let a = e.replace(/\s+$/u, ""), o = g, l = g + a.length;
			if (g += e.length, !a) continue;
			if (!tc(a)) {
				let e = [];
				for (; h < u.length && u[h] <= o;) h += 1;
				for (; h < u.length && u[h] < l;) e.push(u[h++]);
				for (; m < p.length && p[m] <= o;) m += 1;
				for (; m < p.length && p[m] < l;) e.push(p[m++]);
				e.push(l), e.sort((e, t) => e - t);
				let t = o;
				for (let a of new Set(e)) {
					if (r(r_(s, c, t, a, n, i, f.get(a)))) return;
					t = a;
				}
				continue;
			}
			let d = [
				0,
				...b(a),
				a.length
			], _ = [];
			for (let e = 1; e < d.length; e += 1) _.push({
				text: a.slice(d[e - 1], d[e]),
				start: o + d[e - 1],
				end: o + d[e]
			});
			let v = [], y = _[0];
			for (let e = 1; e < _.length; e += 1) {
				let n = [...y.text].at(-1)?.codePointAt(0), r = _[e].text.codePointAt(0);
				n !== void 0 && r !== void 0 && !t.kinsoku.lineEndForbidden.has(n) && !t.kinsoku.lineStartForbidden.has(r) ? (v.push(y), y = _[e]) : y = {
					text: y.text + _[e].text,
					start: y.start,
					end: _[e].end
				};
			}
			y && v.push(y);
			for (let e of v) if (r(r_(s, c, e.start, e.end, n, i))) return;
		}
	}
}
function s_(e, t, n) {
	let r = (n.baseRtl ? n.physicalIndentRightPt : n.physicalIndentLeftPt) + (t === 0 ? n.firstIndentPt : 0) + e.xOffset;
	return {
		startPt: r,
		endPt: r + e.segments.reduce((e, t) => e + t.measuredWidth, 0)
	};
}
function c_(e, t, n, r, i, a, o = {}) {
	if (!Number.isFinite(n) || n < 0) throw RangeError("maximumWidthPt must be finite and non-negative");
	if (n === 0) return {
		minWidthPt: 0,
		maxWidthPt: 0
	};
	let s = Td(e.runs, {
		...i,
		closingPairAdvanceAdmitted: au(e, t, i),
		uprightResourceOrientation: Um(i.verticalPageFrame, i.pageWritingMode),
		lineSpacing: t.lineSpacing,
		lineGridActive: t.lineGrid.active,
		characterGridActive: t.characterGrid.active,
		paragraphRtl: t.baseRtl,
		autoSpaceDE: e.autoSpaceDE,
		autoSpaceDN: e.autoSpaceDN
	}), c = n_(s, ch(t)), l = a_(s, c, t, r), u = Math.max(1, n - t.physicalIndentLeftPt - t.physicalIndentRightPt), d = c.length === 0 ? [] : Mm(r.context, c, u, t.firstIndentPt, 1, [...t.tabStops], void 0, r.fontFamilyClasses, t.physicalIndentLeftPt, t.kinsoku, ch(t), t.defaultTabPt, u + t.physicalIndentRightPt, t.baseRtl, t.isJustified, t.stretchLastLine, void 0, "intrinsic", i.verticalGlyphMeasurement, t.overflowPunct !== !1, !1, void 0, t.cjkClosingMarkHang), f = t.baseRtl ? t.physicalIndentLeftPt : t.physicalIndentRightPt, p = 0, m = 0;
	d.forEach((e, n) => {
		let r = s_(e, n, t);
		p = Math.min(p, r.startPt), m = Math.max(m, r.endPt);
	});
	let h = a ? gg({
		leadingIndentPt: t.baseRtl ? t.physicalIndentRightPt : t.physicalIndentLeftPt,
		authoredFirstIndentPt: e.indentFirst,
		markerShiftPt: a.markerShiftPt,
		markerWidthPt: a.markerWidthPt
	}) : void 0;
	h && (p = Math.min(p, h.startPt), m = Math.max(m, h.endPt));
	let g = i_(c, t, r), _ = 0;
	for (let e of d) {
		let n = 0, r = e.segments.reduce((e, t) => e + t.measuredWidth, 0);
		for (let i of e.segments) if (n += i.measuredWidth, "imagePath" in i && !i.anchor) g = Math.max(g, i.measuredWidth);
		else if ("math" in i) g = Math.max(g, i.measuredWidth);
		else if ("isTab" in i) {
			let e = l[_++];
			g = Math.max(g, e !== void 0 && i.resolvedAlignment !== void 0 && yc(i.resolvedAlignment) === "leading" ? n + e : !t.baseRtl && i.resolvedAlignment === "left" ? n : r);
		}
	}
	let v = t.baseRtl ? t.physicalIndentRightPt : t.physicalIndentLeftPt, y = o.preserveWhitespaceOnlyContent && c.length > 0 && c.every((e) => "text" in e && /^[\s\u00a0]+$/u.test(e.text)) ? c : null, b = y ? (() => {
		let e = "";
		return r_(y.map((t) => {
			let n = e.length;
			return e += t.text, {
				segment: t,
				start: n,
				end: e.length
			};
		}), e, 0, e.length, r, ch(t));
	})() : 0;
	if (b > 0) {
		let e = v + t.firstIndentPt;
		p = Math.min(p, e), m = Math.max(m, e + b);
	}
	let x = Math.min(n, Math.max(0, m - p + f)), S = v, C = Math.min(0, S);
	g = Math.max(g, b);
	let w = Math.max(0, S + g), T = v + t.firstIndentPt;
	return C = Math.min(C, T), w = Math.max(w, T + g), h && (C = Math.min(C, h.startPt), w = Math.max(w, h.endPt)), {
		minWidthPt: Math.min(n, Math.max(0, w - C + f)),
		maxWidthPt: x
	};
}
function l_(e, t) {
	if (!e || t?.suppressBottom) return 0;
	let n = e.bottom;
	return !n || n.style === "none" ? 0 : (n.space ?? 0) + (n.width ?? 0) / 2;
}
function u_(e, t) {
	if (!e || t === "none") return 0;
	let n = e[t];
	return !n || n.style === "none" || n.style === "nil" ? 0 : (n.space ?? 0) + (n.width ?? 0) / 2;
}
function d_(e) {
	return e == null || e.style === "none" ? null : e;
}
function f_(e, t) {
	let n = d_(e), r = d_(t);
	return n == null || r == null ? n == null && r == null : n.style === r.style && n.width === r.width && (n.space ?? 0) === (r.space ?? 0) && (n.color ?? null) === (r.color ?? null);
}
function p_(e, t) {
	return !e || !t ? !1 : f_(e.top, t.top) && f_(e.bottom, t.bottom) && f_(e.left, t.left) && f_(e.right, t.right) && f_(e.between, t.between);
}
function m_(e) {
	return e ? [
		e.top,
		e.right,
		e.bottom,
		e.left,
		e.between
	].some((e) => e != null && e.style !== "none") : !1;
}
function h_(e, t) {
	return !e || !t || e.framePr || t.framePr ? !1 : m_(e.borders) && m_(t.borders) && p_(e.borders, t.borders);
}
function g_(e, t, n, r = !1) {
	let i = (e, t) => r ? !!e && !!t && !!e.framePr && !!t.framePr && m_(e.borders) && m_(t.borders) && p_(e.borders, t.borders) : h_(e, t), a = i(e, t), o = i(t, n), s = t.borders?.between;
	return Object.freeze({
		top: a ? s && s.style !== "none" ? "between" : "none" : "top",
		bottom: o ? "none" : "bottom"
	});
}
function __(e, t, n, r, i, a) {
	return c_(e, t, n, r, i, a).maxWidthPt;
}
function v_(e) {
	let t = e;
	return Oe("w:framePr", [
		t.dropCap,
		t.lines,
		t.wrap,
		t.hAnchor,
		t.vAnchor,
		t.hRule,
		t.hSpace,
		t.vSpace,
		t.w ?? null,
		t.h ?? null,
		t.x ?? null,
		t.y ?? null,
		t.xAlign ?? null,
		t.yAlign ?? null,
		t.__anchorLock === !0
	]);
}
function y_(e) {
	let t = /* @__PURE__ */ new WeakMap();
	for (let n = 0; n < e.length;) {
		let r = e[n];
		if (r?.type !== "paragraph" || !r.framePr) {
			n += 1;
			continue;
		}
		let i = v_(r.framePr), a = [r], o = [n], s = n + 1;
		for (; s < e.length;) {
			let t = e[s];
			if (t?.type !== "paragraph" || !t.framePr || v_(t.framePr) !== i) break;
			a.push(t), o.push(s), s += 1;
		}
		let c = Object.freeze({
			id: `${i}:${n}`,
			owner: r,
			members: Object.freeze(a),
			sourceIndices: Object.freeze(o),
			framePr: r.framePr
		});
		for (let e of a) t.set(e, c);
		n = s;
	}
	return t;
}
var b_ = /* @__PURE__ */ new WeakMap(), x_ = /* @__PURE__ */ new WeakMap();
function S_(e) {
	let t = y_(e);
	for (let n = 0; n < e.length; n += 1) {
		let r = e[n];
		if (r.type !== "paragraph") continue;
		let i = t.get(r);
		i && b_.set(r, i);
		let a = e[n - 1], o = e[n + 1], s = a?.type === "paragraph" && t.get(a) === i ? a : null, c = o?.type === "paragraph" && t.get(o) === i ? o : null;
		x_.set(r, g_(i ? s : a?.type === "paragraph" ? a : null, r, i ? c : o?.type === "paragraph" ? o : null, i !== void 0));
	}
}
var C_ = (e) => b_.get(e), w_ = (e) => x_.get(e);
function T_(e) {
	return e.textDirection == null || e.textDirection === "lrTb";
}
function E_(e, t) {
	return {
		story: e.story,
		containers: [...e.containers, { kind: "tableCell" }],
		lineNumberingEligible: !1,
		...e.quarterTurned ? { quarterTurned: !0 } : {},
		...e.closingMarkHangAdmitted && e.story === "body" && t ? { closingMarkHangAdmitted: !0 } : {}
	};
}
function D_(e) {
	if (!e.closingMarkHangAdmitted) return e;
	let { closingMarkHangAdmitted: t, ...n } = e;
	return n;
}
function O_(e) {
	return e.runs.some((e) => e.type === "text" && !!e.ruby);
}
function k_(e) {
	return e.runs.some((e) => e.type === "text" && vs.test(e.text));
}
function A_(e) {
	for (let t of e) {
		if (t.type === "paragraph") {
			if (k_(t)) return !0;
			continue;
		}
		if (t.type === "table") {
			for (let e of t.rows) for (let t of e.cells) if (A_(t.content)) return !0;
		}
	}
	return !1;
}
function j_(e, t = { normalStyleFontSizePt: 10 }) {
	return S_(e.body), {
		kinsoku: oe(e.settings),
		...e.settings?.noLineBreaksBefore !== void 0 || e.settings?.noLineBreaksAfter !== void 0 ? { hasCustomKinsokuRules: !0 } : {},
		defaultTabPt: hc(e.settings),
		characterSpacingControl: e.settings?.characterSpacingControl,
		mathDefJc: e.settings?.mathDefJc,
		documentHasEastAsianText: A_(e.body),
		normalStyleFontSizePt: t.normalStyleFontSizePt,
		compat: Kl(e.settings)
	};
}
function M_(e) {
	let t = e.pageWidth - e.marginLeft - e.marginRight, n = e.columns;
	if (!n || n.count <= 1) return [{
		xPt: e.marginLeft,
		wPt: Math.max(1, t)
	}];
	if (!n.equalWidth && n.cols.length > 0) {
		let t = [], r = e.marginLeft;
		for (let e of n.cols) t.push({
			xPt: r,
			wPt: Math.max(1, e.widthPt)
		}), r += e.widthPt + e.spacePt;
		return t;
	}
	let r = Math.max(1, (t - (n.count - 1) * n.spacePt) / n.count);
	return Array.from({ length: n.count }, (t, i) => ({
		xPt: e.marginLeft + i * (r + n.spacePt),
		wPt: r
	}));
}
function N_(e) {
	switch (e) {
		case "lines":
		case "linesAndChars":
		case "snapToChars": return e;
		default: return "none";
	}
}
function P_(e) {
	return e === void 0 ? {} : { cjkClosingMarkHang: e };
}
function F_(e) {
	if (e.cjkClosingMarkHang === void 0) return e;
	let { cjkClosingMarkHang: t, ...n } = e;
	return n;
}
function I_(e) {
	return e === "lines" || e === "linesAndChars" || e === "snapToChars";
}
function L_(e) {
	return e === "linesAndChars" || e === "snapToChars";
}
function R_(e, t, n) {
	return {
		geometry: {
			pageWidth: t.pageWidth,
			pageHeight: t.pageHeight,
			marginTop: t.marginTop,
			marginRight: t.marginRight,
			marginBottom: t.marginBottom,
			marginLeft: t.marginLeft,
			headerDistance: t.headerDistance,
			footerDistance: t.footerDistance
		},
		columns: M_(t),
		columnSeparator: t.columns?.sep === !0,
		grid: {
			kind: N_(t.docGridType),
			linePitchPt: t.docGridLinePitch ?? null,
			charSpacePt: t.docGridCharSpace == null ? null : t.docGridCharSpace / 4096
		},
		textDirection: t.textDirection ?? "lrTb",
		...n ? { sectionFlow: n } : {},
		sectionBidi: !1,
		verticalAlignment: t.vAlign ?? "top",
		lineNumbering: t.lineNumbering ?? void 0
	};
}
function z_(e) {
	return e.containers.some((e) => e.kind === "tableCell");
}
function B_(e, t, n, r) {
	let i = I_(t.grid.kind) && t.grid.linePitchPt != null && t.grid.linePitchPt > 0 && r.snapToGrid !== !1 && r.lineSpacing?.rule !== "exact" && (!z_(n) || e.compat.adjustLineHeightInTable), a = L_(t.grid.kind), o = r.bidi === !0, s = Bm(e, t, n, r), c = z_(n), l = a ? e.normalStyleFontSizePt + (t.grid.charSpacePt ?? 0) : null, u = t.grid.kind === "linesAndChars" && e.compat.gridRightIndentPitchAlignment ? l : null, d = r.numbering, f = d != null && (d.text !== "" || d.picBulletImagePath != null), p = o && f && (d.suff || "tab") === "tab" && r.indentFirst < 0;
	return {
		lineGrid: {
			active: i,
			pitchPt: i ? t.grid.linePitchPt : null
		},
		characterGrid: {
			active: a,
			kind: a ? t.grid.kind : null,
			deltaPt: a ? t.grid.charSpacePt ?? 0 : 0,
			pitchPt: l != null && l > 0 ? l : null
		},
		rightIndentGrid: {
			pitchPt: u != null && u > 0 ? u : null,
			paragraphAllowsAdjustment: r.adjustRightInd !== !1 && dr(c)
		},
		physicalIndentLeftPt: o ? r.indentRight : r.indentLeft,
		physicalIndentRightPt: o ? r.indentLeft : r.indentRight,
		firstIndentPt: p ? 0 : r.indentFirst,
		lineSpacing: r.lineSpacing,
		spaceBeforePt: r.spaceBefore,
		spaceAfterPt: r.spaceAfter,
		baseRtl: o,
		isJustified: Ni(r.alignment),
		stretchLastLine: Pi(r.alignment),
		tabStops: V_(r),
		hasRuby: O_(r),
		hasEastAsianText: k_(r),
		kinsoku: s ? zm(e.kinsoku) : e.kinsoku,
		...s ? { documentKinsoku: e.kinsoku } : {},
		...U_(Hm(e, r, s)),
		defaultTabPt: e.defaultTabPt,
		overflowPunct: r.overflowPunct !== !1,
		...P_(Vr(r.alignment, n.closingMarkHangAdmitted === !0 && r.framePr == null && r.overflowPunct !== !1 && !o && t.textDirection === "lrTb" && t.sectionFlow === void 0 && (!I_(t.grid.kind) && !a || s && r.kinsoku === !1), c, r.kinsoku === !1, e.compat.cjkClosingMarkHangProfile, e.kinsoku.enabled, s)),
		...r.wordWrap === !1 ? { wordWrap: !1 } : {},
		...r.endsAtHardBreak === !0 ? { endsAtHardBreak: !0 } : {},
		mathDefJc: e.mathDefJc
	};
}
function V_(e) {
	let t = e.__noHangingIndentTab === !0, n = e.tabStops.filter((e) => e.alignment !== "clear").map((e) => ({ ...e })), r = e.indentLeft, i = n.some((e) => e.pos === r && pr(e.alignment));
	return (e.indentFirst < 0 && !i && !t ? [{
		pos: r,
		alignment: "left",
		leader: "none"
	}, ...n] : n).sort((e, t) => e.pos - t.pos);
}
function H_(e, t) {
	let { pitchPt: n, paragraphAllowsAdjustment: r } = e.rightIndentGrid;
	return !r || n == null ? 0 : fr(t, n);
}
function U_(e) {
	return e ? { lineEdgeRules: e } : {};
}
function W_(e) {
	return e ?? 18;
}
function G_(e, t, n) {
	return e + t - n;
}
function K_(e) {
	return !e.hasContinuationBoundary && e.inkless && e.undecorated && !e.keepNext && e.markReservePt === 0 && e.pageBottomIsUnreserved && e.physicalRegionBottomIsActive ? e.followsNextPageSectionBoundary ? Math.max(0, e.markExtentPt) : e.markOnLineGrid ? e.hasFollowingInk ? e.markGridAfterLeadingPt ?? 0 : 0 : e.hasFollowingInk ? e.markBelowBaselinePt : 0 : 0;
}
function q_() {
	return "right";
}
function J_(e) {
	if (e.sectionOccurrenceId.length === 0) throw RangeError("Section occurrence id must not be empty");
	if (e.columns.length === 0) throw RangeError("A page-flow section requires at least one column");
	return Object.freeze({
		sectionOccurrenceId: e.sectionOccurrenceId,
		geometry: Object.freeze({ ...e.geometry }),
		columns: Object.freeze(e.columns.map((e) => Object.freeze({ ...e }))),
		textDirection: e.textDirection,
		...e.sectionFlow ? { sectionFlow: e.sectionFlow } : {},
		sectionBidi: e.sectionBidi ?? !1,
		grid: Object.freeze(e.grid ?? {
			kind: "none",
			linePitchPt: null,
			charSpacePt: null
		})
	});
}
function Y_(e) {
	return Z_(e.geometry.marginTop);
}
function X_(e) {
	return e.geometry.pageHeight - Z_(e.geometry.marginBottom);
}
function Z_(e) {
	return Math.abs(e);
}
function Q_(e, t) {
	if (t != null) {
		let t = nh($m("sideways-lr", {
			widthPt: e.pageWidth,
			heightPt: e.pageHeight
		}), {
			top: e.marginTop,
			right: e.marginRight,
			bottom: e.marginBottom,
			left: e.marginLeft
		});
		return {
			pageWidth: e.pageHeight,
			pageHeight: e.pageWidth,
			marginLeft: t.left,
			marginTop: t.top,
			marginRight: t.right,
			marginBottom: t.bottom,
			headerDistance: e.headerDistance,
			footerDistance: e.footerDistance
		};
	}
	return {
		pageWidth: e.pageHeight,
		pageHeight: e.pageWidth,
		marginLeft: e.marginTop,
		marginTop: e.marginRight,
		marginRight: e.marginBottom,
		marginBottom: e.marginLeft,
		headerDistance: e.headerDistance,
		footerDistance: e.footerDistance
	};
}
function $_(e, t) {
	if (t != null) {
		let t = nh(Qm("sideways-lr", {
			widthPt: e.pageHeight,
			heightPt: e.pageWidth
		}), {
			top: e.marginTop,
			right: e.marginRight,
			bottom: e.marginBottom,
			left: e.marginLeft
		});
		return {
			pageWidth: e.pageHeight,
			pageHeight: e.pageWidth,
			marginTop: t.top,
			marginRight: t.right,
			marginBottom: t.bottom,
			marginLeft: t.left,
			headerDistance: e.headerDistance,
			footerDistance: e.footerDistance
		};
	}
	return {
		pageWidth: e.pageHeight,
		pageHeight: e.pageWidth,
		marginTop: e.marginLeft,
		marginRight: e.marginTop,
		marginBottom: e.marginRight,
		marginLeft: e.marginBottom,
		headerDistance: e.headerDistance,
		footerDistance: e.footerDistance
	};
}
function ev(e) {
	return e === "tbRl" || e === "tbRlV" || e === "tbLrV" || e === "btLr";
}
function tv(e, t) {
	if (!Number.isInteger(t) || t < 0) throw RangeError("Physical page index must be a non-negative integer");
	let { pageWidth: n, pageHeight: r } = e.physicalGeometry, { marginTop: i, marginRight: a, marginBottom: o, marginLeft: s } = e.physicalGeometry, c = e.bookFoldPrinting || e.bookFoldRevPrinting;
	return c ? (n /= 2, q_() === "right" && (a += e.gutterPt)) : e.printTwoOnOne ? (r /= 2, i += e.gutterPt) : e.gutterAtTop && !e.mirrorMargins ? i += e.gutterPt : e.rtlGutter ? a += e.gutterPt : s += e.gutterPt, !c && !e.printTwoOnOne && e.mirrorMargins && t % 2 == 1 && ([s, a] = [a, s]), {
		...e.physicalGeometry,
		pageWidth: n,
		pageHeight: r,
		marginTop: i,
		marginRight: a,
		marginBottom: o,
		marginLeft: s
	};
}
function nv(e, t, n) {
	let r = tv(t, n), i = ev(t.textDirection) ? Q_(r, e.sectionFlow) : r;
	return Object.freeze({
		...e,
		geometry: Object.freeze(i),
		columns: Object.freeze(M_({
			...i,
			titlePage: !1,
			evenAndOddHeaders: !1,
			columns: t.columns
		}).map((e) => Object.freeze(e)))
	});
}
function rv(e) {
	return {
		pageWidth: e.pageWidth,
		pageHeight: e.pageHeight,
		marginTop: e.marginTop,
		marginRight: e.marginRight,
		marginBottom: e.marginBottom,
		marginLeft: e.marginLeft,
		headerDistance: e.headerDistance,
		footerDistance: e.footerDistance
	};
}
function iv() {
	return {
		pageWidth: 612,
		pageHeight: 792,
		marginTop: 72,
		marginRight: 72,
		marginBottom: 72,
		marginLeft: 72,
		headerDistance: 36,
		footerDistance: 36
	};
}
function av(e, t = !1, n) {
	let r = e.docGridType === "lines" || e.docGridType === "linesAndChars" || e.docGridType === "snapToChars" ? e.docGridType : "none";
	return Object.freeze({
		geometry: Object.freeze(rv(e)),
		columns: Object.freeze(M_(e).map((e) => Object.freeze(e))),
		columnSeparator: e.columns?.sep === !0,
		grid: Object.freeze({
			kind: r,
			linePitchPt: e.docGridLinePitch ?? null,
			charSpacePt: e.docGridCharSpace == null ? null : e.docGridCharSpace / 4096
		}),
		textDirection: e.textDirection ?? "lrTb",
		...n ? { sectionFlow: n } : {},
		sectionBidi: t,
		verticalAlignment: e.vAlign ?? "top",
		...e.lineNumbering === null || e.lineNumbering === void 0 ? {} : { lineNumbering: Object.freeze({ ...e.lineNumbering }) }
	});
}
function ov() {
	return !1;
}
var sv = class extends TypeError {}, cv = /* @__PURE__ */ new WeakSet(), lv = /* @__PURE__ */ new WeakSet();
function uv(e) {
	return lv.has(e) || cv.has(e);
}
function dv(e, t, n = /* @__PURE__ */ new WeakSet(), r = /* @__PURE__ */ new WeakSet()) {
	if (e == null || typeof e == "string" || typeof e == "boolean") return;
	if (typeof e == "number") {
		if (!Number.isFinite(e)) throw TypeError(`${t} must contain finite numbers`);
		return;
	}
	if (typeof e != "object" || n.has(e)) throw TypeError(`${t} must be structured-clone-safe plain data`);
	if (r.has(e) || cv.has(e)) return;
	let i = Object.getPrototypeOf(e);
	if (!Array.isArray(e) && i !== Object.prototype && i !== null) throw TypeError(`${t} must be structured-clone-safe plain data`);
	if (Object.getOwnPropertySymbols(e).length !== 0) throw TypeError(`${t} must contain only enumerable string data properties`);
	n.add(e);
	try {
		for (let i of Object.getOwnPropertyNames(e)) {
			if (Array.isArray(e) && i === "length") continue;
			if (Array.isArray(e) && String(Number(i)) !== i) throw TypeError(`${t}.${i} must be an array index`);
			let a = Object.getOwnPropertyDescriptor(e, i);
			if (!a || !a.enumerable || !("value" in a)) throw TypeError(`${t}.${i} must be an enumerable data property`);
			dv(a.value, `${t}.${i}`, n, r);
		}
	} finally {
		n.delete(e);
	}
	r.add(e);
}
function fv(e, t = /* @__PURE__ */ new WeakSet()) {
	let n = hv(e, t, [], !1);
	return typeof e == "object" && e && Object.isFrozen(e) && lv.add(e), n;
}
function pv(e, t, n = /* @__PURE__ */ new WeakSet()) {
	if (!lv.has(t) && !cv.has(t)) return fv(e, n);
	let r = hv(e, n, [], !0);
	return typeof e == "object" && e && Object.isFrozen(e) && lv.add(e), r;
}
function mv(e, t) {
	let n = Number(e);
	return Number.isInteger(n) && n >= 0 && n < t && String(n) === e;
}
function hv(e, t, n, r) {
	if (typeof e != "object" || !e || t.has(e)) {
		if (typeof e == "number" && !Number.isFinite(e)) throw new sv("must contain finite numbers");
		return e;
	}
	if (cv.has(e) || lv.has(e) || r && Object.isFrozen(e)) return e;
	let i = Object.isFrozen(e);
	if (i) {
		if (n.includes(e)) return e;
		n.push(e);
	} else t.add(e);
	if (Array.isArray(e)) {
		for (let i = 0; i < e.length; i += 1) hv(e[i], t, n, r);
		for (let i in e) !mv(i, e.length) && Object.prototype.hasOwnProperty.call(e, i) && hv(e[i], t, n, r);
	} else for (let i in e) Object.prototype.hasOwnProperty.call(e, i) && hv(e[i], t, n, r);
	return i ? n.pop() : Object.freeze(e), e;
}
function gv(e, t) {
	if (typeof e != "object" || !e) {
		if (typeof e == "function" || typeof e == "symbol") throw TypeError("value must be structured-clone-safe plain data");
		if (typeof e == "number" && !Number.isFinite(e)) throw new sv("must contain finite numbers");
		return e;
	}
	if (Object.isFrozen(e) && cv.has(e)) return e;
	let n = t.get(e);
	if (n !== void 0) return n;
	if (Array.isArray(e)) {
		let n = Array(e.length);
		t.set(e, n);
		for (let r = 0; r < e.length; r += 1) Object.prototype.hasOwnProperty.call(e, r) && (n[r] = gv(e[r], t));
		return Object.freeze(n), n;
	}
	let r = Object.getPrototypeOf(e);
	if (r !== Object.prototype && r !== null) throw TypeError("value must be structured-clone-safe plain data");
	let i = {};
	t.set(e, i);
	for (let n in e) if (Object.prototype.hasOwnProperty.call(e, n)) {
		let r = gv(e[n], t);
		n === "__proto__" ? Object.defineProperty(i, n, {
			value: r,
			enumerable: !0,
			writable: !0,
			configurable: !0
		}) : i[n] = r;
	}
	return Object.freeze(i), (i.kind === "paragraph" || i.kind === "table") && cv.add(i), i;
}
function Z(e, t, n) {
	if (typeof e == "object" && e && cv.has(e)) return e;
	ov() && vv(e, t);
	try {
		let t = n && (cv.has(n) || lv.has(n)) ? pv(e, n) : gv(e, /* @__PURE__ */ new Map());
		return typeof t == "object" && t && cv.add(t), t;
	} catch (e) {
		let n = e instanceof sv ? e.message : "must be structured-clone-safe plain data";
		throw TypeError(`${t} ${n}`);
	}
}
function _v(e, t) {
	ov() && vv(e, t);
	let n = fv(e);
	return typeof e == "object" && e && cv.add(e), n;
}
function vv(e, t) {
	try {
		structuredClone(e);
	} catch {
		throw TypeError(`${t} must be structured-clone-safe plain data`);
	}
	dv(e, t);
}
var yv = new Set([
	"kind",
	"id",
	"source",
	"flowDomainId",
	"ordinaryFlow",
	"sectionFlowOwnership",
	"flowBounds",
	"inkBounds",
	"clipBounds",
	"advancePt",
	"diagnostics",
	"paragraphId",
	"styleId",
	"bookmarkStarts",
	"spacing",
	"contextualSpacing",
	"lines",
	"resources",
	"events",
	"exclusions",
	"cellContainmentBounds",
	"anchorCollisions",
	"anchorFrames",
	"continuation"
]), bv = new Set([
	"range",
	"bounds",
	"baselinePt",
	"advancePt",
	"gridAfterLeadingPt",
	"pageEdgeOverhangPt",
	"placements",
	"wrapBounds",
	"wrapFragments"
]), xv = new Set([
	"kind",
	"text",
	"optionalHyphenGlyph",
	"semanticSlotSpans",
	"sourceRunIndex",
	"range",
	"origin",
	"bounds",
	"highlightBounds",
	"advancePt",
	"clusters",
	"trailingSpaceCompressionPt",
	"color",
	"fontRoute",
	"fontSizePt",
	"fontWeight",
	"fontStyle",
	"direction",
	"writingMode",
	"characterSpacingPt",
	"characterScale",
	"fitText",
	"kerning",
	"ownedTrailingSlackPt",
	"hyperlink"
]), Sv = new Set([
	"text",
	"range",
	"offset",
	"letterSpacingPt",
	"scaleX",
	"scaleY",
	"direction",
	"kerning",
	"writingMode",
	"glyphOrientation",
	"verticalFeature",
	"glyphOffsetPt",
	"sourceMapping",
	"inkBounds",
	"blockAxisInkBounds",
	"naturalAdvancePt"
]), Cv = new Set([
	"caps",
	"smallCaps",
	"strike",
	"doubleStrike",
	"verticalAlign",
	"positionPt",
	"emphasis"
]);
function wv(e, t) {
	return Object.entries(e).every(([e, t]) => t === void 0 || yv.has(e) || [
		"borders",
		"drawings",
		"textBoxes"
	].includes(e) && Array.isArray(t) && t.length === 0) && e.lines.every((e) => (e.barTabRules?.length ?? 0) === 0) && Object.entries(t).every(([e, t]) => t === void 0 || bv.has(e) || e === "barTabRules" && Array.isArray(t) && t.length === 0) && t.placements.every((e) => e.kind === "text" && Object.entries(e).every(([t, n]) => n === void 0 || xv.has(t) || (t === "paintOps" || t === "basePaintOps") && Array.isArray(n) && n.every((e) => Object.keys(e).every((e) => Sv.has(e))) || t === "role" && n === "content" || t === "sourceRuns" && e.sourceRuns?.every((e) => e.role === void 0 && e.dependency === void 0) || t === "decorations" && e.decorations.length === 0 || t === "unsupportedGeometry" && e.unsupportedGeometry?.length === 0 || t === "typography" && e.typography && Object.keys(e.typography).every((e) => Cv.has(e)) && !e.typography.strike && !e.typography.doubleStrike && e.typography.verticalAlign.status === "missing" && e.typography.positionPt.status === "missing" && e.typography.emphasis.status === "missing"));
}
function Tv(e, t, n, r, i = 0, a = 0) {
	let o = e.lines.at(-1), s = o?.gridAfterLeadingPt ?? 0;
	return s === 0 || !t || r === void 0 || i > 0 || o && e.exclusions.some(({ bounds: t, verticalOwnership: n }) => {
		let i = t.yPt + (n === "host" ? a : 0);
		return i < r && i + t.heightPt > o.bounds.yPt + a && t.xPt < e.flowBounds.xPt + e.flowBounds.widthPt && t.xPt + t.widthPt > e.flowBounds.xPt;
	}) || !o || !wv(e, o) ? n : Math.max(0, n - s);
}
function Ev(e) {
	return Math.max(0, e);
}
function Dv(e) {
	return e === "none";
}
function Ov(e, t) {
	let n = e.lines.at(-1), r = n ? void 0 : e.paragraphMark, i = (n ?? r)?.pageEdgeOverhangPt ?? 0;
	if (!(i > 0)) return t;
	let a = n ? n.bounds.yPt + n.advancePt - e.flowBounds.yPt : r.bounds.yPt + r.bounds.heightPt - e.flowBounds.yPt;
	return t > a + 1e-6 ? t : Math.max(0, Math.min(t, a - i));
}
function kv(e, t, n, r, i) {
	let a = e.lines.at(-1), o = a ? void 0 : e.paragraphMark;
	return !(((a ?? o)?.pageEdgeOverhangPt ?? 0) > 0) || !(r > 0) ? t : Math.min(t, Math.max(i, n - r));
}
function Av(e, t) {
	let n = e.spacing.afterPt, r = e.lines.at(-1), i = r ? void 0 : e.paragraphMark;
	return ((r ?? i)?.pageEdgeOverhangPt ?? 0) > 0 ? Math.max(0, Math.min(n, n - (e.advancePt - t))) : n;
}
function jv(e) {
	return Math.max(0, e.advancePt - Math.min(e.authoredSpaceAfterPt, e.retainedSpaceAfterPt));
}
function Mv(e) {
	return e.origin.yPt + (e.inkBounds?.descentPt ?? 0);
}
function Nv(e) {
	if (e.kind === "resource" || e.kind === "drawing") return e.bounds.yPt + e.bounds.heightPt;
	if (e.kind === "anchor-host") return null;
	if (e.kind === "tab") {
		let t = e.leaderGlyphs ?? [];
		return t.length > 0 ? Math.max(...t.map(Mv)) : null;
	}
	let t = e.paintOps ?? [], n = t.length > 0 ? t.map((t) => e.origin.yPt + t.offset.yPt + (t.blockAxisInkBounds?.endPt ?? t.inkBounds?.descentPt ?? 0)) : [e.origin.yPt];
	for (let t of e.decorations) {
		let e = t.widthPt / 2;
		n.push(t.from.yPt + e, t.to.yPt + e);
		for (let r of t.path ?? []) n.push(r.yPt + e);
	}
	for (let t of e.highlightFragments ?? []) n.push(t.rect.yPt + t.rect.heightPt);
	for (let t of e.runBorderFragments ?? []) {
		let e = t.widthPt / 2;
		n.push(t.from.yPt + e, t.to.yPt + e);
	}
	for (let t of e.emphasis?.glyphs ?? []) n.push(Mv(t));
	for (let t of e.ruby?.paintOps ?? []) n.push(Mv(t));
	for (let t of e.emphasis?.paths ?? []) {
		let e = t.stroke === null ? 0 : t.strokeWidthPt / 2;
		for (let r of t.points) n.push(r.yPt + e);
	}
	return Math.max(...n);
}
function Pv(e) {
	if (e.writingMode !== "vertical-rl" || e.logicalLineBoxExtentPt <= e.availableBlockExtentPt) return e.logicalLineBoxExtentPt;
	let t = e.paragraph.lines.at(-1);
	if (!t || t.placements.some((e) => e.kind === "text" && (e.paintOps ?? []).some((e) => e.glyphOrientation !== void 0 && e.blockAxisInkBounds === void 0))) return e.logicalLineBoxExtentPt;
	let n = t.placements.flatMap((e) => {
		let t = Nv(e);
		return t === null ? [] : [t];
	});
	if (n.length === 0 || e.paragraph.shading) return e.logicalLineBoxExtentPt;
	for (let t of e.paragraph.borders) {
		let e = t.widthPt / 2;
		n.push(t.from.yPt + e, t.to.yPt + e);
	}
	if (e.paragraph.paragraphMark && !e.paragraph.paragraphMark.hidden) {
		let t = e.paragraph.paragraphMark.bounds;
		n.push(t.yPt + t.heightPt);
	}
	return Math.max(0, Math.max(...n) - e.paragraph.flowBounds.yPt);
}
function Fv(e) {
	return e.keepNext && e.inkless && e.undecoratedMark;
}
function Iv(e, t) {
	let n = e[t];
	if (n?.kind !== "body-block" || n.block.kind !== "paragraph") return;
	let r = e[t + 1], i = e[t + 2], a = n.block.inkless === !0 && r?.kind === "begin-section" && r.section.startType === "continuous";
	return a && n.block.spaceBeforePt === 0 ? "collapse-mark" : a ? "suppress-before" : n.block.inkless === !0 && r?.kind === "body-block" && r.block.kind === "paragraph" && r.block.inkless === !0 && r.block.spaceBeforePt === 0 && i?.kind === "begin-section" && i.section.startType === "continuous" ? "drop-previous-after" : void 0;
}
function Lv(e) {
	let t = /* @__PURE__ */ new Set(), n = (e) => e?.kind === "consume-source" && e.framed === void 0;
	for (let r = 0; r < e.length;) {
		if (!n(e[r])) {
			r += 1;
			continue;
		}
		let i = r;
		for (; n(e[i]);) i += 1;
		let a = e[i];
		if (a?.kind === "adjacent-table-group" || a?.kind === "body-block" && (a.block.kind === "table" || a.block.framed === "frame")) {
			let n = [];
			for (let t = r; t < i; t += 1) {
				let r = e[t];
				r.kind === "consume-source" && r.pageBreakBefore === !0 && n.push(t);
			}
			n.length === 1 && t.add(n[0]);
		}
		r = i;
	}
	return t;
}
function Rv(e) {
	return e.drawings.length > 0 && e.lines.every((e) => e.placements.every((e) => e.kind === "drawing" || e.kind === "anchor-host"));
}
function zv(e) {
	return e.lines.some((e) => e.placements.some((e) => (e.kind === "resource" && (e.resourceKind === "image" || e.resourceKind === "chart") || e.kind === "drawing") && e.advancePt > 0 && e.bounds !== void 0 && e.bounds.widthPt > 0 && e.bounds.heightPt > 0));
}
function Bv(e, t) {
	if (!Rv(e)) return null;
	let n = e.drawings.filter((e) => e.anchorLayer?.verticalOwnership === "host" && Number.isFinite(e.flowBounds.xPt) && Number.isFinite(e.flowBounds.yPt) && Number.isFinite(e.flowBounds.widthPt) && Number.isFinite(e.flowBounds.heightPt) && e.flowBounds.widthPt > 0 && e.flowBounds.heightPt > 0);
	if (n.length !== e.drawings.length) return null;
	let r = Math.max(...n.map((e) => e.flowBounds.yPt + e.flowBounds.heightPt));
	return Math.max(0, r - t);
}
function Vv(e) {
	if (!Rv(e)) return null;
	let { paragraphMark: t, ...n } = e;
	return Object.freeze({
		...n,
		advancePt: 0,
		flowBounds: Object.freeze({
			...e.flowBounds,
			heightPt: 0
		})
	});
}
function Hv(e) {
	return !e.wholeNoteFitsWithReference && (e.columnBand || !e.wholeNoteFitsFreshPage || e.textAfterReference || e.hardBreakBeforeNextNote || e.wholeNoteFitsOnlyWithoutTrailingAfter || e.pageOpensWithIncomingTail);
}
function Uv(e) {
	return e.kind === "authored-break" && e.break !== "column" || e.kind === "begin-section" && e.section.startType !== "continuous" || e.kind === "body-block" && e.block.kind === "paragraph" && e.block.pageBreakBefore;
}
function Wv(e, t) {
	return t > 1 && e.perColumnFootnoteBands;
}
function Gv(e, t) {
	return e.continuousSectionKeepsFootnotePage || e.footnoteLayoutLikeWW8 && !t;
}
var Kv = "page-object:";
function qv(e) {
	return Object.freeze({
		story: "header",
		storyInstance: `${Kv}${e}`,
		path: []
	});
}
function Jv(e) {
	return e.story === "header" && e.storyInstance.startsWith(Kv);
}
function Yv(e) {
	switch (e) {
		case "continuous":
		case "nextColumn":
		case "nextPage":
		case "oddPage":
		case "evenPage": return e;
		default: return "nextPage";
	}
}
function Xv(e, t, n) {
	let r = n === null ? null : `section:${n}`, i = (n) => e[n] === null ? null : {
		story: t,
		storyInstance: r === null ? n : `${r}:${n}`,
		path: []
	};
	return Object.freeze({
		default: i("default"),
		first: i("first"),
		even: i("even")
	});
}
function Zv(e) {
	return {
		...e.geometry,
		titlePage: e.titlePage,
		evenAndOddHeaders: !1,
		sectionStart: e.startType,
		columns: e.columns,
		textDirection: e.textDirection,
		docGridType: e.docGridType,
		docGridLinePitch: e.docGridLinePitch,
		docGridCharSpace: e.docGridCharSpace,
		pageNumType: e.pageNumType,
		vAlign: e.vAlign,
		lineNumbering: e.lineNumbering
	};
}
function Qv(e, t) {
	let n = e.markerBodyIndex;
	return Object.freeze({
		sectionOccurrenceId: e.sectionOccurrenceId,
		source: Object.freeze(n === null ? {
			story: "body",
			storyInstance: "body",
			path: Object.freeze([])
		} : {
			story: "body",
			storyInstance: "body",
			path: Object.freeze([n])
		}),
		startType: Yv(e.startType),
		context: Object.freeze(av(Zv(e), e.sectionBidi, e.sectionFlow)),
		pageNumbering: Object.freeze({
			start: e.pageNumType?.start ?? null,
			format: e.pageNumType?.fmt ?? null
		}),
		titlePage: e.titlePage,
		evenAndOddHeaders: t.evenAndOddHeaders,
		headers: Xv(e.headers, "header", n),
		footers: Xv(e.footers, "footer", n),
		pageBordersAuthored: e.pageBordersAuthored,
		pageBorders: e.pageBorders,
		pageLayout: Object.freeze({
			physicalGeometry: Object.freeze({ ...e.geometry }),
			columns: e.columns,
			textDirection: e.textDirection ?? "lrTb",
			gutterPt: e.gutterPt,
			rtlGutter: e.rtlGutter,
			...t.pageLayoutSettings
		})
	});
}
function $v(e) {
	let t = new Map(e.sectionIndex.occurrences.map((t) => [t.sectionOccurrenceId, Qv(t, e)])), n = e.sectionIndex.occurrences[0];
	if (!n) throw Error("DOCX body requires a final section owner");
	let r = t.get(n.sectionOccurrenceId), i = Lv(e.sequence), a = e.sequence.map((n, r) => {
		if (n.kind === "begin-section") {
			let e = t.get(n.section.sectionOccurrenceId);
			if (!e) throw Error(`Missing body section owner: ${n.section.sectionOccurrenceId}`);
			return Object.freeze({
				...n,
				section: e
			});
		}
		if (n.kind === "consume-source") return i.has(r) ? Object.freeze({
			kind: "authored-break",
			source: n.source,
			break: "pageBreakBefore"
		}) : n;
		if (n.kind !== "body-block" || n.block.kind !== "paragraph") return n;
		let a = Iv(e.sequence, r);
		return a === void 0 ? n : Object.freeze({
			...n,
			block: Object.freeze({
				...n.block,
				continuousSectionRole: a
			})
		});
	});
	return Z({
		source: {
			story: "body",
			storyInstance: "body",
			path: []
		},
		compat: e.compat,
		initialSection: r,
		sequence: a,
		parserDiagnostics: e.parserDiagnostics ?? [],
		endnoteIds: e.endnoteIds ?? [],
		repeatedFootnoteLastEntries: e.repeatedFootnoteLastEntries ?? [],
		noteLayoutSettings: e.noteLayoutSettings,
		...e.pageObjects && e.pageObjects.length > 0 ? { pageObjects: e.pageObjects } : {}
	}, "DOCX body layout input");
}
var ey = class extends Error {
	kind;
	ids;
	failure;
	constructor(e, t, n) {
		super(n.message), this.kind = e, this.ids = t, this.failure = n;
	}
}, ty = class {
	permitted = /* @__PURE__ */ new Map();
	work = /* @__PURE__ */ new Map();
	sourceSizes = /* @__PURE__ */ new Map();
	retainedSizes = /* @__PURE__ */ new WeakMap();
	sourceTraversalSizes = /* @__PURE__ */ new WeakMap();
	textViews = /* @__PURE__ */ new WeakMap();
	originalFailure;
	get recovering() {
		return this.originalFailure !== void 0;
	}
	errorForAttempt(e) {
		return this.originalFailure ?? e;
	}
	textServiceFor(e, t) {
		let n = this.textViews.get(t);
		n || (n = /* @__PURE__ */ new Map(), this.textViews.set(t, n));
		let r = `${e.story}:${e.storyInstance}`, i = n.get(r);
		return i || (i = Object.freeze({
			...t,
			shape: (n) => (this.chargeWork(e, Math.max(1, n.text.length)), t.shape(n))
		}), n.set(r, i)), i;
	}
	get permissionCount() {
		return this.permitted.size;
	}
	permittedSince(e) {
		return [...this.permitted.keys()].slice(e).map((e) => {
			let t = e.indexOf(":");
			return Object.freeze({
				kind: e.slice(0, t),
				id: e.slice(t + 1)
			});
		});
	}
	allows(e, t) {
		return t.some((t) => this.permitted.has(`${e}:${t}`));
	}
	failure(e, t) {
		for (let n of t) {
			let t = this.permitted.get(`${e}:${n}`);
			if (t) return this.originalFailure ?? t;
		}
	}
	fail(e, t, n) {
		throw this.failure(e, t) ?? n;
	}
	charge(e, t, n, r) {
		let i = `${e}:${t}`, a = this.permitted.get(i);
		if (!a) return;
		n = this.sourceSizes.get(i) ?? n, this.sourceSizes.set(i, n);
		let o = this.work.get(i) ?? 0;
		if (r > 32 * (n + 1) - o) throw this.originalFailure ?? a;
		this.work.set(i, o + r);
	}
	registerSource(e, t) {
		let n = `${e.story}:${e.storyInstance}`;
		this.permitted.has(n) && !this.sourceSizes.has(n) && this.sourceSizes.set(n, t);
	}
	chargeWork(e, t) {
		if (e.story !== "footnote" && e.story !== "endnote") return;
		let n = this.sourceSizes.get(`${e.story}:${e.storyInstance}`);
		n !== void 0 && this.charge(e.story, e.storyInstance, n, t);
	}
	chargeSourceTraversal(e, t) {
		this.chargeTraversal(e, t, !0);
	}
	chargeRetained(e, t) {
		this.chargeTraversal(e, t, !1);
	}
	chargeTraversal(e, t, n) {
		if (e.story !== "footnote" && e.story !== "endnote") return;
		let r = e.story, i = e.storyInstance, a = this.sourceSizes.get(`${r}:${i}`);
		if (a === void 0) return;
		let o = n ? this.sourceTraversalSizes : this.retainedSizes, s = (e, t = !1) => {
			if (!e || typeof e != "object") return this.charge(r, i, a, 1), 1;
			let c = o.get(e);
			if (c !== void 0) return this.charge(r, i, a, c), c;
			this.charge(r, i, a, 1);
			let l = 1;
			t ||= uv(e);
			for (let o in e) Object.hasOwn(e, o) && (n && (this.charge(r, i, a, 1), l++), l += s(e[o], t));
			return t && o.set(e, l), l;
		};
		s(t);
	}
	recover(e) {
		if (!(e instanceof ey)) return !1;
		this.originalFailure ??= e.failure;
		let t = e.ids.filter((t) => !this.permitted.has(`${e.kind}:${t}`));
		return t.length === 0 && this.fail(e.kind, e.ids, e.failure), t.forEach((t) => this.permitted.set(`${e.kind}:${t}`, e.failure)), !0;
	}
}, ny = /* @__PURE__ */ new WeakMap(), ry = /* @__PURE__ */ new WeakMap();
function iy(e, t) {
	ry.set(e, t);
}
function ay(e) {
	return ry.get(e);
}
function oy(e, t) {
	ny.set(e, t);
}
function sy(e) {
	return ny.get(e);
}
function cy(e, t, n) {
	return ny.get(e)?.allows(t, n) === !0;
}
var ly = 1e4, uy = 32e6;
function dy() {
	let e = /* @__PURE__ */ new WeakMap(), t = 0, n = (t) => {
		let n = e.get(t);
		return n === void 0 && (n = fy(t), e.set(t, n)), n;
	};
	return Object.freeze({
		sourceUnits: n,
		charge(e) {
			let r = n(e);
			if (r > 32e6 - t) throw Error(`Footnote acquisition cumulative work budget exceeded (${uy} source units)`);
			t += r;
		}
	});
}
function fy(e) {
	let t = [e], n = 0;
	for (; t.length > 0;) {
		let e = t.pop();
		if (n += typeof e == "string" ? Math.max(1, e.length) : 1, n + t.length > 1e6) throw Error("Footnote acquisition source budget exceeded");
		if (e && typeof e == "object") for (let r in e) {
			if (!Object.hasOwn(e, r)) continue;
			let i = e[r];
			if (++n + t.length > 1e6) throw Error("Footnote acquisition source budget exceeded");
			t.push(i);
		}
	}
	return n;
}
var py = 8e6;
function my(e) {
	let t, n = e.runs.length, r = py, i = () => {
		throw Error("Paragraph anchor reference work budget exceeded");
	};
	return Object.freeze({ charge(a) {
		if (t === void 0) {
			t = 0;
			let a = [e];
			for (; a.length > 0;) {
				let e = a.pop();
				if (t += typeof e == "string" ? Math.max(1, e.length) : 1, t + a.length > r && i(), e && typeof e == "object") for (let o in e) {
					if (!Object.hasOwn(e, o)) continue;
					let s = e[o];
					o === "text" && typeof s == "string" && (n += s.length), ++t + a.length > r && i(), a.push(s);
				}
			}
		}
		let o = 1;
		for (let e of a) o += 1 + e.polygon.length;
		let s = t + Math.max(1, n) * o;
		(!Number.isSafeInteger(s) || s > r) && i(), r -= s;
	} });
}
var hy = 25e3, gy = 1e6, _y = (e, t) => Math.min(gy, e + t);
function vy(e) {
	let t = /* @__PURE__ */ new Map(), n = (n) => {
		let r = Me(n), i = t.get(r);
		if (i) return i;
		let a = 1, o = 0, s = [], c = [e.blocks.storyRoot(n)];
		for (; c.length && a < 1e6;) {
			if (++o >= 1e6) {
				a = gy;
				break;
			}
			let e = c.pop();
			e.type === "paragraph" && (a = _y(a, 1)), Array.isArray(e.cells) && (a = _y(a, e.cells.length)), e.kind === "compatibility" && Array.isArray(e.paragraphs) && (a = _y(a, _y(1, e.paragraphs.length))), e.kind === "complete" && e.source && s.push(e.source);
			for (let t of Object.values(e)) if (t && typeof t == "object") {
				if (c.length >= 1e6) {
					a = gy;
					break;
				}
				c.push(t);
			}
		}
		let l = {
			story: n.story,
			own: a,
			children: s
		};
		return t.set(r, l), l;
	};
	return {
		local: n,
		total: (e) => {
			let t = n(e), r = new Set([t]), i = [{
				entry: t,
				index: 0,
				units: t.own
			}];
			for (; i.length;) {
				let e = i[i.length - 1];
				if (e.entry.total !== void 0 || e.index === e.entry.children.length || e.units === 1e6) {
					e.entry.total ??= e.units, r.delete(e.entry), i.pop();
					continue;
				}
				let t = n(e.entry.children[e.index]);
				if (t.total !== void 0) e.units = _y(e.units, t.total), e.index++;
				else {
					if (r.has(t)) throw TypeError("Cyclic complete text-box story source");
					r.add(t), i.push({
						entry: t,
						index: 0,
						units: t.own
					});
				}
			}
			return t.total;
		},
		definitions: t
	};
}
function yy(e) {
	let t = /* @__PURE__ */ new Map(), n = 0;
	if (e) {
		let r = vy(e);
		n = r.local({
			story: "body",
			storyInstance: "body",
			path: []
		}).own;
		for (let i of ["footnote", "endnote"]) for (let a of i === "footnote" ? e.blocks.footnotes : e.blocks.endnotes) {
			let e = {
				story: i,
				storyInstance: a.id,
				path: []
			};
			n = _y(n, r.local(e).own), t.set(Me(e), r.total(e));
		}
		for (let i of e.blocks.reservedNoteRoots) n = _y(n, r.local(i).own), t.set(Me(i), r.total(i));
		for (let t of e.blocks.sources) t.story === "textbox" && r.local({
			...t,
			path: []
		});
		let i = [e.bodyLayoutInput.initialSection, ...e.bodyLayoutInput.sequence.flatMap((e) => e.kind === "begin-section" ? [e.section] : [])];
		for (let e of i) for (let n of [...Object.values(e.headers), ...Object.values(e.footers)]) n && !t.has(Me(n)) && t.set(Me(n), r.total(n));
		for (let n of e.bodyLayoutInput.pageObjects ?? []) t.has(Me(n.source)) || t.set(Me(n.source), r.total(n.source));
		for (let e of r.definitions.values()) {
			for (let t of e.children) r.local(t);
			e.story === "textbox" && (n = _y(n, e.own));
		}
	}
	let r = Math.min(gy, Math.max(hy, 32 * n)), i = 0, a = !1, o = 0, s = /* @__PURE__ */ new Map();
	return Object.freeze({
		get limit() {
			return r;
		},
		get misses() {
			return i;
		},
		noteMiss() {
			if (a || ++i > r) throw a = !0, new Wo("NON_CONVERGENCE", `layout acquisition exceeded the operational miss budget ${r}`);
		},
		admitPageStories(e, i, c) {
			if (a || r === 1e6 || !Number.isInteger(i) || i < 0 || i >= 1e4) return;
			let l = s.get(e), u = l?.get(i), d = 0;
			for (let n of c) {
				if (!n) continue;
				let r = Me(n), a = t.get(r) ?? 0;
				a === 0 || u?.has(r) || (l || s.set(e, l = /* @__PURE__ */ new Map()), u || l.set(i, u = /* @__PURE__ */ new Set()), u.add(r), d = _y(d, a));
			}
			d !== 0 && (o = _y(o, d), r = Math.min(gy, Math.max(hy, 32 * (n + o))), r === 1e6 && s.clear());
		}
	});
}
function by(e, t = /* @__PURE__ */ new WeakSet()) {
	if (typeof e == "string") return 1 + e.length;
	if (!e || typeof e != "object") return 1;
	if (t.has(e)) return 0;
	t.add(e);
	let n = 1;
	for (let r in e) if (Object.hasOwn(e, r) && (n += r.length + by(e[r], t), n > 2e6)) break;
	return n;
}
function xy(e) {
	let t = /* @__PURE__ */ new Map(), n = /* @__PURE__ */ new Map(), r = 0, i = (e) => {
		let i = t.get(e);
		t.delete(e), r -= i.units;
		let a = n.get(i.occurrence);
		a.delete(e), a.size === 0 && n.delete(i.occurrence);
	};
	return { layout(a, o) {
		let s = JSON.stringify([a.occurrence, a.placement]), c = t.get(s);
		if (c) {
			t.delete(s), t.set(s, c);
			let e = n.get(a.occurrence);
			return e.delete(s), e.add(s), c.story;
		}
		a.trial && e();
		let l = o(), u = s.length + a.occurrence.length + by(l);
		if (u > 2e6) return l;
		let d = n.get(a.occurrence);
		for (d || n.set(a.occurrence, d = /* @__PURE__ */ new Set()), d.add(s), t.set(s, {
			occurrence: a.occurrence,
			story: l,
			units: u
		}), r += u; d.size > 2;) i(d.values().next().value);
		for (; t.size > 4096 || r > 2e6;) i(t.keys().next().value);
		return l;
	} };
}
var Sy = Symbol("document-layout-runtime");
function Cy(e, t) {
	Object.defineProperty(e, Sy, {
		configurable: !1,
		enumerable: !1,
		writable: !1,
		value: {
			services: null,
			defaultCurrentDateMs: t,
			activeLayoutOptions: null
		}
	});
}
function wy(e) {
	let t = e[Sy];
	if (t) return t;
	throw Error("Document layout runtime is not initialized; attach it explicitly");
}
function Ty(e) {
	let t = new Map(e), n = Object.freeze([...t.keys()].sort());
	return Object.freeze({
		keys: n,
		resolve(e) {
			let n = t.get(e);
			if (n === void 0) throw Error(`Unknown runtime resource: ${e}`);
			return n;
		}
	});
}
var Ey = /* @__PURE__ */ new WeakMap(), Dy = /* @__PURE__ */ new WeakMap(), Oy = /* @__PURE__ */ new WeakMap(), ky = /* @__PURE__ */ new WeakMap(), Ay = /* @__PURE__ */ new WeakMap(), jy = /* @__PURE__ */ new WeakMap(), My = /* @__PURE__ */ new WeakMap();
function Ny(e) {
	return My.get(e);
}
var Py = /* @__PURE__ */ new WeakMap(), Fy = /* @__PURE__ */ new WeakMap();
function Iy(e) {
	return Fy.get(e);
}
function Ly(e) {
	let t = /* @__PURE__ */ new WeakMap(), n = /* @__PURE__ */ new WeakMap(), r = /* @__PURE__ */ new WeakMap(), i = /* @__PURE__ */ new WeakMap(), a = /* @__PURE__ */ new Map(), o = /* @__PURE__ */ new Map(), s = 1;
	return Object.freeze({
		objectIdentity(e) {
			let n = t.get(e);
			return n === void 0 && (n = s, s += 1, t.set(e, n)), n;
		},
		fingerprintOrdinal(e) {
			if (e === null) return null;
			let t = o.get(e);
			return t === void 0 && (t = o.size, o.set(e, t)), t;
		},
		kinsokuKey(e) {
			let t = i.get(e);
			if (t === void 0) {
				let n = JSON.stringify([
					e.enabled,
					[...e.lineStartForbidden].sort((e, t) => e - t),
					[...e.lineEndForbidden].sort((e, t) => e - t)
				]);
				t = a.get(n), t === void 0 && (t = a.size, a.set(n, t)), i.set(e, t);
			}
			return t;
		},
		get(e, t) {
			let r = n.get(e);
			if (!r?.has(t)) return;
			let i = r.get(t);
			return r.delete(t), r.set(t, i), i;
		},
		set(e, t, r) {
			let i = n.get(e);
			for (i || (i = /* @__PURE__ */ new Map(), n.set(e, i)), i.set(t, r); i.size > 2;) i.delete(i.keys().next().value);
		},
		getLineBreaking(e, t) {
			let n = r.get(e);
			if (!n?.has(t)) return;
			let i = n.get(t);
			return n.delete(t), n.set(t, i), i;
		},
		setLineBreaking(e, t, n) {
			let i = r.get(e);
			for (i || (i = /* @__PURE__ */ new Map(), r.set(e, i)), i.set(t, n); i.size > 2;) i.delete(i.keys().next().value);
		},
		workBudget: e,
		noteMiss: () => e.noteMiss()
	});
}
function Ry(e, t) {
	let n = [
		e.text,
		e.images,
		e.math
	], r = new Set(n.flatMap((e) => {
		let t = Dy.get(e);
		return t ? [t] : [];
	}));
	if (r.size > 1) throw Error("Layout services combine foreign runtime owners");
	let i = r.values().next().value, a = n.filter((e) => !Dy.has(e));
	if (i && a.length > 1) throw Error("Layout services are missing service lineage for multiple components");
	if (!i && !t) return;
	let o = i ?? {};
	for (let e of n) {
		let t = Dy.get(e);
		if (t && t !== o) throw Error("Layout services combine foreign runtime owners");
		Dy.set(e, o);
	}
	return o;
}
function zy(e, t) {
	let n = Ry(e, !0);
	if (Oy.has(n)) throw Error("Body layout kernel is already attached");
	Oy.set(n, t);
}
function By(e) {
	let t = Ry(e, !1);
	return t ? Oy.get(t) : void 0;
}
function Vy(e, t) {
	let n = Ry(e, !0);
	if (ky.has(n)) throw Error("Layout source store is already attached");
	ky.set(n, t);
}
function Hy(e) {
	let t = Ry(e, !1);
	return t ? ky.get(t) : void 0;
}
function Uy(e, t) {
	let n = Ry(e, !0);
	if (Ay.has(n)) throw Error("Vertical glyph measurement service is already attached");
	Ay.set(n, t);
}
function Wy(e) {
	let t = Ry(e, !1), n = t ? Ay.get(t) : void 0;
	if (!n) throw Error("Vertical glyph measurement service is not attached");
	return n;
}
function Gy(e, t) {
	if (jy.has(e)) throw Error("Layout variant store is already attached");
	jy.set(e, t);
}
function Ky(e) {
	return jy.get(e);
}
function qy(e, t, n = t.keys()) {
	if (Ey.has(e)) throw Error("Private resource lookup is already attached");
	let r = new Set(t.keys()), i = new Set(n), a = [...i].filter((e) => !r.has(e)).sort(), o = [...r].filter((e) => !i.has(e)).sort();
	if (a.length > 0 || o.length > 0) throw Error(`Runtime resource membership mismatch: missing [${a.join(", ")}]; extra [${o.join(", ")}]`);
	Ey.set(e, Ty(t));
}
function Jy(e) {
	return Ey.get(e);
}
var Yy = /* @__PURE__ */ new WeakMap(), Xy = /* @__PURE__ */ new WeakMap();
function Zy(e, t = {}) {
	let n = Object.freeze({
		...e,
		...t
	}), r = sy(e);
	r && oy(n, r);
	let i = ay(e);
	i && iy(n, i);
	let a = By(e);
	if (!a) throw Error("Body layout kernel is not attached to the supplied services");
	if (By(n) !== a) throw Error("Layout service view did not retain its body layout kernel owner");
	let o = Ey.get(e);
	o && Ey.set(n, o);
	let s = Yy.get(e);
	s && Yy.set(n, s);
	let c = Py.get(e);
	c && Py.set(n, c);
	let l = My.get(e);
	l && My.set(n, l);
	let u = Fy.get(e);
	return u && Fy.set(n, u), n;
}
function Qy(e) {
	let t = Zy(e), n = yy(Hy(e));
	return Py.set(t, Ly(n)), My.set(t, xy(() => n.noteMiss())), Fy.set(t, dy()), t;
}
function $y(e) {
	return Py.get(e);
}
function eb(e, t) {
	if (!Number.isInteger(t.totalPages) || t.totalPages < 1) throw RangeError("Field acquisition totalPages must be a positive integer");
	let n = Zy(e);
	return Xy.set(n, Object.freeze({ ...t })), n;
}
function tb(e) {
	return Xy.get(e) ?? Object.freeze({ totalPages: 1 });
}
function nb(e, t) {
	if (Yy.has(e)) throw Error("Paint resource registry is already attached");
	Yy.set(e, t);
}
function rb(e) {
	let t = Yy.get(e);
	if (!t) throw Error("Paint resource registry is not attached");
	return t;
}
function ib(e) {
	if (e.length === 0) return null;
	let t = Math.min(...e.map((e) => e.xPt)), n = Math.min(...e.map((e) => e.yPt)), r = Math.max(...e.map((e) => e.xPt + e.widthPt)), i = Math.max(...e.map((e) => e.yPt + e.heightPt));
	return {
		xPt: t,
		yPt: n,
		widthPt: r - t,
		heightPt: i - n
	};
}
function ab(e) {
	return {
		x: !e.horzSpecified || e.horzAnchor !== "page" && e.horzAnchor !== "margin",
		y: e.vertAnchor !== "page" && e.vertAnchor !== "margin"
	};
}
function ob(e, t) {
	return {
		...e,
		xPt: e.xPt + t.xPt,
		yPt: e.yPt + t.yPt
	};
}
function Q(e, t) {
	return {
		...e,
		xPt: e.xPt + t.xPt,
		yPt: e.yPt + t.yPt
	};
}
function sb(e, t) {
	return {
		...e,
		from: ob(e.from, t),
		to: ob(e.to, t)
	};
}
function cb(e, t) {
	return e.kind === "rect" ? {
		...e,
		rect: Q(e.rect, t)
	} : {
		...e,
		points: e.points.map((e) => ob(e, t))
	};
}
function lb(e, t) {
	return e.kind === "noop" ? e : e.kind === "drawingml-shape" || e.kind === "drawingml-image-fill" ? {
		...e,
		...e.kind === "drawingml-shape" && e.concentricFill?.bounds ? { concentricFill: {
			...e.concentricFill,
			bounds: Q(e.concentricFill.bounds, t)
		} } : {},
		...e.kind === "drawingml-image-fill" && e.maskBounds ? { maskBounds: Q(e.maskBounds, t) } : {},
		plan: {
			...e.plan,
			rect: {
				...e.plan.rect,
				x: e.plan.rect.x + t.xPt,
				y: e.plan.rect.y + t.yPt
			}
		}
	} : {
		...e,
		...e.kind === "watermark-text" && e.glyphTransform ? { glyphTransform: {
			...e.glyphTransform,
			e: e.glyphTransform.e + t.xPt - e.glyphTransform.a * t.xPt - e.glyphTransform.c * t.yPt,
			f: e.glyphTransform.f + t.yPt - e.glyphTransform.b * t.xPt - e.glyphTransform.d * t.yPt
		} } : {},
		...e.kind === "watermark-text" && e.maskBounds ? { maskBounds: Q(e.maskBounds, t) } : {},
		rect: Q(e.rect, t)
	};
}
function ub(e, t) {
	let n = e.orientation === "upright-physical" ? {
		xPt: 0,
		yPt: 0
	} : t;
	return {
		...e,
		flowBounds: Q(e.flowBounds, t),
		inkBounds: Q(e.inkBounds, t),
		...e.clipBounds ? { clipBounds: Q(e.clipBounds, t) } : {},
		...e.transform ? { transform: {
			...e.transform,
			e: e.transform.e + t.xPt,
			f: e.transform.f + t.yPt
		} } : {},
		...e.clip ? { clip: cb(e.clip, t) } : {},
		commands: e.commands.map((e) => lb(e, n))
	};
}
function db(e, t, n) {
	let r = `${t.xPt}\u0000${t.yPt}`, i = n.drawingMemo.get(e);
	if (i) {
		if (i.key !== r) throw Error("incompatible projection ownership");
		return i.value;
	}
	let a = ub(e, t);
	return n.drawingMemo.set(e, {
		key: r,
		value: a
	}), a;
}
function fb(e, t, n) {
	return e.kind === "text" ? {
		...e,
		origin: ob(e.origin, t),
		bounds: Q(e.bounds, t),
		...e.highlightBounds ? { highlightBounds: Q(e.highlightBounds, t) } : {},
		decorations: e.decorations.map((e) => ({
			...e,
			from: ob(e.from, t),
			to: ob(e.to, t),
			...e.path ? { path: e.path.map((e) => ob(e, t)) } : {}
		})),
		...e.highlightFragments ? { highlightFragments: e.highlightFragments.map((e) => ({
			...e,
			rect: Q(e.rect, t)
		})) } : {},
		...e.ruby ? { ruby: {
			...e.ruby,
			paintOps: e.ruby.paintOps.map((e) => ({
				...e,
				origin: ob(e.origin, t)
			}))
		} } : {},
		...e.emphasis ? { emphasis: {
			...e.emphasis,
			...e.emphasis.glyphs ? { glyphs: e.emphasis.glyphs.map((e) => ({
				...e,
				origin: ob(e.origin, t)
			})) } : {},
			...e.emphasis.paths ? { paths: e.emphasis.paths.map((e) => ({
				...e,
				points: e.points.map((e) => ob(e, t))
			})) } : {}
		} } : {},
		...e.runBorderFragments ? { runBorderFragments: e.runBorderFragments.map((e) => sb(e, t)) } : {}
	} : e.kind === "anchor-host" ? {
		...e,
		bounds: Q(e.bounds, t),
		baselinePt: e.baselinePt + t.yPt
	} : e.kind === "drawing" ? {
		...e,
		bounds: Q(e.bounds, n?.get(e.drawingId) ?? t)
	} : e.kind === "tab" && (e.leaderGlyphs || e.decorations) ? {
		...e,
		...e.bounds ? { bounds: Q(e.bounds, t) } : {},
		...e.leaderGlyphs ? { leaderGlyphs: e.leaderGlyphs.map((e) => ({
			...e,
			origin: ob(e.origin, t)
		})) } : {},
		...e.decorations ? { decorations: e.decorations.map((e) => ({
			...e,
			from: ob(e.from, t),
			to: ob(e.to, t),
			...e.path ? { path: e.path.map((e) => ob(e, t)) } : {}
		})) } : {}
	} : e.bounds ? {
		...e,
		bounds: Q(e.bounds, t)
	} : e;
}
function pb(e, t, n) {
	return {
		...e,
		bounds: Q(e.bounds, t),
		...e.wrapBounds ? { wrapBounds: Q(e.wrapBounds, t) } : {},
		...e.wrapFragments ? { wrapFragments: e.wrapFragments.map((e) => Q(e, t)) } : {},
		baselinePt: e.baselinePt + t.yPt,
		placements: e.placements.map((e) => fb(e, t, n)),
		...e.barTabRules ? { barTabRules: e.barTabRules.map((e) => ({
			...e,
			from: ob(e.from, t),
			to: ob(e.to, t)
		})) } : {}
	};
}
function mb(e, t) {
	let n = e.axes[t];
	return n.status === "resolved" && [
		"page",
		"margin",
		"leftMargin",
		"rightMargin",
		"topMargin",
		"bottomMargin"
	].includes(n.referenceFrame);
}
function hb(e, t) {
	let n = mb(e, "horizontal") ? 0 : t.xPt, r = mb(e, "vertical") ? 0 : t.yPt, i = {
		xPt: n,
		yPt: r
	}, a = {
		horizontal: e.axes.horizontal.status === "resolved" ? {
			...e.axes.horizontal,
			baseStartPt: e.axes.horizontal.baseStartPt + n,
			baseEndPt: e.axes.horizontal.baseEndPt + n,
			resolvedOriginPt: e.axes.horizontal.resolvedOriginPt + n
		} : e.axes.horizontal,
		vertical: e.axes.vertical.status === "resolved" ? {
			...e.axes.vertical,
			baseStartPt: e.axes.vertical.baseStartPt + r,
			baseEndPt: e.axes.vertical.baseEndPt + r,
			resolvedOriginPt: e.axes.vertical.resolvedOriginPt + r
		} : e.axes.vertical
	};
	return e.status === "unsupported" ? {
		...e,
		axes: a
	} : {
		...e,
		axes: a,
		geometry: {
			...e.geometry,
			objectFrame: Q(e.geometry.objectFrame, i),
			inkBounds: Q(e.geometry.inkBounds, i),
			wrapBounds: e.geometry.wrapBounds ? Q(e.geometry.wrapBounds, i) : null,
			wrap: {
				...e.geometry.wrap,
				polygon: e.geometry.wrap.polygon ? {
					...e.geometry.wrap.polygon,
					points: e.geometry.wrap.polygon.points.map((e) => ob(e, i))
				} : null
			}
		}
	};
}
function gb(e, t) {
	return _b(e, t, {
		memo: /* @__PURE__ */ new WeakMap(),
		drawingMemo: /* @__PURE__ */ new WeakMap()
	});
}
function _b(e, t, n) {
	let r = `${t.xPt}\u0000${t.yPt}`, i = n.memo.get(e);
	if (i) {
		if (i.key !== r) throw Error("incompatible projection ownership");
		return i.value;
	}
	let a = new Map(e.drawings.flatMap((e) => e.anchorLayer ? [[e.anchorLayer.occurrenceId, e.anchorLayer]] : [])), o = /* @__PURE__ */ new Map(), s = /* @__PURE__ */ new Map();
	for (let n of e.drawings) {
		let e = {
			xPt: n.anchorLayer?.horizontalOwnership === "page" ? 0 : t.xPt,
			yPt: n.anchorLayer?.verticalOwnership === "page" ? 0 : t.yPt
		};
		s.set(n.id, e), n.textBoxIds?.forEach((t) => o.set(t, n.orientation === "upright-physical" ? {
			xPt: 0,
			yPt: 0
		} : e));
	}
	let c = e.drawings.map((e) => db(e, s.get(e.id) ?? t, n)), l = ib(c.filter((e) => e.anchorLayer?.cellContainment === !0).map((e) => e.flowBounds)), u = {
		...e,
		flowBounds: Q(e.flowBounds, t),
		inkBounds: Q(e.inkBounds, t),
		...e.clipBounds ? { clipBounds: Q(e.clipBounds, t) } : {},
		lines: e.lines.map((e) => pb(e, t, s)),
		borders: e.borders.map((e) => sb(e, t)),
		drawings: c,
		...l ? { cellContainmentBounds: l } : {},
		textBoxes: e.textBoxes.map((e) => yb(e, o.get(e.id) ?? t, n)),
		exclusions: e.exclusions.map((e) => {
			let n = e.anchorOccurrenceId ? a.get(e.anchorOccurrenceId) : void 0, r = {
				xPt: n?.horizontalOwnership === "page" ? 0 : t.xPt,
				yPt: e.verticalOwnership === "page" || n?.verticalOwnership === "page" ? 0 : t.yPt
			};
			return {
				...e,
				bounds: Q(e.bounds, r),
				polygon: e.polygon.map((e) => ob(e, r))
			};
		}),
		...e.anchorCollisions ? { anchorCollisions: e.anchorCollisions.map((e) => ({
			...e,
			bounds: Q(e.bounds, {
				xPt: e.horizontalOwnership === "page" ? 0 : t.xPt,
				yPt: e.verticalOwnership === "page" ? 0 : t.yPt
			})
		})) } : {},
		...e.anchorFrames ? { anchorFrames: e.anchorFrames.map((e) => hb(e, t)) } : {},
		...e.paragraphMark ? { paragraphMark: {
			...e.paragraphMark,
			bounds: Q(e.paragraphMark.bounds, t),
			...e.paragraphMark.wrapBounds ? { wrapBounds: Q(e.paragraphMark.wrapBounds, t) } : {}
		} } : {},
		...e.lineNumbers ? { lineNumbers: e.lineNumbers.map((e) => ({
			...e,
			bounds: Q(e.bounds, t),
			paintOps: e.paintOps.map((e) => ({
				...e,
				origin: ob(e.origin, t)
			}))
		})) } : {}
	};
	return n.memo.set(e, {
		key: r,
		value: u
	}), u;
}
function vb(e, t) {
	return yb(e, t, {
		memo: /* @__PURE__ */ new WeakMap(),
		drawingMemo: /* @__PURE__ */ new WeakMap()
	});
}
function yb(e, t, n) {
	let r = e.verticalMode === void 0;
	return {
		...e,
		flowBounds: Q(e.flowBounds, t),
		inkBounds: Q(e.inkBounds, t),
		...e.clipBounds ? { clipBounds: r ? Q(e.clipBounds, t) : e.clipBounds } : {},
		...e.clipRects ? { clipRects: r ? e.clipRects.map((e) => Q(e, t)) : e.clipRects } : {},
		...e.contentBounds ? { contentBounds: r ? Q(e.contentBounds, t) : e.contentBounds } : {},
		transform: r ? e.transform : {
			...e.transform,
			e: e.transform.e + t.xPt,
			f: e.transform.f + t.yPt
		},
		story: r ? {
			...e.story,
			flowBounds: Q(e.story.flowBounds, t),
			inkBounds: Q(e.story.inkBounds, t),
			...e.story.clipBounds ? { clipBounds: Q(e.story.clipBounds, t) } : {},
			blocks: e.story.blocks.map((e) => {
				if (e.kind === "paragraph") return _b(e, t, n);
				if (e.kind === "table") return bb(e, t);
				throw Error(`Text-box story contains unsupported retained node: ${e.kind}`);
			})
		} : e.story
	};
}
function bb(e, t) {
	let n = Sb(e, t), r = /* @__PURE__ */ new Map(), i = (e) => {
		let n = r.get(e);
		if (n) return n;
		let i = {
			...e,
			anchorBounds: Q(e.anchorBounds, t),
			...e.columnBounds ? { columnBounds: Q(e.columnBounds, t) } : {},
			child: bb(e.child, t)
		};
		return r.set(e, i), i;
	}, a = e.floatingTables?.map(i), o = e.resolvedFloatingTables?.map((e) => {
		let n = i(e.source);
		return {
			...e,
			xPt: e.xPt + t.xPt,
			yPt: e.yPt + t.yPt,
			bounds: Q(e.bounds, t),
			exclusionBounds: Q(e.exclusionBounds, t),
			source: n,
			child: n.child
		};
	});
	return {
		...n,
		...a ? { floatingTables: a } : {},
		...o ? { resolvedFloatingTables: o } : {}
	};
}
function xb(e, t) {
	return gb(e, t);
}
function Sb(e, t) {
	let n = e.ownerHostPageAxes, r = n ? {
		xPt: n.horizontal ? 0 : t.xPt,
		yPt: n.vertical ? 0 : t.yPt
	} : t;
	return {
		...e,
		flowBounds: Q(e.flowBounds, r),
		inkBounds: Q(e.inkBounds, r),
		...e.clipBounds ? { clipBounds: Q(e.clipBounds, r) } : {},
		borders: e.borders.map((e) => sb(e, r)),
		...e.compoundBorderFrames ? { compoundBorderFrames: e.compoundBorderFrames.map((e) => ({
			...e,
			bounds: Q(e.bounds, r)
		})) } : {},
		rows: e.rows.map((e) => ({
			...e,
			flowBounds: Q(e.flowBounds, r),
			inkBounds: Q(e.inkBounds, r),
			...e.clipBounds ? { clipBounds: Q(e.clipBounds, r) } : {},
			cells: e.cells.map((e) => ({
				...e,
				flowBounds: Q(e.flowBounds, r),
				inkBounds: Q(e.inkBounds, r),
				...e.clipBounds ? { clipBounds: Q(e.clipBounds, r) } : {},
				...e.verticalText ? {
					contentBounds: e.contentBounds,
					verticalText: {
						...e.verticalText,
						transform: {
							...e.verticalText.transform,
							e: e.verticalText.transform.e + r.xPt,
							f: e.verticalText.transform.f + r.yPt
						}
					}
				} : { contentBounds: Q(e.contentBounds, r) },
				blocks: e.blocks
			}))
		}))
	};
}
function Cb(e, t) {
	let n = u(e, t), r = e === "triple" || /^(?:thinThick|thickThin|thinThickThin)(?:Small|Medium|Large)Gap$/.test(e);
	return Object.freeze({
		authoredStyle: e,
		style: e === "double" ? "double" : r ? "compound" : n.length > 0 ? "dashed" : e.includes("wave") ? "wavy" : "solid",
		dashPatternPt: Object.freeze(n)
	});
}
function wb(e) {
	if (e.length === 0) return null;
	let t = Math.min(...e.map((e) => e.xPt)), n = Math.min(...e.map((e) => e.yPt)), r = Math.max(...e.map((e) => e.xPt + e.widthPt)), i = Math.max(...e.map((e) => e.yPt + e.heightPt));
	return {
		xPt: t,
		yPt: n,
		widthPt: r - t,
		heightPt: i - n
	};
}
function Tb(e) {
	let { paintOps: t, trailingSpaceCompressionPt: n, ...r } = e, i = t.find((e) => e.naturalAdvancePt === void 0) ?? t[0], a = {
		...r,
		letterSpacingPt: i?.letterSpacingPt ?? 0
	}, o = n === void 0 ? a : {
		...a,
		trailingSpaceCompressionPt: n
	};
	if (!e.sourceRuns) return [o];
	let s = n === void 0 ? e.range.end : e.range.start + e.text.replace(/ +$/u, "").length, c = (n ?? 0) / Math.max(1, e.range.end - s), l = 0;
	return e.sourceRuns.map((t) => {
		for (; l < e.clusters.length && e.clusters[l].range.end <= t.range.start;) l++;
		let n = l;
		for (; n < e.clusters.length && e.clusters[n].range.start < t.range.end;) n++;
		let r = e.clusters.slice(l, n), i = Infinity, o = -Infinity;
		for (let e of r) i = Math.min(i, e.offset.xPt), o = Math.max(o, e.offset.xPt + e.advancePt);
		r.length === 0 && (i = o = 0);
		let u = t.range.start === e.range.start && t.range.end === e.range.end, d = t.range.start - e.range.start, f = Math.max(0, t.range.end - Math.max(t.range.start, s));
		return {
			...a,
			...f > 0 && c > 0 ? { trailingSpaceCompressionPt: f * c } : {},
			sourceRuns: void 0,
			sourceRunIndex: t.sourceRunIndex,
			role: t.role ?? "content",
			dependency: t.dependency,
			range: t.range,
			text: e.text.slice(d, d + t.range.end - t.range.start),
			...e.semanticSlotSpans ? { semanticSlotSpans: Ds(e.semanticSlotSpans, d, d + t.range.end - t.range.start) } : {},
			origin: u ? e.origin : {
				...e.origin,
				xPt: e.origin.xPt + i
			},
			bounds: u ? e.bounds : {
				...e.bounds,
				xPt: e.bounds.xPt + i,
				widthPt: o - i
			},
			...e.highlightBounds ? { highlightBounds: u ? e.highlightBounds : {
				...e.highlightBounds,
				xPt: e.highlightBounds.xPt + i,
				widthPt: o - i
			} } : {},
			advancePt: u ? e.advancePt : o - i,
			clusters: u ? e.clusters : r.map((e) => ({
				...e,
				range: {
					start: Math.max(t.range.start, e.range.start),
					end: Math.min(t.range.end, e.range.end)
				},
				offset: {
					...e.offset,
					xPt: e.offset.xPt - i
				}
			}))
		};
	});
}
function Eb(e, t) {
	return Object.freeze({
		a: e.a * t.a + e.c * t.b,
		b: e.b * t.a + e.d * t.b,
		c: e.a * t.c + e.c * t.d,
		d: e.b * t.c + e.d * t.d,
		e: e.a * t.e + e.c * t.f + e.e,
		f: e.b * t.e + e.d * t.f + e.f
	});
}
function Db(e) {
	return Object.freeze({
		a: e,
		b: 0,
		c: 0,
		d: e,
		e: 0,
		f: 0
	});
}
function Ob(e, t) {
	return Object.freeze({
		a: 1,
		b: 0,
		c: 0,
		d: 1,
		e,
		f: t
	});
}
function kb(e) {
	return Object.freeze(e === 1 ? {
		a: 0,
		b: 1,
		c: -1,
		d: 0,
		e: 0,
		f: 0
	} : {
		a: 0,
		b: -1,
		c: 1,
		d: 0,
		e: 0,
		f: 0
	});
}
function Ab(e, t) {
	return {
		xPt: e.a * t.xPt + e.c * t.yPt + e.e,
		yPt: e.b * t.xPt + e.d * t.yPt + e.f
	};
}
function jb(e, t) {
	let n = e.a * e.d - e.b * e.c;
	if (!Number.isFinite(n) || n === 0) return null;
	let r = t.xPt - e.e, i = t.yPt - e.f, a = {
		xPt: (e.d * r - e.c * i) / n,
		yPt: (-e.b * r + e.a * i) / n
	};
	return Number.isFinite(a.xPt) && Number.isFinite(a.yPt) ? a : null;
}
function Mb(e, t) {
	if (!(e.b === 0 && e.c === 0 || e.a === 0 && e.d === 0)) return null;
	let n = [{
		xPt: t.xPt,
		yPt: t.yPt
	}, {
		xPt: t.xPt + t.widthPt,
		yPt: t.yPt + t.heightPt
	}].map((t) => jb(e, t));
	if (n.some((e) => e === null)) return null;
	let [r, i] = n, a = Math.min(r.xPt, i.xPt), o = Math.min(r.yPt, i.yPt);
	return Object.freeze({
		xPt: a,
		yPt: o,
		widthPt: Math.max(r.xPt, i.xPt) - a,
		heightPt: Math.max(r.yPt, i.yPt) - o
	});
}
function Nb(e, t) {
	let n = e.a * e.d - e.b * e.c;
	if (!Number.isFinite(n) || n === 0) return null;
	let r = {
		xPt: (e.d * t.xPt - e.c * t.yPt) / n,
		yPt: (-e.b * t.xPt + e.a * t.yPt) / n
	};
	return Number.isFinite(r.xPt) && Number.isFinite(r.yPt) ? r : null;
}
function Pb(e) {
	if (!e.some((e) => e.kind === "text" && e.text.includes(" "))) return;
	let t = [], n = [], r = !1;
	for (let i = 0; i < e.length; i += 1) {
		let a = e[i];
		if (n.push(t.length), a.kind === "text" && a.nativeVisiblePrefix) {
			let e = a.nativeVisiblePrefix, t = a.basePaintOps[0];
			if (a.nativeBaseDirection !== "rtl" || !a.text.endsWith(" ") || e.endUTF16 !== a.text.replace(/ +$/u, "").length || e.request.text !== a.text.slice(0, e.endUTF16) || e.request.baseDirection !== "rtl" || e.measurement.nativeBaseDirection !== "rtl" || e.request.fontRoute.fingerprint !== a.fontRoute.fingerprint || e.request.fontSizePt !== a.fontSizePt || e.request.weight !== a.fontWeight || e.request.style !== a.fontStyle || a.basePaintOps.length !== 1 || !t || t.text !== a.text || t.range.start !== a.range.start || t.range.end !== a.range.end || t.letterSpacingPt !== e.request.letterSpacingPt || t.scaleX !== 1 || t.scaleY !== void 0 && t.scaleY !== 1 || t.glyphOrientation !== void 0 || t.kerning !== (e.request.kerning === !0 ? "normal" : "none")) return;
		}
		if (a.kind === "text" && (a.fixedPitch || a.fitText || a.ruby || a.tateChuYoko || a.optionalHyphenGlyph || a.retainedGeometry?.emphasis || a.decorations.length > 0 && !a.retainedGeometry || a.basePaintOps.some((e) => e.writingMode !== "horizontal-tb" || e.sourceMapping === "kashida" || e.naturalAdvancePt !== void 0))) return;
		if (a.kind !== "text" || !a.text.includes(" ")) {
			t.push({
				parentIndex: i,
				startUTF16: 0,
				endUTF16: a.kind === "text" ? a.text.length : 0,
				spaceOnly: !1,
				firstCluster: -1,
				endCluster: -1,
				fromPt: 0,
				toPt: 0,
				firstOperation: 0,
				endOperation: 0
			});
			continue;
		}
		let o = [], s = 0;
		for (let e = 0; e < a.clusters.length; e += 1) {
			let t = a.clusters[e], n = a.text.slice(t.range.start - a.range.start, t.range.end - a.range.start);
			if (n.includes(" ")) {
				if (n !== " ") return;
				r = !0, s < e && o.push({
					first: s,
					end: e,
					space: !1
				}), o.push({
					first: e,
					end: e + 1,
					space: !0
				}), s = e + 1;
			}
		}
		if (s < a.clusters.length && o.push({
			first: s,
			end: a.clusters.length,
			space: !1
		}), o.length === 0 || a.basePaintOps.some((e) => e.text.replace(/ +$/u, "").includes(" "))) return;
		let c = 0;
		for (let e = 0; e < o.length; e += 1) {
			let n = o[e], r = a.clusters[n.first].range.start, s = a.clusters[n.end - 1].range.end, l = e === 0 ? 0 : a.clusters[n.first].offset.xPt, u = e + 1 === o.length ? a.measuredWidthPt : a.clusters[o[e + 1].first].offset.xPt;
			if (!Number.isFinite(l) || !Number.isFinite(u) || u < l) return;
			for (; a.basePaintOps[c] && a.basePaintOps[c].range.end <= r;) c += 1;
			let d = c, f, p, m = n.first;
			for (; d < a.basePaintOps.length; d += 1) {
				let e = a.basePaintOps[d];
				if (e.range.start >= s) break;
				let t = Math.max(r, e.range.start), i = Math.min(s, e.range.end);
				for (; m < n.end && a.clusters[m].range.start < t;) m += 1;
				let o = m < n.end ? a.clusters[m] : void 0;
				if (!o || o.range.start !== t || i <= t) return;
				f ??= t, p = i;
			}
			if (f !== r || p !== s) return;
			t.push({
				parentIndex: i,
				startUTF16: r - a.range.start,
				endUTF16: s - a.range.start,
				spaceOnly: n.space,
				firstCluster: n.first,
				endCluster: n.end,
				fromPt: l,
				toPt: u,
				firstOperation: c,
				endOperation: d
			});
		}
	}
	if (n.push(t.length), r) return {
		projection: t,
		materialize: () => Fb(e, t, n)
	};
}
function Fb(e, t, n) {
	let r = [], i = [];
	for (let a = 0; a < e.length; a += 1) {
		let o = e[a], s = n[a], c = n[a + 1];
		if (o.kind !== "text" || t[s].firstCluster < 0) {
			r.push(o), i.push(!1);
			continue;
		}
		let { textShapeRequest: l, textLayoutService: u, nativeVisiblePrefix: d, ...f } = o, p = 0, m = 0;
		for (let e = s; e < c; e += 1) {
			let n = t[e], a = e === s, c = o.range.start + n.startUTF16, l = o.range.start + n.endUTF16, { fromPt: u, toPt: h } = n, g = d && !n.spaceOnly && n.startUTF16 === 0 && n.endUTF16 === d.endUTF16 ? d : void 0, _ = [];
			for (let e = n.firstCluster; e < n.endCluster; e += 1) {
				let t = o.clusters[e];
				_.push(Object.is(u, 0) ? t : {
					...t,
					offset: {
						...t.offset,
						xPt: t.offset.xPt - u
					}
				});
			}
			let v = [], y = n.firstCluster;
			for (let e = n.firstOperation; e < n.endOperation; e += 1) {
				let t = o.basePaintOps[e], r = Math.max(c, t.range.start), i = Math.min(l, t.range.end);
				for (; o.clusters[y].range.start < r;) y += 1;
				let a = o.clusters[y], { inkBounds: s, blockAxisInkBounds: d, ...f } = t;
				v.push({
					...f,
					text: t.text.slice(r - t.range.start, i - t.range.start),
					range: {
						start: r,
						end: i
					},
					offset: {
						...t.offset,
						xPt: (r === t.range.start ? t.offset.xPt : a.offset.xPt) - u
					},
					...!n.spaceOnly && (g?.measurement.inkBounds ?? s) ? { inkBounds: g?.measurement.inkBounds ?? s } : {},
					...!n.spaceOnly && d ? { blockAxisInkBounds: g ? {
						startPt: (t.glyphOffsetPt?.yPt ?? 0) - g.measurement.inkBounds.ascentPt,
						endPt: (t.glyphOffsetPt?.yPt ?? 0) + g.measurement.inkBounds.descentPt
					} : d } : {}
				});
			}
			let b = c - o.range.start, x = l - o.range.start, S;
			if (o.sourceRuns) {
				for (; o.sourceRuns[p] && o.sourceRuns[p].range.end <= c;) p += 1;
				let e = [];
				for (let t = p; t < o.sourceRuns.length; t += 1) {
					let n = o.sourceRuns[t];
					if (n.range.start >= l) break;
					e.push({
						...n,
						range: {
							start: Math.max(c, n.range.start),
							end: Math.min(l, n.range.end)
						}
					});
				}
				S = e;
			}
			let C;
			if (o.semanticSlotSpans) {
				for (; o.semanticSlotSpans[m] && o.semanticSlotSpans[m].end <= b;) m += 1;
				let e = [];
				for (let t = m; t < o.semanticSlotSpans.length; t += 1) {
					let n = o.semanticSlotSpans[t];
					if (n.start >= x) break;
					e.push({
						...n,
						start: Math.max(b, n.start) - b,
						end: Math.min(x, n.end) - b
					});
				}
				C = e;
			}
			let w = {
				...f,
				breakBefore: a ? o.breakBefore : !0,
				text: o.text.slice(b, x),
				range: {
					start: c,
					end: l
				},
				measuredWidthPt: h - u,
				clusters: _,
				basePaintOps: v,
				...o.retainedGeometry && d ? { retainedGeometry: {
					...o.retainedGeometry,
					base: g ? {
						ascentPt: g.measurement.ascentPt,
						descentPt: g.measurement.descentPt,
						inkBounds: g.measurement.inkBounds
					} : n.spaceOnly ? {
						...o.retainedGeometry.base,
						inkBounds: {
							xMinPt: 0,
							xMaxPt: 0,
							ascentPt: 0,
							descentPt: 0
						}
					} : o.retainedGeometry.base
				} } : {},
				...S ? { sourceRuns: S } : {},
				...C ? { semanticSlotSpans: C } : {},
				autoSpace: a ? o.autoSpace : void 0,
				leadingSeamPairPt: a ? o.leadingSeamPairPt : void 0,
				decorationTerminalAdvancePt: o.decorationTerminalAdvancePt === void 0 ? void 0 : Math.max(0, Math.min(h, o.decorationTerminalAdvancePt) - u)
			};
			r.push(w), i.push(n.spaceOnly);
		}
	}
	return {
		segments: r,
		parentCellStarts: n,
		spaceOnly: i,
		projection: t
	};
}
function Ib(e, t, n) {
	let r = [], i = [0, 0], a = i, o = (e) => {
		let [n, o] = t(e);
		r.push({
			cmd: "moveTo",
			x: n,
			y: o
		}), i = e, a = e;
	}, s = (e) => {
		let [n, a] = t(e);
		r.push({
			cmd: "lineTo",
			x: n,
			y: a
		}), i = e;
	}, c = (e) => {
		let a = (i, o, s, c, l) => {
			n();
			let u = [
				.25,
				.5,
				.75
			].map((n) => t(e(i + (o - i) * n)));
			if (Math.max(...u.map((e, t) => {
				let n = (t + 1) / 4;
				return Math.hypot(e[0] - s[0] - (c[0] - s[0]) * n, e[1] - s[1] - (c[1] - s[1]) * n);
			})) <= 1 / 1024) {
				r.push({
					cmd: "lineTo",
					x: c[0],
					y: c[1]
				});
				return;
			}
			if (l >= 24) throw new H("VML projected vector cannot meet numerical precision");
			let d = (i + o) / 2;
			a(i, d, s, u[1], l + 1), a(d, o, u[1], c, l + 1);
		};
		a(0, 1, t(e(0)), t(e(1)), 0), i = e(1);
	}, l = (e, t, n, r, i, a, o, l) => {
		let u = o - a;
		l && u > 0 && (u = u >= 2 * Math.PI ? -2 * Math.PI : u - 2 * Math.PI), !l && u < 0 && (u = u <= -2 * Math.PI ? 2 * Math.PI : u + 2 * Math.PI);
		let d = (o) => {
			let s = a + u * o, c = n * Math.cos(s), l = r * Math.sin(s);
			return [e + c * Math.cos(i) - l * Math.sin(i), t + c * Math.sin(i) + l * Math.cos(i)];
		};
		s(d(0)), c(d);
	};
	for (let { op: t, args: u } of e) switch (n(), t) {
		case "moveTo":
			o([u[0], u[1]]);
			break;
		case "lineTo":
			s([u[0], u[1]]);
			break;
		case "closePath":
			r.push({ cmd: "close" }), i = a;
			break;
		case "quadraticCurveTo": {
			let e = i;
			c((t) => {
				let n = 1 - t;
				return [n * n * e[0] + 2 * n * t * u[0] + t * t * u[2], n * n * e[1] + 2 * n * t * u[1] + t * t * u[3]];
			});
			break;
		}
		case "bezierCurveTo": {
			let e = i;
			c((t) => {
				let n = 1 - t;
				return [n ** 3 * e[0] + 3 * n * n * t * u[0] + 3 * n * t * t * u[2] + t ** 3 * u[4], n ** 3 * e[1] + 3 * n * n * t * u[1] + 3 * n * t * t * u[3] + t ** 3 * u[5]];
			});
			break;
		}
		case "rect":
			o([u[0], u[1]]), s([u[0] + u[2], u[1]]), s([u[0] + u[2], u[1] + u[3]]), s([u[0], u[1] + u[3]]), r.push({ cmd: "close" }), i = a;
			break;
		case "arc":
			l(u[0], u[1], u[2], u[2], 0, u[3], u[4], !!u[5]);
			break;
		case "ellipse":
			l(u[0], u[1], u[2], u[3], u[4], u[5], u[6], !!u[7]);
			break;
		case "roundRect": {
			let e = u[4] === 0 ? Array.from({ length: 4 }, () => [u[5], u[5]]) : Array.from({ length: (u.length - 5) / 2 }, (e, t) => [u[5 + 2 * t], u[6 + 2 * t]]), t = (t) => e[t % e.length], n = t(0), c = e.length === 1 ? n : t(1), d = e.length === 2 ? n : t(2), f = e.length === 1 ? n : e.length === 2 || e.length === 3 ? c : t(3), p = u[0], m = u[1], h = p + u[2], g = m + u[3], _ = Math.min(1, u[2] / (n[0] + c[0] || 1), u[2] / (f[0] + d[0] || 1), u[3] / (n[1] + f[1] || 1), u[3] / (c[1] + d[1] || 1)), [v, y] = [n[0] * _, n[1] * _], [b, x] = [c[0] * _, c[1] * _], [S, C] = [d[0] * _, d[1] * _], [w, T] = [f[0] * _, f[1] * _];
			o([p + v, m]), s([h - b, m]), l(h - b, m + x, b, x, 0, -Math.PI / 2, 0, !1), s([h, g - C]), l(h - S, g - C, S, C, 0, 0, Math.PI / 2, !1), s([p + w, g]), l(p + w, g - T, w, T, 0, Math.PI / 2, Math.PI, !1), s([p, m + y]), l(p + v, m + y, v, y, 0, Math.PI, 1.5 * Math.PI, !1), r.push({ cmd: "close" }), i = a;
			break;
		}
	}
	return r;
}
function Lb(e, t, n = Infinity) {
	return t.a === 1 && t.b === 0 && t.c === 0 && t.d === 1 && t.e === 0 && t.f === 0 ? {
		...e,
		resolvedGeometry: e.resolvedGeometry ?? ve(e, 1, n)
	} : Rb(e, ([e, n]) => [t.a * e + t.c * n + t.e, t.b * e + t.d * n + t.f], n);
}
function Rb(e, t, n = Infinity) {
	n = Math.min(n, 1048576);
	let r = e.resolvedGeometry ?? ve(e, 1, n), i = r.workUnits, a = (e = 1) => {
		if (i += e, i > n) throw new H("VML affine geometry work budget exceeded");
	}, o = ([n, i]) => {
		a();
		let o = e.rect.x - r.originX, s = e.rect.y - r.originY, c = t([n + o, i + s]);
		return [c[0] - o, c[1] - s];
	}, s = (e, t = o) => Ib(e, t, a).map((e) => {
		if (e.cmd === "close") return a(), {
			op: "closePath",
			args: []
		};
		if (e.cmd !== "moveTo" && e.cmd !== "lineTo") throw Error("VML projection returned an unacquired curve");
		return a(3), {
			op: e.cmd,
			args: [e.x, e.y]
		};
	}), c = r.paths.map((e) => ({
		...e,
		path: s(e.path)
	})), l = s(r.fillSilhouette), u = r.arrows.map((e) => ({
		...e,
		tipX: 0,
		tipY: 0,
		angle: 0,
		geometry: {
			...e.geometry,
			path: s(e.geometry.path, ([t, n]) => o([e.tipX + Math.cos(e.angle) * t - Math.sin(e.angle) * n, e.tipY + Math.sin(e.angle) * t + Math.cos(e.angle) * n]))
		}
	}));
	return {
		...e,
		resolvedGeometry: {
			...r,
			paths: c,
			fillSilhouette: l,
			arrows: u,
			workUnits: i
		}
	};
}
function zb(e, t, n = Infinity) {
	return Lb(e, Bb(e, t), n);
}
function Bb(e, t) {
	let { x: n, y: r, w: i, h: a } = e.rect, [o, s, c, l, u, d] = t.matrix;
	if (u !== 0 || d !== 0) throw Error("Projective VML skew requires resolved reciprocal-factor semantics");
	let f = n + i / 2, p = r + a / 2, m = f + i * t.origin[0], h = p + a * t.origin[1], g = t.offset.xPt + t.offset.xFraction * i, _ = t.offset.yPt + t.offset.yFraction * a, v = e.transform.rotationDeg * Math.PI / 180, y = Math.cos(v), b = Math.sin(v), x = e.transform.flipH ? -1 : 1, S = e.transform.flipV ? -1 : 1, C = (e, t) => {
		let n = (e - f) * x, r = (t - p) * S, i = f + y * n - b * r - m, a = p + b * n + y * r - h, u = m + o * i + c * a + g - f, d = h + s * i + l * a + _ - p;
		return {
			x: f + x * (y * u + b * d),
			y: p + S * (-b * u + y * d)
		};
	}, w = C(0, 0), T = C(1, 0), E = C(0, 1);
	return {
		a: T.x - w.x,
		b: T.y - w.y,
		c: E.x - w.x,
		d: E.y - w.y,
		e: w.x,
		f: w.y
	};
}
function Vb(e, t) {
	let { x: n, y: r, w: i, h: a } = e.rect, o = e.transform.rotationDeg * Math.PI / 180, s = e.transform.flipH ? -1 : 1, c = e.transform.flipV ? -1 : 1, l = Math.cos(o) * s, u = Math.sin(o) * s, d = -Math.sin(o) * c, f = Math.cos(o) * c, p = n + i / 2, m = r + a / 2, h = {
		a: l,
		b: u,
		c: d,
		d: f,
		e: p - l * p - d * m,
		f: m - u * p - f * m
	}, g = (e, t) => {
		let n = jb(h, {
			xPt: e,
			yPt: t
		});
		if (!n) throw RangeError("Invalid VML host orientation");
		return n;
	}, _ = g(0, 0), v = g(1, 0), y = g(0, 1);
	return Eb({
		a: v.xPt - _.xPt,
		b: v.yPt - _.yPt,
		c: y.xPt - _.xPt,
		d: y.yPt - _.yPt,
		e: _.xPt,
		f: _.yPt
	}, Eb(t, h));
}
function Hb(e, t = Infinity) {
	let n = e.resolvedGeometry, r = ve(e, 1, t);
	if (!n) return r;
	let i = r.workUnits + n.workUnits;
	if (i > t) throw new H("VML geometry pass work budget exceeded");
	if (!e.stroke) return {
		...r,
		originX: n.originX,
		originY: n.originY,
		paths: n.paths.map((e) => ({
			...e,
			stroke: null
		})),
		fillSilhouette: n.fillSilhouette,
		arrows: [],
		workUnits: i
	};
	if (r.paths.length !== n.paths.length) throw Error("VML geometry pass changed path scheduling");
	return {
		...r,
		originX: n.originX,
		originY: n.originY,
		paths: r.paths.map((e, t) => ({
			...e,
			path: n.paths[t].path
		})),
		fillSilhouette: n.fillSilhouette,
		arrows: r.arrows.map((e, t) => {
			let r = n.arrows[t];
			if (!r) throw Error("VML geometry pass changed arrow scheduling");
			return {
				...e,
				tipX: r.tipX,
				tipY: r.tipY,
				angle: r.angle,
				geometry: {
					...e.geometry,
					path: r.geometry.path
				}
			};
		}),
		workUnits: i
	};
}
function Ub(e, t, n) {
	let r = t.xPt, i = t.yPt, a = r + t.widthPt, o = i + t.heightPt, s = (e, t) => {
		r = Math.min(r, e), i = Math.min(i, t), a = Math.max(a, e), o = Math.max(o, t);
	};
	for (let t of e) if (t.kind === "drawingml-shape") {
		let e = ye(t.plan, n);
		e && (s(e.x, e.y), s(e.x + e.w, e.y + e.h));
	} else if (t.kind === "watermark-text") {
		let e = t.rect, r = e.xPt + e.widthPt / 2, i = e.yPt + e.heightPt / 2, a = t.fitShape ? e.widthPt : t.sourceBounds.widthPt, o = t.fitShape ? e.heightPt : t.sourceBounds.heightPt, c = t.rotationDeg * Math.PI / 180, l = Math.cos(c), u = Math.sin(c), d = t.maskBounds ?? {
			xPt: e.xPt,
			yPt: e.yPt,
			widthPt: a,
			heightPt: o
		};
		for (let [e, a] of [
			[0, 0],
			[d.widthPt, 0],
			[d.widthPt, d.heightPt],
			[0, d.heightPt]
		]) {
			let o = (d.xPt + e - r) * (t.flipH ? -1 : 1), c = (d.yPt + a - i) * (t.flipV ? -1 : 1), f = r + o * l - c * u, p = i + o * u + c * l;
			s(n ? n.a * f + n.c * p + n.e : f, n ? n.b * f + n.d * p + n.f : p);
		}
	}
	return {
		xPt: r,
		yPt: i,
		widthPt: a - r,
		heightPt: o - i
	};
}
function Wb(e, t, n = Infinity, r = t.rect) {
	let i = e.vmlShadow;
	if (!i || i.opacity === 0) return [];
	n = Math.min(n, 1048576);
	let { x: a, y: o, w: s, h: c } = t.rect, l = r, u = 0, d = (e = 1) => {
		if (u += e, u > n) throw new H("VML shadow geometry allowance exceeded");
	}, f = [], p = i.kind === "double" || i.kind === "emboss" ? [[i.offset, i.color], [i.offset2, i.color2]] : [[i.offset, i.color]];
	for (let [r, m] of p) {
		let p = r.xPt + r.xFraction * l.w, h = r.yPt + r.yFraction * l.h, g = t.stroke ? {
			...t.stroke,
			color: m
		} : null;
		g && delete g.fill;
		let _ = {
			...t,
			rect: {
				x: a + p,
				y: o + h,
				w: s,
				h: c
			},
			fill: !i.obscured || e.fill || e.vmlPicture ? {
				fillType: "solid",
				color: m
			} : null,
			stroke: g,
			resolvedGeometry: t.resolvedGeometry
		};
		if (i.kind === "perspective") {
			let [e, r, m, g, v, y] = i.matrix, b = l.x + l.w * (.5 + i.origin[0]), x = l.y + l.h * (.5 + i.origin[1]), S = t.transform.rotationDeg * Math.PI / 180, C = Math.cos(S), w = Math.sin(S), T = (n) => {
				d();
				let l = (n[0] - (a + s / 2)) * (t.transform.flipH ? -1 : 1), u = (n[1] - (o + c / 2)) * (t.transform.flipV ? -1 : 1), f = a + s / 2 + C * l - w * u - b, _ = o + c / 2 + w * l + C * u - x, S = 1 + (i.absolutePerspective ? 12700 * (v * f + y * _) : v * f / (s || 1) + y * _ / (c || 1));
				if (S === 0 || !Number.isFinite(S)) throw RangeError("VML shadow crosses the perspective horizon");
				return [b + (e * f + m * _ + p) / S, x + (r * f + g * _ + h) / S];
			};
			if (!t.resolvedGeometry) throw Error("VML shadow requires acquired source geometry");
			let E = {
				..._,
				rect: t.rect
			}, D = Hb(E, n - u);
			d(D.workUnits);
			let O = Rb({
				...E,
				resolvedGeometry: D
			}, T, n - u);
			d(O.resolvedGeometry.workUnits), f.push({
				kind: "drawingml-shape",
				shadowPass: !0,
				plan: {
					...O,
					transform: {
						rotationDeg: 0,
						flipH: !1,
						flipV: !1
					}
				},
				opacity: i.opacity
			});
			continue;
		}
		let v = Hb(_, n - u);
		d(v.workUnits), f.push({
			kind: "drawingml-shape",
			shadowPass: !0,
			plan: {
				..._,
				resolvedGeometry: v
			},
			opacity: i.opacity
		});
	}
	return f;
}
function Gb(e, t, n) {
	let r = e.group?.resolvedChildFrame;
	if (!r) return t;
	let i = e.extent.widthPt, a = e.extent.heightPt;
	if (e.extent.widthStatus !== "valid" || e.extent.heightStatus !== "valid" || i === null || a === null || i <= 0 || a <= 0) throw Error("resolved grouped anchor requires its authored wp:extent");
	let o = n === void 0 ? t : th(n.logicalToPhysical, t), s = o.widthPt / i, c = o.heightPt / a, l = {
		xPt: o.xPt + r.offsetXPt * s,
		yPt: o.yPt + r.offsetYPt * c,
		widthPt: r.widthPt * s,
		heightPt: r.heightPt * c
	};
	return n === void 0 ? l : th(n.physicalToLogical, l);
}
function Kb(e, t, n, r = Infinity) {
	if (e.status !== "planned") return e;
	let [i, a, o, s, c, l] = t, u = {
		a: i,
		b: a,
		c: o,
		d: s,
		e: n.xPt + c - i * n.xPt - o * n.yPt,
		f: n.yPt + l - a * n.xPt - s * n.yPt
	}, d = r, f = (e) => {
		if (e.kind === "noop") return e;
		if (e.kind === "watermark-text") {
			let t = e.rect, n = Vb({
				rect: {
					x: t.xPt,
					y: t.yPt,
					w: t.widthPt,
					h: t.heightPt
				},
				transform: {
					rotationDeg: e.rotationDeg,
					flipH: e.flipH ?? !1,
					flipV: e.flipV ?? !1
				}
			}, u), r = e.maskBounds, i = r ? [
				{
					xPt: r.xPt,
					yPt: r.yPt
				},
				{
					xPt: r.xPt + r.widthPt,
					yPt: r.yPt
				},
				{
					xPt: r.xPt + r.widthPt,
					yPt: r.yPt + r.heightPt
				},
				{
					xPt: r.xPt,
					yPt: r.yPt + r.heightPt
				}
			].map((e) => Ab(n, e)) : [], a = Math.min(...i.map((e) => e.xPt)), o = Math.min(...i.map((e) => e.yPt));
			return {
				...e,
				glyphTransform: e.glyphTransform ? Eb(n, e.glyphTransform) : n,
				...r ? { maskBounds: {
					xPt: a,
					yPt: o,
					widthPt: Math.max(...i.map((e) => e.xPt)) - a,
					heightPt: Math.max(...i.map((e) => e.yPt)) - o
				} } : {}
			};
		}
		let t = Vb(e.plan, u), n = Lb(e.plan, t, d);
		d -= n.resolvedGeometry.workUnits;
		let r = e.kind === "drawingml-image-fill" && e.strokeMask ? ye({
			...n,
			transform: {
				rotationDeg: 0,
				flipH: !1,
				flipV: !1
			}
		}) : null;
		return {
			...e,
			plan: n,
			...r ? { maskBounds: {
				xPt: r.x,
				yPt: r.y,
				widthPt: r.w,
				heightPt: r.h
			} } : {}
		};
	}, p = e.before?.map(f).filter((e) => e.kind !== "noop");
	return Z({
		...e,
		...p ? { before: p } : {},
		command: f(e.command)
	}, "VML group vectors");
}
function qb(e, t, n, r = Infinity) {
	let { sourceBounds: i, fitShape: a } = t, o = t.pathSlices, s = (e) => {
		if (o?.length) {
			let t = o[Math.max(0, Math.min(o.length - 1, Math.floor((e.x - i.xPt) / o[0].sourceWidth)))];
			return {
				x: t.xPt + t.a * (e.x - t.sourceX) + t.c * e.y,
				y: t.yPt + t.b * (e.x - t.sourceX) + t.d * e.y
			};
		}
		return {
			x: (e.x - i.xPt) * (a ? n.widthPt / i.widthPt : 1),
			y: (e.y - i.yPt) * (a ? n.heightPt / i.heightPt : 1)
		};
	}, c = 0, l = Math.min(r ?? Infinity, 1048576), u = e.map((e) => {
		let r = [], a = (e) => {
			if (++c > l) throw RangeError("VML fitted glyph contour work budget exceeded");
			let i = s(e), a = t.glyphTransform, o = n.xPt + i.x, u = n.yPt + i.y;
			r.push(a ? {
				x: a.a * o + a.c * u + a.e,
				y: a.b * o + a.d * u + a.f
			} : {
				x: o,
				y: u
			});
		};
		for (let t = 0; t < e.length; t++) {
			let n = e[t], r = e[(t + 1) % e.length];
			if (a(n), o?.length && n.x !== r.x) {
				let e = o[0].sourceWidth, t = Math.max(1, Math.floor((Math.min(n.x, r.x) - i.xPt) / e) + 1), s = Math.min(o.length - 1, Math.ceil((Math.max(n.x, r.x) - i.xPt) / e) - 1);
				for (let e = 0; e <= s - t; e++) {
					let i = o[r.x > n.x ? t + e : s - e], c = i.sourceX - i.sourceWidth / 2;
					a({
						x: c,
						y: n.y + (r.y - n.y) * (c - n.x) / (r.x - n.x)
					});
				}
			}
		}
		return [...r.map((e, t) => ({
			cmd: t === 0 ? "moveTo" : "lineTo",
			...e
		})), { cmd: "close" }];
	}), d = n;
	if (n.widthPt === 0 || n.heightPt === 0) {
		let e = n.xPt + n.widthPt / 2, t = n.yPt + n.heightPt / 2, r = 0, i = 0;
		for (let n of u) for (let a of n) "x" in a && "y" in a && (r = Math.max(r, Math.abs(a.x - e)), i = Math.max(i, Math.abs(a.y - t)));
		if (r === 0 || i === 0) throw RangeError("VML fitted glyph contours have no ink frame");
		d = {
			xPt: e - r,
			yPt: t - i,
			widthPt: 2 * r,
			heightPt: 2 * i
		};
	}
	return {
		subpaths: u.map((e) => e.map((e) => "x" in e && "y" in e ? {
			...e,
			x: (e.x - d.xPt) / d.widthPt,
			y: (e.y - d.yPt) / d.heightPt
		} : e)),
		bounds: d,
		workUnits: c
	};
}
function Jb(e) {
	let t = e.fill;
	if (t?.fillType !== "gradient" || t.path !== "shape") return;
	let n = [...t.stops].sort((e, t) => e.position - t.position);
	if (!n.length) return;
	let r = (e) => {
		let t = 0, r = n.length;
		for (; t < r;) {
			let i = Math.floor((t + r) / 2);
			n[i].position <= e ? t = i + 1 : r = i;
		}
		let i = Math.max(0, t - 1), a = n[i], o = n[Math.min(i + 1, n.length - 1)], s = Math.max(0, Math.min(1, (e - a.position) / (o.position - a.position || 1))), c = (e) => {
			let t = e.replace(/^#/u, "");
			return [
				0,
				2,
				4,
				6
			].map((e) => e === 6 && t.length === 6 ? 255 : parseInt(t.slice(e, e + 2), 16));
		}, l = c(a.color), u = c(o.color);
		return `#${l.map((e, t) => Math.round(e + (u[t] - e) * s).toString(16).padStart(2, "0")).join("")}`;
	}, i = t.fillToRect, a = i?.l ?? 0, o = i?.t ?? 0, s = 1 - a - (i?.r ?? 1), c = 1 - o - (i?.b ?? 1), l = ye({
		...e,
		transform: {
			rotationDeg: 0,
			flipH: !1,
			flipV: !1
		}
	});
	return {
		...l ? { bounds: {
			xPt: l.x,
			yPt: l.y,
			widthPt: l.w,
			heightPt: l.h
		} } : {},
		focus: {
			l: a,
			t: o,
			width: s,
			height: c
		},
		rings: Array.from({ length: 256 }, (e, t) => ({
			outside: 1 - t / 256,
			inside: 1 - (t + 1) / 256,
			color: r(1 - t / 256)
		})),
		centerColor: r(0)
	};
}
function Yb(e, t, n, r, i = Infinity) {
	i = Math.min(i, 1048576);
	let a = 0, o = (e = 1) => {
		if (a += e, a > i) throw new H("VML text path work budget exceeded");
	}, s = [], c = [], l = {
		x: 0,
		y: 0
	}, u = (e, t) => {
		o(), l = {
			x: e,
			y: t
		}, c.push(l);
	}, d = () => {
		c.length > 1 && s.push(c), c = [];
	}, f = (e) => {
		for (let t = 1; t <= 48; t++) {
			let n = e(t / 48);
			u(n.x, n.y);
		}
	}, p = (e, t, n, r, i, a, o, s = !1) => {
		let c = o - a;
		s && c > 0 && (c -= Math.PI * 2), !s && c < 0 && (c += Math.PI * 2), f((o) => {
			let s = a + c * o;
			return {
				x: e + n * Math.cos(s) * Math.cos(i) - r * Math.sin(s) * Math.sin(i),
				y: t + n * Math.cos(s) * Math.sin(i) + r * Math.sin(s) * Math.cos(i)
			};
		});
	};
	!n.xScale && e.presetGeometry === "line" ? s.push([{
		x: 0,
		y: 0
	}, {
		x: t.widthPt,
		y: t.heightPt
	}]) : n.xScale || e.subpaths.length === 0 ? s.push([{
		x: 0,
		y: t.heightPt
	}, {
		x: t.widthPt,
		y: t.heightPt
	}]) : (me({
		moveTo: (e, t) => {
			d(), u(e, t);
		},
		lineTo: u,
		bezierCurveTo: (e, t, n, r, i, a) => {
			let o = l;
			f((s) => ({
				x: (1 - s) ** 3 * o.x + 3 * (1 - s) ** 2 * s * e + 3 * (1 - s) * s * s * n + s ** 3 * i,
				y: (1 - s) ** 3 * o.y + 3 * (1 - s) ** 2 * s * t + 3 * (1 - s) * s * s * r + s ** 3 * a
			}));
		},
		quadraticCurveTo: (e, t, n, r) => {
			let i = l;
			f((a) => ({
				x: (1 - a) ** 2 * i.x + 2 * (1 - a) * a * e + a * a * n,
				y: (1 - a) ** 2 * i.y + 2 * (1 - a) * a * t + a * a * r
			}));
		},
		ellipse: p,
		arc: (e, t, n, r, i, a) => p(e, t, n, n, 0, r, i, a),
		closePath: () => {
			c[0] && u(c[0].x, c[0].y);
		},
		rect: (e, t, n, r) => {
			d(), u(e, t), u(e + n, t), u(e + n, t + r), u(e, t + r), u(e, t);
		},
		roundRect: () => {
			throw Error("Custom VML paths cannot contain roundRect");
		}
	}, e.subpaths, 0, 0, t.widthPt, t.heightPt), d());
	let m = s[s.length - 1];
	if (!m) return [];
	let h = (e) => {
		let t = [0];
		for (let n = 1; n < e.length; n++) t.push(t[n - 1] + Math.hypot(e[n].x - e[n - 1].x, e[n].y - e[n - 1].y));
		return t;
	}, g = h(m), _ = g[g.length - 1], v = s.length > 1 ? s[0] : void 0, y = v ? h(v) : void 0, b = n.fitPath || n.fitShape ? _ / r.sourceBounds.widthPt : 1, x = m.length === 2 && (!v || v.length === 2 && v[1].x - v[0].x === m[1].x - m[0].x && v[1].y - v[0].y === m[1].y - m[0].y) ? 1 : 256;
	return o(x * r.spans.reduce((e, t) => e + t.text.length, 0)), Array.from({ length: x }, (e, i) => {
		o();
		let a = r.sourceBounds.widthPt / x, s = r.sourceBounds.xPt + (i + .5) * a, c = _ > 0 ? (i + .5) * a * b / _ : 0, l = xe(m, g, c), u = v && y ? xe(v, y, c) : void 0, d = n.fitShape ? (u ? Math.hypot(l.x - u.x, l.y - u.y) : t.heightPt) / r.sourceBounds.heightPt : n.fitPath ? b : 1, f = r.sourceBounds.yPt + r.sourceBounds.heightPt, p = n.fitShape && u ? (l.x - u.x) / r.sourceBounds.heightPt : -l.ty * d, h = n.fitShape && u ? (l.y - u.y) / r.sourceBounds.heightPt : l.tx * d;
		return {
			sourceX: s,
			sourceWidth: a,
			xPt: l.x - (n.fitShape ? f * p : 0),
			yPt: l.y - (n.fitShape ? f * h : 0),
			a: l.tx * b,
			b: l.ty * b,
			c: p,
			d: h
		};
	});
}
var Xb = 1;
function Zb(e) {
	return Object.freeze({
		status: "unsupported",
		command: Object.freeze({ kind: "noop" }),
		diagnostics: Object.freeze([Object.freeze({
			code: "UNSUPPORTED_FEATURE",
			severity: "error",
			message: e
		})])
	});
}
function Qb(e) {
	return e ? {
		type: e.type,
		w: e.w,
		len: e.len
	} : void 0;
}
function $b(e) {
	if (e) return e.fillType === "gradient" ? {
		fillType: "gradient",
		stops: e.stops.map((e) => ({
			position: e.position,
			color: e.color
		})),
		angle: e.angle,
		gradType: e.gradType,
		...e.scaled === void 0 ? {} : { scaled: e.scaled },
		...e.path === void 0 ? {} : { path: e.path },
		...e.fillToRect === void 0 ? {} : { fillToRect: { ...e.fillToRect } },
		...e.tileRect === void 0 ? {} : { tileRect: { ...e.tileRect } },
		...e.flip === void 0 ? {} : { flip: e.flip },
		...e.rotWithShape === void 0 ? {} : { rotWithShape: e.rotWithShape }
	} : {
		fillType: "pattern",
		fg: e.fg,
		bg: e.bg,
		preset: e.preset
	};
}
function ex(e) {
	if (!e.stroke || !e.strokeWidth || e.strokeWidth <= 0) return null;
	let t = $b(e.strokeFill);
	return {
		color: e.stroke,
		width: e.strokeWidth,
		...t ? { fill: t } : {},
		...e.strokeDash ? { dashStyle: e.strokeDash } : {},
		...e.strokeCustomDash?.length ? { customDash: e.strokeCustomDash } : {},
		...e.strokeCap ? { lineCap: e.strokeCap } : {},
		...e.strokeJoin ? { lineJoin: e.strokeJoin } : {},
		...e.strokeMiterLimit !== void 0 && e.strokeMiterLimit !== null ? { miterLimit: e.strokeMiterLimit } : {},
		...e.strokeAlignment ? { alignment: e.strokeAlignment } : {},
		...e.strokeCompound ? { cmpd: e.strokeCompound } : {},
		...Qb(e.headEnd) ? { headEnd: Qb(e.headEnd) } : {},
		...Qb(e.tailEnd) ? { tailEnd: Qb(e.tailEnd) } : {}
	};
}
function tx(e, t, n, r, i, a, o, s) {
	let c = r !== void 0 && (r.textPathOk !== void 0 || r.on !== void 0 || r.fitShape !== void 0 || r.fitPath !== void 0 || r.trim !== void 0 || r.xScale !== void 0);
	if (r !== void 0 && (!c || r.textPathOk === !0 && r.on === !0)) {
		if (r.string.trim().length === 0) return Object.freeze({
			status: "planned",
			command: Object.freeze({ kind: "noop" })
		});
		if (!n) throw Error("Shape textPath acquisition requires TextLayoutService");
		let o = c ? r.fitShape === !0 : !0, l = r.fitPath === !0;
		if (r.fontSizePt !== void 0 && (!Number.isFinite(r.fontSizePt) || r.fontSizePt < 0)) throw RangeError("VML textPath fontSizePt must be finite and non-negative");
		if (!o && !l && r.fontSizePt === void 0) return Zb("VML textPath fitShape=false requires an authored font-size");
		if (r.fontSizePt === 0) return Object.freeze({
			status: "planned",
			command: Object.freeze({ kind: "noop" })
		});
		let u = r.fontSizePt ?? Xb, d = r.fontFamily ?? void 0, f = n.shape({
			text: r.string,
			fontSizePt: u,
			fonts: {
				ascii: d,
				highAnsi: d,
				eastAsia: d,
				complexScript: d
			},
			weight: r.bold ? 700 : 400,
			style: r.italic ? "italic" : "normal",
			measure: !0
		});
		if (r.trim === !0 && !f.inkBounds) return Zb("VML textPath trim=true requires glyph ink bounds");
		let p = r.trim === !0 ? f.inkBounds?.xMinPt ?? 0 : 0, m = r.trim === !0 ? f.inkBounds?.xMaxPt ?? 0 : f.advancePt, h = r.trim === !0 ? f.inkBounds?.ascentPt ?? 0 : f.ascentPt, g = r.trim === !0 ? f.inkBounds?.descentPt ?? 0 : f.descentPt, _ = {
			xPt: p,
			yPt: -h,
			widthPt: m - p,
			heightPt: h + g
		};
		if (!Number.isFinite(f.advancePt) || Object.values(_).some((e) => !Number.isFinite(e)) || f.spans.some((e) => !Number.isFinite(e.advancePt))) throw Error("Shape textPath acquisition produced non-finite metrics");
		if (_.widthPt <= 0 || _.heightPt <= 0 || f.spans.length === 0) return Zb("VML textPath produced empty glyph metrics");
		let v = Z({
			kind: "watermark-text",
			rect: { ...t },
			text: r.string,
			...e.fill?.fillType === "image" ? {
				imageResourceKey: i,
				imageRotationDeg: e.fill.vml?.alignShape === !1 ? 0 : e.rotation ?? 0,
				...e.fill.vml?.alignShape === !1 ? {
					imageFlipH: e.flipH ?? !1,
					imageFlipV: e.flipV ?? !1
				} : {}
			} : {},
			fill: e.fill?.fillType === "image" ? {
				fillType: "solid",
				color: "FFFFFF"
			} : e.fill ? {
				...e.fill,
				...e.fill.fillType === "gradient" ? { stops: e.fill.stops.map((e) => ({ ...e })) } : {}
			} : null,
			opacity: Math.max(0, Math.min(1, e.fillOpacity ?? 1)),
			rotationDeg: e.rotation ?? 0,
			flipH: e.flipH ?? !1,
			flipV: e.flipV ?? !1,
			...e.vmlSkew ? { glyphTransform: Bb({
				rect: {
					x: t.xPt,
					y: t.yPt,
					w: t.widthPt,
					h: t.heightPt
				},
				transform: {
					rotationDeg: e.rotation ?? 0,
					flipH: e.flipH ?? !1,
					flipV: e.flipV ?? !1
				}
			}, e.vmlSkew) } : {},
			fitShape: o,
			fontSizePt: u,
			sourceBounds: _,
			spans: f.spans.map((e) => ({
				text: e.text,
				advancePt: e.advancePt,
				fontRoute: e.fontRoute,
				fontWeight: e.font.weight,
				fontStyle: e.font.style
			}))
		}, "VML textPath command"), y = r.fitPath || r.xScale || e.subpaths.length ? Z({
			...v,
			pathSlices: Yb(e, t, r, v, a)
		}, "VML fitted path text") : v, b = ex(e);
		if (y.imageResourceKey || b || e.vmlSkew || e.vmlGroupTransform || e.vmlShadow) {
			let e = f.inkBounds ? {
				xPt: f.inkBounds.xMinPt,
				yPt: -f.inkBounds.ascentPt,
				widthPt: f.inkBounds.xMaxPt - f.inkBounds.xMinPt,
				heightPt: f.inkBounds.ascentPt + f.inkBounds.descentPt
			} : _, n = [], r = [
				[e.xPt, e.yPt],
				[e.xPt + e.widthPt, e.yPt],
				[e.xPt + e.widthPt, e.yPt + e.heightPt],
				[e.xPt, e.yPt + e.heightPt]
			];
			if (y.pathSlices) for (let e of y.pathSlices) for (let r of [-e.sourceWidth / 2, e.sourceWidth / 2]) for (let i of [_.yPt, _.yPt + _.heightPt]) n.push({
				x: t.xPt + e.xPt + e.a * r + e.c * i,
				y: t.yPt + e.yPt + e.b * r + e.d * i
			});
			else {
				let e = o ? t.widthPt / _.widthPt : 1, i = o ? t.heightPt / _.heightPt : 1;
				for (let [a, o] of r) n.push({
					x: t.xPt + (a - _.xPt) * e,
					y: t.yPt + (o - _.yPt) * i
				});
			}
			if (v.glyphTransform) {
				let e = v.glyphTransform;
				for (let t of n) {
					let n = t.x, r = t.y;
					t.x = e.a * n + e.c * r + e.e, t.y = e.b * n + e.d * r + e.f;
				}
			}
			if (n.length) {
				let e = Math.min(...n.map((e) => e.x)), t = Math.min(...n.map((e) => e.y));
				y = Z({
					...y,
					maskBounds: {
						xPt: e - (b?.width ?? 0),
						yPt: t - (b?.width ?? 0),
						widthPt: Math.max(...n.map((e) => e.x)) - e + 2 * (b?.width ?? 0),
						heightPt: Math.max(...n.map((e) => e.y)) - t + 2 * (b?.width ?? 0)
					}
				}, "VML image text ink");
			}
		}
		let { imageResourceKey: x, imageRotationDeg: S, imageFlipH: C, imageFlipV: w, ...T } = y, E = e.vmlShadow, D = E && !b && E.kind !== "perspective" && E.opacity > 0 ? (E.kind === "single" ? [[E.offset, E.color]] : [[E.offset, E.color], [E.offset2, E.color2]]).map(([n, r]) => Z({
			...T,
			rect: {
				...t,
				xPt: t.xPt + n.xPt + n.xFraction * t.widthPt,
				yPt: t.yPt + n.yPt + n.yFraction * t.heightPt
			},
			...T.glyphTransform ? { glyphTransform: {
				...T.glyphTransform,
				e: T.glyphTransform.e + (1 - T.glyphTransform.a) * (n.xPt + n.xFraction * t.widthPt) - T.glyphTransform.c * (n.yPt + n.yFraction * t.heightPt),
				f: T.glyphTransform.f + (1 - T.glyphTransform.d) * (n.yPt + n.yFraction * t.heightPt) - T.glyphTransform.b * (n.xPt + n.xFraction * t.widthPt)
			} } : {},
			...T.maskBounds ? { maskBounds: {
				...T.maskBounds,
				xPt: T.maskBounds.xPt + n.xPt + n.xFraction * t.widthPt,
				yPt: T.maskBounds.yPt + n.yPt + n.yFraction * t.heightPt
			} } : {},
			fill: e.fill || !E.obscured ? {
				fillType: "solid",
				color: r
			} : null,
			opacity: E.opacity
		}, "VML text shadow")) : [], O = [], k = E?.kind === "perspective" && E.matrix[4] === 0 && E.matrix[5] === 0;
		if (b || k && E.opacity > 0) {
			let r = y.pathSlices?.map((e) => Math.hypot(e.a, e.b, e.c, e.d)) ?? [o ? Math.max(t.widthPt / _.widthPt, t.heightPt / _.heightPt) : 1];
			if (!n.glyphContours || !f.inkBounds) O.push({
				code: "UNSUPPORTED_FEATURE",
				severity: "error",
				message: "VML text decoration requires native glyph contours"
			});
			else {
				let i = e.vmlGroupTransform ? Math.hypot(...e.vmlGroupTransform.slice(0, 4)) : 1, o = k ? Math.hypot(...E.matrix.slice(0, 4)) : 1, c = n.glyphContours({
					spans: f.spans,
					fontSizePt: u,
					...f.nativeBaseDirection === void 0 ? {} : { baseDirection: f.nativeBaseDirection },
					ink: f.inkBounds,
					maximumScale: Math.max(...r) * Math.max(1, i) * Math.max(1, o) * (v.glyphTransform ? Math.hypot(v.glyphTransform.a, v.glyphTransform.b, v.glyphTransform.c, v.glyphTransform.d) : 1),
					maximumWork: a ?? Infinity
				});
				if (!c?.length) O.push({
					code: "UNSUPPORTED_FEATURE",
					severity: "error",
					message: "Native glyph contours are unavailable at the bounded outline precision"
				});
				else {
					let n = qb(c, y, t, a), r = {
						...e,
						presetGeometry: null,
						subpaths: n.subpaths,
						subpathPaint: [],
						fill: null,
						vmlPicture: void 0,
						vmlEdgeStrokes: void 0,
						vmlSkew: void 0,
						vmlConcentricGradient: !1,
						vmlShadow: void 0,
						headEnd: null,
						tailEnd: null
					}, i = Math.min(a ?? Infinity, 1048576) - n.workUnits;
					if (E && (k || E.kind !== "perspective")) {
						let r = n.bounds, a = {
							rect: {
								x: r.xPt,
								y: r.yPt,
								w: r.widthPt,
								h: r.heightPt
							},
							geometry: {
								kind: "custom",
								subpaths: n.subpaths
							},
							fill: e.fill ? {
								fillType: "solid",
								color: E.color
							} : null,
							stroke: b,
							transform: {
								rotationDeg: e.rotation ?? 0,
								flipH: e.flipH ?? !1,
								flipV: e.flipV ?? !1
							}
						}, o = ve(a, 1, i);
						i -= o.workUnits;
						let s = Wb(e, {
							...a,
							resolvedGeometry: o
						}, i, {
							x: t.xPt,
							y: t.yPt,
							w: t.widthPt,
							h: t.heightPt
						});
						D.push(...s), i -= s.reduce((e, t) => e + t.plan.resolvedGeometry.workUnits, 0);
					}
					if (b) {
						let e = nx(r, n.bounds, void 0, void 0, void 0, i, void 0, s);
						if (e.status !== "planned") throw Error("VML text outline acquisition failed");
						if (D.push(...e.before ?? []), D.push(y), e.command.kind === "noop") throw Error("VML text outline produced no command");
						y = e.command;
					}
				}
			}
		}
		return E?.kind === "perspective" && !k && O.push({
			code: "UNSUPPORTED_FEATURE",
			severity: "error",
			message: "VML projective text shadow requires resolved reciprocal-factor semantics"
		}), Object.freeze({
			status: "planned",
			command: y,
			...D.length ? { before: D } : {},
			...O.length ? { diagnostics: O } : {}
		});
	}
	let l = {
		rect: {
			x: t.xPt,
			y: t.yPt,
			w: t.widthPt,
			h: t.heightPt
		},
		geometry: e.presetGeometry ? {
			kind: "preset",
			name: e.presetGeometry,
			adjustments: [...e.adjValues ?? []]
		} : {
			kind: "custom",
			subpaths: e.subpaths.map((e) => e.map((e) => ({ ...e }))),
			...e.subpathPaint?.length && e.subpathPaint.length === e.subpaths.length ? { paint: e.subpathPaint.map((e) => ({ ...e })) } : {}
		},
		fill: e.fill && e.fill.fillType !== "image" ? {
			...e.fill,
			...e.fill.fillType === "gradient" ? { stops: e.fill.stops.map((e) => ({ ...e })) } : {}
		} : null,
		stroke: ex(e),
		transform: {
			rotationDeg: e.rotation ?? 0,
			flipH: e.flipH ?? !1,
			flipV: e.flipV ?? !1
		}
	};
	e.vmlSkew && (l = zb(l, e.vmlSkew, a));
	let u = {
		...l,
		resolvedGeometry: l.resolvedGeometry ?? ve(l, 1, a)
	}, d = Wb(e, u, (a ?? Infinity) - u.resolvedGeometry.workUnits), f = (a ?? Infinity) - u.resolvedGeometry.workUnits - d.reduce((e, t) => e + (t.plan.resolvedGeometry?.workUnits ?? 0), 0), p = (e) => {
		let t = Hb(e, f);
		return f -= t.workUnits, {
			...e,
			resolvedGeometry: t
		};
	};
	if (e.vmlPicture) {
		if (!o) throw Error("VML picture requires a retained image resource key");
		let t = p({
			...l,
			stroke: null
		}), n = [...d];
		if (e.fill?.fillType === "image") {
			if (!i) throw Error("VML backing brush requires a retained image resource key");
			n.push({
				kind: "drawingml-image-fill",
				plan: t,
				resourceKey: i,
				...e.fill.vml?.alignShape === !1 ? {
					imageRotationDeg: -(e.rotation ?? 0),
					imageFlipH: e.flipH ?? !1,
					imageFlipV: e.flipV ?? !1
				} : {}
			});
		} else e.fill && n.push({
			kind: "drawingml-shape",
			plan: t,
			...e.fillOpacity == null ? {} : { opacity: Math.max(0, Math.min(1, e.fillOpacity)) }
		});
		return Object.freeze({
			status: "planned",
			before: Z(n, "VML picture backing commands"),
			command: Z({
				kind: "drawingml-image-fill",
				plan: p({
					...l,
					fill: null
				}),
				resourceKey: o
			}, "VML picture and outline command")
		});
	}
	if (e.fill?.fillType === "image") {
		if (e.fill.tile !== void 0) return Object.freeze({
			status: "unsupported",
			command: Object.freeze({ kind: "noop" }),
			diagnostics: Object.freeze([Object.freeze({
				code: "UNSUPPORTED_FEATURE",
				severity: "error",
				message: "Tiled DrawingML shape image fills are not rendered"
			})])
		});
		if (!i) throw Error("DrawingML shape image fill requires a retained image resource key");
		return Object.freeze({
			status: "planned",
			...d.length ? { before: Z(d, "VML shadows") } : {},
			command: Z({
				kind: "drawingml-image-fill",
				plan: u,
				resourceKey: i,
				...e.fill.vml?.alignShape === !1 ? {
					imageRotationDeg: -(e.rotation ?? 0),
					imageFlipH: e.flipH ?? !1,
					imageFlipV: e.flipV ?? !1
				} : {},
				...e.fill.fillRect === void 0 ? {} : { fillRect: {
					l: e.fill.fillRect.l ?? 0,
					t: e.fill.fillRect.t ?? 0,
					r: e.fill.fillRect.r ?? 0,
					b: e.fill.fillRect.b ?? 0
				} }
			}, "DrawingML shape image-fill command")
		});
	}
	if (e.fill && e.fillOpacity != null && e.fillOpacity !== 1) {
		let t = Math.max(0, Math.min(1, e.fillOpacity)), n = {
			kind: "drawingml-shape",
			plan: l.stroke ? p({
				...l,
				stroke: null
			}) : u,
			opacity: t
		};
		return Object.freeze({
			status: "planned",
			...d.length || l.stroke ? { before: Z([...d, ...l.stroke ? [n] : []], "VML fill and shadows") } : {},
			command: Z(l.stroke ? {
				kind: "drawingml-shape",
				plan: p({
					...l,
					fill: null
				})
			} : n, "VML shape command")
		});
	}
	return Object.freeze({
		status: "planned",
		...d.length ? { before: Z(d, "VML shadows") } : {},
		command: Z({
			kind: "drawingml-shape",
			plan: u
		}, "DrawingML shape command")
	});
}
function nx(e, t, n, r, i, a, o, s) {
	let c = tx(e, t, n, r, i, a, o, s);
	if (c.status === "planned" && (c.command.kind === "watermark-text" || c.before?.some((e) => e.kind === "watermark-text")) || c.status !== "planned" || !e.vmlStrokeFill && !e.vmlInsetPen && !e.vmlConcentricGradient) return c;
	let l = [], u = a ?? Infinity;
	for (let t of [...c.before ?? [], c.command]) {
		let n = t.kind === "drawingml-shape" && t.shadowPass;
		if (t.kind !== "drawingml-shape" && t.kind !== "drawingml-image-fill") {
			l.push(t);
			continue;
		}
		u -= t.plan.resolvedGeometry.workUnits;
		let r = !n && e.vmlConcentricGradient ? Jb(t.plan) : void 0;
		if (n || !t.plan.stroke && !r) {
			l.push(t);
			continue;
		}
		let i = e.vmlInsetPen === !0, a = (e) => {
			let t = Hb(e, u);
			return u -= t.workUnits, {
				...e,
				resolvedGeometry: t
			};
		};
		if (r) {
			let e = r.rings.length * t.plan.resolvedGeometry.workUnits;
			if (e > 1048576 || (u -= e, u <= 0)) throw RangeError("VML concentric fill geometry work budget exceeded");
			if (l.push({
				kind: "drawingml-shape",
				plan: a({
					...t.plan,
					stroke: null
				}),
				concentricFill: r
			}), !t.plan.stroke) continue;
		}
		if (!t.plan.stroke) continue;
		let o = a({
			...t.plan,
			fill: null,
			stroke: {
				...t.plan.stroke,
				...e.vmlStrokeFill ? { color: "FFFFFF" } : {},
				width: t.plan.stroke.width * (i ? 2 : 1)
			}
		});
		if (r || l.push({
			...t,
			plan: a({
				...t.plan,
				stroke: null
			})
		}), e.vmlStrokeFill) {
			if (!s) throw Error("VML textured pen requires a retained resource");
			let t = ye({
				...o,
				transform: {
					rotationDeg: 0,
					flipH: !1,
					flipV: !1
				}
			});
			l.push({
				kind: "drawingml-image-fill",
				plan: o,
				resourceKey: s,
				strokeMask: !0,
				insetStroke: i,
				...t ? { maskBounds: {
					xPt: t.x,
					yPt: t.y,
					widthPt: t.w,
					heightPt: t.h
				} } : {},
				...e.vmlStrokeFill.vml?.alignShape === !1 ? {
					imageRotationDeg: -(e.rotation ?? 0),
					imageFlipH: e.flipH ?? !1,
					imageFlipV: e.flipV ?? !1
				} : {}
			});
		} else l.push({
			kind: "drawingml-shape",
			plan: o,
			insetStroke: i,
			...t.kind === "drawingml-shape" && t.opacity !== void 0 ? { opacity: t.opacity } : {}
		});
	}
	return Z({
		...c,
		before: l.slice(0, -1).filter((e) => e.kind !== "noop"),
		command: l[l.length - 1]
	}, "VML pen passes");
}
function rx(e, t, n, r, i, a, o, s, c) {
	let l = nx(e, t, n, r, i, a, o, s);
	if (l.status === "planned" && e.vmlEdgeStrokes?.length) {
		let n = [], r = a ?? Infinity;
		for (let e of [...l.before ?? [], l.command]) (e.kind === "drawingml-shape" || e.kind === "drawingml-image-fill") && (r -= e.plan.resolvedGeometry.workUnits);
		for (let i of e.vmlEdgeStrokes) {
			if (i.edge === "column") continue;
			let a = {
				left: [
					0,
					0,
					0,
					1
				],
				top: [
					0,
					0,
					1,
					0
				],
				right: [
					1,
					0,
					1,
					1
				],
				bottom: [
					0,
					1,
					1,
					1
				]
			}[i.edge], o = {
				...e,
				presetGeometry: null,
				vmlEdgeStrokes: void 0,
				vmlGroupTransform: void 0,
				vmlShadow: void 0,
				vmlPicture: void 0,
				vmlConcentricGradient: !1,
				fill: null,
				stroke: i.color,
				strokeWidth: i.widthPt,
				strokeDash: i.dash,
				strokeCap: i.cap,
				strokeJoin: i.join,
				strokeMiterLimit: i.miterLimit,
				strokeCompound: i.compound,
				headEnd: null,
				tailEnd: null,
				vmlStrokeFill: i.image ?? void 0,
				vmlStrokePattern: i.pattern ?? void 0,
				vmlInsetPen: !1,
				strokeFill: null,
				strokeCustomDash: void 0,
				strokeAlignment: void 0,
				subpaths: [[{
					cmd: "moveTo",
					x: a[0],
					y: a[1]
				}, {
					cmd: "lineTo",
					x: a[2],
					y: a[3]
				}]],
				subpathPaint: []
			};
			if (i.image && !c) throw Error("VML edge image pen requires a retained resource");
			let s = rx(o, t, void 0, void 0, void 0, r, void 0, i.image ? `${c}${i.edge}` : void 0);
			if (s.status !== "planned") throw Error("VML edge pen acquisition failed");
			for (let e of [...s.before ?? [], s.command]) e.kind !== "noop" && (n.push(e), (e.kind === "drawingml-shape" || e.kind === "drawingml-image-fill") && (r -= e.plan.resolvedGeometry.workUnits));
		}
		n.length && (l = Z({
			...l,
			before: [
				...l.before ?? [],
				...l.command.kind === "noop" ? [] : [l.command],
				...n.slice(0, -1)
			],
			command: n.at(-1) ?? l.command
		}, "VML independent edge pens"));
	}
	return e.vmlGroupTransform ? Kb(l, e.vmlGroupTransform, t, a) : l;
}
function ix(e, t, n, r, i, a, o, s, c) {
	let l = t.group?.resolvedChildFrame;
	return rx(l ? {
		...e,
		rotation: l.rotationDeg,
		flipH: l.flipH,
		flipV: l.flipV
	} : e, n, r, e.vmlTextPathInput, i, a, o, s, c);
}
function ax(e, t = !1) {
	return e.clusters.map((n) => {
		let r = e.optionalHyphenGlyph ? e.text : e.text.slice(n.range.start - e.range.start, n.range.end - e.range.start), i = e.paintOps.find((e) => e.range.start <= n.range.start && e.range.end >= n.range.end) ?? e.paintOps[0], a = vs.test(r) || t && /\p{Emoji_Presentation}/u.test(r);
		return {
			...i,
			text: r,
			range: n.range,
			offset: a ? {
				xPt: n.offset.xPt + n.advancePt / 2,
				yPt: n.offset.yPt
			} : n.offset,
			glyphOrientation: a ? "upright" : "sideways"
		};
	});
}
var ox = Object.freeze([
	"#C00000",
	"#0070C0",
	"#00B050",
	"#7030A0",
	"#E97132",
	"#196B24",
	"#9E480E",
	"#525252"
]), sx = Object.freeze({
	underline: !1,
	strike: !1
}), cx = Object.freeze({
	underline: !0,
	strike: !1
}), lx = Object.freeze({
	underline: !1,
	strike: !0
});
function ux(e) {
	return e === "insertion" || e === "moveTo" ? cx : e === "deletion" || e === "moveFrom" ? lx : sx;
}
function dx(e, t, n, r, i = -Infinity, a = !0, o = !1, s) {
	return Se(e, t, {
		firstContentSi: n,
		lastDrawnSi: r,
		minPerGap: i,
		seaClusterGaps: o,
		...s ? {
			seaClusterSpaceGaps: !0,
			gapWidth: (e, t) => s(e, t)
		} : {},
		...a ? {} : { isGapChar: () => !1 }
	});
}
function fx(e) {
	if (!e) return 0;
	let t = 0;
	for (let n of e.perSeg.values()) t += n.internalStretch, n.trailingGap && (t += n.trailingDelta ?? e.perGap);
	return t;
}
var px = [
	1587,
	1588,
	1589,
	1590,
	1690,
	1691,
	1692,
	1693,
	1694,
	1786,
	1787,
	1884,
	1901,
	1904,
	1917,
	1918,
	2223
], mx = [
	1580,
	1581,
	1582,
	1665,
	1666,
	1667,
	1668,
	1669,
	1670,
	1671,
	1727,
	1879,
	1880,
	1902,
	1903,
	1906,
	1916,
	2186,
	2210,
	2241,
	2245,
	2246
], hx = [
	1576,
	1578,
	1579,
	1646,
	1657,
	1658,
	1659,
	1660,
	1661,
	1662,
	1663,
	1664,
	1872,
	1873,
	1874,
	1875,
	1876,
	1877,
	1878,
	2208,
	2209,
	2230,
	2231,
	2232,
	2238,
	2239,
	2240
], gx = [
	1574,
	1585,
	1586,
	1597,
	1598,
	1599,
	1609,
	1610,
	1656,
	1681,
	1682,
	1683,
	1684,
	1685,
	1686,
	1687,
	1688,
	1689,
	1740,
	1742,
	1744,
	1745,
	1775,
	1883,
	1899,
	1900,
	1905,
	1909,
	1910,
	1911,
	2216,
	2217,
	2218,
	2226,
	2233,
	2234,
	69319
], _x = [
	1570,
	1571,
	1573,
	1575,
	1591,
	1592,
	1595,
	1596,
	1603,
	1604,
	1649,
	1650,
	1651,
	1653,
	1695,
	1705,
	1707,
	1708,
	1709,
	1710,
	1711,
	1712,
	1713,
	1714,
	1715,
	1716,
	1717,
	1718,
	1719,
	1720,
	1890,
	1891,
	1892,
	1898,
	1907,
	1908,
	1919,
	2160,
	2161,
	2162,
	2163,
	2164,
	2165,
	2166,
	2167,
	2168,
	2169,
	2170,
	2171,
	2172,
	2173,
	2174,
	2175,
	2176,
	2177,
	2178,
	2187,
	2188,
	2189,
	2211,
	2214,
	2224,
	2228,
	2242,
	2247,
	2248,
	69315,
	69316
], vx = [
	1572,
	1593,
	1594,
	1601,
	1602,
	1608,
	1647,
	1654,
	1655,
	1696,
	1697,
	1698,
	1699,
	1700,
	1701,
	1702,
	1703,
	1704,
	1732,
	1733,
	1734,
	1735,
	1736,
	1737,
	1738,
	1739,
	1743,
	1788,
	1885,
	1886,
	1887,
	1888,
	1889,
	1912,
	1913,
	2212,
	2213,
	2219,
	2227,
	2229,
	2243
], yx = 1604, bx = new Set([
	1575,
	1570,
	1571,
	1573,
	1649
]), xx = 1600, Sx = new Set(px), Cx = new Set(mx), wx = new Set(hx), Tx = new Set(gx), Ex = new Set(_x), Dx = new Set(vx);
function Ox(e) {
	let t = [...e].map((e) => e.codePointAt(0)), n = [], r = t.length > 0 && d(t[0]) !== "T" ? 0 : -1;
	for (let e = 1; e < t.length; e++) {
		let i = t[e];
		if (d(i) !== "T") {
			if (r >= 0) {
				let a = t[r];
				!(a === yx && bx.has(i)) && p(a) && l(i) && n.push(e);
			}
			r = e;
		}
	}
	return n;
}
function kx(e, t, n) {
	let r = t - 1;
	for (; r >= 0 && d(e[r]) === "T";) r--;
	let i = e[r], a = e[t];
	return i === xx ? 13 : Sx.has(i) ? 12 : Cx.has(i) ? 11 : vi(t, n) && Ex.has(a) ? 10 : wx.has(i) && Tx.has(a) ? 9 : vi(t, n) && Dx.has(a) ? 8 : 7;
}
function Ax(e) {
	let t = [...e], n = [];
	for (let e = 0; e < t.length;) {
		for (; e < t.length && /\s/u.test(t[e]);) e++;
		if (e >= t.length) break;
		let r = e + 1;
		for (; r < t.length && !/\s/u.test(t[r]);) r++;
		let i = t.slice(e, r), a = i.map((e) => e.codePointAt(0)), o = a.length - 1;
		for (; o >= 0 && d(a[o]) === "T";) o--;
		let s = -1, c = -1;
		for (let e of Ox(i.join(""))) {
			let t = kx(a, e, o);
			t >= c && (s = e, c = t);
		}
		s >= 0 && n.push({
			beforeCp: e + s,
			priority: c
		}), e = r;
	}
	return n;
}
var jx = "ـ";
function Mx(e, t) {
	let n = [...e], r = "";
	for (let e = 0; e < n.length; e++) {
		let i = t.get(e) ?? 0;
		i > 0 && (r += jx.repeat(i)), r += n[e];
	}
	return r;
}
function Nx(e, t, n, r) {
	if (t <= .5) return null;
	let i = [];
	for (let t = 0; t < e.length; t++) {
		let n = e[t].text;
		if (n !== void 0) for (let { beforeCp: e, priority: r } of Ax(n)) i.push({
			si: t,
			beforeCp: e,
			priority: r,
			textOrder: i.length
		});
	}
	if (i.length === 0) return null;
	i.sort((e, t) => t.priority - e.priority || e.textOrder - t.textOrder);
	let a = n === "low" ? 1 : n === "medium" ? 2 : Infinity, o = a, s = i.length * 64, c = /* @__PURE__ */ new Map(), l = /* @__PURE__ */ new Map(), u = /* @__PURE__ */ new Map();
	for (let { si: t } of i) {
		if (u.has(t)) continue;
		let n = r(t, e[t].text);
		l.set(t, n), u.set(t, n);
	}
	let d = t, f = 0;
	for (let t = 0; t < o && d > .5 && f < s; t++) {
		let t = !1;
		for (let { si: n, beforeCp: o } of i) {
			if (d <= .5 || f >= s) break;
			let i = c.get(n);
			i || (i = /* @__PURE__ */ new Map(), c.set(n, i));
			let l = i.get(o) ?? 0;
			if (l >= a) continue;
			i.set(o, l + 1);
			let p = r(n, Mx(e[n].text, i)), m = p - u.get(n);
			m > 0 && m <= d + 1e-6 ? (u.set(n, p), d -= m, f++, t = !0) : l === 0 ? i.delete(o) : i.set(o, l);
		}
		if (!t) break;
	}
	let p = /* @__PURE__ */ new Map();
	for (let [t, n] of c) {
		let r = [...n.entries()].filter(([, e]) => e > 0).sort(([e], [t]) => e - t).map(([e, t]) => ({
			beforeCp: e,
			count: t
		}));
		r.length !== 0 && p.set(t, {
			text: Mx(e[t].text, n),
			insertions: r,
			advanceDeltaPx: u.get(t) - l.get(t)
		});
	}
	if (p.size === 0) return null;
	let m = [...p.values()].reduce((e, t) => e + t.advanceDeltaPx, 0);
	return {
		perSeg: p,
		appliedPx: m,
		residualPx: t - m
	};
}
function Px(e, t) {
	let n = e.fontFamily ?? null;
	return {
		fontSizePt: t,
		fonts: {
			ascii: n,
			highAnsi: n,
			eastAsia: e.fontFamilyEastAsia ?? n,
			complexScript: n
		},
		weight: 400,
		style: "normal",
		complexScript: !1
	};
}
function Fx(e, t = {
	story: "textbox",
	storyInstance: "shape",
	path: []
}, n = Px) {
	return Z((e.textBlocks ?? []).map((e, r) => {
		let i = {
			story: "textbox",
			storyInstance: t.storyInstance,
			path: [...t.path, r]
		}, a = e.runs?.length ? e.runs : [{
			text: e.text,
			fontSizePt: e.fontSizePt,
			color: e.color,
			fontFamily: e.fontFamily,
			bold: e.bold,
			italic: e.italic
		}], o = e.paragraphMarkColor === void 0 ? e.color ?? a[0]?.color : e.paragraphMarkColor ?? void 0, s = e.numbering ? {
			...e.numbering,
			...e.numbering.color == null && !e.numbering.colorAuto && o ? { color: o } : {}
		} : null;
		return {
			source: i,
			spacing: {
				beforePt: e.spaceBefore ?? 0,
				afterPt: e.spaceAfter ?? 0
			},
			runs: a.map((t) => ({
				text: t.text,
				fontSizePt: t.fontSizePt,
				...t.color ?? e.color ? { color: `#${t.color ?? e.color}` } : {},
				...t.fontFamily || e.fontFamily ? { fontFamily: t.fontFamily ?? e.fontFamily ?? void 0 } : {},
				...t.fontFamilyEastAsia ? { fontFamilyEastAsia: t.fontFamilyEastAsia } : {},
				bold: t.bold ?? e.bold ?? !1,
				italic: t.italic ?? e.italic ?? !1,
				...t.rtl === void 0 ? {} : { rtl: t.rtl },
				cs: t.cs,
				fontFamilyCs: t.fontFamilyCs,
				fontSizeCsPt: t.fontSizeCsPt,
				boldCs: t.boldCs,
				italicCs: t.italicCs,
				...t.ruby ? { ruby: t.ruby } : {}
			})),
			alignment: e.alignment ?? "left",
			indentLeftPt: e.indentLeft ?? 0,
			indentRightPt: e.indentRight ?? 0,
			indentFirstPt: e.indentFirst ?? 0,
			lineSpacing: e.lineSpacingVal == null ? null : {
				value: e.lineSpacingVal,
				rule: e.lineSpacingRule === "exact" || e.lineSpacingRule === "atLeast" ? e.lineSpacingRule : "auto",
				explicit: !0
			},
			tabStops: (e.tabStops ?? []).map((e) => ({ ...e })),
			...e.bidi === void 0 ? {} : { bidi: e.bidi },
			contextualSpacing: e.contextualSpacing ?? !1,
			...e.styleId === void 0 ? {} : { styleId: e.styleId },
			...s ? {
				numbering: s,
				numberingMarkerShapeInput: n(s, e.fontSizePt)
			} : {},
			...e.imagePath ? { image: {
				imagePath: e.imagePath,
				mimeType: e.mimeType ?? "application/octet-stream",
				...e.svgImagePath ? { svgImagePath: e.svgImagePath } : {},
				widthPt: e.imageWidthPt ?? 0,
				heightPt: e.imageHeightPt ?? 0
			} } : {}
		};
	}), "DOCX text box acquisition input");
}
function Ix(e) {
	if (!Number.isFinite(e.advancePt) || e.advancePt <= 0) throw RangeError("Tab leader glyph advance must be finite and positive");
	let t = Math.floor(e.interval.widthPt / e.advancePt), n = e.interval.widthPt - t * e.advancePt;
	return Array.from({ length: t }, (t, r) => ({
		text: e.glyph,
		origin: {
			xPt: e.interval.xPt + n / 2 + r * e.advancePt,
			yPt: e.baselinePt
		},
		fontRoute: e.fontRoute,
		fontSizePt: e.fontSizePt,
		fontWeight: e.fontWeight,
		fontStyle: e.fontStyle,
		color: e.color
	}));
}
function Lx(e) {
	let t;
	if (e.raisePt !== void 0) t = e.baseOrigin.yPt - e.raisePt;
	else if (e.baseInkTopPt !== void 0 && e.guideInkBottomFromBaselinePt !== void 0) t = e.baseInkTopPt - e.guideInkBottomFromBaselinePt;
	else throw Error("Ruby geometry requires authored w:hpsRaise or retained base/guide ink bounds");
	let n = e.baseOrigin.xPt + (e.baseAdvancePt - e.guideAdvancePt) / 2;
	return e.spans.map((e) => ({
		text: e.text,
		origin: {
			xPt: n + e.offsetPt,
			yPt: t
		},
		fontRoute: e.fontRoute,
		fontSizePt: e.fontSizePt,
		fontWeight: e.fontWeight,
		fontStyle: e.fontStyle,
		color: e.color,
		...e.kerning ? { kerning: e.kerning } : {}
	}));
}
function Rx(e) {
	return -(e.inkBounds?.ascentPt ?? e.ascentPt);
}
function zx(e) {
	return e.inkBounds?.descentPt ?? e.descentPt;
}
function Bx(e) {
	let t = e.inkBounds ? e.inkBounds.ascentPt + e.inkBounds.descentPt : Math.min(e.ascentPt, e.descentPt);
	if (!Number.isFinite(t) || t <= 0) throw Error("Retained decoration probe requires positive selected-face ink");
	return t;
}
function Vx(e) {
	return e === "double" || e === "dbl" ? "double" : e?.includes("dot") ? "dotted" : e?.includes("dash") ? "dashed" : e?.includes("wave") ? "wavy" : "solid";
}
function Hx(e, t, n) {
	let r = Math.max(0, t.xPt - e.xPt), i = n * 2, a = Math.max(1, Math.ceil(r / i));
	return Array.from({ length: a + 1 }, (t, i) => ({
		xPt: e.xPt + r * i / a,
		yPt: e.yPt + (i % 2 == 0 ? -n / 2 : n / 2)
	}));
}
function Ux(e) {
	let t = [], n = e.origin.xPt + e.advancePt, r = e.fontRule;
	if (e.underline) {
		let i, a;
		if (r) {
			let t = r.geometry.underlineTopEm * r.sizePt, n = r.geometry.underlineThicknessEm * r.sizePt;
			if (e.underline.authoredStyle === "thick") {
				let r = t / 2, o = t + n / 2;
				i = o - r, a = e.origin.yPt + (r + o) / 2;
			} else i = n, a = e.origin.yPt + t + n / 2;
		} else {
			i = Bx(e.underline.probe);
			let t = e.origin.yPt + (Rx(e.underline.probe) + zx(e.underline.probe)) / 2, n = e.origin.yPt + zx(e.base) + i / 2;
			a = Math.max(t, n);
		}
		let o = Vx(e.underline.authoredStyle), s = {
			kind: "underline",
			...e.underline.authoredStyle === void 0 ? {} : { authoredStyle: e.underline.authoredStyle },
			color: e.underline.color,
			widthPt: i
		};
		if (o === "double") {
			let r = a + i * 2;
			t.push({
				...s,
				style: "solid",
				from: {
					xPt: e.origin.xPt,
					yPt: a
				},
				to: {
					xPt: n,
					yPt: a
				}
			}, {
				...s,
				style: "solid",
				from: {
					xPt: e.origin.xPt,
					yPt: r
				},
				to: {
					xPt: n,
					yPt: r
				}
			});
		} else {
			let r = {
				xPt: e.origin.xPt,
				yPt: a
			}, c = {
				xPt: n,
				yPt: a
			};
			t.push({
				...s,
				style: o,
				from: r,
				to: c,
				...o === "wavy" ? { path: Hx(r, c, i) } : {},
				...o === "dotted" ? { dashPatternPt: [i, i * 2] } : {},
				...o === "dashed" ? { dashPatternPt: [i * 4, i * 3] } : {}
			});
		}
	}
	if (e.strike) {
		let i = e.strike.color ?? e.color;
		if (r) {
			let a = r.geometry.strikeThicknessEm * r.sizePt, o = e.origin.yPt + r.geometry.strikeTopEm * r.sizePt + a / 2, s = e.strike.double ? [o - a, o + a] : [o];
			for (let r of s) t.push({
				kind: "strikethrough",
				color: i,
				widthPt: a,
				style: "solid",
				from: {
					xPt: e.origin.xPt,
					yPt: r
				},
				to: {
					xPt: n,
					yPt: r
				}
			});
			return t;
		}
		let a = Bx(e.strike.probe);
		if (e.strike.double && e.strike.doubleProbe) {
			let r = e.origin.yPt + Rx(e.strike.doubleProbe) + a / 2, o = e.origin.yPt + zx(e.strike.doubleProbe) - a / 2;
			for (let s of [r, o]) t.push({
				kind: "strikethrough",
				color: i,
				widthPt: a,
				style: "solid",
				from: {
					xPt: e.origin.xPt,
					yPt: s
				},
				to: {
					xPt: n,
					yPt: s
				}
			});
		} else {
			let r = e.origin.yPt + (Rx(e.strike.probe) + zx(e.strike.probe)) / 2;
			t.push({
				kind: "strikethrough",
				color: i,
				widthPt: a,
				style: "solid",
				from: {
					xPt: e.origin.xPt,
					yPt: r
				},
				to: {
					xPt: n,
					yPt: r
				}
			});
		}
	}
	return t;
}
function Wx(e) {
	let t = e.mark.inkBounds.xMaxPt - e.mark.inkBounds.xMinPt, n = e.mark.inkBounds.ascentPt + e.mark.inkBounds.descentPt;
	if (!(t > 0) || !(n > 0)) throw Error("Retained emphasis glyph requires positive selected-face ink bounds");
	let r = [];
	for (let t of e.clusterInk) {
		if (/^\s+$/u.test(t.text)) continue;
		let n = e.clusters.find((e) => e.range.start === t.range.start && e.range.end === t.range.end);
		if (!n) throw Error("Retained emphasis cluster ink does not match shaped cluster geometry");
		let i = (e.origin.xPt + n.offset.xPt + t.ink.xMinPt * e.scaleX + (e.origin.xPt + n.offset.xPt + t.ink.xMaxPt * e.scaleX)) / 2 - (e.mark.inkBounds.xMinPt + e.mark.inkBounds.xMaxPt) / 2, a = e.authored === "underDot" ? e.origin.yPt + t.ink.descentPt + e.mark.inkBounds.ascentPt : e.origin.yPt - t.ink.ascentPt - e.mark.inkBounds.descentPt;
		r.push({
			text: e.glyph,
			origin: {
				xPt: i,
				yPt: a
			},
			fontRoute: e.mark.fontRoute,
			fontSizePt: e.mark.fontSizePt,
			fontWeight: e.mark.fontWeight,
			fontStyle: e.mark.fontStyle,
			color: e.mark.color,
			inkBounds: e.mark.inkBounds
		});
	}
	return r;
}
function Gx(e, t) {
	return e.val === t.val && e.color === t.color && e.widthPt === t.widthPt && e.spacePt === t.spacePt && e.themeColor === t.themeColor && e.themeTint === t.themeTint && e.themeShade === t.themeShade && e.shadow === t.shadow && e.frame === t.frame;
}
function Kx(e) {
	let t = [], n = 0;
	for (; n < e.length;) {
		let r = e[n], i = n + 1, a = r.bounds.xPt + r.bounds.widthPt + r.trailingSlackPt;
		for (; i < e.length;) {
			let t = e[i];
			if (!Gx(r.border, t.border) || Math.abs(t.bounds.xPt - a) > 1e-6 || t.bounds.yPt !== r.bounds.yPt || t.bounds.heightPt !== r.bounds.heightPt) break;
			a = t.bounds.xPt + t.bounds.widthPt + t.trailingSlackPt, i += 1;
		}
		let o = r.bounds.xPt - r.border.spacePt, s = r.bounds.yPt - r.border.spacePt, c = a + r.border.spacePt, l = r.bounds.yPt + r.bounds.heightPt + r.border.spacePt, u = {
			color: r.border.color,
			widthPt: r.border.widthPt,
			...Cb(r.border.val, r.border.widthPt)
		};
		t.push({
			...u,
			edge: "top",
			from: {
				xPt: o,
				yPt: s
			},
			to: {
				xPt: c,
				yPt: s
			}
		}, {
			...u,
			edge: "right",
			from: {
				xPt: c,
				yPt: s
			},
			to: {
				xPt: c,
				yPt: l
			}
		}, {
			...u,
			edge: "bottom",
			from: {
				xPt: o,
				yPt: l
			},
			to: {
				xPt: c,
				yPt: l
			}
		}, {
			...u,
			edge: "left",
			from: {
				xPt: o,
				yPt: s
			},
			to: {
				xPt: o,
				yPt: l
			}
		}), n = i;
	}
	return t;
}
var qx = /* @__PURE__ */ Object.freeze({ id: "word-zero-relative-size" });
function Jx(e, t) {
	return !e || t !== "none";
}
function Yx(e) {
	return e.shading || e.borders.length > 0 || e.resources.length > 0 || e.drawings.length > 0 || e.textBoxes.length > 0 || e.lineNumbers?.some((e) => e.paintOps.length > 0) ? !0 : e.lines.some((e) => e.placements.some((e) => e.kind === "text" || e.kind === "resource" || e.kind === "drawing" ? !0 : e.kind === "tab" && (e.leaderGlyphs?.length ?? 0) > 0));
}
function Xx(e) {
	let t = e.flowBounds.yPt, n;
	for (let r of e.blocks) {
		if (r.kind === "table") {
			n = Math.max(n ?? t, r.flowBounds.yPt + r.advancePt);
			continue;
		}
		r.kind !== "paragraph" || !Yx(r) || (n = Math.max(n ?? t, r.flowBounds.yPt + Math.max(0, r.advancePt - r.spacing.afterPt)));
	}
	return n === void 0 ? 0 : Math.max(0, n - t);
}
function Zx(e) {
	return e === 0;
}
function Qx(e, t) {
	return e == null ? !t : e !== "paragraph" && e !== "line" && e !== "character";
}
function $x(e, t, n) {
	return e === "page" && t !== null && n !== void 0 && t < n;
}
function eS(e, t, n) {
	return e - (n - t);
}
var tS = 21600;
function $(e, t, n) {
	return {
		code: e,
		path: t,
		message: n
	};
}
function nS(e) {
	return typeof e == "number" && Number.isFinite(e);
}
function rS(e) {
	return nS(e.xPt) && nS(e.yPt) && nS(e.widthPt) && nS(e.heightPt) && e.widthPt >= 0 && e.heightPt >= 0;
}
function iS(e) {
	return e.kind === "align" ? e.value : e.kind === "offset" ? e.valuePt : e.kind === "percent" ? e.fraction : null;
}
function aS(e, t, n, r = !1) {
	let i = t[e];
	return {
		axis: e,
		status: "unsupported",
		relativeFrom: r ? "page" : i.relativeFrom,
		choiceKind: r ? "simple-position" : i.choice.kind,
		choiceValue: r ? e === "horizontal" ? t.simplePosition.xPt : t.simplePosition.yPt : iS(i.choice),
		issueCode: n.code
	};
}
function oS(e, t, n, r) {
	let i = n[e];
	return i === null ? { problem: $("missing-reference-frame", r, `${e} frame is required`) } : rS(i) ? { base: {
		startPt: t === "horizontal" ? i.xPt : i.yPt,
		endPt: t === "horizontal" ? i.xPt + i.widthPt : i.yPt + i.heightPt,
		referenceFrame: e
	} } : { problem: $("invalid-reference-frame", r, `${e} frame must be finite and non-negative`) };
}
function sS(e, t, n, r) {
	let i = oS("page", t, n, r);
	if (!i.base) return i;
	let a = oS("margin", t, n, r);
	if (!a.base) return a;
	let o = n.page, s = n.margin, c = e === "leftMargin" || e === "rightMargin";
	if (c !== (t === "horizontal")) return { problem: $("unsupported-relative-from", r, `${e} is not valid for the ${t} axis`) };
	let l = c ? o.xPt : o.yPt, u = c ? o.xPt + o.widthPt : o.yPt + o.heightPt, d = c ? s.xPt : s.yPt, f = c ? s.xPt + s.widthPt : s.yPt + s.heightPt;
	if (d < l || f > u) return { problem: $("invalid-reference-frame", r, "margin frame must be contained by the page frame") };
	let p = e === "leftMargin" || e === "topMargin";
	return { base: {
		startPt: p ? l : f,
		endPt: p ? d : u,
		referenceFrame: e
	} };
}
function cS(e, t, n, r) {
	if (t === "page" || t === "margin" || e === "horizontal" && (t === "column" || t === "character") || e === "vertical" && (t === "paragraph" || t === "line")) return oS(t, e, n, r);
	if (e === "horizontal" && (t === "leftMargin" || t === "rightMargin") || e === "vertical" && (t === "topMargin" || t === "bottomMargin")) return sS(t, e, n, r);
	if (t === "insideMargin" || t === "outsideMargin") {
		if (n.pageParity === null) return { problem: $("missing-page-parity", r, `${t} requires explicit page parity`) };
		let i = t === "insideMargin" == (n.pageParity === "odd");
		return {
			...sS(e === "horizontal" ? i ? "leftMargin" : "rightMargin" : i ? "topMargin" : "bottomMargin", e, n, r),
			parityRequired: !0
		};
	}
	return { problem: $("unsupported-relative-from", r, `${t} is not a valid ${e} reference`) };
}
function lS(e, t, n) {
	let r = t.relativeSize[e], i = e === "horizontal" ? "width" : "height", a = (n = null) => {
		let r = e === "horizontal" ? t.extent.widthStatus : t.extent.heightStatus, a = e === "horizontal" ? t.extent.widthPt : t.extent.heightPt;
		return r === "missing" ? { problem: $("missing-size", `extent.${i}`, `${i} is required`) } : r !== "valid" || !nS(a) || a < 0 ? { problem: $("invalid-size", `extent.${i}`, `${i} extent must be finite and non-negative`) } : { resolved: {
			valuePt: a,
			diagnostic: {
				source: "extent",
				valuePt: a,
				relativeFrom: n?.relativeFrom ?? null,
				referenceFrame: null,
				fraction: n?.fraction ?? null,
				...n === null ? {} : { compatibilityFallback: qx.id }
			}
		} };
	};
	if (r === null) return a();
	let o = `relativeSize.${e}`;
	if (r.fractionStatus === "missing" || r.fraction === null) return { problem: $("missing-relative-size-fraction", `${o}.fraction`, "relative size fraction is required") };
	if (r.fractionStatus !== "valid" || !nS(r.fraction)) return { problem: $("invalid-relative-size-fraction", `${o}.fraction`, "relative size fraction must be finite") };
	if (r.fraction < 0) return { problem: $("invalid-relative-size-fraction", `${o}.fraction`, "relative size fraction must be non-negative") };
	if (Zx(r.fraction)) return a({
		relativeFrom: r.relativeFrom,
		fraction: r.fraction
	});
	if (r.relativeFromStatus === "missing" || r.relativeFrom === null) return { problem: $("missing-relative-size-reference", `${o}.relativeFrom`, "relative size reference is required") };
	if (r.relativeFromStatus !== "valid") return { problem: $("invalid-relative-size-reference", `${o}.relativeFrom`, "relative size reference is invalid") };
	let s = cS(e, r.relativeFrom, n, `${o}.relativeFrom`);
	if (!s.base) return { problem: $(s.problem?.code === "missing-reference-frame" ? "missing-relative-size-reference" : "invalid-relative-size-reference", `${o}.relativeFrom`, s.problem?.message ?? "relative size reference cannot be resolved") };
	let c = (s.base.endPt - s.base.startPt) * r.fraction;
	return !nS(c) || c < 0 ? { problem: $("invalid-relative-size-fraction", `${o}.fraction`, "relative size result must be finite and non-negative") } : { resolved: {
		valuePt: c,
		diagnostic: {
			source: "relative",
			valuePt: c,
			relativeFrom: r.relativeFrom,
			referenceFrame: s.base.referenceFrame,
			fraction: r.fraction
		}
	} };
}
function uS(e, t, n, r) {
	let i = n[e], a = e;
	if (i.relativeFromStatus === "missing" || i.relativeFrom === null) {
		let t = $("missing-relative-from", `${a}.relativeFrom`, `${e} relativeFrom is required`);
		return {
			diagnostic: aS(e, n, t),
			problem: t
		};
	}
	if (i.relativeFromStatus !== "valid") {
		let t = $("invalid-relative-from", `${a}.relativeFrom`, `${e} relativeFrom is invalid`);
		return {
			diagnostic: aS(e, n, t),
			problem: t
		};
	}
	let o = cS(e, i.relativeFrom, r, `${a}.relativeFrom`);
	if (!o.base) {
		let t = o.problem;
		return {
			diagnostic: aS(e, n, t),
			problem: t
		};
	}
	let s = i.choice;
	if (s.kind === "missing") {
		let t = $("missing-axis-choice", `${a}.choice`, `${e} choice is required`);
		return {
			diagnostic: aS(e, n, t),
			problem: t
		};
	}
	if (s.kind === "invalid") {
		let t = $("invalid-axis-choice", `${a}.choice`, `${e} choice is invalid`);
		return {
			diagnostic: aS(e, n, t),
			problem: t
		};
	}
	let c = o.base.endPt - o.base.startPt, l, u;
	if (s.kind === "offset") {
		if (!nS(s.valuePt)) {
			let t = $("invalid-axis-value", `${a}.choice`, "offset must be finite");
			return {
				diagnostic: aS(e, n, t),
				problem: t
			};
		}
		l = o.base.startPt + s.valuePt, u = s.valuePt;
	} else if (s.kind === "percent") {
		if (!nS(s.fraction)) {
			let t = $("invalid-axis-value", `${a}.choice`, "percentage must be finite");
			return {
				diagnostic: aS(e, n, t),
				problem: t
			};
		}
		l = o.base.startPt + c * s.fraction, u = s.fraction;
	} else if (s.kind === "align") {
		if (!(e === "horizontal" ? [
			"left",
			"center",
			"right",
			"inside",
			"outside"
		].includes(s.value) : [
			"top",
			"center",
			"bottom",
			"inside",
			"outside"
		].includes(s.value))) {
			let t = $("invalid-axis-value", `${a}.choice`, `${s.value} is invalid`);
			return {
				diagnostic: aS(e, n, t),
				problem: t
			};
		}
		if ((s.value === "inside" || s.value === "outside") && r.pageParity === null) {
			let t = $("missing-page-parity", "frames.pageParity", `${s.value} alignment requires explicit page parity`);
			return {
				diagnostic: aS(e, n, t),
				problem: t
			};
		}
		let i = dS(e, s.value, r.pageParity);
		l = i === "leading" ? o.base.startPt : i === "trailing" ? o.base.endPt - t : o.base.startPt + (c - t) / 2, u = s.value;
	} else {
		let t = $("invalid-axis-choice", `${a}.choice`, `${e} choice is invalid`);
		return {
			diagnostic: aS(e, n, t),
			problem: t
		};
	}
	if (!nS(l)) {
		let t = $("invalid-axis-value", `${a}.choice`, "resolved origin is not finite");
		return {
			diagnostic: aS(e, n, t),
			problem: t
		};
	}
	return {
		valuePt: l,
		diagnostic: {
			axis: e,
			status: "resolved",
			relativeFrom: i.relativeFrom,
			referenceFrame: o.base.referenceFrame,
			choiceKind: s.kind,
			choiceValue: u,
			baseStartPt: o.base.startPt,
			baseEndPt: o.base.endPt,
			resolvedOriginPt: l,
			pageParity: s.kind === "align" && (s.value === "inside" || s.value === "outside") ? r.pageParity : null
		}
	};
}
function dS(e, t, n) {
	let r = e === "horizontal" ? "left" : "top", i = e === "horizontal" ? "right" : "bottom", a = n === "odd";
	return t === r || t === "inside" && a || t === "outside" && !a ? "leading" : t === i || t === "inside" && !a || t === "outside" && a ? "trailing" : "center";
}
function fS(e, t, n) {
	let r = e === "horizontal" ? n.xPt : n.yPt, i = e === "horizontal" ? n.xPt + n.widthPt : n.yPt + n.heightPt, a = r + t;
	return {
		valuePt: a,
		diagnostic: {
			axis: e,
			status: "resolved",
			relativeFrom: "page",
			referenceFrame: "page",
			choiceKind: "simple-position",
			choiceValue: t,
			baseStartPt: r,
			baseEndPt: i,
			resolvedOriginPt: a,
			pageParity: null
		}
	};
}
var pS = [
	"top",
	"right",
	"bottom",
	"left"
];
function mS(e, t) {
	return e[`${t}Status`];
}
function hS(e, t) {
	return e[`${t}Pt`];
}
function gS(e, t, n) {
	let r = pS.some((t) => mS(e, t) !== "missing");
	if (!n && !r) return { values: {
		topPt: 0,
		rightPt: 0,
		bottomPt: 0,
		leftPt: 0
	} };
	let i = {
		topPt: 0,
		rightPt: 0,
		bottomPt: 0,
		leftPt: 0
	};
	for (let n of pS) {
		let r = mS(e, n), a = hS(e, n);
		if (r !== "valid" || !nS(a)) return { problem: $("invalid-effect-extent", `${t}.${n}`, "present effectExtent requires four finite edge values") };
		i[`${n}Pt`] = a;
	}
	return { values: i };
}
function _S(e, t) {
	let n = {
		topPt: 0,
		rightPt: 0,
		bottomPt: 0,
		leftPt: 0
	}, r = {};
	for (let i of pS) {
		let a = mS(t, i), o = mS(e, i), s = a === "valid" || a === "invalid" ? {
			status: a,
			value: hS(t, i),
			source: "wrap"
		} : o === "valid" || o === "invalid" ? {
			status: o,
			value: hS(e, i),
			source: "anchor"
		} : {
			status: "missing",
			value: null,
			source: "implicit-zero"
		};
		if (s.status === "invalid" || s.status === "valid" && (!nS(s.value) || s.value < 0)) return { problem: $("invalid-distance", `${s.source === "wrap" ? "wrap.distances" : "anchorDistances"}.${i}`, "wrap distance must be finite and non-negative") };
		n[`${i}Pt`] = s.status === "missing" ? 0 : s.value, r[i] = s.source;
	}
	return { resolved: {
		values: n,
		sources: r
	} };
}
function vS(e, t) {
	let n = {
		xPt: e.xPt - t.leftPt,
		yPt: e.yPt - t.topPt,
		widthPt: e.widthPt + t.leftPt + t.rightPt,
		heightPt: e.heightPt + t.topPt + t.bottomPt
	};
	return rS(n) ? n : null;
}
function yS(e, t) {
	let n = e.wrap.polygon;
	if (n === null || n.invalidPointCount !== 0 || n.coordinateSpace.width !== tS || n.coordinateSpace.height !== tS || n.points.length < 3) return { problem: $("invalid-wrap-polygon", "wrap.polygon", "tight and through wrapping require a valid fixed 21600 by 21600 polygon") };
	let r = [];
	for (let [e, i] of n.points.entries()) {
		if (!nS(i.x) || !nS(i.y)) return { problem: $("invalid-wrap-polygon", `wrap.polygon.points.${e}`, "polygon coordinates must be finite") };
		r.push({
			xPt: t.xPt + i.x / tS * t.widthPt,
			yPt: t.yPt + i.y / tS * t.heightPt
		});
	}
	let i = Infinity, a = -Infinity, o = Infinity, s = -Infinity;
	for (let e of r) i = Math.min(i, e.xPt), a = Math.max(a, e.xPt), o = Math.min(o, e.yPt), s = Math.max(s, e.yPt);
	return {
		polygon: {
			edited: n.edited,
			points: r
		},
		bounds: {
			xPt: i,
			yPt: o,
			widthPt: a - i,
			heightPt: s - o
		}
	};
}
function bS(e) {
	return {
		coordinateSpace: "anchor-frame",
		groupApplication: "parser-resolved-child-frame",
		group: e === null ? null : {
			childSourceId: e.childSourceId,
			sourceIndex: e.sourceIndex,
			sourceCount: e.sourceCount,
			transformChain: e.transformChain.map((e) => ({ ...e })),
			childTransform: e.childTransform === null ? null : { ...e.childTransform },
			resolvedChildFrame: { ...e.resolvedChildFrame }
		}
	};
}
function xS(e) {
	return Z(e, "anchor frame result");
}
function SS(e) {
	let { acquisition: t, frames: n } = e;
	for (let e of [
		"relativeHeight",
		"behindDoc",
		"locked",
		"layoutInCell",
		"allowOverlap"
	]) {
		let n = t.behavior[`${e}Status`], r = t.behavior[e];
		if (n === "valid" && r !== null) continue;
		let i = $(n === "missing" ? "missing-required-behavior" : "invalid-required-behavior", `behavior.${e}`, `CT_Anchor requires a ${e} value`);
		return xS({
			status: "unsupported",
			occurrenceId: t.occurrenceId,
			axes: {
				horizontal: aS("horizontal", t, i),
				vertical: aS("vertical", t, i)
			},
			issues: [i]
		});
	}
	let r = [], i = lS("horizontal", t, n), a = lS("vertical", t, n);
	i.problem && r.push(i.problem), a.problem && r.push(a.problem);
	let o, s, c = i.problem ?? a.problem;
	if (c || !i.resolved || !a.resolved) {
		let e = c;
		o = { diagnostic: aS("horizontal", t, e) }, s = { diagnostic: aS("vertical", t, e) };
	} else if (t.simplePosition.status === "invalid") {
		let e = $("invalid-simple-position", "simplePosition.enabled", "simplePos enablement is invalid");
		r.push(e), o = {
			diagnostic: aS("horizontal", t, e, !0),
			problem: e
		}, s = {
			diagnostic: aS("vertical", t, e, !0),
			problem: e
		};
	} else if (t.simplePosition.status === "valid" && t.simplePosition.enabled === !0) {
		let e = oS("page", "horizontal", n, "frames.page"), i = t.simplePosition.xPt, a = t.simplePosition.yPt;
		if (!e.base || n.page === null || !rS(n.page)) {
			let n = e.problem ?? $("invalid-reference-frame", "frames.page", "simple positioning requires a valid page frame");
			r.push(n), o = {
				diagnostic: aS("horizontal", t, n, !0),
				problem: n
			}, s = {
				diagnostic: aS("vertical", t, n, !0),
				problem: n
			};
		} else if (t.simplePosition.xStatus !== "valid" || !nS(i)) {
			let e = t.simplePosition.xStatus === "invalid", n = $(e ? "invalid-simple-position" : "missing-simple-coordinate", "simplePosition.x", e ? "simple position x is lexically invalid" : "simple position x is required");
			r.push(n), o = {
				diagnostic: aS("horizontal", t, n, !0),
				problem: n
			}, s = {
				diagnostic: aS("vertical", t, n, !0),
				problem: n
			};
		} else if (t.simplePosition.yStatus !== "valid" || !nS(a)) {
			let e = t.simplePosition.yStatus === "invalid", n = $(e ? "invalid-simple-position" : "missing-simple-coordinate", "simplePosition.y", e ? "simple position y is lexically invalid" : "simple position y is required");
			r.push(n), o = {
				diagnostic: aS("horizontal", t, n, !0),
				problem: n
			}, s = {
				diagnostic: aS("vertical", t, n, !0),
				problem: n
			};
		} else o = fS("horizontal", i, n.page), s = fS("vertical", a, n.page);
	} else {
		let e = uS("horizontal", i.resolved.valuePt, t, n), c = uS("vertical", a.resolved.valuePt, t, n);
		o = {
			...e,
			diagnostic: e.diagnostic
		}, s = {
			...c,
			diagnostic: c.diagnostic
		}, e.problem && r.push(e.problem), c.problem && r.push(c.problem);
	}
	if (r.length > 0 || !i.resolved || !a.resolved || o.valuePt === void 0 || s.valuePt === void 0) return xS({
		status: "unsupported",
		occurrenceId: t.occurrenceId,
		axes: {
			horizontal: o.diagnostic,
			vertical: s.diagnostic
		},
		issues: r
	});
	let l = {
		xPt: o.valuePt,
		yPt: s.valuePt,
		widthPt: i.resolved.valuePt,
		heightPt: a.resolved.valuePt
	};
	return Z({
		status: "resolved",
		occurrenceId: t.occurrenceId,
		axes: {
			horizontal: o.diagnostic,
			vertical: s.diagnostic
		},
		issues: [],
		geometry: {
			objectFrame: l,
			size: {
				horizontal: i.resolved.diagnostic,
				vertical: a.resolved.diagnostic
			}
		}
	}, "anchor placement result");
}
function CS(e) {
	let { acquisition: t } = e, n = SS(e);
	if (n.status !== "resolved") return n;
	let r = n.geometry.objectFrame, i = { diagnostic: n.axes.horizontal }, a = { diagnostic: n.axes.vertical }, o = gS(t.parentEffectExtent, "parentEffectExtent", !1);
	if (o.problem || !o.values) {
		let e = o.problem;
		return xS({
			status: "unsupported",
			occurrenceId: t.occurrenceId,
			axes: {
				horizontal: i.diagnostic,
				vertical: a.diagnostic
			},
			issues: [e]
		});
	}
	let s = vS(r, o.values);
	if (s === null) {
		let e = $("invalid-effect-extent", "parentEffectExtent", "parent effect extents produce invalid ink bounds");
		return xS({
			status: "unsupported",
			occurrenceId: t.occurrenceId,
			axes: {
				horizontal: i.diagnostic,
				vertical: a.diagnostic
			},
			issues: [e]
		});
	}
	if (t.wrap.kind === "missing" || t.wrap.kind === "invalid") {
		let e = $(t.wrap.kind === "missing" ? "missing-wrap-kind" : "invalid-wrap-kind", "wrap.kind", "exactly one valid wrap kind is required");
		return xS({
			status: "unsupported",
			occurrenceId: t.occurrenceId,
			axes: {
				horizontal: i.diagnostic,
				vertical: a.diagnostic
			},
			issues: [e]
		});
	}
	let c = _S(t.anchorDistances, t.wrap.distances);
	if (c.problem || !c.resolved) return xS({
		status: "unsupported",
		occurrenceId: t.occurrenceId,
		axes: {
			horizontal: i.diagnostic,
			vertical: a.diagnostic
		},
		issues: [c.problem]
	});
	let l = t.wrap.kind === "square" || t.wrap.kind === "tight" || t.wrap.kind === "through", u = l && [
		"bothSides",
		"left",
		"right",
		"largest"
	].includes(t.wrap.side ?? "") ? t.wrap.side : null;
	if (l && u === null) {
		let e = $("invalid-wrap-side", "wrap.side", "square, tight, and through wrapping require an authored wrap side");
		return xS({
			status: "unsupported",
			occurrenceId: t.occurrenceId,
			axes: {
				horizontal: i.diagnostic,
				vertical: a.diagnostic
			},
			issues: [e]
		});
	}
	let d = o.values, f = pS.some((e) => mS(t.parentEffectExtent, e) !== "missing") ? "parent" : "none";
	if (t.wrap.effectExtent !== null) {
		let e = gS(t.wrap.effectExtent, "wrap.effectExtent", !0);
		if (e.problem || !e.values) return xS({
			status: "unsupported",
			occurrenceId: t.occurrenceId,
			axes: {
				horizontal: i.diagnostic,
				vertical: a.diagnostic
			},
			issues: [e.problem]
		});
		d = e.values, f = "wrap-child";
	}
	let p = null, m = null, h = null;
	if (t.wrap.kind === "tight" || t.wrap.kind === "through") {
		let e = yS(t, r);
		if (e.problem || !e.polygon || !e.bounds) return xS({
			status: "unsupported",
			occurrenceId: t.occurrenceId,
			axes: {
				horizontal: i.diagnostic,
				vertical: a.diagnostic
			},
			issues: [e.problem]
		});
		p = e.polygon, m = {
			width: 21600,
			height: 21600
		}, h = e.bounds, d = {
			topPt: 0,
			rightPt: 0,
			bottomPt: 0,
			leftPt: 0
		}, f = "none";
	} else if (t.wrap.kind !== "none" && (h = vS(r, d), h === null)) {
		let e = $("invalid-effect-extent", "wrap.effectExtent", "wrapping effect extents produce invalid bounds");
		return xS({
			status: "unsupported",
			occurrenceId: t.occurrenceId,
			axes: {
				horizontal: i.diagnostic,
				vertical: a.diagnostic
			},
			issues: [e]
		});
	}
	let g = h === null ? null : vS(h, c.resolved.values);
	if (h !== null && g === null) {
		let e = $("invalid-distance", "wrap.distances", "distances produce invalid bounds");
		return xS({
			status: "unsupported",
			occurrenceId: t.occurrenceId,
			axes: {
				horizontal: i.diagnostic,
				vertical: a.diagnostic
			},
			issues: [e]
		});
	}
	return xS({
		status: "resolved",
		occurrenceId: t.occurrenceId,
		axes: {
			horizontal: i.diagnostic,
			vertical: a.diagnostic
		},
		issues: [],
		geometry: {
			objectFrame: r,
			inkBounds: s,
			wrapBounds: g,
			size: n.geometry.size,
			parentEffectExtent: o.values,
			wrap: {
				kind: t.wrap.kind,
				side: u,
				distances: c.resolved.values,
				distanceSources: c.resolved.sources,
				effectExtent: d,
				effectExtentSource: f,
				coordinateSpace: m,
				polygon: p
			},
			transform: bS(t.group)
		}
	});
}
function wS(e, t, n, r) {
	if (!e) return r;
	let i = !!(e.styleId && e.styleId === t.styleId), a = !!(i && e.contextualSpacing), o = !!(i && t.contextualSpacing);
	return a && o ? 0 : o ? n : a ? Math.max(r - n, 0) : Math.max(n, r);
}
function TS(e, t, n, r) {
	let i = wS(e, t, n, r), a = i <= n;
	return {
		suppressBefore: a,
		overlap: n + (a ? 0 : r) - i
	};
}
function ES(e, t, n) {
	return n ? {
		spaceBefore: e.spaceBefore ?? 0,
		spaceAfter: e.spaceAfter ?? 0
	} : {
		spaceBefore: e.beforeAutospacing === !0 ? t : e.spaceBefore ?? 0,
		spaceAfter: e.afterAutospacing === !0 ? t : e.spaceAfter ?? 0
	};
}
function DS(e) {
	return Object.freeze(e.pages.map((e) => Object.freeze({
		pageIndex: e.pageIndex,
		displayPageNumber: e.pageNumber.displayNumber,
		pageNumberFormat: e.pageNumber.format
	})));
}
function OS(e) {
	if (e.fieldType === "page") return "page";
	if (/numPages/i.test(e.fieldType) || /NUMPAGES/i.test(e.instruction)) return "total-pages";
}
function kS(e) {
	return e.some((e) => e.type === "paragraph" ? e.runs.some((e) => e.type === "field" ? OS(e) !== void 0 : !1) : e.type === "table" ? e.rows.some((e) => e.cells.some((e) => kS(e.content))) : !1);
}
function AS(e, t = [], n = []) {
	return kS(e) || t.some((e) => kS(e.content)) || n.some((e) => kS(e));
}
var jS = /* @__PURE__ */ new WeakMap(), MS = "table-final-frame:";
function NS(e) {
	let t = new Set(e.drawings.flatMap((e) => {
		let t = e.anchorLayer?.acquisitionOccurrenceId ?? e.anchorLayer?.occurrenceId;
		return t === void 0 ? [] : [t];
	}));
	return Object.freeze({
		exclusions: Object.freeze(e.exclusions.filter((e) => !e.id.startsWith("table-final-frame:") && (e.anchorOccurrenceId === void 0 || !t.has(e.anchorOccurrenceId)))),
		collisions: Object.freeze((e.anchorCollisions ?? []).filter((e) => !t.has(e.occurrenceId)))
	});
}
function PS(e) {
	return new Set((e.anchorFrames ?? []).flatMap((e) => e.status === "resolved" ? [e.occurrenceId] : []));
}
function FS(e) {
	let t = PS(e), n = (e.anchorCollisions ?? []).filter((e) => t.has(e.occurrenceId)), r = new Set(n.map((e) => e.occurrenceId));
	for (let e of t) if (!r.has(e)) throw Error(`Paragraph anchor omitted collision geometry: ${e}`);
	return Object.freeze(n);
}
function IS(e) {
	let t = PS(e);
	return Object.freeze(e.exclusions.filter((e) => e.anchorOccurrenceId !== void 0 && t.has(e.anchorOccurrenceId)));
}
function LS(e) {
	return Object.freeze({
		flowDomainId: e,
		collisions: Object.freeze([]),
		exclusions: Object.freeze([])
	});
}
function RS(e, t) {
	let n = jS.get(e);
	n || (n = /* @__PURE__ */ new Map(), jS.set(e, n));
	let r = n.get(t);
	if (r) return r;
	let i = LS(t);
	return n.set(t, i), i;
}
function zS(e, t, n) {
	let r = jS.get(e);
	if (!r || r.get(t.flowDomainId) !== t) throw Error("Paragraph wrap registry transaction is stale");
	r.set(t.flowDomainId, BS(t, n));
}
function BS(e, t) {
	if (t.flowDomainId !== e.flowDomainId) throw Error("Paragraph wrap registry cannot cross flow domains");
	let n = new Set(e.collisions.map((e) => e.occurrenceId)), r = FS(t);
	for (let e of r) {
		if (n.has(e.occurrenceId)) throw Error(`Paragraph wrap occurrence committed twice: ${e.occurrenceId}`);
		n.add(e.occurrenceId);
	}
	let i = IS(t), a = new Set(r.map((e) => e.occurrenceId)), o = /* @__PURE__ */ new Set();
	for (let e of i) {
		let t = e.anchorOccurrenceId;
		if (t === void 0 || !a.has(t)) throw Error("Owned paragraph wrap exclusion omitted its collision occurrence");
		if (o.has(t)) throw Error(`Paragraph wrap occurrence produced duplicate exclusions: ${t}`);
		o.add(t);
	}
	return Object.freeze({
		flowDomainId: e.flowDomainId,
		collisions: Object.freeze([...e.collisions, ...r]),
		exclusions: Object.freeze([...e.exclusions, ...i])
	});
}
function VS(e) {
	let t = e.storyFlowPt ?? {
		xPt: 0,
		yPt: 0
	}, n = (e) => Object.freeze({
		...e,
		xPt: e.xPt + t.xPt,
		yPt: e.yPt + t.yPt
	});
	return Object.freeze({
		frames: Object.freeze({
			page: n(e.page),
			margin: n(e.margin)
		}),
		flowPt: t
	});
}
function HS(e, t) {
	let n = Mb(t, e.page), r = Mb(t, e.margin);
	return n && r ? Object.freeze({
		page: n,
		margin: r
	}) : null;
}
function US(e, t, n) {
	let r = (e) => JSON.stringify(e), i = null, a = (t) => {
		if (!t) return null;
		let n = t.page.xPt - e.page.xPt, r = t.page.yPt - e.page.yPt, a = (e, t) => t.widthPt === e.widthPt && t.heightPt === e.heightPt && t.xPt === e.xPt + n && t.yPt === e.yPt + r;
		if (!a(e.page, t.page) || !a(e.margin, t.margin) || e.storyFlowPt === void 0 != (t.storyFlowPt === void 0) || e.storyFlowPt && t.storyFlowPt && (t.storyFlowPt.xPt !== e.storyFlowPt.xPt - n || t.storyFlowPt.yPt !== e.storyFlowPt.yPt - r) || n !== 0 && r !== 0) return null;
		if (n === 0 && r === 0) return 0;
		let o = n === 0 ? "yPt" : "xPt";
		return i !== null && i !== o ? null : (i = o, o === "xPt" ? n : r);
	}, o = (t) => {
		let n = i === "xPt" ? t : 0, r = i === "yPt" ? t : 0, a = (e) => Object.freeze({
			...e,
			xPt: e.xPt + n,
			yPt: e.yPt + r
		});
		return Object.freeze({
			page: a(e.page),
			margin: a(e.margin),
			...e.storyFlowPt ? { storyFlowPt: Object.freeze({
				xPt: e.storyFlowPt.xPt - n,
				yPt: e.storyFlowPt.yPt - r
			}) } : {}
		});
	}, s = [], c = /* @__PURE__ */ new Set(), l = (e) => Number.isFinite(e) && !c.has(r(o(e))), u = GS(l), d = e;
	for (let e = 1; e <= n; e += 1) {
		let n = r(d);
		s.push(n), c.add(n);
		let { value: f, next: p } = t(d);
		if (r(p) === n) return f;
		let m = a(d), h = a(p);
		if (m === null || h === null || i === null) {
			if (c.has(r(p))) throw new Go("cycle", [...s, r(p)], e);
			d = p;
			continue;
		}
		let g = u(m, h);
		if (!l(g)) throw new Go("cycle", [...s, r(o(g))], e);
		d = o(g);
	}
	throw new Go("limit", s, n);
}
function WS(e, t, n) {
	let r = [], i = /* @__PURE__ */ new Set(), a = (e) => Number.isFinite(e) && !i.has(e), o = GS(a), s = e;
	for (let e = 1; e <= n; e += 1) {
		r.push(JSON.stringify(s)), i.add(s);
		let { value: n, implied: c } = t(s);
		if (c === s) return n;
		let l = o(s, c);
		if (!a(l)) throw new Go("cycle", [...r, JSON.stringify(l)], e);
		s = l;
	}
	throw new Go("limit", r, n);
}
function GS(e) {
	let t = [], n = !1, r = 1;
	return (i, a) => {
		t.push({
			t: i,
			r: a - i
		});
		let o = null, s = null;
		for (let e of t) if (!(e.r <= 0)) for (let n of t) n.r >= 0 || (!o || !s || Math.abs(e.t - n.t) < Math.abs(o.t - s.t)) && (o = e, s = n);
		if (o && s) {
			let t = Math.min(o.t, s.t), r = Math.max(o.t, s.t), i = (n) => n > t && n < r && e(n), c = o.t - o.r * (s.t - o.t) / (s.r - o.r);
			return !n && i(a) ? (n = !0, a) : (n = !1, i(c) ? c : (t + r) / 2);
		}
		if (t.length === 1) return a;
		let [c, l] = t.slice(-2), u = l.r === c.r ? NaN : l.t - l.r * (l.t - c.t) / (l.r - c.r);
		return r *= 2, Number.isFinite(u) && Math.sign(u - l.t) === Math.sign(l.r) ? u : l.t + r * l.r;
	};
}
function KS(e, t) {
	if (!Number.isFinite(e) || e < 0) throw RangeError(`${t} must be finite and non-negative`);
	return e;
}
function qS(e) {
	if (!(!e || e.type !== "text" && e.type !== "field")) return e.typographyInput;
}
function JS(e) {
	switch (e) {
		case "left": return "left";
		case "right": return "right";
		default: return "center";
	}
}
function YS(e) {
	return KS(e.measuredWidthPt, "segment.measuredWidthPt");
}
function XS(e, t, n) {
	let r = e.length, i = !1;
	for (; r > 0;) {
		let t = e[r - 1];
		if (t?.kind === "anchor-host") {
			--r;
			continue;
		}
		if (t?.kind !== "text") break;
		let n = SC(t.text);
		if (n < t.text.length && (i = !0), n > 0) break;
		--r;
	}
	let a = i && yr(t, n);
	return e.map((e, t) => e.kind === "text" && !e.fixedPitch && !e.listLabel ? { text: e.text } : a && t >= r && e.kind === "anchor-host" ? { text: "" } : {});
}
function ZS(e, t) {
	if (t) return;
	let n = (e) => e >= 3584 && e <= 3711, r = [], i = [], a = [], o = !1;
	for (let t of e) {
		if (a.push(r.length), t.kind !== "text" || t.fixedPitch || t.fitText || t.ruby || t.direction !== "ltr" || (t.writingMode ?? "horizontal-tb") !== "horizontal-tb" || (t.characterSpacingPt ?? 0) !== 0 || (t.characterScale ?? 1) !== 1 || (t.characterGridDeltaPt ?? 0) !== 0) return;
		let e = new Map(t.clusters.map((e) => [e.range.start - t.range.start, e.advancePt])), s = 0;
		for (let a of t.text) {
			let t = a.codePointAt(0), c = r.at(-1);
			if (!n(t) && (t < 32 || t > 126) || c !== void 0 && n(t) !== n(c) && t !== 32 && c !== 32 || x(t) && (c === void 0 || c === 32) || s > 0 && c !== void 0 && (n(c) || c === 32) && !x(t) && !e.has(s)) return;
			o ||= n(t), r.push(t), i.push(e.get(s) ?? 0), s += a.length;
		}
	}
	if (o) return (e, t) => {
		let n = (a[e] ?? 0) + t;
		if (r[n] === 32) return i[n] ?? 0;
		let o = 0;
		for (; n >= 0 && (o += i[n] ?? 0, x(r[n] ?? 0)); --n);
		return o;
	};
}
function QS(e) {
	return iC(e.alignment) === null ? !(e.alignment === "thaiDistribute" && e.lineEndJustificationBeforeMode15 === !0) : !1;
}
function $S(e, t, n, r, i) {
	let a = n;
	e.forEach((e, t) => {
		e.kind === "tab" && (a = Math.max(a, t + 1));
	});
	let o = /* @__PURE__ */ new Map(), s = i;
	for (let t = e.length - 1; t >= a; --t) {
		let n = e[t];
		if (n.kind !== "text") {
			n.kind !== "anchor-host" && (s = !1);
			continue;
		}
		let r = s ? SC(n.text) : n.text.length;
		o.set(t, r), r > 0 && (s = !1);
	}
	let c = /* @__PURE__ */ new Map(), l = 0;
	for (let t = a; t < e.length; t += 1) {
		let n = e[t];
		if (n.kind === "anchor-host" || n.kind === "tab") continue;
		let r = n.kind === "text" ? o.get(t) ?? n.text.length : 1;
		if (r === 0) continue;
		if (n.kind !== "text" || n.fixedPitch) {
			c.set(t, [0]), l += 1;
			continue;
		}
		let i = n.clusters.map((e) => e.range.start - n.range.start).filter((e) => e < r);
		i.length !== 0 && (c.set(t, i), l += i.length);
	}
	if (l < 2 || !(t > 0)) return null;
	let u = [...r].reverse().find((e) => c.has(e)), d = [...c.keys()], { closed: f, boundaries: p } = eC(e, d);
	for (let t of d) {
		let n = e[t], r = p.get(t);
		if (n.kind !== "text" || n.fixedPitch || !r) continue;
		let i = /* @__PURE__ */ new Map(), a = 0;
		[...n.text].forEach((e, t) => {
			i.set(a, t), a += e.length;
		});
		let [o, ...s] = c.get(t);
		c.set(t, [o, ...s.filter((e) => r.has(e))].map((e) => i.get(e)));
	}
	let m = new Set(d.filter((e) => e !== u && !f.has(e))), h = [...c.values()].reduce((e, t) => e + t.length - 1, 0) + m.size;
	if (h === 0) return null;
	let g = t / h, _ = /* @__PURE__ */ new Map();
	for (let [e, t] of c) {
		let n = t.slice(1);
		_.set(e, {
			splitBefore: n,
			internalStretch: g * n.length,
			trailingGap: m.has(e)
		});
	}
	return {
		perGap: g,
		perSeg: _
	};
}
function eC(e, t) {
	let n = /* @__PURE__ */ new Set(), r = /* @__PURE__ */ new Map(), i = [], a = () => {
		if (i.length === 0) return;
		let t = "", a = [];
		for (let n of i) a.push(t.length), t += e[n].text;
		let o = b(t), s = 0;
		i.forEach((e, c) => {
			let l = a[c], u = a[c + 1] ?? t.length, d = /* @__PURE__ */ new Set();
			for (; s < o.length && o[s] < u;) o[s] >= l && d.add(o[s] - l), s += 1;
			r.set(e, d), c + 1 < i.length && o[s] !== u && n.add(e);
		}), i = [];
	};
	return t.forEach((r, o) => {
		let s = e[r], c = t[o + 1], l = c === void 0 ? void 0 : e[c], u = s.kind === "text" ? s.fitText?.regionIndex : void 0;
		if (u !== void 0 && l?.kind === "text" && l.fitText?.regionIndex === u && n.add(r), s.kind !== "text" || s.text === "") {
			a();
			return;
		}
		i.push(r);
		let d = c === void 0 ? [] : e.slice(r + 1, c);
		(l?.kind !== "text" || d.some((e) => e.kind !== "anchor-host")) && a();
	}), a(), {
		closed: n,
		boundaries: r
	};
}
function tC(e) {
	for (let t = e.length - 1; t >= 0; --t) if (e[t].kind === "tab") return t;
	return -1;
}
function nC(e, t, n, r) {
	return e.some((e) => e.kind === "text" && /\S/.test(e.text)) ? !n || be(t, {
		firstContentSi: r,
		lastDrawnSi: Infinity
	}).gaps.length === 0 : !1;
}
function rC(e, t) {
	let n = /* @__PURE__ */ new Map();
	for (let t = e.length - 1; t >= 0; --t) {
		let r = e[t];
		if (r.kind === "anchor-host") continue;
		if (r.kind !== "text") break;
		let i = SC(r.text, (e) => e === 32), a = r.clusters.filter((e) => e.range.start >= r.range.start + i).reduce((e, t) => e + t.advancePt, 0);
		if (a > 0 && n.set(t, {
			widthPt: a,
			spacesOnly: i === 0
		}), i > 0) break;
	}
	let r = t.order.filter((t) => e[t]?.kind !== "anchor-host"), i = /* @__PURE__ */ new Set(), a = (e, t) => {
		let r = 0;
		for (let a of e) {
			let e = n.get(a);
			if (!e || i.has(a) || !e.spacesOnly && !t(a) || (r += e.widthPt, i.add(a), !e.spacesOnly)) break;
		}
		return r;
	}, o = a([...r].reverse(), (e) => t.rtl[e] !== !0), s = a(r, (e) => t.rtl[e] === !0), c = [];
	for (let [e, { widthPt: a, spacesOnly: o }] of n) {
		if (i.has(e)) continue;
		let n = r.indexOf(e), s = o || t.rtl[e] !== !0 ? e : r[n - 1];
		s !== void 0 && c.push({
			owner: s,
			widthPt: a
		});
	}
	return {
		rightPt: o,
		leftPt: s,
		interior: c
	};
}
function iC(e) {
	return e === "lowKashida" ? "low" : e === "mediumKashida" ? "medium" : e === "highKashida" ? "high" : null;
}
function aC(e, t, n, r) {
	return !e.textLayoutService || !e.textShapeRequest ? r : e.textLayoutService.shape({
		...As(e.textShapeRequest, t),
		fontSizePt: q(e, 1),
		measure: !0,
		clusterGeometry: !1
	}).advancePt * n;
}
function oC(e, t) {
	let n = e.basePaintOps[0]?.letterSpacingPt ?? 0, r = e.characterGridDeltaPt ?? 0;
	if (n >= 0 && r >= 0) return !1;
	if (!e.textLayoutService || !e.textShapeRequest) throw Error("Kashida acquisition requires the retained TextLayoutService authority");
	let i = e.basePaintOps[0]?.scaleX ?? 1;
	return (e.textLayoutService.shape({
		...js(e.textShapeRequest, t),
		measure: !0,
		clusterGeometry: !0
	}).clusters ?? []).some((e) => is(t.slice(e.range.start, e.range.end), e.advancePt * i, r, n - r) > 0);
}
function sC(e, t) {
	if (!e.textLayoutService || !e.textShapeRequest) throw Error("Kashida acquisition requires the retained TextLayoutService authority");
	let n = e.basePaintOps[0]?.scaleX ?? 1, r = e.basePaintOps[0]?.letterSpacingPt ?? 0, i = e.characterGridDeltaPt ?? 0, a = r < 0 || i < 0, o = e.textLayoutService.shape({
		...js(e.textShapeRequest, t),
		measure: !0,
		...a ? { clusterGeometry: !0 } : {}
	}), s = a ? (o.clusters ?? []).reduce((e, a) => e + is(t.slice(a.range.start, a.range.end), a.advancePt * n, i, r - i), 0) : 0;
	return o.advancePt * n + ts(t, i, r - i, r) + s;
}
function cC(e, t) {
	if (!e) return null;
	if ([...e.perSeg.values()].some((e) => e.gapDeltas !== void 0)) {
		for (let [n, r] of e.perSeg) {
			let e = t[n];
			if (e?.kind !== "text") continue;
			let i = new Set(e.clusters.map((t) => t.range.start - e.range.start)), a = [...e.text], o = 0, s = a.map((e) => {
				let t = o;
				return o += e.length, t;
			});
			if (r.splitBefore.some((e) => !i.has(s[e]))) throw Error("Proportional space justification requires a retained cluster boundary");
		}
		return e;
	}
	let n = fx(e), r = /* @__PURE__ */ new Map(), i = 0;
	for (let [n, a] of e.perSeg) {
		let e = t[n], o = a.splitBefore;
		if (e?.kind === "text") {
			let t = new Set(e.clusters.slice(1).map((t) => t.range.start - e.range.start)), n = [...e.text], r = [0];
			for (let e of n) r.push((r.at(-1) ?? 0) + e.length);
			o = o.filter((e) => t.has(r[e] ?? -1));
		}
		let s = t[n + 1], c = a.trailingGap && !(s?.kind === "text" && s.breakBefore === !1);
		i += o.length + +!!c, r.set(n, {
			splitBefore: [...o],
			trailingGap: c,
			internalStretch: 0
		});
	}
	if (i === 0) return null;
	let a = n / i;
	for (let e of r.values()) e.internalStretch = e.splitBefore.length * a;
	return {
		perGap: a,
		perSeg: r
	};
}
function lC(e, t, n) {
	if (!t || t.splitBefore.length === 0) return {
		clusters: e.clusters,
		paintOps: e.basePaintOps
	};
	let r = t.splitBefore, i = t.gapDeltas;
	if (i && i.length !== r.length) throw Error("Internal paragraph justification has incomplete gap deltas");
	let a = [], o = 0, s = e.range.start, c = 0;
	for (let t of e.text) r[c] === o && (a.push(s), c += 1), o += 1, s += t.length;
	if (c !== r.length || r.some((e, t) => e <= 0 || t > 0 && e <= r[t - 1])) throw Error("Internal paragraph justification contains an invalid code-point cut");
	let l = 0, u = 0, d = e.clusters.map((e) => {
		let t = a[l];
		if (t !== void 0 && t < e.range.start) throw Error("Internal paragraph justification must split at shaped cluster boundaries");
		return t === e.range.start && (u += i?.[l] ?? n, l += 1), {
			...e,
			offset: {
				...e.offset,
				xPt: e.offset.xPt + u
			}
		};
	});
	if (l !== a.length) throw Error("Internal paragraph justification must split at shaped cluster boundaries");
	let f = e.range.start;
	for (let t of e.basePaintOps) {
		if (t.range.start !== f || t.range.end <= f) throw Error("Internal paragraph justification has incomplete retained paint operations");
		f = t.range.end;
	}
	if (f !== e.range.end || e.basePaintOps.length === 0) throw Error("Internal paragraph justification has incomplete retained paint operations");
	let p = e.basePaintOps[0];
	if (e.basePaintOps.length === 1 && r.length === o - 1 && r.every((e, t) => e === t + 1) && (!i || i.every((e) => e === i[0]))) return {
		clusters: d,
		paintOps: [{
			...p,
			letterSpacingPt: p.letterSpacingPt + (i?.[0] ?? n)
		}]
	};
	let m = [], h = 0;
	l = 0, u = 0;
	for (let t of e.basePaintOps) {
		let e = t.range.start;
		for (; e < t.range.end;) {
			for (; a[l] !== void 0 && a[l] <= e;) u += i?.[l] ?? n, l += 1;
			for (; d[h] && d[h].range.start < e;) h += 1;
			let r = d[h];
			if (!r || r.range.start !== e) throw Error("Internal paragraph justification is missing retained slice geometry");
			let o = Math.min(t.range.end, a[l] ?? t.range.end);
			m.push({
				...t,
				text: t.text.slice(e - t.range.start, o - t.range.start),
				range: {
					start: e,
					end: o
				},
				offset: e === t.range.start ? {
					...t.offset,
					xPt: t.offset.xPt + u
				} : r.offset
			}), e = o;
		}
	}
	return {
		clusters: d,
		paintOps: m
	};
}
function uC(e, t) {
	return e.flatMap((e) => {
		let n = e.text.trimEnd();
		if (n === "" || n.length === e.text.length) return [e];
		if (e.sourceMapping === "kashida") return [{
			...e,
			text: n
		}];
		let r = e.range.start + n.length, i = t.find((e) => e.range.start === r), { inkBounds: a, blockAxisInkBounds: o, ...s } = e;
		return [{
			...e,
			text: n,
			range: {
				...e.range,
				end: r
			}
		}, {
			...s,
			text: e.text.slice(n.length),
			range: {
				start: r,
				end: e.range.end
			},
			offset: i?.offset ?? e.offset
		}];
	});
}
function dC(e) {
	return e % 2 == 1 ? "rtl" : "ltr";
}
function fC(e) {
	let t = e.map((e) => e.xPt), n = e.map((e, t) => t), r = 0, i = Infinity;
	for (let t of e) r = Math.max(r, t.level), t.level % 2 == 1 && (i = Math.min(i, t.level));
	for (let a = r; a >= i; --a) {
		let r = [], i = 0;
		for (; i < n.length;) {
			if (e[n[i]].level < a) {
				r.push(n[i]), i += 1;
				continue;
			}
			let o = i, s = Infinity, c = -Infinity;
			for (; o < n.length && e[n[o]].level >= a;) {
				let r = n[o];
				s = Math.min(s, t[r]), c = Math.max(c, t[r] + e[r].advancePt), o += 1;
			}
			for (let a = o - 1; a >= i; --a) {
				let i = n[a];
				t[i] = s + c - t[i] - e[i].advancePt, r.push(i);
			}
			i = o;
		}
		n = r;
	}
	return e.map((e, n) => e.drawnAdvancePt !== void 0 && e.level % 2 == 1 ? t[n] + e.advancePt - e.drawnAdvancePt : t[n]);
}
function pC(e, t, n) {
	let r = 0;
	return e.map((e) => {
		let i = 0;
		for (; r < t.length && t[r].range.start < e.range.end;) {
			let a = t[r];
			a.range.start >= e.range.start && a.range.start < n && (i += a.advancePt), r += 1;
		}
		return i;
	});
}
function mC(e, t) {
	return t === "rtl" || s(e);
}
function hC(e, t, n, r, i, a) {
	if (!e.some((e) => e.naturalAdvancePt !== void 0)) return e;
	let o = n.slice(0, a - r);
	if (!mC(o, i)) return e;
	let s = cs(o, i), c = pC(e, t, a), l = e.flatMap((e, t) => e.range.start < a ? [t] : []), u = fC(l.map((t) => {
		let n = e[t];
		return {
			xPt: n.offset.xPt,
			advancePt: c[t],
			...n.naturalAdvancePt === void 0 ? {} : { drawnAdvancePt: n.naturalAdvancePt },
			level: s[n.range.start - r]
		};
	})), d = 0;
	for (let t of l) d = Math.max(d, e[t].offset.xPt + c[t]);
	let f = 0;
	return e.map((e) => e.range.start < a ? {
		...e,
		offset: {
			...e.offset,
			xPt: u[f++]
		},
		direction: dC(s[e.range.start - r])
	} : i === "rtl" ? {
		...e,
		offset: {
			...e.offset,
			xPt: d - e.offset.xPt
		}
	} : e);
}
function gC(e, t, n, r, i, a) {
	if (!e.some((t, n) => n > 0 && t.glyphOrientation === "sideways" && e[n - 1].glyphOrientation === "sideways")) return e;
	let o = pC(e, t, a), s = [...e], c = 0;
	for (; c < e.length;) {
		if (e[c].glyphOrientation !== "sideways") {
			c += 1;
			continue;
		}
		let t = c;
		for (; t < e.length && e[t].glyphOrientation === "sideways" && e[t].range.start < a;) t += 1;
		let l = e[c].range.start, u = t > c ? n.slice(l - r, e[t - 1].range.end - r) : "";
		if (t - c > 1 && mC(u, i)) {
			let n = cs(u, i), r = e.slice(c, t), a = fC(r.map((e, t) => ({
				xPt: e.offset.xPt,
				advancePt: o[c + t],
				...e.naturalAdvancePt === void 0 ? {} : { drawnAdvancePt: e.naturalAdvancePt },
				level: n[e.range.start - l]
			})));
			r.forEach((e, t) => {
				s[c + t] = {
					...e,
					offset: {
						...e.offset,
						xPt: a[t]
					},
					direction: dC(n[e.range.start - l])
				};
			});
		}
		for (c = Math.max(t, c + 1); c < e.length && e[c].glyphOrientation === "sideways" && e[c].range.start >= a;) c += 1;
	}
	return s;
}
function _C(e, t) {
	return e === void 0 || t === void 0 ? e === t : e.length === t.length && e.every((e, n) => e === t[n]);
}
function vC(e, t) {
	if (e === t) return !0;
	let n = 2 ** -52 * Math.max(1, Math.abs(e) + Math.abs(t));
	return Math.abs(e - t) <= n;
}
function yC(e, t) {
	return e.kind === "underline" && e.kind === t.kind && e.authoredStyle === t.authoredStyle && e.style === t.style && e.color === t.color && e.widthPt === t.widthPt && vC(e.to.xPt, t.from.xPt) && _C(e.dashPatternPt, t.dashPatternPt);
}
function bC(e, t) {
	let n = Math.max(e.from.yPt, t.from.yPt), r = {
		xPt: e.from.xPt,
		yPt: n
	}, i = {
		xPt: t.to.xPt,
		yPt: n
	}, { path: a, ...o } = e;
	return {
		...o,
		from: r,
		to: i,
		...e.style === "wavy" ? { path: Hx(r, i, e.widthPt) } : {}
	};
}
function xC(e, t) {
	let n = Math.min(t, Math.max(0, e.to.xPt - e.from.xPt)), r = e.from, i = {
		...e.to,
		xPt: e.to.xPt - n
	}, { path: a, ...o } = e;
	return {
		...o,
		from: r,
		to: i,
		...e.style === "wavy" ? { path: Hx(r, i, e.widthPt) } : {}
	};
}
function SC(e, t = (e) => e === 32 || e === 12288) {
	let n = e.length;
	for (; n > 0 && t(e.charCodeAt(n - 1));) --n;
	return n;
}
function CC(e, t) {
	let n = t.length - 1, r = 0;
	for (; n >= 0; --n) {
		let e = t[n];
		if (e.kind === "anchor-host") continue;
		if (e.kind !== "text") break;
		let i = SC(e.text);
		if (i > 0) {
			r = [...e.text.slice(0, i)].length;
			break;
		}
	}
	return e.filter((e) => e.segIndex < n || e.segIndex === n && e.cpOffset < r - 1);
}
function wC(e, t, n) {
	let r = e.clusters.filter((n) => n.range.start >= e.range.start + t).reduce((e, t) => e + t.advancePt, 0) + (e.ownedTrailingSlackPt ?? 0);
	if (r <= 0) return e;
	let i = (e) => e.kind === "overline" || n && e.kind === "underline", a = t === 0 ? e.decorations?.filter(i) : e.decorations?.map((e) => i(e) ? e : xC(e, r)), o = (e) => ({
		...e,
		widthPt: Math.max(0, e.widthPt - r)
	}), s = t === 0 ? e.highlightFragments ? [] : void 0 : e.highlightFragments?.map((e) => ({
		...e,
		rect: o(e.rect)
	}));
	return {
		...e,
		...a ? { decorations: a } : {},
		...s ? { highlightFragments: s } : {},
		...e.highlightBounds ? { highlightBounds: o(e.highlightBounds) } : {}
	};
}
function TC(e, t) {
	let n = (e) => e.xPt + e.widthPt > t ? {
		...e,
		widthPt: Math.max(0, t - e.xPt)
	} : e;
	return {
		...e,
		...e.decorations ? { decorations: e.decorations.filter((e) => e.from.xPt < t).map((e) => e.to.xPt > t ? xC(e, e.to.xPt - t) : e) } : {},
		...e.highlightFragments ? { highlightFragments: e.highlightFragments.map((e) => ({
			...e,
			rect: n(e.rect)
		})) } : {},
		...e.highlightBounds ? { highlightBounds: n(e.highlightBounds) } : {}
	};
}
function EC(e) {
	let t = [];
	e.forEach((n, r) => {
		if (n.kind !== "text" && n.kind !== "tab" || !n.decorations) {
			t = [];
			return;
		}
		let i = [], a = [], o = /* @__PURE__ */ new Set();
		for (let s of n.decorations) {
			let n = t.filter((e) => !o.has(e) && yC(e.decoration, s)).sort((e, t) => Math.abs(e.decoration.from.yPt - s.from.yPt) - Math.abs(t.decoration.from.yPt - s.from.yPt))[0];
			if (n) {
				o.add(n);
				let t = e[n.placementIndex];
				if (!t || t.kind !== "text" && t.kind !== "tab" || !t.decorations) throw Error("Continuous decoration owner left the retained line");
				let r = [...t.decorations], i = bC(n.decoration, s);
				r[n.decorationIndex] = i, e[n.placementIndex] = {
					...t,
					decorations: r
				}, a.push({
					...n,
					decoration: i
				});
			} else {
				let e = i.length;
				i.push(s), a.push({
					placementIndex: r,
					decorationIndex: e,
					decoration: s
				});
			}
		}
		e[r] = {
			...n,
			decorations: i
		}, t = a;
	});
}
function DC(e, t, n = 0) {
	if (!(t > 0)) return;
	let r = [], i = 0;
	if (e.forEach((e, t) => {
		if (t <= n || e.kind !== "text" || !e.autoSpace) return;
		let a = kr(e.autoSpace.naturalPt) - e.autoSpace.appliedPt;
		a > 0 && (r.push([t - 1, a]), i += a);
	}), !(i > 0)) return;
	let a = Math.min(t, i), o = /* @__PURE__ */ new Map();
	for (let [e, t] of r) o.set(e, (o.get(e) ?? 0) + a * t / i);
	return {
		takenPt: a,
		trailingByIndex: o
	};
}
function OC(e, t, n) {
	if (!n) return e;
	let r = new Map(e ?? []);
	for (let [e, i] of n.trailingByIndex) {
		let n = r.get(e), a = n?.trailingGap ? n.trailingDelta ?? t : 0;
		r.set(e, {
			splitBefore: n?.splitBefore ?? [],
			internalStretch: n?.internalStretch ?? 0,
			...n?.gapDeltas ? { gapDeltas: n.gapDeltas } : {},
			trailingGap: !0,
			trailingDelta: a + i
		});
	}
	return r;
}
function kC(e) {
	let { line: t } = e, n = t.segments, r = e.baseRtl || Si(n), i = r && e.displayMathJustification === void 0 && Mi(e.alignment, e.baseRtl) === "justify" && si(e, t.endsWithBreak) === "character", a = n.reduce((e, t) => e + YS(t), 0), o = e.paragraphXPt + t.xOffsetPt, s = Math.min(e.availableWidthPt, t.availableWidthPt) + (t.marginExtensionPt ?? 0), c = (e.isFirstLine ? e.numbering ? KS(e.numbering.bodyOffsetPt, "numbering.bodyOffsetPt") : e.firstLineIndentPt ?? 0 : 0) - (e.listLabelShiftPt ?? 0), l = e.baseRtl ? 0 : c, u = e.baseRtl ? s - c : s, d = u - l - a, f = e.displayMathJustification === void 0 ? Mi(e.alignment, e.baseRtl) : JS(e.displayMathJustification), p = f === "justify" ? si(e, t.endsWithBreak) : null, m = p === "character" && r ? "word" : p, h = m !== null, g = tC(n) + 1, _, v = e.displayMathJustification === void 0 && _r(e.baseRtl === !0, e.wordWrap !== !1), y = n[0]?.kind === "text" && n[0].nativeBaseDirection !== void 0 && n.every((e) => e.kind === "text" && e.nativeBaseDirection !== void 0);
	if (r && !i && !e.runDirectionUnauthored && (m === "word" || m === "word-or-centre" || y) && iC(e.alignment) === null && d + (v ? TT(n, (e) => e.replace(/ +$/u, "").length) : 0) >= -1e-6 && t.gapPlan === void 0 && t.justifiedCompressionPt === void 0) {
		let t = y || yr(r, e.wordWrap !== !1) || v;
		(!wT(n) || t) && (_ = Pb(n));
	}
	let b = n.map((e) => e.kind === "tab" ? { isTab: !0 } : e.kind === "text" ? {
		text: e.text,
		rtl: e.rtl,
		digitsAsAN: e.digitsAsAN
	} : {}), x = y && n.some((e) => e.kind === "text" && e.text.includes(" "));
	if (x && !_) throw TypeError("Selected native source bundle lost projectable SPACE geometry");
	let S = xi({
		baseRtl: e.baseRtl,
		alignment: e.alignment,
		runDirectionUnauthored: e.runDirectionUnauthored,
		characterSpreadBidi: i
	}), C = _ ? Di(b, _.projection, e.baseRtl, S) : void 0;
	if (x && C?.view !== "cells") throw TypeError("Selected native source bundle lost its authored host projection");
	let w = C?.view === "cells" ? _.materialize() : void 0;
	w && (n = w.segments);
	let T = C ? {
		order: C.order,
		rtl: w ? C.rtl.map((e, t) => w.spaceOnly[t] ? (C.anchorLevels[t] & 1) == 1 : e) : C.rtl
	} : Ei(b, e.baseRtl, S), E = !t.endsWithBreak && !e.isLastLine && vr(e.alignment), D = w?.parentCellStarts[g] ?? g, O = v, k = O ? rC(n, T) : {
		rightPt: 0,
		leftPt: 0,
		interior: []
	}, A = k.rightPt + k.leftPt, j = k.interior.reduce((e, { widthPt: t }) => e + t, 0), M = h ? Math.min(j, Math.max(0, -(d + A))) : 0, N = h && e.alignment !== "lowKashida", P = (N ? A : Math.min(A, Math.max(0, -d))) + M, F = h ? iC(e.alignment) : null, I = 0;
	if (F && d + P > 0) {
		let e = /* @__PURE__ */ new Set(), t = () => Nx(n.map((t, n) => t.kind === "text" && n >= D && t.basePaintOps.length === 1 && t.basePaintOps[0].naturalAdvancePt === void 0 && !e.has(n) ? { text: t.text } : {}), d + P, F, (e, t) => {
			let r = n[e];
			return r?.kind === "text" ? sC(r, t) : 0;
		}), r = t();
		for (;;) {
			let i = [...r?.perSeg ?? []].filter(([e, t]) => {
				let r = n[e];
				return r?.kind === "text" && oC(r, t.text);
			});
			if (i.length === 0) break;
			for (let [t] of i) e.add(t);
			r = t();
		}
		r && (n = n.map((e, t) => {
			if (e.kind !== "text") return e;
			let n = r.perSeg.get(t);
			if (!n) return e;
			let i = e.basePaintOps[0];
			if (!i) throw Error("Kashida acquisition requires a contextual text paint operation");
			return {
				...e,
				nativeBaseDirection: void 0,
				nativeVisiblePrefix: void 0,
				measuredWidthPt: e.measuredWidthPt + n.advanceDeltaPx,
				basePaintOps: [{
					...i,
					text: n.text,
					sourceMapping: "kashida"
				}]
			};
		}), a += r.appliedPx, I = r.appliedPx, d = r.residualPx - P);
	}
	let L = yr(r, e.wordWrap !== !1) ? TT(n, SC) : 0, R = T.order.at(-1) ?? -1, z = 0;
	if (!r) {
		let e = n.findIndex((e) => e.kind !== "text" || /\S/.test(e.text));
		z = e < 0 ? 0 : e;
	}
	let ee = null, B = 0, V = 0, te = XS(n, r, e.wordWrap !== !1), H = !1;
	if (m === "character" && !(t.justifiedCompressionPt > 0)) {
		let t = d + L, i = $S(n, t, z, T.order, yr(r, e.wordWrap !== !1));
		B = i?.perGap ?? 0, ee = i?.perSeg ?? null, V = fx(i);
	} else if (t.justifiedCompressionPt !== void 0 && (t.justifiedCompressionPt > 0 || e.alignment !== "distribute" && e.alignment !== "lowKashida")) {
		let e = t.gapPlan;
		if (!e) throw Error("Justified line is missing its retained gap plan");
		let i = a;
		if (a = e.visibleWidthPx, d = u - l - a, h || t.justifiedCompressionPt > 0) {
			let o = h ? DC(n, d, D) : void 0, s = o?.takenPt ?? 0, c = t.justifiedCompressionPt > 0 && d < -t.justifiedCompressionPt - 1e-6 ? -t.justifiedCompressionPt : d, f = t.justifiedCompressionPt > 0 ? 0 : D, p = f > 0 ? e.gaps.filter((e) => e.segIndex >= f) : e.gaps, g = f > 0 ? e.expansionGaps.filter((e) => e.segIndex >= f) : e.expansionGaps, _ = cC(Se([], c - s, {
				gapModel: {
					gaps: p,
					state: f > 0 ? {
						...e.scan,
						naturalGapSum: p.reduce((e, t) => e + t.naturalPx, 0)
					} : {
						...e.scan,
						naturalGapSum: e.S
					}
				},
				proportional: !0,
				unweightedExpansion: {
					gaps: L > 0 ? CC(g, n) : g,
					slack: u - l - i + Math.min(L, e.lineEndSeparatorPx) - s
				}
			}), n);
			if (_?.usedUnweightedExpansion && (a = i, d = u - l - a), B = _?.perGap ?? 0, ee = OC(_?.perSeg ?? null, B, o), V = fx(_) + s, H = m === "word-or-centre" && V <= 0 && d > 0 && nC(n, te, r, z) && D === 0, t.justifiedCompressionPt > 0 && Math.abs(V + t.justifiedCompressionPt) > 1e-7) throw Error(`Justified fit and retained paint disagree: delta=${V}, C=${t.justifiedCompressionPt}, slack=${d}, visible=${e.visibleWidthPx}, end=${e.lineEndSeparatorPx}`);
		}
	} else if (h) {
		let i = d + L + P, a = DC(n, i, D), o = a?.takenPt ?? 0, s = i - o, c = cC(dx(te, s, Math.max(z, D), r ? R : n.length, -(t.baselinePt - t.topPt) * .25, s > 0 && !((t.endsWithBreak || e.isLastLine && e.endsAtHardBreak === !0) && !QS(e)) && !E, e.alignment === "thaiDistribute" && s > 0, e.thaiProportionalSpread === !0 && s > 0 && (t.endsWithBreak || !e.isLastLine) ? ZS(n, r) : void 0), n);
		B = c?.perGap ?? 0, ee = OC(c?.perSeg ?? null, B, a), V = fx(c) + o, H = m === "word-or-centre" && V <= 0 && s > 0 && nC(n, te, r, z) && D === 0;
	}
	let U = 0;
	if (O) {
		let e = V - d;
		U = N ? k.rightPt : Math.min(Math.max(0, e), k.rightPt);
		let t = N ? k.leftPt : Math.min(Math.max(0, e - U), k.leftPt), n = e - U - t;
		for (let { owner: e, widthPt: t } of k.interior) {
			if (!(n > 1e-9)) break;
			let r = Math.min(n, t), i = new Map(ee ?? []), a = i.get(e), o = a?.trailingGap ? a.trailingDelta ?? B : 0;
			i.set(e, {
				splitBefore: a?.splitBefore ?? [],
				internalStretch: a?.internalStretch ?? 0,
				...a?.gapDeltas ? { gapDeltas: a.gapDeltas } : {},
				trailingGap: !0,
				trailingDelta: o - r
			}), ee = i, V -= r, n -= r;
		}
	}
	let ne = t.availableWidthPt < e.availableWidthPt && !r ? TT(n, (e) => e.trimEnd().length) : L;
	if (V <= 0 && I <= 0 && !H) {
		let e = tC(n), t = n[e];
		if (t?.kind === "tab" && (t.alignedGapLimitPt ?? 0) > 0) {
			let r = Math.max(0, Math.min(t.alignedGapLimitPt, d + ne));
			r > 0 && (n = n.map((t, n) => n === e && t.kind === "tab" ? {
				...t,
				measuredWidthPt: t.measuredWidthPt + r
			} : t), a += r, d -= r);
		}
	}
	let re = a + V, ie = d - V + ne, ae = f === "right" ? ie : f === "center" || H ? ie / 2 : f === "justify" && e.baseRtl && (O || !h || V <= 0) ? ie + U : 0, oe = o + l, se = e.decimalAutoTabPt === void 0 ? ae : Math.max(0, e.paragraphXPt + e.decimalAutoTabPt - re - oe), W = oe + se;
	if (O && e.decimalAutoTabPt === void 0) {
		let e = oe + u - l, t = k.leftPt + k.rightPt, n = W + re - k.rightPt - e, r = oe - (W + k.leftPt);
		n > 1e-9 && n <= t + 1e-9 && r + n <= 1e-9 ? W -= n : r > 1e-9 && r <= t + 1e-9 && n + r <= 1e-9 && (W += r);
	}
	let ce = [], le = /* @__PURE__ */ new Map();
	for (let r of T.order) {
		let i = n[r];
		if (!i) continue;
		let a = ee?.get(r), o = a?.trailingGap ? a.trailingDelta ?? B : 0, s = w?.spaceOnly[r] && o > 0 ? o : 0, c = s > 0 && a ? {
			...a,
			trailingGap: !1,
			trailingDelta: 0
		} : a, l = c?.internalStretch ?? 0, u = YS(i) + l + s;
		if (i.kind === "tab") {
			let e = {
				xPt: W,
				yPt: t.topPt,
				widthPt: i.measuredWidthPt,
				heightPt: t.advancePt
			}, n = i.underline ? Ux({
				origin: {
					xPt: W,
					yPt: t.baselinePt
				},
				advancePt: i.measuredWidthPt,
				base: i.underline.base,
				color: i.underline.color,
				underline: i.underline,
				...i.underline.fontRule ? { fontRule: i.underline.fontRule } : {}
			}) : void 0;
			ce.push({
				kind: "tab",
				range: i.range,
				bounds: e,
				advancePt: i.measuredWidthPt,
				leader: i.leader,
				...n?.length ? { decorations: n } : {},
				...i.leader === "none" ? {} : i.leaderShape ? { leaderGlyphs: Ix({
					interval: e,
					baselinePt: t.baselinePt,
					...i.leaderShape
				}) } : {}
			});
		} else if (i.kind === "resource") ce.push({
			kind: "resource",
			range: i.range,
			...i.sourceRunIndex === void 0 ? {} : { sourceRunIndex: i.sourceRunIndex },
			resourceKey: i.resourceKey,
			resourceKind: i.resourceKind,
			...i.orientation ? { orientation: i.orientation } : {},
			bounds: {
				xPt: W + (i.leftOffsetPt ?? 0),
				yPt: t.baselinePt + i.topOffsetPt,
				widthPt: i.widthPt,
				heightPt: i.heightPt
			},
			advancePt: i.measuredWidthPt
		});
		else if (i.kind === "unavailable-resource" || i.kind === "inline-drawing") ce.push({
			kind: "drawing",
			range: i.range,
			drawingId: i.drawingId,
			bounds: {
				xPt: W + (i.leftOffsetPt ?? 0),
				yPt: t.baselinePt + i.topOffsetPt,
				widthPt: i.widthPt,
				heightPt: i.heightPt
			},
			advancePt: i.measuredWidthPt
		});
		else if (i.kind === "anchor-host") ce.push({
			kind: "anchor-host",
			range: i.range,
			bounds: {
				xPt: W,
				yPt: t.topPt,
				widthPt: 0,
				heightPt: t.advancePt
			},
			baselinePt: t.baselinePt,
			...i.sourceMetrics ? { sourceMetrics: i.sourceMetrics } : {},
			...i.anchorOccurrenceId ? { anchorOccurrenceId: i.anchorOccurrenceId } : {},
			...i.noteReference ? { noteReference: i.noteReference } : {}
		});
		else {
			let { measuredWidthPt: n, characterGridDeltaPt: a, breakBefore: o, rtl: l, digitsAsAN: d, fixedPitch: f, listLabel: p, decorationTerminalAdvancePt: m, textLayoutService: h, textShapeRequest: g, autoSpace: _, leadingSeamPairPt: v, selectedFaceFontBox: y, retainedGeometry: b, direction: x, nativeBaseDirection: S, nativeVisiblePrefix: C, ...E } = i, D = lC(i, c, B), O = s > 0 ? {
				...D,
				clusters: [{
					...D.clusters[0],
					advancePt: D.clusters[0].advancePt + s
				}]
			} : D, k = !w?.spaceOnly[r] && i.nativeBaseDirection !== void 0 ? i.nativeBaseDirection : T.rtl[r] ? "rtl" : "ltr", A = i.text.trimEnd().length, j = k === "rtl" && !w?.spaceOnly[r] ? (E.fitText?.trailingPadPt ?? 0) + O.clusters.filter((e) => e.range.start >= i.range.start + A).reduce((e, t) => e + t.advancePt, 0) : 0, M = ((O.paintOps[0]?.writingMode ?? "horizontal-tb") === "horizontal-tb" ? hC : gC)(O.paintOps.map((e) => ({
				...e,
				direction: k
			})), O.clusters, i.text, i.range.start, k, i.range.start + A), N = k === "rtl" ? uC(M, O.clusters) : M, P = c?.trailingGap ? c.trailingDelta ?? B : 0, F = {
				xPt: W + j,
				yPt: t.baselinePt
			}, I = O.paintOps[0]?.offset.yPt ?? 0, L = {
				xPt: W,
				yPt: t.baselinePt + I
			}, R = b ? Ux({
				origin: L,
				advancePt: u + P,
				base: b.base,
				color: sw(E.color),
				...b.underline ? { underline: b.underline } : {},
				...b.strike ? { strike: b.strike } : {},
				...b.fontRule ? { fontRule: b.fontRule } : {}
			}) : E.decorations, z = b?.emphasis ? {
				authored: b.emphasis.authored,
				glyphs: Wx({
					authored: b.emphasis.authored,
					glyph: b.emphasis.glyph,
					origin: {
						xPt: F.xPt,
						yPt: t.baselinePt + I
					},
					clusters: O.clusters,
					clusterInk: b.emphasis.clusterInk,
					mark: b.emphasis.mark,
					scaleX: i.basePaintOps[0]?.scaleX ?? 1
				})
			} : void 0, ee = y ?? b?.base, V = ee ? {
				xPt: W,
				yPt: t.baselinePt + I - ee.ascentPt,
				widthPt: u + P,
				heightPt: ee.ascentPt + ee.descentPt
			} : {
				xPt: W,
				yPt: t.topPt,
				widthPt: u + P,
				heightPt: t.advancePt
			}, te = {
				...E,
				kind: "text",
				origin: F,
				bounds: {
					xPt: W,
					yPt: t.topPt,
					widthPt: u,
					heightPt: t.advancePt
				},
				highlightBounds: V,
				advancePt: u,
				clusters: O.clusters,
				paintOps: N,
				decorations: R,
				...z ? { emphasis: z } : {},
				direction: k,
				...P === 0 ? {} : { ownedTrailingSlackPt: P },
				...E.highlight || E.background ? { highlightFragments: [{
					rect: E.highlight || !e.exactLineSpacing ? V : {
						xPt: W,
						yPt: t.topPt,
						widthPt: u + P,
						heightPt: t.advancePt
					},
					color: E.highlight ?? E.background
				}] } : {},
				...E.ruby ? { ruby: {
					...E.ruby,
					paintOps: E.ruby.paintOps.map((e) => ({
						...e,
						origin: {
							xPt: e.origin.xPt + W + (u - i.measuredWidthPt) / 2,
							yPt: e.origin.yPt + t.baselinePt
						}
					}))
				} } : {}
			}, H = m === void 0 ? 0 : Math.max(0, u + P - m);
			k === "ltr" && H > 0 && le.set(ce.length, H), ce.push(te);
		}
		W += u, c?.trailingGap && (W += c.trailingDelta ?? B);
	}
	let ue = n.some((e) => e.kind === "text" && e.decorationTerminalAdvancePt !== void 0);
	if (L > 0) {
		let t = o + s;
		for (let n = ce.length - 1; n >= 0; --n) {
			let r = ce[n];
			if (r?.kind === "anchor-host") continue;
			if (r?.kind !== "text") break;
			let i = SC(r.text);
			if (ce[n] = e.ulTrailSpace === !0 ? TC(r, t) : wC(r, i, ue), i > 0) break;
		}
	}
	for (let [t, n] of le) {
		let r = ce[t];
		if (r?.kind !== "text" || !r.decorations || e.ulTrailSpace === !0 && r.text.trimEnd().length < r.text.length) continue;
		let i = ce[t + 1], a = r.decorations.map((e) => e.kind === "underline" ? (i?.kind === "text" || i?.kind === "tab") && i.decorations?.some((t) => yC(e, t)) ? e : xC(e, n) : e);
		ce[t] = {
			...r,
			decorations: a
		};
	}
	for (let e = 0; e < ce.length;) {
		let t = ce[e];
		if (t?.kind !== "text" || !t.runBorder) {
			e += 1;
			continue;
		}
		let n = e + 1;
		for (; n < ce.length;) {
			let e = ce[n];
			if (e?.kind !== "text" || !e.runBorder) break;
			n += 1;
		}
		let r = Kx(ce.slice(e, n).map((e) => ({
			bounds: e.bounds,
			trailingSlackPt: e.ownedTrailingSlackPt ?? 0,
			border: e.runBorder
		})));
		ce[e] = {
			...t,
			runBorderFragments: r
		}, e = n;
	}
	return EC(ce), fv({
		range: t.range,
		bounds: {
			xPt: oe + se,
			yPt: t.topPt,
			widthPt: re,
			heightPt: t.advancePt
		},
		baselinePt: t.baselinePt,
		advancePt: t.advancePt,
		placements: ce
	});
}
function AC(e, t) {
	let n = t[0];
	return n && t.every((e) => uv(e)) ? pv(e, n) : fv(e);
}
function jC(e, t) {
	let n = [];
	for (let r = 0; r < e.length;) {
		let i = e[r], a = r + 1;
		for (; a < e.length && t[a] === t[r];) a += 1;
		if (a === r + 1) n.push(i);
		else {
			let t = e.slice(r, a), { wrapBounds: o, ...s } = i;
			n.push(AC({
				...s,
				...i.gridAfterLeadingPt === void 0 ? {} : { gridAfterLeadingPt: t.reduce((e, t) => Math.min(e, t.gridAfterLeadingPt ?? 0), i.gridAfterLeadingPt) },
				range: {
					start: i.range.start,
					end: t.at(-1).range.end
				},
				bounds: wb(t.map((e) => e.bounds)),
				placements: t.flatMap((e) => e.placements),
				wrapFragments: t.flatMap((e) => e.wrapFragments ?? [e.wrapBounds ?? e.bounds])
			}, t));
		}
		r = a;
	}
	return n;
}
function MC(e) {
	let t = e.continuation, n = t?.lineStart ?? 0, r = t?.lineEnd ?? e.lines.length;
	if (n < 0 || r < n || r > e.lines.length) throw RangeError("Paragraph continuation line range is outside the retained lines");
	let i = t?.continuesFromPrevious ? 0 : e.spacing.beforePt, a = i;
	for (let t = n; t < r; t += 1) a += NC(e, t, n, i);
	return e.lines.length === 0 && e.paragraphMark && (a += KS(e.paragraphMark.bounds.heightPt, "paragraphMark.heightPt")), t?.continuesOnNext || (a += e.spacing.afterPt), a;
}
function NC(e, t, n, r) {
	let i = e.lines[t];
	if (!i) return 0;
	let a = 0;
	if (t === 0) a += Math.max(0, i.bounds.yPt - (e.flowBounds.yPt + r));
	else if (t > n) {
		let n = e.lines[t - 1];
		a += Math.max(0, i.bounds.yPt - ((n?.bounds.yPt ?? i.bounds.yPt) + (n?.advancePt ?? 0)));
	}
	return a + KS(i.advancePt, "line.advancePt");
}
function PC(e, t) {
	let n = t ? 0 : e.spacing.beforePt, r = [n];
	for (let t = 0; t < e.lines.length; t += 1) r.push(r[t] + NC(e, t, 0, n));
	return r;
}
function FC(e, t) {
	return IC(e, t);
}
function IC(e, t, n) {
	let r = e.continuation?.lineStart ?? 0, i = e.continuation?.lineEnd ?? e.lines.length, a = n ?? e.lines.slice(r, i), o = e.continuation ? MC(e) : KS(e.flowBounds.heightPt, "flowBounds.heightPt"), s = {
		kind: "paragraph",
		id: e.id,
		source: e.source,
		...e.paragraphId === void 0 ? {} : { paragraphId: e.paragraphId },
		flowDomainId: e.flowDomainId,
		ordinaryFlow: e.ordinaryFlow,
		...e.styleId === void 0 ? {} : { styleId: e.styleId },
		...e.bookmarkStarts?.length ? { bookmarkStarts: e.bookmarkStarts } : {},
		flowBounds: {
			...e.flowBounds,
			heightPt: o
		},
		inkBounds: e.inkBounds,
		...e.clipBounds ? { clipBounds: e.clipBounds } : {},
		advancePt: o,
		spacing: e.spacing,
		contextualSpacing: e.contextualSpacing ?? !1,
		lines: a,
		borders: e.borders,
		...e.shading ? { shading: e.shading } : {},
		resources: e.resources,
		drawings: e.drawings,
		textBoxes: e.textBoxes,
		events: e.events,
		exclusions: e.exclusions,
		...e.cellContainmentBounds ? { cellContainmentBounds: e.cellContainmentBounds } : {},
		...e.anchorCollisions?.length ? { anchorCollisions: e.anchorCollisions } : {},
		...e.anchorFrames ? { anchorFrames: e.anchorFrames } : {},
		...e.paragraphMark ? { paragraphMark: e.paragraphMark } : {},
		...e.continuation ? { continuation: e.continuation } : {}
	};
	return t ? (e.continuation && fv(e.continuation), pv(s, t)) : fv(s);
}
function LC(e, t) {
	return {
		...e,
		path: [...e.path, t]
	};
}
function RC(e, t) {
	let n = e.diagnostics ?? [];
	if (n.length === 0) return Object.freeze([]);
	let r = Object.freeze({
		...t,
		path: Object.freeze([...t.path])
	});
	return Object.freeze(n.map((e) => Object.freeze({
		...e,
		source: r
	})));
}
function zC(e) {
	return ke(e);
}
function BC(e, t) {
	return Oe("unavailable-drawing", LC(e, t));
}
function VC(e, t) {
	return Object.freeze({
		code: "MISSING_RESOURCE",
		severity: "warning",
		source: Object.freeze({
			...t,
			path: Object.freeze([...t.path])
		}),
		message: `Drawing ${e} resource is unavailable`
	});
}
function HC(e) {
	return OS(e) || (/^date$/i.test(e.fieldType) ? "date" : /^time$/i.test(e.fieldType) ? "time" : "document");
}
function UC(e) {
	return e.sourceRunIndex;
}
function WC(e) {
	if (!e.textLayoutService || !e.textShapeRequest) return;
	let t = e.metricOnly && e.metricProbeText ? e.textLayoutService.shape({
		...As(e.textShapeRequest, e.metricProbeText),
		fontSizePt: e.smallCaps && !e.vertAlign ? e.fontSize : q(e, 1),
		measure: !0,
		clusterGeometry: !1
	}) : e.textLayoutService.shape({
		...e.textShapeRequest,
		measure: !0
	});
	return {
		ascentPt: t.ascentPt,
		descentPt: t.descentPt
	};
}
var GC = Object.freeze({
	yellow: "#FFFF00",
	cyan: "#00FFFF",
	green: "#00FF00",
	magenta: "#FF00FF",
	blue: "#0000FF",
	red: "#FF0000",
	darkBlue: "#000080",
	darkCyan: "#008080",
	darkGreen: "#008000",
	darkMagenta: "#800080",
	darkRed: "#800000",
	darkYellow: "#808000",
	darkGray: "#808080",
	lightGray: "#C0C0C0",
	black: "#000000",
	white: "#FFFFFF"
});
function KC(t) {
	return t.startsWith("#") ? t : e(GC, t) ?? "#FFFF00";
}
function qC(e) {
	let t = Yr(e.vertAlign, e.fontSize) + (e.lineRelativePosition ?? e.position ?? 0);
	return t === 0 ? 0 : -t;
}
function JC(e, t, n, r, i, a, o) {
	let s = UC(e), l = s === void 0 ? void 0 : t.runs[s], u = qS(l);
	if (e.metricOnly) {
		let t = WC(e);
		return {
			kind: "anchor-host",
			...l?.type === "text" && (l.noteRef?.kind === "footnote" || l.noteRef?.kind === "endnote") ? { noteReference: {
				kind: l.noteRef.kind,
				id: l.noteRef.id
			} } : {},
			range: {
				start: n,
				end: n
			},
			bounds: {
				xPt: r,
				yPt: a,
				widthPt: 0,
				heightPt: o
			},
			baselinePt: i,
			...t ? { sourceMetrics: t } : {}
		};
	}
	let d = e.color ? {
		kind: "explicit",
		color: `#${e.color}`
	} : e.colorAuto ? {
		kind: "auto",
		...e.background ? { background: `#${e.background}` } : {}
	} : { kind: "default" }, f = e.fontRoute ?? Fe(e.fontFamily ? c(e.fontFamily) : "sans-serif", e.fontFamily ? "native" : "generic"), p = e.ruby && e.textLayoutService && e.textShapeRequest ? e.textLayoutService.shape({
		...e.textShapeRequest,
		measure: !0
	}) : void 0, m = e.ruby && e.textLayoutService && e.textShapeRequest ? e.textLayoutService.shape({
		...As(e.textShapeRequest, e.ruby.text),
		fontSizePt: e.ruby.fontSizePt,
		measure: !0
	}) : void 0, h = e.ruby && m ? (() => {
		let t = e.ruby, n = /* @__PURE__ */ new Set();
		return (m.clusters ?? []).flatMap((e) => {
			let r = m.spans.find((t) => t.start <= e.range.start && t.end >= e.range.end) ?? m.spans[0];
			if (!r) throw Error("Ruby shaping produced no selected-face span");
			let i = lr(r.text);
			return i && n.has(r) ? [] : (i && n.add(r), [{
				text: i ? t.text.slice(r.start, r.end) : t.text.slice(e.range.start, e.range.end),
				offsetPt: e.offsetPt,
				fontRoute: r.fontRoute,
				fontSizePt: t.fontSizePt,
				fontWeight: r.font.weight,
				fontStyle: r.font.style,
				color: d,
				...i ? { kerning: "normal" } : {}
			}]);
		});
	})() : [], g = u?.ruby?.raisePt.status === "valid" ? u.ruby.raisePt.value ?? void 0 : e.ruby?.hpsRaisePt, _ = e.ruby && m ? Lx({
		baseOrigin: {
			xPt: 0,
			yPt: 0
		},
		baseAdvancePt: e.measuredWidth,
		guideAdvancePt: m.advancePt,
		...g === void 0 ? {} : { raisePt: g },
		...p?.inkBounds && m.inkBounds ? {
			baseInkTopPt: -p.inkBounds.ascentPt,
			guideInkBottomFromBaselinePt: m.inkBounds.descentPt
		} : {},
		spans: h
	}) : [], v = qC(e), y = n + pw(e);
	return {
		kind: "text",
		text: e.text,
		...e.optionalHyphenGlyph ? { optionalHyphenGlyph: !0 } : {},
		...e.semanticSlotSpans ? { semanticSlotSpans: e.semanticSlotRange ? Ds(e.semanticSlotSpans, e.semanticSlotRange.start, e.semanticSlotRange.end) : e.semanticSlotSpans } : {},
		...s === void 0 ? {} : { sourceRunIndex: s },
		...l?.type === "field" ? {
			role: "field-result",
			dependency: HC(l)
		} : {},
		...l?.type === "text" && (l.noteRef?.kind === "footnote" || l.noteRef?.kind === "endnote") ? { noteReference: {
			kind: l.noteRef.kind,
			id: l.noteRef.id
		} } : {},
		range: {
			start: n,
			end: y
		},
		origin: {
			xPt: r,
			yPt: i + v
		},
		bounds: {
			xPt: r,
			yPt: a,
			widthPt: e.measuredWidth,
			heightPt: o
		},
		advancePt: e.measuredWidth,
		clusters: [{
			range: {
				start: n,
				end: y
			},
			offset: {
				xPt: 0,
				yPt: 0
			},
			advancePt: e.measuredWidth
		}],
		color: d,
		fontRoute: f,
		fontSizePt: q(e, 1),
		fontWeight: e.bold ? 700 : 400,
		fontStyle: e.italic ? "italic" : "normal",
		direction: e.rtl ? "rtl" : "ltr",
		...e.verticalRun ? { writingMode: "vertical-rl" } : {},
		...e.charSpacing === void 0 ? {} : { characterSpacingPt: e.charSpacing },
		...e.charScale === void 0 ? {} : { characterScale: e.charScale },
		...e.fitTextRegionIndex === void 0 ? {} : { fitText: {
			regionIndex: e.fitTextRegionIndex,
			perGapPt: e.fitTextPerGapPx ?? 0,
			trailingPadPt: e.fitTextTrailingPadPx ?? 0
		} },
		kerning: (e.textShapeRequest?.kerning ?? cr(e.fontSize, e.kerning)) || lr(e.text),
		...e.position === void 0 ? {} : { positionPt: e.position },
		...e.vertAlign ? { verticalAlign: e.vertAlign } : {},
		...e.tateChuYoko ? { tateChuYoko: !0 } : {},
		...e.tateChuYokoCompress ? { tateChuYokoCompress: !0 } : {},
		...e.ruby && m ? { ruby: {
			text: e.ruby.text,
			advancePt: m.advancePt,
			authored: {
				...u?.ruby?.align.status === "valid" && u.ruby.align.value ? { align: u.ruby.align.value } : {},
				...u?.ruby?.baseFontSizePt.status === "valid" && u.ruby.baseFontSizePt.value !== null ? { baseFontSizePt: u.ruby.baseFontSizePt.value } : {},
				...g === void 0 ? {} : { raisePt: g },
				...u?.ruby?.language.status === "valid" && u.ruby.language.value ? { language: u.ruby.language.value } : {}
			},
			paintOps: _
		} } : {},
		...e.emphasisMark ? { emphasisMark: e.emphasisMark } : {},
		...e.highlight ? { highlight: KC(e.highlight) } : {},
		...e.background ? { background: `#${e.background}` } : {},
		...e.border ? { runBorder: {
			val: u?.border?.val.value ?? e.border.style,
			color: e.border.color ? `#${e.border.color}` : "#000000",
			widthPt: e.border.width,
			spacePt: e.border.space ?? 0,
			...u?.border?.themeColor.value ? { themeColor: u.border.themeColor.value } : {},
			...u?.border?.themeTint.value ? { themeTint: u.border.themeTint.value } : {},
			...u?.border?.themeShade.value ? { themeShade: u.border.themeShade.value } : {},
			...u?.border?.shadow.status === "valid" && u.border.shadow.value !== null ? { shadow: u.border.shadow.value } : {},
			...u?.border?.frame.status === "valid" && u.border.frame.value !== null ? { frame: u.border.frame.value } : {}
		} } : {},
		...e.revision ? { revision: e.revision } : {},
		typography: {
			caps: u?.caps ?? !1,
			smallCaps: u?.smallCaps ?? e.smallCaps === !0,
			strike: u?.strike ?? e.strikethrough,
			doubleStrike: u?.doubleStrike ?? e.doubleStrikethrough === !0,
			verticalAlign: u?.verticalAlign ?? {
				status: e.vertAlign ? "valid" : "missing",
				raw: e.vertAlign ?? null,
				value: e.vertAlign ?? null
			},
			positionPt: u?.positionPt ?? {
				status: e.position === void 0 ? "missing" : "valid",
				raw: e.position === void 0 ? null : String(e.position * 2),
				value: e.position ?? null
			},
			emphasis: u?.emphasis ?? {
				status: e.emphasisMark ? "valid" : "missing",
				raw: e.emphasisMark ?? null,
				value: e.emphasisMark ?? null
			},
			...u?.underline ? { underline: u.underline } : {}
		},
		decorations: [],
		paintOps: [{
			text: e.text,
			range: {
				start: n,
				end: y
			},
			offset: {
				xPt: 0,
				yPt: v
			},
			letterSpacingPt: Vc(e),
			scaleX: e.charScale ?? 1,
			direction: e.rtl ? "rtl" : "ltr",
			kerning: (e.textShapeRequest?.kerning ?? cr(e.fontSize, e.kerning)) || lr(e.text) ? "normal" : "none",
			writingMode: e.verticalRun ? "vertical-rl" : "horizontal-tb"
		}],
		...e.hyperlink ? { hyperlink: e.hyperlink } : {}
	};
}
function YC(e) {
	return e.hasRuby === !0 && e.segments.every((e) => !("ruby" in e) || !e.ruby || e.ruby.hpsRaisePt != null);
}
function XC(e, t, n = !1) {
	let r = e.layout, i = r.visibleAscent ?? r.ascent;
	if (n && !t.lineGrid.active && (!t.lineSpacing || t.lineSpacing.rule === "auto" && t.lineSpacing.value >= 1)) return e.topYPt + i;
	let a = i + (r.visibleDescent ?? r.descent), o = t.lineSpacing?.rule === "auto" && (!t.hasRuby || YC(r)) && !t.lineGrid.active, s = o && (t.lineSpacing?.value ?? 1) < 1, c = o && !s ? Math.max(a, r.visibleIntendedSingle ?? r.intendedSingle) : e.advancePt;
	return e.topYPt + (c - a) / 2 + i;
}
function ZC(e, t, n) {
	let r = e.numbering;
	if (!r) return;
	if (t.numberingMarkerGeometry) return t.numberingMarkerGeometry;
	let i = e.numberingMarkerShapeInput, a = n.environment.layoutServices?.text;
	if (!(!i || !a)) return xg(r, i, {
		authoredFirstIndentPt: e.indentFirst,
		physicalIndentLeftPt: t.physicalIndentLeftPt,
		tabStops: e.tabStops,
		defaultTabPt: t.defaultTabPt,
		...n.environment.compat ? { compat: n.environment.compat } : {},
		baseRtl: t.baseRtl
	}, a);
}
function QC(e) {
	return e.source.story === "body" && e.source.storyInstance === "body" && e.source.path.length === 1 && e.ordinaryFlow && e.anchorCellBounds === void 0;
}
function $C(e) {
	return e.source.story === "body" && e.source.storyInstance === "body" && e.source.path.length === 1 && e.ordinaryFlow && e.anchorCellBounds === void 0 && !e.context.runDirectionUnauthored && !e.context.lineGrid.active && !e.context.characterGrid.active;
}
function ew(e, t, n, r) {
	let i = e.numbering, a = e.numberingMarkerShapeInput, o = n.environment.layoutServices?.text, s = !t.baseRtl || (i?.suff || "tab") === "tab" && e.indentFirst < 0;
	if (!i || !a || !o || !s || i.text === "" && i.picBulletImagePath == null) return;
	let c = r && !t.hasEastAsianText && $C(n) && !t.baseRtl && !n.environment.verticalCJK && !n.environment.verticalPageFrame && Zl(n.environment).numberedWindowFrame && (e.alignment == null || e.alignment === "left" || e.alignment === "start") && (i.jc == null || i.jc === "left") && (i.suff || "tab") === "tab" && !i.picBulletImagePath && e.indentFirst <= 0 && t.physicalIndentLeftPt + e.indentFirst >= 0 && e.tabStops.every((e) => e.alignment === "left") && e.runs.some((e) => e.type === "text" && e.text.trim().length > 0);
	return {
		authoredFirstIndentPx: e.indentFirst,
		...c ? { columnOriginInsetPx: t.physicalIndentLeftPt } : {},
		bodyIndentAt: (r) => xg(i, a, {
			authoredFirstIndentPt: r,
			...c ? { suffixFrameOriginPt: r - e.indentFirst } : {},
			physicalIndentLeftPt: t.baseRtl ? t.physicalIndentRightPt : t.physicalIndentLeftPt,
			tabStops: e.tabStops,
			defaultTabPt: t.defaultTabPt,
			...n.environment.compat ? { compat: n.environment.compat } : {},
			baseRtl: t.baseRtl
		}, o).bodyOffsetPt
	};
}
function tw(e, t, n, r, i, a) {
	if (a) {
		let e = a.leadingEdgePx - a.authoredFirstIndentPt;
		return t.baseRtl ? n + r - e : n + e;
	}
	return i.bounds.widthPt <= 0 ? t.baseRtl ? n + r : n : t.baseRtl ? i.bounds.xPt + i.bounds.widthPt + e.bodyOffsetPt : i.bounds.xPt - e.bodyOffsetPt;
}
function nw(e, t, n, r, i, a, o) {
	if (!e.shape || e.markerText === "") return [];
	let s = e.shape, c = _g({
		baseRtl: n.baseRtl,
		alignedLeadingEdgePt: tw(e, n, r, i, a, o === void 0 ? void 0 : {
			leadingEdgePx: o,
			authoredFirstIndentPt: t.indentFirst
		}),
		authoredFirstIndentPt: t.indentFirst,
		markerShiftPt: e.markerShiftPt,
		markerWidthPt: e.markerWidthPt
	}), l = -e.markerText.length, u = t.numbering?.color ? {
		kind: "explicit",
		color: `#${t.numbering.color}`
	} : t.numbering?.colorAuto ? { kind: "auto" } : t.paragraphMarkColor ? {
		kind: "explicit",
		color: `#${t.paragraphMarkColor}`
	} : { kind: "default" }, d = 0;
	return s.spans.map((e) => {
		let r = d;
		d += e.advancePt;
		let i = s.clusters ? s.clusters.filter((t) => t.range.start >= e.start && t.range.end <= e.end).map((e) => ({
			range: {
				start: l + e.range.start,
				end: l + e.range.end
			},
			offset: {
				xPt: e.offsetPt - r,
				yPt: 0
			},
			advancePt: e.advancePt
		})) : [{
			range: {
				start: l + e.start,
				end: l + e.end
			},
			offset: {
				xPt: 0,
				yPt: 0
			},
			advancePt: e.advancePt
		}], o = c + r;
		return {
			kind: "text",
			role: "numbering-marker",
			text: e.text,
			range: {
				start: l + e.start,
				end: l + e.end
			},
			origin: {
				xPt: o,
				yPt: a.baselinePt
			},
			bounds: {
				xPt: o,
				yPt: a.baselinePt - e.ascentPt,
				widthPt: e.advancePt,
				heightPt: e.ascentPt + e.descentPt
			},
			advancePt: e.advancePt,
			clusters: i,
			paintOps: [{
				text: e.text,
				range: {
					start: l + e.start,
					end: l + e.end
				},
				offset: {
					xPt: 0,
					yPt: 0
				},
				letterSpacingPt: 0,
				scaleX: 1,
				direction: n.baseRtl ? "rtl" : "ltr",
				kerning: t.numberingMarkerShapeInput?.kerning || lr(e.text) ? "normal" : "none",
				writingMode: "horizontal-tb"
			}],
			color: u,
			fontRoute: e.fontRoute,
			fontSizePt: t.numberingMarkerShapeInput?.fontSizePt ?? e.ascentPt + e.descentPt,
			fontWeight: e.font.weight,
			fontStyle: e.font.style,
			direction: n.baseRtl ? "rtl" : "ltr",
			decorations: []
		};
	});
}
function rw(e) {
	if (e) return e.startsWith("#") ? e : `#${e}`;
}
function iw(e, t, n) {
	let r = rw(t), i = rw(n);
	return e.map((e) => {
		let t = !1, n = e.placements.map((e) => {
			if (e.kind !== "text") return e;
			let n = e.background ?? r ?? i;
			return !n || e.color.kind === "explicit" ? e : (t = !0, {
				...e,
				color: {
					kind: "auto",
					background: n
				}
			});
		});
		return t ? AC({
			...e,
			placements: n
		}, [e]) : e;
	});
}
function aw(e) {
	return e != null && e.style !== "none";
}
function ow(e, t, n, r, i, a, o) {
	let s = n, c = n + r;
	e.indentFirst < 0 && (e.bidi ? c -= e.indentFirst : s += e.indentFirst);
	for (let e of t.flatMap((e) => e.placements)) !(e.kind === "text" && e.role === "numbering-marker" || e.kind === "resource" && e.resourceKind === "picture-bullet") || !e.bounds || (s = Math.min(s, e.bounds.xPt), c = Math.max(c, e.bounds.xPt + e.bounds.widthPt));
	let l = e.borders, u = o.top === "none" ? null : l?.[o.top] ?? null, d = o.bottom === "none" ? null : l?.bottom ?? null, f = aw(l?.left ?? null) ? l.left.space ?? 0 : 0, p = aw(l?.right ?? null) ? l.right.space ?? 0 : 0, m = aw(u) ? u.space ?? 0 : 0, h = aw(d) ? d.space ?? 0 : 0;
	return {
		xPt: s - f,
		yPt: i - m,
		widthPt: c - s + f + p,
		heightPt: a + m + h
	};
}
function sw(e) {
	return e.kind === "explicit" ? e.color : e.kind === "auto" ? he(e.background ?? "#FFFFFF") : "#000000";
}
function cw(e) {
	return e.inkBounds ?? {
		xMinPt: 0,
		xMaxPt: e.advancePt,
		ascentPt: e.ascentPt,
		descentPt: e.descentPt
	};
}
function lw(e) {
	return e === "circle" ? "○" : e === "comma" ? "﹅" : "•";
}
function uw(e, t, n) {
	let r = e.trackChangesMarkup, i = ux(r?.kind);
	if (!(e.highlight || e.underline || e.strikethrough || e.doubleStrikethrough || e.emphasisMark || i.underline || i.strike)) return;
	let a = e.textLayoutService, o = e.textShapeRequest;
	if (!a || !o) throw Error("Retained typography geometry requires TextLayoutService");
	let s = (e) => a.shape({
		...As(o, e),
		measure: !0
	}), c = (e) => {
		let t = s(e), n = t.spans[0];
		if (!n || t.spans.length !== 1 || n.start !== 0 || n.end !== e.length) throw Error("Retained decoration probe requires one selected-face span");
		return {
			ascentPt: n.ascentPt,
			descentPt: n.descentPt,
			...n.inkBounds ? { inkBounds: n.inkBounds } : {}
		};
	}, l = e.selectedFaceFontBox;
	if (!l || !e.selectedFaceInkBounds) throw Error("Retained typography geometry requires authoritative selected-face metrics");
	let u = {
		ascentPt: l.ascentPt,
		descentPt: l.descentPt,
		inkBounds: e.selectedFaceInkBounds
	}, d = sw(n), f = e.underline ? {
		...e.underlineStyle ? { authoredStyle: e.underlineStyle } : {},
		color: e.underlineColor && e.underlineColor !== "auto" ? `#${e.underlineColor}` : d,
		probe: c("_")
	} : r && i.underline ? {
		color: r.authorColor,
		probe: c("_")
	} : void 0, p = e.strikethrough || e.doubleStrikethrough ? {
		double: e.doubleStrikethrough === !0,
		probe: c("-"),
		...e.doubleStrikethrough ? { doubleProbe: c("=") } : {}
	} : r && i.strike ? {
		double: !1,
		probe: c("-"),
		color: r.authorColor
	} : void 0, m = e.emphasisMark ? (() => {
		let r = lw(e.emphasisMark), i = s(r), c = i.spans[0];
		if (!c) throw Error("Emphasis shaping produced no selected-face span");
		let l = (e.shapedClusters ?? []).map((n) => ({
			text: e.text.slice(n.range.start, n.range.end),
			range: {
				start: t + n.range.start,
				end: t + n.range.end
			},
			ink: cw(a.shape({
				...ks(o, n.range.start, n.range.end),
				measure: !0
			}))
		}));
		return {
			authored: e.emphasisMark,
			glyph: r,
			mark: {
				inkBounds: cw(i),
				fontRoute: c.fontRoute,
				fontSizePt: o.fontSizePt,
				fontWeight: c.font.weight,
				fontStyle: c.font.style,
				color: n
			},
			clusterInk: l
		};
	})() : void 0, h = (f || p) && e.referenceFontDecoration && s("_").spans[0]?.font.requestedFamily === e.authoredFontFamily ? {
		geometry: e.referenceFontDecoration,
		sizePt: o.fontSizePt
	} : void 0;
	return {
		base: u,
		...h ? { fontRule: h } : {},
		...f ? { underline: f } : {},
		...p ? { strike: p } : {},
		...m ? { emphasis: m } : {}
	};
}
function dw(e, t, n, r, i, a, o) {
	if (e.metricOnly) {
		let t = WC(e);
		return {
			kind: "anchor-host",
			measuredWidthPt: 0,
			...i?.type === "text" && (i.noteRef?.kind === "footnote" || i.noteRef?.kind === "endnote") ? { noteReference: {
				kind: i.noteRef.kind,
				id: i.noteRef.id
			} } : {},
			range: {
				start: n,
				end: n
			},
			...t ? { sourceMetrics: t } : {},
			...i?.type === "anchorHost" && i.anchorOccurrenceId ? { anchorOccurrenceId: i.anchorOccurrenceId } : {}
		};
	}
	let s = {
		...JC(e, t, n, 0, 0, 0, 0),
		...o ? { sourceRuns: o } : {}
	};
	if (s.kind !== "text") throw Error("Visible text segment projected as anchor host");
	let c = rl(e, r, 1), l = e.fitTextPerGapPx ?? zc(e, r, 1), u = e.fitTextPerGapPx === void 0 ? Bc(e, 1) : 0, d = e.charScale ?? 1, f = qC(e), p = Nc(e);
	if (jc(e) && e.textShapeRequest?.baseDirection === "rtl" && e.text.endsWith(" ") && !p) throw TypeError("Selected native RTL suffix lost its visible-prefix authority");
	let m = uw(e, n, s.color), h = e.shapedClusters, g = h?.length && h[0]?.range.start === 0 && h.at(-1)?.range.end === e.text.length && h.every((e, t) => t === 0 || h[t - 1]?.range.end === e.range.start) && h.every((e) => e.range.start < e.range.end && Number.isFinite(e.offsetPt) && Number.isFinite(e.advancePt)) ? h : void 0;
	if (e.text.length > 0 && !g) throw Error("Visible text acquisition requires complete authoritative grapheme clusters from TextLayoutService");
	let _ = 0, v = 0, y = (g ?? []).map((t, i) => {
		let a = e.text.slice(0, t.range.start), o = e.text.slice(t.range.start, t.range.end), s = ns(o), p = rs(s, l, u, c), m = rs({
			scalars: _,
			pitchBearing: v
		}, l, u, c);
		_ += s.scalars, v += s.pitchBearing;
		let h = i === (g?.length ?? 0) - 1 ? e.fitTextTrailingPadPx ?? 0 : 0, y = e.punctuationCompressions?.filter((e) => e.end <= t.range.start).reduce((e, t) => e + t.adjustmentPt, 0) ?? 0, b = e.punctuationCompressions?.filter((e) => e.end > t.range.start && e.end <= t.range.end).reduce((e, t) => e + t.adjustmentPt, 0) ?? 0, x = Kc(e, a, r) * d, S = Kc(e, o, r) * d;
		return {
			range: {
				start: n + t.range.start,
				end: n + t.range.end
			},
			offset: {
				xPt: t.offsetPt * d + (e.leadingWordBoundaryPx ?? 0) + (e.autoSpaceLeadingPx ?? 0) + m + x + y,
				yPt: f
			},
			advancePt: t.advancePt * d + p + S + h + b
		};
	}), b = /* @__PURE__ */ new Map();
	if (!e.verticalRun && il(e, r, 1)) {
		let t = {
			kind: "natural-clusters",
			clusters: e.textLayoutService && e.textShapeRequest ? ul(e, 0, e.text.length, q(e, 1), () => {
				throw Error("Condensed cluster acquisition requires TextLayoutService");
			}, () => {}) : (g ?? []).map((t) => ({
				text: e.text.slice(t.range.start, t.range.end),
				advancePx: t.advancePt
			}))
		}, i = sl(e, r, 1, t);
		if (cl(t, i)) {
			let e = y[0]?.offset.xPt ?? 0, r = n;
			y = t.clusters.map((t, n) => {
				let a = {
					start: r,
					end: r + t.text.length
				};
				r = a.end;
				let o = i[n] > 0 ? i[n] : 0;
				i[n] < 0 && b.set(a.start, t.advancePx * d);
				let s = {
					range: a,
					offset: {
						xPt: e,
						yPt: f
					},
					advancePt: o
				};
				return e += o, s;
			});
		}
	}
	let x = e.verticalRun && a ? a.planRun({
		text: e.text,
		font: Ie(s.fontRoute, s.fontSizePt, s.fontWeight, s.fontStyle),
		fontKerning: s.paintOps[0].kerning,
		fontSizePt: s.fontSizePt,
		letterSpacingPt: c,
		characterGridDeltaPt: l,
		charScale: d,
		growTrRotateInk: !0,
		writingMode: s.paintOps[0].writingMode
	}) : void 0, S;
	if (x && a && il(e, r, 1)) {
		let t = a.planRun({
			text: e.text,
			font: Ie(s.fontRoute, s.fontSizePt, s.fontWeight, s.fontStyle),
			fontKerning: s.paintOps[0].kerning,
			fontSizePt: s.fontSizePt,
			letterSpacingPt: c,
			characterGridDeltaPt: l,
			charScale: d,
			growTrRotateInk: !0,
			writingMode: s.paintOps[0].writingMode,
			characterAdjustmentPt: al(e, r, 1)
		});
		if (t.some((e) => e.floored)) {
			S = t;
			let e = y[0]?.offset.xPt ?? 0;
			y = t.map((t) => {
				let r = {
					range: {
						start: n + t.range.start,
						end: n + t.range.end
					},
					offset: {
						xPt: e,
						yPt: f
					},
					advancePt: t.advancePt
				};
				return e += t.advancePt, r;
			});
		}
	}
	if (e.latinSpaceCompressionPx && e.text.endsWith(" ") && y.length > 0) {
		let t = n + e.text.replace(/ +$/u, "").length, r = e.latinSpaceCompressionPx / (n + e.text.length - t), i = 0;
		y = y.map((e) => {
			let n = Math.max(0, e.range.end - Math.max(e.range.start, t));
			if (n === 0 && i === 0) return e;
			let a = {
				...e,
				offset: {
					...e.offset,
					xPt: e.offset.xPt - i
				},
				advancePt: Math.max(0, e.advancePt - n * r)
			};
			return i += n * r, a;
		});
	}
	let C = e.snapGridLeadingPadPx ?? 0, w = e.measuredWidth - (e.snapGridTrailingPadPx ?? 0), T;
	if (e.snapGridClass === "eastAsia" && e.snapGridCellPitchPx) {
		let t = e.snapGridCellPitchPx, n = 0;
		y = y.map((r, i) => {
			let a = ur(r.advancePt, t), o = a * t, s = n * t + (o - r.advancePt) / 2;
			if (i === y.length - 1) {
				w = s + r.advancePt;
				let t = g?.[i]?.offsetPt;
				e.selectedFaceInkBounds && t !== void 0 && !/\s$/u.test(e.text) && (T = s + Math.max(0, (e.selectedFaceInkBounds.xMaxPt - t) * d));
			}
			let c = {
				...r,
				offset: {
					xPt: s,
					yPt: r.offset.yPt
				},
				advancePt: o
			};
			return n += a, c;
		});
	} else C !== 0 && (y = y.map((e) => ({
		...e,
		offset: {
			xPt: e.offset.xPt + C,
			yPt: e.offset.yPt
		}
	})));
	let { origin: E, bounds: D, advancePt: O, paintOps: k, clusters: A, ...j } = s, M = e.tateChuYoko && e.tateChuYokoCompress ? (() => {
		if (!e.textLayoutService || !e.textShapeRequest) throw Error("Tate-chu-yoko compression requires TextLayoutService");
		let t = e.textLayoutService.shape({
			...e.textShapeRequest,
			fontSizePt: s.fontSizePt,
			measure: !0,
			clusterGeometry: !1
		}), n = t.ascentPt + t.descentPt;
		return n > s.fontSizePt && n > 0 ? s.fontSizePt / n : 1;
	})() : 1, N = e.punctuationCompressions?.some((t) => t.end < e.text.length) ?? !1, P = /* @__PURE__ */ new Set();
	if (b.size > 0) for (let t of y) b.has(t.range.start) && !as(e.text.slice(t.range.start - n, t.range.end - n)) && P.add(t.range.start);
	let F = P.size > 0, I = !e.verticalRun && !e.tateChuYoko && (N || F), L = e.verticalRun ? (() => {
		if (!a) throw Error("Vertical glyph planning capability is required for vertical text");
		let t = k[0];
		return (S ?? x ?? []).map((r) => ({
			...t,
			text: r.text,
			range: {
				start: n + r.range.start,
				end: n + r.range.end
			},
			offset: {
				xPt: r.originPt + (S ? 0 : e.punctuationCompressions?.filter((e) => e.end <= r.range.start).reduce((e, t) => e + t.adjustmentPt, 0) ?? 0),
				yPt: f
			},
			letterSpacingPt: c,
			glyphOrientation: r.orientation,
			...r.verticalFeature ? { verticalFeature: !0 } : {},
			...r.naturalAdvancePt === void 0 ? {} : { naturalAdvancePt: r.naturalAdvancePt },
			...r.blockAxisInkBounds ? { blockAxisInkBounds: r.blockAxisInkBounds } : {},
			...r.drawOffsetPt.xPt !== 0 || r.drawOffsetPt.yPt !== 0 ? { glyphOffsetPt: r.drawOffsetPt } : {}
		}));
	})() : e.tateChuYoko ? k.map((t) => ({
		...t,
		offset: {
			xPt: t.offset.xPt + e.measuredWidth / 2,
			yPt: t.offset.yPt
		},
		glyphOrientation: "upright",
		...M === 1 ? {} : { scaleY: M }
	})) : I ? (() => {
		let t = k[0], r = F ? ls(e.text) : void 0, i = [];
		for (let t of y) {
			let a = t.range.end - n, o = e.punctuationCompressions?.find((e) => e.end === a)?.adjustmentPt ?? null, s = P.has(t.range.start), c = i.at(-1);
			c && !s && !c.floored && c.adjustmentPt === o && !r?.(t.range.start - n) ? c.end = t.range.end : i.push({
				start: t.range.start,
				end: t.range.end,
				offset: t.offset,
				adjustmentPt: o,
				floored: s
			});
		}
		return i.map((r) => {
			let i = e.text.slice(r.start - n, r.end - n);
			return {
				...t,
				text: i,
				range: {
					start: r.start,
					end: r.end
				},
				offset: r.offset,
				letterSpacingPt: r.floored ? 0 : c + (r.adjustmentPt ?? 0),
				...r.floored ? { naturalAdvancePt: aC(e, i, d, b.get(r.start)) } : {}
			};
		});
	})() : k, R = e.snapGridClass === "eastAsia" ? (() => {
		let t = L[0];
		return t ? y.map((r) => ({
			...t,
			text: e.text.slice(r.range.start - n, r.range.end - n),
			range: r.range,
			offset: r.offset
		})) : L;
	})() : C === 0 ? L : L.map((e) => ({
		...e,
		offset: {
			xPt: e.offset.xPt + C,
			yPt: e.offset.yPt
		}
	})), z = r?.type === "snapToChars" && e.underline && !e.verticalRun && t.bidi !== !0 && e.selectedFaceInkBounds ? T ?? (R.length === 1 ? R[0].offset.xPt + (R[0].glyphOffsetPt?.xPt ?? 0) + e.selectedFaceInkBounds.xMaxPt * (R[0].scaleX ?? 1) : w) : w;
	return {
		...j,
		kind: "text",
		measuredWidthPt: e.measuredWidth,
		...jc(e) ? { nativeBaseDirection: e.nativeLevelUnit.baseDirection } : {},
		...p ? { nativeVisiblePrefix: e.nativeVisiblePrefix } : {},
		...e.leadingWordBoundaryPx ? { leadingSeamPairPt: e.leadingWordBoundaryPx } : {},
		characterGridDeltaPt: l,
		...e.latinSpaceCompressionPx ? { trailingSpaceCompressionPt: e.latinSpaceCompressionPx } : {},
		clusters: e.optionalHyphenGlyph ? y.map((e) => ({
			...e,
			range: {
				start: n,
				end: n
			}
		})) : y,
		basePaintOps: R.map((t) => ({
			...t,
			...e.optionalHyphenGlyph ? { range: {
				start: n,
				end: n
			} } : {},
			offset: {
				...t.offset,
				xPt: I ? t.offset.xPt : t.offset.xPt + (e.leadingWordBoundaryPx ?? 0) + (e.autoSpaceLeadingPx ?? 0)
			},
			letterSpacingPt: e.verticalRun && t.glyphOrientation !== "sideways" ? 0 : I ? t.letterSpacingPt : c,
			...!e.verticalRun && e.selectedFaceInkBounds ? { inkBounds: e.selectedFaceInkBounds } : {},
			...!e.verticalRun && e.selectedFaceInkBounds && t.glyphOrientation === void 0 ? { blockAxisInkBounds: {
				startPt: (t.glyphOffsetPt?.yPt ?? 0) - e.selectedFaceInkBounds.ascentPt,
				endPt: (t.glyphOffsetPt?.yPt ?? 0) + e.selectedFaceInkBounds.descentPt
			} } : {}
		})),
		breakBefore: e.breakBefore !== !1 && !e.joinPrev,
		rtl: e.rtl,
		digitsAsAN: e.digitsAsAN,
		fixedPitch: e.fitTextRegionIndex !== void 0 || e.snapGridClass !== void 0,
		...e.listLabel === void 0 ? {} : { listLabel: !0 },
		...r?.type === "snapToChars" && e.underline ? { decorationTerminalAdvancePt: z } : {},
		...m ? { retainedGeometry: m } : {},
		...e.autoSpaceBeforePt !== void 0 && (e.autoSpaceLeadingPx ?? 0) > 0 ? { autoSpace: {
			appliedPt: e.autoSpaceLeadingPx,
			naturalPt: e.autoSpaceBeforePt
		} } : {},
		...e.selectedFaceFontBox ? { selectedFaceFontBox: e.selectedFaceFontBox } : {},
		...e.textLayoutService ? { textLayoutService: e.textLayoutService } : {},
		...e.textShapeRequest ? { textShapeRequest: e.textShapeRequest } : {}
	};
}
function fw(e, t, n) {
	let r = /* @__PURE__ */ new Map(), i = /* @__PURE__ */ new Set();
	for (let e of t.lines) for (let t of e.layout.segments) {
		if (t.sourceTextSequence) {
			if (!i.has(t.sourceTextSequence)) {
				i.add(t.sourceTextSequence);
				for (let e of t.sourceTextSequence) r.set(e.runIndex, e.end - e.start);
			}
			continue;
		}
		let e = UC(t);
		if (e === void 0) continue;
		let n = "text" in t ? pw(t) : "math" in t ? t.fallbackText.length : +("isTab" in t || "imagePath" in t);
		r.set(e, (r.get(e) ?? 0) + n);
	}
	let a = e.runs.map((e, t) => {
		let i = e.revision?.kind;
		if (du(i, n)) return 0;
		let a = r.get(t);
		return a === void 0 ? e.type === "text" ? e.text.length : e.type === "field" ? e.fallbackText.length : e.type === "anchorHost" ? 0 : 1 : a;
	}), o = 0;
	return {
		runStarts: a.map((e) => {
			let t = o;
			return o += e, t;
		}),
		runLengths: a
	};
}
function pw(e) {
	return e.metricOnly || e.optionalHyphenGlyph ? 0 : e.text.length;
}
function mw(e) {
	return "text" in e ? pw(e) : "math" in e ? e.fallbackText.length : 1;
}
function hw(e, t, n, r, i, a, o, s, c, l, u, d = !1, f = ql, p, m) {
	let { ulTrailSpace: h, doNotExpandShiftReturn: g } = f, _ = l?.plainLineBoxes !== !0 && !t.shading && !Object.values(t.borders ?? {}).some(Boolean) && !Object.values(t.typographyInput?.borders ?? {}).some(Boolean) && !t.tabStops?.some((e) => e.alignment === "bar"), v = 0, y = /* @__PURE__ */ new Map(), b = /* @__PURE__ */ new Map(), x = e.lines.some((e) => e.layout.segments.some((e) => "isTab" in e)), S = t.tabStops?.reduce((e, t) => !e || t.pos < e.pos ? t : e, void 0), C = e.lines.flatMap((e) => e.layout.segments.flatMap((e) => "text" in e && !e.metricOnly ? [e.text] : [])).join("").trim(), w = !x && S?.alignment === "decimal" && C !== "" && /^[+\-(]?[\d., ]+\)?%?$/u.test(C) ? S.pos - o.physicalIndentLeftPt : void 0, T = l?.libreOfficeLineBoxes === !0 && !d && !wd(t.runs), E = ah(t, o.lineGrid.active || !f.specifiedTextLineBoxMode15);
	return jC(e.lines.map((x, S) => {
		let C = x.layout, D = S === 0 && c?.markerText ? c.lineBox?.ascentPt : void 0, O = E ? oh(C, o, t, f, d, p, D === void 0 ? void 0 : Math.max(D, C.ascent) + C.descent) : null, k = !O && YC(C) && o.lineSpacing?.rule === "exact" && o.lineSpacing.value >= 12 && o.lineSpacing.value <= 30 && f.specifiedTextLineBoxMode15 && !o.lineGrid.active && C.topY === void 0, A = !O && YC(C) && o.lineSpacing?.rule === "atLeast" && f.specifiedTextLineBoxMode15 && !o.lineGrid.active && C.topY === void 0, j = t.__lineExtraAbove === !0 && (o.lineSpacing?.rule === "exact" || o.lineSpacing?.rule === "atLeast" || o.lineSpacing?.rule === "auto" && o.lineSpacing.value < 1) ? o.lineSpacing.rule === "exact" ? x.topYPt + o.lineSpacing.value * 4 / 5 : o.lineSpacing.rule === "auto" ? x.topYPt + x.advancePt * 4 / 5 : x.topYPt + x.advancePt - (C.visibleDescent ?? C.descent) : O ? x.topYPt + O.baselineOffsetPt : k ? x.topYPt + o.lineSpacing.value * 4 / 5 : A ? x.topYPt + x.advancePt - (C.visibleDescent ?? C.descent) : XC(x, o, T), M = Infinity, N = v, P = [];
		for (let e of C.segments) {
			let n = UC(e), r = n === void 0 ? void 0 : t.runs[n], c = mw(e), d = e.sourceTextSequence, f = d ? (s.runStarts[d[0].runIndex] ?? v) + (e.sourceTextOffset ?? 0) : n === void 0 ? v : (s.runStarts[n] ?? v) + (y.get(n) ?? 0);
			if (n !== void 0 && !d && y.set(n, (y.get(n) ?? 0) + c), M = Math.min(M, f), N = Math.max(N, f + c), "isTab" in e) {
				let t = e, n = t.leader ?? "none", i, a, o = r?.type === "text" || r?.type === "field" ? r : void 0, s = o, u = (e) => {
					if (!l) throw Error("Formatted tab acquisition requires TextLayoutService");
					return l.shape({
						text: e,
						fontSizePt: t.fontSize,
						fonts: s?.fontSlots?.direct ?? (o?.fontFamily ? { ascii: o.fontFamily } : {}),
						themeFonts: s?.fontSlots?.theme,
						themeFontPresence: s?.fontSlots?.themePresent,
						weight: t.bold ? 700 : 400,
						style: t.italic ? "italic" : "normal",
						measure: !0
					});
				}, d = (e) => {
					let t = u(e), n = t.spans[0];
					if (!n || t.spans.length !== 1 || n.start !== 0 || n.end !== e.length) throw Error("Formatted tab probe requires one selected-face span");
					return {
						ascentPt: n.ascentPt,
						descentPt: n.descentPt,
						...n.inkBounds ? { inkBounds: n.inkBounds } : {}
					};
				};
				if (o?.underline) {
					let e = o.color ? `#${o.color}` : "#000000", n = u("_").spans[0]?.font, r = n && (n.source === "local" && n.resourceIdentity?.startsWith("office-local:") === !0 || n.source === "native" && n.installedFamily === !0 || pd(n) && Ju(n)) ? Tu(n.requestedFamily, n.weight, n.style) : void 0;
					a = {
						base: d("M"),
						probe: d("_"),
						...r ? { fontRule: {
							geometry: r,
							sizePt: t.fontSize
						} } : {},
						color: s?.underlineColor && s.underlineColor !== "auto" ? `#${s.underlineColor}` : e,
						...s?.underlineStyle ? { authoredStyle: s.underlineStyle } : {}
					};
				}
				if (n !== "none") {
					if (!l) throw Error("Tab leader acquisition requires TextLayoutService");
					let e = n === "hyphen" ? "-" : n === "underscore" || n === "heavy" ? "_" : n === "middleDot" ? "·" : ".", r = u(e), a = r.spans[0];
					if (!a || !Number.isFinite(r.advancePt) || r.advancePt <= 0) throw Error("Tab leader acquisition produced no shaped glyph advance");
					i = {
						glyph: e,
						advancePt: r.advancePt,
						fontRoute: a.fontRoute,
						fontSizePt: t.fontSize,
						fontWeight: a.font.weight,
						fontStyle: a.font.style,
						color: o?.color ? {
							kind: "explicit",
							color: `#${o.color}`
						} : s?.colorAuto ? { kind: "auto" } : { kind: "default" }
					};
				}
				P.push({
					kind: "tab",
					range: {
						start: f,
						end: f + c
					},
					measuredWidthPt: t.measuredWidth,
					leader: n,
					...t.alignedGapLimit ? { alignedGapLimitPt: t.alignedGapLimit } : {},
					fontSizePt: t.fontSize,
					bold: t.bold,
					italic: t.italic,
					...a ? { underline: a } : {},
					...i ? { leaderShape: i } : {}
				});
			} else if ("imagePath" in e) {
				let t = e;
				if (t.anchor) continue;
				let n = UC(e), r = LC(i, n ?? 0), [o, s] = t.effectExtent ?? [0, 0], [l, u] = t.objectSizePt ?? [t.widthPt, t.heightPt];
				if (t.inlineShape) {
					let e = (t.inlineOffsetXPt ?? 0) + o;
					P.push({
						kind: "inline-drawing",
						range: {
							start: f,
							end: f + c
						},
						drawingId: `${a}:drawing:${n ?? 0}`,
						measuredWidthPt: t.measuredWidth,
						widthPt: l,
						heightPt: u,
						topOffsetPt: -t.heightPt + s + (t.inlineOffsetYPt ?? 0),
						...e ? { leftOffsetPt: e } : {}
					}), v = Math.max(v, f + c);
					continue;
				}
				if (t.unavailableResourceKind) {
					P.push({
						kind: "unavailable-resource",
						range: {
							start: f,
							end: f + c
						},
						resourceKind: t.unavailableResourceKind,
						measuredWidthPt: t.measuredWidth,
						widthPt: l,
						heightPt: u,
						topOffsetPt: -t.heightPt + s,
						...o ? { leftOffsetPt: o } : {},
						drawingId: BC(i, n ?? 0)
					}), v = Math.max(v, f + c);
					continue;
				}
				let d = t.chart ? "chart" : "image", p = t.chartResourceKey ?? (t.chart ? zC(r) : Ee(r, t.imagePath)), h = t.listLabel === void 0 ? void 0 : x.topYPt - j + _s + (Math.max(C.ascent + C.descent, C.intendedSingle ?? 0) - t.heightPt - 2 * _s) / 2;
				P.push({
					kind: "resource",
					range: {
						start: f,
						end: f + c
					},
					...n === void 0 ? {} : { sourceRunIndex: n },
					resourceKey: p,
					resourceKind: d,
					measuredWidthPt: t.measuredWidth,
					widthPt: l,
					heightPt: u,
					topOffsetPt: h ?? -t.heightPt + s,
					...h === void 0 ? o ? { leftOffsetPt: o } : {} : { leftOffsetPt: _s },
					...m ? { orientation: m } : {}
				});
			} else if ("math" in e) {
				let t = e;
				P.push({
					kind: "resource",
					range: {
						start: f,
						end: f + c
					},
					...UC(e) === void 0 ? {} : { sourceRunIndex: UC(e) },
					resourceKey: t.mathResourceKey,
					resourceKind: "math",
					measuredWidthPt: t.measuredWidth,
					widthPt: t.measuredWidth,
					heightPt: t.mathAscent + t.mathDescent,
					topOffsetPt: -t.mathAscent
				});
			} else {
				let n;
				if (d) {
					let r = e.sourceTextOffset ?? 0, i = r + c, a = b.get(d) ?? 0;
					for (; a < d.length && d[a].end <= r;) a++;
					b.set(d, a);
					let o = [];
					for (; a < d.length && d[a].start < i; a++) {
						let e = d[a], n = t.runs[e.runIndex];
						o.push({
							sourceRunIndex: e.runIndex,
							range: {
								start: f + Math.max(e.start, r) - r,
								end: f + Math.min(e.end, i) - r
							},
							...n?.type === "field" ? {
								role: "field-result",
								dependency: HC(n)
							} : {}
						});
					}
					n = o;
				}
				P.push(dw(e, t, f, ch(o), r, u, n));
			}
			v = Math.max(v, f + c);
		}
		let F = C.segments.length === 1 && "math" in (C.segments[0] ?? {}) ? C.segments[0] : void 0, I = kC({
			paragraphXPt: n,
			availableWidthPt: r,
			alignment: t.alignment,
			baseRtl: o.baseRtl,
			isFirstLine: S === 0 || C.listLabelFirstIndent === !0,
			...C.listLabelShiftPx === void 0 ? {} : { listLabelShiftPt: C.listLabelShiftPx },
			isLastLine: (C.physicalLineIndex ?? S) === (e.lines.at(-1).layout.physicalLineIndex ?? e.lines.length - 1),
			stretchLastLine: o.stretchLastLine,
			exactLineSpacing: o.lineSpacing?.rule === "exact",
			...h ? { ulTrailSpace: h } : {},
			...g ? { doNotExpandShiftReturn: g } : {},
			...o.endsAtHardBreak ? { endsAtHardBreak: !0 } : {},
			...o.runDirectionUnauthored ? { runDirectionUnauthored: !0 } : {},
			...f.lineEndJustificationBeforeMode15 ? { lineEndJustificationBeforeMode15: !0 } : {},
			...t.alignment === "thaiDistribute" && f.thaiDistributeProportionalSpread && !o.characterGrid.active ? { thaiProportionalSpread: !0 } : {},
			...o.wordWrap === !1 ? { wordWrap: !1 } : {},
			firstLineIndentPt: o.firstIndentPt,
			...S === 0 && c ? { numbering: { bodyOffsetPt: C.numberingFirstLine?.lineStartOffsetPx ?? c.bodyOffsetPt } } : {},
			...w === void 0 ? {} : { decimalAutoTabPt: w },
			...F?.display ? { displayMathJustification: F.jc ?? o.mathDefJc ?? "centerGroup" } : {},
			line: {
				range: {
					start: Number.isFinite(M) ? M : v,
					end: N
				},
				topPt: x.topYPt,
				baselinePt: j,
				advancePt: x.advancePt,
				xOffsetPt: C.xOffset,
				availableWidthPt: C.availWidth,
				...C.marginExtension ? { marginExtensionPt: C.marginExtension } : {},
				justifiedCompressionPt: C.justifiedCompressionPx,
				gapPlan: C.gapPlan,
				endsWithBreak: C.endsWithBreak ?? !1,
				segments: P
			}
		}), L = o.lineGrid.active ? xf(o.lineSpacing, C.ascent, C.descent, 1, void 0, o.hasRuby, C.intendedSingle, C.eastAsian, C.gridCountSingle, void 0, C.uniformPositionAuto, C.inlinePictureTextSingle, C.latinGridCountSingle) : x.advancePt, R = !o.lineGrid.active && T && o.lineSpacing?.rule === "auto" && o.lineSpacing.value > 1 ? Math.max(0, x.advancePt - xf(null, C.ascent, C.descent, 1, void 0, o.hasRuby, C.intendedSingle, C.eastAsian, C.gridCountSingle)) : 0, z = o.lineGrid.active ? AC({
			...I,
			gridAfterLeadingPt: _ ? Math.max(0, Math.min((x.advancePt - L) / 2, x.topYPt + x.advancePt - j - (C.visibleDescent ?? C.descent))) : 0
		}, [I]) : R > 0 ? AC({
			...I,
			pageEdgeOverhangPt: R
		}, [I]) : I;
		return C.availWidth !== void 0 && (C.availWidth < r || (C.xOffset ?? 0) !== 0) ? AC({
			...z,
			wrapBounds: {
				xPt: n + (C.xOffset ?? 0) + (S === 0 ? Math.min(0, o.firstIndentPt) : 0),
				yPt: x.topYPt,
				widthPt: C.availWidth - (S === 0 ? Math.min(0, o.firstIndentPt) : 0),
				heightPt: x.advancePt
			}
		}, [z]) : z;
	}), e.lines.map((e, t) => e.layout.physicalLineIndex ?? t));
}
function gw(e, t, n, r, i) {
	let a = i.filter((e) => e.alignment === "bar");
	return a.length === 0 ? e : e.map((e) => ({
		...e,
		barTabRules: a.map((i) => {
			let a = r ? t + n - i.pos : t + i.pos;
			return {
				from: {
					xPt: a,
					yPt: e.bounds.yPt
				},
				to: {
					xPt: a,
					yPt: e.bounds.yPt + e.bounds.heightPt
				},
				color: "#000000",
				widthPt: 0,
				authoredStyle: "single",
				style: "solid"
			};
		})
	}));
}
function _w(e, t) {
	return {
		start: e.start + t,
		end: e.end + t
	};
}
function vw(e, t) {
	if (!Number.isFinite(t) || t < 0) throw RangeError("Paragraph continuation source range must be finite and non-negative");
	let n = e[0];
	if (!n) return e;
	let r = t - n.range.start;
	return r === 0 ? e : e.map((e) => ({
		...e,
		range: _w(e.range, r),
		placements: e.placements.map((e) => {
			let t = _w(e.range, r);
			return e.kind === "text" ? {
				...e,
				range: t,
				...e.sourceRuns ? { sourceRuns: e.sourceRuns.map((e) => ({
					...e,
					range: _w(e.range, r)
				})) } : {},
				clusters: e.clusters.map((e) => ({
					...e,
					range: _w(e.range, r)
				})),
				paintOps: e.paintOps.map((e) => ({
					...e,
					range: _w(e.range, r)
				}))
			} : {
				...e,
				range: t
			};
		})
	}));
}
function yw(e, t, n, r, i) {
	let a = e.contentEndYPt - e.contentStartYPt;
	return kC({
		paragraphXPt: n,
		availableWidthPt: r,
		alignment: t.alignment,
		baseRtl: i.baseRtl,
		isFirstLine: !0,
		isLastLine: !0,
		stretchLastLine: i.stretchLastLine,
		line: {
			range: {
				start: 0,
				end: 0
			},
			topPt: e.contentStartYPt,
			baselinePt: e.markPictureBaselineOffsetPt === void 0 ? e.contentEndYPt - e.lastLineBelowBaselinePt : e.contentStartYPt + e.markPictureBaselineOffsetPt,
			advancePt: a,
			xOffsetPt: 0,
			availableWidthPt: r,
			endsWithBreak: !1,
			segments: []
		}
	});
}
function bw(e, t) {
	let n = t.anchorFrames, r = e.anchorXRelativeFrom ?? (e.anchorXFromMargin ? "margin" : "page"), i = e.anchorYRelativeFrom ?? (e.anchorYFromPara ? "paragraph" : "page"), a = n?.page, o = n?.margin, s = a && o ? {
		xPt: a.xPt,
		yPt: a.yPt,
		widthPt: Math.max(0, o.xPt - a.xPt),
		heightPt: a.heightPt
	} : null, c = a && o ? {
		xPt: o.xPt + o.widthPt,
		yPt: a.yPt,
		widthPt: Math.max(0, a.xPt + a.widthPt - o.xPt - o.widthPt),
		heightPt: a.heightPt
	} : null, l = a && o ? {
		xPt: a.xPt,
		yPt: a.yPt,
		widthPt: a.widthPt,
		heightPt: Math.max(0, o.yPt - a.yPt)
	} : null, u = a && o ? {
		xPt: a.xPt,
		yPt: o.yPt + o.heightPt,
		widthPt: a.widthPt,
		heightPt: Math.max(0, a.yPt + a.heightPt - o.yPt - o.heightPt)
	} : null, d = n?.pageParity === "even", f = r === "page" ? a : r === "column" || r === "character" ? n?.column : r === "leftMargin" ? s : r === "rightMargin" ? c : r === "insideMargin" ? d ? c : s : r === "outsideMargin" ? d ? s : c : o, p = i === "paragraph" || i === "line" || i === "character" ? {
		xPt: t.placement.paragraphXPt,
		yPt: t.placement.startYPt,
		widthPt: t.placement.availableWidthPt,
		heightPt: 0
	} : i === "page" ? a : i === "column" ? n?.column : i === "topMargin" ? l : i === "bottomMargin" ? u : i === "insideMargin" ? d ? u : l : i === "outsideMargin" ? d ? l : u : o;
	if (!f || !p) return null;
	let m = e.widthPt, h = e.heightPt, g = e.anchorXPt ?? 0, _ = e.anchorYPt ?? 0, v = e.type === "shape" ? e.pctPosH : null, y = e.type === "shape" ? e.pctPosV : null;
	return {
		xPt: v == null ? e.anchorXAlign === "center" ? f.xPt + (f.widthPt - m) / 2 : e.anchorXAlign === "right" || e.anchorXAlign === "outside" && !d || e.anchorXAlign === "inside" && d ? f.xPt + f.widthPt - m : f.xPt + g : f.xPt + f.widthPt * v + g,
		yPt: y == null ? e.anchorYAlign === "center" ? p.yPt + (p.heightPt - h) / 2 : e.anchorYAlign === "bottom" || e.anchorYAlign === "outside" && !d || e.anchorYAlign === "inside" && d ? p.yPt + p.heightPt - h : p.yPt + _ : p.yPt + p.heightPt * y + _,
		widthPt: m,
		heightPt: h
	};
}
function xw(e, t) {
	return bw(e, t) ?? {
		xPt: e.anchorXPt + (e.anchorXFromMargin ? t.placement.paragraphXPt : 0),
		yPt: e.anchorYPt + (e.anchorYFromPara ? t.placement.startYPt : 0),
		widthPt: e.widthPt,
		heightPt: e.heightPt
	};
}
function Sw(e, t, n, r, i = !1) {
	let a = LC(n.source, r), o = rx(e, t, n.environment.layoutServices?.text, e.vmlTextPathInput, e.fill?.fillType === "image" ? Ee(a, e.fill.imagePath) : void 0, void 0, e.vmlPicture ? Pe(a, e.vmlPicture.imagePath) : void 0, e.vmlStrokeFill ? De(a, e.vmlStrokeFill.imagePath) : void 0, Ae(a)), s = [...o.status === "planned" ? o.before ?? [] : [], o.command], c = RC(o, a);
	return {
		kind: "drawing",
		id: `${n.id}:drawing:${r}`,
		source: a,
		flowDomainId: n.flowDomainId,
		flowBounds: t,
		inkBounds: Ub(o.status === "planned" ? o.before ?? [] : [], t),
		advancePt: 0,
		ordinaryFlow: !1,
		commands: s,
		...c.length === 0 ? {} : { diagnostics: c },
		...i ? {} : { anchorLayer: {
			occurrenceId: `public-shape:${n.id}:${r}`,
			behindDoc: e.behindDoc === !0,
			relativeHeight: Number.isFinite(e.zOrder) ? e.zOrder : r,
			sourceOrder: r,
			horizontalOwnership: e.anchorXRelativeFrom === "character" || e.anchorXRelativeFrom === "column" ? "host" : "page",
			verticalOwnership: e.anchorYRelativeFrom === "paragraph" || e.anchorYRelativeFrom === "line" || e.anchorYRelativeFrom === "character" || !e.anchorYRelativeFrom && e.anchorYFromPara ? "host" : "page"
		} }
	};
}
function Cw(e, t, n) {
	if (!e.anchor || e.anchorAcquisitionInput) return null;
	let r = bw(e, t);
	if (!r) return null;
	let i = e.anchorYRelativeFrom ?? (e.anchorYFromPara ? "paragraph" : "page"), a = LC(t.source, n);
	return {
		kind: "drawing",
		id: `${t.id}:public-anchor-drawing:${n}`,
		source: a,
		flowDomainId: t.flowDomainId,
		flowBounds: r,
		inkBounds: r,
		advancePt: 0,
		ordinaryFlow: !1,
		commands: [{
			kind: "resource",
			resourceKind: e.type,
			resourceKey: e.type === "image" ? Ee(a, e.imagePath) : zC(a),
			rect: r,
			...t.environment.verticalPageFrame ? { orientation: Um(t.environment.verticalPageFrame, t.environment.pageWritingMode) } : {}
		}],
		anchorLayer: {
			occurrenceId: `public-anchor:${t.id}:${n}`,
			behindDoc: !1,
			relativeHeight: n,
			sourceOrder: n,
			horizontalOwnership: "page",
			verticalOwnership: i === "paragraph" ? "host" : "page"
		}
	};
}
function ww(e) {
	return (e.type === "image" || e.type === "chart" || e.type === "shape" || e.type === "unavailableDrawing") && e.anchorAcquisitionInput !== void 0;
}
function Tw(e) {
	return [
		{
			xPt: e.xPt,
			yPt: e.yPt
		},
		{
			xPt: e.xPt + e.widthPt,
			yPt: e.yPt
		},
		{
			xPt: e.xPt + e.widthPt,
			yPt: e.yPt + e.heightPt
		},
		{
			xPt: e.xPt,
			yPt: e.yPt + e.heightPt
		}
	];
}
function Ew(e, t, n) {
	let r = t.xPt - e.xPt, i = t.yPt - e.yPt, a = e.xPt + e.widthPt - t.xPt - t.widthPt, o = e.yPt + e.heightPt - t.yPt - t.heightPt;
	return {
		xPt: n.xPt - r,
		yPt: n.yPt - i,
		widthPt: Math.max(0, n.widthPt + r + a),
		heightPt: Math.max(0, n.heightPt + i + o)
	};
}
function Dw(e, t) {
	return {
		a: t.a,
		b: t.b,
		c: t.c,
		d: t.d,
		e: e.xPt + e.widthPt / 2,
		f: e.yPt + e.heightPt / 2
	};
}
function Ow(e, t) {
	let n = [
		jb(t, e),
		jb(t, {
			xPt: e.xPt + e.widthPt,
			yPt: e.yPt
		}),
		jb(t, {
			xPt: e.xPt,
			yPt: e.yPt + e.heightPt
		}),
		jb(t, {
			xPt: e.xPt + e.widthPt,
			yPt: e.yPt + e.heightPt
		})
	];
	if (n.some((e) => e === null)) throw Error("Upright drawing transform must be invertible");
	let r = n, i = Math.min(...r.map((e) => e.xPt)), a = Math.min(...r.map((e) => e.yPt));
	return {
		xPt: i,
		yPt: a,
		widthPt: Math.max(...r.map((e) => e.xPt)) - i,
		heightPt: Math.max(...r.map((e) => e.yPt)) - a
	};
}
function kw(e, t) {
	return th(t, e);
}
function Aw(e, t) {
	let n = (e) => {
		let n = nh(t, {
			top: e.topPt,
			right: e.rightPt,
			bottom: e.bottomPt,
			left: e.leftPt
		});
		return {
			topPt: n.top,
			rightPt: n.right,
			bottomPt: n.bottom,
			leftPt: n.left
		};
	};
	return {
		...e,
		axes: {
			horizontal: e.axes.vertical,
			vertical: e.axes.horizontal
		},
		geometry: {
			...e.geometry,
			objectFrame: th(t, e.geometry.objectFrame),
			inkBounds: th(t, e.geometry.inkBounds),
			wrapBounds: e.geometry.wrapBounds ? th(t, e.geometry.wrapBounds) : null,
			size: {
				horizontal: e.geometry.size.vertical,
				vertical: e.geometry.size.horizontal
			},
			parentEffectExtent: n(e.geometry.parentEffectExtent),
			wrap: {
				...e.geometry.wrap,
				distances: n(e.geometry.wrap.distances),
				distanceSources: nh(t, e.geometry.wrap.distanceSources),
				effectExtent: n(e.geometry.wrap.effectExtent),
				...e.geometry.wrap.polygon ? { polygon: {
					...e.geometry.wrap.polygon,
					points: e.geometry.wrap.polygon.points.map((e) => eh(t, e))
				} } : {}
			}
		}
	};
}
function jw(e, t) {
	let n = e.geometry.objectFrame;
	if (n.xPt === t.xPt && n.yPt === t.yPt && n.widthPt === t.widthPt && n.heightPt === t.heightPt) return e;
	let r = n.widthPt === 0 ? 1 : t.widthPt / n.widthPt, i = n.heightPt === 0 ? 1 : t.heightPt / n.heightPt, a = e.geometry.wrap.polygon;
	return {
		...e,
		geometry: {
			...e.geometry,
			objectFrame: t,
			inkBounds: Ew(e.geometry.inkBounds, n, t),
			wrapBounds: e.geometry.wrapBounds ? Ew(e.geometry.wrapBounds, n, t) : null,
			wrap: {
				...e.geometry.wrap,
				polygon: a ? {
					...a,
					points: a.points.map((e) => ({
						xPt: t.xPt + (e.xPt - n.xPt) * r,
						yPt: t.yPt + (e.yPt - n.yPt) * i
					}))
				} : null
			}
		}
	};
}
function Mw(e, t, n = !1) {
	let r = e.axes[t];
	return r.status !== "resolved" || n || r.referenceFrame === "paragraph" || r.referenceFrame === "line" || r.referenceFrame === "character" ? "host" : "page";
}
function Nw(e, t, n, r, i, a, o, s, c, l, u, d, f) {
	let p = -1, m;
	for (let t = 0; t < n.length; t += 1) {
		let r = n[t]?.placements.find((t) => t.kind === "anchor-host" && t.anchorOccurrenceId === e);
		if (r?.kind === "anchor-host") {
			p = t, m = r;
			break;
		}
	}
	if (!m || p < 0) return null;
	let h = [...t].sort((e, t) => (e.run.anchorAcquisitionInput?.group?.sourceIndex ?? 0) - (t.run.anchorAcquisitionInput?.group?.sourceIndex ?? 0) || e.runIndex - t.runIndex), g = h[0];
	if (!g?.run.anchorAcquisitionInput) return null;
	let _ = n[p], v = f?.bounds ?? _.bounds, y = f?.firstLine ?? p === 0, b = i.anchorFrames, x = g.run.anchorAcquisitionInput.behavior, S = x.layoutInCellStatus === "valid" && x.layoutInCell === !0 && i.anchorCellBounds !== void 0 ? i.anchorCellBounds : null, C = CS({
		acquisition: g.run.anchorAcquisitionInput,
		frames: {
			page: b?.page ? S ? {
				...b.page,
				...S
			} : b.page : null,
			margin: b?.margin ? S ? {
				...b.margin,
				...S
			} : b.margin : null,
			column: b?.column ? S ? {
				...b.column,
				...S
			} : Jw(g.run.anchorAcquisitionInput, i) ? {
				...b.column,
				xPt: Kw(b.column, o, u, d, n[0]?.bounds.heightPt ?? 0)
			} : b.column : null,
			paragraph: {
				xPt: i.placement.paragraphXPt,
				yPt: i.placement.startYPt + (g.run.anchorAcquisitionInput.vertical.relativeFrom === "paragraph" && g.run.anchorAcquisitionInput.wrap.kind === "none" && x.allowOverlap === !0 && x.layoutInCell === !0 && i.anchorCellBounds !== void 0 && i.environment.pageWritingMode === "horizontal-tb" ? i.paragraphAnchorReferenceDeltaPt ?? 0 : 0),
				widthPt: i.placement.availableWidthPt,
				heightPt: Math.max(0, a)
			},
			line: y && i.context.lineGrid.active && g.run.type === "image" && g.run.anchorAcquisitionInput.vertical.choice.kind === "offset" ? {
				...v,
				yPt: eS(v.yPt, i.placement.startYPt, d)
			} : v,
			character: m.bounds,
			pageParity: b?.pageParity ?? null
		}
	});
	if (C.status !== "resolved") return {
		result: C,
		textBoxes: [],
		hostLineIndex: p,
		hostRange: m.range
	};
	let w = i.environment.verticalPageFrame && b?.page ? Zm(b.page, i.environment.pageWritingMode) : void 0, T = w === void 0 ? void 0 : rh(i.environment.pageWritingMode, w), E = w === void 0 ? C : Aw(C, T.physicalToLogical);
	if (x.behindDocStatus !== "valid" || x.relativeHeightStatus !== "valid" || x.behindDoc === null || x.relativeHeight === null) throw Error("resolved anchor frame must retain required CT_Anchor behavior");
	let D = E.geometry.objectFrame, O = w === void 0 ? void 0 : Dw(D, T.physicalToLogical), k = O ? {
		...i.environment,
		verticalCJK: !1,
		verticalPageFrame: !1
	} : i.environment, A = [], j = [], M = [], N = [], P = [];
	if (x.allowOverlapStatus !== "valid" || x.allowOverlap === null || x.layoutInCellStatus !== "valid" || x.layoutInCell === null) throw Error("resolved anchor frame must retain overlap and cell behavior");
	let F = x.allowOverlap, I = x.layoutInCell, L = (t) => {
		let n = /* @__PURE__ */ new Map(), r = D, a = O, o = {
			xPt: 0,
			yPt: 0
		};
		if (g.run.type === "shape" && g.run.anchorAcquisitionInput.group === null) {
			let s = LC(i.source, g.runIndex), c = a ? Ow(D, a) : D, l = Uw(g.run, c, {
				id: `${i.id}:anchor-textbox:${e}:${g.runIndex}`,
				source: s,
				flowDomainId: i.flowDomainId,
				context: i.context,
				measurer: i.measurer,
				environment: k,
				input: g.run.textBoxInput,
				acquireCompleteStory: i.acquireCompleteStory,
				...a ? { coordinateSpace: "upright-physical" } : {},
				...t ? { pageFrames: t } : {}
			}), u = l ? Hw(g.run.anchorAcquisitionInput, b?.pageParity ?? null, c, l.flowBounds) : {
				xPt: 0,
				yPt: 0
			}, d = l && (u.xPt !== 0 || u.yPt !== 0) ? vb(l, u) : l;
			o = u, d && (n.set(g.runIndex, d), r = a ? kw(d.flowBounds, a) : d.flowBounds);
		}
		let s = jw(E, r), u = (e) => {
			if (r = Q(r, e), a) a = {
				...a,
				e: a.e + e.xPt,
				f: a.f + e.yPt
			};
			else {
				let t = n.get(g.runIndex);
				t && n.set(g.runIndex, vb(t, e)), o = {
					xPt: o.xPt + e.xPt,
					yPt: o.yPt + e.yPt
				};
			}
			s = jw(E, r);
		}, d = i.frozenAnchorFrames?.get(e);
		if (d) {
			let e = {
				xPt: d.xPt - r.xPt,
				yPt: d.yPt - r.yPt
			};
			(e.xPt !== 0 || e.yPt !== 0) && u(e);
		}
		let f = s.geometry.wrapBounds;
		if (!F) {
			let t = Mw(s, "vertical", I && i.anchorCellBounds !== void 0), n = l.filter((e) => !$x(t, x.relativeHeight, e.relativeHeight)), a = [...c, ...n].filter((t) => t.occurrenceId !== e).map((e) => ({
				occurrenceId: e.occurrenceId,
				kind: "drawingml",
				paragraphId: 0,
				bounds: e.bounds,
				exclusionBounds: e.bounds
			})), o = i.anchorFrames?.page, d = I && i.anchorCellBounds ? i.anchorCellBounds.xPt + i.anchorCellBounds.widthPt : o ? o.xPt + o.widthPt : Infinity, p = Ra({
				moving: {
					occurrenceId: e,
					kind: "drawingml",
					paragraphId: 1,
					bounds: r,
					exclusionBounds: f ?? r
				},
				blockers: a,
				avoidance: { kind: "drawingml-normative" },
				rightBoundaryPt: d
			}).displacement;
			(p.xPt !== 0 || p.yPt !== 0) && u(p);
		}
		return Object.freeze({
			acquiredShapeTextBoxes: n,
			rect: r,
			uprightTransform: a,
			effectiveResult: s,
			textBoxShift: o
		});
	}, R = i.hostFlowPageTranslationPt, z = i.hostPageFrames === void 0 ? b?.page && b.margin ? {
		page: b.page,
		margin: b.margin
	} : null : i.hostPageFrames, ee = (e) => {
		if (!z) return null;
		let t = I && i.anchorCellBounds !== void 0, n = {
			horizontal: Mw(e.effectiveResult, "horizontal", t) === "host",
			vertical: Mw(e.effectiveResult, "vertical", t) === "host"
		};
		return (n.horizontal || n.vertical) && !R ? null : HS(z, Eb(Ob(n.horizontal ? R.xPt : 0, n.vertical ? R.yPt : 0), Eb(e.uprightTransform ?? {
			a: 1,
			b: 0,
			c: 0,
			d: 1,
			e: 0,
			f: 0
		}, Ob(e.textBoxShift.xPt, e.textBoxShift.yPt))));
	}, B = L(), V = B.acquiredShapeTextBoxes.get(g.runIndex)?.story.bandDependent === !0 ? ee(B) : null;
	if (V) try {
		B = US(V, (e) => {
			let t = L(e ?? void 0);
			return {
				value: t,
				next: ee(t)
			};
		}, 16);
	} catch (e) {
		throw e instanceof Go ? new Wo("NON_CONVERGENCE", `anchored text-box page frames did not converge (${e.reason}; ${e.states.length} states)`) : e;
	}
	let { acquiredShapeTextBoxes: te, rect: H, effectiveResult: U } = B;
	O = B.uprightTransform;
	for (let { run: t, runIndex: n } of h) {
		let r = LC(i.source, n), a = t.anchorAcquisitionInput, o = Gb(a, H, T), s = O ? Ow(o, O) : o;
		if (t.type === "image") A.push({
			kind: "resource",
			resourceKind: "image",
			resourceKey: Ee(r, t.imagePath),
			rect: s
		});
		else if (t.type === "chart") A.push({
			kind: "resource",
			resourceKind: "chart",
			resourceKey: zC(r),
			rect: s
		});
		else if (t.type === "unavailableDrawing") A.push({ kind: "noop" }), M.push(VC(t.resourceKind, r));
		else {
			let o = ix(t, a, s, i.environment.layoutServices?.text, t.fill?.fillType === "image" ? Ee(r, t.fill.imagePath) : void 0, void 0, t.vmlPicture ? Pe(r, t.vmlPicture.imagePath) : void 0, t.vmlStrokeFill ? De(r, t.vmlStrokeFill.imagePath) : void 0, Ae(r));
			A.push(...o.status === "planned" ? o.before ?? [] : [], o.command), o.status === "planned" && j.push(...o.before ?? []), M.push(...RC(o, r));
			let c = `${i.id}:anchor-textbox:${e}:${n}`, l = te.get(n) ?? Uw(t, s, {
				id: c,
				source: r,
				flowDomainId: i.flowDomainId,
				context: i.context,
				measurer: i.measurer,
				environment: k,
				input: t.textBoxInput,
				acquireCompleteStory: i.acquireCompleteStory,
				...O ? { coordinateSpace: "upright-physical" } : {}
			});
			l && (N.push(l), P.push(c));
		}
	}
	let ne = {
		kind: "drawing",
		id: `${i.id}:anchor-drawing:${e}`,
		source: LC(i.source, g.runIndex),
		flowDomainId: i.flowDomainId,
		flowBounds: H,
		inkBounds: Ub(j, U.geometry.inkBounds, O),
		advancePt: 0,
		ordinaryFlow: !1,
		...O ? {
			orientation: "upright-physical",
			transform: O
		} : {},
		commands: A,
		...M.length === 0 ? {} : { diagnostics: Object.freeze(M) },
		anchorLayer: {
			occurrenceId: e,
			behindDoc: x.behindDoc,
			relativeHeight: x.relativeHeight,
			sourceOrder: g.runIndex,
			horizontalOwnership: Mw(U, "horizontal", x.layoutInCell && i.anchorCellBounds !== void 0),
			verticalOwnership: Mw(U, "vertical", x.layoutInCell && i.anchorCellBounds !== void 0),
			...x.layoutInCell && i.anchorCellBounds ? { layoutInCell: !0 } : {},
			...x.layoutInCell && Jx(x.allowOverlap, U.geometry.wrap.kind) && i.anchorCellBounds ? { cellContainment: !0 } : {}
		},
		...P.length ? { textBoxIds: P } : {}
	}, re = U.geometry.wrapBounds;
	return {
		result: U,
		drawing: ne,
		exclusion: re && U.geometry.wrap.kind !== "none" ? {
			id: `${i.id}:anchor-exclusion:${e}`,
			wrap: U.geometry.wrap.kind,
			...U.geometry.wrap.side ? { wrapSide: U.geometry.wrap.side } : {},
			bounds: re,
			polygon: U.geometry.wrap.polygon?.points ?? Tw(re),
			anchorOccurrenceId: e,
			...i.anchorLineExemptions?.has(e) ? { anchorLineExemptTopPt: i.anchorLineExemptions.get(e) } : {},
			...U.geometry.wrap.kind === "tight" && Zl(i.environment).mode14TightAnchor ? { wordMode14TightAnchor: !0 } : {},
			verticalOwnership: Mw(U, "vertical", x.layoutInCell && i.anchorCellBounds !== void 0)
		} : void 0,
		collision: {
			occurrenceId: e,
			bounds: H,
			horizontalOwnership: Mw(U, "horizontal", x.layoutInCell && i.anchorCellBounds !== void 0),
			verticalOwnership: Mw(U, "vertical", x.layoutInCell && i.anchorCellBounds !== void 0),
			...x.relativeHeight === null ? {} : { relativeHeight: x.relativeHeight }
		},
		textBoxes: N,
		...x.layoutInCell && Jx(x.allowOverlap, U.geometry.wrap.kind) && i.anchorCellBounds ? { cellContainmentBounds: H } : {},
		hostLineIndex: p,
		hostRange: m.range
	};
}
function Pw(e, t) {
	let n = t.bidi === !0, r = t.runs.some((e) => e.type === "text" && !!e.ruby), i = t.runs.some((e) => e.type === "text" && vs.test(e.text)), { endsAtHardBreak: a, cjkClosingMarkHang: o, lineEdgeRules: s, documentKinsoku: c, ...l } = e;
	return {
		...l,
		kinsoku: c ?? e.kinsoku,
		...t.endsAtHardBreak === !0 ? { endsAtHardBreak: !0 } : {},
		runDirectionUnauthored: !0,
		rightIndentGrid: {
			...e.rightIndentGrid,
			paragraphAllowsAdjustment: t.adjustRightInd !== !1
		},
		physicalIndentLeftPt: n ? t.indentRight : t.indentLeft,
		physicalIndentRightPt: n ? t.indentLeft : t.indentRight,
		firstIndentPt: t.indentFirst,
		lineSpacing: t.lineSpacing,
		spaceBeforePt: t.spaceBefore,
		spaceAfterPt: t.spaceAfter,
		baseRtl: n,
		isJustified: Ni(t.alignment),
		stretchLastLine: Pi(t.alignment),
		tabStops: V_(t),
		hasRuby: r,
		hasEastAsianText: i
	};
}
function Fw(e) {
	return gs(e);
}
function Iw(e, t, n) {
	let r = Math.max(0, t - n);
	return e === "b" ? r : e === "ctr" ? r / 2 : 0;
}
function Lw(e, t) {
	return t === "vert" || t === "eaVert" ? {
		topPt: e.rightPt,
		rightPt: e.bottomPt,
		bottomPt: e.leftPt,
		leftPt: e.topPt
	} : t === "vert270" ? {
		topPt: e.leftPt,
		rightPt: e.topPt,
		bottomPt: e.rightPt,
		leftPt: e.bottomPt
	} : { ...e };
}
function Rw(e, t, n, r, i = !1) {
	let a = t === "eaVert" || t === "mongolianVert", o = e.lines.map((e) => {
		let o = t === "mongolianVert" ? e.placements.reduce((t, n) => n.kind === "text" && n.ruby ? Math.max(t, e.baselinePt - Math.min(e.baselinePt, ...n.ruby.paintOps.map((e) => e.origin.yPt))) : t, 0) : 0, s = (t === "mongolianVert" ? 2 * n.yPt + n.heightPt - e.baselinePt + (i ? 0 : r.bottomPt - r.leftPt) + o : e.baselinePt) - e.baselinePt, c = e.bounds.yPt + s, l = e.placements.map((e) => {
			if (e.kind !== "text") return "bounds" in e && e.bounds ? {
				...e,
				bounds: {
					...e.bounds,
					yPt: e.bounds.yPt + s
				}
			} : e;
			let t = a ? ax(e, i) : e.paintOps;
			return vT({
				...e,
				paintOps: t
			}, s);
		});
		return {
			...e,
			bounds: {
				...e.bounds,
				yPt: c
			},
			baselinePt: e.baselinePt + s,
			placements: l
		};
	});
	return {
		...e,
		lines: o
	};
}
function zw(e, t, n = !1) {
	let r = (e, r) => e.kind === "paragraph" ? Rw(e, t === "mongolianVert" ? "eaVert" : t, r, {
		topPt: 0,
		rightPt: 0,
		bottomPt: 0,
		leftPt: 0
	}, n) : zw(e, t, n), i = {
		...e,
		rows: e.rows.map((e) => ({
			...e,
			cells: e.cells.map((e) => ({
				...e,
				blocks: e.blocks.map((t) => ({
					...t,
					layout: r(t.layout, e.contentBounds)
				}))
			}))
		}))
	}, a = /* @__PURE__ */ new Map(), o = (e) => {
		let r = a.get(e);
		if (r) return r;
		let i = {
			...e,
			child: zw(e.child, t, n)
		};
		return a.set(e, i), i;
	}, s = e.floatingTables?.map(o), c = e.resolvedFloatingTables?.map((e) => {
		let t = o(e.source);
		return {
			...e,
			source: t,
			child: t.child
		};
	});
	return {
		...i,
		...s ? { floatingTables: s } : {},
		...c ? { resolvedFloatingTables: c } : {}
	};
}
function Bw(e, t, n, r, i = !1) {
	return {
		...e,
		blocks: e.blocks.map((e) => {
			if (e.kind === "paragraph") return Rw(e, t, n, r, i);
			if (e.kind === "table") return zw(e, t, i);
			throw Error(`Text-box story contains unsupported retained node: ${e.kind}`);
		})
	};
}
function Vw(e, t, n = !0) {
	if (t === 0) return e;
	let r = {
		xPt: 0,
		yPt: t
	};
	return {
		...e,
		flowBounds: Q(e.flowBounds, r),
		inkBounds: Q(e.inkBounds, r),
		...e.clipBounds ? { clipBounds: n ? Q(e.clipBounds, r) : e.clipBounds } : {},
		blocks: e.blocks.map((e) => {
			if (e.kind === "paragraph") return gb(e, r);
			if (e.kind === "table") return bb(e, r);
			throw Error(`Text-box story contains unsupported retained node: ${e.kind}`);
		})
	};
}
function Hw(e, t, n, r) {
	let i = (n, r, i, a, o) => {
		let s = e[n].choice;
		if (s.kind !== "align" || i === o) return 0;
		let c = dS(n, s.value, t), l = c === "trailing" ? r + i - a - o : c === "center" ? r + i / 2 - a - o / 2 : 0;
		return Number.isFinite(l) ? l : 0;
	};
	return {
		xPt: i("horizontal", n.xPt, n.widthPt, r.xPt, r.widthPt),
		yPt: i("vertical", n.yPt, n.heightPt, r.yPt, r.heightPt)
	};
}
function Uw(e, t, n) {
	let r = n.source, i = n.input ?? {
		kind: "compatibility",
		source: {
			story: "textbox",
			storyInstance: `${r.story}:${r.storyInstance}:${r.path.join(".")}`,
			path: []
		},
		paragraphs: Fx(e, {
			story: "textbox",
			storyInstance: `${r.story}:${r.storyInstance}:${r.path.join(".")}`,
			path: []
		})
	}, a = i.source, o = i.kind === "complete" ? i.blockCount : i.paragraphs.length;
	if (o === 0) return;
	let s = e.vmlTextRects, c;
	for (let e of s ?? []) c = c ? [
		Math.min(c[0], e[0]),
		Math.min(c[1], e[1]),
		Math.max(c[2], e[2]),
		Math.max(c[3], e[3])
	] : [
		e[0],
		e[1],
		e[2],
		e[3]
	];
	let l = e.textVert === "wordArtVert" || e.textVert === "wordArtVertRtl", u = Fw(e.textVert), d = u ? {
		xPt: -t.heightPt / 2,
		yPt: -t.widthPt / 2,
		widthPt: t.heightPt,
		heightPt: t.widthPt
	} : t, f = i.kind === "compatibility" ? i.paragraphs : Object.freeze([]), p = !e.vmlTextBox && e.stroke && e.strokeWidth && e.strokeWidth > 0 ? e.strokeWidth / 2 : 0, m = Lw({
		topPt: (e.textInsetT ?? 0) + p,
		rightPt: (e.textInsetR ?? 0) + p,
		bottomPt: (e.textInsetB ?? 0) + p,
		leftPt: (e.textInsetL ?? 0) + p
	}, l ? "vert" : u);
	c && (m.leftPt += c[0] * d.widthPt, m.topPt += c[1] * d.heightPt, m.rightPt += (1 - c[2]) * d.widthPt, m.bottomPt += (1 - c[3]) * d.heightPt);
	let h = {
		xPt: d.xPt + m.leftPt,
		yPt: d.yPt + m.topPt,
		widthPt: Math.max(0, d.widthPt - m.leftPt - m.rightPt),
		heightPt: Math.max(0, d.heightPt - m.topPt - m.bottomPt)
	}, g = n.acquireCompleteStory;
	if (i.kind === "complete" && !g) throw Error("Complete text-box content requires the shared story acquisition adapter");
	let _ = (t) => g({
		source: a,
		container: {
			id: `${n.id}:story`,
			kind: "textbox",
			bounds: h,
			...l ? { quarterTurnMath: !0 } : {},
			...u ? { quarterTurned: !0 } : {},
			capacity: "unbounded",
			...l && e.textWrap === "none" ? { noWrap: !0 } : {}
		},
		coordinateSpace: n.coordinateSpace ?? "section-logical",
		...t ? { pageFrames: t } : {}
	}), v = d.yPt + m.topPt, y = null, b = f.map((t, r) => {
		let i = t.runs.map((t) => xs({
			text: t.text,
			fontSizePt: t.fontSizePt,
			color: t.color?.slice(1) ?? null,
			fontFamily: t.fontFamily ?? null,
			fontFamilyEastAsia: t.fontFamilyEastAsia ?? null,
			bold: t.bold,
			italic: t.italic,
			rtl: t.rtl,
			cs: t.cs,
			fontFamilyCs: t.fontFamilyCs,
			fontSizeCsPt: t.fontSizeCsPt,
			boldCs: t.boldCs,
			italicCs: t.italicCs,
			ruby: t.ruby
		}, e.textVert)), a = Math.max(0, d.widthPt - m.leftPt - m.rightPt - t.indentLeftPt - t.indentRightPt - Math.max(0, t.indentFirstPt)), o = u ? t.image?.heightPt ?? 0 : t.image?.widthPt ?? 0, s = u ? t.image?.widthPt ?? 0 : t.image?.heightPt ?? 0, c = o > a && o > 0 ? a / o : 1, f = t.image ? [{
			type: "image",
			imagePath: t.image.imagePath,
			mimeType: t.image.mimeType,
			...t.image.svgImagePath ? { svgImagePath: t.image.svgImagePath } : {},
			widthPt: o > 0 ? o * c : a,
			heightPt: s > 0 ? s * c : a,
			anchor: !1
		}] : i, p = {
			alignment: t.alignment,
			indentLeft: t.indentLeftPt,
			indentRight: t.indentRightPt,
			indentFirst: t.indentFirstPt,
			spaceBefore: t.spacing.beforePt,
			spaceAfter: t.spacing.afterPt,
			lineSpacing: t.lineSpacing,
			numbering: t.numbering ?? null,
			numberingMarkerShapeInput: t.numberingMarkerShapeInput,
			tabStops: [...t.tabStops],
			bidi: t.bidi,
			contextualSpacing: t.contextualSpacing,
			styleId: t.styleId,
			runs: f
		}, g = Pw(n.context, p), _ = wS(y, t, y?.spacing.afterPt ?? 0, t.spacing.beforePt);
		v += _;
		let b = cT(p, {
			id: `${n.id}:paragraph:${r}`,
			source: t.source,
			flowDomainId: `${n.flowDomainId}:textbox`,
			ordinaryFlow: !0,
			context: g,
			placement: {
				startYPt: v,
				paragraphXPt: d.xPt + m.leftPt,
				availableWidthPt: Math.max(0, d.widthPt - m.leftPt - m.rightPt),
				maximumYPt: d.yPt + d.heightPt - m.bottomPt,
				suppressSpaceBefore: !0,
				...l && e.textWrap === "none" ? { noWrap: !0 } : {}
			},
			measurer: n.measurer,
			environment: n.environment,
			exclusions: []
		});
		return v += b.advancePt - b.spacing.afterPt, y = t, u ? Rw(b, u, h, m, l) : b;
	}), x = (r) => {
		let i = r ? Math.max(0, r.advancePt + m.topPt + m.bottomPt) : Math.max(0, v - d.yPt + m.bottomPt), c = e.textAutofit === "sp" && o > 0 && (!u || f.every((e) => e.image === void 0)) && Number.isFinite(i) && i > 0 ? u ? {
			...t,
			widthPt: i
		} : {
			...t,
			heightPt: i
		} : t, p = u ? {
			xPt: -c.heightPt / 2,
			yPt: -c.widthPt / 2,
			widthPt: c.heightPt,
			heightPt: c.widthPt
		} : c, h = u && c.widthPt !== t.widthPt && u !== "mongolianVert" ? b.map((e) => bT(e, p.yPt - d.yPt)) : b, g = {
			xPt: p.xPt + m.leftPt,
			yPt: p.yPt + m.topPt,
			widthPt: Math.max(0, p.widthPt - m.leftPt - m.rightPt),
			heightPt: Math.max(0, p.heightPt - m.topPt - m.bottomPt)
		}, _ = wb(h.map((e) => e.flowBounds)) ?? {
			xPt: g.xPt,
			yPt: g.yPt,
			widthPt: 0,
			heightPt: 0
		}, y = wb(h.map((e) => e.inkBounds)) ?? {
			xPt: g.xPt,
			yPt: g.yPt,
			widthPt: 0,
			heightPt: 0
		}, x = r ?? {
			story: "textbox",
			flowBounds: _,
			inkBounds: y,
			clipBounds: g,
			blocks: h,
			advancePt: Math.max(0, i - m.topPt - m.bottomPt),
			diagnostics: []
		}, S = Xx(x), C = r && u ? p.yPt - d.yPt : 0;
		r && u && (x = Bw(Vw(x, C), u, g, m, l));
		let w = (l ? -1 : 1) * Iw(e.textAnchor, g.heightPt, S);
		x = Vw(x, w, !1);
		let T = e.textUpright ? 0 : (e.rotation ?? 0) + (l && e.flipV ? 180 : 0), E = Number.isInteger(T / 90) ? (T / 90 % 4 + 4) % 4 : null, D = E === null ? Math.sin(T * Math.PI / 180) : [
			0,
			1,
			0,
			-1
		][E], O = E === null ? Math.cos(T * Math.PI / 180) : [
			1,
			0,
			-1,
			0
		][E], k = u ? {
			a: 0,
			b: u === "vert270" ? -1 : 1,
			c: u === "vert270" ? 1 : -1,
			d: 0,
			e: c.xPt + c.widthPt / 2,
			f: c.yPt + c.heightPt / 2
		} : {
			a: 1,
			b: 0,
			c: 0,
			d: 1,
			e: 0,
			f: 0
		}, A = c.xPt + c.widthPt / 2, j = c.yPt + c.heightPt / 2, M = T === 0 ? k : Eb({
			a: O,
			b: D,
			c: -D,
			d: O,
			e: A - O * A + D * j,
			f: j - D * A - O * j
		}, k);
		return {
			layout: fv({
				kind: "textbox",
				id: n.id,
				source: f[0]?.source ?? a,
				flowDomainId: `${n.flowDomainId}:textbox`,
				flowBounds: c,
				inkBounds: c,
				...e.defaultTextColor ? { defaultTextColor: `#${e.defaultTextColor.replace(/^#/u, "")}` } : {},
				...(e.vmlTextRects?.length || e.textAutofit === "none") && !l ? { clipBounds: g } : {},
				...s?.length ? { clipRects: s.map((e) => ({
					xPt: p.xPt + e[0] * p.widthPt,
					yPt: p.yPt + e[1] * p.heightPt,
					widthPt: (e[2] - e[0]) * p.widthPt,
					heightPt: (e[3] - e[1]) * p.heightPt
				})) } : {},
				advancePt: 0,
				ordinaryFlow: !1,
				story: x,
				transform: M,
				writingMode: e.textVert === "vert270" ? "vertical-lr" : e.textVert ? "vertical-rl" : "horizontal-tb",
				insets: m,
				contentBounds: p,
				...u ? { verticalMode: u } : {}
			}),
			storyToBox: Eb(M, Ob(0, C + w)),
			storyFlowPt: {
				xPt: 0,
				yPt: C + w
			}
		};
	};
	if (i.kind !== "complete") return x(void 0).layout;
	let S = n.pageFrames;
	if (!S) return x(_()).layout;
	let C = (e) => {
		let t = HS(S, e.storyToBox);
		return t && Object.freeze({
			...t,
			storyFlowPt: e.storyFlowPt
		});
	}, w = x(_());
	if (!w.layout.story.bandDependent) return w.layout;
	let T = C(w);
	if (!T) return w.layout;
	try {
		return US(T, (e) => {
			let t = x(e ? _(e) : _());
			return {
				value: t.layout,
				next: C(t)
			};
		}, 16);
	} catch (e) {
		throw e instanceof Go ? new Wo("NON_CONVERGENCE", `text-box story page frames did not converge (${e.reason}; ${e.states.length} states)`) : e;
	}
}
var Ww = class extends Wo {
	reason;
	states;
	occurrenceCapacity;
	constructor(e, t, n) {
		super("NON_CONVERGENCE", `parser-owned paragraph anchor reflow did not converge (${e}; ${n} occurrences; ${t.length} states)`), this.name = "ParagraphAnchorReflowNonConvergenceError", this.reason = e, this.states = Object.freeze([...t]), this.occurrenceCapacity = n;
	}
};
function Gw(e) {
	return e.map((e, t) => ({
		kind: "shape",
		mode: e.wrap === "topAndBottom" ? "topAndBottom" : "square",
		authoredWrap: e.wrap,
		wrapPolygon: e.polygon,
		imageKey: e.id,
		imageX: e.bounds.xPt,
		imageY: e.bounds.yPt,
		imageW: e.bounds.widthPt,
		imageH: e.bounds.heightPt,
		xLeft: e.bounds.xPt,
		xRight: e.bounds.xPt + e.bounds.widthPt,
		yTop: e.bounds.yPt,
		yBottom: e.bounds.yPt + e.bounds.heightPt,
		side: e.wrapSide ?? "bothSides",
		distLeft: 0,
		distRight: 0,
		distTop: 0,
		distBottom: 0,
		paraId: t,
		...e.anchorLineExemptTopPt === void 0 ? {} : { exemptLineTopPt: e.anchorLineExemptTopPt },
		...e.topEdgeInclusiveFromYPt === void 0 ? {} : { topEdgeInclusiveFromYPt: e.topEdgeInclusiveFromYPt }
	}));
}
function Kw(e, t, n, r, i) {
	let a = t.filter((e) => e.anchorOccurrenceId === void 0 || !n.has(e.anchorOccurrenceId));
	return a.length === 0 ? e.xPt : _o(Gw(a), r, i, e.xPt, e.xPt + e.widthPt) ?? e.xPt;
}
function qw(e, t, n, r) {
	let i = /* @__PURE__ */ new Map();
	if (!Zl(t.environment).mode14TightAnchor) return i;
	for (let t of r) {
		if (t.wrap !== "tight" || t.anchorOccurrenceId === void 0) continue;
		let r = n.lines.find((e) => e.placements.some((e) => e.kind === "anchor-host" && e.anchorOccurrenceId === t.anchorOccurrenceId));
		if (!r) continue;
		let a = Infinity, o = -Infinity;
		for (let e of r.placements) {
			if (e.kind !== "text" && e.kind !== "resource" && e.kind !== "tab") continue;
			let t = e.bounds;
			!t || !(t.widthPt > 0) || (a = Math.min(a, t.xPt), o = Math.max(o, t.xPt + t.widthPt));
		}
		o > a || (a = r.bounds.xPt, o = a + af(e)), co(t.polygon, r.bounds.yPt, r.bounds.heightPt, a, o) || i.set(t.anchorOccurrenceId, r.bounds.yPt);
	}
	return i;
}
function Jw(e, t) {
	return Zl(t.environment).mode14ColumnLineStartOrigin && t.ordinaryFlow && e.simplePosition.enabled !== !0 && e.horizontal.relativeFromStatus === "valid" && e.horizontal.relativeFrom === "column" && e.horizontal.choice.kind === "offset";
}
function Yw(e, t, n) {
	if (t.length === 0) return e.placement;
	if (e.placement.wrap) throw Error("Conflicting paragraph wrap authorities: placement.wrap and effective exclusions");
	let r = e.anchorFrames?.page, i = sh(Gw(t), {
		xLeftPt: r?.xPt ?? e.placement.paragraphXPt,
		xRightPt: r ? r.xPt + r.widthPt : e.placement.paragraphXPt + e.placement.availableWidthPt,
		readingDirection: e.context.baseRtl ? "rtl" : "ltr",
		stepThroughPolygons: Zl(e.environment).throughWrapStepsLines
	});
	return {
		...e.placement,
		wrap: n ? {
			hasExclusions: i.hasExclusions,
			lineWindow(e) {
				let t = i.lineWindow(e);
				return n(Math.max(e.topYPt, t.topYPt), e.probeHeightPt, t.topYPt !== e.topYPt), t;
			},
			skipTopAndBottomBands(e) {
				let t = i.skipTopAndBottomBands(e);
				return n(Math.max(e.yPt, t), 0, t !== e.yPt), t;
			}
		} : i
	};
}
function Xw(e, t) {
	let n = /* @__PURE__ */ new Map();
	for (let r of e.exclusions) {
		let e = r.anchorOccurrenceId;
		if (!(!e || !t.has(e))) {
			if (n.has(e)) throw Error(`Paragraph anchor occurrence produced duplicate exclusions: ${e}`);
			n.set(e, r);
		}
	}
	return Object.freeze([...n.values()]);
}
function Zw(e) {
	return Oe("paragraph-effective-wrap-exclusions", e.map((e) => ({
		id: e.id,
		...e.anchorOccurrenceId === void 0 ? {} : { occurrenceId: e.anchorOccurrenceId },
		wrap: e.wrap,
		...e.wrapSide === void 0 ? {} : { wrapSide: e.wrapSide },
		bounds: e.bounds,
		polygon: e.polygon,
		...e.verticalOwnership === void 0 ? {} : { verticalOwnership: e.verticalOwnership },
		...e.anchorLineExemptTopPt === void 0 ? {} : { anchorLineExemptTopPt: e.anchorLineExemptTopPt },
		...e.topEdgeInclusiveFromYPt === void 0 ? {} : { topEdgeInclusiveFromYPt: e.topEdgeInclusiveFromYPt },
		...e.wordMode14TightAnchor === !0 ? { wordMode14TightAnchor: !0 } : {}
	})));
}
function Qw(e) {
	let t = /* @__PURE__ */ new Set();
	for (let n of e) {
		let e = n.anchorOccurrenceId;
		if (e) {
			if (t.has(e)) throw Error(`Duplicate external paragraph exclusion occurrence: ${e}`);
			t.add(e);
		}
	}
	return t;
}
function $w(e, t) {
	let n = Qw(e);
	return Object.freeze([...e, ...t.filter((e) => !e.anchorOccurrenceId || !n.has(e.anchorOccurrenceId))]);
}
function eT(e, t) {
	let n = /* @__PURE__ */ new Set();
	for (let t of e) {
		if (n.has(t.occurrenceId)) throw Error(`Duplicate external anchor collision occurrence: ${t.occurrenceId}`);
		n.add(t.occurrenceId);
	}
	return Object.freeze([...e, ...t.filter((e) => !n.has(e.occurrenceId))]);
}
function tT(e, t, n, r, i = !1) {
	let a = n.environment.layoutServices, o = n.environment.verticalGlyphMeasurement, s = n.anchorFrames, c = !i && t.runs.some(ww), l = !i && t.runs.some((e) => e.type === "shape" && e.textBoxInput?.kind === "complete"), { wrap: u, ...d } = n.placement, f = n.context, p = n.environment, m = xc(f.baseRtl, f.tabStops) || p.nativeUnitMinimumBandPt !== void 0 && a?.text.acquireProjectableNativeUnits !== void 0 ? ki() : void 0, h = t.runs.some((e) => e.type === "field"), g = t.runs.some((e) => e.type === "text" && e.noteRef !== void 0), _ = !i && t.runs.some((e) => e.type !== "text" && e.type !== "field" && e.type !== "break" && e.type !== "ptab"), v = h || _, y = g || _, b = !i && u ? e.objectIdentity(u) : null, x = [e.objectIdentity(n.measurer.context), e.objectIdentity(n.measurer.fontFamilyClasses)];
	return m && x.push(e.objectIdentity(m.engine), e.objectIdentity(m.token), e.objectIdentity(m.compute), e.objectIdentity(m.reorder)), `${i ? "paragraph-line-breaking-v1" : "paragraph-acquisition-v1"}:${JSON.stringify([
		i ? null : n.id,
		i ? null : [
			n.source.story,
			n.source.storyInstance,
			n.source.path
		],
		i ? null : n.flowDomainId,
		i ? null : n.ordinaryFlow,
		$C(n),
		QC(n) && au(t, f, p),
		i ? [
			d.paragraphXPt,
			d.availableWidthPt,
			d.noWrap ?? !1
		] : [
			d.startYPt,
			d.paragraphXPt,
			d.availableWidthPt,
			d.maximumYPt,
			d.suppressSpaceBefore,
			d.noWrap ?? !1,
			b
		],
		[
			f.lineGrid.active,
			f.lineGrid.pitchPt,
			f.characterGrid.active,
			f.characterGrid.kind,
			f.characterGrid.deltaPt,
			f.rightIndentGrid.pitchPt,
			f.rightIndentGrid.paragraphAllowsAdjustment,
			f.physicalIndentLeftPt,
			f.physicalIndentRightPt,
			f.firstIndentPt,
			f.lineSpacing ? [
				f.lineSpacing.value,
				f.lineSpacing.rule,
				f.lineSpacing.explicit ?? null
			] : null,
			f.spaceBeforePt,
			f.spaceAfterPt,
			f.baseRtl,
			f.runDirectionUnauthored === !0,
			f.isJustified,
			f.stretchLastLine,
			f.tabStops.map((e) => [
				e.pos,
				e.alignment,
				e.leader
			]),
			f.hasRuby,
			f.hasEastAsianText,
			e.kinsokuKey(f.kinsoku),
			...f.lineEdgeRules ? [["line-edge-rules", e.kinsokuKey(f.lineEdgeRules)]] : [],
			...f.documentKinsoku ? [["textbox-document-rules", e.kinsokuKey(f.documentKinsoku)]] : [],
			f.defaultTabPt,
			f.overflowPunct !== !1,
			f.cjkClosingMarkHang ?? null,
			f.numberingMarkerGeometry ? JSON.stringify(f.numberingMarkerGeometry) : null,
			f.mathDefJc ?? null,
			...i ? [f.characterGrid.pitchPt] : []
		],
		x,
		[
			v ? p.pageIndex : null,
			v ? p.totalPages : null,
			v ? p.displayPageNumber ?? null : null,
			v ? p.pageNumberFormat ?? null : null,
			v ? p.currentDateMs ?? null : null,
			!y || !p.noteNumbers ? null : [...p.noteNumbers.entries()].sort(([e], [t]) => e.localeCompare(t)),
			y ? p.noteReferenceNumber ?? null : null,
			y && p.noteNumbering ? [
				p.noteNumbering.footnote.format,
				p.noteNumbering.footnote.start,
				p.noteNumbering.endnote.format,
				p.noteNumbering.endnote.start
			] : null,
			i ? null : p.pageWritingMode,
			p.inlineObjectRunLeadingAdmitted === !0,
			p.nativeUnitMinimumBandPt ?? null,
			p.nativeUnitMinimumBandPt === void 0 ? null : a?.text.acquireProjectableNativeUnits !== void 0,
			p.verticalCJK ?? null,
			i ? null : p.verticalPageFrame ?? null,
			Xl(Zl(p)),
			p.documentHasEastAsianText,
			p.characterSpacingControl ?? null,
			p.resolvedLocalFonts ? e.objectIdentity(p.resolvedLocalFonts) : null,
			e.fingerprintOrdinal(a?.text.fingerprint ?? null),
			e.fingerprintOrdinal(a?.images.fingerprint ?? null),
			e.fingerprintOrdinal(a?.math.fingerprint ?? null),
			e.fingerprintOrdinal(a?.verticalGlyphFingerprint ?? null),
			e.fingerprintOrdinal(o?.fingerprint ?? null),
			p.showTrackedChanges === !0,
			p.showTrackedChanges === !0 && p.revisionAuthorColor ? e.objectIdentity(p.revisionAuthorColor) : null,
			...i ? [p.positionExtendsLineBox !== !1] : []
		],
		i ? null : JSON.stringify(n.exclusions),
		i || !c ? null : JSON.stringify(n.anchorCollisions ?? []),
		i || !c ? null : n.paragraphAnchorReferenceDeltaPt ?? null,
		i || !c || !n.frozenAnchorFrames?.size ? null : JSON.stringify([...n.frozenAnchorFrames].sort(([e], [t]) => e.localeCompare(t))),
		r ? JSON.stringify(r) : null,
		i ? null : n.paragraphBorderEdges ? [n.paragraphBorderEdges.top, n.paragraphBorderEdges.bottom] : null,
		i ? null : n.trailingExtentPt ?? null,
		i ? null : n.containerShading ?? null,
		n.continuesFromPrevious ?? null,
		i ? null : n.sourceRangeStart ?? null,
		i ? null : s ? [
			s.page ? [
				s.page.xPt,
				s.page.yPt,
				s.page.widthPt,
				s.page.heightPt
			] : null,
			s.margin ? [
				s.margin.xPt,
				s.margin.yPt,
				s.margin.widthPt,
				s.margin.heightPt
			] : null,
			s.column ? [
				s.column.xPt,
				s.column.yPt,
				s.column.widthPt,
				s.column.heightPt
			] : null,
			s.pageParity
		] : null,
		i || !c ? null : JSON.stringify(n.anchorCellBounds ?? null),
		i || !l || !n.acquireCompleteStory ? null : e.objectIdentity(n.acquireCompleteStory),
		i || !l || !n.hostFlowPageTranslationPt ? null : [n.hostFlowPageTranslationPt.xPt, n.hostFlowPageTranslationPt.yPt],
		i || !l || n.hostPageFrames === void 0 ? null : JSON.stringify(n.hostPageFrames)
	])}`;
}
function nT(e, t, n, r) {
	return tT(e, t, n, r);
}
function rT(e, t) {
	return t.placement.wrap !== void 0 || t.exclusions.length > 0 || t.context.lineGrid.active || e.runs.some(ww);
}
function iT(e, t) {
	let n = t.startYPt + (t.suppressSpaceBefore ? 0 : e.requestedSpaceBeforePt), r = e.lines.map((e) => {
		let t = Object.freeze({
			...e,
			topYPt: n
		});
		return n += e.advancePt, t;
	});
	return Object.freeze({
		...e,
		lines: Object.freeze(r),
		contentStartYPt: r[0].topYPt,
		contentEndYPt: n,
		placement: Object.freeze({ ...t })
	});
}
function aT(e) {
	let t = e.src ? Object.freeze({ ...e.src }) : void 0;
	return "text" in e ? Object.freeze({
		...e,
		...t ? { src: t } : {},
		...e.shapedClusters ? { shapedClusters: Object.freeze(e.shapedClusters.map((e) => Object.freeze({
			...e,
			range: Object.freeze({ ...e.range })
		}))) } : {},
		...e.selectedFaceInkBounds ? { selectedFaceInkBounds: Object.freeze({ ...e.selectedFaceInkBounds }) } : {},
		...e.selectedFaceFontBox ? { selectedFaceFontBox: Object.freeze({ ...e.selectedFaceFontBox }) } : {},
		...e.ruby ? { ruby: Object.freeze({ ...e.ruby }) } : {},
		...e.border ? { border: Object.freeze({ ...e.border }) } : {},
		...e.revision ? { revision: Object.freeze({ ...e.revision }) } : {},
		...e.hyperlink ? { hyperlink: Object.freeze({ ...e.hyperlink }) } : {},
		...e.seaBreaks ? { seaBreaks: Object.freeze([...e.seaBreaks]) } : {}
	}) : "imagePath" in e ? Object.freeze({
		...e,
		...t ? { src: t } : {},
		...e.srcRect ? { srcRect: Object.freeze({ ...e.srcRect }) } : {},
		...e.duotone ? { duotone: Object.freeze({ ...e.duotone }) } : {}
	}) : "isTab" in e ? Object.freeze({
		...e,
		...t ? { src: t } : {},
		...e.ptab ? { ptab: Object.freeze({ ...e.ptab }) } : {}
	}) : Object.freeze({
		...e,
		...t ? { src: t } : {}
	});
}
function oT(e) {
	return Object.freeze({
		...e,
		layout: Object.freeze({
			...e.layout,
			segments: Object.freeze(e.layout.segments.map(aT)),
			...e.layout.consumedEnd ? { consumedEnd: Object.freeze({ ...e.layout.consumedEnd }) } : {}
		})
	});
}
function sT(e, t, n) {
	t.environment.closingPairRootSource && !QC(t) && (t = {
		...t,
		environment: {
			...t.environment,
			closingPairRootSource: void 0
		}
	});
	let r = t.environment.layoutServices ? $y(t.environment.layoutServices) : void 0, i = r ? nT(r, e, t, n) : void 0, a = i === void 0 ? void 0 : r.get(e, i);
	if (a) return a;
	r?.noteMiss();
	let o = !rT(e, t) && r ? tT(r, e, t, n, !0) : void 0, s = o === void 0 ? void 0 : r.getLineBreaking(e, o), c = Qw(t.exclusions), l = new Set(e.runs.flatMap((e) => ww(e) ? [e.anchorAcquisitionInput.occurrenceId] : []));
	for (let e of c) l.delete(e);
	let u = l.size, d = u > 0 && t.exclusions.length === 0 && t.placement.wrap === void 0, f = Object.freeze([]), p = $w(t.exclusions, f), m = n || t.continuesFromPrevious ? void 0 : ZC(e, t.context, t), h = m && !t.context.numberingMarkerGeometry ? {
		...t,
		context: {
			...t.context,
			numberingMarkerGeometry: m
		}
	} : t, g = m ? ew(e, h.context, h, d) : void 0, _ = (r, i) => dh(e, h.context, Yw(t, r, i), t.measurer, {
		...t.environment,
		paragraphMarkShapeInput: e.paragraphMarkShapeInput,
		...m?.lineBox && m.markerText ? { firstLineNumberingMarkerBox: m.lineBox } : {},
		...g ? { numberingFirstLine: g } : {},
		...m?.markerText && m.lineBox ? { markOnlyTextMarkerAscentPt: m.lineBox.ascentPt } : {},
		...e.numbering?.picBulletImagePath ? { firstLinePictureMarkerHeightPt: e.numbering.picBulletHeightPt ?? e.numberingMarkerShapeInput?.fontSizePt } : {}
	}, n), v = new Set(l.size === 0 ? [] : e.runs.flatMap((e) => {
		if (!ww(e)) return [];
		let t = e.anchorAcquisitionInput;
		return l.has(t.occurrenceId) && t.vertical.relativeFrom === "line" && !t.simplePosition.enabled && [
			"square",
			"tight",
			"through",
			"topAndBottom"
		].includes(t.wrap.kind) ? [t.occurrenceId] : [];
	})), y, b;
	try {
		let n = Ko({
			seedState: Zw(p),
			step: (n) => {
				let r = $w(t.exclusions, n?.ownedExclusions ?? f), i = s ? iT(s, t.placement) : _(r), a = b && b.size > 0 ? {
					...h,
					anchorLineExemptions: b
				} : h, o = mT(e, a, i, y);
				if (y === void 0 && v.size > 0) {
					let n = my(e), r = Xw(o, l), s = (e) => {
						let t = /* @__PURE__ */ new Map();
						return e.forEach((e, n) => {
							for (let r of e.placements) r.kind === "anchor-host" && r.anchorOccurrenceId && !t.has(r.anchorOccurrenceId) && t.set(r.anchorOccurrenceId, {
								bounds: e.bounds,
								firstLine: n === 0
							});
						}), t;
					}, c = s(o.lines), u = c, d = -Infinity, f = !0;
					if (r.length > 1) {
						let i = $w(t.exclusions, r);
						n.charge(i), u = s(pT(e, h, _(i, (e, t, n) => {
							f &&= !n;
							let r = Zi(Ri(Wi(e), Wi(t)));
							d = Math.max(d, r);
						})).lines);
					}
					let p = new Map(r.map((e) => [e.anchorOccurrenceId, e])), m = /* @__PURE__ */ new Map(), g = !1;
					for (let i of v) {
						let a = p.get(i), o;
						if (r.length > 1 && (!a || f && a.bounds.yPt > d && a.polygon.every((e) => e.yPt > d))) o = u.get(i), g = !0;
						else {
							let a = r.filter((e) => e.anchorOccurrenceId !== i);
							if (g ||= a.length > 0, a.length === 0) o = c.get(i);
							else {
								let r = $w(t.exclusions, a);
								n.charge(r), o = s(pT(e, h, _(r)).lines).get(i);
							}
						}
						o && m.set(i, o);
					}
					y = m, g && (o = mT(e, a, i, y));
				}
				let c = Xw(o, l);
				b === void 0 && (b = qw(e, t, o, c));
				let u = Zw($w(t.exclusions, c));
				if (Zw(o.exclusions) !== u) throw Error("Paragraph retained exclusions differ from the measured exclusion authority");
				return Object.freeze({
					measured: i,
					layout: o,
					ownedExclusions: c,
					state: u
				});
			},
			stateOf: (e) => e.state,
			limit: 16
		}).value, a = s ? n.measured : Object.freeze({
			...n.measured,
			lines: Object.freeze(n.measured.lines.map(oT)),
			placement: Object.freeze({ ...n.measured.placement })
		}), c = Object.freeze({
			measured: a,
			layout: n.layout
		});
		return i !== void 0 && r.set(e, i, c), o !== void 0 && !s && !a.markOnly && r.setLineBreaking(e, o, a), c;
	} catch (e) {
		throw e instanceof Go ? new Ww(e.reason, e.states, u) : e;
	}
}
function cT(e, t) {
	return sT(e, t).layout;
}
function lT(e) {
	let t = 0;
	for (let n of e.members) for (let e of n.fragment.lines) for (let n of e.placements) n.kind === "text" && (t = Math.max(t, -(n.positionPt ?? 0)));
	return t;
}
var uT = /* @__PURE__ */ new WeakMap();
function dT(e) {
	return e === void 0 ? null : e instanceof Date ? { date: e.toISOString() } : e instanceof Set ? { set: [...e].map(dT).sort((e, t) => JSON.stringify(e).localeCompare(JSON.stringify(t))) } : e instanceof Map ? { map: [...e.entries()].map(([e, t]) => [dT(e), dT(t)]).sort((e, t) => JSON.stringify(e[0]).localeCompare(JSON.stringify(t[0]))) } : Array.isArray(e) ? e.map(dT) : e && typeof e == "object" ? Object.fromEntries(Object.entries(e).map(([e, t]) => [e, dT(t)])) : e;
}
function fT(e, t) {
	if (t.contexts.length !== e.members.length || t.inputs.length !== e.members.length || t.borderEdges.length !== e.members.length || t.borderExtentsPt.length !== e.members.length) throw Error("Frame acquisition metadata must align with every group member");
	if (!Number.isFinite(t.maximumWidthPt) || t.maximumWidthPt < 0) throw RangeError("Frame maximumWidthPt must be finite and non-negative");
	let n = uT.get(t.acquisitionSession);
	n || (n = /* @__PURE__ */ new Map(), uT.set(t.acquisitionSession, n));
	let r = t.story ?? {
		story: "body",
		storyInstance: "body"
	}, i = r.story === "body" ? "body-frame" : `${r.story}:${r.storyInstance}:frame`, a = Oe("w:frame-acquisition", [
		r.story,
		r.storyInstance,
		e.id,
		t.placementSignature,
		t.maximumWidthPt,
		t.environment.pageIndex,
		t.environment.totalPages,
		t.environment.displayPageNumber ?? null,
		t.environment.pageNumberFormat ?? null,
		t.environment.currentDateMs ?? null,
		t.environment.documentHasEastAsianText,
		t.environment.layoutServices?.text.fingerprint ?? null,
		t.environment.layoutServices?.images.fingerprint ?? null,
		t.environment.layoutServices?.math.fingerprint ?? null,
		t.environment.layoutServices?.verticalGlyphFingerprint ?? null,
		dT(t.contexts),
		dT(t.inputs),
		dT(t.borderEdges),
		dT(t.borderExtentsPt),
		t.containerShading ?? null,
		dT(t.anchorFrames)
	]), o = n.get(a);
	if (o) return o;
	let s = e.framePr, c = s.w == null ? Math.max(0, ...e.members.map((e, n) => __(e, t.contexts[n], t.maximumWidthPt, t.measurer, t.environment, ZC(t.inputs[n], t.contexts[n], t)))) : Math.max(0, s.w), l = Math.max(1, c), u = (() => {
		let n = LS(`${i}:${e.id}`), a = 0, o = null, s = 0, c = 0, u = [];
		return e.members.forEach((d, f) => {
			let p = t.contexts[f], m = Math.max(wS(o, d, s, p.spaceBeforePt), c), h = {
				startYPt: a + m,
				paragraphXPt: 0,
				availableWidthPt: l,
				maximumYPt: Infinity,
				suppressSpaceBefore: !0
			}, g = t.borderExtentsPt[f] ?? 0, _ = {
				story: r.story,
				storyInstance: r.storyInstance,
				path: [e.sourceIndices[f]]
			}, { measured: v, layout: y } = sT(t.inputs[f], {
				id: `${i}:${e.id}:${f}`,
				source: _,
				flowDomainId: `${i}:${e.id}`,
				ordinaryFlow: !1,
				context: p,
				placement: h,
				measurer: t.measurer,
				environment: {
					...t.environment,
					positionExtendsLineBox: Dv(e.framePr.dropCap)
				},
				exclusions: n.exclusions,
				anchorCollisions: n.collisions,
				containerShading: t.containerShading,
				paragraphBorderEdges: t.borderEdges[f],
				trailingExtentPt: Math.max(p.spaceAfterPt, g),
				anchorFrames: t.anchorFrames
			});
			n = BS(n, y), u.push({
				paragraph: d,
				fragment: y,
				source: _
			}), a = v.contentEndYPt, o = d, s = v.requestedSpaceAfterPt, c = g;
		}), {
			heightPt: Math.max(0, a + Math.max(s, c)),
			members: u
		};
	})(), d = t.place(c, u.heightPt), f = Object.freeze(u.members.map((e) => {
		let t = gb(e.fragment, {
			xPt: d.bounds.xPt,
			yPt: d.bounds.yPt
		}), n = FC(s.hRule === "exact" && s.h != null ? {
			...t,
			clipBounds: d.bounds
		} : t), r = Object.freeze({
			...n,
			advancePt: 0
		});
		return Object.freeze({
			...e,
			fragment: r
		});
	})), p = Object.freeze({
		box: Object.freeze({
			bounds: d.bounds,
			exclusionBounds: d.exclusionBounds,
			exclusionId: `frame:${e.id}`
		}),
		members: f
	});
	return n.set(a, p), p;
}
function pT(e, t, n) {
	let r = t.continuesFromPrevious ? {
		...t.context,
		firstIndentPt: 0
	} : t.context, i = t.placement.paragraphXPt + r.physicalIndentLeftPt, a = H_(r, t.placement.availableWidthPt), o = t.placement.availableWidthPt - r.physicalIndentLeftPt - r.physicalIndentRightPt - a, s = fw(e, n, t.environment.showTrackedChanges), c = t.continuesFromPrevious ? void 0 : ZC(e, r, t), l = hw(n, e, i, o, t.source, t.id, r, s, c, t.environment.layoutServices?.text, t.environment.verticalGlyphMeasurement, t.environment.verticalPageFrame, Zl(t.environment), t.environment.paragraphMarkShapeInput, Um(t.environment.verticalPageFrame, t.environment.pageWritingMode));
	return t.sourceRangeStart !== void 0 && (l = vw(l, t.sourceRangeStart)), l = gw(l, t.placement.paragraphXPt, t.placement.availableWidthPt, r.baseRtl, r.tabStops), c && n.markOnly && l.length === 0 && (c.markerText !== "" || e.numbering?.picBulletImagePath) && (l = [yw(n, e, i, o, r)]), {
		lines: l,
		planningContext: r,
		paragraphXPt: i,
		availableWidthPt: o,
		occurrences: s,
		numberingPlan: c
	};
}
function mT(e, t, n, r) {
	let i = pT(e, t, n), { lines: a } = i, { paragraphXPt: o, availableWidthPt: s, occurrences: c, numberingPlan: l } = i, u = [], d = [], f = [], p = [], m = [], h = [], g = [], _ = e.runs.map((e, t) => e.type === "break" ? {
		kind: "break",
		breakKind: e.breakType,
		offset: c.runStarts[t] ?? 0
	} : void 0).filter((e) => e !== void 0), v = /* @__PURE__ */ new Map();
	e.runs.forEach((e, t) => {
		if (!ww(e)) return;
		let n = v.get(e.anchorAcquisitionInput.occurrenceId) ?? [];
		n.push({
			run: e,
			runIndex: t
		}), v.set(e.anchorAcquisitionInput.occurrenceId, n);
	});
	let y = new Set(v.keys());
	for (let [i, o] of v) {
		let s = Nw(i, o, a, e, t, n.contentEndYPt - t.placement.startYPt, t.exclusions, m, t.anchorCollisions ?? [], h, y, t.placement.startYPt + (t.placement.suppressSpaceBefore ? 0 : n.requestedSpaceBeforePt), r?.get(i));
		s && (p.push(s.result), s.cellContainmentBounds && g.push(s.cellContainmentBounds), s.drawing && (d.push(s.drawing), f.push(...s.textBoxes), s.exclusion && m.push(s.exclusion), s.collision && h.push(s.collision), a[s.hostLineIndex] && (a = a.map((e, t) => t === s.hostLineIndex ? {
			...e,
			placements: [...e.placements, {
				kind: "drawing",
				range: s.hostRange,
				drawingId: s.drawing.id,
				bounds: s.drawing.inkBounds,
				advancePt: 0
			}]
		} : e))));
	}
	let b = t.continuesFromPrevious ? void 0 : n.lines[0]?.layout.numberingFirstLine?.leadingEdgePx ?? n.markNumberingLeadingEdgePt;
	if (l && a[0]) {
		let n = nw(l, e, t.context, o, s, a[0], b);
		n.length > 0 && (a = [{
			...a[0],
			placements: [...n, ...a[0].placements]
		}, ...a.slice(1)]);
	}
	if (e.runs.forEach((e, n) => {
		let r = LC(t.source, n);
		if (e.type === "unavailableDrawing" && e.anchorAcquisitionInput === void 0) {
			let i = BC(t.source, n), o = a.flatMap((e) => e.placements).find((e) => e.kind === "drawing" && e.drawingId === i);
			o?.kind === "drawing" && d.push({
				kind: "drawing",
				id: i,
				source: r,
				flowDomainId: t.flowDomainId,
				flowBounds: o.bounds,
				inkBounds: o.bounds,
				advancePt: 0,
				ordinaryFlow: !1,
				commands: Object.freeze([{ kind: "noop" }]),
				diagnostics: Object.freeze([VC(e.resourceKind, r)])
			});
		}
		if (e.type === "image" && u.push({
			kind: "image",
			resourceKey: Ee(r, e.imagePath),
			intrinsicSize: {
				widthPt: e.widthPt,
				heightPt: e.heightPt
			}
		}), e.type === "chart" && u.push({
			kind: "chart",
			resourceKey: zC(r),
			intrinsicSize: {
				widthPt: e.widthPt,
				heightPt: e.heightPt
			}
		}), e.type === "math" && u.push({
			kind: "math",
			resourceKey: e.resourceKey ?? Oe("math-resource", r),
			intrinsicSize: {
				widthPt: a.flatMap((e) => e.placements).find((e) => e.kind === "resource" && e.resourceKind === "math")?.bounds?.widthPt ?? 0,
				heightPt: e.fontSize
			}
		}), (e.type === "image" || e.type === "chart") && !t.continuesFromPrevious) {
			let r = Cw(e, t, n);
			if (r) {
				d.push(r);
				let e = a[0];
				e && (a = [{
					...e,
					placements: [...e.placements, {
						kind: "drawing",
						range: {
							start: c.runStarts[n] ?? 0,
							end: (c.runStarts[n] ?? 0) + (c.runLengths[n] ?? 1)
						},
						drawingId: r.id,
						bounds: r.inkBounds,
						advancePt: 0
					}]
				}, ...a.slice(1)]);
			}
		}
		if (e.type === "shape" && !e.anchorAcquisitionInput && !t.continuesFromPrevious) {
			let i = `${t.id}:drawing:${n}`, o = e.inline === !0 ? a.flatMap((e) => e.placements).find((e) => e.kind === "drawing" && e.drawingId === i) : void 0;
			if (e.inline === !0 && !o) throw Error(`Inline shape ${i} has no retained line placement`);
			let s = o?.bounds ?? xw(e, t), l = `${t.id}:textbox:${n}`, u = t.hostFlowPageTranslationPt, p = t.hostPageFrames === void 0 ? t.anchorFrames?.page && t.anchorFrames.margin ? {
				page: t.anchorFrames.page,
				margin: t.anchorFrames.margin
			} : null : t.hostPageFrames, m = u && p ? HS(p, Ob(u.xPt, u.yPt)) : null, h = Uw(e, s, {
				id: l,
				source: r,
				flowDomainId: t.flowDomainId,
				context: t.context,
				measurer: t.measurer,
				environment: t.environment,
				input: e.textBoxInput,
				acquireCompleteStory: t.acquireCompleteStory,
				...m ? { pageFrames: m } : {}
			}), g = Sw(e, e.inline === !0 ? s : h?.flowBounds ?? s, t, n, e.inline === !0);
			h && (f.push(h), g = {
				...g,
				textBoxIds: [l]
			}), d.push(g);
			let _ = e.inline === !0 ? void 0 : a[0];
			_ && (a = [{
				..._,
				placements: [..._.placements, {
					kind: "drawing",
					range: {
						start: c.runStarts[n] ?? 0,
						end: (c.runStarts[n] ?? 0) + (c.runLengths[n] ?? 1)
					},
					drawingId: g.id,
					bounds: g.inkBounds,
					advancePt: 0
				}]
			}, ...a.slice(1)]);
		}
	}), e.numbering?.picBulletImagePath && !t.continuesFromPrevious && u.push({
		kind: "picture-bullet",
		resourceKey: Ee(t.source, e.numbering.picBulletImagePath),
		intrinsicSize: {
			widthPt: e.numbering.picBulletWidthPt ?? e.numberingMarkerShapeInput?.fontSizePt ?? 0,
			heightPt: e.numbering.picBulletHeightPt ?? e.numberingMarkerShapeInput?.fontSizePt ?? 0
		}
	}), e.numbering?.picBulletImagePath && a[0] && !t.continuesFromPrevious) {
		if (!l) throw Error("Picture-bullet acquisition requires resolved marker font geometry");
		let n = e.numbering.picBulletWidthPt ?? l.markerWidthPt, r = e.numbering.picBulletHeightPt ?? e.numberingMarkerShapeInput?.fontSizePt;
		if (r === void 0) throw Error("Picture-bullet acquisition requires resolved marker height");
		let i = _g({
			baseRtl: t.context.baseRtl,
			alignedLeadingEdgePt: tw(l, t.context, o, s, a[0], b === void 0 ? void 0 : {
				leadingEdgePx: b,
				authoredFirstIndentPt: e.indentFirst
			}),
			authoredFirstIndentPt: e.indentFirst,
			markerShiftPt: l.markerShiftPt,
			markerWidthPt: n
		});
		a = [{
			...a[0],
			placements: [{
				kind: "resource",
				resourceKind: "picture-bullet",
				range: {
					start: -1,
					end: 0
				},
				resourceKey: Ee(t.source, e.numbering.picBulletImagePath),
				bounds: {
					xPt: i,
					yPt: a[0].baselinePt - r,
					widthPt: n,
					heightPt: r
				},
				advancePt: 0
			}, ...a[0].placements]
		}, ...a.slice(1)];
	}
	a = iw(a, e.shading, t.containerShading);
	let x = n.contentEndYPt - n.contentStartYPt, S = t.paragraphBorderEdges ?? {
		top: "top",
		bottom: "bottom"
	}, C = ow(e, a, o, s, n.contentStartYPt, x, S), w = e.borders ? [
		...S.top === "none" ? [] : [[S.top, e.borders[S.top]]],
		["right", e.borders.right],
		...S.bottom === "none" ? [] : [["bottom", e.borders.bottom]],
		["left", e.borders.left]
	] : [], T = e.borders ? w.flatMap(([e, t]) => {
		if (!aw(t)) return [];
		let n = e === "top" || e === "between" || e === "bottom", r = e === "right" || e === "bottom", i = n ? C.yPt + (r ? C.heightPt : 0) : C.xPt + (r ? C.widthPt : 0);
		return [{
			edge: e,
			from: n ? {
				xPt: C.xPt,
				yPt: i
			} : {
				xPt: i,
				yPt: C.yPt
			},
			to: n ? {
				xPt: C.xPt + C.widthPt,
				yPt: i
			} : {
				xPt: i,
				yPt: C.yPt + C.heightPt
			},
			color: t.color ? `#${t.color}` : "#000000",
			widthPt: t.width,
			...Cb(t.style, t.width)
		}];
	}) : [], E = t.trailingExtentPt ?? n.requestedSpaceAfterPt, D = wb(g);
	return FC({
		kind: "paragraph",
		id: t.id,
		source: t.source,
		...e.paragraphId === void 0 ? {} : { paragraphId: e.paragraphId },
		flowDomainId: t.flowDomainId,
		ordinaryFlow: t.ordinaryFlow,
		...e.styleId === void 0 ? {} : { styleId: e.styleId },
		...!t.continuesFromPrevious && e.bookmarks?.length ? { bookmarkStarts: e.bookmarks } : {},
		flowBounds: {
			xPt: t.placement.paragraphXPt,
			yPt: t.placement.startYPt,
			widthPt: t.placement.availableWidthPt,
			heightPt: n.contentEndYPt - t.placement.startYPt + E
		},
		inkBounds: { ...e.shading || e.borders ? C : {
			xPt: o,
			yPt: n.contentStartYPt,
			widthPt: Math.max(0, ...a.map((e) => e.bounds.widthPt)),
			heightPt: x
		} },
		spacing: {
			beforePt: t.placement.suppressSpaceBefore ? 0 : n.requestedSpaceBeforePt,
			afterPt: E
		},
		contextualSpacing: e.contextualSpacing ?? !1,
		lines: a,
		borders: T,
		shading: e.shading ? { color: `#${e.shading}` } : void 0,
		resources: u,
		drawings: d,
		textBoxes: f,
		events: _,
		exclusions: $w(t.exclusions, m),
		...D ? { cellContainmentBounds: D } : {},
		anchorCollisions: eT(t.anchorCollisions ?? [], h),
		...p.length ? { anchorFrames: p } : {},
		paragraphMark: n.markOnly ? {
			...n.markWrapBounds ? { wrapBounds: n.markWrapBounds } : {},
			...(n.markPageEdgeOverhangPt ?? 0) > 0 ? { pageEdgeOverhangPt: n.markPageEdgeOverhangPt } : {},
			hidden: e.markVanish === !0,
			bounds: {
				xPt: o,
				yPt: n.contentStartYPt,
				widthPt: 0,
				heightPt: x
			}
		} : void 0
	});
}
var hT = (e, t) => ob(e, {
	xPt: 0,
	yPt: t
}), gT = (e, t) => Q(e, {
	xPt: 0,
	yPt: t
}), _T = (e, t) => ub(e, {
	xPt: 0,
	yPt: t
}), vT = (e, t) => fb(e, {
	xPt: 0,
	yPt: t
}), yT = (e, t) => pb(e, {
	xPt: 0,
	yPt: t
}), bT = (e, t) => gb(e, {
	xPt: 0,
	yPt: t
}), xT = (e, t) => vb(e, {
	xPt: 0,
	yPt: t
});
function ST(e, t, n, r) {
	if (!e.shading && e.borders.length === 0) return null;
	let i = t[0], a = t.at(-1);
	if (!i || !a) return {
		box: gT(e.inkBounds, n),
		borders: []
	};
	let o = e.inkBounds.yPt, s = o + e.inkBounds.heightPt, c = r.continuesFromPrevious ? Math.max(o, i.bounds.yPt) : o, l = r.continuesOnNext ? Math.min(s, a.bounds.yPt + a.advancePt) : s, u = {
		xPt: e.inkBounds.xPt,
		yPt: c + n,
		widthPt: e.inkBounds.widthPt,
		heightPt: Math.max(0, l - c)
	}, d = u.xPt, f = d + u.widthPt, p = u.yPt, m = p + u.heightPt;
	return {
		box: u,
		borders: e.borders.flatMap((e) => (e.edge === "top" || e.edge === "between") && r.continuesFromPrevious || e.edge === "bottom" && r.continuesOnNext ? [] : e.edge === "top" || e.edge === "between" ? [{
			...e,
			from: {
				xPt: d,
				yPt: p
			},
			to: {
				xPt: f,
				yPt: p
			}
		}] : e.edge === "bottom" ? [{
			...e,
			from: {
				xPt: d,
				yPt: m
			},
			to: {
				xPt: f,
				yPt: m
			}
		}] : e.edge === "left" ? [{
			...e,
			from: {
				xPt: d,
				yPt: p
			},
			to: {
				xPt: d,
				yPt: m
			}
		}] : e.edge === "right" ? [{
			...e,
			from: {
				xPt: f,
				yPt: p
			},
			to: {
				xPt: f,
				yPt: m
			}
		}] : [{
			...e,
			from: hT(e.from, n),
			to: hT(e.to, n)
		}])
	};
}
function CT(e, t, n = `${e.id}:${t.lineStart}-${t.lineEnd}`) {
	let r = e.lines.slice(t.lineStart, t.lineEnd), i = r[0], a = r.at(-1), o = t.continuesFromPrevious && t.lineStart > 0 && i ? e.flowBounds.yPt - i.bounds.yPt : 0, s = o === 0 ? r : r.map((e) => yT(e, o)), c = s[0], l = s.at(-1), u = c && l ? {
		xPt: Math.min(...s.map((e) => e.bounds.xPt)),
		yPt: c.bounds.yPt,
		widthPt: Math.max(...s.map((e) => e.bounds.xPt + e.bounds.widthPt)) - Math.min(...s.map((e) => e.bounds.xPt)),
		heightPt: l.bounds.yPt + l.bounds.heightPt - c.bounds.yPt
	} : e.inkBounds, d = ST(e, r, o, t), f = new Set(r.flatMap((e) => e.placements.flatMap((e) => e.kind === "drawing" ? [e.drawingId] : []))), p = e.drawings.filter((e) => f.has(e.id)).map((e) => e.anchorLayer?.verticalOwnership === "page" ? e : _T(e, o)), m = wb(p.filter((e) => e.anchorLayer?.cellContainment === !0).map((e) => e.flowBounds)), h = new Set(e.drawings.flatMap((e) => {
		if (e.anchorLayer?.verticalOwnership !== "host") return [];
		let t = e.anchorLayer.acquisitionOccurrenceId ?? e.anchorLayer.occurrenceId;
		return t === void 0 ? [] : [t];
	})), g = new Set(p.flatMap((e) => {
		if (e.anchorLayer?.verticalOwnership !== "host") return [];
		let t = e.anchorLayer.acquisitionOccurrenceId ?? e.anchorLayer.occurrenceId;
		return t === void 0 ? [] : [t];
	})), _ = new Set(r.flatMap((e) => e.placements.flatMap((e) => e.kind === "resource" ? [e.resourceKey] : [])));
	for (let e of p) for (let t of e.commands) t.kind === "resource" && _.add(t.resourceKey);
	let v = new Set(p.flatMap((e) => [e.id.replace(":drawing:", ":textbox:"), ...e.textBoxIds ?? []])), y = new Set(p.filter((e) => e.anchorLayer?.verticalOwnership === "page" || e.orientation === "upright-physical").flatMap((e) => e.textBoxIds ?? [])), b = new Set(p.map((e) => Oe("source-occurrence", e.source))), x = i?.range.start, S = a?.range.end, { bookmarkStarts: C, ...w } = e;
	return IC({
		...w,
		kind: "paragraph",
		id: n,
		...!t.continuesFromPrevious && C?.length ? { bookmarkStarts: C } : {},
		lines: e.lines,
		flowBounds: {
			...e.flowBounds,
			yPt: e.flowBounds.yPt
		},
		...e.clipBounds ? { clipBounds: gT(e.clipBounds, o) } : {},
		spacing: {
			beforePt: t.continuesFromPrevious ? 0 : e.spacing.beforePt,
			afterPt: t.continuesOnNext ? 0 : e.spacing.afterPt
		},
		inkBounds: d?.box ?? u,
		borders: d?.borders ?? e.borders.map((e) => ({
			...e,
			from: hT(e.from, o),
			to: hT(e.to, o)
		})),
		resources: e.resources.filter((e) => _.has(e.resourceKey)),
		drawings: p,
		cellContainmentBounds: m ?? void 0,
		textBoxes: e.textBoxes.filter((e) => v.has(e.id) || b.has(Oe("source-occurrence", e.source))).map((e) => y.has(e.id) ? e : xT(e, o)),
		events: x === void 0 || S === void 0 ? [] : e.events.filter((e) => e.offset >= x && (e.offset < S || !t.continuesOnNext && e.offset === S)),
		exclusions: e.exclusions.filter((e) => e.verticalOwnership === "page" || e.anchorOccurrenceId === void 0 || !h.has(e.anchorOccurrenceId) || g.has(e.anchorOccurrenceId)).map((e) => ({
			...e,
			bounds: e.verticalOwnership === "page" ? e.bounds : gT(e.bounds, o),
			polygon: e.verticalOwnership === "page" ? e.polygon : e.polygon.map((e) => hT(e, o))
		})),
		anchorCollisions: (e.anchorCollisions ?? []).filter((e) => e.verticalOwnership === "page" || !h.has(e.occurrenceId) || g.has(e.occurrenceId)).map((e) => ({
			...e,
			bounds: e.verticalOwnership === "page" ? e.bounds : gT(e.bounds, o)
		})),
		...t.continuesOnNext ? { paragraphMark: void 0 } : e.paragraphMark ? { paragraphMark: {
			...e.paragraphMark,
			bounds: gT(e.paragraphMark.bounds, o),
			...e.paragraphMark.wrapBounds ? { wrapBounds: gT(e.paragraphMark.wrapBounds, o) } : {}
		} } : {},
		continuation: t
	}, e, s);
}
function wT(e) {
	for (let t = e.length - 1; t >= 0; t--) {
		let n = e[t];
		if (n.kind !== "anchor-host") {
			if (n.kind !== "text") return !1;
			if (n.text.length > 0) return n.text.endsWith(" ");
		}
	}
	return !1;
}
function TT(e, t) {
	let n = 0;
	for (let r = e.length - 1; r >= 0; --r) {
		let i = e[r];
		if (i?.kind === "anchor-host") continue;
		if (i?.kind !== "text") break;
		let a = t(i.text);
		if (n += i.clusters.filter((e) => e.range.start >= i.range.start + a).reduce((e, t) => e + t.advancePt, 0), a > 0) break;
		/^ +$/u.test(i.text) && (n += i.leadingSeamPairPt ?? 0);
	}
	return n;
}
function ET(e, t, n = /* @__PURE__ */ new Set()) {
	let r = /* @__PURE__ */ new Map();
	if (!e) return r;
	let i = new Set(e.map((e) => e.id)), a = 0;
	return t.forEach((e) => {
		i.has(e) && !r.has(e) && r.set(e, n.has(e) ? 0 : ++a);
	}), r;
}
function DT(e) {
	let t = /* @__PURE__ */ new Map();
	if (!e) return t;
	for (let n of e) t.set(n.id, n);
	return t;
}
function OT(e) {
	let t = /* @__PURE__ */ new Map(), n = /* @__PURE__ */ new Map(), r = (e, i) => {
		for (let a of e) if (a.type === "paragraph" && "runs" in a) for (let e of a.runs) e.type === "text" && e.noteRef?.kind === "footnote" && e.noteRef.id.length > 0 && (t.set(e.noteRef.id, (t.get(e.noteRef.id) ?? 0) + 1), n.set(e.noteRef.id, i));
		else if (a.type === "table" && "rows" in a) for (let e of a.rows) for (let t of e.cells) r(t.content, i);
	};
	return e.forEach((e, t) => r([e], t)), new Map([...n].filter(([e]) => (t.get(e) ?? 0) > 1));
}
function kT(e, t, n = !1) {
	let r = [], i = /* @__PURE__ */ new Set();
	for (let a of e) if (a.type === "paragraph" && "runs" in a) for (let e of a.runs) e.type !== "text" || e.noteRef?.kind !== t || e.noteRef.id.length === 0 || n && e.noteRef.customMarkFollows !== !0 || i.has(e.noteRef.id) || (i.add(e.noteRef.id), r.push(e.noteRef.id));
	else if (a.type === "table" && "rows" in a) for (let e of a.rows) for (let a of e.cells) for (let e of kT(a.content, t, n)) i.has(e) || (i.add(e), r.push(e));
	return Object.freeze(r);
}
function AT(e, t) {
	return Object.freeze([...new Set(e.flatMap((e) => e.placements.flatMap((e) => (e.kind === "text" || e.kind === "anchor-host") && e.noteReference?.kind === t ? [e.noteReference.id] : [])))]);
}
function jT(e, t) {
	return e.rows.flatMap((e) => e.cells.flatMap((e) => e.blocks.flatMap((e) => MT(e.layout, t))));
}
function MT(e, t) {
	let n = e.kind === "paragraph" ? AT(e.lines, t) : jT(e, t);
	return Object.freeze([...new Set(n)]);
}
function NT(e) {
	return AT(e, "footnote");
}
function PT(e) {
	return MT(e, "footnote");
}
function FT(e) {
	return MT(e, "endnote");
}
function IT(e) {
	let t = e.__typographyAcquisition;
	if (t !== void 0) return Z({
		sourceText: "text" in e ? e.text : e.fallbackText,
		...t
	}, "DOCX run typography acquisition input");
}
function LT(e) {
	let t = e.__paragraphTypographyAcquisition;
	if (t !== void 0) return Z(t, "DOCX paragraph typography acquisition input");
}
function RT(e, t) {
	let n = t[0].logicalTotalRows, r = 0;
	for (let i of t) {
		if (i.logicalTotalRows !== n || !Number.isInteger(i.rowCount) || i.rowCount < 0 || i.logicalRowOffset !== r) throw Error(`Parser-owned adjacent table sequence ${e} is inconsistent`);
		r += i.rowCount;
	}
	if (r !== n) throw Error(`Parser-owned adjacent table sequence ${e} is incomplete`);
}
function* zT(e) {
	let t = null, n = [];
	function* r() {
		n.length > 0 && RT(t, n), n.length === 1 ? yield Object.freeze({
			kind: "body-element",
			element: n[0].element
		}) : n.length > 1 && (yield Object.freeze({
			kind: "adjacent-table-group",
			logicalSequenceId: t,
			tables: Object.freeze(n.map((e) => e.element))
		})), t = null, n = [];
	}
	for (let { element: i, table: a } of e) {
		if (i.type === "table" && a !== null) {
			n.length > 0 && t !== a.logicalSequenceId && (yield* r()), t = a.logicalSequenceId, n.push(Object.freeze({
				element: i,
				logicalRowOffset: a.logicalRowOffset,
				logicalTotalRows: a.logicalTotalRows,
				rowCount: a.rowCount
			}));
			continue;
		}
		yield* r(), yield Object.freeze({
			kind: "body-element",
			element: i
		});
	}
	yield* r();
}
function BT(e) {
	return !(e.runs ?? []).some((e) => e.type === "text" ? e.text.length > 0 : !0);
}
function VT(e) {
	return e === "start" || e === "end" || e === "center";
}
var HT = /* @__PURE__ */ new WeakMap();
function UT(e) {
	return HT.get(e) ?? [];
}
function WT(e) {
	let t = UT(e);
	if (t.length === 0) return e.runs;
	let n = [], r = 0;
	for (let i = 0; i <= e.runs.length; i += 1) {
		for (; t[r]?.publicRunIndex === i;) n.push(t[r].run), r += 1;
		i < e.runs.length && n.push(e.runs[i]);
	}
	return n;
}
function GT(e) {
	return UT(e).length > 0;
}
function KT(e) {
	return e.settings ?? {};
}
function qT(e) {
	let t = e.__documentTypographySettings?.normalStyleFontSizePt;
	return Z({ normalStyleFontSizePt: typeof t == "number" && Number.isFinite(t) && t > 0 ? t : 10 }, "DOCX document typography settings input");
}
function JT(e) {
	let t = e.__pageLayoutSettings;
	return Z({
		mirrorMargins: t?.mirrorMargins === !0,
		gutterAtTop: t?.gutterAtTop === !0,
		bookFoldPrinting: t?.bookFoldPrinting === !0,
		bookFoldRevPrinting: t?.bookFoldRevPrinting === !0,
		printTwoOnOne: t?.printTwoOnOne === !0
	}, "DOCX page layout settings input");
}
function YT(e) {
	if (e === void 0) return "default";
	if (e === "short" || e === "full" || e === "none") return e;
	throw Error("Unsupported note separator");
}
function XT(e) {
	return typeof e == "object" && !!e && !Array.isArray(e);
}
function ZT(e) {
	if (!XT(e) || e.rule !== void 0 && !XT(e.rule)) throw Error("Unsupported reserved note separator story");
	let t = e.rule?.mark;
	if (t !== void 0 && t !== "short" && t !== "full") throw Error("Unsupported reserved note separator story");
}
function QT(e, t) {
	if (e === void 0) return {};
	if (!XT(e)) throw Error("Unsupported reserved note separator story");
	let n = (e) => {
		ZT(e);
		let n = e.paragraph;
		if (!XT(n) || !XT(n.paragraph)) return e;
		let r = n.paragraph;
		if (r.beforeAutospacing !== !0 && r.afterAutospacing !== !0) return e;
		let i = ES(r, r.defaultFontSize ?? 10, t);
		return i.spaceBefore === r.spaceBefore && i.spaceAfter === r.spaceAfter ? e : {
			...e,
			paragraph: {
				...n,
				paragraph: {
					...r,
					...i
				}
			}
		};
	}, r = (e) => {
		if (e === void 0) return e;
		if (!XT(e)) throw Error("Unsupported reserved note separator story");
		let t = n(e.separator), r = n(e.continuationSeparator), i = n(e.continuationNotice);
		return t === e.separator && r === e.continuationSeparator && i === e.continuationNotice ? e : {
			...e,
			separator: t,
			continuationSeparator: r,
			continuationNotice: i
		};
	}, i = r(e.footnote), a = r(e.endnote);
	return { reservedSeparators: i === e.footnote && a === e.endnote ? e : {
		...e,
		footnote: i,
		endnote: a
	} };
}
function $T(e, t) {
	let n = (e, n) => {
		if (e !== void 0) {
			if (n !== "short" && n !== "full" && n !== "none") throw Error("Unsupported note separator story paragraph");
			return e.beforeAutospacing !== !0 && e.afterAutospacing !== !0 ? e : {
				...e,
				...ES(e, e.defaultFontSize ?? 10, t)
			};
		}
	}, r = n(e?.footnoteSeparatorParagraph, e?.footnoteSeparator), i = n(e?.footnoteContinuationSeparatorParagraph, e?.footnoteContinuationSeparator), a = n(e?.endnoteSeparatorParagraph, e?.endnoteSeparator), o = n(e?.endnoteContinuationSeparatorParagraph, e?.endnoteContinuationSeparator);
	return {
		...a || o ? { endnoteSeparatorParagraphs: {
			...a ? { separator: a } : {},
			...o ? { continuationSeparator: o } : {}
		} } : {},
		...r || i ? { footnoteSeparatorParagraphs: {
			...r ? { separator: r } : {},
			...i ? { continuationSeparator: i } : {}
		} } : {}
	};
}
function eE(e, t) {
	return {
		format: typeof e == "string" && e.length > 0 ? e : "decimal",
		start: typeof t == "number" && Number.isSafeInteger(t) ? t : 1
	};
}
function tE(e) {
	let t = e.__noteLayoutSettings;
	return Z({
		footnotePosition: t?.footnotePosition ?? "pageBottom",
		endnotePosition: t?.endnotePosition ?? "docEnd",
		footnoteNumbering: eE(t?.footnoteNumberFormat, t?.footnoteNumberStart),
		endnoteNumbering: eE(t?.endnoteNumberFormat, t?.endnoteNumberStart),
		footnoteSeparator: YT(t?.footnoteSeparator),
		endnoteSeparator: YT(t?.endnoteSeparator),
		endnoteContinuationSeparator: YT(t?.endnoteContinuationSeparator),
		footnoteContinuationSeparator: YT(t?.footnoteContinuationSeparator),
		...$T(t, e.settings?.doNotUseHtmlParagraphAutoSpacing === !0),
		...QT(t?.reservedSeparators, e.settings?.doNotUseHtmlParagraphAutoSpacing === !0)
	}, "DOCX note layout settings input");
}
function nE(e, t) {
	let n = e?.sectionFlow;
	if (n == null) return {};
	if (n !== "bottomToTop") throw TypeError(`Invalid section flow ${String(n)}`);
	if (t !== "btLr") throw TypeError(`Section flow ${n} contradicts text direction ${JSON.stringify(t ?? null)}`);
	return { sectionFlow: n };
}
function rE(e) {
	return Object.freeze(e ? Object.fromEntries(Object.entries(e).filter((e) => typeof e[1] == "number")) : {});
}
function iE(e) {
	return Object.freeze({
		...e,
		pageGeometry: rE(e.pageGeometry)
	});
}
var aE = /* @__PURE__ */ new WeakMap(), oE = /* @__PURE__ */ new WeakMap(), sE = /* @__PURE__ */ new WeakMap(), cE = /* @__PURE__ */ new WeakMap(), lE = /* @__PURE__ */ new WeakMap();
function uE(e) {
	let t = sE.get(e);
	if (t) return t;
	let n = Z({
		table: e.__tableLayout ?? null,
		rows: e.rows.map((e) => ({
			row: e.__tableRowLayout ?? null,
			cells: e.cells.map((e) => e.__tableCellLayout ?? null)
		}))
	}, "DOCX table acquisition input");
	return sE.set(e, n), n;
}
var dE = (e) => e != null && Number.isFinite(e) ? e : null;
function fE(e) {
	return Z({
		colWidths: (e.colWidths ?? []).map((e) => Number.isFinite(e) && e >= 0 ? e : 0),
		layout: e.layout ?? null,
		widthPt: dE(e.widthPt),
		widthPct: dE(e.widthPct),
		rows: e.rows.map((e) => ({
			gridBefore: dE(e.gridBefore) ?? 0,
			gridAfter: dE(e.gridAfter) ?? 0,
			cells: e.cells.map((e) => ({
				colSpan: dE(e.colSpan) ?? 1,
				widthPt: dE(e.widthPt),
				widthPct: dE(e.widthPct),
				...e.noWrap === !0 ? { noWrap: !0 } : {}
			}))
		}))
	}, "DOCX table column semantic input");
}
function pE(e) {
	let t = lE.get(e);
	if (t) return t;
	let n = fv({
		semantic: fE(e),
		lexical: uE(e),
		format: EE(e)
	});
	return lE.set(e, n), n;
}
function mE(e) {
	return pE(e).format.ordinaryFlow;
}
function hE(e) {
	return pE(e).format.positioning === null ? null : e.tblpPr ?? null;
}
function gE(e) {
	return {
		leftFromTextPt: e.leftFromText,
		rightFromTextPt: e.rightFromText,
		topFromTextPt: e.topFromText,
		bottomFromTextPt: e.bottomFromText,
		horzAnchor: e.horzAnchor,
		horzSpecified: e.horzSpecified,
		vertAnchor: e.vertAnchor,
		xPt: e.tblpX,
		yPt: e.tblpY,
		...e.tblpXSpec == null ? {} : { xAlign: e.tblpXSpec },
		...e.tblpYSpec == null ? {} : { yAlign: e.tblpYSpec }
	};
}
function _E(e, t) {
	if (e === null) return null;
	let n = e.trim(), r = t && n.endsWith("%") ? n.slice(0, -1) : n;
	if (r.length === 0) return null;
	let i = Number(r);
	return Number.isFinite(i) ? i : null;
}
function vE(e) {
	let t = _E(e ?? null, !1);
	return t === null ? null : t / 20;
}
function yE(e) {
	return e === "exact" || e === "atLeast" ? e : "auto";
}
function bE(e) {
	return {
		rule: Ug(yE(e.rule), e.ruleAuthored),
		valuePt: vE(e.value)
	};
}
function xE(e) {
	if (e.rowHeight === null || !Number.isFinite(e.rowHeight)) return null;
	let t = yE(e.rowHeightRule);
	return {
		rule: t === "auto" ? "atLeast" : t,
		valuePt: e.rowHeight
	};
}
function SE(...e) {
	for (let t of e) {
		if (!t) continue;
		let e = Wg(eg(t), ng(t));
		if (e !== null) return e;
	}
	return null;
}
function CE(e, t, n) {
	if (!e) return null;
	let r = eg(e);
	return Gg({
		kind: r,
		dxaValuePt: r === "dxa" ? vE(e.value ?? "0") : null,
		scope: t,
		edge: n
	});
}
function wE(e, t, n, r, i, a, o) {
	let s = e.bidiVisual === !0, c = (e, t) => {
		let n = t === "left" ? s ? "end" : "start" : s ? "start" : "end";
		return {
			width: e?.[n] ?? e?.[t],
			edge: n,
			physicalLeftAuthored: t === "left" && e?.left != null && e?.[n] == null
		};
	}, l = (e, ...t) => {
		for (let n of t) {
			let t = CE(n.width, n.scope, n.edge ?? e);
			if (t !== null) return {
				value: t,
				originLeftMarginPt: n.physicalLeftAuthored ? t : null
			};
		}
		return null;
	}, u = (...e) => l(...e)?.value ?? null, d = c(r, "left"), f = c(i, "left"), p = c(a, "left"), m = c(o, "left"), h = c(r, "right"), g = c(i, "right"), _ = c(a, "right"), v = c(o, "right"), y = (e) => !n && e != null && Number.isFinite(e) ? e : null, b = y(t.marginLeft), x = l(d.edge, {
		...d,
		scope: "cell"
	}) ?? (b === null ? null : {
		value: b,
		originLeftMarginPt: null
	}) ?? l(f.edge, {
		...f,
		scope: "exception"
	}, {
		...p,
		scope: "table"
	}, {
		...m,
		scope: "style"
	}), S = u(h.edge, {
		...h,
		scope: "cell"
	}) ?? y(t.marginRight) ?? u(g.edge, {
		...g,
		scope: "exception"
	}, {
		..._,
		scope: "table"
	}, {
		...v,
		scope: "style"
	});
	return {
		originLeftMarginPt: x?.originLeftMarginPt ?? null,
		horizontalMarginsOmitted: n && [
			r,
			i,
			a,
			o
		].every((e) => e?.left == null && e?.right == null && e?.start == null && e?.end == null),
		dxaHorizontalMarginsOnly: n && [
			r,
			i,
			a,
			o
		].every((e) => e?.start == null && e?.end == null && [e?.left, e?.right].every((e) => e == null || eg(e) === "dxa")),
		marginsPt: {
			top: u("top", {
				width: r?.top,
				scope: "cell"
			}) ?? y(t.marginTop) ?? u("top", {
				width: i?.top,
				scope: "exception"
			}, {
				width: a?.top,
				scope: "table"
			}, {
				width: o?.top,
				scope: "style"
			}) ?? e.cellMarginTop,
			bottom: u("bottom", {
				width: r?.bottom,
				scope: "cell"
			}) ?? y(t.marginBottom) ?? u("bottom", {
				width: i?.bottom,
				scope: "exception"
			}, {
				width: a?.bottom,
				scope: "table"
			}, {
				width: o?.bottom,
				scope: "style"
			}) ?? e.cellMarginBottom,
			left: x?.value ?? e.cellMarginLeft,
			right: S ?? e.cellMarginRight
		}
	};
}
function TE(e) {
	if (!e) return null;
	let t = e.indent ? eg(e.indent) : null;
	return {
		preferredWidthAuthored: e.preferredWidth != null,
		preferredWidth: tg(e.preferredWidth),
		layout: e.layout?.kind === "fixed" || e.layout?.kind === "autofit" ? e.layout.kind : null,
		justification: e.justification,
		indentAuthored: e.indent != null && (t === "dxa" || t === "nil"),
		indentPt: t === "nil" ? 0 : ng(e.indent),
		borders: e.borders
	};
}
function EE(e) {
	let t = cE.get(e);
	if (t) return t;
	let n = uE(e), r = n.table?.ordinaryFlow ?? e.tblpPr == null, i = n.table?.cellFrame, a = e.rows.map((t, r) => {
		let i = n.rows[r]?.row ?? null, a = i?.exception ?? null;
		return {
			height: i?.height ? bE(i.height) : xE(t),
			cantSplit: t.cantSplit === !0,
			...t.__cutsInPlace === !0 ? { cutsInPlace: !0 } : {},
			repeatedHeader: t.isHeader === !0,
			cellSpacingPt: SE(i?.cellSpacing, a?.cellSpacing, n.table?.cellSpacing, i?.styleCellSpacing) ?? 0,
			justification: i?.justification ?? a?.justification ?? null,
			exception: TE(a),
			cells: t.cells.map((t, o) => {
				let s = n.rows[r]?.cells[o];
				return wE(e, t, s != null, s?.margins, a?.cellMargins, n.table?.cellMargins, i?.styleCellMargins);
			})
		};
	}), o = Z({
		effectiveStyleId: n.table?.effectiveStyleId ?? null,
		ordinaryFlow: r,
		...n.table?.outerEdgeIndent === !0 ? { outerEdgeIndent: !0 } : {},
		logicalSequenceId: n.table?.logicalSequenceId ?? null,
		logicalRowOffset: n.table?.logicalRowOffset ?? 0,
		logicalTotalRows: n.table?.logicalTotalRows ?? 0,
		positioning: r ? null : i ? Sg(i) : e.tblpPr == null ? null : gE(e.tblpPr),
		rows: a,
		firstRowException: a[0]?.exception ?? null
	}, "DOCX table format input");
	return cE.set(e, o), o;
}
function* DE(e) {
	for (let t of e) {
		if (t.type !== "table") {
			yield Object.freeze({
				element: t,
				table: null
			});
			continue;
		}
		let e = EE(t);
		if (e.logicalSequenceId == null) {
			yield Object.freeze({
				element: t,
				table: null
			});
			continue;
		}
		yield Object.freeze({
			element: t,
			table: Object.freeze({
				logicalSequenceId: e.logicalSequenceId,
				logicalRowOffset: e.logicalRowOffset ?? 0,
				logicalTotalRows: e.logicalTotalRows ?? 0,
				rowCount: t.rows.length
			})
		});
	}
}
var OE = (e) => Object.freeze({
	story: "body",
	storyInstance: "body",
	path: Object.freeze([e])
}), kE = new Set([
	"paragraph",
	"line",
	"character"
]);
function AE(e, t, n) {
	if (e.type !== "shape" && e.type !== "image" && e.type !== "chart" || WE(e) !== void 0 || !Ja(e.wrapMode) || e.type !== "shape" && !e.anchor || e.widthPt <= 0 || e.heightPt <= 0) return null;
	let r = e.anchorXRelativeFrom ?? (e.anchorXFromMargin ? "margin" : "page"), i = e.anchorYRelativeFrom ?? (e.anchorYFromPara ? "paragraph" : "page"), a = `${t.story}:${t.storyInstance}:${t.path.join(".")}`;
	return Object.freeze({
		occurrenceId: e.type === "shape" ? `public-shape:${a}:${n}` : `public-anchor:${a}:${n}`,
		pageOwned: !kE.has(r) && !kE.has(i)
	});
}
function jE(e, t) {
	let n = new Set([
		"paragraph",
		"line",
		"character"
	]), r = Object.freeze([...new Set(WT(e).flatMap((e, r) => {
		let i = e;
		if (e.type !== "shape" && e.type !== "image" && e.type !== "chart" && i.type !== "unavailableDrawing") return [];
		let a = WE(i);
		if (!a) {
			let e = i.type === "unavailableDrawing" ? null : AE(i, t, r);
			return e?.pageOwned ? [e.occurrenceId] : [];
		}
		return a.horizontal.relativeFromStatus !== "valid" || a.vertical.relativeFromStatus !== "valid" || a.horizontal.relativeFrom === null || a.vertical.relativeFrom === null || a.wrap.kind === "none" || n.has(a.horizontal.relativeFrom) || n.has(a.vertical.relativeFrom) ? [] : [Ne(t, a.occurrenceId)];
	}))]);
	return Object.freeze({
		kind: "paragraph",
		source: t,
		pageBreakBefore: e.pageBreakBefore === !0,
		keepLines: e.keepLines === !0,
		keepNext: e.keepNext === !0,
		widowControl: e.widowControl !== !1,
		...e.framePr?.vAnchor === "text" && e.framePr.dropCap === "none" ? { textFrameMember: !0 } : {},
		...PE(e),
		spaceBeforePt: e.spaceBefore ?? 0,
		spaceAfterPt: e.spaceAfter ?? 0,
		contextualSpacing: e.contextualSpacing === !0,
		styleId: e.styleId ?? null,
		inkless: !GT(e) && BT(e),
		onlyTextualContent: !GT(e) && e.runs.every((e) => e.type === "text" || e.type === "break" && e.breakType === "line"),
		...r.length === 0 ? {} : { pageOwnedAnchorOccurrenceIds: r }
	});
}
function ME(e, t) {
	let n = hE(t);
	return Object.freeze({
		kind: "table",
		source: e,
		...n?.vertAnchor === "page" || n?.vertAnchor === "margin" ? { pageOwnedFloatingTable: !0 } : {}
	});
}
function NE(e, t) {
	let n = OT(e);
	if (n.size === 0) return Object.freeze([]);
	let r = [];
	return t.forEach((e, t) => {
		let n = e.kind === "adjacent-table-group" ? e.tables.length : 1;
		for (let e = 0; e < n; e += 1) r.push(t);
	}), Object.freeze([...n].map(([e, n]) => Object.freeze({
		id: e,
		entryIndex: r[n] ?? t.length
	})));
}
function PE(e) {
	if (!e.framePr) return {};
	let t = e.framePr.dropCap;
	return { framed: t === "drop" || t === "margin" ? "drop-cap" : "frame" };
}
function FE(e, t) {
	let n = 0;
	return Object.freeze(Array.from(zT(DE(e)), (e) => {
		if (e.kind === "adjacent-table-group") {
			let t = n;
			return n += e.tables.length, Object.freeze({
				kind: "adjacent-table-group",
				logicalSequenceId: e.logicalSequenceId,
				source: OE(t),
				tables: Object.freeze(e.tables.map((e, n) => Object.freeze({
					...ME(OE(t + n), e),
					rowCount: e.rows.length
				})))
			});
		}
		let r = e.element, i = n, a = OE(i);
		if (n += 1, r.type === "paragraph") return r.markVanish !== !0 || GT(r) || !BT(r) ? Object.freeze({
			kind: "body-block",
			block: jE(r, a)
		}) : Object.freeze({
			kind: "consume-source",
			source: a,
			reason: "hidden-paragraph",
			...r.pageBreakBefore === !0 ? { pageBreakBefore: !0 } : {},
			...PE(r)
		});
		if (r.type === "table") return Object.freeze({
			kind: "body-block",
			block: ME(a, r)
		});
		if (r.type === "pageBreak" || r.type === "columnBreak") return Object.freeze({
			kind: "authored-break",
			source: a,
			break: r.type === "pageBreak" ? "page" : "column",
			...r.type === "pageBreak" && r.origin !== void 0 ? { origin: r.origin } : {},
			...r.type === "pageBreak" && r.parity !== void 0 ? { parity: r.parity } : {},
			...r.type === "pageBreak" && r.sameParagraphAsPrevious === !0 ? { sameSourceParagraphAsPrevious: !0 } : {}
		});
		if (r.type === "sectionBreak") return Object.freeze({
			kind: "begin-section",
			source: a,
			section: t(i)
		});
		throw Error(`Unsupported body layout source at ${i}`);
	}));
}
function IE(e, t) {
	return ig(pE(e), t);
}
function LE(e, t, n, r = t) {
	return hg(pE(e), t, (t, r, i) => n(e.rows[t].cells[r], i), r);
}
function RE(e, t, n) {
	if (!t || typeof t != "object") return;
	let r = oE.get(e);
	r || (r = /* @__PURE__ */ new WeakMap(), oE.set(e, r)), r.set(t, n);
}
function zE(e) {
	let t = /* @__PURE__ */ new Map(), n = 0;
	e.body.forEach((e, r) => {
		if (e.type !== "sectionBreak") return;
		let i = e.__sectionPlacement;
		t.set(r, Z({
			sectionId: i?.sectionId ?? `section:${n}`,
			sectionBidi: i?.sectionBidi === !0,
			vAlign: i?.vAlign ?? null,
			lineNumbering: i?.lineNumbering ?? null,
			docGridType: i?.docGridType ?? null,
			docGridLinePitch: i?.docGridLinePitch ?? null,
			docGridCharSpace: i?.docGridCharSpace ?? null,
			gutterPt: i?.gutterPt ?? null,
			rtlGutter: i?.rtlGutter ?? null,
			pageBordersAuthored: i?.pageBordersAuthored ?? !1,
			pageBorders: i?.pageBorders ?? null,
			pageGeometry: i?.pageGeometry ?? e.geom ?? {},
			...nE(i, e.textDirection)
		}, "DOCX ending-section placement input")), n += 1;
	});
	let r = e.section?.__sectionPlacement;
	return Object.freeze({
		endingSections: t,
		finalSection: Z({
			sectionId: r?.sectionId ?? `section:${n}`,
			sectionBidi: r?.sectionBidi === !0,
			vAlign: r?.vAlign ?? e.section?.vAlign ?? null,
			lineNumbering: r?.lineNumbering ?? e.section?.lineNumbering ?? null,
			docGridType: r?.docGridType ?? e.section?.docGridType ?? null,
			docGridLinePitch: r?.docGridLinePitch ?? e.section?.docGridLinePitch ?? null,
			docGridCharSpace: r?.docGridCharSpace ?? e.section?.docGridCharSpace ?? null,
			gutterPt: r?.gutterPt ?? null,
			rtlGutter: r?.rtlGutter ?? null,
			pageBordersAuthored: r?.pageBordersAuthored ?? e.section?.pageBorders != null,
			pageBorders: r?.pageBorders ?? e.section?.pageBorders ?? null,
			pageGeometry: r?.pageGeometry ?? (e.section ? rv(e.section) : {}),
			...nE(r, e.section?.textDirection)
		}, "DOCX final-section placement input")
	});
}
var BE = Object.freeze({
	default: null,
	first: null,
	even: null
});
function VE(e) {
	let t = [], n = zE(e), r = 0;
	e.body.forEach((e, i) => {
		if (e.type !== "sectionBreak") return;
		let a = n.endingSections.get(i) ?? n.finalSection, o = t.length;
		t.push({
			sectionOccurrenceId: a.sectionId,
			ordinal: o,
			startBodyIndex: r,
			endBodyIndex: i,
			markerBodyIndex: i,
			final: !1,
			startType: e.kind ?? "nextPage",
			columns: e.columns ?? null,
			authoredGeometry: rE(a.pageGeometry),
			textDirection: e.textDirection ?? null,
			...a.sectionFlow ? { sectionFlow: a.sectionFlow } : {},
			pageNumType: e.pageNumType ?? null,
			headers: e.headers ?? BE,
			footers: e.footers ?? BE,
			titlePage: e.titlePage ?? !1,
			sectionBidi: a.sectionBidi,
			vAlign: a.vAlign,
			lineNumbering: a.lineNumbering,
			docGridType: a.docGridType,
			docGridLinePitch: a.docGridLinePitch,
			docGridCharSpace: a.docGridCharSpace,
			authoredGutterPt: a.gutterPt,
			rtlGutter: a.rtlGutter === !0,
			pageBordersAuthored: a.pageBordersAuthored,
			pageBorders: a.pageBorders,
			placement: iE(a)
		}), r = i + 1;
	});
	let i = n.finalSection;
	t.push({
		sectionOccurrenceId: i.sectionId,
		ordinal: t.length,
		startBodyIndex: r,
		endBodyIndex: e.body.length - 1,
		markerBodyIndex: null,
		final: !0,
		startType: e.section.sectionStart ?? "nextPage",
		columns: e.section.columns ?? null,
		authoredGeometry: i.pageGeometry == null ? rv(e.section) : rE(i.pageGeometry),
		textDirection: e.section.textDirection ?? null,
		...i.sectionFlow ? { sectionFlow: i.sectionFlow } : {},
		pageNumType: e.section.pageNumType ?? null,
		headers: e.headers ?? BE,
		footers: e.footers ?? BE,
		titlePage: e.section.titlePage,
		sectionBidi: i.sectionBidi,
		vAlign: i.vAlign,
		lineNumbering: i.lineNumbering,
		docGridType: i.docGridType,
		docGridLinePitch: i.docGridLinePitch,
		docGridCharSpace: i.docGridCharSpace,
		authoredGutterPt: i.gutterPt,
		rtlGutter: i.rtlGutter === !0,
		pageBordersAuthored: i.pageBordersAuthored,
		pageBorders: i.pageBorders,
		placement: iE(i)
	});
	let a = Array(t.length), o = rv(e.section), s = null, c = null;
	for (let e = t.length - 1; e >= 0; --e) {
		let n = t[e], r = n.startType === "continuous" && s !== null ? s : o, i = n.authoredGeometry, l = {
			pageWidth: i.pageWidth ?? r.pageWidth,
			pageHeight: i.pageHeight ?? r.pageHeight,
			marginTop: i.marginTop ?? r.marginTop,
			marginRight: i.marginRight ?? r.marginRight,
			marginBottom: i.marginBottom ?? r.marginBottom,
			marginLeft: i.marginLeft ?? r.marginLeft,
			headerDistance: i.headerDistance ?? r.headerDistance,
			footerDistance: i.footerDistance ?? r.footerDistance
		}, u = n.authoredGutterPt ?? (n.startType === "continuous" ? c : null) ?? 0, { authoredGeometry: d, authoredGutterPt: f, ...p } = n;
		a[e] = {
			...p,
			geometry: l,
			gutterPt: u
		}, s = l, c = u;
	}
	return Z({
		bodyLength: e.body.length,
		occurrences: a
	}, "DOCX body section index input");
}
function HE(e) {
	let t = VE(e), n = /* @__PURE__ */ new Map();
	for (let e of t.occurrences) e.startBodyIndex !== 0 && n.set(e.startBodyIndex - 1, e);
	let r = FE(e.body, (e) => {
		let t = n.get(e);
		if (!t) throw Error(`Missing incoming body section at ${e}`);
		return Object.freeze({
			sectionOccurrenceId: t.sectionOccurrenceId,
			startType: t.startType
		});
	}), i = Pm(e).map((e, t) => {
		let n = qv(t), r = e.body.flatMap((e, t) => {
			if (e.type !== "paragraph") return [];
			let r = Object.freeze({
				...n,
				path: Object.freeze([t])
			});
			return (jE(e, r).pageOwnedAnchorOccurrenceIds ?? []).map((e) => Object.freeze({
				occurrenceId: e,
				paragraphSource: r
			}));
		});
		return Object.freeze({
			pageIndex: e.page - 1,
			source: n,
			wrapAnchors: Object.freeze(r)
		});
	});
	return {
		...i.length > 0 ? { pageObjects: Object.freeze(i) } : {},
		sectionIndex: t,
		compat: Kl(e.settings),
		evenAndOddHeaders: e.section.evenAndOddHeaders,
		endnoteIds: (e.endnotes ?? []).map((e) => e.id),
		repeatedFootnoteLastEntries: NE(e.body, r),
		noteLayoutSettings: tE(e),
		pageLayoutSettings: JT(e),
		parserDiagnostics: Uo(e.diagnostics, e.body.length),
		sequence: r
	};
}
function UE(e) {
	let t = e.textPath;
	if (t) return Z({
		string: t.string,
		...t.fontFamily === void 0 ? {} : { fontFamily: t.fontFamily },
		bold: t.bold ?? !1,
		italic: t.italic ?? !1,
		...t.textPathOk === void 0 ? {} : { textPathOk: t.textPathOk },
		...t.on === void 0 ? {} : { on: t.on },
		...t.fitShape === void 0 ? {} : { fitShape: t.fitShape },
		...t.fitPath === void 0 ? {} : { fitPath: t.fitPath },
		...t.trim === void 0 ? {} : { trim: t.trim },
		...t.xScale === void 0 ? {} : { xScale: t.xScale },
		...t.fontSizePt === void 0 ? {} : { fontSizePt: t.fontSizePt }
	}, "DOCX VML text path acquisition input");
}
function WE(e) {
	let t = e.__anchorAcquisition;
	if (t !== void 0) return Z(t, "DOCX anchor acquisition input");
}
function GE(e, t) {
	let n = rD(e).fontFacts, r = n?.rtl === !0 || n?.cs === !0, i = r ? n?.fontSizeCs ?? n?.fontSize ?? t : n?.fontSize ?? t, a = n?.fontFamily ?? e.fontFamily ?? null, o = {
		ascii: a,
		highAnsi: n?.fontFamilyHighAnsi ?? a,
		eastAsia: n?.fontFamilyEastAsia ?? e.fontFamilyEastAsia ?? a,
		complexScript: n?.fontFamilyCs ?? a
	}, s = n?.fontSlots;
	return Object.freeze({
		fontSizePt: i,
		fonts: Object.freeze({ ...s?.direct ?? o }),
		themeFonts: s?.theme ? Object.freeze({ ...s.theme }) : void 0,
		themeFontPresence: s?.themePresent ? Object.freeze({ ...s.themePresent }) : void 0,
		weight: (r ? n?.boldCs ?? !1 : n?.bold ?? !1) ? 700 : 400,
		style: (r ? n?.italicCs ?? !1 : n?.italic ?? !1) ? "italic" : "normal",
		complexScript: r,
		fontHint: n?.fontHint,
		eastAsiaLanguage: n?.langEastAsia,
		kerning: cr(i, n?.kerning, "size-comparison")
	});
}
function KE(e, t) {
	let n = e.textBoxContent;
	return n === void 0 ? Z({
		kind: "compatibility",
		source: t,
		paragraphs: Fx(e, t, GE)
	}, "DOCX public text box acquisition input") : Z({
		kind: "complete",
		source: t,
		blockCount: n.length
	}, "DOCX complete text box acquisition input");
}
function qE(e) {
	let t = iD(e).paragraphMarkFontFacts;
	return t ? YE(t, e) : void 0;
}
function JE(e) {
	if (e.type !== "image" && e.type !== "shape") return;
	let t = e.__inlineObjectFontFacts;
	return t ? YE(t) : void 0;
}
function YE(e, t) {
	let n = e.rtl === !0 || e.cs === !0, r = t?.runs.find((e) => e.type === "text" || e.type === "field")?.fontSize ?? t?.defaultFontSize ?? 10, i = n ? e.fontSizeCs ?? e.fontSize ?? r : e.fontSize ?? r, a = e.fontFamily ?? t?.defaultFontFamily ?? null, o = {
		ascii: a,
		highAnsi: e.fontFamilyHighAnsi ?? a,
		eastAsia: e.fontFamilyEastAsia ?? t?.defaultFontFamilyEastAsia ?? a,
		complexScript: e.fontFamilyCs ?? a
	};
	return Object.freeze({
		fontSizePt: i,
		fonts: Object.freeze({ ...e.fontSlots?.direct ?? o }),
		themeFonts: e.fontSlots?.theme ? Object.freeze({ ...e.fontSlots.theme }) : void 0,
		themeFontPresence: e.fontSlots?.themePresent ? Object.freeze({ ...e.fontSlots.themePresent }) : void 0,
		weight: (n ? e.boldCs ?? !1 : e.bold ?? !1) ? 700 : 400,
		style: (n ? e.italicCs ?? !1 : e.italic ?? !1) ? "italic" : "normal",
		complexScript: n,
		fontHint: e.fontHint,
		eastAsiaLanguage: e.langEastAsia,
		kerning: cr(i, e.kerning, "size-comparison")
	});
}
function XE(e, t) {
	let n = e, { layoutLines: r, lineSlice: i, runs: a, paragraphMarkFontFacts: o, __paragraphTypographyAcquisition: s, __complexFieldBoundaries: c, __runRevisions: l, ...u } = e, d = LT(n), f = e.__complexFieldBoundaries?.map((e) => ({
		occurrenceKey: [
			"complex-field",
			t.story,
			t.storyInstance,
			t.path.slice(0, -1).join("."),
			String(e.occurrenceId)
		].join(":"),
		boundary: e.boundary,
		runIndex: e.runIndex,
		fieldType: e.fieldType,
		instruction: e.instruction,
		...e.hyperlinkAnchor === void 0 ? {} : { hyperlinkAnchor: e.hyperlinkAnchor }
	})), p = u.numbering, m = p == null ? null : (({ fontFacts: e, ...t }) => t)(p), h = structuredClone({
		...u,
		numbering: m
	}), g = UT(n), _ = [];
	if (g.length === 0) n.runs.forEach((e, t) => {
		_.push({
			run: e,
			originalRun: n.runs[t]
		});
	});
	else {
		let e = 0;
		for (let t = 0; t <= n.runs.length; t += 1) {
			for (; g[e]?.publicRunIndex === t;) {
				let t = g[e].run;
				_.push({
					run: t,
					originalRun: t
				}), e += 1;
			}
			t < n.runs.length && _.push({
				run: n.runs[t],
				originalRun: n.runs[t]
			});
		}
	}
	let v = _.map(({ run: e, originalRun: n }, r) => {
		let i = e;
		if (i.type === "unavailableDrawing") {
			let e = WE(n), r = e === void 0 ? void 0 : Z({
				...e,
				occurrenceId: Ne(t, e.occurrenceId)
			}, "DOCX scoped unavailable drawing anchor acquisition input"), { __anchorAcquisition: a, ...o } = i;
			return Object.freeze({
				...o,
				...r === void 0 ? {} : { anchorAcquisitionInput: r }
			});
		}
		if (e.type === "math") {
			let n = Object.freeze({
				...t,
				path: Object.freeze([...t.path, r])
			}), i = e;
			return Object.freeze({
				type: "math",
				...e.revision ? { revision: Object.freeze({ ...e.revision }) } : {},
				display: e.display,
				fontSize: e.fontSize,
				...e.jc === void 0 ? {} : { jc: e.jc },
				source: i.source ?? n,
				resourceKey: i.resourceKey ?? je(n, e.display ? "display" : "inline"),
				fallbackText: Y(e.nodes)
			});
		}
		if (e.type === "anchorHost") {
			let { __anchorOccurrenceId: n, __listLabel: r, ...i } = e;
			return Object.freeze({
				...i,
				...n === void 0 ? {} : { anchorOccurrenceId: Ne(t, n) },
				...VT(r) ? { listLabel: r } : {}
			});
		}
		if (e.type === "shape" || e.type === "image" || e.type === "chart") {
			let i = WE(n), a = i === void 0 ? void 0 : Z({
				...i,
				occurrenceId: Ne(t, i.occurrenceId)
			}, "DOCX scoped anchor acquisition input"), { __anchorAcquisition: o, __listLabel: s, __inlineObjectFontFacts: c, __inlineObjectOrigin: l, ...u } = e, d = JE(n), f = l === "drawingml" || l === "vmlStaticTextbox" ? l : void 0;
			if (e.type !== "shape") {
				let n = e.type === "chart" ? (({ chart: e, ...n }) => ({
					...n,
					resourceKey: ke({
						...t,
						path: [...t.path, r]
					})
				}))(u) : u;
				return Object.freeze({
					...structuredClone(n),
					...d ? { inlineObjectShapeInput: d } : {},
					...f ? { inlineObjectOrigin: f } : {},
					...a === void 0 ? {} : { anchorAcquisitionInput: a },
					...e.type === "image" && VT(s) ? { listLabel: s } : {}
				});
			}
			let p = n, m = UE(p), h = Object.freeze({
				...t,
				path: Object.freeze([...t.path, r])
			}), g = KE(p, {
				story: "textbox",
				storyInstance: `${h.story}:${h.storyInstance}:${h.path.join(".")}`,
				path: []
			}), { textBoxContent: _, textBlocks: v, textPath: y, ...b } = u;
			return Object.freeze({
				type: "shape",
				...structuredClone(b),
				...d ? { inlineObjectShapeInput: d } : {},
				...f ? { inlineObjectOrigin: f } : {},
				...m === void 0 ? {} : { vmlTextPathInput: m },
				...(g.kind === "complete" ? g.blockCount : g.paragraphs.length) === 0 ? {} : { textBoxInput: g },
				...a === void 0 ? {} : { anchorAcquisitionInput: a }
			});
		}
		if (e.type === "text" || e.type === "field") {
			let t = IT(n), { __typographyAcquisition: r, __noBreakBefore: i, __noBreakAfter: a, __noBreakHyphenOffsets: o, __optionalHyphen: s, __spaceAdvancePt: c, __listLabel: l, ...u } = e, d = e.type === "text" ? o?.filter((t) => Number.isInteger(t) && t > 0 && t <= e.text.length).map((e) => Object.freeze({
				start: e - 1,
				end: e
			})) : void 0;
			return Object.freeze({
				...structuredClone(u),
				...s === !0 && e.type === "text" ? { optionalHyphen: !0 } : {},
				...e.type === "text" && typeof c == "number" && Number.isFinite(c) && c >= 0 ? { spaceAdvancePt: c } : {},
				...e.type === "text" && VT(l) ? { listLabel: l } : {},
				...i === !0 ? { noBreakBefore: !0 } : {},
				...a === !0 ? { noBreakAfter: !0 } : {},
				...d?.length ? { noBreakRanges: Object.freeze(d) } : {},
				...t === void 0 ? {} : { typographyInput: t }
			});
		}
		return Object.freeze(structuredClone(e));
	});
	return fv({
		...h,
		runs: v,
		...f?.length ? { complexFieldBoundaries: f } : {},
		numberingMarkerShapeInput: e.numbering ? GE(e.numbering, n.runs.find((e) => e.type === "text" || e.type === "field")?.fontSize ?? e.defaultFontSize ?? 10) : void 0,
		paragraphMarkShapeInput: qE(e),
		...d === void 0 ? {} : { typographyInput: d }
	});
}
function ZE(e, t, n) {
	let r = XE({
		...e,
		type: "paragraph",
		runs: t.map(({ run: e }) => ({
			...e,
			type: "text",
			text: ""
		}))
	}, n);
	if (r.runs.length !== t.length) throw Error("Reserved note separator participants were not projected one-to-one");
	return fv({
		...r,
		runs: r.runs.map((e, n) => ({
			...e,
			noteSeparatorCharacter: t[n].role
		}))
	});
}
function QE(e, t) {
	return XE({
		...e,
		type: "paragraph",
		runs: []
	}, t);
}
function $E(e) {
	return tD(e, !1);
}
function eD(e) {
	return tD(e, !0);
}
function tD(e, t) {
	let n = [], r = (a, o, s, c) => {
		if (a.type === "paragraph") {
			let i = a, l = i.__runRevisions ?? [], u = i.__runRevisions !== void 0, d = [], f = [], p = a.runs.some((e) => e.type === "unavailableDrawing");
			WT(a).forEach((i, a) => {
				let m = l[a] ?? void 0, h = i.revision, g = m === void 0 || h !== void 0 ? i : {
					...i,
					revision: m
				};
				if (g !== i && (u = !0), g.type === "unavailableDrawing") {
					f.push(Object.freeze({
						publicRunIndex: d.length,
						run: Z(g, "DOCX unavailable drawing parser sidecar")
					})), p && (u = !0);
					return;
				}
				if (g.type === "math") {
					u = !0;
					let e = Object.freeze({
						story: o,
						storyInstance: s,
						path: Object.freeze([...c, a])
					}), t = je(e, g.display ? "display" : "inline");
					n.push(Object.freeze({
						nodes: g.nodes,
						display: g.display,
						source: e,
						resourceKey: t
					})), d.push(Object.freeze({
						...g,
						source: e,
						resourceKey: t
					}));
					return;
				}
				if (g.type !== "shape") {
					d.push(g);
					return;
				}
				let _ = g;
				if (_.textBlocks?.some((e) => e.beforeAutospacing === !0 || e.afterAutospacing === !0)) {
					let t = _.textBlocks.map((t) => {
						let n = ES(t, t.defaultFontSize ?? t.fontSizePt, e.settings?.doNotUseHtmlParagraphAutoSpacing === !0);
						return n.spaceBefore === t.spaceBefore && n.spaceAfter === t.spaceAfter ? t : {
							...t,
							...n
						};
					});
					t.some((e, t) => e !== _.textBlocks?.[t]) && (_ = {
						..._,
						textBlocks: t
					}, u = !0);
				}
				let v = _.textBoxContent;
				if (v === void 0) {
					d.push(_);
					return;
				}
				let y = {
					story: o,
					storyInstance: s,
					path: [...c, a]
				}, b = `${y.story}:${y.storyInstance}:${y.path.join(".")}`, x = !1, S = t ? v : Array(v.length);
				if (v.forEach((e, t) => {
					if (e.type === "unsupportedTextBoxBlock") {
						S[t] = e;
						return;
					}
					let n = r(e, "textbox", b, [t]);
					n !== e && (x = !0), S[t] = n;
				}), !x) {
					d.push(_);
					return;
				}
				u = !0, t ? (_.textBoxContent = S, d.push(_)) : d.push({
					..._,
					textBoxContent: S
				});
			});
			let m = ES(a, a.defaultFontSize ?? 10, e.settings?.doNotUseHtmlParagraphAutoSpacing === !0), h = m.spaceBefore !== a.spaceBefore || m.spaceAfter !== a.spaceAfter, g;
			if (t) u && Object.assign(a, { runs: d }), h && Object.assign(a, m), delete a.__runRevisions, g = a;
			else if (u || h) {
				let { __runRevisions: e, ...t } = i;
				g = {
					...t,
					...m,
					runs: d
				};
			} else g = a;
			return f.length > 0 && HT.set(g, Object.freeze(f)), g;
		}
		if (a.type === "table") {
			if (t) return a.rows.forEach((e, t) => e.cells.forEach((e, n) => {
				e.content = i(e.content, o, s, [
					...c,
					t,
					n
				]);
			})), a;
			let e = !1, n = a.rows.map((t, n) => {
				let r = !1, a = t.cells.map((e, t) => {
					let a = i(e.content, o, s, [
						...c,
						n,
						t
					]);
					return a === e.content ? e : (r = !0, {
						...e,
						content: a
					});
				});
				return r ? (e = !0, {
					...t,
					cells: a
				}) : t;
			});
			return e ? {
				...a,
				rows: n
			} : a;
		}
		if (a.type !== "sectionBreak") return a;
		let l = c.at(-1) ?? 0, u = !1, d = (e, t) => {
			if (!e) return e;
			let n = e;
			for (let r of [
				"default",
				"first",
				"even"
			]) {
				let a = e[r];
				if (!a) continue;
				let o = i(a.body, t, `section:${l}:${r}`);
				o !== a.body && (n === e && (n = { ...e }), n[r] = {
					...a,
					body: o
				}, u = !0);
			}
			return n;
		}, f = d(a.headers, "header"), p = d(a.footers, "footer");
		return u ? {
			...a,
			headers: f,
			footers: p
		} : a;
	}, i = (e, n, i, a = []) => {
		if (t) {
			for (let t = 0; t < e.length; t += 1) e[t] = r(e[t], n, i, [...a, t]);
			return e;
		}
		let o = !1, s = e.map((e, t) => {
			let s = r(e, n, i, [...a, t]);
			return s !== e && (o = !0), s;
		});
		return o ? s : e;
	}, a = (e, t) => {
		if (!e) return {
			default: null,
			first: null,
			even: null
		};
		let n = e;
		for (let r of [
			"default",
			"first",
			"even"
		]) {
			let a = e[r];
			if (!a) continue;
			let o = i(a.body, t, r);
			o !== a.body && (n === e && (n = { ...e }), n[r] = {
				...a,
				body: o
			});
		}
		return n;
	}, o = i(e.body, "body", "body"), s = a(e.headers, "header"), c = a(e.footers, "footer"), l = (e, n) => {
		if (!e) return e;
		if (t) {
			for (let t of e) t.content = i(t.content, n, t.id);
			return e;
		}
		let r = !1, a = e.map((e) => {
			let t = i(e.content, n, e.id);
			return t === e.content ? e : (r = !0, {
				...e,
				content: t
			});
		});
		return r ? a : e;
	}, u = l(e.footnotes, "footnote"), d = l(e.endnotes, "endnote"), f = e.__pageObjects, p = f;
	if (f) {
		let e = !1, t = f.map((t, n) => {
			let r = i(t.body, "header", qv(n).storyInstance);
			return r === t.body ? t : (e = !0, {
				...t,
				body: r
			});
		});
		e && (p = t);
	}
	let m = o !== e.body || s !== e.headers || c !== e.footers || u !== e.footnotes || d !== e.endnotes || p !== f ? {
		...e,
		body: o,
		headers: s,
		footers: c,
		footnotes: u,
		endnotes: d,
		...p ? { __pageObjects: p } : {}
	} : e, h = zE(m);
	aE.set(m, h), RE(m.body, m.section, h);
	let g, _ = () => g ??= HE(m), v = sD();
	return Object.freeze({
		document: m,
		mathOccurrences: Object.freeze(n),
		fontFamilyCharsets: Object.freeze({ ...aD(m).fontFamilyCharsets ?? {} }),
		get bodyLayoutInput() {
			return $v(_());
		},
		bodyModelGateway: Object.freeze({
			acquisitionInputs: v,
			get bodySectionIndex() {
				return _().sectionIndex;
			},
			effectiveTablePositioning: hE,
			publicAnchorBridge: AE
		})
	});
}
function nD(e) {
	return $E(e).document;
}
function rD(e) {
	return e;
}
function iD(e) {
	return e;
}
function aD(e) {
	return e;
}
var oD = Object.freeze({
	numberingMarkerShapeInput: GE,
	paragraphMarkShapeInput: qE,
	tableFormatInput: EE,
	tableSourceAcquisitionInput: pE,
	effectiveTablePreferredWidthPt: IE,
	tableColumnLayoutInput: LE,
	tableParticipatesInOrdinaryFlow: mE,
	paragraphAcquisitionInput: XE
});
function sD() {
	let e = /* @__PURE__ */ new WeakMap(), t = (t, n) => {
		let r = e.get(t);
		r || (r = /* @__PURE__ */ new Map(), e.set(t, r));
		let i = Me(n), a = r.get(i);
		if (a) return a;
		let o = XE(t, n);
		return r.set(i, o), o;
	};
	return Object.freeze({
		...oD,
		paragraphAcquisitionInput: t
	});
}
function cD(e, t) {
	return t.map((t) => Ks(e, t));
}
function lD(e, t) {
	let n = e ?? null, r = {
		ascii: n,
		highAnsi: t.fontFamilyHighAnsi ?? n,
		eastAsia: t.fontFamilyEastAsia ?? n,
		complexScript: t.fontFamilyCs ?? n
	};
	return {
		fonts: t.fontSlots?.direct ?? r,
		themeFonts: t.fontSlots?.theme,
		themeFontPresence: t.fontSlots?.themePresent
	};
}
function uD(e) {
	return e.cs === !0 || e.rtl === !0 || e.fontFamilyCs != null || e.fontSlots?.direct.complexScript != null || e.fontSlots?.themePresent.complexScript === !0;
}
function dD(e, t) {
	return {
		text: e,
		eastAsiaLanguage: t.eastAsiaLanguage,
		fontFamilies: cD(t, [
			"ascii",
			"highAnsi",
			"eastAsia",
			"complexScript"
		]),
		bold: t.weight >= 700,
		italic: t.style === "italic"
	};
}
function* fD(e, t) {
	e.textPath && (yield {
		text: e.textPath.string,
		fontFamilies: [e.textPath.fontFamily]
	});
	let n = e.textBoxContent;
	if (t === "font-demand" && n !== void 0) {
		yield* yD(n, t);
		return;
	}
	for (let r of e.textBlocks ?? []) yield* pD(r, t, n === void 0);
}
function* pD(e, t, n) {
	if (e.numbering && (yield {
		text: e.numbering.text,
		fontFamilies: [e.numbering.fontFamily, e.numbering.fontFamilyEastAsia]
	}), e.runs?.length) for (let r of e.runs) {
		if (n && (r.rtl || r.cs)) {
			yield* hD(xs({
				...r,
				fontFamily: r.fontFamily ?? e.fontFamily,
				bold: r.bold ?? e.bold,
				italic: r.italic ?? e.italic
			}), t);
			continue;
		}
		yield {
			text: r.text,
			fontFamilies: [
				r.fontFamily,
				r.fontFamilyEastAsia,
				e.fontFamily
			],
			latinFontFamily: r.fontFamily ?? e.fontFamily ?? null,
			bold: r.bold ?? e.bold,
			italic: r.italic ?? e.italic
		};
	}
	else yield {
		text: e.text,
		fontFamilies: [e.fontFamily],
		latinFontFamily: e.fontFamily ?? null,
		bold: e.bold,
		italic: e.italic
	};
}
function* mD(e, t, n, r, i, a) {
	let o = lD(t, n), [s, c, l] = a === "font-demand" ? cD(o, [
		"ascii",
		"highAnsi",
		"eastAsia"
	]) : [
		t,
		n.fontFamilyHighAnsi,
		n.fontFamilyEastAsia
	];
	if (yield {
		text: e,
		eastAsiaLanguage: n.langEastAsia,
		fontFamilies: [
			s,
			c,
			l
		],
		latinFontFamily: s ?? c ?? null,
		bold: r,
		italic: i
	}, a === "font-demand" ? uD(n) : n.fontFamilyCs != null) {
		let t = a === "font-demand" ? Ks(o, "complexScript") : n.fontFamilyCs;
		t && (yield {
			text: e,
			eastAsiaLanguage: n.langEastAsia,
			fontFamilies: [t],
			bold: n.boldCs ?? !1,
			italic: n.italicCs ?? !1
		});
	}
}
function* hD(e, t) {
	let n = JE(e);
	if (n && (yield dD("", n)), e.type === "text") {
		let n = e;
		yield* mD(e.text, e.fontFamily, n, e.bold, e.italic, t);
	} else if (e.type === "field") {
		let n = e;
		yield* mD(n.fallbackText, n.fontFamily, n, n.bold, n.italic, t);
	} else e.type === "shape" ? yield* fD(e, t) : e.type === "anchorHost" && (yield {
		text: "",
		fontFamilies: [e.fontFamily, e.fontFamilyEastAsia],
		bold: e.bold,
		italic: e.italic
	});
}
function* gD(e, t) {
	if (yield {
		text: "",
		fontFamilies: [e.defaultFontFamily, e.defaultFontFamilyEastAsia]
	}, t === "font-demand") {
		let t = qE(e);
		t && (yield dD("", t));
	}
	e.numbering && (t === "font-demand" ? yield dD(e.numbering.text, GE(e.numbering, e.defaultFontSize ?? 10)) : yield {
		text: e.numbering.text,
		fontFamilies: [e.numbering.fontFamily, e.numbering.fontFamilyEastAsia]
	});
	for (let n of e.runs) for (let r of hD(n, t)) {
		let t = r.fontFamilies.some(Boolean) ? r.fontFamilies : [e.defaultFontFamily, e.defaultFontFamilyEastAsia];
		yield {
			...r,
			fontFamilies: t,
			...r.latinFontFamily === null ? { latinFontFamily: e.defaultFontFamily ?? null } : {}
		};
	}
}
function* _D(e, t) {
	for (let n of e.rows) for (let e of n.cells) yield* yD(e.content, t);
}
function* vD(e, t) {
	if (e) for (let n of [
		e.default,
		e.first,
		e.even
	]) n && (yield* yD(n.body, t));
}
function* yD(e, t) {
	for (let n of e) n.type === "paragraph" ? yield* gD(n, t) : n.type === "table" ? yield* _D(n, t) : n.type === "sectionBreak" && (yield* vD(n.headers, t), yield* vD(n.footers, t));
}
function* bD(e, t) {
	let n = e.__noteLayoutSettings?.reservedSeparators;
	for (let e of [n?.footnote, n?.endnote]) if (e) for (let n of [
		e.separator,
		e.continuationSeparator,
		e.continuationNotice
	]) {
		let e = n.paragraph;
		if (!e) continue;
		let r = [n.rule?.control.run, e.contentMark?.run].filter((e) => e !== void 0).map((e) => ({
			...e,
			type: "text",
			text: ""
		}));
		yield* gD({
			...e.paragraph,
			runs: r
		}, t);
	}
}
function* xD(e, t) {
	let n = e.__noteLayoutSettings;
	for (let e of [
		n?.footnoteSeparatorParagraph,
		n?.footnoteContinuationSeparatorParagraph,
		n?.endnoteSeparatorParagraph,
		n?.endnoteContinuationSeparatorParagraph
	]) e && (yield* gD({
		...e,
		runs: []
	}, t));
}
function* SD(e, t = "native-preflight") {
	yield* yD(e.body ?? [], t), yield* vD(e.headers, t), yield* vD(e.footers, t);
	for (let n of Pm(e)) yield* yD(n.body, t);
	for (let n of [...e.footnotes ?? [], ...e.endnotes ?? []]) yield* yD(n.content, t);
	yield* bD(e, t), yield* xD(e, t);
}
function CD(e) {
	let t = /* @__PURE__ */ new Set();
	for (let n of SD(e)) for (let e of n.fontFamilies) {
		let n = e?.trim();
		n && t.add(n);
	}
	return [...t];
}
export { Sb as $, ig as $n, Va as $r, iv as $t, FS as A, Xg as An, Ns as Ar, qv as At, jb as B, Eg as Bn, qo as Br, Ev as Bt, CT as C, Ut as Ci, u_ as Cn, tf as Cr, ey as Ct, RS as D, Fe as Di, Pg as Dn, qu as Dr, sy as Dt, MS as E, Ie as Ei, Bg as En, ef as Er, cy as Et, CS as F, jg as Fn, ns as Fr, Fv as Ft, Ob as G, Hg as Gn, qa as Gr, Pv as Gt, Ab as H, zg as Hn, Wo as Hr, Wv as Ht, Qx as I, Ig as In, as as Ir, jv as It, Cb as J, qg as Jn, Aa as Jr, uv as Jt, Tb as K, Kg as Kn, Da as Kr, fv as Kt, ox as L, Jg as Ln, ts as Lr, Vv as Lt, DS as M, Lg as Mn, Ms as Mr, kv as Mt, TS as N, Mg as Nn, Ls as Nr, Av as Nt, zS as O, Ng as On, Y as Or, ay as Ot, wS as P, Ag as Pn, ls as Pr, Gv as Pt, Q, ag as Qn, ja as Qr, J_ as Qt, ax as R, wg as Rn, Go as Rr, Uv as Rt, lT as S, $t as Si, g_ as Sn, Of as Sr, ty as St, VS as T, Ft as Ti, Qg as Tn, af as Tr, iy as Tt, kb as U, Fg as Un, fo as Ur, Bv as Ut, Nb as V, Rg as Vn, Jo as Vr, Hv as Vt, Db as W, Og as Wn, Ja as Wr, zv as Wt, sb as X, vg as Xn, Ma as Xr, Z as Xt, ab as Y, Dg as Yn, Na as Yr, _v as Yt, xb as Z, xg as Zn, ka as Zr, ov as Zt, sT as _, Ln as _i, C_ as _n, th as _r, rb as _t, $E as a, mi as ai, X_ as an, Th as ar, qy as at, PC as b, Nn as bi, S_ as bn, Pm as br, Wy as bt, ZE as c, ci, W_ as cn, xh as cr, eb as ct, ET as d, $r as di, j_ as dn, ch as dr, wy as dt, Ra as ei, ev as en, hg as er, zy as et, FT as f, $n as fi, B_ as fn, rh as fr, tb as ft, kT as g, Xn as gi, D_ as gn, eh as gr, Ky as gt, DT as h, Jn as hi, F_ as hn, Gm as hr, Hy as ht, nD as i, fi as ii, Z_ as in, Ah as ir, nb as it, AS as j, Zg as jn, Xs as jr, Ov as jt, NS as k, Yg as kn, ql as kr, Jv as kt, QE as l, ui as li, K_ as ln, wh as lr, Zy as lt, PT as m, In as mi, T_ as mn, $m as mr, Ny as mt, SD as n, li as ni, $_ as nn, Qh as nr, Vy as nt, eD as o, di as oi, Y_ as on, kh as or, Uy as ot, NT as p, er as pi, R_ as pn, Xm as pr, Iy as pt, wb as q, kg as qn, Oa as qr, pv as qt, qT as r, pi as ri, nv as rn, Yh as rr, Gy as rt, KT as s, hi as si, G_ as sn, Oh as sr, By as st, CD as t, yi as ti, Q_ as tn, Wh as tr, Cy as tt, pE as u, ar as ui, E_ as un, Dh as ur, Qy as ut, fT as v, xn as vi, w_ as vn, Zm as vr, $y as vt, WS as w, Vt as wi, c_ as wn, Qd as wr, oy as wt, Aw as x, Qt as xi, l_ as xn, Nm as xr, ly as xt, lw as y, mn as yi, y_ as yn, Vm as yr, Jy as yt, Eb as z, Cg as zn, Ko as zr, Tv as zt };
