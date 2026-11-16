import { n as e } from "./ooxml-error-DbICW35n.js";
import { S as t } from "./resource-policy.generated-D_HlV2Rm.js";
import { n } from "./abort-JztSoyw2.js";
import { a as r, o as i, t as a } from "./error-wire-Dr1HjXGZ.js";
import { t as o } from "./transfer-D3T5fQj4.js";
import { i as s, n as c, r as l, t as u } from "./pull-session-CJuB3jmq.js";
import { n as d, r as f, t as p } from "./resource-measurement-b6dkzjLJ.js";
import { t as m } from "./worksheet-policy-G1KBtmuQ.js";
import { t as h } from "./worksheet-policy-context-CntId_kd.js";
var g = t, _ = Object.freeze({
	archiveEntryCount: 0,
	declaredInflatedBytes: 0,
	distinctInflatedBytes: 0,
	operationInflatedBytes: 0
});
function v(e, t = m) {
	let { maxCells: n, maxOwnedUtf8Bytes: r } = t.worksheet, i = e.reduce((e, t) => p(e, t.cells.length, n), 0);
	return {
		rows: e.length,
		cells: i,
		ownedUtf8Bytes: e.reduce((e, t) => t.cells.reduce((e, t) => {
			let n = d(t.value, r).stringValueUtf8Bytes;
			return p(e, p(n, t.formula === void 0 ? 0 : f(t.formula, r), r), r);
		}, e), 0)
	};
}
function y(e, t = m) {
	return b(e, v(e.rows, t), t);
}
function b(e, t, n = m) {
	let r = d(e, n.worksheet.maxJsonBytes);
	return {
		...t,
		jsonBytes: r.jsonBytes
	};
}
function x(e, t, n = m) {
	let r = n.worksheet;
	return {
		rows: p(e.rows, t.rows, r.maxRows),
		cells: p(e.cells, t.cells, r.maxCells),
		ownedUtf8Bytes: p(e.ownedUtf8Bytes, t.ownedUtf8Bytes, r.maxOwnedUtf8Bytes)
	};
}
function S(e, t, n = {}, r = m) {
	let i = r.cache, a = e.rows - (n.rows ?? 0), o = e.cells - (n.cells ?? 0), s = e.ownedUtf8Bytes - (n.ownedUtf8Bytes ?? 0), c = e.jsonBytes - (n.jsonBytes ?? 0);
	if (a < 0 || o < 0 || s < 0 || c < 0) throw Error("worksheet cache accounting underflow");
	return {
		rows: p(a, t.rows, i.maxRows),
		cells: p(o, t.cells, i.maxCells),
		ownedUtf8Bytes: p(s, t.ownedUtf8Bytes, i.maxOwnedUtf8Bytes),
		jsonBytes: p(c, t.jsonBytes, i.maxJsonBytes)
	};
}
function C(t, n, i, a, o, s, c, l = i !== "delimited-text-source") {
	let u = i === "worksheet-json" ? "serialization" : "parsing";
	return new e(r({
		stage: u,
		violation: {
			part: n,
			resource: i,
			metric: a,
			observed: s,
			limit: o
		}
	}), {
		stage: u,
		violation: {
			format: "xlsx",
			operation: t,
			resource: i,
			metric: a,
			...n === void 0 ? {} : { part: n },
			limit: o,
			observed: Math.min(s, o + 1),
			configurable: l,
			usage: c ?? _
		}
	});
}
function w(e, t, n, r, i = m) {
	let a = i.worksheet, o = [
		[
			"rows",
			e.rows,
			a.maxRows
		],
		[
			"cells",
			e.cells,
			a.maxCells
		],
		[
			"owned-utf8-bytes",
			e.ownedUtf8Bytes,
			a.maxOwnedUtf8Bytes
		]
	];
	for (let [e, i, a] of o) if (i > a) throw C(t, n, e === "owned-utf8-bytes" ? "worksheet-cell-content" : "worksheet-model", e, a, i, r);
}
function T(e, t, n, r, i = m) {
	let a = i.worksheet.maxJsonBytes;
	if (e > a) throw C(t, n, "worksheet-json", "bytes", a, e, r);
}
function E(e, t, n, r, i = m) {
	let a = i.cache;
	if (e.rows > a.maxRows) throw C(t, n, "worksheet-cache", "rows", a.maxRows, e.rows, r);
	if (e.cells > a.maxCells) throw C(t, n, "worksheet-cache", "cells", a.maxCells, e.cells, r);
	if (e.ownedUtf8Bytes > a.maxOwnedUtf8Bytes) throw C(t, n, "worksheet-cache", "owned-utf8-bytes", a.maxOwnedUtf8Bytes, e.ownedUtf8Bytes, r);
	if (e.jsonBytes > a.maxJsonBytes) throw C(t, n, "worksheet-cache", "bytes", a.maxJsonBytes, e.jsonBytes, r);
}
function D(e, t) {
	return O(e.rows, t), e;
}
function O(e, t) {
	for (let n of e) for (let e of n.cells) {
		let n = e.value;
		if (n.type === "shared") {
			let r = t[n.si];
			if (r) {
				let t = {
					type: "text",
					text: r.text
				};
				r.runs !== void 0 && (t.runs = r.runs), r.phoneticRuns !== void 0 && (t.phoneticRuns = r.phoneticRuns), r.phoneticPr !== void 0 && (t.phoneticPr = r.phoneticPr), e.value = t;
			} else e.value = {
				type: "text",
				text: ""
			};
		}
	}
	return e;
}
var k = new Set([
	"outline",
	"merge",
	"conditional-format",
	"ancillary-content",
	"metadata-unavailable",
	"unordered-rows"
]);
function A(e, t, n, r) {
	let i = e instanceof ArrayBuffer ? new Uint8Array(e) : new Uint8Array(e.buffer, e.byteOffset, e.byteLength), a = JSON.parse(new TextDecoder().decode(i));
	if (!a || typeof a != "object" || !("kind" in a)) throw Error("worksheet cursor returned an invalid unit");
	let o = a;
	if (t !== (o.kind === "finished")) throw Error("worksheet cursor terminal marker mismatch");
	if (o.kind === "rows") {
		if (!Array.isArray(o.rows)) throw Error("worksheet row unit is missing rows");
		return n && O(o.rows, n), r?.(o.rows), {
			kind: "rows",
			rows: o.rows
		};
	}
	if (o.kind === "preview") {
		if (!Number.isSafeInteger(o.maxRow) || !Number.isSafeInteger(o.maxCol) || o.maxRow < 0 || o.maxCol < 0 || o.worksheet === null == (o.reason === null) || o.worksheet !== null && (typeof o.worksheet != "object" || Array.isArray(o.worksheet)) || o.reason !== null && !k.has(o.reason)) throw Error("worksheet preview unit is invalid");
		return o.worksheet && (o.worksheet.rows = []), o;
	}
	if (o.kind === "finished") {
		if (!o.worksheet || typeof o.worksheet != "object") throw Error("worksheet terminal unit is missing its worksheet");
		return o.worksheet.rows = [], {
			kind: "finished",
			worksheet: o.worksheet
		};
	}
	throw Error("worksheet cursor returned an unknown unit kind");
}
var j = 64 * 1024 * 1024, M = class {
	archive;
	acceptWorksheet;
	executeArchive;
	prepareRows;
	provisional;
	worksheetPolicy;
	coordinator = new s();
	sessions = /* @__PURE__ */ new Map();
	operationTail = Promise.resolve();
	pendingOpens = /* @__PURE__ */ new Map();
	resourceFailure;
	constructor(e, t, n = (e) => e(this.requireArchive()), r, i, a = () => m) {
		this.archive = e, this.acceptWorksheet = t, this.executeArchive = n, this.prepareRows = r, this.provisional = i, this.worksheetPolicy = a;
	}
	reserveOpen(e) {
		this.pendingOpens.set(e.sessionId, {
			identity: e,
			canceled: !1
		});
	}
	abandonOpen(e) {
		this.pendingOpens.delete(e);
	}
	get pendingOpenCount() {
		return this.pendingOpens.size;
	}
	runDuringPull(t) {
		return this.sessions.size === 0 ? this.run(t) : this.coordinator.enqueue(async () => {
			if (this.resourceFailure) throw this.resourceFailure;
			try {
				return t();
			} catch (t) {
				throw t instanceof e && (this.resourceFailure ??= t), t;
			}
		});
	}
	async open(t, n, r) {
		if (this.resourceFailure) throw this.resourceFailure;
		let i = this.pendingOpens.get(r.sessionId);
		if (!i || i.identity.operationId !== r.operationId || i.identity.generation !== r.generation) throw Error("worksheet pull session open reservation is stale or missing");
		let a = this.worksheetPolicy(), s, c = new Promise((e) => {
			s = e;
		}), u = this.operationTail.then(() => this.coordinator.enqueue(async () => {
			if (i.canceled) throw Error("worksheet pull session open was canceled");
			this.executeArchive((e) => e.open_sheet_cursor(t, n));
			let c = [], u = {
				rows: 0,
				cells: 0,
				ownedUtf8Bytes: 0
			}, d, f = !1, p = new l({
				...r,
				maxByteCredit: j,
				coordinator: this.coordinator,
				driver: {
					pull: () => {
						let n = this.executeArchive((e) => e.pull_sheet_cursor(128)), r = this.executeArchive((e) => e.sheet_cursor_pull_finished());
						if (this.acceptWorksheet) {
							let i = A(n, r, void 0, this.prepareRows);
							try {
								if (i.kind === "preview") i.worksheet && (i.worksheet.rows = c, h(i.worksheet, a), this.provisional?.preview(t, i.worksheet));
								else if (i.kind === "rows") {
									let e = x(u, v(i.rows, a), a);
									w(e, "get-worksheet-worker", void 0, this.readResourceUsage(), a), c.push(...i.rows), u = e;
								} else i.kind === "finished" && (d = i.worksheet);
							} catch (t) {
								throw t instanceof e && (this.resourceFailure ??= t), t;
							}
						}
						f = r;
						let i = o(n);
						return {
							payload: i,
							byteLength: i.byteLength,
							done: r,
							transfer: [i]
						};
					},
					measureChunk: ({ payload: e }) => e.byteLength,
					acknowledge: () => {
						if (!f) return;
						let n, i;
						try {
							if (this.acceptWorksheet) {
								if (!d) throw Error("worksheet terminal payload is missing");
								d.rows = d.parseError ? [] : c;
								let e = d.parseError ? {
									rows: 0,
									cells: 0,
									ownedUtf8Bytes: 0
								} : u, r = b(d, e, a), o = this.readResourceUsage();
								w(r, "get-worksheet-worker", void 0, o, a), T(r.jsonBytes, "get-worksheet-worker", void 0, o, a), h(d, a);
								let s = this.acceptWorksheet(t, d, r, o);
								typeof s == "function" ? n = s : s && ({rollback: n, commit: i} = s);
							}
							this.executeArchive((e) => e.acknowledge_sheet_cursor_terminal()), i?.();
						} catch (t) {
							throw n?.(), t instanceof e && (this.resourceFailure ??= t), t;
						}
						f = !1, this.sessions.delete(r.sessionId), this.provisional?.stop(t), s();
					},
					cancel: () => {
						try {
							this.archive() && this.executeArchive((e) => e.cancel_sheet_cursor());
						} finally {
							this.sessions.delete(r.sessionId), this.provisional?.stop(t), s();
						}
					},
					close: () => {
						try {
							this.archive() && this.executeArchive((e) => e.close_sheet_cursor());
						} finally {
							this.sessions.delete(r.sessionId), this.provisional?.stop(t), s();
						}
					},
					resourceUsage: () => this.readResourceUsage()
				}
			});
			this.sessions.set(r.sessionId, {
				host: p,
				identity: r
			}), this.pendingOpens.delete(r.sessionId);
		}));
		this.operationTail = u.then(() => c, () => void 0);
		try {
			await u;
		} catch (e) {
			throw this.pendingOpens.delete(r.sessionId), s(), e;
		}
	}
	async postOpenedSafely(e, t, n) {
		try {
			t();
		} catch (t) {
			await this.closeIdentity(e);
			try {
				n(t);
			} catch {}
		}
	}
	dispatch(e, t) {
		let n = this.sessions.get(e.sessionId);
		if (n) return n.host.dispatch(e, t);
		let r = this.pendingOpens.get(e.sessionId);
		if (r && (e.kind === "cancel" || e.kind === "close")) {
			let n = r.identity.operationId === e.operationId && r.identity.generation === e.generation;
			return n && (r.canceled = !0), t(n ? {
				protocol: c,
				kind: "accepted",
				sessionId: e.sessionId,
				operationId: e.operationId,
				generation: e.generation,
				requestId: e.requestId,
				command: e.kind
			} : {
				protocol: c,
				kind: "error",
				sessionId: e.sessionId,
				operationId: e.operationId,
				generation: e.generation,
				requestId: e.requestId,
				error: {
					message: "stale lifecycle targets another pending worksheet operation",
					errorName: "PullSessionProtocolError",
					code: "ooxml-stale-lifecycle"
				}
			}), Promise.resolve();
		}
		return e.kind === "cancel" || e.kind === "close" ? (t({
			protocol: c,
			kind: "accepted",
			sessionId: e.sessionId,
			operationId: e.operationId,
			generation: e.generation,
			requestId: e.requestId,
			command: e.kind
		}), Promise.resolve()) : (t({
			protocol: c,
			kind: "error",
			sessionId: e.sessionId,
			operationId: e.operationId,
			generation: e.generation,
			requestId: e.requestId,
			error: i(/* @__PURE__ */ Error("worksheet pull session is not open"))
		}), Promise.resolve());
	}
	async dispatchSafely(e, t) {
		try {
			await this.dispatch(e, t);
		} catch (n) {
			try {
				t({
					protocol: c,
					kind: "error",
					sessionId: e.sessionId,
					operationId: e.operationId,
					generation: e.generation,
					requestId: e.requestId,
					error: i(n)
				});
			} catch {}
		}
	}
	run(t) {
		let n = this.operationTail.then(() => this.coordinator.enqueue(async () => {
			if (this.resourceFailure) throw this.resourceFailure;
			return t();
		})).catch((t) => {
			throw t instanceof e && (this.resourceFailure ??= t), t;
		});
		return this.operationTail = n.then(() => void 0, () => void 0), n;
	}
	async reset() {
		for (let e of this.pendingOpens.values()) e.canceled = !0;
		let e = 1;
		for (let { host: t, identity: n } of [...this.sessions.values()]) await t.dispatch({
			protocol: c,
			kind: "close",
			...n,
			requestId: e++
		}, () => void 0);
		this.sessions.clear(), await this.operationTail, this.pendingOpens.clear(), this.resourceFailure = void 0;
	}
	requireArchive() {
		let e = this.archive();
		if (!e) throw Error("Workbook not loaded");
		return e;
	}
	async closeIdentity(e) {
		let t = this.sessions.get(e.sessionId);
		if (t) {
			await t.host.dispatch({
				protocol: c,
				kind: "close",
				...e,
				requestId: 1
			}, () => void 0);
			return;
		}
		let n = this.pendingOpens.get(e.sessionId);
		n && n.identity.operationId === e.operationId && n.identity.generation === e.generation && (n.canceled = !0);
	}
	readResourceUsage() {
		return a(this.executeArchive((e) => e.sheet_cursor_resource_usage()));
	}
}, N = "XLSX workbook session was aborted", P = class {
	options;
	active = /* @__PURE__ */ new Set();
	nextSessionId = 1;
	constructor(e) {
		if (this.options = e, e.generation !== void 0 && (!Number.isSafeInteger(e.generation) || e.generation <= 0)) throw TypeError("generation must be a positive safe integer");
	}
	async *stream(e, t, r) {
		if (!Number.isSafeInteger(e) || e < 0) throw RangeError("sheetIndex must be a non-negative safe integer");
		if (!t) throw TypeError("sheetName must be non-empty");
		n(r, N);
		let i = this.nextSessionId++, a = {
			sessionId: i,
			operationId: i,
			generation: this.options.generation ?? 1
		}, o = new u(this.options.transport, {
			...a,
			maxByteCredit: j,
			timeoutMs: this.options.timeoutMs,
			disposeTransferred: this.options.disposeTransferred
		});
		this.active.add(o);
		let s = !1, c;
		try {
			for (await this.options.open(e, t, a, this.options.timeoutMs);;) {
				n(r, N);
				let e = await o.pull(j, { signal: r });
				try {
					let t = e.usage ?? o.usageCheckpoint;
					t && this.options.onUsage?.(t);
					let n = A(e.payload, e.done, this.options.sharedStrings);
					if (yield n.kind === "preview" ? {
						...n,
						sequence: e.sequence,
						wireBytes: e.byteLength,
						usage: t
					} : n.kind === "rows" ? {
						kind: "rows",
						rows: n.rows,
						sequence: e.sequence,
						wireBytes: e.byteLength,
						usage: t
					} : {
						kind: "finished",
						worksheet: n.worksheet,
						sequence: e.sequence,
						wireBytes: e.byteLength,
						usage: t
					}, await e.ack({ signal: r }), n.kind === "finished") {
						s = !0;
						return;
					}
				} finally {
					e.disposeTransferred();
				}
			}
		} catch (e) {
			throw c = e, e;
		} finally {
			let e;
			try {
				s || await o.cancel(I(c));
			} catch (t) {
				e = t;
			} finally {
				this.active.delete(o);
			}
			if (c === void 0 && e !== void 0) throw e;
		}
	}
	async cancelAll(e = "closed") {
		let t = (await Promise.allSettled([...this.active].map((t) => t.cancel(e)))).find((e) => e.status === "rejected");
		if (t) throw t.reason;
	}
};
function F(e) {
	return !!e && typeof e == "object" && e.protocol === "ooxml-pull-v1";
}
function I(e) {
	return e && typeof e == "object" && "name" in e && e.name === "AbortError" ? "abort" : e === void 0 ? "closed" : "request-error";
}
export { D as a, x as c, w as d, b as f, C as h, A as i, E as l, y as m, F as n, g as o, v as p, M as r, S as s, P as t, T as u };
