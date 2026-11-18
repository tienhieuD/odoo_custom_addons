import { t as e } from "./chunk-D5OxutzX.js";
import { t } from "./substitutions-_KDT_mVq.js";
import { n, t as r } from "./ooxml-error-DbICW35n.js";
import { Fr as i } from "./document-content-DXDaB_ij.js";
import { u as a } from "./vertical-vert-feature-ru96Mg5B.js";
import { o } from "./units-BBDOirYi.js";
import { f as s, u as c } from "./pixel-budget-DI82Hn3R.js";
import { i as l, t as u } from "./tiff-contract-DEd8CGuz.js";
import { _ as d, a as f, c as p, g as m, h, i as g, l as _, n as v, o as y, r as b, s as x, t as S, u as C, v as ee, x as te } from "./canvas-viewer-mechanics-DrH37lzF.js";
import { a as ne, o as re } from "./chart-context-DqNY4BWJ.js";
import { S as w, T as ie, _ as ae, a as oe, b as se, c as ce, d as le, f as ue, g as de, h as fe, i as pe, l as me, m as he, n as ge, o as _e, p as ve, r as ye, t as be, u as xe, v as Se, w as Ce, x as T, y as we } from "./comment-overlay-controller-ByvOX8Dp.js";
import { r as E } from "./hyperlink-BOJHX05H.js";
import { n as Te, t as D } from "./highlight-rect-CuBeY9DT.js";
import { i as Ee, o as De, r as Oe, s as ke } from "./source-GXgH3t1X.js";
import { n as O, s as k } from "./part-failures-pZSloLZv.js";
import { a as A, c as j, f as Ae, i as M, m as je, n as N, o as P, p as F, r as I, s as L, t as R, u as z } from "./document-CexDucFg.js";
import { y as B } from "./document-pull-client-DsaDuAP-.js";
import { n as V, r as Me } from "./comments-B3a2O0op.js";
function H(e, t) {
	if (!e.eastAsianVert) return 1;
	let n = t(e.text);
	return !(n > 0) || e.w >= n ? 1 : e.w / n;
}
function U(e, t, n, r, i, a, o) {
	e.innerHTML = "", w(e, "ooxmlSelectionSurface", "docx"), w(e, "pageIndex", o === void 0 ? void 0 : String(o));
	let s = e.ownerDocument ?? document;
	for (let [o, c] of t.entries()) {
		let t = s.createElement("span");
		w(t, "ooxmlSelectionRun", "docx"), w(t, "runIndex", String(o)), c.paragraphId !== void 0 && w(t, "paragraphId", c.paragraphId), c.source !== void 0 && (w(t, "sourceStory", c.source.story), w(t, "sourceStoryInstance", c.source.storyInstance), w(t, "sourcePath", JSON.stringify(c.source.path))), t.textContent = c.text;
		let l = c.transform ?? "";
		if (a && c.eastAsianVert) {
			let e = H(c, a(c.font));
			e !== 1 && (l = `${l ? `${l} ` : ""}scaleX(${e})`);
		}
		let u = l ? `transform:${l};transform-origin:top left;` : "", d = i ? c.hyperlink : void 0, f = d ? "pointer" : "text", p = c.letterSpacingPx === void 0 ? "0" : `${c.letterSpacingPx}px`, m = c.trailingSpaceCompressionPx === void 0 ? "" : `width:${D(c.w, n)};overflow:hidden;`;
		t.style.cssText = `position:absolute;left:${D(c.x, n)};top:${D(c.y, r)};font:${c.font};line-height:${c.h}px;letter-spacing:${p};` + m + u + `white-space:pre;color:transparent;cursor:${f};pointer-events:all;`, d && i && (t.title = d.kind === "external" ? d.url : d.ref, t.addEventListener("click", (e) => {
			e.preventDefault(), i(d);
		})), e.appendChild(t);
	}
}
function W(e, t, n, r, a, o, s = {}) {
	e.innerHTML = "";
	let c = s.match ?? "rgba(255, 214, 0, 0.42)", l = s.active ?? "rgba(255, 140, 0, 0.55)";
	for (let s of n) {
		let n = s.active ? l : c;
		for (let c of s.slices) {
			let s = t[c.runIndex];
			if (!s) continue;
			let l = o(s.font), u = Te(s.text, c.start, c.end, l), d = s.letterSpacingPx ?? 0, f = Math.max(0, Math.min(c.start, s.text.length)), p = Math.max(f, Math.min(c.end, s.text.length)), m = i(s.text.slice(f, p)).pitchBearing, h = i(s.text.slice(0, f)).pitchBearing, g = u.x + h * d, _ = u.width + Math.max(0, m - 1) * d, v = H(s, l), y = g * v, b = _ * v;
			if (b <= 0) continue;
			let x = document.createElement("div"), S = s.transform ? `transform:${s.transform};transform-origin:top left;` : "";
			x.style.cssText = `position:absolute;left:${D(s.x + y, r)};top:${D(s.y, a)};width:${D(b, r)};height:${D(s.h, a)};` + S + `background:${n};pointer-events:none;`, e.appendChild(x);
		}
	}
}
var G = class extends se {
	constructor(e, t) {
		super(e, t, (e) => ({ page: e }));
	}
	pageRuns(e) {
		return this.unitRuns(e);
	}
	setPageRuns(e, t) {
		this.setUnitRuns(e, t);
	}
	pageHighlights(e) {
		return this.unitHighlights(e);
	}
	activePage() {
		return this.activeUnit();
	}
};
function Ne(e, t, n, r, i = {}) {
	let a = e.find((e) => e.id === n && e.parentId === void 0);
	if (!a) return null;
	let o = new Map(e.map((e) => [e.id, e])), s = e.filter((e) => {
		if (e.parentId === void 0) return !1;
		let t = e, n = /* @__PURE__ */ new Set();
		for (; t.parentId !== void 0 && !n.has(t.id);) {
			n.add(t.id);
			let e = o.get(t.parentId);
			if (!e) return !1;
			if (e.id === a.id) return !0;
			t = e;
		}
		return !1;
	}), c = we({
		id: a.id,
		author: a.author,
		date: a.date,
		text: a.paragraphs?.join("\n") ?? a.text,
		status: a.resolved ? "resolved" : "active"
	}, s.map((e) => ({
		id: e.id,
		author: e.author,
		date: e.date,
		text: e.paragraphs?.join("\n") ?? e.text,
		status: e.resolved ? "resolved" : "active"
	})), i.maxTextCharacters), l = t.find((e) => e.commentId === n)?.source;
	return Object.freeze({
		format: "docx",
		kind: "comment",
		pageIndex: r,
		commentId: n,
		...l ? { source: Object.freeze({
			...l,
			path: Object.freeze([...l.path])
		}) } : {},
		thread: c.thread,
		truncated: c.truncated,
		truncationReasons: c.truncated ? ["text"] : [],
		textCharacters: c.textCharacters,
		maxTextCharacters: c.maxTextCharacters
	});
}
function Pe(e) {
	for (let t = e; t; t = t.parentElement) {
		let e = T(t.dataset.pageIndex);
		if (e !== null) return e;
	}
	return null;
}
var Fe = new Set([
	"body",
	"header",
	"footer",
	"footnote",
	"endnote",
	"textbox"
]);
function K(e) {
	let t = e.dataset.sourceStory, n = e.dataset.sourceStoryInstance, r = e.dataset.sourcePath;
	if (!t || !Fe.has(t) || !n || !r) return null;
	try {
		let e = JSON.parse(r);
		return !Array.isArray(e) || e.length === 0 || e.length > 32 || !e.every((e) => Number.isSafeInteger(e) && e >= 0) ? null : {
			story: t,
			storyInstance: n,
			path: [...e]
		};
	} catch {
		return null;
	}
}
function q(e, t, n = {}) {
	let r = p(e, t, (e) => {
		let t = Pe(e), n = T(e.dataset.runIndex);
		return t === null || n === null ? null : {
			pageIndex: t,
			runIndex: n,
			...e.dataset.paragraphId === void 0 ? {} : { paragraphId: e.dataset.paragraphId },
			...K(e) === null ? {} : { source: K(e) }
		};
	}, {
		maxChars: n.maxTextCharacters,
		maxLocators: n.maxRunLocators
	});
	if (!r) return null;
	let i = [...r.locators].sort((e, t) => e.pageIndex - t.pageIndex || e.runIndex - t.runIndex);
	return {
		format: "docx",
		kind: "text",
		text: r.text,
		pageIndexes: [...new Set(i.map((e) => e.pageIndex))],
		paragraphIds: [...new Set(i.flatMap((e) => e.paragraphId ? [e.paragraphId] : []))],
		runs: i,
		truncated: r.truncated,
		truncationReasons: r.truncationReasons,
		textCharacters: r.textCharacters,
		maxTextCharacters: r.maxTextCharacters,
		maxRunLocators: r.maxLocators
	};
}
function J(e, t, n, r, i) {
	return r === "worker" ? e.renderPageToBitmap(n, i) : e.renderPage(t, n, i);
}
var Y = Symbol("DocxViewer.borrowedDocument"), X = class e {
	_pendingLoadAbort = null;
	_pendingRequestedView;
	_pendingViewChanged = null;
	_documentOwner;
	get _doc() {
		return this._documentOwner.current;
	}
	_borrowed;
	_hostWindow;
	_currentPage = 0;
	_scale = null;
	_canvas;
	_wrapper;
	_canvasMount;
	_textLayer = null;
	_highlightLayer = null;
	_elementLayer = null;
	_find;
	_findRequestGeneration = 0;
	_measureCtx = null;
	_opts;
	_showTrackedChangesExplicit = !1;
	_mode;
	_renderDispatcher;
	_errorRouter;
	_destroyed = !1;
	_partFailureDelivery;
	_selectionChangeListener = null;
	_selectionContextKey = "null";
	_elementContext = null;
	_elementHitGeneration = 0;
	_layoutViewGeneration = 0;
	_layoutViewPublicationGeneration = 0;
	_navigationGeneration = 0;
	_layoutUnsubscribe = null;
	_internalHyperlinkGeneration = 0;
	_layoutWaiters = /* @__PURE__ */ new Set();
	_layoutFailed = !1;
	_loadingIndicator;
	_elementClickListener = null;
	_contextMenuListener = null;
	static fromDocument(t, n, r = {}) {
		let i = A(n);
		return new e(t, {
			...r,
			currentDate: i.currentDate,
			showTrackedChanges: i.showTrackedChanges,
			[Y]: n
		});
	}
	constructor(e, t = {}) {
		this._canvas = e, this._opts = t, this._showTrackedChangesExplicit = t.showTrackedChanges !== void 0;
		let n = t[Y];
		this._borrowed = n !== void 0, this._mode = C("DocxViewer", t.mode, n), this._documentOwner = new y("DocxViewer", n ?? null, !1);
		let r = e.ownerDocument?.defaultView ?? (typeof window < "u" ? window : null);
		if (!r) throw Error("DocxViewer requires a canvas with an active Window");
		this._hostWindow = r, this._canvasMount = new S(e, {
			wrapperCssText: "position:relative;display:inline-block;vertical-align:top;",
			forceDisplayBlock: !0
		}), this._wrapper = this._canvasMount.wrapper, this._renderDispatcher = new f(e, this._mode === "worker"), this._errorRouter = new g("DocxViewer", t.onError), k(t.errorPlaceholder), this._partFailureDelivery = new O("DocxViewer", t.onPartFailure, () => "document");
		let i = new b(this._wrapper, t.enableTextSelection === !0, t.enableElementSelection === !0);
		this._textLayer = i.textLayer, this._highlightLayer = i.highlightLayer, this._elementLayer = i.elementLayer, this._loadingIndicator = new v(this._wrapper, "Loading page");
		let a = this._wrapper.ownerDocument.createElement("progress");
		a.setAttribute("aria-hidden", "true"), this._loadingIndicator.layer.appendChild(a), this._wrapper.insertBefore(this._loadingIndicator.layer, this._elementLayer), this._textLayer && (t.onSelectionContextChange || t.enableElementSelection) && (this._selectionChangeListener = () => this._emitSelectionContextChange(), this._wrapper.ownerDocument.addEventListener("selectionchange", this._selectionChangeListener)), t.enableElementSelection && (this._elementClickListener = (e) => {
			this._onElementClick(e).catch((e) => this._reportRenderError(e));
		}, this._wrapper.addEventListener("click", this._elementClickListener)), t.onContextMenu && (this._contextMenuListener = (e) => this._onContextMenu(e), this._wrapper.addEventListener("contextmenu", this._contextMenuListener)), this._find = new G(() => this.pageCount, (e) => this._collectPageRuns(e)), n && this._bindLayoutDocument(n);
	}
	async load(e) {
		let t = this._partFailureDelivery.beginLoad();
		try {
			await this._loadSource(e);
		} finally {
			let e = this._destroyed ? null : this._doc;
			this._partFailureDelivery.endLoad(t, e ? M(e) : null);
		}
	}
	async _loadSource(e) {
		if (this._destroyed) throw Error("DocxViewer is destroyed");
		if (this._borrowed) throw Error("DocxViewer.load() is unsupported on a Viewer created by fromDocument(); the borrowed document is already loaded.");
		let t = !1, n = this._pendingRequestedView;
		this._pendingLoadAbort?.abort();
		let r = new AbortController();
		this._pendingLoadAbort = r, this._pendingRequestedView = n;
		try {
			let i = await this._documentOwner.replace(async () => {
				let t = await R.load(e, {
					password: this._opts.password,
					useGoogleFonts: this._opts.useGoogleFonts,
					fonts: this._opts.fonts,
					allowFootnoteContinuation: this._opts.allowFootnoteContinuation,
					cjkFallback: this._opts.cjkFallback,
					maxZipEntryBytes: this._opts.maxZipEntryBytes,
					resourceLimits: this._opts.resourceLimits,
					debug: this._opts.debug,
					onResourceMetrics: this._opts.onResourceMetrics,
					workerTimeoutMs: this._opts.workerTimeoutMs,
					wasmUrl: this._opts.wasmUrl,
					math: this._opts.math,
					threeD: this._opts.threeD,
					regionMap: this._opts.regionMap,
					chartEx: this._opts.chartEx,
					tiff: this._opts.tiff,
					mode: this._mode,
					...this._opts.progressiveLayout ? { progressiveLayout: !0 } : {},
					...this._opts.sliceLayout === void 0 ? {} : { sliceLayout: this._opts.sliceLayout },
					[I]: {
						signal: r.signal,
						requestedView: () => this._pendingRequestedView,
						subscribeViewChange: (e) => (this._pendingViewChanged = e, () => {
							this._pendingViewChanged === e && (this._pendingViewChanged = null);
						})
					},
					onLayoutProgress: this._opts.onLayoutProgress,
					onLayoutPartial: this._opts.onLayoutPartial,
					onLayoutComplete: this._opts.onLayoutComplete,
					...n === void 0 ? N(this._opts) ? this._showTrackedChangesExplicit ? { showTrackedChanges: this._opts.showTrackedChanges } : void 0 : this._opts.showTrackedChanges === !0 ? { showTrackedChanges: !0 } : {} : { showTrackedChanges: n },
					...this._opts.legacyDoc === void 0 ? void 0 : { legacyDoc: this._opts.legacyDoc },
					...this._opts.odt === void 0 ? void 0 : { odt: this._opts.odt },
					...this._opts.currentDate === void 0 ? {} : { currentDate: this._opts.currentDate }
				});
				return await P(t, r.signal, () => this._pendingRequestedView, () => this._opts.currentDate, this), t;
			}, () => {
				this._invalidateElementContext(!1), t = !0, this._renderDispatcher.begin(), this._findRequestGeneration++, this._find.invalidate(), this._unbindLayoutDocument();
			});
			if (!i) return;
			if (this._destroyed) throw Error("DocxViewer is destroyed");
			if (this._pendingLoadAbort !== r) return;
			if (this._pendingRequestedView !== void 0 && (this._showTrackedChangesExplicit = !0, this._opts = {
				...this._opts,
				showTrackedChanges: this._pendingRequestedView
			}), this._currentPage = 0, this._bindLayoutDocument(i), this._destroyed) throw Error("DocxViewer is destroyed");
			if (this._pendingLoadAbort !== r || (this._find.invalidate(), await this._render(), this._pendingLoadAbort !== r)) return;
		} catch (e) {
			if (this._destroyed) throw Error("DocxViewer is destroyed");
			if (this._pendingLoadAbort !== r) return;
			throw e instanceof Error ? e : Error(String(e));
		} finally {
			this._pendingLoadAbort === r && (this._pendingLoadAbort = null, this._pendingRequestedView = void 0, this._pendingViewChanged = null);
		}
		t && !this._destroyed && this._emitSelectionContextChange();
	}
	get pageCount() {
		return this._doc?.pageCount ?? 0;
	}
	get partFailures() {
		return this._destroyed ? [] : this._doc?.partFailures ?? [];
	}
	get currentPage() {
		return this._currentPage;
	}
	get layoutComplete() {
		return this._doc?.layoutComplete ?? !0;
	}
	async waitUntilLayoutComplete() {
		await this._errorRouter.ownBackgroundLifecycle(async () => {
			await this._doc?.waitUntilLayoutComplete?.();
		});
	}
	get canvasElement() {
		return this._canvas;
	}
	async goToPage(e) {
		let t = this._doc;
		if (!t) return;
		let n = this._cancelPendingNavigation(), r = Math.max(0, Number.isNaN(e) ? 0 : Math.trunc(e));
		if (r >= this.pageCount && !this.layoutComplete) {
			this._setLoading(!0);
			try {
				await this._waitForPage(t, r, n);
			} finally {
				n === this._navigationGeneration && this._setLoading(!1);
			}
		}
		if (this._destroyed || n !== this._navigationGeneration || t !== this._doc) return;
		let i = Math.max(0, Math.min(r, this.pageCount - 1)), a = i !== this._currentPage;
		a && this._invalidateElementContext(!1), this._currentPage = i, await this._render(), a && !this._destroyed && this._emitSelectionContextChange();
	}
	async nextPage() {
		await this.goToPage(this._currentPage + 1);
	}
	async prevPage() {
		await this.goToPage(this._currentPage - 1);
	}
	_naturalWidthPx() {
		return !this._doc || this._doc.pageCount === 0 ? 0 : this._doc.pageSize(this._currentPage).widthPt * o;
	}
	_renderWidth() {
		if (this._scale === null) return this._opts.width;
		let e = this._naturalWidthPx();
		return e <= 0 ? this._opts.width : Math.round(e * this._scale);
	}
	getScale() {
		if (this._scale !== null) return this._scale;
		let e = this._naturalWidthPx();
		return e <= 0 ? 1 : this._opts.width && this._opts.width > 0 ? this._opts.width / e : 1;
	}
	_zoomMin() {
		return this._opts.zoomMin ?? .1;
	}
	_zoomMax() {
		return this._opts.zoomMax ?? 4;
	}
	async setScale(e) {
		let t = h(e, this._zoomMin(), this._zoomMax()), n = t !== this.getScale();
		this._scale = t, await this._render(), n && this._opts.onScaleChange?.(t);
	}
	async zoomIn() {
		await this.setScale(d(this.getScale()));
	}
	async zoomOut() {
		await this.setScale(ee(this.getScale()));
	}
	async fitWidth() {
		await this._fit("width");
	}
	async fitPage() {
		await this._fit("page");
	}
	async _fit(e) {
		if (!this._doc || this._doc.pageCount === 0) return;
		let t = this._doc.pageSize(this._currentPage), n = this._fitContainer();
		if (!n) return;
		let r = m({
			contentWidth: t.widthPt * o,
			contentHeight: t.heightPt * o,
			containerWidth: n.clientWidth,
			containerHeight: n.clientHeight
		}, e);
		r <= 0 || await this.setScale(r);
	}
	_fitContainer() {
		return this._opts.container ?? this._wrapper.parentElement ?? null;
	}
	async findText(e, t = {}) {
		let n = this._doc;
		if (!n) return [];
		let r = ++this._findRequestGeneration;
		if (e.length > 0 && !n.layoutComplete && (await this._errorRouter.ownBackgroundLifecycle(() => n.waitUntilLayoutComplete()), this._destroyed || this._doc !== n || r !== this._findRequestGeneration)) return [];
		let i = await this._errorRouter.ownAwaitable(() => this._find.find(e, t));
		return this._redrawHighlights(), i;
	}
	async findNext() {
		return this._activateMatch(this._find.next());
	}
	async findPrev() {
		return this._activateMatch(this._find.prev());
	}
	clearFind() {
		this._findRequestGeneration++, this._find.invalidate(), this._redrawHighlights();
	}
	async _activateMatch(e) {
		return e ? (e.location.page === this._currentPage ? this._redrawHighlights() : await this.goToPage(e.location.page), e) : (this._redrawHighlights(), null);
	}
	_redrawHighlights() {
		let e = this._find.pageRuns(this._currentPage) ?? [];
		this._buildHighlightLayer(e);
	}
	async getResourceMetrics() {
		if (!this._doc) throw Error("Document not loaded");
		return await this._doc.getResourceMetrics();
	}
	getSelectionContext(e = {}) {
		if (this._destroyed) throw Error("DocxViewer is destroyed");
		return (this._textLayer ? q(this._wrapper, this._wrapper.ownerDocument?.getSelection?.() ?? null, e) : null) ?? (this._elementContext ? je(this._elementContext, e.maxTextCharacters) : null);
	}
	_emitSelectionContextChange() {
		let e = this.getSelectionContext();
		e?.kind === "text" && (this._elementHitGeneration++, this._elementContext = null, this._redrawElementOutline());
		let t = JSON.stringify(e);
		t !== this._selectionContextKey && (this._selectionContextKey = t, this._opts.onSelectionContextChange?.(e ? structuredClone(e) : null));
	}
	_setElementContext(e) {
		this._elementContext = e ? structuredClone(e) : null, this._redrawElementOutline(), this._emitSelectionContextChange();
	}
	_invalidateElementContext(e = !0) {
		this._elementHitGeneration++, this._elementContext = null, this._redrawElementOutline(), e && this._emitSelectionContextChange();
	}
	_redrawElementOutline() {
		let e = this._elementContext, t = this._doc;
		if (!e || !t || e.pageIndex !== this._currentPage) {
			_(this._elementLayer, null);
			return;
		}
		let n = t.pageSize(e.pageIndex);
		_(this._elementLayer, {
			x: e.bounds.xPt / n.widthPt,
			y: e.bounds.yPt / n.heightPt,
			width: e.bounds.widthPt / n.widthPt,
			height: e.bounds.heightPt / n.heightPt
		});
	}
	async _onElementClick(e) {
		this._destroyed || e.defaultPrevented || e.button !== 0 || await this._resolveContextAt(e);
	}
	_onContextMenu(e) {
		let t;
		this._opts.onContextMenu?.({
			originalEvent: e,
			getContext: () => t ??= this._resolveContextAt(e)
		});
	}
	async _resolveContextAt(e) {
		let t = this._doc;
		if (this._destroyed || !t) return null;
		if (this._textLayer && q(this._wrapper, this._wrapper.ownerDocument?.getSelection?.() ?? null)) return this._emitSelectionContextChange(), this._destroyed ? null : this.getSelectionContext();
		if (!this._opts.enableElementSelection) return this.getSelectionContext();
		let n = this._canvas.getBoundingClientRect();
		if (n.width <= 0 || n.height <= 0) return this._invalidateElementContext(), null;
		let r = e.clientX - n.left, i = e.clientY - n.top;
		if (r < 0 || i < 0 || r > n.width || i > n.height) return this._invalidateElementContext(), null;
		let a = ++this._elementHitGeneration, o = this._currentPage, s = t.pageSize(o), c;
		try {
			c = await t.getElementContextAt(o, {
				xPt: r / n.width * s.widthPt,
				yPt: i / n.height * s.heightPt
			}, {
				currentDate: this._opts.currentDate,
				showTrackedChanges: this._opts.showTrackedChanges,
				maxTextCharacters: F
			});
		} catch (e) {
			if (this._destroyed || a !== this._elementHitGeneration || o !== this._currentPage || t !== this._doc) return null;
			throw e;
		}
		return this._destroyed || a !== this._elementHitGeneration || o !== this._currentPage || t !== this._doc ? null : (this._setElementContext(c), this._destroyed ? null : this.getSelectionContext());
	}
	destroy() {
		this._destroyed || (this._destroyed = !0, this._pendingLoadAbort?.abort(), this._pendingLoadAbort = null, this._pendingViewChanged = null, this._findRequestGeneration++, this._layoutViewGeneration++, this._partFailureDelivery.close(), this._unbindLayoutDocument(), this._errorRouter.close(), this._renderDispatcher.destroy(), B(this._canvas), this._documentOwner.close(), this._find.invalidate(), this._selectionChangeListener &&= (this._wrapper.ownerDocument.removeEventListener("selectionchange", this._selectionChangeListener), null), this._elementHitGeneration++, this._elementClickListener &&= (this._wrapper.removeEventListener("click", this._elementClickListener), null), this._contextMenuListener &&= (this._wrapper.removeEventListener("contextmenu", this._contextMenuListener), null), this._elementContext = null, this._canvasMount.restore());
	}
	async _render() {
		let e = this._renderDispatcher.begin();
		try {
			await this._renderPage(e);
		} catch (t) {
			if (!this._renderDispatcher.isCurrent(e)) return;
			throw t;
		}
	}
	_reportRenderError(e) {
		this._errorRouter.report(e);
	}
	async _renderPage(e) {
		if (!this._doc) return;
		let t = this._mode === "worker", n = this._renderWidth(), r = this._doc.pageSize(this._currentPage), i = n ?? r.widthPt * 1.3333333333333333, o = r.widthPt > 0 ? i * r.heightPt / r.widthPt : 0, s = [], c = (e) => s.push(e), l = this._opts.dpr ?? a(), u = {
			width: n,
			dpr: this._opts.dpr,
			imageResources: this._opts.imageResources,
			defaultTextColor: this._opts.defaultTextColor,
			currentDate: this._opts.currentDate,
			showTrackedChanges: this._opts.showTrackedChanges,
			onTextRun: c,
			...this._opts.errorPlaceholder === void 0 ? {} : { errorPlaceholder: this._opts.errorPlaceholder }
		};
		if (t) {
			let t = await J(this._doc, this._canvas, this._currentPage, "worker", u);
			if (!this._renderDispatcher.commitBitmap(e, t, {
				cssWidth: i > 0 ? i : Math.round(t.width / l),
				cssHeight: o > 0 ? o : Math.round(t.height / l)
			})) return;
		} else if (await J(this._doc, this._canvas, this._currentPage, "main", u), !this._renderDispatcher.isCurrent(e)) return;
		this._textLayer && this._buildTextLayer(this._textLayer, s), this._find.setPageRuns(this._currentPage, s), this._buildHighlightLayer(s), this._opts.onPageChange?.(this._currentPage, this.pageCount, this.layoutComplete);
	}
	_clearPresentedPage() {
		this._renderDispatcher.begin(), B(this._canvas), this._canvas.width = 0, this._canvas.height = 0, this._textLayer?.replaceChildren(), this._find.invalidate();
	}
	_bindLayoutDocument(e) {
		this._unbindLayoutDocument(), this._layoutFailed = !1, this._layoutViewPublicationGeneration = 0;
		let t = j(e, (t) => this._onLayoutViewPublication(e, t), (e) => this._reportRenderError(e)), n = !0, r = z(e, () => ({
			pageCount: e.pageCount,
			exact: e.layoutComplete,
			complete: e.layoutComplete
		}), (t) => {
			if (n) {
				n = !1;
				return;
			}
			this._onLayoutPublication(e, t);
		}, (e) => this._reportRenderError(e));
		this._layoutUnsubscribe = () => {
			r(), t();
		}, this._partFailureDelivery.attach(M(e));
	}
	_unbindLayoutDocument() {
		this._partFailureDelivery.attach(null), this._layoutUnsubscribe?.(), this._layoutUnsubscribe = null, this._layoutFailed = !1, this._cancelPendingNavigation();
	}
	_onLayoutPublication(e, t) {
		if (!(this._destroyed || e !== this._doc)) {
			if (this._wakeLayoutWaiters(), t.error !== void 0) {
				t.pageCount === 0 && this._clearPresentedPage(), this._layoutFailed = !0, this._errorRouter.reportBackground(t.error, this._opts.onLayoutComplete !== void 0);
				return;
			}
			this._find.invalidate(), this._currentPage = Math.max(0, Math.min(this._currentPage, t.pageCount - 1)), this._render().catch((e) => this._reportRenderError(e));
		}
	}
	_onLayoutViewPublication(e, t) {
		this._destroyed || e !== this._doc || t.generation <= this._layoutViewPublicationGeneration || (this._layoutViewPublicationGeneration = t.generation, t.requester !== this && (this._layoutViewGeneration++, this._opts = {
			...this._opts,
			currentDate: t.view.currentDate,
			showTrackedChanges: t.view.showTrackedChanges
		}, this._find.invalidate(), this._currentPage = Math.max(0, Math.min(this._currentPage, e.pageCount - 1)), this._render().catch((e) => this._reportRenderError(e))));
	}
	async _waitForPage(e, t, n) {
		await this._errorRouter.ownBackgroundLifecycle(async () => {
			for (; !this._destroyed && n === this._navigationGeneration && e === this._doc && t >= e.pageCount && !e.layoutComplete && !this._layoutFailed;) await new Promise((e) => {
				this._layoutWaiters.add(e);
			});
			e === this._doc && (e.layoutComplete || this._layoutFailed) && await e.waitUntilLayoutComplete();
		});
	}
	_wakeLayoutWaiters() {
		for (let e of this._layoutWaiters) e();
		this._layoutWaiters.clear();
	}
	_cancelPendingNavigation() {
		let e = ++this._navigationGeneration;
		return this._wakeLayoutWaiters(), this._setLoading(!1), e;
	}
	_setLoading(e) {
		this._loadingIndicator.setLoading(e);
	}
	async setShowTrackedChanges(e) {
		let t = ++this._layoutViewGeneration;
		if (this._pendingLoadAbort) {
			let t = this._pendingRequestedView !== e;
			this._pendingRequestedView = e, t && this._pendingViewChanged?.();
		}
		let n = this._doc, r = N(this._opts) && n ? A(n).showTrackedChanges : this._opts.showTrackedChanges === !0;
		if ((!n || r === e) && (this._showTrackedChangesExplicit = !0, this._opts = {
			...this._opts,
			showTrackedChanges: e
		}), r === e) {
			n && await L(n, {
				showTrackedChanges: e,
				currentDate: this._opts.currentDate
			}, this);
			return;
		}
		let i = {
			...this._opts,
			showTrackedChanges: e
		};
		(!n || await L(n, {
			showTrackedChanges: e,
			currentDate: i.currentDate
		}, this)) && (this._destroyed || t !== this._layoutViewGeneration || n !== this._doc || (this._showTrackedChangesExplicit = !0, this._opts = i, this._find.invalidate(), this._currentPage = Math.max(0, Math.min(this._currentPage, this.pageCount - 1)), await this._render()));
	}
	_buildHighlightLayer(e) {
		let t = this._highlightLayer;
		if (!t) return;
		let { width: n, height: r } = this._canvasCssPx();
		W(t, e, this._find.pageHighlights(this._currentPage), n, r, (e) => this._measureForFont(e), this._opts.findHighlightColors);
	}
	_canvasCssPx() {
		return {
			width: parseFloat(this._canvas.style.width) || this._canvas.width,
			height: parseFloat(this._canvas.style.height) || this._canvas.height
		};
	}
	_measureForFont(e) {
		if (!this._measureCtx) {
			let e = document.createElement("canvas");
			this._measureCtx = e.getContext("2d");
		}
		let t = this._measureCtx;
		return t ? (t.font = e, (e) => t.measureText(e).width) : (e) => e.length;
	}
	async _collectPageRuns(e) {
		return this._doc ? this._doc.collectPageRuns(e, {
			width: this._renderWidth(),
			currentDate: this._opts.currentDate,
			showTrackedChanges: this._opts.showTrackedChanges
		}) : [];
	}
	_buildTextLayer(e, t) {
		let { width: n, height: r } = this._canvasCssPx();
		U(e, t, n, r, this._hyperlinkHandler(), (e) => this._measureForFont(e), this._currentPage);
	}
	_hyperlinkHandler() {
		return this._opts.enableHyperlinks === !1 ? void 0 : this._opts.onHyperlinkClick || ((e) => {
			if (e.kind === "external") {
				E(e.url, void 0, this._hostWindow);
				return;
			}
			let t = this._doc;
			if (!t) return;
			let n = ++this._internalHyperlinkGeneration;
			this._navigateInternalHyperlink(t, e.ref, n).catch((e) => this._reportRenderError(e));
		});
	}
	async _navigateInternalHyperlink(e, t, n) {
		if (e.layoutComplete || await e.waitUntilLayoutComplete(), this._destroyed || this._doc !== e || n !== this._internalHyperlinkGeneration) return;
		let r = e.getBookmarkPage(t);
		r !== void 0 && await this.goToPage(r);
	}
}, Ie = class {
	hooks;
	pageById = /* @__PURE__ */ new Map();
	runsByPage = /* @__PURE__ */ new Map();
	indexedPages = /* @__PURE__ */ new Set();
	frontier = 0;
	generation = 0;
	constructor(e) {
		this.hooks = e;
	}
	reset() {
		this.generation++, this.pageById.clear(), this.runsByPage.clear(), this.indexedPages.clear(), this.frontier = 0;
	}
	commitRuns(e, t) {
		this.runsByPage.set(e, {
			scale: this.hooks.scale(),
			runs: Promise.resolve(t)
		});
		let n = this.hooks.document();
		n && e === this.frontier && this.indexPage(e, t, n.commentAnchorRanges());
	}
	indexPage(e, t, n) {
		if (!this.indexedPages.has(e)) {
			for (let r of n) !this.pageById.has(r.commentId) && V(r, t).length > 0 && this.pageById.set(r.commentId, e);
			for (this.indexedPages.add(e); this.indexedPages.has(this.frontier);) this.frontier++;
		}
	}
	async runsForPage(e, t) {
		for (; !this.hooks.destroyed() && this.hooks.document() === t;) {
			let n = this.hooks.scale(), r = this.runsByPage.get(e);
			(!r || r.scale !== n) && (r = {
				scale: n,
				runs: t.collectPageRuns(e, {
					width: this.hooks.pageWidth(e),
					currentDate: this.hooks.currentDate(),
					...this.hooks.showTrackedChanges() ? { showTrackedChanges: !0 } : {}
				})
			}, this.runsByPage.set(e, r));
			try {
				let e = await r.runs;
				if (this.hooks.destroyed() || this.hooks.document() !== t) return null;
				if (this.hooks.scale() !== n) continue;
				return e;
			} catch (t) {
				throw this.runsByPage.get(e) === r && this.runsByPage.delete(e), t;
			}
		}
		return null;
	}
	async goToComment(e, t) {
		if (this.hooks.destroyed()) throw Error("DocxScrollViewer is destroyed");
		let n = this.hooks.document();
		if (!n || !n.comments.some((t) => t.id === e && t.parentId === void 0)) return !1;
		let r = ++this.generation, i = !n.layoutComplete, a = n.commentAnchorRanges().filter((t) => t.commentId === e), o = t?.pageIndex;
		if (o !== void 0 && (!Number.isInteger(o) || o < 0)) return !1;
		let s = o ?? this.pageById.get(e), c = async () => {
			let t = n.commentAnchorRanges();
			for (; s === void 0 && this.frontier < n.pageCount;) {
				let i = this.frontier, a = await this.runsForPage(i, n);
				if (this.hooks.destroyed()) throw Error("DocxScrollViewer is destroyed");
				if (this.hooks.document() !== n || r !== this.generation || !a) return;
				this.indexPage(i, a, t), s = this.pageById.get(e);
			}
		};
		if (o === void 0 && s === void 0 && a.length > 0 && await c(), i && (o !== void 0 && o >= n.pageCount || o === void 0 && s === void 0)) {
			if (await this.hooks.waitForLayout(n), this.hooks.destroyed()) throw Error("DocxScrollViewer is destroyed");
			if (this.hooks.document() !== n || r !== this.generation) return !1;
			a = n.commentAnchorRanges().filter((t) => t.commentId === e), this.pageById.clear(), this.runsByPage.clear(), this.indexedPages.clear(), this.frontier = 0, s = o, o === void 0 && a.length > 0 && await c();
		}
		if (a.length === 0 || s === void 0 || o !== void 0 && o >= n.pageCount) return !1;
		let l = await this.runsForPage(s, n);
		if (this.hooks.destroyed()) throw Error("DocxScrollViewer is destroyed");
		if (this.hooks.document() !== n || r !== this.generation || !l) return !1;
		let u = a.flatMap((e) => V(e, l))[0];
		return u ? (this.hooks.select(e, s, u, t), !0) : !1;
	}
	destroy() {
		this.reset();
	}
}, Le = class {
	hooks;
	unsubscribe = null;
	viewGeneration = 0;
	prefix = 0;
	constructor(e) {
		this.hooks = e;
	}
	get presentedPageCount() {
		return this.prefix;
	}
	set presentedPageCount(e) {
		this.prefix = e;
	}
	bind(e) {
		this.unbind(), this.viewGeneration = 0, this.prefix = e.pageCount;
		let t = j(e, (t) => this.onViewPublication(e, t), this.hooks.report), n = !0, r = z(e, () => ({
			pageCount: e.pageCount,
			exact: e.layoutComplete,
			complete: e.layoutComplete
		}), (t) => {
			if (n) {
				n = !1;
				return;
			}
			this.onPublication(e, t);
		}, this.hooks.report);
		this.unsubscribe = () => {
			r(), t();
		};
	}
	unbind() {
		this.unsubscribe?.(), this.unsubscribe = null, this.prefix = 0;
	}
	onPublication(e, t) {
		if (!(this.hooks.destroyed() || e !== this.hooks.current())) {
			if (t.error !== void 0) {
				t.pageCount === 0 && (this.prefix = 0), this.hooks.reportBackground(t.error);
				return;
			}
			this.hooks.invalidateFind(), this.hooks.refreshComments(), this.apply(t);
		}
	}
	onViewPublication(e, t) {
		this.hooks.destroyed() || e !== this.hooks.current() || t.generation <= this.viewGeneration || (this.viewGeneration = t.generation, this.hooks.adoptView(t));
	}
	apply(e) {
		let t = [...this.hooks.mounted()], n = this.prefix;
		if (this.prefix = e.pageCount, (e.unchangedPages ?? 0) >= Math.min(n, e.pageCount)) {
			this.hooks.relayout();
			return;
		}
		this.hooks.invalidateRender(), this.hooks.relayout();
		for (let [e, n] of t) e >= this.prefix || !this.hooks.stillMounted(e, n) || this.hooks.refreshSlot(e, n);
	}
	destroy() {
		this.unbind();
	}
}, Re = 12, ze = 13, Z = Symbol("DocxScrollViewer.borrowedDocument"), Be;
function Ve() {
	return Be ??= import("./comment-ui-runtime-BSbj7kz-.js");
}
var Q = class e {
	_pendingLoadAbort = null;
	_pendingRequestedView;
	_pendingViewChanged = null;
	_documentOwner;
	get _doc() {
		return this._documentOwner.current;
	}
	_borrowed;
	_opts;
	_errorRouter;
	_container;
	_shell;
	get _wrapper() {
		return this._shell.wrapper;
	}
	get _scrollHost() {
		return this._shell.scrollHost;
	}
	get _spacer() {
		return this._shell.spacer;
	}
	_mode;
	_viewport = new ce({
		options: () => this._opts,
		container: () => this._container,
		scrollHost: () => this._scrollHost
	});
	_zoom = new ye({
		scrollHost: () => this._scrollHost,
		spacer: () => this._spacer,
		count: () => this._doc?.pageCount ?? 0,
		zoomMin: () => this._opts.zoomMin ?? .1,
		zoomMax: () => this._opts.zoomMax ?? 4,
		baseScale: () => this._baseScale(),
		fitWidthPx: () => this._viewport.fitWidth(),
		fitContentSize: (e) => {
			if (!this._doc) return null;
			let t = this._doc.pageSize(0);
			return {
				width: (e === "width" ? this._widestPageWidthPt() : t.widthPt) * o,
				height: t.heightPt * o
			};
		},
		indexAt: (e) => this._pageIndexAtOffset(this._range(), e),
		offset: (e) => this._scrollGeometry.offsets[e] ?? 0,
		height: (e) => this._heights[e] || 0,
		totalHeight: () => this._scrollGeometry.totalHeight,
		recomputeHeights: () => this._recomputeHeights(),
		syncSpacerWidth: () => this._syncSpacerWidth(),
		padLeft: () => this._viewport.horizontalPadding().left,
		invalidateRender: () => {
			this._renderEpoch++;
		},
		preview: () => this._previewVisible(),
		scheduleSettle: () => this._scheduleSettle(),
		onScaleChange: (e) => this._opts.onScaleChange?.(e),
		relayout: () => this.relayout(),
		mountVisible: () => this._mountVisible(),
		refitOnResize: () => this._opts.refitOnResize !== !1
	});
	get _scale() {
		return this._zoom.scale;
	}
	get _scaleEstablished() {
		return this._zoom.established;
	}
	_scroller = new le({
		spacer: () => this._spacer,
		count: () => this._doc?.pageCount ?? 0,
		range: () => this._range(),
		createSlot: () => this._createSlot(),
		attachSlot: (e) => this._scrollHost.appendChild(e.wrapper),
		resetSlot: (e, t) => this._resetSlot(e, t),
		positionSlot: (e, t, n) => this._positionSlot(t, e, n),
		renderSlot: (e, t, n) => this._renderSlot(e, t, n),
		previewSlot: (e, t, n) => this._previewSlot(t, e, n),
		settleSlot: (e, t) => this._refreshSlotAtomically(e, t),
		renderedScale: (e) => e.renderedScale,
		scale: () => this._scale,
		syncSpacerWidth: () => this._syncSpacerWidth(),
		onRange: (e) => this._emitVisiblePageChange(e),
		onExistingSlot: (e, t, n) => this._renderSlot(e, t, n)
	});
	_slots = this._scroller.slots;
	_layout = new Le({
		current: () => this._doc,
		destroyed: () => this._destroyed,
		report: (e) => this._reportRenderError(e),
		reportBackground: (e) => this._errorRouter.reportBackground(e, this._opts.onLayoutComplete !== void 0),
		invalidateFind: () => this._find.invalidate(),
		refreshComments: () => this._refreshCommentSurface(),
		adoptView: (e) => {
			e.requester !== this && (this._layoutViewGeneration++, this._showTrackedChanges = e.view.showTrackedChanges, this._currentDate = e.view.currentDate, this._find.invalidate(), this._layout.apply({
				pageCount: this._doc.pageCount,
				exact: !0,
				complete: this._doc.layoutComplete
			}));
		},
		relayout: () => this.relayout(),
		invalidateRender: () => {
			this._renderEpoch++;
		},
		mounted: () => this._slots,
		stillMounted: (e, t) => this._slots.get(e) === t,
		refreshSlot: (e, t) => this._refreshSlotAtomically(e, t)
	});
	_renderHooks = {
		slots: () => this._slots,
		epoch: () => this._renderEpoch,
		scale: () => this._scale,
		slotIndex: (e) => e.renderedPage,
		token: () => 0,
		nextToken: () => 0,
		wantRuns: (e) => !!(this._opts.enableTextSelection && e.textLayer) || this._findActive || !!e.commentTintLayer,
		reportError: (e) => this._reportRenderError(e)
	};
	_bitmap = new de({
		...this._renderHooks,
		inFlight: () => this._scroller.inFlight,
		destroyed: () => this._destroyed,
		width: (e) => this._pageWidthPx(e),
		dpr: () => this._viewport.dpr(),
		canRetry: () => !0,
		render: (e, t, n, r, i) => J(this._doc, t, e, "worker", {
			width: n,
			dpr: r,
			imageResources: this._opts.imageResources,
			defaultTextColor: this._opts.defaultTextColor,
			currentDate: this._currentDate,
			...this._showTrackedChanges ? { showTrackedChanges: !0 } : {},
			onTextRun: i,
			...this._opts.errorPlaceholder === void 0 ? {} : { errorPlaceholder: this._opts.errorPlaceholder }
		}),
		commitBitmap: (e, t, n, r, i, a) => n.commitBitmap(r, i, {
			cssWidth: a,
			cssHeight: this._pageHeightPx(e)
		}),
		commitRuns: (e, t, n, r, i) => this._commitRenderedRuns(e, t, n, t.canvas, i, !0)
	});
	_main = new fe({
		...this._renderHooks,
		render: (e, t, n, r, i) => J(this._doc, t, e, "main", {
			width: n,
			dpr: r,
			imageResources: this._opts.imageResources,
			defaultTextColor: this._opts.defaultTextColor,
			currentDate: this._currentDate,
			...this._showTrackedChanges ? { showTrackedChanges: !0 } : {},
			onTextRun: i,
			...this._opts.errorPlaceholder === void 0 ? {} : { errorPlaceholder: this._opts.errorPlaceholder }
		}),
		commitRuns: (e, t, n, r, i, a, o) => this._commitRenderedRuns(e, t, n, r, a, o),
		shadow: () => this._pageShadow
	});
	_navigation = new me({
		host: () => this._scrollHost,
		spacer: () => this._spacer,
		count: () => this.pageCount,
		established: () => this._scaleEstablished,
		offset: (e) => this._scrollGeometry.offsets[e] ?? 0,
		height: (e) => this._heights[e] || 0,
		indexAt: (e) => this._pageIndexAtOffset(this._range(), e),
		totalHeight: () => this._scrollGeometry.totalHeight,
		width: (e) => this._pageWidthPx(e),
		padLeft: () => this._viewport.horizontalPadding().left,
		marginOrigin: () => this._commentMargin.originPx,
		mount: () => this._mountVisible()
	});
	_selection = new ge({
		wrapper: () => this._wrapper,
		scrollHost: () => this._scrollHost,
		slots: () => this._slots,
		resource: () => this._doc,
		destroyed: () => this._destroyed,
		textSelectionEnabled: () => this._opts.enableTextSelection === !0,
		elementSelectionEnabled: () => this._opts.enableElementSelection === !0,
		textSelected: () => q(this._wrapper, this._wrapper.ownerDocument?.getSelection?.() ?? null) !== null,
		getContext: () => this.getSelectionContext(),
		hitTest: (e, t, n, r) => {
			let i = e.pageSize(t);
			return e.getElementContextAt(t, {
				xPt: n * i.widthPt,
				yPt: r * i.heightPt
			}, {
				currentDate: this._currentDate,
				...this._showTrackedChanges ? { showTrackedChanges: !0 } : {},
				maxTextCharacters: F
			});
		},
		outline: (e, t, n) => {
			if (n.pageIndex !== t) return null;
			let r = e.pageSize(t);
			return {
				x: n.bounds.xPt / r.widthPt,
				y: n.bounds.yPt / r.heightPt,
				width: n.bounds.widthPt / r.widthPt,
				height: n.bounds.heightPt / r.heightPt
			};
		},
		onChange: (e) => this._opts.onSelectionContextChange?.(e),
		onContextMenu: (e, t) => this._opts.onContextMenu?.({
			originalEvent: e,
			getContext: t
		}),
		reportError: (e) => this._reportRenderError(e)
	});
	_heights = [];
	_scrollGeometry = {
		offsets: [],
		totalHeight: 0
	};
	_visibleEvents = new _e((e, t, n) => this._opts.onVisiblePageChange?.(e, t, n));
	_loader = new oe({
		name: () => "DocxScrollViewer",
		borrowed: () => this._borrowed,
		borrowedMessage: () => "DocxScrollViewer.load() is unsupported on a Viewer created by fromDocument(); the borrowed document is already loaded.",
		destroyed: () => this._destroyed,
		owner: () => this._documentOwner,
		beginLoad: () => {
			let e = this._pendingRequestedView;
			this._pendingLoadAbort?.abort();
			let t = new AbortController();
			return this._pendingLoadAbort = t, this._pendingRequestedView = e, t;
		},
		isCurrentLoad: (e) => this._pendingLoadAbort === e,
		finishLoad: (e) => {
			this._pendingLoadAbort === e && (this._pendingLoadAbort = null, this._pendingRequestedView = void 0, this._pendingViewChanged = null);
		},
		acquire: async (e, t) => {
			let n = this._pendingRequestedView, r = await R.load(e, {
				password: this._opts.password,
				useGoogleFonts: this._opts.useGoogleFonts,
				fonts: this._opts.fonts,
				allowFootnoteContinuation: this._opts.allowFootnoteContinuation,
				cjkFallback: this._opts.cjkFallback,
				maxZipEntryBytes: this._opts.maxZipEntryBytes,
				resourceLimits: this._opts.resourceLimits,
				debug: this._opts.debug,
				onResourceMetrics: this._opts.onResourceMetrics,
				workerTimeoutMs: this._opts.workerTimeoutMs,
				wasmUrl: this._opts.wasmUrl,
				math: this._opts.math,
				threeD: this._opts.threeD,
				regionMap: this._opts.regionMap,
				chartEx: this._opts.chartEx,
				tiff: this._opts.tiff,
				mode: this._mode,
				...n === void 0 ? N(this._opts) ? this._requestedShowTrackedChanges === void 0 ? void 0 : { showTrackedChanges: this._requestedShowTrackedChanges } : this._showTrackedChanges ? { showTrackedChanges: !0 } : {} : { showTrackedChanges: n },
				...this._currentDate === void 0 ? {} : { currentDate: this._currentDate },
				...this._opts.legacyDoc === void 0 ? void 0 : { legacyDoc: this._opts.legacyDoc },
				...this._opts.odt === void 0 ? void 0 : { odt: this._opts.odt },
				...this._opts.progressiveLayout ? { progressiveLayout: !0 } : {},
				...this._opts.sliceLayout === void 0 ? {} : { sliceLayout: this._opts.sliceLayout },
				[I]: {
					signal: t.signal,
					requestedView: () => this._pendingRequestedView,
					subscribeViewChange: (e) => (this._pendingViewChanged = e, () => {
						this._pendingViewChanged === e && (this._pendingViewChanged = null);
					})
				},
				onLayoutProgress: this._opts.onLayoutProgress,
				onLayoutPartial: this._opts.onLayoutPartial,
				onLayoutComplete: this._opts.onLayoutComplete
			});
			return await P(r, t.signal, () => this._pendingRequestedView, () => this._currentDate, this), r;
		},
		beforeReplace: (e) => {
			if (this._selection.invalidateElementContext(!1), this._findRequestGeneration++, this._find.invalidate(), this._findActive = !1, this._activeCommentId = null, this._activeCommentPage = null, this._commentNavigation.reset(), this._partFailureDelivery.attach(null), this._layout.unbind(), e) {
				for (let [e, t] of [...this._slots]) this._recycleSlot(e, t);
				this._visibleEvents.reset();
			}
		},
		afterReplace: (e) => {
			this._pendingRequestedView !== void 0 && (this._showTrackedChanges = this._pendingRequestedView, this._requestedShowTrackedChanges = this._pendingRequestedView), N(this._opts) && (this._showTrackedChanges = A(e).showTrackedChanges), this._layout.bind(e), this._partFailureDelivery.attach(M(e)), this._find.invalidate(), this._findActive = !1, this._activeCommentId = null, this._activeCommentPage = null, this._commentNavigation.reset();
		},
		mountOpeningWindow: async () => {
			let e = [];
			this._relayout(e), await Promise.all(e);
		},
		selectionChanged: () => this._selection.emitChange()
	});
	_activeCommentId = null;
	_activeCommentPage = null;
	_commentUi = null;
	_internalHyperlinkGeneration = 0;
	_commentAnchorRangesForMargin = null;
	_commentAnchorIds = /* @__PURE__ */ new Set();
	_commentMargin = new pe({
		container: () => this._container,
		scrollHost: () => this._scrollHost,
		spacer: () => this._spacer,
		enabled: () => this._commentsEnabled(),
		cards: () => this._commentsOptions()?.cards !== !1,
		hasDisplayableComments: () => this._hasDisplayableComments(),
		requestedSide: () => this._commentsOptions()?.side,
		zoom: () => this._scaleEstablished ? this._scale : 1,
		gapPx: Re,
		widthPx: 280,
		fontSizePx: ze
	});
	_layers = new xe({
		markerLayer: (e) => e.commentTintLayer,
		syncMargin: (e) => this._commentMargin.syncMargin(e),
		marginSide: () => this._commentMargin.side(),
		marginExtent: () => this._commentMargin.extent(),
		commentsEnabled: () => this._commentsEnabled(),
		previewMargin: (e, t) => this._commentUi?.previewReadOnlyCommentMargin(e, t),
		disposeMargin: (e) => {
			this._commentUi?.disposeReadOnlyCommentMargin(e), this._commentUi || e.replaceChildren();
		},
		disposeDecoration: (e) => {
			this._commentUi?.disposeReadOnlyCommentDecoration(e), this._commentUi || e.replaceChildren();
		},
		redrawOutline: (e, t) => this._selection.redrawOutlineForSlot(e, t),
		markerRatio: (e) => e,
		resetMarkerTransform: () => !0,
		resetDecorationVisibility: () => !1
	});
	_commentNavigation = new Ie({
		document: () => this._doc,
		destroyed: () => this._destroyed,
		scale: () => this._scale,
		pageWidth: (e) => this._pageWidthPx(e),
		currentDate: () => this._currentDate,
		showTrackedChanges: () => this._showTrackedChanges,
		waitForLayout: (e) => this._errorRouter.ownBackgroundLifecycle(() => e.waitUntilLayoutComplete()),
		select: (e, t, n, r) => {
			this._activeCommentId = e, this._activeCommentPage = t, this._selection.clearElementContext(), this._scrollToPageTarget(t, n, r);
			for (let [e, t] of this._slots) this._redrawSlotComments(e, t);
			this._selection.emitChange();
		}
	});
	_commentOverlay = new be({
		slots: () => this._slots,
		scale: () => this._scale,
		destroyed: () => this._destroyed,
		ownerWindow: () => this._wrapper.ownerDocument.defaultView,
		width: (e) => this._pageWidthPx(e),
		height: (e) => this._pageHeightPx(e),
		side: () => this._commentMargin.side(),
		marginExtent: () => this._commentMargin.extent(),
		connectorOptions: () => this._commentsOptions()?.connectors,
		runtime: () => this._commentUi,
		redrawComments: (e, t) => this._redrawSlotComments(e, t)
	});
	_destroyed = !1;
	_partFailureDelivery;
	get _renderEpoch() {
		return this._scroller.renderEpoch;
	}
	set _renderEpoch(e) {
		this._scroller.renderEpoch = e;
	}
	get _prevBase() {
		return this._zoom.prevBase;
	}
	set _prevBase(e) {
		this._zoom.prevBase = e;
	}
	_pageShadow;
	_find = new G(() => this.pageCount, (e) => this._collectPageRuns(e));
	_findActive = !1;
	_highlights = new ae({
		slots: () => this._slots,
		active: () => this._findActive,
		runs: (e) => this._find.pageRuns(e),
		setRuns: (e, t) => this._find.setPageRuns(e, t),
		paint: (e, t, n, r) => W(t.highlightLayer, n, this._find.pageHighlights(e), this._pageWidthPx(e), this._pageHeightPx(e), r, this._opts.findHighlightColors),
		reveal: (e) => this.scrollToPage(e),
		unitOf: (e) => e.page
	});
	_findRequestGeneration = 0;
	_showTrackedChanges;
	_currentDate;
	_layoutViewGeneration = 0;
	static fromDocument(t, n, r = {}) {
		let i = A(n);
		return new e(t, {
			...r,
			currentDate: i.currentDate,
			showTrackedChanges: i.showTrackedChanges,
			[Z]: n
		});
	}
	constructor(e, t = {}) {
		if (e.tagName === "CANVAS") throw Error("DocxScrollViewer takes a container element (e.g. a <div>), not a <canvas> — the viewer creates and manages its own canvases. Pass a block container; for the single-page canvas API use DocxViewer.");
		this._container = e, this._opts = t, this._errorRouter = new g("DocxScrollViewer", t.onError), k(t.errorPlaceholder), this._partFailureDelivery = new O("DocxScrollViewer", t.onPartFailure, () => "document"), this._showTrackedChanges = t.showTrackedChanges === !0, N(t) && (this._requestedShowTrackedChanges = t.showTrackedChanges), this._currentDate = t.currentDate, this._pageShadow = t.pageShadow ?? "0 1px 3px rgba(0,0,0,0.2)";
		let n = t[Z];
		this._borrowed = n !== void 0, n ? (this._documentOwner = new y("DocxScrollViewer", n, !1), this._mode = C("DocxScrollViewer", t.mode, n)) : (this._documentOwner = new y("DocxScrollViewer"), this._mode = C("DocxScrollViewer", t.mode, void 0)), this._shell = new Se(e, {
			background: t.background,
			comments: !!t.comments,
			onScroll: () => this._onScroll(),
			onOutsideComment: () => {
				if (this._activeCommentId !== null) {
					this._activeCommentId = null, this._activeCommentPage = null;
					for (let [e, t] of this._slots) this._redrawSlotComments(e, t);
					this._selection.emitChange();
				}
			}
		}), this._commentsEnabled() && Ve().then((e) => {
			if (!this._destroyed) {
				this._commentUi = e;
				for (let [e, t] of this._slots) this._redrawSlotComments(e, t);
			}
		}).catch((e) => this._reportRenderError(e)), this._selection.bind(!!t.onSelectionContextChange, !!t.onContextMenu), this._zoom.bind(this._container, this._scrollHost, this._opts.enableZoom !== !1), this._borrowed && (this._layout.bind(n), this._partFailureDelivery.attach(M(n)), this.relayout());
	}
	async load(e) {
		let t = this._partFailureDelivery.beginLoad();
		try {
			await this._loader.load(e);
		} finally {
			let e = this._destroyed ? null : this._doc;
			this._partFailureDelivery.endLoad(t, e ? M(e) : null);
		}
	}
	get pageCount() {
		return this._doc?.pageCount ?? 0;
	}
	get partFailures() {
		return this._destroyed ? [] : this._doc?.partFailures ?? [];
	}
	get layoutComplete() {
		return this._doc?.layoutComplete ?? !0;
	}
	async waitUntilLayoutComplete() {
		await this._errorRouter.ownBackgroundLifecycle(async () => {
			await this._doc?.waitUntilLayoutComplete?.();
		});
	}
	_refreshCommentSurface() {
		if (!(!this._commentsEnabled() || this._slots.size === 0)) {
			this._syncSpacerWidth();
			for (let [e, t] of this._slots) this._redrawSlotComments(e, t);
		}
	}
	_pageWidthPx(e) {
		return this._doc.pageSize(e).widthPt * o * this._scale;
	}
	_pageHeightPx(e) {
		return this._doc.pageSize(e).heightPt * o * this._scale;
	}
	_hasDisplayableComments() {
		if (!this._commentsEnabled()) return !1;
		let e = this._doc;
		if (!e) return !1;
		let t = e.commentAnchorRanges();
		if (this._commentAnchorRangesForMargin !== t && (this._commentAnchorRangesForMargin = t, this._commentAnchorIds = new Set(t.map((e) => e.commentId))), this._commentAnchorIds.size === 0) return !1;
		let n = this._commentsOptions()?.includeResolved === !0;
		return e.comments.some((e) => this._commentAnchorIds.has(e.id) && e.parentId === void 0 && (n || e.resolved !== !0));
	}
	_commentsEnabled() {
		return this._opts.comments === !0 || typeof this._opts.comments == "object";
	}
	_commentsOptions() {
		return typeof this._opts.comments == "object" ? this._opts.comments : void 0;
	}
	_widestPageWidthPt() {
		if (!this._doc) return 0;
		let e = 0, t = this._layout.presentedPageCount || this._doc.pageCount;
		for (let n = 0; n < t; n++) {
			let t = this._doc.pageSize(n).widthPt;
			t > e && (e = t);
		}
		return e;
	}
	_baseScale() {
		if (!this._doc || this._doc.pageCount === 0) return 0;
		let e = this._viewport.fitWidth();
		if (e <= 0) return 0;
		let t = this._widestPageWidthPt();
		return t <= 0 ? 0 : e / (t * o);
	}
	relayout() {
		this._relayout();
	}
	_relayout(e) {
		if (this._doc) {
			if (this._doc.layoutComplete !== !1 && (this._layout.presentedPageCount = this._doc.pageCount), this._scaleEstablished) {
				let e = this._baseScale();
				if (e > 0 && e !== this._prevBase) {
					let t = this._prevBase > 0 ? this._scale / this._prevBase : 1;
					this._prevBase = e, this.setScale(e * t);
				}
			} else if (!this._zoom.establishBase()) return;
			this._recomputeHeights(), this._syncSpacer(), this._mountVisible(e);
			for (let [e, t] of this._slots) t.renderedPage === e && t.renderedScale >= 0 && this._redrawSlotComments(e, t);
		}
	}
	_recomputeHeights() {
		let e = Math.min(this._layout.presentedPageCount, this._doc.pageCount), t = Array(e);
		for (let n = 0; n < e; n++) t[n] = this._pageHeightPx(n);
		this._heights = t, this._scrollGeometry = ie(t, this._viewport.gap(), this._viewport.verticalPadding());
	}
	_pageIndexAtOffset(e, t) {
		let { offsets: n } = e, r = 0, i = n.length - 1, a = 0;
		for (; r <= i;) {
			let e = r + i >> 1;
			n[e] <= t ? (a = e, r = e + 1) : i = e - 1;
		}
		return a;
	}
	_range() {
		return Ce(this._scrollGeometry, this._scrollHost.scrollTop, this._scrollHost.clientHeight, this._viewport.overscan());
	}
	_syncSpacer() {
		this._scroller.syncSpacer();
	}
	_syncSpacerWidth() {
		let { left: e, right: t } = this._viewport.horizontalPadding(), n = 0;
		for (let e = 0; e < this._heights.length; e++) {
			let t = this._pageWidthPx(e);
			t > n && (n = t);
		}
		this._commentMargin.syncSpacerWidth(n, e, t);
	}
	_onScroll() {
		!this._doc || !this._scaleEstablished || this._mountVisible(void 0, !1);
	}
	_mountVisible(e, t = !0) {
		this._scroller.mount(e, t);
	}
	_emitVisiblePageChange(e) {
		this._doc && this._visibleEvents.publish(e, this._doc.pageCount, this.layoutComplete);
	}
	_createSlot() {
		let { wrapper: e, canvas: t, textLayer: n, highlightLayer: r } = he(this._scrollHost, this._opts.enableTextSelection === !0, this._pageShadow), { markerLayer: i, margin: a, decorationLayer: o } = ve(e, this._commentsEnabled(), this._commentsOptions()?.cards !== !1, this._commentsOptions()?.connectors !== void 0, (e) => this._commentMargin.syncMargin(e)), s = x(e, this._opts.enableElementSelection === !0);
		return this._scrollHost.appendChild(e), {
			wrapper: e,
			canvas: t,
			textLayer: n,
			highlightLayer: r,
			elementLayer: s,
			commentTintLayer: i,
			commentMargin: a,
			commentDecorationLayer: o,
			commentRuns: Object.freeze([]),
			commentGeometry: null,
			renderedPage: -1,
			renderedScale: -1,
			dispatcher: new f(t, this._mode === "worker")
		};
	}
	_recycleSlot(e, t) {
		this._scroller.recycleSlot(e, t);
	}
	_resetSlot(e, t) {
		t.dispatcher.destroy(), this._destroyed || (t.dispatcher = new f(t.canvas, this._mode === "worker")), this._layers.reset(t), t.commentRuns = Object.freeze([]), t.commentGeometry = null, t.renderedPage = -1, t.renderedScale = -1, t.wrapper.remove();
	}
	_positionSlot(e, t, n) {
		this._layers.position(t, e, n.offsets[t], this._pageWidthPx(t), this._pageHeightPx(t), this._scrollHost.clientWidth, this._viewport.horizontalPadding().left);
	}
	_renderSlot(e, t, n = !0) {
		if (!this._doc || t.renderedPage === e) return null;
		t.renderedPage = e;
		let r = this._viewport.dpr(), i = this._pageWidthPx(e), a = this._scale, o = t.dispatcher, s = o.begin();
		return this._mode === "worker" ? this._renderSlotBitmap(e, t, i, r, a, o, s, n) : this._main.render(e, t, i, r, 0, o, s, n);
	}
	_hyperlinkHandler() {
		return this._opts.enableHyperlinks === !1 ? void 0 : this._opts.onHyperlinkClick || ((e) => {
			if (e.kind === "external") {
				E(e.url);
				return;
			}
			let t = this._doc;
			if (!t) return;
			let n = ++this._internalHyperlinkGeneration;
			this._navigateInternalHyperlink(t, e.ref, n).catch((e) => this._reportRenderError(e));
		});
	}
	async _navigateInternalHyperlink(e, t, n) {
		if (e.layoutComplete || await e.waitUntilLayoutComplete(), this._destroyed || this._doc !== e || n !== this._internalHyperlinkGeneration) return;
		let r = e.getBookmarkPage(t);
		r !== void 0 && this.scrollToPage(r);
	}
	_canvasCssPx(e) {
		return {
			width: parseFloat(e.style.width) || e.width,
			height: parseFloat(e.style.height) || e.height
		};
	}
	_commitRenderedRuns(e, t, n, r, i, a) {
		if (t.textLayer && (a && this._clearTextLayerPreview(t.textLayer), this._opts.enableTextSelection)) {
			let { width: i, height: a } = this._canvasCssPx(r);
			U(t.textLayer, n, i, a, this._hyperlinkHandler(), (e) => this._highlights.measure(e), e);
		}
		i && this._highlights.refreshRuns(e, n), this._commitCommentRuns(e, t, n), this._highlights.redrawSlot(e, t);
	}
	_reportRenderError(e) {
		this._errorRouter.report(e);
	}
	_renderSlotBitmap(e, t, n, r, i, a = t.dispatcher, o = a.begin(), s = !0) {
		return this._bitmap.render(e, t, n, r, i, 0, a, o, s);
	}
	setScale(e) {
		this._zoom.setScale(e);
	}
	getScale() {
		return this._zoom.getScale();
	}
	zoomIn() {
		this._zoom.zoomIn();
	}
	zoomOut() {
		this._zoom.zoomOut();
	}
	fitWidth() {
		this._zoom.fit("width");
	}
	fitPage() {
		this._zoom.fit("page");
	}
	_previewVisible() {
		this._scroller.preview();
	}
	_previewSlot(e, t, n) {
		this._positionSlot(e, t, n), this._layers.preview(e, this._pageWidthPx(t), this._pageHeightPx(t), this._scale);
	}
	_clearTextLayerPreview(e) {
		ue(e);
	}
	_scheduleSettle() {
		this._scroller.scheduleSettle(150);
	}
	_refreshSlotAtomically(e, t) {
		if (!this._doc) return;
		let n = this._viewport.dpr(), r = this._pageWidthPx(e), i = this._scale;
		if (this._mode === "worker") {
			this._renderSlotBitmap(e, t, r, n, i);
			return;
		}
		this._main.settle(e, t, r, n);
	}
	async setShowTrackedChanges(e) {
		let t = ++this._layoutViewGeneration;
		if (this._pendingLoadAbort) {
			let t = this._pendingRequestedView !== e;
			this._pendingRequestedView = e, t && this._pendingViewChanged?.();
		}
		let n = this._doc;
		if (N(this._opts) && (this._requestedShowTrackedChanges = e), this._showTrackedChanges === e) {
			n && await L(n, {
				showTrackedChanges: e,
				currentDate: this._currentDate
			}, this);
			return;
		}
		(!n || await L(n, {
			showTrackedChanges: e,
			currentDate: this._currentDate
		}, this)) && (this._destroyed || t !== this._layoutViewGeneration || n !== this._doc || (this._showTrackedChanges = e, N(this._opts) && (this._requestedShowTrackedChanges = e), this._find.invalidate(), this._layout.apply({
			pageCount: n?.pageCount ?? 0,
			exact: !0,
			complete: n?.layoutComplete !== !1
		})));
	}
	scrollToPage(e, t) {
		this._navigation.scrollToUnit(e, t);
	}
	_scrollToPageTarget(e, t, n) {
		this._navigation.scrollToPoint(e, t.x + t.w / 2, t.y + t.h / 2, n);
	}
	async goToComment(e, t) {
		return this._commentNavigation.goToComment(e, t);
	}
	async findText(e, t = {}) {
		if (!this._doc) return [];
		let n = ++this._findRequestGeneration;
		if (this._doc.layoutComplete === !1) {
			let e = this._doc;
			if (await this._errorRouter.ownBackgroundLifecycle(() => e.waitUntilLayoutComplete()), this._destroyed || this._doc !== e || n !== this._findRequestGeneration) return [];
		}
		this._findActive = e.length > 0;
		let r = await this._errorRouter.ownAwaitable(() => this._find.find(e, t));
		return this._highlights.redrawAll(), r;
	}
	async findNext() {
		return this._highlights.activate(this._find.next());
	}
	async findPrev() {
		return this._highlights.activate(this._find.prev());
	}
	clearFind() {
		this._findRequestGeneration++, this._findActive = !1, this._find.invalidate(), this._highlights.redrawAll();
	}
	async _collectPageRuns(e) {
		return this._doc ? this._doc.collectPageRuns(e, {
			width: this._pageWidthPx(e),
			currentDate: this._currentDate,
			...this._showTrackedChanges ? { showTrackedChanges: !0 } : {}
		}) : [];
	}
	_commitCommentRuns(e, t, n) {
		t.commentTintLayer && (t.commentRuns = Object.freeze([...n]), this._commentNavigation.commitRuns(e, t.commentRuns), t.commentTintLayer.style.transform = "", t.commentTintLayer.style.transformOrigin = "", this._redrawSlotComments(e, t), t.commentTintLayer.style.visibility = "", t.commentMargin && (t.commentMargin.style.visibility = ""), t.commentDecorationLayer && (t.commentDecorationLayer.style.visibility = ""));
	}
	_redrawSlotComments(e, t) {
		if (!this._doc || !t.commentTintLayer) return;
		this._commentMargin.syncMargin(t.commentMargin);
		let n = this._commentUi;
		if (!n) {
			t.commentTintLayer.replaceChildren(), t.commentMargin?.replaceChildren(), t.commentDecorationLayer?.replaceChildren(), t.commentGeometry = null;
			return;
		}
		t.commentGeometry = n.buildDocxCommentMargin(t.commentTintLayer, t.commentMargin, t.commentRuns, {
			comments: this._doc.comments,
			anchors: this._doc.commentAnchorRanges()
		}, this._pageWidthPx(e), this._pageHeightPx(e), this._activeCommentId, (t, n) => {
			let r = n ? t : this._activeCommentId === t ? null : this._activeCommentId;
			if (r !== this._activeCommentId) {
				this._activeCommentId = r, this._activeCommentPage = r ? e : null, this._selection.clearElementContext();
				for (let [e, t] of this._slots) this._redrawSlotComments(e, t);
				this._selection.emitChange();
			}
		}, this._commentMargin.zoom(), 280, this._commentsOptions()?.markers !== !1, this._commentsOptions()?.includeResolved === !0, t.commentDecorationLayer ? () => this._commentOverlay.schedule(e, t, !1) : void 0, t.commentDecorationLayer ? () => this._commentOverlay.schedule(e, t, !0) : void 0), this._commentOverlay.drawConnectors(e, t);
	}
	get topVisiblePage() {
		return this._scroller.lastRange?.topIndex ?? 0;
	}
	async getResourceMetrics() {
		if (!this._doc) throw Error("Document not loaded");
		return await this._doc.getResourceMetrics();
	}
	getSelectionContext(e = {}) {
		if (this._destroyed) throw Error("DocxScrollViewer is destroyed");
		return (this._doc && this._activeCommentId !== null && this._activeCommentPage !== null ? Ne(this._doc.comments, this._doc.commentAnchorRanges(), this._activeCommentId, this._activeCommentPage, e) : null) || ((this._opts.enableTextSelection ? q(this._wrapper, this._wrapper.ownerDocument?.getSelection?.() ?? null, e) : null) ?? (this._selection.elementContext ? je(this._selection.elementContext, e.maxTextCharacters) : null));
	}
	destroy() {
		this._destroyed || (this._destroyed = !0, this._pendingLoadAbort?.abort(), this._pendingLoadAbort = null, this._pendingViewChanged = null, this._findRequestGeneration++, this._errorRouter.close(), this._partFailureDelivery.close(), this._layout.unbind(), this._layoutViewGeneration++, this._commentNavigation.reset(), this._find.invalidate(), this._findActive = !1, this._selection.destroy(), this._highlights.destroy(), this._commentOverlay.destroy(), this._selection.clearElementContext(), this._scroller.destroy(), this._zoom.destroy(), this._commentMargin.destroy(), this._documentOwner.close(), this._shell.destroy());
	}
};
function $(e) {
	let t = [];
	for (let n of e.content) {
		if (n.type !== "paragraph") continue;
		let e = "";
		for (let t of n.runs) t.type === "text" && !t.noteRef && (e += t.text);
		e = e.trim(), e && t.push(e);
	}
	return t.join(" ");
}
var He = /* @__PURE__ */ e({
	DocxDocument: () => R,
	DocxScrollViewer: () => Q,
	DocxViewer: () => X,
	OoxmlDecodedImageLimitError: () => c,
	OoxmlError: () => r,
	OoxmlResourceLimitError: () => n,
	TiffDecodeError: () => u,
	autoResize: () => te,
	buildDocxHighlightLayer: () => W,
	buildDocxTextLayer: () => U,
	fontCss: () => Oe,
	fontCssApi: () => Ee,
	fontFiles: () => De,
	fontResolver: () => ke,
	googleFonts: () => re,
	googleFontsSubstitutions: () => ne,
	isOoxmlDecodedImageLimitError: () => s,
	isTiffDecodeError: () => l,
	noteText: () => $,
	officeFontSubstitutions: () => t,
	openExternalHyperlink: () => E,
	readDocxTextSelectionContext: () => q,
	resolveCommentAnchorRuns: () => V,
	resolveDocxCommentThreads: () => Me,
	resolveRevisionAnchorRuns: () => Ae
});
export { q as a, X as i, $ as n, W as o, Q as r, U as s, He as t };
