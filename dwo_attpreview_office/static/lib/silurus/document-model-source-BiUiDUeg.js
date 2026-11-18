import { i as e } from "./embedded-B4q5SDVm.js";
import { i as t } from "./office-fallback-O-L6rrDh.js";
import { dt as n, fi as r } from "./document-content-DXDaB_ij.js";
import { n as i } from "./cjk-fallback-CxqXJu32.js";
import { n as a } from "./renderer-module-contract-BuTx2FWJ.js";
import { i as o, n as s } from "./resource-debug-D8EBjKbZ.js";
import { t as c } from "./rejected-load-CS5sDp04.js";
import { n as l } from "./bundled-asset-url-Cv8ajMAZ.js";
import { u } from "./source-GXgH3t1X.js";
import { t as d } from "./deferred-D2gd0MY2.js";
import { _ as f, d as p, g as m, h, l as g, t as _, v } from "./document-CexDucFg.js";
import { C as y, T as b, a as x, d as S, f as C, g as w, h as T, l as E, o as D, s as O } from "./document-pull-client-DsaDuAP-.js";
import { i as k, n as A, r as j, s as M } from "./model-source-BwpDCGYU.js";
function N(e) {
	let t = l(new URL("./docx-source-worker.mjs", import.meta.url).href, import.meta.url);
	return e.transfer.length > 0 ? {
		source: e.module,
		sourceTransfer: e.transfer,
		sourceOwnerUrl: t
	} : {
		source: e.module,
		sourceOwnerUrl: t
	};
}
function P(e, t) {
	if (t === void 0) return;
	let r = n(e), i = r.activeLayoutOptions;
	if (!i || i.showTrackedChanges === !0 === t) return;
	let a = b(i.currentDateMs, r.defaultCurrentDateMs, t);
	r.activeLayoutOptions = a, e._progressive && (e._progressive.layoutOptions = a);
}
async function F(l, k = {}, N) {
	let F = N?.signal, L = () => {
		if (F?.aborted) throw new w();
	};
	L();
	let R = i(k.cjkFallback), z = o(k), B = Date.now(), V = k.mode ?? "main";
	V === "main" && k.fonts && import("./font-source-load-DtHoLLYl.js").catch(() => void 0);
	let H = new s({
		enabled: !0,
		format: "docx",
		mode: V,
		policy: z.policy,
		onMetrics: z.onResourceMetrics,
		emitToConsole: z.debug
	});
	try {
		if (V === "worker" && (typeof Worker > "u" || typeof OffscreenCanvas > "u")) throw Error("mode: 'worker' requires Worker and OffscreenCanvas support");
		let i;
		if (typeof l == "string") {
			let e = await fetch(l, { signal: F });
			if (!e.ok) throw Error(`Failed to fetch: ${e.status} ${e.statusText}`);
			i = await e.arrayBuffer();
		} else i = l;
		L();
		let o = M(j(k.legacyDoc, k.odt), "docx", new Uint8Array(i));
		if (!o) return _.load(i, {
			...k,
			legacyDoc: void 0,
			odt: void 0
		});
		let s = A(o, "docx");
		try {
			H.setSourceBytes(i.byteLength), H.checkpoint("container ready");
			let o = V === "worker" ? (await import("./render-worker-host-BPvvLDas.js")).createRenderWorker() : new (await (import("./worker-source-Z57e-fLF.js"))).default(), l, A, j = !1, M = () => {
				j || !l || (j = !0, l.destroy());
			}, U = I(o, s, k, (e) => {
				l && P(l, e);
			}), W = V === "worker" ? a(k) : void 0, G = V === "worker" && !!k.progressiveLayout;
			try {
				A = Reflect.construct(_, [
					U,
					V,
					B,
					k.wasmUrl
				]), l = A, F?.addEventListener("abort", M, { once: !0 }), L(), l._metrics = H, l._cjkFallback = R, l._allowFootnoteContinuation = k.allowFootnoteContinuation !== !1;
				let a = n(l), o = b(k.currentDate, a.defaultCurrentDateMs, k.showTrackedChanges === !0);
				a.activeLayoutOptions = o, await l._parse(i, z.policy, V === "worker" ? k.fonts : void 0, k.workerTimeoutMs, (e) => H.observeUsage(e), W, G ? {
					onPartial: k.onLayoutPartial,
					onComplete: k.onLayoutComplete,
					onProgress: k.onLayoutProgress,
					layoutOptions: o,
					abort: new AbortController(),
					firstPublication: d(),
					published: !1,
					settled: !1
				} : void 0), V === "worker" && l._mode === "main" && (H.setMode("main"), console.warn(m(l._mainThreadFallbackReason))), k.math && l._mode === "worker" && !W?.math && console.warn("[ooxml] a custom math renderer cannot cross the worker boundary; equations will be skipped in mode: 'worker'. Use the math renderer from @silurus/ooxml/math."), k.threeD && l._mode === "worker" && !W?.threeD && console.warn("[ooxml] a custom 3-D chart renderer cannot cross the worker boundary; charts use their 2-D family fallback in mode: 'worker'. Use the renderer from @silurus/ooxml/three-d."), l._threeD = l._mode === "worker" ? void 0 : k.threeD, k.regionMap && l._mode === "worker" && !W?.regionMap && console.warn("[ooxml] a custom Region Map renderer cannot cross the worker boundary; geospatial charts use the unsupported-chart placeholder in mode: 'worker'. Use the renderer from @silurus/ooxml/region-map."), l._regionMap = l._mode === "worker" ? void 0 : k.regionMap, k.chartEx && l._mode === "worker" && !W?.chartEx && console.warn("[ooxml] a custom ChartEx renderer cannot cross the worker boundary; ChartEx charts use the unsupported-chart placeholder in mode: 'worker'. Use the renderer from @silurus/ooxml/chart-ex."), l._chartEx = l._mode === "worker" ? void 0 : k.chartEx, k.tiff && l._mode === "worker" && !W?.tiff && console.warn("[ooxml] a custom TIFF codec cannot cross the worker boundary; recognized TIFF images will use an unavailable-image placeholder in mode: 'worker'. Use the codec from @silurus/ooxml/tiff to display them."), l._tiff = l._mode === "worker" ? void 0 : k.tiff;
				let c, j;
				if (l._mode === "main" && l._document?.embeddedFonts?.length) {
					let t = l, n = await h(l._document, (e) => t.getFontBytes(e));
					if (F?.aborted) throw e(n.faces), new w();
					f(l, n.diagnostics), l._embeddedFontFaces = n.faces, c = n.metrics, j = n.routes;
				}
				let P = l._mode === "main" && l._document ? await v(C(l._document, {
					fontDemand: !!k.fonts,
					cjkFallback: R
				}).filter((e) => e.presenceOnly || !j?.some((t) => t.requestedFamily.toLowerCase() === e.family.toLowerCase() && t.weight === (e.weight ?? 400) && t.style === (e.style ?? "normal")))) : {
					faces: [],
					routes: {}
				};
				if (F?.aborted) throw t(P.faces), new w();
				l._officeFontFaces = P.faces;
				let { installedSubstituteFamilies: I, sourceFonts: K } = await l._loadFontSources(k.fonts, R, P, F), q;
				if (l._mode === "main" && k.math && l._document && D(l._document) && (q = await O(l._document, k.math)), L(), l._mode === "main" && l._document && l._source) {
					let e = l, i = n(l), a = {
						allowFootnoteContinuation: l._allowFootnoteContinuation,
						fontMetrics: c,
						fontSubstitutes: r(u(k.fonts)),
						cjkFallback: R,
						embeddedRoutes: j,
						officeRoutes: Object.values(P.routes),
						sourceFonts: K,
						installedSubstituteFamilies: I,
						installedFamilies: "installed" in P ? P.installed : void 0,
						mathResources: q?.records,
						mathDrawables: q?.drawables
					}, o = await S(l._source, l._document, {
						fontSubstitutes: r(u(k.fonts)),
						cjkFallback: R
					});
					if (F?.aborted) throw t(o.faces), new w();
					l._officeFontFaces = [...l._officeFontFaces, ...o.faces], i.services = E(l._source, {
						...a,
						nativeRouteMetrics: o.nativeRouteMetrics
					});
					let s = i.services, f = y(l._source, F);
					f && await f;
					let m = x(l._source, s, i.defaultCurrentDateMs), h = l._source.fatalParse === null, _ = i.activeLayoutOptions;
					if (!_) throw Error("Active layout view was not recorded at load");
					let v = { onProgress: k.onLayoutProgress ? (t) => e._layoutObservers.notify("onLayoutProgress", k.onLayoutProgress, { committedUnits: t }) : void 0 };
					if (h && k.progressiveLayout) {
						let e = m.layoutVariants, t = l, n = new AbortController();
						t._layoutAbort = n;
						let r = d(), i = null, a = !0;
						t._layoutCompletion = p(l._source.bodyLayoutInput, s, _, {
							scheduler: {
								...v,
								signal: n.signal
							},
							onPreview: (n) => {
								if (!a) return;
								let o = i === null, s = t._replaceMainLayoutPublication(e, _, i, n.layout);
								if (s === null) {
									a = !1;
									return;
								}
								if (i = s, o) t._layoutLifecycle.begin(), g(t, {
									pageCount: n.layout.pages.length,
									exact: n.exact,
									complete: !1
								}), r.resolve();
								else {
									if (!t._isLayoutViewActive(_)) return;
									g(t, {
										pageCount: n.layout.pages.length,
										exact: n.exact,
										complete: !1
									}), t._layoutObservers.notify("onLayoutPartial", k.onLayoutPartial, {
										availableUnits: n.layout.pages.length,
										exact: n.exact
									});
								}
							}
						}).then((n) => {
							a && t._replaceMainLayoutPublication(e, _, i, n) === null && (a = !1), t._layoutLifecycle.succeed(), g(t, {
								pageCount: t.pageCount,
								exact: !0,
								complete: !0
							}), t._layoutObservers.notify("onLayoutComplete", k.onLayoutComplete), r.resolve();
						}).catch((e) => {
							if (i === null) {
								r.reject(e);
								return;
							}
							if (e instanceof w) {
								t._layoutLifecycle.succeed();
								return;
							}
							let n = t._layoutLifecycle.fail(e);
							g(t, {
								pageCount: t.pageCount,
								exact: !1,
								complete: !1,
								error: n
							}), t._layoutObservers.notify("onLayoutComplete", k.onLayoutComplete, n);
						}), await r.promise;
					} else if (h && (k.sliceLayout !== !1 || k.onLayoutProgress)) for (;;) {
						L();
						let e = N?.requestedView(), t = e === void 0 ? _ : b(k.currentDate, i.defaultCurrentDateMs, e);
						i.activeLayoutOptions = t;
						let n = new AbortController(), r = !1, a = N?.subscribeViewChange(() => {
							let e = N.requestedView();
							r || e === void 0 || e === !0 == (t.showTrackedChanges === !0) || (r = !0, n.abort());
						});
						l._layoutAbort = n;
						try {
							let e = await T(l._source.bodyLayoutInput, s, t, {
								...v,
								signal: n.signal
							});
							if (L(), r) continue;
							m.layoutVariants.prime(t, e);
							break;
						} catch (e) {
							if (e instanceof w && r && !F?.aborted) continue;
							throw e;
						} finally {
							a?.(), l._layoutAbort = null;
						}
					}
					else m.layoutVariants.layoutFor(_);
				}
				return L(), await l._resourceUsage(k.workerTimeoutMs ?? 1e3).then((e) => H.observeUsage(e), () => void 0), H.checkpoint("model and layout ready"), L(), H.succeed({ pages: l.pageCount }), s.release(), A;
			} catch (e) {
				throw c(o, l ? M : void 0), e;
			} finally {
				F?.removeEventListener("abort", M);
			}
		} finally {
			s.release();
		}
	} catch (e) {
		throw H.fail(e), e;
	}
}
function I(e, t, n, r) {
	let i = /* @__PURE__ */ new Map();
	return k(e, {
		discriminator: "type",
		load: t,
		parseMessage: (e) => ({
			...e,
			...N(t),
			...n.showTrackedChanges === void 0 ? {} : { showTrackedChanges: n.showTrackedChanges }
		}),
		member: (e, t) => {
			if (t === "addEventListener") return (t, a, o) => {
				if (t !== "message") return e.addEventListener(t, a, o);
				let s = (e) => {
					let t = e.data;
					n.showTrackedChanges === void 0 && (t.type === "documentSessionOpened" || t.type === "mainThreadVerticalFallback") && r(t.viewDefaults?.showTrackedChanges), (t.type === "parsedMeta" || t.type === "layoutPartial") && r(t.showTrackedChanges), typeof a == "function" ? a(e) : a.handleEvent(e);
				};
				i.set(a, s), e.addEventListener("message", s, o);
			};
			if (t === "removeEventListener") return (t, n, r) => e.removeEventListener(t, t === "message" ? i.get(n) ?? n : n, r);
		}
	});
}
export { F as loadDocxModelSource };
