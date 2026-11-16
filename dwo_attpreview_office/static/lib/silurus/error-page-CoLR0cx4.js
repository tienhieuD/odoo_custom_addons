import { n as e, t } from "./error-placeholder-text-DT-UPN5r.js";
var n = Object.freeze({
	story: "body",
	storyInstance: "parse-error",
	path: Object.freeze([])
});
function r(e) {
	let { errorPlaceholderDetail: r, errorPlaceholderTitle: i, wrapErrorPlaceholderText: a } = t(e);
	function o(e, t, n, r, i, o) {
		return a(e, t, i, (e) => r.shape(o === void 0 ? {
			text: e,
			fontSizePt: n,
			fonts: {},
			genericFamily: "sans-serif"
		} : {
			text: e,
			fontSizePt: n,
			weight: o,
			fonts: {},
			genericFamily: "sans-serif"
		}).advancePt);
	}
	function s(t, a, s, c = null) {
		if (!(a.widthPt > 0 && a.heightPt > 0)) throw RangeError("Error page size must be positive");
		let l = Math.max(18, Math.min(a.widthPt, a.heightPt) * .06), u = {
			xPt: l,
			yPt: l,
			widthPt: a.widthPt - l * 2,
			heightPt: a.heightPt - l * 2
		}, d = Math.max(8, Math.min(a.widthPt, a.heightPt) * .02), f = s.resolve({
			fonts: {},
			slot: "ascii",
			genericFamily: "sans-serif"
		}).route, p = r(c, t), m = p === null ? [] : o(p, a.widthPt - l * 4, d, s, 4), h = d * 1.4, g = o(i(c, "This document could not be displayed"), a.widthPt - l * 4, 13, s, 1, 600)[0] ?? "", _ = [
			{
				kind: "fill-rect",
				rect: {
					xPt: 0,
					yPt: 0,
					widthPt: a.widthPt,
					heightPt: a.heightPt
				},
				fill: "#ffffff"
			},
			{
				kind: "stroke-rect",
				rect: u,
				stroke: "#c8ccd2",
				lineWidthPt: 1,
				dashPt: [6, 5]
			},
			{
				kind: "text",
				rect: {
					xPt: 0,
					yPt: a.heightPt * .27,
					widthPt: a.widthPt,
					heightPt: 36
				},
				text: "⚠",
				fill: "#b23b3b",
				fontRoute: f,
				fontSizePt: 28,
				fontWeight: 400,
				fontStyle: "normal",
				align: "center",
				baseline: "middle"
			},
			{
				kind: "text",
				rect: {
					xPt: l * 2,
					yPt: a.heightPt * .4,
					widthPt: a.widthPt - l * 4,
					heightPt: 24
				},
				text: g,
				fill: "#333333",
				fontRoute: f,
				fontSizePt: 13,
				fontWeight: 600,
				fontStyle: "normal",
				align: "center",
				baseline: "middle"
			},
			...m.map((e, t) => ({
				kind: "text",
				rect: {
					xPt: l * 2,
					yPt: a.heightPt * .5 + h * t,
					widthPt: a.widthPt - l * 4,
					heightPt: h
				},
				text: e,
				fill: "#666666",
				fontRoute: f,
				fontSizePt: d,
				fontWeight: 400,
				fontStyle: "normal",
				align: "center",
				baseline: "middle"
			}))
		], v = {
			kind: "drawing",
			id: "parse-error-page",
			source: n,
			flowDomainId: "parse-error",
			flowBounds: u,
			inkBounds: u,
			advancePt: u.heightPt,
			ordinaryFlow: !1,
			commands: _
		}, y = {
			geometry: {
				pageWidth: a.widthPt,
				pageHeight: a.heightPt,
				marginTop: l,
				marginRight: l,
				marginBottom: l,
				marginLeft: l,
				headerDistance: 0,
				footerDistance: 0
			},
			columns: [{
				xPt: l,
				wPt: u.widthPt
			}],
			columnSeparator: !1,
			grid: {
				kind: "none",
				linePitchPt: null,
				charSpacePt: null
			},
			textDirection: "lrTb",
			verticalAlignment: "top"
		};
		return {
			pages: [{
				pageIndex: 0,
				geometry: {
					xPt: 0,
					yPt: 0,
					widthPt: a.widthPt,
					heightPt: a.heightPt,
					contentTopPt: l,
					contentBottomPt: a.heightPt - l
				},
				flowDomains: [{
					id: "parse-error",
					kind: "body",
					logicalBounds: u,
					physicalBounds: u
				}],
				section: y,
				sectionOccurrenceId: "parse-error-section",
				pageBorder: null,
				parityBlank: !1,
				bookmarkStarts: [],
				pageNumber: {
					displayNumber: 1,
					format: "decimal",
					sectionOccurrenceId: "parse-error-section"
				},
				columnSeparators: [],
				sectionRegions: [{
					id: "parse-error-region",
					sectionOccurrenceId: "parse-error-section",
					coordinateSpace: {
						writingMode: "horizontal-tb",
						logicalToPhysical: {
							a: 1,
							b: 0,
							c: 0,
							d: 1,
							e: 0,
							f: 0
						},
						physicalToLogical: {
							a: 1,
							b: 0,
							c: 0,
							d: 1,
							e: 0,
							f: 0
						}
					},
					blockStartPt: l,
					blockEndPt: a.heightPt - l,
					columnFlowDirection: "ltr",
					columnIndexes: [0],
					flowDomainIds: ["parse-error"],
					section: y
				}],
				layers: e.createPageLayers([{
					layer: "body",
					node: v
				}]),
				readingOrder: [v.id]
			}],
			diagnostics: [{
				code: "UNSUPPORTED_FEATURE",
				severity: "error",
				source: n,
				message: t
			}]
		};
	}
	return s;
}
export { r as parseErrorPageLayout, e as resolvedFromWire };
