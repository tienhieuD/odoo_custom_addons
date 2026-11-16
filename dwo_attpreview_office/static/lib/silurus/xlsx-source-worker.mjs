//#region packages/core/src/internal/abort.ts
function e(e) {
	let t = Error(e);
	return t.name = "AbortError", t;
}
function t(t, n) {
	if (t?.aborted) throw e(n);
}
//#endregion
//#region packages/core/src/source/model-source.ts
var n = "model source load was aborted", r = "ooxml-model-source-module/v2", i = new Set([
	"docx",
	"xlsx",
	"pptx"
]), a = new Set([
	"http:",
	"https:",
	"file:",
	"blob:"
]), o = [
	"protocol",
	"target",
	"moduleUrl",
	"config"
], s = 8192, c = 32, l = 8192, u = 16, d = /^[A-Za-z][A-Za-z0-9_]{0,63}$/;
function f(e) {
	if (!(e instanceof Uint8Array)) throw TypeError("model source archive must return Uint8Array bytes");
	let t = new Uint8Array(e.byteLength);
	return t.set(e), t.buffer;
}
function p(e, t) {
	if (typeof e != "object" || !e || Array.isArray(e)) throw TypeError("model source module descriptor must be an object");
	let n = Reflect.ownKeys(e);
	if (n.length !== o.length || o.some((e) => !n.includes(e))) throw TypeError("model source module descriptor has unknown or missing fields");
	let c = Object.getOwnPropertyDescriptors(e);
	if (o.some((e) => !c[e]?.enumerable || !("value" in c[e]))) throw TypeError("model source module descriptor fields must be data properties");
	let l = c.protocol.value, u = c.target.value, d = c.moduleUrl.value;
	if (l !== "ooxml-model-source-module/v2") throw TypeError("unsupported model source module protocol");
	if (typeof u != "string" || !i.has(u)) throw TypeError("unsupported model source target");
	if (t !== void 0 && u !== t) throw TypeError(`a ${u} model source module cannot load ${t} input`);
	if (typeof d != "string" || d.length === 0 || d.length > s || d.trim() !== d) throw TypeError("model source moduleUrl must be a nonempty absolute URL");
	let f;
	try {
		f = new URL(d);
	} catch {
		throw TypeError("model source moduleUrl must be a nonempty absolute URL");
	}
	if (!a.has(f.protocol)) throw TypeError("model source moduleUrl protocol is unsupported");
	return Object.freeze({
		protocol: r,
		target: u,
		moduleUrl: d,
		config: m(c.config.value)
	});
}
function m(e) {
	if (!C(e)) throw TypeError("model source config must be a plain object");
	let t = Reflect.ownKeys(e);
	if (t.length > c) throw RangeError(`model source config accepts at most ${c} entries`);
	let n = {};
	for (let r of t) {
		if (typeof r != "string" || !d.test(r)) throw TypeError("model source config keys must be short identifiers");
		let t = Object.getOwnPropertyDescriptor(e, r);
		if (!t?.enumerable || !("value" in t)) throw TypeError("model source config entries must be data properties");
		let i = t.value;
		if (typeof i == "string") {
			if (i.length > l) throw RangeError("model source config string is too long");
		} else if (typeof i == "number") {
			if (!Number.isFinite(i)) throw TypeError("model source config numbers must be finite");
		} else if (typeof i != "boolean" && i !== null) throw TypeError("model source config values must be strings, numbers, booleans or null");
		n[r] = i;
	}
	return Object.freeze(n);
}
async function h(e, r, i, a, o = [], s) {
	let c = p(e);
	t(a, n);
	let l = await import(
		/* @vite-ignore */
		c.moduleUrl
), u = typeof l == "object" && l ? l.openModelSource : void 0;
	if (typeof u != "function") throw TypeError("model source module must export openModelSource()");
	t(a, n);
	let d = await u(r, c.config, a, o, s === void 0 ? void 0 : v(s));
	if (typeof d != "object" || !d) throw TypeError("openModelSource() must return an object");
	let f = d, m = f.close;
	if (typeof m != "function") throw TypeError("an opened model source must provide close()");
	let h = !1, g = () => {
		h || (h = !0, m.call(d));
	};
	try {
		let e = i(f.archive), r = y(f.viewDefaults);
		return t(a, n), Object.freeze({
			archive: e,
			viewDefaults: r,
			close: g
		});
	} catch (e) {
		try {
			g();
		} catch {}
		throw e;
	}
}
function g(e, t) {
	if (t && e === null) return null;
	if (typeof e != "number" || !Number.isSafeInteger(e) || e < 0) throw TypeError("model source context limits must be non-negative safe integers");
	return e;
}
function _(e) {
	let t = typeof e == "object" && e ? e : {};
	return Object.freeze({
		maxRows: g(t.maxRows, !1),
		maxCells: g(t.maxCells, !1),
		maxOwnedUtf8Bytes: g(t.maxOwnedUtf8Bytes, !1),
		maxJsonBytes: g(t.maxJsonBytes, !1)
	});
}
function v(e) {
	let t = e.resourcePolicy, n = Object.freeze({
		maxArchiveEntryBytes: g(t?.maxArchiveEntryBytes, !0),
		maxTotalInflatedBytes: g(t?.maxTotalInflatedBytes, !0),
		maxArchiveEntries: g(t?.maxArchiveEntries, !0)
	}), r = e.worksheetPolicy;
	return Object.freeze(r === void 0 ? { resourcePolicy: n } : {
		resourcePolicy: n,
		worksheetPolicy: Object.freeze({
			worksheet: _(r.worksheet),
			cache: _(r.cache),
			maxCoordinateIndexEntries: g(r.maxCoordinateIndexEntries, !1)
		})
	});
}
function y(e) {
	if (e === void 0) return Object.freeze({});
	if (!C(e)) throw TypeError("model source viewDefaults must be a plain object");
	let t = Reflect.ownKeys(e);
	if (t.length > u) throw RangeError("model source viewDefaults has too many entries");
	let n = {};
	for (let r of t) {
		let t = typeof r == "string" ? Object.getOwnPropertyDescriptor(e, r) : void 0;
		if (typeof r != "string" || !d.test(r) || !t?.enumerable || !("value" in t) || typeof t.value != "boolean") throw TypeError("model source viewDefaults entries must be boolean data properties");
		n[r] = t.value;
	}
	return Object.freeze(n);
}
function b(e, t, n) {
	if (typeof e != "object" && typeof e != "function" || e === null) throw TypeError(`${t} model source archive must be an object`);
	for (let r of n) if (typeof e[r] != "function") throw TypeError(`${t} model source archive must implement ${r}()`);
}
function x(e, t) {
	return (typeof e == "object" || typeof e == "function") && e !== null && typeof e[t] == "function";
}
function S(e) {
	return /* @__PURE__ */ Error(`${e} is unsupported for this source`);
}
function C(e) {
	if (typeof e != "object" || !e || Array.isArray(e)) return !1;
	let t = Object.getPrototypeOf(e);
	return t === Object.prototype || t === null;
}
//#endregion
//#region packages/core/src/errors/ooxml-error.ts
var w = class e extends Error {
	code = "ooxml-resource-limit";
	details;
	constructor(t, n) {
		super(t), this.name = "OoxmlResourceLimitError";
		let r = n.violation, i = Object.freeze({
			format: r.format,
			operation: r.operation,
			resource: r.resource,
			metric: r.metric,
			...r.part === void 0 ? {} : { part: r.part },
			limit: r.limit,
			observed: r.observed,
			configurable: r.configurable,
			usage: Object.freeze({
				archiveEntryCount: r.usage.archiveEntryCount,
				declaredInflatedBytes: r.usage.declaredInflatedBytes,
				...r.usage.largestInflatedEntryBytes === void 0 ? {} : { largestInflatedEntryBytes: r.usage.largestInflatedEntryBytes },
				distinctInflatedBytes: r.usage.distinctInflatedBytes,
				operationInflatedBytes: r.usage.operationInflatedBytes
			})
		});
		this.details = Object.freeze({
			stage: n.stage,
			violation: i
		}), Object.setPrototypeOf(this, e.prototype);
	}
}, ee = "OOXML_RESOURCE_LIMIT:", te = 128, T = 256, E = 4096;
function D(e) {
	return typeof e == "number" && Number.isSafeInteger(e) && e >= 0;
}
function O(e) {
	if (!e || typeof e != "object" || Array.isArray(e)) return !1;
	let t = e;
	return D(t.archiveEntryCount) && D(t.declaredInflatedBytes) && (t.largestInflatedEntryBytes === void 0 || D(t.largestInflatedEntryBytes)) && D(t.distinctInflatedBytes) && D(t.operationInflatedBytes);
}
function k(e) {
	return e === "docx" || e === "xlsx" || e === "pptx";
}
function A(e) {
	return e === "container" || e === "decompression" || e === "parsing" || e === "serialization" || e === "layout" || e === "rendering" || e === "worker";
}
function j(e, t) {
	return typeof e == "string" && e.length > 0 && e.length <= t && !/[\u0000-\u001f\u007f]/u.test(e);
}
function M(e) {
	return j(e, te) && /^[a-z0-9][a-z0-9-]*$/u.test(e);
}
function N(e) {
	return !j(e, E) || e.startsWith("/") || e.startsWith("\\") || e.includes("\\") || e.includes("?") || e.includes("#") || e.includes("://") || /^[a-z]:/iu.test(e) ? !1 : e.split("/").every((e) => e !== "" && e !== "." && e !== "..");
}
var P = new Map([
	["archive-entry:declared-inflated-bytes", {
		stage: "container",
		part: "required"
	}],
	["archive-entry:actual-inflated-bytes", {
		stage: "decompression",
		part: "required"
	}],
	["archive:entry-count", {
		stage: "container",
		part: "forbidden"
	}],
	["archive:central-directory-bytes", {
		stage: "container",
		part: "forbidden",
		configurable: !1
	}],
	["archive:distinct-inflated-bytes", {
		stage: "decompression",
		part: "required"
	}],
	["xml-event:bytes", {
		stage: "parsing",
		part: "optional",
		configurable: !1
	}],
	["xml-context:bytes", {
		stage: "parsing",
		part: "optional",
		configurable: !1
	}],
	["image-effect:work", {
		stage: "parsing",
		part: "forbidden",
		configurable: !1
	}],
	["chartex-allocation:elements", {
		stage: "parsing",
		part: "forbidden",
		configurable: !1
	}],
	["chartex-allocation:bytes", {
		stage: "parsing",
		part: "forbidden",
		configurable: !1
	}],
	["chart-cache:points", {
		stage: "parsing",
		part: "forbidden",
		configurable: !1
	}],
	["numbering-marker:bytes", {
		stage: "parsing",
		part: "forbidden",
		configurable: !1
	}],
	["chart-style-formats:entries", {
		stage: "parsing",
		part: "required",
		configurable: !1
	}],
	["chart-custom-number-formats:entries", {
		stage: "parsing",
		part: "required",
		configurable: !1
	}],
	["chart-number-format-bytes:bytes", {
		stage: "parsing",
		part: "required",
		configurable: !1
	}],
	["xml-tree:depth", {
		stage: "parsing",
		part: "optional",
		configurable: !1
	}],
	["worksheet-row:projected-bytes", {
		stage: "parsing",
		part: "optional",
		configurable: !1
	}],
	["worksheet-shell:projected-bytes", {
		stage: "parsing",
		part: "optional",
		configurable: !1
	}],
	["theme-style-reparse:bytes", {
		stage: "parsing",
		part: "forbidden",
		configurable: !1
	}],
	["style-inheritance:depth", {
		stage: "parsing",
		part: "required",
		configurable: !1
	}],
	["complex-field:depth", {
		stage: "parsing",
		part: "forbidden",
		configurable: !1
	}]
]), F = new Set([...P.keys()].map((e) => e.slice(0, e.indexOf(":")))), I = new Set([...P.keys()].map((e) => e.slice(e.indexOf(":") + 1)));
function L(e) {
	if (!e || typeof e != "object" || Array.isArray(e)) return !1;
	let t = e;
	return !k(t.format) || !j(t.operation, T) || !M(t.resource) || !M(t.metric) || !D(t.limit) || !D(t.observed) || typeof t.configurable != "boolean" || !O(t.usage) ? !1 : !("part" in t) || N(t.part);
}
function R(e) {
	if (!e || typeof e != "object" || Array.isArray(e)) return !1;
	let t = e;
	if (!A(t.stage) || !L(t.violation)) return !1;
	let n = t.violation, r = P.get(`${n.resource}:${n.metric}`);
	return r ? t.stage !== r.stage || r.configurable === !1 && n.configurable !== !1 ? !1 : r.part === "required" ? n.part !== void 0 : r.part === "forbidden" ? n.part === void 0 : !0 : !(F.has(n.resource) && I.has(n.metric));
}
function z(e) {
	let t = e.violation;
	return `OOXML resource limit exceeded${t.part ? ` for ${t.part}` : ""} (${t.resource}, ${e.stage}): ${t.metric} ${t.observed} > ${t.limit}`;
}
function B(e) {
	let t = e instanceof Error ? e.message : String(e);
	if (!t.startsWith(ee)) return;
	let n;
	try {
		n = JSON.parse(t.slice(21));
	} catch {
		return;
	}
	if (!n || typeof n != "object") return;
	let r = n;
	if (!(r.code !== "ooxml-resource-limit" || !R(r.details))) return new w(z(r.details), r.details);
}
function ne(e) {
	try {
		return e();
	} catch (e) {
		throw e instanceof w || typeof e != "string" && !(e instanceof Error) ? e : B(e) ?? e;
	}
}
//#endregion
//#region packages/core/src/worker/wasm-guard.ts
function V(e) {
	let t = globalThis.WebAssembly?.RuntimeError;
	return t && e instanceof t || e instanceof RangeError ? !0 : e instanceof Error ? e.name === "RuntimeError" || e.name === "CompileError" || e.name === "LinkError" || e.name === "InternalError" || e.name === "OOMError" : !1;
}
//#endregion
//#region packages/core/src/source/worker-model-source.ts
function H(e, t) {
	return new Proxy(e, { get(e, n) {
		if (n === t) return (...n) => new Uint8Array(f(Reflect.apply(e[t], e, n)));
		let r = Reflect.get(e, n);
		return typeof r == "function" ? r.bind(e) : r;
	} });
}
function U(e, t) {
	try {
		return ne(e);
	} catch (e) {
		if (V(e)) try {
			t();
		} catch {}
		throw e;
	}
}
//#endregion
//#region packages/xlsx/src/internal/host-layout.ts
var W = "xlsx-host-layout-request", G = 4096, K = 255, q = 65535 / 20, J = 4096;
function Y(e) {
	if (!(e instanceof Uint8Array) || e.byteLength > G) throw RangeError("XLSX host layout request byte budget exceeded");
	let t;
	try {
		t = JSON.parse(new TextDecoder("utf-8", { fatal: !0 }).decode(e));
	} catch {
		throw TypeError("invalid XLSX host layout request");
	}
	return t === null ? null : X(t);
}
function X(e) {
	if (typeof e != "object" || !e || Array.isArray(e)) throw TypeError("invalid XLSX host layout font");
	let t = Object.keys(e), n = [
		"family",
		"sizePt",
		"bold",
		"italic"
	];
	if (t.length !== n.length || !n.every((t) => Object.hasOwn(e, t))) throw TypeError("invalid XLSX host layout font");
	let { family: r, sizePt: i, bold: a, italic: o } = e;
	if (typeof r != "string" || r.length === 0 || r.length > K || typeof i != "number" || !Number.isFinite(i) || i <= 0 || i > q || typeof a != "boolean" || typeof o != "boolean") throw TypeError("invalid XLSX host layout font");
	return Object.freeze({
		family: r,
		sizePt: i,
		bold: a,
		italic: o
	});
}
function Z(e) {
	return typeof e == "number" && Number.isInteger(e) && e >= 1 && e <= J ? e : void 0;
}
async function re(e, t) {
	if (typeof e.host_layout_request != "function") return;
	if (typeof e.configure_host_layout != "function") throw TypeError("XLSX model source archive must implement configure_host_layout()");
	let n = Y(e.host_layout_request()), r = n ? Z(await t(n)) : void 0;
	return e.configure_host_layout(r), r;
}
var ie = 1;
function ae(e, t) {
	let n = ie++;
	return new Promise((r) => {
		let i = (t) => {
			let a = t.data;
			!Q(a) || a.requestId !== n || (e.removeEventListener("message", i), r(Z(a.maximumDigitWidth)));
		};
		e.addEventListener("message", i);
		try {
			e.postMessage({
				type: W,
				requestId: n,
				font: t
			});
		} catch {
			e.removeEventListener("message", i), r(void 0);
		}
	});
}
function Q(e) {
	return typeof e == "object" && !!e && e.type === "xlsx-host-layout-result" && typeof e.requestId == "number";
}
//#endregion
//#region packages/xlsx/src/internal/worker-worksheet-source.ts
var oe = [
	"open_sheet_cursor",
	"pull_sheet_cursor",
	"sheet_cursor_pull_finished",
	"acknowledge_sheet_cursor_terminal",
	"cancel_sheet_cursor",
	"close_sheet_cursor",
	"assert_healthy",
	"parse",
	"extract_image"
];
function $(e) {
	return b(e, "XLSX", oe), e;
}
function se(e) {
	let [t] = Object.keys(e);
	if (t !== void 0) throw TypeError(`unsupported XLSX model source view default: ${t}`);
}
var ce = (e, t, n, r) => h(e, t, $, void 0, n, r), le = class {
	ooxmlHost;
	openSource;
	modelSource;
	measuredMaximumDigitWidth;
	copyBytes(e) {
		return f(e);
	}
	isHostLayoutResult(e) {
		return Q(e);
	}
	requestHostLayoutFromPage(e, t) {
		return ae(e, t);
	}
	extractImage(e) {
		return this.execute((t) => this.copyBytes(t.extract_image(e)));
	}
	constructor(e, t = ce) {
		this.ooxmlHost = e, this.openSource = t;
	}
	get kind() {
		return this.modelSource ? "model-source" : "ooxml";
	}
	async openModelSource(e, t, n, r = [], i) {
		if (this.modelSource || this.ooxmlHost.archive) throw Error("Workbook source already loaded");
		let a = await this.openSource(t, e, r, i);
		try {
			if (se(a.viewDefaults), this.modelSource || this.ooxmlHost.archive) throw Error("Workbook source open was superseded");
		} catch (e) {
			try {
				a.close();
			} catch {}
			throw e;
		}
		let o = H(a.archive, "pull_sheet_cursor"), s = {
			archive: a.archive,
			transferArchive: o,
			close: a.close
		};
		this.modelSource = s;
		try {
			if (this.measuredMaximumDigitWidth = await re(a.archive, n), this.modelSource !== s) throw Error("Workbook source open was superseded");
		} catch (e) {
			if (this.modelSource === s) try {
				this.closeModelSource();
			} catch {}
			throw e;
		}
	}
	get maximumDigitWidth() {
		return this.measuredMaximumDigitWidth;
	}
	cursor() {
		return this.modelSource?.archive ?? this.ooxmlHost.archive;
	}
	execute(e) {
		let t = this.modelSource;
		if (!t) {
			let t = this.ooxmlHost.archive;
			if (!t) throw Error("Workbook not loaded");
			return this.ooxmlHost.run(() => e(t));
		}
		return U(() => e(t.transferArchive), () => {
			this.modelSource === t && this.closeModelSource();
		});
	}
	resourceUsage() {
		let e = this.modelSource;
		if (e) return x(e.archive, "resource_usage") ? this.execute(() => e.archive.resource_usage()) : void 0;
		let t = this.ooxml();
		return this.ooxmlHost.run(() => t.resource_usage());
	}
	toMarkdown() {
		let e = this.modelSource;
		if (e) {
			if (!x(e.archive, "to_markdown")) throw S("Markdown conversion");
			return this.execute(() => e.archive.to_markdown());
		}
		let t = this.ooxml();
		return this.ooxmlHost.run(() => t.to_markdown());
	}
	closeModelSource() {
		let e = this.modelSource;
		this.modelSource = void 0, this.measuredMaximumDigitWidth = void 0, e?.close();
	}
	ooxml() {
		let e = this.ooxmlHost.archive;
		if (!e) throw Error("Workbook not loaded");
		return e;
	}
};
//#endregion
export { le as WorkerWorksheetSourceOwner };
