import { n as e } from "./cjk-fallback-CxqXJu32.js";
import { n as t } from "./renderer-module-contract-BuTx2FWJ.js";
import { i as n, n as r } from "./resource-debug-D8EBjKbZ.js";
import { t as i } from "./rejected-load-CS5sDp04.js";
import { t as a } from "./presentation-C1LgjJBF.js";
import { u as o } from "./source-DncDPEPn.js";
import { t as s } from "./bundled-asset-url-BMJ8vNHP.js";
import { t as c } from "./deferred-D2gd0MY2.js";
import { i as l, n as u, r as d, s as f } from "./model-source-BwpDCGYU.js";
async function p(s, l) {
	let p = l.mode ?? "main";
	p === "main" && l.fonts && import("./font-source-load-Br2RCNdG.js").catch(() => void 0);
	let g = n(l), _ = new r({
		enabled: !0,
		format: "pptx",
		mode: p,
		policy: g.policy,
		onMetrics: g.onResourceMetrics,
		emitToConsole: g.debug
	});
	try {
		if (p === "worker" && (typeof Worker > "u" || typeof OffscreenCanvas > "u")) throw Error("mode: 'worker' requires Worker and OffscreenCanvas support");
		let n;
		if (typeof s == "string") {
			let e = await fetch(s);
			if (!e.ok) throw Error(`Failed to fetch: ${e.status} ${e.statusText}`);
			n = await e.arrayBuffer();
		} else n = s;
		let r = f(d(l.legacyPpt, l.odp), "pptx", new Uint8Array(n));
		if (!r) return a.load(n, {
			...l,
			legacyPpt: void 0,
			odp: void 0
		});
		let v = u(r, "pptx");
		try {
			_.setSourceBytes(n.byteLength), _.checkpoint("container ready");
			let r = p === "worker" ? (await import("./render-worker-host-DznCpFun.js")).createRenderWorker() : new (await (import("./worker-source-Ct2Uw1YR.js"))).default(), s = m(r, v), u = p === "worker" ? t(l) : void 0, d;
			try {
				d = new a(s, p, l.wasmUrl);
				let t = d;
				t._metrics = _, t._cjkFallback = e(l.cjkFallback), t._math = p === "worker" ? void 0 : l.math, t._threeD = p === "worker" ? void 0 : l.threeD, t._regionMap = p === "worker" ? void 0 : l.regionMap, t._chartEx = p === "worker" ? void 0 : l.chartEx, t._tiff = p === "worker" ? void 0 : l.tiff, t._fonts = o(l.fonts), t._parsedTextChain = !1, h(l, p, u);
				let r = l.progressiveLayout ? {
					onProgress: l.onLayoutProgress,
					onPartial: l.onLayoutPartial,
					onComplete: l.onLayoutComplete,
					firstPublication: c(),
					published: !1,
					deferred: !1,
					settled: !1
				} : void 0;
				return await t._parse(n, g.policy, o(l.fonts), l.workerTimeoutMs, (e) => _.observeUsage(e), u, r), _.checkpoint("presentation preflight ready"), p === "main" && l.fonts && t._preflight && !r && await t._ensureFontSources(t._preflight.fontPreloadNames, t._preflight.fontPreloadFacts, t._preflight.fontPreloadDemand), _.succeed({ slides: d.slideCount }), v.release(), d;
			} catch (e) {
				let t = d;
				throw i(r, t ? () => t.destroy() : void 0), e;
			}
		} finally {
			v.release();
		}
	} catch (e) {
		throw _.fail(e), e;
	}
}
function m(e, t) {
	let n = s(new URL("./pptx-source-worker.mjs", import.meta.url).href, import.meta.url);
	return l(e, {
		discriminator: "kind",
		load: t,
		parseMessage: (e) => ({
			...e,
			source: t.module,
			sourceOwnerUrl: n,
			...t.transfer.length ? { sourceTransfer: t.transfer } : {}
		})
	});
}
function h(e, t, n) {
	t === "worker" && (e.math && !n?.math && console.warn("[ooxml] a custom math renderer cannot cross the worker boundary; equations will be skipped in mode: 'worker'. Use the math renderer from @silurus/ooxml/math."), e.threeD && !n?.threeD && console.warn("[ooxml] a custom 3-D chart renderer cannot cross the worker boundary; charts use their 2-D family fallback in mode: 'worker'. Use the renderer from @silurus/ooxml/three-d."), e.regionMap && !n?.regionMap && console.warn("[ooxml] a custom Region Map renderer cannot cross the worker boundary; geospatial charts use the unsupported-chart placeholder in mode: 'worker'. Use the renderer from @silurus/ooxml/region-map."), e.chartEx && !n?.chartEx && console.warn("[ooxml] a custom ChartEx renderer cannot cross the worker boundary; ChartEx charts use the unsupported-chart placeholder in mode: 'worker'. Use the renderer from @silurus/ooxml/chart-ex."), e.tiff && !n?.tiff && console.warn("[ooxml] a custom TIFF codec cannot cross the worker boundary; recognized TIFF images will use an unavailable-image placeholder in mode: 'worker'. Use the codec from @silurus/ooxml/tiff to display them."));
}
export { p as loadPptxModelSource };
