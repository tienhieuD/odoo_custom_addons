import { n as e, t } from "./error-placeholder-text-DT-UPN5r.js";
function n(n) {
	let { errorPlaceholderCanvasLines: r, errorPlaceholderDetail: i, errorPlaceholderTitle: a } = t(n);
	function o(t, n, o, s, c, l) {
		let u = e(l);
		t.save(), t.fillStyle = "#f7f7f8", t.fillRect(0, 0, n, o);
		let d = n / 2, f = Math.min(n, o), p = Math.max(20, f * .1);
		t.fillStyle = "#b23b3b", t.textAlign = "center", t.textBaseline = "middle", t.font = `${p}px sans-serif`, t.fillText("⚠", d, o * .32);
		let m = Math.max(13, f * .035);
		t.fillStyle = "#333333", t.font = `600 ${m}px sans-serif`;
		let h = a(u, `Sheet "${s}" could not be displayed`);
		for (let e of r(t, h, n * .9, 1)) t.fillText(e, d, o * .46);
		let g = i(u, c);
		if (g === null) {
			t.restore();
			return;
		}
		let _ = Math.max(10, f * .022);
		t.fillStyle = "#666666", t.font = `${_}px sans-serif`;
		let v = r(t, g, Math.min(n * .8, 640), 4), y = _ * 1.4, b = o * .52 + y;
		for (let e of v) t.fillText(e, d, b), b += y;
		t.restore();
	}
	return o;
}
export { n as sheetErrorOverlay };
