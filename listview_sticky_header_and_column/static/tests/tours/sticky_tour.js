import { registry } from "@web/core/registry";

const KEY = "listview_sticky_header_and_column";
const LIST = ".o_action_manager .o_list_view";
const NAME_COL = "complete_name"; // first named column of the res.partner list
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function assert(cond, msg) {
    if (!cond) {
        throw new Error(`[lshc] ${msg}`);
    }
}
function near(a, b, tol, msg) {
    assert(Math.abs(a - b) <= tol, `${msg}: ${a} vs ${b} (tol ${tol})`);
}
async function waitFor(fn, msg, timeout = 5000) {
    const end = Date.now() + timeout;
    while (Date.now() < end) {
        const res = fn();
        if (res) {
            return res;
        }
        await sleep(50);
    }
    throw new Error(`[lshc] timeout: ${msg}`);
}
/** nearest ancestor that really scrolls on the given axis */
function scroller(el, axis) {
    for (let n = el.parentElement; n; n = n.parentElement) {
        const cs = getComputedStyle(n);
        const ov = axis === "y" ? cs.overflowY : cs.overflowX;
        const overflowing = axis === "y" ? n.scrollHeight > n.clientHeight + 1 : n.scrollWidth > n.clientWidth + 1;
        if (/(auto|scroll)/.test(ov) && overflowing) {
            return n;
        }
    }
    return null;
}
function lshcKeys() {
    return Object.keys(localStorage).filter((k) => k.startsWith(KEY));
}
function clearKeys() {
    lshcKeys().forEach((k) => localStorage.removeItem(k));
}
function pinStyles() {
    return [...document.head.querySelectorAll(`style[name="${KEY}"]`)];
}
function th(root, name) {
    return root.querySelector(`thead th[data-name="${name}"]`);
}
function pinBtn(root, name) {
    return th(root, name)?.querySelector(".js_pin_this_column");
}
async function pin(root, name) {
    const btn = await waitFor(() => pinBtn(root, name), `pin button of ${name}`);
    btn.click();
    await sleep(700);
}
/** make the table clearly wider than the viewport so a horizontal scroll exists */
async function widen(root) {
    root.querySelector("table").style.minWidth = "2600px";
    await sleep(200);
}
const rect = (el) => el.getBoundingClientRect();

registry.category("web_tour.tours").add("lshc_header_sticky", {
    steps: () => [
        { trigger: `${LIST} .o_data_row` },
        {
            content: "header cells are sticky and stay at the top of the scroll area",
            trigger: `${LIST} .o_data_row`,
            run: async () => {
                clearKeys();
                const root = document.querySelector(LIST);
                const thead = root.querySelector("thead");
                const cell = root.querySelector("thead th:not(.o_list_record_selector)");
                assert(["sticky"].includes(getComputedStyle(thead).position) ||
                    getComputedStyle(cell).position === "sticky", "thead/th is not position: sticky");
                const sc = scroller(thead, "y");
                assert(sc, "no vertical scroll area: not enough demo rows?");
                near(rect(thead).top, rect(sc).top, 2, "header top before scroll");
                const row0 = root.querySelector(".o_data_row");
                sc.scrollTop = 400;
                await sleep(300);
                assert(sc.scrollTop > 100, `did not scroll (${sc.scrollTop})`);
                near(rect(thead).top, rect(sc).top, 2, "header top after scroll");
                assert(rect(row0).bottom <= rect(thead).bottom + 1, "first row should have scrolled under the header");
                sc.scrollTop = 0;
            },
        },
    ],
});

registry.category("web_tour.tours").add("lshc_pin_buttons", {
    steps: () => [
        { trigger: `${LIST} .o_data_row` },
        {
            content: "one hidden pin button per sortable header, none on the checkbox header",
            trigger: `${LIST} .o_data_row`,
            run: async () => {
                const root = document.querySelector(LIST);
                await waitFor(() => pinBtn(root, "complete_name"), "pin button");
                const sortable = [...root.querySelectorAll("thead th[data-name]")];
                assert(sortable.length >= 3, "expected several named headers");
                const withBtn = sortable.filter((t) => t.querySelector(".js_pin_this_column"));
                assert(withBtn.length >= 3, `pin buttons missing (${withBtn.length})`);
                for (const t of withBtn) {
                    assert(t.querySelectorAll(".js_pin_this_column").length === 1, `duplicate pin button in ${t.dataset.name}`);
                }
                assert(!root.querySelector("thead th.o_list_record_selector .js_pin_this_column"), "pin button on checkbox header");
                assert(getComputedStyle(withBtn[0].querySelector(".js_pin_this_column")).display === "none", "pin button should be hidden until hover");
                // sorting re-renders the header: still exactly one button per header
                th(root, "complete_name").click();
                await sleep(800);
                const root2 = document.querySelector(LIST);
                await waitFor(() => pinBtn(root2, "complete_name"), "pin button after sort");
                for (const t of root2.querySelectorAll("thead th[data-name]")) {
                    assert(t.querySelectorAll(".js_pin_this_column").length <= 1, `duplicate pin button after sort in ${t.dataset.name}`);
                }
            },
        },
    ],
});

registry.category("web_tour.tours").add("lshc_pin_column", {
    steps: () => [
        { trigger: `${LIST} .o_data_row` },
        {
            content: "pin a column, scroll both ways and measure",
            trigger: `${LIST} .o_data_row`,
            run: async () => {
                clearKeys();
                const root = document.querySelector(LIST);
                await widen(root);
                await pin(root, "complete_name");
                // saved index = position of the th in the row (checkbox + avatar + name)
                const idx = [...root.querySelectorAll("thead tr th")].indexOf(th(root, "complete_name"));
                const keys = lshcKeys();
                assert(keys.length === 1 && !keys[0].includes("__field_"), `localStorage keys: ${keys}`);
                assert(Number(localStorage.getItem(keys[0])) === idx, `saved index ${localStorage.getItem(keys[0])} != ${idx}`);
                const styles = pinStyles();
                // a pinned list owns two style nodes: the "pre" one (sticky thead) and the final one (freeze)
                assert(styles.length === 2, `expected 2 style nodes, got ${styles.length}`);
                assert(styles[0].dataset.owner === styles[1].dataset.owner, "style nodes of different owners");
                assert(root.querySelector(".o_list_renderer").dataset.lshcId === styles[0].dataset.owner, "list not scoped to its style node");
                // sticky left offsets are cumulative widths
                const heads = [...root.querySelectorAll("thead tr th")].slice(0, idx + 1);
                let acc = 0;
                heads.forEach((h, i) => {
                    const cs = getComputedStyle(h);
                    assert(cs.position === "sticky", `th ${i} not sticky`);
                    near(parseFloat(cs.left), acc, 1, `left of th ${i}`);
                    assert(cs.zIndex === "10", `z-index of th ${i}: ${cs.zIndex}`);
                    acc += rect(h).width;
                });
                const cell = root.querySelector(`.o_data_row td:nth-child(${idx + 1})`);
                assert(getComputedStyle(cell).position === "sticky", "pinned td not sticky");
                const free = root.querySelector(`.o_data_row td:nth-child(${idx + 3})`);
                assert(getComputedStyle(free).position !== "sticky", "unpinned td must not be sticky");

                const sx = scroller(root.querySelector("table"), "x");
                assert(sx, "no horizontal scroll area");
                const left0 = rect(cell).left - rect(sx).left;
                const freeX0 = rect(free).left;
                sx.scrollLeft = 300;
                await sleep(300);
                assert(sx.scrollLeft > 100, `did not scroll horizontally (${sx.scrollLeft})`);
                near(rect(cell).left - rect(sx).left, left0, 1.5, "pinned td moved on horizontal scroll");
                near(rect(heads[idx]).left - rect(sx).left, left0, 1.5, "pinned th moved on horizontal scroll");
                assert(freeX0 - rect(free).left > 100, "unpinned column should move with the scroll");

                // header still on top while scrolling both ways
                const sy = scroller(root.querySelector("table"), "y");
                assert(sy, "no vertical scroll area");
                sy.scrollTop = 400;
                await sleep(300);
                near(rect(root.querySelector("thead")).top, rect(sy).top, 2, "header top (both scrolls)");
                near(rect(heads[idx]).top, rect(sy).top, 2, "pinned th top (both scrolls)");
                near(rect(heads[idx]).left - rect(sx).left, left0, 1.5, "pinned th left (both scrolls)");
                sx.scrollLeft = 0;
                sy.scrollTop = 0;
                clearKeys();
            },
        },
    ],
});

registry.category("web_tour.tours").add("lshc_unpin_column", {
    steps: () => [
        { trigger: `${LIST} .o_data_row` },
        {
            content: "pin then unpin the same column",
            trigger: `${LIST} .o_data_row`,
            run: async () => {
                clearKeys();
                const root = document.querySelector(LIST);
                await pin(root, "email");
                const idx = [...root.querySelectorAll("thead tr th")].indexOf(th(root, "email"));
                const cell = () => root.querySelector(`.o_data_row td:nth-child(${idx + 1})`);
                assert(getComputedStyle(cell()).position === "sticky", "column not pinned");
                await pin(root, "email"); // second click = unpin
                assert(pinStyles().length === 0, "style node still present after unpin");
                assert(lshcKeys().length === 0, `localStorage keys left after unpin: ${lshcKeys()}`);
                assert(getComputedStyle(cell()).position !== "sticky", "td still sticky after unpin");
                assert(!root.querySelector("thead th:first-child") ||
                    getComputedStyle(root.querySelector("thead th:first-child")).left === "auto" ||
                    getComputedStyle(root.querySelector("thead th:first-child")).zIndex !== "10", "th still pinned after unpin");
                clearKeys();
            },
        },
    ],
});

registry.category("web_tour.tours").add("lshc_pin_persist", {
    steps: () => [
        { trigger: `${LIST} .o_data_row` },
        {
            content: "pin a column",
            trigger: `${LIST} .o_data_row`,
            run: async () => {
                clearKeys();
                await pin(document.querySelector(LIST), "complete_name");
            },
        },
        {
            content: "open a record",
            trigger: `${LIST} .o_data_row:first-child .o_data_cell[name=complete_name]`,
            run: "click",
        },
        { trigger: ".o_form_view" },
        {
            content: "back to the list",
            trigger: ".o_control_panel .breadcrumb-item:not(.active), .o_control_panel .o_back_button",
            run: "click",
        },
        { trigger: `${LIST} .o_data_row` },
        {
            content: "the pinned column is restored from localStorage",
            trigger: `${LIST} .o_data_row`,
            run: async () => {
                const root = document.querySelector(LIST);
                const idx = [...root.querySelectorAll("thead tr th")].indexOf(th(root, "complete_name"));
                await waitFor(() => getComputedStyle(root.querySelector(`.o_data_row td:nth-child(${idx + 1})`)).position === "sticky",
                    "pinned column restored after remount");
                await sleep(800);
                const info = pinStyles().map((n) => `${n.dataset.owner}:${!!document.querySelector(`[data-lshc-id="${n.dataset.owner}"]`)}`);
                assert(pinStyles().length === 2, `style nodes after remount: ${info} (leak?)`);
                clearKeys();
            },
        },
    ],
});

registry.category("web_tour.tours").add("lshc_checkbox_optional", {
    steps: () => [
        { trigger: `${LIST} .o_data_row` },
        {
            content: "pin a column, select all rows with the checkbox column",
            trigger: `${LIST} .o_data_row`,
            run: async () => {
                clearKeys();
                const root = document.querySelector(LIST);
                await pin(root, "complete_name");
                const box0 = root.querySelector("thead th:first-child");
                assert(getComputedStyle(box0).position === "sticky", "checkbox header not sticky when pinned");
                near(parseFloat(getComputedStyle(box0).left), 0, 0.5, "checkbox column left");
                const all = root.querySelector("thead .o_list_record_selector input");
                all.click();
                await sleep(400);
                const rows = root.querySelectorAll(".o_data_row").length;
                assert(root.querySelectorAll(".o_data_row .o_list_record_selector input:checked").length === rows, "select-all did not select every row");
                assert(document.querySelector(".o_selection_box, .o_list_selection_box"), "selection box missing");
                all.click();
                await sleep(300);
            },
        },
        {
            content: "open optional columns",
            trigger: `${LIST} .o_optional_columns_dropdown_toggle`,
            run: "click",
        },
        {
            content: "show the Tax ID column",
            trigger: ".o-dropdown--menu .dropdown-item:contains('Tax ID'), .o-dropdown--menu .dropdown-item:contains('TIN')",
            run: "click",
        },
        {
            content: "new column has a pin button, pinned column kept its sticky left",
            trigger: `${LIST} thead th[data-name=vat]`,
            run: async () => {
                const root = document.querySelector(LIST);
                await waitFor(() => pinBtn(root, "vat"), "pin button on the new column");
                const idx = [...root.querySelectorAll("thead tr th")].indexOf(th(root, "complete_name"));
                const cell = root.querySelector(`.o_data_row td:nth-child(${idx + 1})`);
                assert(getComputedStyle(cell).position === "sticky", "pinned column lost after optional column toggle");
                assert(th(root, "vat").querySelectorAll(".js_pin_this_column").length === 1, "duplicate pin button");
                clearKeys();
            },
        },
    ],
});

registry.category("web_tour.tours").add("lshc_o2m_form", {
    steps: () => [
        { trigger: ".o_form_view .o_notebook" },
        {
            content: "open the Users tab",
            trigger: ".o_notebook .nav-link[name=user_ids], .o_notebook .nav-link[name=users]",
            run: "click",
        },
        { trigger: ".o_field_widget[name=user_ids] .o_data_row, .o_field_widget[name=users] .o_data_row" },
        {
            content: "pin a column of the embedded list",
            trigger: ".o_field_widget[name=user_ids] .o_data_row, .o_field_widget[name=users] .o_data_row",
            run: async () => {
                clearKeys();
                const root = document.querySelector(".o_field_widget[name=user_ids] .o_list_renderer, .o_field_widget[name=users] .o_list_renderer");
                assert(root, "embedded list not found");
                // the very first column (index 0: an embedded list has no checkbox column)
                const name = root.querySelector("thead th[data-name]").dataset.name;
                assert(root.querySelector("thead tr th") === th(root, name), "first th is not a named column");
                await pin(root, name);
                const keys = lshcKeys();
                assert(keys.length === 1 && /__field_(user_ids|users)$/.test(keys[0]), `localStorage keys: ${keys}`);
                assert(localStorage.getItem(keys[0]) === "0", `saved index: ${localStorage.getItem(keys[0])}`);
                const pinned = root.querySelector(".o_data_row td:nth-child(1)");
                assert(getComputedStyle(pinned).position === "sticky", `first embedded column not pinned: pos=${getComputedStyle(pinned).position} styles=${pinStyles().length}`);
                assert(getComputedStyle(th(root, name)).position === "sticky", "first embedded th not sticky");
                // the embedded list keeps its own scrollbar (form does not scroll it)
                assert(getComputedStyle(root).overflowX !== "visible", "embedded list lost its overflow");
            },
        },
        {
            content: "open the Access Rights tab (a second embedded list)",
            trigger: ".o_notebook .nav-link[name=access_rights]",
            run: "click",
        },
        { trigger: ".o_field_widget[name=access_ids] thead th, .o_field_widget[name=model_access] thead th" },
        {
            content: "the other embedded list is not affected",
            trigger: ".o_field_widget[name=access_ids] thead th, .o_field_widget[name=model_access] thead th",
            run: async () => {
                await sleep(500);
                const other = document.querySelector(".o_field_widget[name=access_ids] .o_list_renderer, .o_field_widget[name=model_access] .o_list_renderer");
                assert(!other.dataset.lshcId, "second list wrongly scoped");
                // the pinned list was unmounted with its tab: its two style nodes must be gone (no leak)
                assert(pinStyles().length === 0, `style nodes after leaving the pinned list: ${pinStyles().length}`);
                clearKeys();
            },
        },
    ],
});

registry.category("web_tour.tours").add("lshc_dialog", {
    steps: () => [
        { trigger: ".o_form_view .o_field_widget[name=parent_id] input" },
        {
            content: "open the Many2one search dialog",
            trigger: ".o_form_view .o_field_widget[name=parent_id] input",
            run: "click",
        },
        {
            trigger: ".o-autocomplete--dropdown-menu .o_m2o_dropdown_option a:contains('Search More')",
            run: "click",
        },
        { trigger: ".modal .o_list_view .o_data_row" },
        {
            content: "pin a column inside the dialog: it stays put on horizontal scroll, header sticky",
            trigger: ".modal .o_list_view .o_data_row",
            run: async () => {
                clearKeys();
                const root = document.querySelector(".modal .o_list_view");
                await widen(root);
                // make the rows tall enough for a vertical scroll whatever the demo data / window size
                root.querySelectorAll(".o_data_row td").forEach((td) => (td.style.paddingBlock = "40px"));
                const name = root.querySelector("thead th[data-name]").dataset.name;
                await pin(root, name);
                const idx = [...root.querySelectorAll("thead tr th")].indexOf(th(root, name));
                const styles = pinStyles();
                assert(styles.length === 2, `style nodes in dialog: ${styles.length}`);
                const cell = root.querySelector(`.o_data_row td:nth-child(${idx + 1})`);
                const head = th(root, name);
                assert(getComputedStyle(cell).position === "sticky", "pinned dialog td not sticky");
                assert(getComputedStyle(head).position === "sticky", "pinned dialog th not sticky");
                const free = root.querySelector(`.o_data_row td:nth-child(${idx + 3})`);
                assert(getComputedStyle(free).position !== "sticky", "unpinned dialog td must not be sticky");
                const sx = scroller(root.querySelector("table"), "x");
                assert(sx && sx.closest(".modal"), "no horizontal scroll area inside the dialog");
                const left0 = rect(cell).left - rect(sx).left;
                const freeX0 = rect(free).left;
                sx.scrollLeft = 300;
                await sleep(300);
                assert(sx.scrollLeft > 100, `dialog did not scroll horizontally (${sx.scrollLeft})`);
                near(rect(cell).left - rect(sx).left, left0, 1.5, "pinned dialog td moved on horizontal scroll");
                near(rect(head).left - rect(sx).left, left0, 1.5, "pinned dialog th moved on horizontal scroll");
                assert(freeX0 - rect(free).left > 100, "unpinned dialog column should move with the scroll");
                // header stays on top of the dialog scroll area while scrolling down
                const sy = scroller(root.querySelector("table"), "y");
                assert(sy && sy.closest(".modal"), "no vertical scroll area inside the dialog");
                sy.scrollTop = 200;
                await sleep(300);
                assert(sy.scrollTop > 50, `dialog did not scroll vertically (${sy.scrollTop})`);
                near(rect(root.querySelector("thead")).top, rect(sy).top, 2, "dialog header top after scroll");
                near(rect(head).top, rect(sy).top, 2, "pinned dialog th top after scroll");
                sx.scrollLeft = 0;
                sy.scrollTop = 0;
                clearKeys();
            },
        },
        {
            content: "pick a record in the dialog",
            trigger: ".modal .o_list_view .o_data_row:first-child .o_data_cell",
            run: "click",
        },
        {
            content: "the record picked in the dialog is set on the form",
            trigger: ".o_form_view .o_field_widget[name=parent_id] input",
            run: async () => {
                await waitFor(() => !document.querySelector(".modal") &&
                    document.querySelector(".o_field_widget[name=parent_id] input").value, "parent set after dialog");
                clearKeys();
            },
        },
        {
            content: "discard the new record (no dirty form left behind)",
            trigger: ".o_form_button_cancel",
            run: "click",
        },
        { trigger: "body:not(:has(.o_form_status_indicator .o_form_button_save))" },
    ],
});

registry.category("web_tour.tours").add("lshc_pin_first_column", {
    steps: () => [
        { trigger: ".o_form_view .o_notebook" },
        {
            content: "open the Users tab",
            trigger: ".o_notebook .nav-link[name=user_ids], .o_notebook .nav-link[name=users]",
            run: "click",
        },
        { trigger: ".o_field_widget[name=user_ids] .o_data_row, .o_field_widget[name=users] .o_data_row" },
        {
            content: "pin the first column (index 0), then unpin it",
            trigger: ".o_field_widget[name=user_ids] .o_data_row, .o_field_widget[name=users] .o_data_row",
            run: async () => {
                clearKeys();
                const root = document.querySelector(".o_field_widget[name=user_ids] .o_list_renderer, .o_field_widget[name=users] .o_list_renderer");
                const name = root.querySelector("thead th[data-name]").dataset.name;
                assert(root.querySelector("thead tr th") === th(root, name), "first th is not a named column");
                const cell = () => root.querySelector(".o_data_row td:nth-child(1)");
                assert(getComputedStyle(cell()).position !== "sticky", "first column pinned before any click");
                await pin(root, name);
                assert(getComputedStyle(cell()).position === "sticky", "first column (index 0) not pinned");
                near(parseFloat(getComputedStyle(cell()).left), 0, 0.5, "first column left");
                assert(pinStyles().length === 2, `style nodes after pin: ${pinStyles().length}`);
                const key = lshcKeys()[0];
                assert(localStorage.getItem(key) === "0", `saved index: ${localStorage.getItem(key)}`);
                await pin(root, name); // second click = unpin
                assert(getComputedStyle(cell()).position !== "sticky", "first column still pinned after unpin");
                assert(pinStyles().length === 0, `style nodes after unpin: ${pinStyles().length}`);
                assert(lshcKeys().length === 0, `localStorage keys left after unpin: ${lshcKeys()}`);
                await pin(root, name); // and it can be pinned again
                assert(getComputedStyle(cell()).position === "sticky", "first column not pinned again");
                clearKeys();
            },
        },
    ],
});

registry.category("web_tour.tours").add("lshc_unpin_remount", {
    steps: () => [
        { trigger: `${LIST} .o_data_row` },
        {
            content: "pin then unpin a column",
            trigger: `${LIST} .o_data_row`,
            run: async () => {
                clearKeys();
                const root = document.querySelector(LIST);
                await pin(root, NAME_COL);
                const key = lshcKeys()[0];
                assert(key, "nothing saved after pin");
                await pin(root, NAME_COL);
                assert(lshcKeys().length === 0, `keys left after unpin: ${lshcKeys()}`);
                // an old version left "-1" behind after an unpin: it must not count as pinned
                localStorage.setItem(key, "-1");
            },
        },
        {
            content: "open a record",
            trigger: `${LIST} .o_data_row:first-child .o_data_cell[name=${NAME_COL}]`,
            run: "click",
        },
        { trigger: ".o_form_view" },
        {
            content: "back to the list",
            trigger: ".o_control_panel .breadcrumb-item:not(.active), .o_control_panel .o_back_button",
            run: "click",
        },
        { trigger: `${LIST} .o_data_row` },
        {
            content: "no leftover pin style, header still sticky, nothing pinned",
            trigger: `${LIST} .o_data_row`,
            run: async () => {
                await sleep(800);
                const root = document.querySelector(LIST);
                await waitFor(() => pinBtn(root, NAME_COL), "pin button after remount");
                assert(pinStyles().length === 0, `style nodes after remount: ${pinStyles().length}`);
                assert(lshcKeys().length === 0, `legacy -1 key not cleaned: ${lshcKeys()}`);
                const idx = [...root.querySelectorAll("thead tr th")].indexOf(th(root, NAME_COL));
                assert(getComputedStyle(root.querySelector(`.o_data_row td:nth-child(${idx + 1})`)).position !== "sticky", "column pinned after unpin");
                assert(getComputedStyle(root.querySelector("thead th:first-child")).left === "auto" ||
                    getComputedStyle(root.querySelector("thead th:first-child")).position !== "sticky" ||
                    getComputedStyle(root.querySelector("thead th:first-child")).zIndex !== "10", "th still pinned after unpin");
                // the sticky header (from the core list) still works
                const thead = root.querySelector("thead");
                const sc = scroller(thead, "y");
                assert(sc, "no vertical scroll area");
                sc.scrollTop = 400;
                await sleep(300);
                near(rect(thead).top, rect(sc).top, 2, "header top after remount + scroll");
                sc.scrollTop = 0;
                // and pinning still works after the unpin / remount
                await widen(root);
                await pin(root, NAME_COL);
                assert(getComputedStyle(root.querySelector(`.o_data_row td:nth-child(${idx + 1})`)).position === "sticky", "cannot pin again after remount");
                clearKeys();
            },
        },
    ],
});

// The row being edited (inline, e.g. a one2many) must stay above the pinned header cells and the pinned
// cells of the other rows: its Many2one dropdown is a child of the pinned cell and opens over them.
registry.category("web_tour.tours").add("lshc_edit_row_on_top", {
    steps: () => [
        { trigger: ".o_form_view .o_notebook" },
        { content: "Access Rights tab", trigger: ".o_notebook .nav-link[name=access_rights]", run: "click" },
        { trigger: ".o_field_widget[name=access_ids] .o_data_row" },
        {
            content: "pin Group, edit a row, open its Many2one dropdown and measure what is on top",
            trigger: ".o_field_widget[name=access_ids] .o_data_row",
            run: async () => {
                clearKeys();
                const fld = document.querySelector(".o_field_widget[name=access_ids]");
                const root = fld.querySelector(".o_list_renderer");
                await widen(root);
                await pin(root, "group_id");
                const idx = [...root.querySelectorAll("thead tr th")].indexOf(th(root, "group_id"));
                const sx = scroller(root.querySelector("table"), "x");
                sx.scrollLeft = 200;
                await sleep(300);
                root.querySelector(".o_data_row:nth-child(3) td[name=name]").click();
                const sel = await waitFor(() => root.querySelector(".o_selected_row"), "edited row");
                await sleep(500);
                const z = (el) => parseInt(getComputedStyle(el).zIndex, 10);
                const selCell = sel.querySelector(`td:nth-child(${idx + 1})`);
                assert(getComputedStyle(selCell).position === "sticky", "edited pinned cell not sticky");
                const otherCells = [...root.querySelectorAll(`.o_data_row:not(.o_selected_row) td:nth-child(${idx + 1})`)];
                assert(otherCells.length >= 3, "not enough other rows");
                otherCells.forEach((c) => assert(z(selCell) > z(c), `edited pinned cell z-index ${z(selCell)} <= other row's ${z(c)}`));
                assert(z(selCell) > z(th(root, "group_id")), `edited pinned cell z-index ${z(selCell)} <= pinned header's ${z(th(root, "group_id"))}`);
                // open the Many2one dropdown of the pinned cell and check what is really painted on top of it
                const input = selCell.querySelector("input");
                assert(input, "no Many2one input in the edited pinned cell");
                input.focus();
                input.value = "a";
                input.dispatchEvent(new Event("input", { bubbles: true }));
                const dd = await waitFor(() => document.querySelector(".o-autocomplete--dropdown-menu"), "dropdown");
                await sleep(500);
                const items = [...dd.querySelectorAll(".o-autocomplete--dropdown-item")];
                assert(items.length > 3, `dropdown items: ${items.length}`);
                const head = rect(root.querySelector("thead"));
                let overHeader = 0;
                items.forEach((it) => {
                    const r = rect(it);
                    const el = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
                    if (r.top < head.bottom && r.bottom > head.top) {
                        overHeader++;
                    }
                    assert(el && dd.contains(el), `dropdown item "${it.textContent.trim()}" is covered by <${el?.tagName} class="${el?.className}">`);
                });
                assert(overHeader || rect(dd).top > head.bottom, "the dropdown does not overlap the header: nothing measured");
                clearKeys();
            },
        },
    ],
});

// ---- Order Lines (sale): headers of a `<column>` group have no data-name -------------------------------
const OL = ".o_field_widget[name=order_line]";
const labelOf = (t) => t.innerText.trim();
// by text, or by data-name (Odoo 19 labels the product column "Product" or "product_id" depending on the groups; the field is product_id or product_template_id)
const olHead = (root, label) => [...root.querySelectorAll("thead tr th")].find((t) => labelOf(t) === label || t.dataset.name === label || (label === "product_id" && /^product_(template_)?id$/.test(t.dataset.name || "")));

registry.category("web_tour.tours").add("lshc_order_lines", {
    steps: () => [
        { trigger: `${OL} .o_data_row` },
        {
            content: "every data header of Order Lines has exactly one pin button (also those without data-name)",
            trigger: `${OL} .o_data_row`,
            run: async () => {
                clearKeys();
                const root = document.querySelector(`${OL} .o_list_renderer`);
                await waitFor(() => olHead(root, "Quantity")?.querySelector(".js_pin_this_column"), "pin button on Quantity");
                const ths = [...root.querySelectorAll("thead tr th")];
                let labelled = 0;
                for (const label of ["product_id", "Quantity", "Unit Price"]) {
                    const t = olHead(root, label);
                    assert(t, `no header ${label}`);
                    assert(t.querySelectorAll(".js_pin_this_column").length === 1, `${label}: pin buttons = ${t.querySelectorAll(".js_pin_this_column").length}`);
                }
                for (const t of ths) {
                    const n = t.querySelectorAll(".js_pin_this_column").length;
                    const excluded = t.matches(".o_handle_cell, .o_list_record_selector, .o_list_controller, .o_list_actions_header, .o_list_button, .o_list_open_form_view");
                    if (excluded || !labelOf(t) && !t.dataset.name) {
                        assert(n === 0, `pin button on a non-data header (class="${t.className}")`);
                    } else {
                        labelled++;
                        assert(n === 1, `header "${labelOf(t)}": ${n} pin buttons`);
                    }
                }
                assert(labelled >= 4, `only ${labelled} pinnable headers`);
                assert(getComputedStyle(olHead(root, "Quantity").querySelector(".js_pin_this_column")).display === "none", "pin button should be hidden until hover");
                // the (absolute) button is positioned against its header, as for named columns
                assert(getComputedStyle(olHead(root, "Unit Price")).position !== "static", "header is not a positioning context for the button");
            },
        },
        {
            content: "pin Description, Quantity, Unit Price in turn: that column and all on its left stay, scrolling horizontally",
            trigger: `${OL} .o_data_row`,
            run: async () => {
                const root = document.querySelector(`${OL} .o_list_renderer`);
                await widen(root);
                for (const label of ["product_id", "Quantity", "Unit Price"]) {
                    const heads = () => [...root.querySelectorAll("thead tr th")];
                    const idx = heads().indexOf(olHead(root, label));
                    assert(idx >= 1, `${label} index ${idx}`);
                    olHead(root, label).querySelector(".js_pin_this_column").click();
                    await sleep(700);
                    const keys = lshcKeys();
                    assert(keys.length === 1 && /__field_order_line$/.test(keys[0]), `localStorage keys: ${keys}`);
                    assert(Number(localStorage.getItem(keys[0])) === idx, `${label}: saved index ${localStorage.getItem(keys[0])} != ${idx}`);
                    heads().slice(0, idx + 1).forEach((h, i) => assert(getComputedStyle(h).position === "sticky" && getComputedStyle(h).zIndex === "10", `${label}: th ${i} not pinned`));
                    const cell = root.querySelector(`.o_data_row td:nth-child(${idx + 1})`);
                    const first = root.querySelector(".o_data_row td:nth-child(1)");
                    assert(getComputedStyle(cell).position === "sticky", `${label}: pinned td not sticky`);
                    const free = root.querySelector(`.o_data_row td:nth-child(${idx + 3})`);
                    assert(getComputedStyle(free).position !== "sticky", `${label}: column ${idx + 3} must not be pinned`);
                    const sx = scroller(root.querySelector("table"), "x");
                    assert(sx, "no horizontal scroll area");
                    const l0 = rect(cell).left - rect(sx).left, f0 = rect(first).left, x0 = rect(free).left;
                    sx.scrollLeft = 300;
                    await sleep(300);
                    assert(sx.scrollLeft > 100, `did not scroll (${sx.scrollLeft})`);
                    near(rect(cell).left - rect(sx).left, l0, 1.5, `${label}: pinned td moved`);
                    near(rect(first).left, f0, 1.5, `${label}: columns on the left of the pinned one moved`);
                    near(rect(heads()[idx]).left - rect(sx).left, l0, 1.5, `${label}: pinned th moved`);
                    assert(x0 - rect(free).left > 100, `${label}: unpinned column should move`);
                    sx.scrollLeft = 0;
                    await sleep(200);
                    // pinning another column replaces the first pin (never two pins)
                    assert(pinStyles().length === 2, `${label}: style nodes ${pinStyles().length}`);
                }
            },
        },
        {
            content: "second click on the pinned column unpins it",
            trigger: `${OL} .o_data_row`,
            run: async () => {
                const root = document.querySelector(`${OL} .o_list_renderer`);
                olHead(root, "Unit Price").querySelector(".js_pin_this_column").click();
                await sleep(700);
                assert(pinStyles().length === 0, "style nodes left after unpin");
                assert(lshcKeys().length === 0, `localStorage keys left: ${lshcKeys()}`);
                const idx = [...root.querySelectorAll("thead tr th")].indexOf(olHead(root, "Unit Price"));
                assert(getComputedStyle(root.querySelector(`.o_data_row td:nth-child(${idx + 1})`)).position !== "sticky", "td still sticky");
                clearKeys();
            },
        },
    ],
});
