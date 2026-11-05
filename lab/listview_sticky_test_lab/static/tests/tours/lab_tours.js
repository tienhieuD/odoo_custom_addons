import { registry } from "@web/core/registry";

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const STYLE = "style[name=listview_sticky_header_and_column]";

/** closest scrolling ancestor of el */
function scroller(el) {
    let p = el.parentElement;
    while (p) {
        const o = getComputedStyle(p);
        if (/(auto|scroll)/.test(o.overflowX + o.overflowY) && (p.scrollWidth > p.clientWidth || p.scrollHeight > p.clientHeight)) {
            return p;
        }
        p = p.parentElement;
    }
    return document.scrollingElement;
}
const fail = (msg) => console.error("LABFAIL " + msg);
const check = (cond, msg) => { if (!cond) { fail(msg); } return cond; };

/** pin the column `name` inside `root`, then verify sticky behaviour while scrolling */
async function pinAndScroll(root, name, label, { vertical = true } = {}) {
    const th = root.querySelector(`thead th[data-name=${name}]`);
    if (!check(th, label + ": header " + name + " not found")) { return; }
    const idx = [...th.parentNode.children].indexOf(th);
    th.querySelector(".js_pin_this_column").click();
    await sleep(900);
    const owned = [...document.head.querySelectorAll(STYLE)];
    check(owned.length >= 1, label + ": no style injected");
    const sc = scroller(root.querySelector("table"));
    const ths = [...root.querySelectorAll("thead th")];
    const pinned = ths.slice(0, idx + 1);
    const free = ths.slice(idx + 1);
    pinned.forEach((t, i) => check(getComputedStyle(t).position === "sticky", `${label}: th ${i} not sticky`));
    const rel = (el) => el.getBoundingClientRect().left - sc.getBoundingClientRect().left;
    const freeBefore = free.length ? rel(free[free.length - 1]) : 0;
    sc.scrollLeft = 900;
    await sleep(300);
    const after = pinned.map(rel);
    // once scrolled, pinned column i must sit at the sum of the widths of the pinned columns before it
    let acc = 0;
    pinned.forEach((t, i) => {
        check(Math.abs(after[i] - acc) < 3, `${label}: pinned col ${i} at ${after[i]} instead of ${acc} (scrollLeft=${sc.scrollLeft})`);
        acc += t.getBoundingClientRect().width;
    });
    if (free.length) {
        check(Math.abs(rel(free[free.length - 1]) - freeBefore) > 50 || sc.scrollLeft === 0, label + ": free columns did not scroll");
    }
    // body cells of the pinned columns follow too
    const row = root.querySelector("tbody tr.o_data_row");
    if (row) {
        const cells = [...row.children].slice(0, idx + 1);
        cells.forEach((c, i) => check(Math.abs(rel(c) - after[i]) < 3, `${label}: body cell ${i} not aligned with header`));
        cells.forEach((c, i) => check(getComputedStyle(c).backgroundColor !== "rgba(0, 0, 0, 0)", `${label}: pinned cell ${i} is transparent`));
    }
    if (vertical) {
        sc.scrollTop = 600;
        await sleep(300);
        const top = ths[0].getBoundingClientRect().top - sc.getBoundingClientRect().top;
        check(top < 4 && top > -4, `${label}: header not stuck on top (offset ${top})`);
        check(getComputedStyle(ths[0]).backgroundColor !== "rgba(0, 0, 0, 0)", label + ": header transparent");
        sc.scrollTop = 0;
    }
    sc.scrollLeft = 0;
    return { sc, idx };
}

registry.category("web_tour.tours").add("lshc_lab_wide_list", {
    steps: () => [
        { trigger: ".o_list_view .o_data_row", run: () => {} },
        { trigger: ".o_search_panel .o_search_panel_category_value, .o_search_panel", run: () => {} },
        { trigger: ".o_list_view thead th[data-name=category_id]:has(.js_pin_this_column)", run: async () => {
            try {
                const root = document.querySelector(".o_list_view .o_list_renderer");
                const cols = root.querySelectorAll("thead th[data-name]").length;
                check(cols >= 50, "expected >= 50 columns, got " + cols);
                await pinAndScroll(root, "category_id", "wide(cat)");
                // pin a column further right, then unpin by clicking again
                await pinAndScroll(root, "amount", "wide(amount)");
                root.querySelector("thead th[data-name=amount] .js_pin_this_column").click();
                await sleep(400);
                check(!document.head.querySelector(STYLE), "wide: style not removed on unpin");
                // pin again, then filter through the search panel: the pin must survive the reload
                root.querySelector("thead th[data-name=state] .js_pin_this_column").click();
                await sleep(700);
                document.querySelector(".o_search_panel li.o_search_panel_category_value header, .o_search_panel .o_search_panel_filter_value input")?.click();
                await sleep(1500);
                const root2 = document.querySelector(".o_list_view .o_list_renderer");
                check(document.head.querySelector(STYLE), "wide: pin lost after search panel reload");
                check(getComputedStyle(root2.querySelector("thead th:nth-child(3)")).position === "sticky", "wide: col not sticky after reload");
            } catch (e) { fail(e.message + " " + e.stack); }
            document.body.classList.add("lab_done");
        } },
        { trigger: "body.lab_done", run: () => {} },
    ],
});

registry.category("web_tour.tours").add("lshc_lab_editable_list", {
    steps: () => [
        { trigger: ".o_list_view .o_data_row", run: () => {} },
        { trigger: ".o_list_view thead th[data-name=partner_id]:has(.js_pin_this_column)", run: async () => {
            try {
                const root = document.querySelector(".o_list_view .o_list_renderer");
                await pinAndScroll(root, "partner_id", "editable(partner)");
                // enter edit mode on a row: pinned columns must stay aligned
                root.querySelector("tbody tr.o_data_row td[name=name]").click();
                await sleep(800);
                check(root.querySelector("tbody tr.o_selected_row"), "editable: row did not enter edit mode");
                const th = root.querySelector("thead th[data-name=partner_id]");
                check(getComputedStyle(th).position === "sticky", "editable: pin lost while editing");
                const sc = scroller(root.querySelector("table"));
                sc.scrollLeft = 700;
                await sleep(300);
                const row = root.querySelector("tbody tr.o_selected_row");
                const rel = (el) => el.getBoundingClientRect().left - sc.getBoundingClientRect().left;
                const idx = [...th.parentNode.children].indexOf(th);
                const cell = row.children[idx];
                check(Math.abs(rel(cell) - rel(th)) < 3, "editable: edited row pinned cell misaligned");
                sc.scrollLeft = 0;
            } catch (e) { fail(e.message + " " + e.stack); }
            document.body.classList.add("lab_done");
        } },
        { trigger: "body.lab_done", run: () => {} },
    ],
});

registry.category("web_tour.tours").add("lshc_lab_form_lists", {
    steps: () => [
        { trigger: ".o_list_view .o_data_row td[name=name]", run: "click" },
        { trigger: ".o_form_view .o_notebook", run: () => {} },
        { trigger: ".o_form_view .o_field_widget[name=line_medium_ids] thead th[data-name=name]:has(.js_pin_this_column)", run: async () => {
            try {
                const form = document.querySelector(".o_form_view");
                const medium = form.querySelector(".o_field_widget[name=line_medium_ids]");
                const small = form.querySelector(".o_field_widget[name=line_small_ids]");
                check(small && medium, "form: x2many fields missing");
                check(small.querySelectorAll("thead th[data-name]").length >= 5, "form: small list columns");
                // pin in the medium list only
                const th = medium.querySelector("thead th[data-name=product]");
                th.querySelector(".js_pin_this_column").click();
                await sleep(900);
                const owners = new Set([...document.head.querySelectorAll(STYLE)].map((s) => s.dataset.owner));
                check(owners.size === 1, "form: expected 1 owner style, got " + owners.size);
                check(getComputedStyle(small.querySelector("thead th:nth-child(2)")).position !== "sticky", "form: pin leaked into the small list");
                const sc = scroller(medium.querySelector("table"));
                check(getComputedStyle(medium.querySelector("thead th:nth-child(3)")).position === "sticky", "form: medium col not sticky");
                // medium list is wide: scroll horizontally inside it
                const mscroll = medium.querySelector(".o_list_renderer") || sc;
                mscroll.scrollLeft = 600;
                await sleep(300);
                const rel = (el) => el.getBoundingClientRect().left - mscroll.getBoundingClientRect().left;
                const pth = medium.querySelector("thead th:nth-child(3)");
                check(Math.abs(rel(pth) - rel(medium.querySelector("thead th:nth-child(1)")) - (pth.getBoundingClientRect().left - medium.querySelector("thead th:nth-child(1)").getBoundingClientRect().left)) < 3, "form: sanity");
                check(mscroll.scrollWidth > mscroll.clientWidth, "form: medium list should overflow horizontally (scrollWidth " + mscroll.scrollWidth + " vs " + mscroll.clientWidth + ")");
                check(rel(pth) < 200, "form: pinned medium col left edge " + rel(pth) + " after horizontal scroll");
                mscroll.scrollLeft = 0;
            } catch (e) { fail(e.message + " " + e.stack); }
            document.body.classList.add("lab_done");
        } },
        { trigger: "body.lab_done", run: () => {} },
    ],
});
