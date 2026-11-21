var sleep = function (ms) { return new Promise(function (r) { setTimeout(r, ms); }); };
var STYLE = "style[name=listview_sticky_header_and_column]";

/** closest scrolling ancestor of el */
function scroller(el) {
    var p = el.parentElement;
    while (p) {
        var o = getComputedStyle(p);
        if (/(auto|scroll)/.test(o.overflowX + o.overflowY) && (p.scrollWidth > p.clientWidth || p.scrollHeight > p.clientHeight)) {
            return p;
        }
        p = p.parentElement;
    }
    return document.scrollingElement;
}
/** Odoo 12: `.o_list_view` is the <table> itself */
function tableOf(root) { return root.tagName === 'TABLE' ? root : root.querySelector('table'); }
function fail(msg) { console.error("LABFAIL " + msg); }
function check(cond, msg) { if (!cond) { fail(msg); } return cond; }

/** pin the column `name` inside `root`, then verify the sticky behaviour while scrolling both ways */
async function pinAndScroll(root, name, label) {
    var th = root.querySelector("thead th[data-name=" + name + "]");
    if (!check(th, label + ": header " + name + " not found")) { return; }
    var idx = Array.prototype.indexOf.call(th.parentNode.children, th);
    th.querySelector(".js_pin_this_column").click();
    await sleep(900);
    check(document.head.querySelectorAll(STYLE).length >= 1, label + ": no style injected");
    var sc = scroller(tableOf(root));
    var ths = Array.prototype.slice.call(root.querySelectorAll("thead th"));
    var pinned = ths.slice(0, idx + 1);
    var free = ths.slice(idx + 1);
    pinned.forEach(function (t, i) { check(getComputedStyle(t).position === "sticky", label + ": th " + i + " not sticky"); });
    var rel = function (el) { return el.getBoundingClientRect().left - sc.getBoundingClientRect().left; };
    var freeBefore = free.length ? rel(free[free.length - 1]) : 0;
    sc.scrollLeft = 900;
    await sleep(300);
    var after = pinned.map(rel);
    // once scrolled, pinned column i must sit at the sum of the widths of the pinned columns before it
    var acc = 0;
    pinned.forEach(function (t, i) {
        check(Math.abs(after[i] - acc) < 3, label + ": pinned col " + i + " at " + after[i] + " instead of " + acc + " (scrollLeft=" + sc.scrollLeft + ")");
        acc += t.getBoundingClientRect().width;
    });
    if (free.length) {
        check(Math.abs(rel(free[free.length - 1]) - freeBefore) > 50 || sc.scrollLeft === 0, label + ": free columns did not scroll");
    }
    // body cells of the pinned columns follow too, and are opaque
    var row = root.querySelector("tbody tr.o_data_row");
    if (row) {
        Array.prototype.slice.call(row.children, 0, idx + 1).forEach(function (c, i) {
            check(Math.abs(rel(c) - after[i]) < 3, label + ": body cell " + i + " not aligned with header");
            check(getComputedStyle(c).backgroundColor !== "rgba(0, 0, 0, 0)", label + ": pinned cell " + i + " is transparent");
        });
    }
    sc.scrollTop = 600;
    await sleep(300);
    var top = ths[0].getBoundingClientRect().top - sc.getBoundingClientRect().top;
    check(top < 4 && top > -4, label + ": header not stuck on top (offset " + top + ")");
    check(getComputedStyle(ths[0]).backgroundColor !== "rgba(0, 0, 0, 0)", label + ": header transparent");
    sc.scrollTop = 0;
    sc.scrollLeft = 0;
    return { sc: sc, idx: idx };
}
