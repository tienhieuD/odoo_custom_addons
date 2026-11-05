import { registry } from "@web/core/registry";

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

registry.category("web_tour.tours").add("lshc_lab_wide_list", {
    steps: () => [
        { trigger: ".o_list_view .o_data_row", run: () => { void 0; } },
        { trigger: ".o_list_view thead th[data-name=category_id]:has(.js_pin_this_column)", run: async function () {
            try {
                var root = document.querySelector(".o_list_view");
                var cols = root.querySelectorAll("thead th[data-name]").length;
                check(cols >= 50, "expected >= 50 columns, got " + cols);
                await pinAndScroll(root, "category_id", "wide(cat)");
                // pin a column further right, then unpin by clicking again
                await pinAndScroll(root, "amount", "wide(amount)");
                root.querySelector("thead th[data-name=amount] .js_pin_this_column").click();
                await sleep(400);
                check(!document.head.querySelector(STYLE), "wide: style not removed on unpin");
                // pin again, then change the search panel (when the version has one): the pin must survive the reload
                root.querySelector("thead th[data-name=state] .js_pin_this_column").click();
                await sleep(700);
                var values = document.querySelectorAll(".o_search_panel_category_value header");
                var box = document.querySelector(".o_search_panel_filter_value input");
                var target = values.length > 1 ? values[1] : box;
                if (target) {
                    target.click();
                    await sleep(1500);
                    var root2 = document.querySelector(".o_list_view");
                    check(document.head.querySelector(STYLE), "wide: pin lost after search panel reload");
                    check(getComputedStyle(root2.querySelector("thead th:nth-child(3)")).position === "sticky", "wide: col not sticky after reload");
                }
            } catch (e) { fail(e.message + " " + e.stack); }
            document.body.classList.add("lab_done");
        } },
        { trigger: "body.lab_done", run: () => { void 0; } },
    ],
});

registry.category("web_tour.tours").add("lshc_lab_editable_list", {
    steps: () => [
        { trigger: ".o_list_view .o_data_row", run: () => { void 0; } },
        { trigger: ".o_list_view thead th[data-name=partner_id]:has(.js_pin_this_column)", run: async function () {
            try {
                var root = document.querySelector(".o_list_view");
                await pinAndScroll(root, "partner_id", "editable(partner)");
                // enter edit mode on a row: pinned columns must stay aligned
                root.querySelector("tbody tr.o_data_row td:nth-child(3)").click();
                await sleep(800);
                check(root.querySelector("tbody tr.o_selected_row"), "editable: row did not enter edit mode");
                var th = root.querySelector("thead th[data-name=partner_id]");
                check(getComputedStyle(th).position === "sticky", "editable: pin lost while editing");
                var sc = scroller(tableOf(root));
                sc.scrollLeft = 700;
                await sleep(300);
                var row = root.querySelector("tbody tr.o_selected_row");
                var rel = function (el) { return el.getBoundingClientRect().left - sc.getBoundingClientRect().left; };
                var idx = Array.prototype.indexOf.call(th.parentNode.children, th);
                check(Math.abs(rel(row.children[idx]) - rel(th)) < 3, "editable: edited row pinned cell misaligned: cell " + rel(row.children[idx]) + " th " + rel(th) + " idx " + idx + " cells " + row.children.length + " pos " + getComputedStyle(row.children[idx]).position + " rowclass " + row.className);
                sc.scrollLeft = 0;
            } catch (e) { fail(e.message + " " + e.stack); }
            document.body.classList.add("lab_done");
        } },
        { trigger: "body.lab_done", run: () => { void 0; } },
    ],
});

registry.category("web_tour.tours").add("lshc_lab_form_lists", {
    steps: () => [
        { trigger: ".o_list_view .o_data_row td:nth-child(3)", run: "click" },
        { trigger: ".o_form_view .o_notebook", run: () => { void 0; } },
        { trigger: ".o_form_view .o_field_widget[name=line_medium_ids] thead th[data-name=product]:has(.js_pin_this_column)", run: async function () {
            try {
                var form = document.querySelector(".o_form_view");
                var medium = form.querySelector(".o_field_widget[name=line_medium_ids]");
                var small = form.querySelector(".o_field_widget[name=line_small_ids]");
                check(small && medium, "form: x2many fields missing");
                check(small.querySelectorAll("thead th[data-name]").length >= 5, "form: small list columns");
                // pin in the medium list only
                medium.querySelector("thead th[data-name=product] .js_pin_this_column").click();
                await sleep(900);
                var owners = {};
                Array.prototype.forEach.call(document.head.querySelectorAll(STYLE), function (s) { owners[s.getAttribute("data-owner")] = 1; });
                check(Object.keys(owners).length === 1, "form: expected 1 owner style, got " + Object.keys(owners).length);
                check(getComputedStyle(small.querySelector("thead th:nth-child(2)")).position !== "sticky", "form: pin leaked into the small list");
                // pinned header cells must be opaque, or the scrolled column titles show through them
                check(getComputedStyle(medium.querySelector("thead th:nth-child(3)")).backgroundColor !== "rgba(0, 0, 0, 0)", "form: pinned header cell is transparent");
                check(getComputedStyle(medium.querySelector("thead th:nth-child(3)")).position === "sticky", "form: medium col not sticky");
                // the medium list is wide: scroll horizontally inside it and check the pinned column stays at the left edge
                var mscroll = scroller(tableOf(medium));
                check(mscroll.scrollWidth > mscroll.clientWidth, "form: medium list should overflow horizontally (scrollWidth " + mscroll.scrollWidth + " vs " + mscroll.clientWidth + ")");
                mscroll.scrollLeft = 600;
                await sleep(300);
                var first = medium.querySelector("thead th:nth-child(1)");
                var pth = medium.querySelector("thead th:nth-child(3)");
                var left = pth.getBoundingClientRect().left - mscroll.getBoundingClientRect().left;
                var expected = first.getBoundingClientRect().width + medium.querySelector("thead th:nth-child(2)").getBoundingClientRect().width;
                check(Math.abs(left - expected) < 3, "form: pinned medium col at " + left + " instead of " + expected);
                mscroll.scrollLeft = 0;
            } catch (e) { fail(e.message + " " + e.stack); }
            document.body.classList.add("lab_done");
        } },
        { trigger: "body.lab_done", run: () => { void 0; } },
    ],
});

