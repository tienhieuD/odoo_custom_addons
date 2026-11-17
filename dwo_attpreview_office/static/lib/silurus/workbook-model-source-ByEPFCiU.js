import { n as e } from "./cjk-fallback-CxqXJu32.js";
import { a as t, g as n } from "./renderer-D-5lFQlk.js";
import { i as r, n as i } from "./resource-debug-D8EBjKbZ.js";
import { t as a } from "./rejected-load-CS5sDp04.js";
import { n as o } from "./bundled-asset-url-Cv8ajMAZ.js";
import { n as s } from "./worksheet-policy-G1KBtmuQ.js";
import { n as c, r as l } from "./worker-protocol-DQ4IlKqk.js";
import { i as u, n as d, r as f, s as p } from "./model-source-BwpDCGYU.js";
import { n as m } from "./host-layout-Cz_lCuTZ.js";
async function h(t, o, u) {
	let m = s(o);
	o = {
		...o,
		xlsxWorksheetLimits: m.worksheet
	}, o = {
		...o,
		cjkFallback: e(o.cjkFallback)
	};
	let h = r(o), _ = o.mode ?? "main", v = new i({
		enabled: !0,
		format: "xlsx",
		mode: _,
		policy: h.policy,
		formatLimits: { xlsxWorksheetLimits: { ...m.worksheet } },
		onMetrics: h.onResourceMetrics,
		emitToConsole: h.debug
	});
	try {
		if (_ === "worker" && (typeof Worker > "u" || typeof OffscreenCanvas > "u")) throw Error("mode: 'worker' requires Worker and OffscreenCanvas support");
		let e;
		if (typeof t == "string") {
			let n = await fetch(t);
			if (!n.ok) throw Error(`Failed to fetch: ${n.status} ${n.statusText}`);
			e = await n.arrayBuffer();
		} else e = t;
		let r = p(f(o.legacyXls, o.ods), "xlsx", new Uint8Array(e));
		if (!r) return u.load(e, {
			...o,
			legacyXls: void 0,
			ods: void 0
		});
		let i = u;
		class s extends i {
			sourceMdw;
			async getWorksheet(e) {
				let t = await super.getWorksheet(e);
				return this.sourceMdw !== void 0 && n(t, this.sourceMdw), t;
			}
			async renderViewport(e, t, n, r = {}) {
				let i = this.sourceMdw !== void 0 && !c(r).layoutMetrics ? l(r, this.sourceMdw) : r;
				return super.renderViewport(e, t, n, i);
			}
		}
		let m = d(r, "xlsx");
		try {
			v.setSourceBytes(e.byteLength), v.checkpoint("container ready");
			let t = _ === "worker" ? (await import("./render-worker-host-BLcI-NEt.js")).createRenderWorker() : new (await (import("./worker-source-CswzFCb1.js"))).default(), n, r = g(t, m, o, (e) => {
				n && (n.sourceMdw = e);
			});
			try {
				n = new s(r, _, o.wasmUrl);
				let t = n;
				return t.metrics = v, await t._load(e, o, h.policy, (e) => v.observeUsage(e), !0), n.sourceMdw !== void 0 && t.parsedWorkbook && (t.parsedWorkbook.layoutMetrics = { maximumDigitWidth: n.sourceMdw }), v.checkpoint("workbook index ready"), v.succeed({ sheets: n.sheetCount }), m.release(), n;
			} catch (e) {
				let r = n;
				throw a(t, r ? () => r.destroy() : void 0), e;
			}
		} finally {
			m.release();
		}
	} catch (e) {
		throw v.fail(e), e;
	}
}
function g(e, n, r, i) {
	let a = o(new URL("./xlsx-source-worker.mjs", import.meta.url).href, import.meta.url);
	return u(e, {
		discriminator: "type",
		load: n,
		parseMessage: (e) => ({
			...e,
			source: n.module,
			sourceOwnerUrl: a,
			...n.transfer.length ? { sourceTransfer: n.transfer } : {}
		}),
		member: (e, n) => {
			if (n === "addEventListener") return (n, r) => n === "message" ? e.addEventListener("message", ((a) => {
				let o = a.data;
				o.type === "parsed" && o.layoutMetrics && i(o.layoutMetrics.maximumDigitWidth), n === "message" && m((t) => e.postMessage(t), a.data, (e) => t(e.family, e.sizePt, void 0, void 0, e.bold ? 700 : 400, e.italic ? "italic" : "normal")), r(a);
			})) : e.addEventListener(n, r);
		}
	});
}
export { h as loadXlsxModelSource };
